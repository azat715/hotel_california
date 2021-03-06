"""add identity order, remove guest field

Revision ID: ce06f7cb2bd9
Revises: cb0489f5ecfe
Create Date: 2022-02-13 16:22:55.201087

"""
import sqlalchemy as sa

from alembic import op



# revision identifiers, used by Alembic.
revision = 'ce06f7cb2bd9'
down_revision = 'cb0489f5ecfe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('identity', sa.Integer(), nullable=True))
    op.drop_column('orders', 'guest')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('guest', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('orders', 'identity')
    # ### end Alembic commands ###
