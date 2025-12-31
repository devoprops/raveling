"""add style_attributes to effect_style

Revision ID: 001_add_style_attributes
Revises: 
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_style_attributes'
down_revision = '000_add_user_color'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add style_attributes column to effect_styles table
    # This column stores type-specific attributes (range, area, duration, cost, affected_attributes)
    op.add_column('effect_styles', sa.Column('style_attributes', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove style_attributes column
    op.drop_column('effect_styles', 'style_attributes')
