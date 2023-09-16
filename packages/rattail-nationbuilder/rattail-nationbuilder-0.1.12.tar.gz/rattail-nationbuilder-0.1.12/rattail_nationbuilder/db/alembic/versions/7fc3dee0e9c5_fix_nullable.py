# -*- coding: utf-8; -*-
"""fix nullable

Revision ID: 7fc3dee0e9c5
Revises: c3cb75afcae2
Create Date: 2023-09-13 09:12:33.740638

"""

# revision identifiers, used by Alembic.
revision = '7fc3dee0e9c5'
down_revision = 'c3cb75afcae2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # nationbuilder_cache_donation
    op.alter_column('nationbuilder_cache_donation_version', 'id',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=False)


def downgrade():

    # nationbuilder_cache_donation
    op.alter_column('nationbuilder_cache_donation_version', 'id',
               existing_type=sa.INTEGER(),
               nullable=False,
               autoincrement=False)
