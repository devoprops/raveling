"""add user_color to users

Revision ID: 000_add_user_color
Revises: 
Create Date: 2025-01-01 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '000_add_user_color'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user_color column to users table
    # This column stores hex color for collaboration notes
    op.add_column('users', sa.Column('user_color', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove user_color column
    op.drop_column('users', 'user_color')
