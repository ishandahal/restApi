"""add content column to posts table

Revision ID: e83b8a931bc7
Revises: d58c569bd6ca
Create Date: 2023-05-11 08:52:40.655867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e83b8a931bc7'
down_revision = 'd58c569bd6ca'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
