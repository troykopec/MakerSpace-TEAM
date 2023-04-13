"""Add_Posts_Model

Revision ID: a1e7c301c1c8
Revises: 802c4a6a4b00
Create Date: 2023-04-11 12:43:18.378628

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a1e7c301c1c8'
down_revision = '802c4a6a4b00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('slug')
        batch_op.drop_column('author')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', mysql.VARCHAR(length=255), nullable=True))
        batch_op.add_column(sa.Column('slug', mysql.VARCHAR(length=255), nullable=True))

    # ### end Alembic commands ###