"""добавлено поле для введенных попыток

Revision ID: 2ff820197d8d
Revises: 2c49d9860626
Create Date: 2022-04-24 13:11:11.486134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ff820197d8d'
down_revision = '2c49d9860626'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('entered_words', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'entered_words')
    # ### end Alembic commands ###
