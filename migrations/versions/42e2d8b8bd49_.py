"""empty message

Revision ID: 42e2d8b8bd49
Revises: ec9896600b91
Create Date: 2018-12-12 20:33:32.824824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42e2d8b8bd49'
down_revision = 'ec9896600b91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('note',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=150), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('creation_timestamp', sa.DateTime(), nullable=True),
    sa.Column('region_id', sa.Integer(), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=True),
    sa.Column('is_shared_with_friends', sa.Boolean(), nullable=True),
    sa.Column('is_commentable', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['region_id'], ['region.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('note_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('parent_comment_id', sa.Integer(), nullable=True),
    sa.Column('content', sa.String(length=150), nullable=True),
    sa.ForeignKeyConstraint(['note_id'], ['note.id'], ),
    sa.ForeignKeyConstraint(['parent_comment_id'], ['comment.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('note_patterns',
    sa.Column('note_id', sa.Integer(), nullable=True),
    sa.Column('recurrence_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['note_id'], ['note.id'], ),
    sa.ForeignKeyConstraint(['recurrence_id'], ['recurrence_pattern.id'], )
    )
    op.create_table('note_tags',
    sa.Column('note_id', sa.Integer(), nullable=True),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['note_id'], ['note.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], )
    )
    op.create_table('note_visibility',
    sa.Column('note_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['note_id'], ['note.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('note_visibility')
    op.drop_table('note_tags')
    op.drop_table('note_patterns')
    op.drop_table('comment')
    op.drop_table('note')
    # ### end Alembic commands ###
