"""init

Revision ID: 9aefffb77d37
Revises: 
Create Date: 2022-01-12 11:10:05.945763

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '9aefffb77d37'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sport',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(op.f('ix_sport_id'), 'sport', ['id'], unique=False)
    op.create_index(op.f('ix_sport_name'), 'sport', ['name'], unique=True)

    op.create_table('team',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('city', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['sport_id'], ['sport.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(op.f('ix_team_city'), 'team', ['city'], unique=False)
    op.create_index(op.f('ix_team_id'), 'team', ['id'], unique=False)
    op.create_index(op.f('ix_team_name'), 'team', ['name'], unique=False)
    op.create_index(op.f('ix_team_sport_id'), 'team', ['sport_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_team_sport_id'), table_name='team')
    op.drop_index(op.f('ix_team_name'), table_name='team')
    op.drop_index(op.f('ix_team_id'), table_name='team')
    op.drop_index(op.f('ix_team_city'), table_name='team')
    op.drop_table('team')
    op.drop_index(op.f('ix_sport_name'), table_name='sport')
    op.drop_index(op.f('ix_sport_id'), table_name='sport')
    op.drop_table('sport')
    # ### end Alembic commands ###
