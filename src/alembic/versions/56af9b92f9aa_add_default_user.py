"""add default user

Revision ID: 56af9b92f9aa
Revises: cb0489f5ecfe
Create Date: 2022-02-12 20:41:27.558478

"""
import sqlalchemy as sa

from alembic import op



# revision identifiers, used by Alembic.
revision = '56af9b92f9aa'
down_revision = 'cb0489f5ecfe'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "INSERT INTO user VALUES (test_user, test2@email.com, $2b$12$weBWKfMBr5PrBd/zoc2C8O9skLoZnJSxu4uLMVsLK1RoDeCpca5j6, TRUE)"
    )



def downgrade():
    op.execute(
        "DELETE FROM user WHERE id in 1"
    )
