"""limit tag name length

Revision ID: dd4491f4198c
Revises: 43e1a810e56f
Create Date: 2026-02-12 00:04:21.038532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd4491f4198c'
down_revision = '43e1a810e56f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.TEXT(),
               type_=sa.String(length=30),
               existing_nullable=False)

def downgrade():
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.String(length=30),
               type_=sa.TEXT(),
               existing_nullable=False)
