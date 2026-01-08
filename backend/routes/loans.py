from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.loan import LoanAgreement
from models.covenant import Covenant
from schemas import LoanCreate, LoanResponse
from routes.auth import get_current_user
from services.pdf_service import pdf_service
from services.claude_service import claude_service
from typing import List, Optional
import os
import uuid as uuid_lib
import logging
from datetime import date

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/loans", tags=["Loans"])

@router.post("/upload", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def upload_loan_agreement(
    file: UploadFile = File(...),
    title: str = Form(...),
    borrower_name: str = Form(...),
    loan_amount: Optional[float] = Form(None),
    currency: str = Form("USD"),
    origination_date: Optional[str] = Form(None),
    maturity_date: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload PDF loan agreement and extract covenants"""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Save file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid_lib.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}.pdf")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    logger.info(f"Saved PDF to {file_path}")
    
    # Parse dates
    orig_date = date.fromisoformat(origination_date) if origination_date else None
    mat_date = date.fromisoformat(maturity_date) if maturity_date else None
    
    # Create loan record
    loan = LoanAgreement(
        user_id=current_user.id,
        title=title,
        borrower_name=borrower_name,
        loan_amount=loan_amount,
        currency=currency,
        origination_date=orig_date,
        maturity_date=mat_date,
        file_url=file_path,
        file_name=file.filename,
        extraction_status="processing"
    )
    
    db.add(loan)
    db.commit()
    db.refresh(loan)
    
    # Extract text from PDF
    extracted_text = pdf_service.extract_text_from_pdf(file_path)
    
    if not extracted_text:
        loan.extraction_status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract text from PDF"
        )
    
    # Extract covenants using Claude
    covenants_data = claude_service.extract_covenants_from_text(extracted_text)
    
    if not covenants_data:
        loan.extraction_status = "completed"
        db.commit()
        logger.warning(f"No covenants extracted from loan {loan.id}")
        return LoanResponse.from_orm(loan)
    
    # Create covenant records
    for cov_data in covenants_data:
        covenant = Covenant(
            loan_agreement_id=loan.id,
            covenant_type=cov_data.get('covenant_type', 'financial'),
            covenant_name=cov_data.get('covenant_name', ''),
            description=cov_data.get('description'),
            threshold_value=cov_data.get('threshold_value'),
            threshold_operator=cov_data.get('threshold_operator'),
            measurement_frequency=cov_data.get('measurement_frequency'),
            status='healthy'
        )
        db.add(covenant)
    
    loan.extraction_status = "completed"
    db.commit()
    
    logger.info(f"Created loan {loan.id} with {len(covenants_data)} covenants")
    
    return LoanResponse.from_orm(loan)

@router.get("/", response_model=List[LoanResponse])
def get_all_loans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all loans for current user"""
    loans = db.query(
        LoanAgreement,
        func.count(Covenant.id).label('covenant_count')
    ).outerjoin(
        Covenant
    ).filter(
        LoanAgreement.user_id == current_user.id
    ).group_by(
        LoanAgreement.id
    ).all()
    
    result = []
    for loan, covenant_count in loans:
        loan_dict = LoanResponse.from_orm(loan).dict()
        loan_dict['covenant_count'] = covenant_count
        result.append(loan_dict)
    
    return result

@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific loan details"""
    from uuid import UUID
    
    loan = db.query(LoanAgreement).filter(
        LoanAgreement.id == UUID(loan_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    return LoanResponse.from_orm(loan)

@router.get("/{loan_id}/covenants", response_model=List)
def get_loan_covenants(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all covenants for a loan"""
    from uuid import UUID
    from schemas import CovenantResponse
    
    # Verify loan belongs to user
    loan = db.query(LoanAgreement).filter(
        LoanAgreement.id == UUID(loan_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    covenants = db.query(Covenant).filter(
        Covenant.loan_agreement_id == UUID(loan_id)
    ).all()
    
    return [CovenantResponse.from_orm(c) for c in covenants]

@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a loan and all associated covenants"""
    from uuid import UUID
    
    loan = db.query(LoanAgreement).filter(
        LoanAgreement.id == UUID(loan_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Delete file if exists
    if loan.file_url and os.path.exists(loan.file_url):
        try:
            os.remove(loan.file_url)
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
    
    db.delete(loan)
    db.commit()
    
    logger.info(f"Deleted loan {loan_id}")
    return None
