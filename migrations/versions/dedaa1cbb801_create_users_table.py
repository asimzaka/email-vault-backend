"""create users table

Revision ID: dedaa1cbb801
Revises: 
Create Date: 2024-10-25 18:08:52.524250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR, VARCHAR, BOOLEAN, DATETIME


# revision identifiers, used by Alembic.
revision: str = 'dedaa1cbb801'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('entity_id', CHAR(32), primary_key=True),
        sa.Column('version', CHAR(32), nullable=False),
        sa.Column('previous_version', CHAR(32), nullable=True),
        sa.Column('active', BOOLEAN, default=True),
        sa.Column('changed_by_id', CHAR(32), nullable=False),
        sa.Column('changed_on', DATETIME, nullable=False),
        sa.Column('first_name', VARCHAR(255), nullable=True),
        sa.Column('last_name', VARCHAR(255), nullable=True),
        sa.Column('company_name', VARCHAR(255), nullable=True),
        sa.Column('email', VARCHAR(255), unique=True, nullable=False),
        sa.Column('password', VARCHAR(512), nullable=False),
        sa.Column('referral_code', VARCHAR(255), nullable=True),
        sa.Column('reset_password_token', VARCHAR(255), nullable=True),
        sa.Column('verification_token', VARCHAR(255), nullable=True),
        sa.Column('is_verified', BOOLEAN, default=False)
    )
    op.create_table(
        'user_audit',
        sa.Column('entity_id', CHAR(32), primary_key=True),
        sa.Column('version', CHAR(32), nullable=False),
        sa.Column('previous_version', CHAR(32), nullable=True),
        sa.Column('active', BOOLEAN, default=True),
        sa.Column('changed_by_id', CHAR(32), nullable=False),
        sa.Column('changed_on', DATETIME, nullable=False),
        sa.Column('first_name', VARCHAR(255), nullable=True),
        sa.Column('last_name', VARCHAR(255), nullable=True),
        sa.Column('company_name', VARCHAR(255), nullable=True),
        sa.Column('email', VARCHAR(255), unique=True, nullable=False),
        sa.Column('password', VARCHAR(512), nullable=False),
        sa.Column('referral_code', VARCHAR(255), nullable=True),
        sa.Column('reset_password_token', VARCHAR(255), nullable=True),
        sa.Column('verification_token', VARCHAR(255), nullable=True),
        sa.Column('is_verified', BOOLEAN, default=False)
    )


def downgrade() -> None:
    op.drop_table('user')
    op.drop_table('user_audit')
