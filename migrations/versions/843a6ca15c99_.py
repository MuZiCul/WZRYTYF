"""empty message

Revision ID: 843a6ca15c99
Revises: 04d951f70bed
Create Date: 2022-12-12 15:59:41.777846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '843a6ca15c99'
down_revision = '04d951f70bed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cookies_log',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('qq', sa.String(length=100), nullable=False),
    sa.Column('remarks', sa.String(length=100), nullable=True),
    sa.Column('states', sa.Integer(), nullable=False),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('qq'),
    sa.UniqueConstraint('remarks')
    )
    op.add_column('cookies', sa.Column('Notifications', sa.Integer(), nullable=True))
    op.add_column('cookies', sa.Column('contact', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cookies', 'contact')
    op.drop_column('cookies', 'Notifications')
    op.drop_table('cookies_log')
    # ### end Alembic commands ###
