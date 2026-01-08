from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.loan import LoanAgreement
from app.models.covenant import Covenant
from app.schemas.loan import LoanResponse, CovenantResponse
from app.api.deps import get_current_user
from app.services.pdf_service import pdf_service
from app.services.openai_service import openai_service
from app.config import settings
from typing import List, Optional
from datetime import date
import os
import uuid as uuid_lib
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/loans", tags=["Loans"])

async def process_loan_extraction(loan_id: str, file_path: str, db: Session):
    """Background task to extract covenants from PDF"""
    try:
        # Get loan
        from uuid import UUID
        loan = db.query(LoanAgreement).filter(LoanAgreement.id == UUID(loan_id)).first()
        if not loan:
            return
        
        loan.ai_extraction_status = "processing"
        db.commit()
        
        # Extract text from PDF
        extracted_text = pdf_service.extract_text_from_pdf(file_path)
        
        if not extracted_text:
            loan.ai_extraction_status = "failed"
            db.commit()
            logger.error(f"Failed to extract text from PDF for loan {loan_id}")
            return
        
        # Extract covenants using OpenAI
        extraction_result = await openai_service.extract_covenants_from_agreement(
            extracted_text, 
            loan.title
        )
        
        # Store full extraction result
        loan.ai_extraction_result = extraction_result
        
        # Update loan basic info if extracted
        if extraction_result.get('borrower_name'):
            loan.borrower_name = extraction_result['borrower_name']
        if extraction_result.get('loan_amount'):
            loan.loan_amount = extraction_result['loan_amount']
        if extraction_result.get('currency'):
            loan.currency = extraction_result['currency']
        if extraction_result.get('origination_date'):
            loan.origination_date = date.fromisoformat(extraction_result['origination_date'])
        if extraction_result.get('maturity_date'):
            loan.maturity_date = date.fromisoformat(extraction_result['maturity_date'])
        
        # Create covenant records
        covenants_data = extraction_result.get('covenants', [])
        for cov_data in covenants_data:
            covenant = Covenant(
                loan_agreement_id=loan.id,
                covenant_type=cov_data.get('covenant_type', 'financial'),
                covenant_name=cov_data.get('covenant_name', 'Unknown Covenant'),
                description=cov_data.get('description'),
                threshold_value=cov_data.get('threshold_value'),
                threshold_operator=cov_data.get('threshold_operator'),
                frequency=cov_data.get('frequency'),
                is_active=True
            )
            db.add(covenant)
        
        loan.ai_extraction_status = "completed"
        db.commit()
        
        logger.info(f"Successfully extracted {len(covenants_data)} covenants from loan {loan_id}")
        
    except Exception as e:
        logger.error(f"Error in background extraction for loan {loan_id}: {e}")
        if loan:
            loan.ai_extraction_status = "failed"
            db.commit()

@router.post("/upload", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def upload_loan_agreement(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload PDF loan agreement and trigger AI extraction"""
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file
    file_id = str(uuid_lib.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.pdf")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        
        # Check file size
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB limit"
            )
        
        f.write(content)
    
    logger.info(f"Saved PDF to {file_path}")
    
    # Create loan record
    loan = LoanAgreement(
        user_id=current_user.id,
        title=title,
        document_path=file_path,
        ai_extraction_status="pending",
        status="active",
        currency="EUR"
    )
    
    db.add(loan)
    db.commit()
    db.refresh(loan)
    
    # Trigger background extraction
    background_tasks.add_task(process_loan_extraction, str(loan.id), file_path, db)
    
    return LoanResponse.from_orm(loan)

@router.get("/", response_model=List[LoanResponse])
def get_all_loans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all loans for current user with covenant counts"""
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
        loan_dict['covenant_count'] = covenant_count or 0
        result.append(LoanResponse(**loan_dict))
    
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

@router.get("/{loan_id}/covenants", response_model=List[CovenantResponse])
def get_loan_covenants(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all covenants for a loan with latest measurement status"""
    from uuid import UUID
    from app.models.covenant import CovenantMeasurement
    
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
        Covenant.loan_agreement_id == UUID(loan_id),
        Covenant.is_active == True
    ).all()
    
    # Enrich with latest measurement
    result = []
    for covenant in covenants:
        latest = db.query(CovenantMeasurement).filter(
            CovenantMeasurement.covenant_id == covenant.id
        ).order_by(CovenantMeasurement.measurement_date.desc()).first()
        
        cov_dict = CovenantResponse.from_orm(covenant).dict()
        if latest:
            cov_dict['latest_status'] = latest.status
            cov_dict['latest_value'] = float(latest.actual_value)
        
        result.append(CovenantResponse(**cov_dict))
    
    return result

@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a loan and all associated data"""
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
    if loan.document_path and os.path.exists(loan.document_path):
        try:
            os.remove(loan.document_path)
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
    
    db.delete(loan)
    db.commit()
    
    logger.info(f"Deleted loan {loan_id}")
    return None
