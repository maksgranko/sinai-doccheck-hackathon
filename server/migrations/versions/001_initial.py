"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы documents
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=100), nullable=True),
        sa.Column('issuer', sa.String(length=255), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )
    
    # Создание индексов
    op.create_index('idx_document_id', 'documents', ['document_id'])
    op.create_index('idx_status', 'documents', ['status'])
    op.create_index('idx_expiry_date', 'documents', ['expiry_date'])
    
    # Создание таблицы verifications
    op.create_table(
        'verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_verifications_document', 'verifications', ['document_id'])
    op.create_index('idx_verifications_date', 'verifications', ['verified_at'])


def downgrade() -> None:
    op.drop_index('idx_verifications_date', table_name='verifications')
    op.drop_index('idx_verifications_document', table_name='verifications')
    op.drop_table('verifications')
    op.drop_index('idx_expiry_date', table_name='documents')
    op.drop_index('idx_status', table_name='documents')
    op.drop_index('idx_document_id', table_name='documents')
    op.drop_table('documents')


