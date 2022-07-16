"""alter team add unique constraint

Revision ID: be0c2c580afa
Revises: 9aefffb77d37
Create Date: 2022-01-17 15:57:40.925728

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'be0c2c580afa'
down_revision = '9aefffb77d37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.create_unique_constraint('team_name_city_sport_unique_idx', ['name', 'city', 'sport_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.drop_constraint('team_name_city_sport_unique_idx', type_='unique')

    # ### end Alembic commands ###