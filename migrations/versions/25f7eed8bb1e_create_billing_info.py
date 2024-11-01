"""create billing info.

Revision ID: 25f7eed8bb1e
Revises: dedaa1cbb801
Create Date: 2024-10-28 16:06:59.507316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR, VARCHAR, BOOLEAN, DATETIME


# revision identifiers, used by Alembic.
revision: str = '25f7eed8bb1e'
down_revision: Union[str, None] = 'dedaa1cbb801'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'billing_info',
        sa.Column('entity_id', CHAR(32), primary_key=True),
        sa.Column('version', CHAR(32), nullable=False),
        sa.Column('previous_version', CHAR(32), nullable=True),
        sa.Column('active', BOOLEAN, default=True),
        sa.Column('changed_by_id', CHAR(32), nullable=False),
        sa.Column('changed_on', DATETIME, nullable=False),
        sa.Column('user', CHAR(32), nullable=True),
        sa.Column('name_on_card', VARCHAR(255), nullable=True),
        sa.Column('card_number', VARCHAR(255), nullable=True),
        sa.Column('expiration_date', VARCHAR(255), nullable=True),
        sa.Column('cvv', VARCHAR(255), unique=True, nullable=False)
    )
    op.create_table(
        'billing_info_audit',
        sa.Column('entity_id', CHAR(32), primary_key=True),
        sa.Column('version', CHAR(32), nullable=False),
        sa.Column('previous_version', CHAR(32), nullable=True),
        sa.Column('active', BOOLEAN, default=True),
        sa.Column('changed_by_id', CHAR(32), nullable=False),
        sa.Column('changed_on', DATETIME, nullable=False),
        sa.Column('user', CHAR(32), nullable=True),
        sa.Column('name_on_card', VARCHAR(255), nullable=True),
        sa.Column('card_number', VARCHAR(255), nullable=True),
        sa.Column('expiration_date', VARCHAR(255), nullable=True),
        sa.Column('cvv', VARCHAR(255), unique=True, nullable=False)
    )


def downgrade() -> None:
    op.drop_table('user')
    op.drop_table('user_audit')
