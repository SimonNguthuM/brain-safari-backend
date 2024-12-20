"""empty message

Revision ID: 41ee6b4dd0dc
Revises: 4c4620b5ce74
Create Date: 2024-11-16 20:12:58.566642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41ee6b4dd0dc'
down_revision = '4c4620b5ce74'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TYPE IF EXISTS user_roles_enum")
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)

    # ### end Alembic commands ###
