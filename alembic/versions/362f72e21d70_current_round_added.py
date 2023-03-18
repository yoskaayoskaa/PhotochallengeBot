"""'current_round_added'

Revision ID: 362f72e21d70
Revises: decd02f1d9d5
Create Date: 2023-03-07 11:47:58.724607

"""
import sqlalchemy as sa

from alembic import op

# Have added column 'current_round' to 'games' table

# revision identifiers, used by Alembic.
revision = "362f72e21d70"
down_revision = "decd02f1d9d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("games", sa.Column("current_round", sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("games", "current_round")
    # ### end Alembic commands ###
