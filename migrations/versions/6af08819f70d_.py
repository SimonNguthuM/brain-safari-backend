"""empty message

Revision ID: 6af08819f70d
Revises: 890de685394f
Create Date: 2024-11-20 21:31:55.409439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6af08819f70d'
down_revision = '890de685394f'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add columns as nullable
    with op.batch_alter_table('quiz_content', schema=None) as batch_op:
        batch_op.add_column(sa.Column('question', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('options', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('correct_option', sa.String(), nullable=True))
        batch_op.drop_column('type')
        batch_op.drop_column('is_correct')
        batch_op.drop_column('content_text')

    with op.batch_alter_table('quiz_submissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('selected_option', sa.String(), nullable=True))

    # Step 2: Populate existing rows with default values
    op.execute("UPDATE quiz_content SET question = 'Default Question', options = '[]', correct_option = 'A'")
    op.execute("UPDATE quiz_submissions SET selected_option = 'A'")

    # Step 3: Alter columns to make them NOT NULL
    with op.batch_alter_table('quiz_content', schema=None) as batch_op:
        batch_op.alter_column('question', nullable=False)
        batch_op.alter_column('options', nullable=False)
        batch_op.alter_column('correct_option', nullable=False)

    with op.batch_alter_table('quiz_submissions', schema=None) as batch_op:
        batch_op.alter_column('selected_option', nullable=False)


def downgrade():
    # Reverse the changes in the downgrade function
    with op.batch_alter_table('quiz_submissions', schema=None) as batch_op:
        batch_op.drop_column('selected_option')

    with op.batch_alter_table('quiz_content', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_text', sa.TEXT(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('is_correct', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.drop_column('correct_option')
        batch_op.drop_column('options')
        batch_op.drop_column('question')
