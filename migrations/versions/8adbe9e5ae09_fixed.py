"""'fixed'

Revision ID: 8adbe9e5ae09
Revises: 
Create Date: 2024-03-02 22:24:08.250584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8adbe9e5ae09'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Cookies',
    sa.Column('session_id', sa.String(), nullable=False),
    sa.Column('jwt_token', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('session_id')
    )
    op.create_table('One-time sales',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('percentage', sa.Integer(), nullable=False),
    sa.Column('comment', sa.TEXT(), nullable=True),
    sa.Column('start_at', postgresql.TIME(), nullable=True),
    sa.Column('end_at', postgresql.TIME(), nullable=False),
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('categories', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('creator', sa.String(), nullable=False),
    sa.Column('coordinates', postgresql.ARRAY(sa.DECIMAL()), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Repeated sales',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('percentage', sa.Integer(), nullable=False),
    sa.Column('comment', sa.TEXT(), nullable=True),
    sa.Column('start_at', postgresql.TIME(), nullable=False),
    sa.Column('end_at', postgresql.TIME(), nullable=False),
    sa.Column('weekday', sa.String(), nullable=False),
    sa.Column('categories', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('creator', sa.String(), nullable=False),
    sa.Column('coordinates', postgresql.ARRAY(sa.DECIMAL()), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Users table',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('surname', sa.String(length=256), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('created_at', sa.DATE(), nullable=True),
    sa.Column('updated_at', sa.DATE(), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Users table')
    op.drop_table('Repeated sales')
    op.drop_table('One-time sales')
    op.drop_table('Cookies')
    # ### end Alembic commands ###