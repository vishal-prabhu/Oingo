"""empty message

Revision ID: cc34f6c0e804
Revises: a02b8503a5e2
Create Date: 2018-12-06 12:29:28.252973

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cc34f6c0e804'
down_revision = 'a02b8503a5e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_friends')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_friends',
    sa.Column('origin_user', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('other_user', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('friend_status', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.Column('request_sent_timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('request_response_timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['origin_user'], ['user.id'], name='user_friends_origin_user_fkey'),
    sa.ForeignKeyConstraint(['other_user'], ['user.id'], name='user_friends_other_user_fkey')
    )
    # ### end Alembic commands ###
