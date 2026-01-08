from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.models.user_activity import UserActivity
from app.schemas.user_settings import (
    UserProfileUpdate,
    UserPreferencesUpdate,
    UserPreferences as UserPreferencesSchema,
    UserActivityItem
)
from app.schemas.user import UserResponse
from app.api.deps import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["User Settings"])

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db:Session = Depends(get_db)
):
    """Update user profile"""
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.company is not None:
        current_user.company = profile_data.company
    
    db.commit()
    db.refresh(current_user)
    
    # Log activity
    activity = UserActivity(
        user_id=current_user.id,
        action="profile_update",
        description="Updated profile information"
    )
    db.add(activity)
    db.commit()
    
    logger.info(f"User {current_user.email} updated profile")
    return current_user

@router.get("/preferences", response_model=UserPreferencesSchema)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notification preferences"""
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    # Create default preferences if they don't exist
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return prefs

@router.put("/preferences", response_model=UserPreferencesSchema)
def update_preferences(
    prefs_data: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user notification preferences"""
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    # Create if doesn't exist
    if not prefs:
        prefs = UserPreferences(
            user_id=current_user.id,
            email_alerts=prefs_data.email_alerts,
            weekly_reports=prefs_data.weekly_reports,
            system_updates=prefs_data.system_updates
        )
        db.add(prefs)
    else:
        prefs.email_alerts = prefs_data.email_alerts
        prefs.weekly_reports = prefs_data.weekly_reports
        prefs.system_updates = prefs_data.system_updates
    
    db.commit()
    db.refresh(prefs)
    
    # Log activity
    activity = UserActivity(
        user_id=current_user.id,
        action="preferences_update",
        description="Updated notification preferences"
    )
    db.add(activity)
    db.commit()
    
    logger.info(f"User {current_user.email} updated preferences")
    return prefs

@router.get("/activity", response_model=List[UserActivityItem])
def get_activity(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user activity log"""
    activities = db.query(UserActivity).filter(
        UserActivity.user_id == current_user.id
    ).order_by(UserActivity.created_at.desc()).limit(limit).all()
    
    return activities
