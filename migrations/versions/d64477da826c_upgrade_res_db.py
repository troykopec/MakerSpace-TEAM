"""'Upgrade-Res-DB'

Revision ID: d64477da826c
Revises: 874a53524a20
Create Date: 2023-03-28 13:31:40.468607

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd64477da826c'
down_revision = '874a53524a20'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reservations', schema=None) as batch_op:
        batch_op.alter_column('machineid',
               existing_type=mysql.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reservations', schema=None) as batch_op:
        batch_op.alter_column('machineid',
               existing_type=sa.String(length=255),
               type_=mysql.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###