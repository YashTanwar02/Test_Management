"""Initial migration

Revision ID: 82686dc222dd
Revises: 
Create Date: 2025-03-23 09:39:58.821278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82686dc222dd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_type', sa.String(length=100), nullable=False),
    sa.Column('language', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('profile_picture', sa.String(length=255), nullable=True),
    sa.Column('otp', sa.String(length=6), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('allocated_tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('test_type_id', sa.Integer(), nullable=False),
    sa.Column('assigned_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['test_type_id'], ['test_types.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('exam_attempts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('test_type_id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('total_questions', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('attempted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['test_type_id'], ['test_types.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_master',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_type_id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('question_image', sa.String(length=255), nullable=True),
    sa.Column('option_a', sa.String(length=255), nullable=False),
    sa.Column('option_b', sa.String(length=255), nullable=False),
    sa.Column('option_c', sa.String(length=255), nullable=False),
    sa.Column('option_d', sa.String(length=255), nullable=False),
    sa.Column('correct_option', sa.String(length=1), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['test_type_id'], ['test_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_type', sa.String(length=50), nullable=False),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('attempts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('test_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('attempted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('attempts')
    op.drop_table('tests')
    op.drop_table('test_master')
    op.drop_table('exam_attempts')
    op.drop_table('allocated_tests')
    op.drop_table('users')
    op.drop_table('test_types')
    # ### end Alembic commands ###
