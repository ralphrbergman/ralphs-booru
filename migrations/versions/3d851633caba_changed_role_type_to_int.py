"""Changed role type to int

Revision ID: 3d851633caba
Revises: 9877037168ec
Create Date: 2026-01-21 18:59:11.026116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d851633caba'
down_revision = '9877037168ec'
branch_labels = None
depends_on = None


role_map = {
    'adm': 3,
    'mod': 2,
    'reg': 1,
    'ter': 0
}

def upgrade():
    op.alter_column('user', 'role', new_column_name='role_old')
    op.add_column('user', sa.Column('role', sa.Integer(), nullable=True))

    connection = op.get_bind()
    for string_val, int_val in role_map.items():
        connection.execute(
            sa.text(f"UPDATE \"user\" SET role = {int_val} WHERE role_old = '{string_val}'")
        )

    op.drop_column('user', 'role_old')


def downgrade():
    op.add_column('user', sa.Column('role_old', sa.String(length=10), nullable=True))
    
    connection = op.get_bind()
    inv_map = {v: k for k, v in role_map.items()}
    for int_val, string_val in inv_map.items():
        connection.execute(
            sa.text(f"UPDATE \"user\" SET role_old = '{string_val}' WHERE role = {int_val}")
        )
        
    op.drop_column('user', 'role')
    op.alter_column('user', 'role_old', new_column_name='role')
