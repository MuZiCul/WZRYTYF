"""empty message

Revision ID: 74577572e8b8
Revises: e303d3a9ca0f
Create Date: 2022-12-14 23:59:41.561019

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74577572e8b8'
down_revision = 'e303d3a9ca0f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cookies', sa.Column('wx', sa.String(length=100), nullable=False))
    op.create_unique_constraint(None, 'cookies', ['wx'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'cookies', type_='unique')
    op.drop_column('cookies', 'wx')
    # ### end Alembic commands ###
