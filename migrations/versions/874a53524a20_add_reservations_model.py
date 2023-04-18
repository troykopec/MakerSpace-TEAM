"""'Add_Reservations_Model'

Revision ID: 874a53524a20
Revises: 4af2ea372151
Create Date: 2023-03-21 12:49:25.457692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '874a53524a20'
down_revision = '4af2ea372151'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reservations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userid', sa.Integer(), nullable=True),
    sa.Column('machineid', sa.Integer(), nullable=True),
    sa.Column('selected_date', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reservations')
    # ### end Alembic commands ###
