"""add user table

Revision ID: 437eeaac5dc8
Revises: e83b8a931bc7
Create Date: 2023-05-11 08:57:03.360269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '437eeaac5dc8'
down_revision = 'e83b8a931bc7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    pass


def downgrade():
    op.drop_table('users')
    pass
