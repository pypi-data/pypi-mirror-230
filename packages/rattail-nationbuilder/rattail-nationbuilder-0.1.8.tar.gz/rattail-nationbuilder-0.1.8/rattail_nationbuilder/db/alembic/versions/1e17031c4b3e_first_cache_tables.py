# -*- coding: utf-8; -*-
"""first cache tables

Revision ID: 1e17031c4b3e
Revises: fa3aec1556bc
Create Date: 2023-09-12 15:05:08.853989

"""

# revision identifiers, used by Alembic.
revision = '1e17031c4b3e'
down_revision = None
branch_labels = ('rattail_nationbuilder',)
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # nationbuilder_cache_person
    op.create_table('nationbuilder_cache_person',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('email_opt_in', sa.Boolean(), nullable=True),
                    sa.Column('external_id', sa.String(length=50), nullable=True),
                    sa.Column('first_name', sa.String(length=100), nullable=True),
                    sa.Column('middle_name', sa.String(length=100), nullable=True),
                    sa.Column('last_name', sa.String(length=100), nullable=True),
                    sa.Column('mobile', sa.String(length=50), nullable=True),
                    sa.Column('mobile_opt_in', sa.Boolean(), nullable=True),
                    sa.Column('note', sa.Text(), nullable=True),
                    sa.Column('phone', sa.String(length=50), nullable=True),
                    sa.Column('primary_image_url_ssl', sa.String(length=255), nullable=True),
                    sa.Column('signup_type', sa.Integer(), nullable=True),
                    sa.Column('primary_address_address1', sa.String(length=100), nullable=True),
                    sa.Column('primary_address_address2', sa.String(length=100), nullable=True),
                    sa.Column('primary_address_city', sa.String(length=100), nullable=True),
                    sa.Column('primary_address_state', sa.String(length=50), nullable=True),
                    sa.Column('primary_address_zip', sa.String(length=10), nullable=True),
                    sa.Column('tags', sa.Text(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('id', name='nationbuilder_cache_person_uq_id')
                    )
    op.create_table('nationbuilder_cache_person_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('created_at', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('email', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('email_opt_in', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('external_id', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('first_name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('middle_name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('last_name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('mobile', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('mobile_opt_in', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('note', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('phone', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('primary_image_url_ssl', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('signup_type', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('primary_address_address1', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('primary_address_address2', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('primary_address_city', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('primary_address_state', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('primary_address_zip', sa.String(length=10), autoincrement=False, nullable=True),
                    sa.Column('tags', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_nationbuilder_cache_person_version_end_transaction_id'), 'nationbuilder_cache_person_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_nationbuilder_cache_person_version_operation_type'), 'nationbuilder_cache_person_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_nationbuilder_cache_person_version_transaction_id'), 'nationbuilder_cache_person_version', ['transaction_id'], unique=False)


def downgrade():

    # nationbuilder_cache_person
    op.drop_index(op.f('ix_nationbuilder_cache_person_version_transaction_id'), table_name='nationbuilder_cache_person_version')
    op.drop_index(op.f('ix_nationbuilder_cache_person_version_operation_type'), table_name='nationbuilder_cache_person_version')
    op.drop_index(op.f('ix_nationbuilder_cache_person_version_end_transaction_id'), table_name='nationbuilder_cache_person_version')
    op.drop_table('nationbuilder_cache_person_version')
    op.drop_table('nationbuilder_cache_person')
