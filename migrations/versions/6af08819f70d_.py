"""Revert quiz_content columns to nullable for seeding

Revision ID: 6af08819f70d
Revises: 890de685394f
Create Date: 2024-11-20 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6af08819f70d'
down_revision = '890de685394f'
branch_labels = None
depends_on = None


def upgrade():
    # Make columns nullable to support seeding
    with op.batch_alter_table('quiz_content', schema=None) as batch_op:
        batch_op.alter_column('question', nullable=True)
        batch_op.alter_column('options', nullable=True)
        batch_op.alter_column('correct_option', nullable=True)

    with op.batch_alter_table('quiz_submissions', schema=None) as batch_op:
        batch_op.alter_column('selected_option', nullable=True)


def downgrade():
    # Revert columns to NOT NULL
    with op.batch_alter_table('quiz_content', schema=None) as batch_op:
        batch_op.alter_column('question', nullable=False)
        batch_op.alter_column('options', nullable=False)
        batch_op.alter_column('correct_option', nullable=False)

    with op.batch_alter_table('quiz_submissions', schema=None) as batch_op:
        batch_op.alter_column('selected_option', nullable=False)
