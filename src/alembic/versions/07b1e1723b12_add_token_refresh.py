"""add token_refresh

Revision ID: 07b1e1723b12
Revises: f3a7bd31a332
Create Date: 2022-02-06 21:20:28.650246

"""
import sqlalchemy as sa

from alembic import op



# revision identifiers, used by Alembic.
revision = '07b1e1723b12'
down_revision = 'f3a7bd31a332'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('refresh_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('value', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('refresh_token')
    # ### end Alembic commands ###
