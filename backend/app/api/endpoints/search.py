from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List
from app.database import get_db
from app.models.loan import LoanAgreement
from app.models.covenant import Covenant
from app.models.alert import Alert
from app.models.user import User
from app.api.deps import get_current_user
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search", tags=["Search"])

# Search result schemas
class LoanSearchResult(BaseModel):
    id: str
    title: str
    borrower_name: str
    type: str = "loan"
    
    class Config:
        from_attributes = True

class CovenantSearchResult(BaseModel):
    id: str
    name: str
    loan_title: str
    type: str = "covenant"
    
    class Config:
        from_attributes = True

class SearchResults(BaseModel):
    loans: List[LoanSearchResult]
    covenants: List[CovenantSearchResult]
    total: int

@router.get("/", response_model=SearchResults)
def search(
    q: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Global search across loans, covenants, and borrowers
    """
    if not q or len(q.strip()) < 2:
        return SearchResults(loans=[], covenants=[], total=0)
    
    search_term = f"%{q.lower()}%"
    
    # Search loans (title, borrower name)
    loans = db.query(LoanAgreement).filter(
        LoanAgreement.user_id == current_user.id,
        or_(
            func.lower(LoanAgreement.title).like(search_term),
            func.lower(LoanAgreement.borrower_name).like(search_term)
        )
    ).limit(limit).all()
    
    # Search covenants (name)
    covenants = db.query(Covenant).join(LoanAgreement).filter(
        LoanAgreement.user_id == current_user.id,
        func.lower(Covenant.name).like(search_term)
    ).limit(limit).all()
    
    # Format results
    loan_results = [
        LoanSearchResult(
            id=str(loan.id),
            title=loan.title,
            borrower_name=loan.borrower_name or "Unknown",
            type="loan"
        )
        for loan in loans
    ]
    
    covenant_results = [
        CovenantSearchResult(
            id=str(covenant.id),
            name=covenant.name,
            loan_title=covenant.loan.title,
            type="covenant"
        )
        for covenant in covenants
    ]
    
    total = len(loan_results) + len(covenant_results)
    
    logger.info(f"Search query '{q}' returned {total} results for user {current_user.email}")
    
    return SearchResults(
        loans=loan_results,
        covenants=covenant_results,
        total=total
    )
