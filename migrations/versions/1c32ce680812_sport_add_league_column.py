"""Sport add league column

Revision ID: 1c32ce680812
Revises: be0c2c580afa
Create Date: 2022-07-17 04:06:18.483346

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = '1c32ce680812'
down_revision = 'be0c2c580afa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sport', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('league', sa.Enum('AHL', 'NHL', 'MLB', 'NFL', 'CFL', 'NBA', 'WNBA', name='leagueenum'),
                      nullable=False))
        batch_op.drop_index('ix_sport_name')
        batch_op.create_index(batch_op.f('ix_sport_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_sport_league'), ['league'], unique=True)
        batch_op.create_unique_constraint('sport_name_league_unique_idx', ['name', 'league'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('sport', schema=None) as batch_op:
        batch_op.drop_constraint('sport_name_league_unique_idx', type_='unique')
        batch_op.drop_index(batch_op.f('ix_sport_league'))
        batch_op.drop_index(batch_op.f('ix_sport_name'))
        batch_op.create_index('ix_sport_name', ['name'], unique=False)
        batch_op.drop_column('league')

    # ### end Alembic commands ###
