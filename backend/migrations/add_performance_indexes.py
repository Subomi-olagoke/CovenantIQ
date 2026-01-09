"""Add performance indexes

Revision ID: add_performance_indexes
Revises: 
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    # Loans table indexes
    op.create_index('idx_loans_user_id', 'loans', ['user_id'])
    op.create_index('idx_loans_created_at', 'loans', ['created_at'])
    op.create_index('idx_loans_user_created', 'loans', ['user_id', 'created_at'])
    
    # Covenants table indexes
    op.create_index('idx_covenants_loan_id', 'covenants', ['loan_id'])
    op.create_index('idx_covenants_status', 'covenants', ['status'])
    op.create_index('idx_covenants_loan_status', 'covenants', ['loan_id', 'status'])
    
    # Alerts table indexes
    op.create_index('idx_alerts_user_id', 'alerts', ['user_id'])
    op.create_index('idx_alerts_severity', 'alerts', ['severity'])
    op.create_index('idx_alerts_created_at', 'alerts', ['created_at'])
    op.create_index('idx_alerts_user_severity', 'alerts', ['user_id', 'severity'])
    
    # User preferences table index
    op.create_index('idx_user_preferences_user_id', 'user_preferences', ['user_id'])
    
    # User activity table indexes
    op.create_index('idx_user_activity_user_id', 'user_activity', ['user_id'])
    op.create_index('idx_user_activity_created_at', 'user_activity', ['created_at'])
    op.create_index('idx_user_activity_user_created', 'user_activity', ['user_id', 'created_at'])


def downgrade():
    # Drop all indexes
    op.drop_index('idx_loans_user_id', 'loans')
    op.drop_index('idx_loans_created_at', 'loans')
    op.drop_index('idx_loans_user_created', 'loans')
    
    op.drop_index('idx_covenants_loan_id', 'covenants')
    op.drop_index('idx_covenants_status', 'covenants')
    op.drop_index('idx_covenants_loan_status', 'covenants')
    
    op.drop_index('idx_alerts_user_id', 'alerts')
    op.drop_index('idx_alerts_severity', 'alerts')
    op.drop_index('idx_alerts_created_at', 'alerts')
    op.drop_index('idx_alerts_user_severity', 'alerts')
    
    op.drop_index('idx_user_preferences_user_id', 'user_preferences')
    
    op.drop_index('idx_user_activity_user_id', 'user_activity')
    op.drop_index('idx_user_activity_created_at', 'user_activity')
    op.drop_index('idx_user_activity_user_created', 'user_activity')
