"""empty message

Revision ID: a02b8503a5e2
Revises: ddf469ad2906
Create Date: 2018-12-06 01:23:32.510309

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a02b8503a5e2'
down_revision = 'ddf469ad2906'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('friends',
    sa.Column('origin_user', sa.Integer(), nullable=False),
    sa.Column('other_user', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=True),
    sa.Column('request_sent_timestamp', sa.DateTime(), nullable=True),
    sa.Column('request_response_timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['origin_user'], ['user.id'], ),
    sa.ForeignKeyConstraint(['other_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('origin_user', 'other_user')
    )
    op.drop_table('association')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('association',
    sa.Column('left_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('right_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('status', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['left_id'], ['user.id'], name='association_left_id_fkey'),
    sa.ForeignKeyConstraint(['right_id'], ['user.id'], name='association_right_id_fkey'),
    sa.PrimaryKeyConstraint('left_id', 'right_id', name='association_pkey')
    )
    op.drop_table('friends')
    # ### end Alembic commands ###