"""empty message

Revision ID: 5fda3dd79dce
Revises: fc6e98491798
Create Date: 2022-12-11 00:26:34.541892

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5fda3dd79dce'
down_revision = 'fc6e98491798'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cookies', sa.Column('past_due', sa.Integer(), nullable=False))
    op.add_column('cookies', sa.Column('convertibility', sa.Integer(), nullable=False))
    op.drop_column('cookies', 'flag')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cookies', sa.Column('flag', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('cookies', 'convertibility')
    op.drop_column('cookies', 'past_due')
    # ### end Alembic commands ###