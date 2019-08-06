"""empty message

Revision ID: ddf469ad2906
Revises: 1678e209b1f6
Create Date: 2018-12-06 00:54:58.102105

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddf469ad2906'
down_revision = '1678e209b1f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('association',
    sa.Column('left_id', sa.Integer(), nullable=False),
    sa.Column('right_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['left_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['right_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('left_id', 'right_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('association')
    # ### end Alembic commands ###