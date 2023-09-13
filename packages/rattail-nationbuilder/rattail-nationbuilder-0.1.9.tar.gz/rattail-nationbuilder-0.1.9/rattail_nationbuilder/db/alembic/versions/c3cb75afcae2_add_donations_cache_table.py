# -*- coding: utf-8; -*-
"""add donations cache table

Revision ID: c3cb75afcae2
Revises: 1e17031c4b3e
Create Date: 2023-09-12 19:30:47.583505

"""

# revision identifiers, used by Alembic.
revision = 'c3cb75afcae2'
down_revision = '1e17031c4b3e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # nationbuilder_cache_donation
    op.create_table('nationbuilder_cache_donation',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('author_id', sa.Integer(), nullable=True),
                    sa.Column('membership_id', sa.Integer(), nullable=True),
                    sa.Column('donor_id', sa.Integer(), nullable=True),
                    sa.Column('donor_external_id', sa.String(length=50), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('payment_type_name', sa.String(length=100), nullable=True),
                    sa.Column('check_number', sa.String(length=255), nullable=True),
                    sa.Column('tracking_code_slug', sa.String(length=255), nullable=True),
                    sa.Column('note', sa.Text(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('succeeded_at', sa.DateTime(), nullable=True),
                    sa.Column('failed_at', sa.DateTime(), nullable=True),
                    sa.Column('canceled_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('id', name='nationbuilder_cache_donation_uq_id')
                    )
    op.create_table('nationbuilder_cache_donation_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
                    sa.Column('author_id', sa.Integer(), nullable=True),
                    sa.Column('membership_id', sa.Integer(), nullable=True),
                    sa.Column('donor_id', sa.Integer(), nullable=True),
                    sa.Column('donor_external_id', sa.String(length=50), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('payment_type_name', sa.String(length=100), nullable=True),
                    sa.Column('check_number', sa.String(length=255), nullable=True),
                    sa.Column('tracking_code_slug', sa.String(length=255), nullable=True),
                    sa.Column('note', sa.Text(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('succeeded_at', sa.DateTime(), nullable=True),
                    sa.Column('failed_at', sa.DateTime(), nullable=True),
                    sa.Column('canceled_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_nationbuilder_cache_donation_version_end_transaction_id'), 'nationbuilder_cache_donation_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_nationbuilder_cache_donation_version_operation_type'), 'nationbuilder_cache_donation_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_nationbuilder_cache_donation_version_transaction_id'), 'nationbuilder_cache_donation_version', ['transaction_id'], unique=False)


def downgrade():

    # nationbuilder_cache_donation
    op.drop_index(op.f('ix_nationbuilder_cache_donation_version_transaction_id'), table_name='nationbuilder_cache_donation_version')
    op.drop_index(op.f('ix_nationbuilder_cache_donation_version_operation_type'), table_name='nationbuilder_cache_donation_version')
    op.drop_index(op.f('ix_nationbuilder_cache_donation_version_end_transaction_id'), table_name='nationbuilder_cache_donation_version')
    op.drop_table('nationbuilder_cache_donation_version')
    op.drop_table('nationbuilder_cache_donation')
