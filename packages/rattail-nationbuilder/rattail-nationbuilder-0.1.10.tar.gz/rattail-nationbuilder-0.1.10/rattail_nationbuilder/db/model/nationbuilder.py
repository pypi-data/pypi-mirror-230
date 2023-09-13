# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
NationBuilder cache tables
"""

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model
from rattail.db.util import normalize_full_name
from rattail.config import parse_list


class NationBuilderCachePerson(model.Base):
    """
    Represents a Person record in NationBuilder.

    https://apiexplorer.nationbuilder.com/nationbuilder#People
    """
    __tablename__ = 'nationbuilder_cache_person'
    __table_args__ = (
        sa.UniqueConstraint('id', name='nationbuilder_cache_person_uq_id'),
    )
    __versioned__ = {}
    model_title = "NationBuilder Person"
    model_title_plural = "NationBuilder People"

    uuid = model.uuid_column()

    id = sa.Column(sa.Integer(), nullable=False)
    signup_type = sa.Column(sa.Integer(), nullable=True)
    external_id = sa.Column(sa.String(length=50), nullable=True)
    tags = sa.Column(sa.String(length=255), nullable=True)
    first_name = sa.Column(sa.String(length=100), nullable=True)
    middle_name = sa.Column(sa.String(length=100), nullable=True)
    last_name = sa.Column(sa.String(length=100), nullable=True)
    email = sa.Column(sa.String(length=255), nullable=True)
    email_opt_in = sa.Column(sa.Boolean(), nullable=True)
    mobile = sa.Column(sa.String(length=50), nullable=True)
    mobile_opt_in = sa.Column(sa.Boolean(), nullable=True)
    phone = sa.Column(sa.String(length=50), nullable=True)
    primary_address_address1 = sa.Column(sa.String(length=100), nullable=True)
    primary_address_address2 = sa.Column(sa.String(length=100), nullable=True)
    primary_address_city = sa.Column(sa.String(length=100), nullable=True)
    primary_address_state = sa.Column(sa.String(length=50), nullable=True)
    primary_address_zip = sa.Column(sa.String(length=10), nullable=True)
    primary_image_url_ssl = sa.Column(sa.String(length=255), nullable=True)
    note = sa.Column(sa.Text(), nullable=True)
    created_at = sa.Column(sa.DateTime(), nullable=True)
    updated_at = sa.Column(sa.DateTime(), nullable=True)

    def __str__(self):
        return normalize_full_name(self.first_name, self.last_name)

    def has_tag(self, tag):
        if self.tags:
            for value in parse_list(self.tags):
                if value == tag:
                    return True
        return False


class NationBuilderCacheDonation(model.Base):
    """
    Represents a Donation record in NationBuilder.

    https://apiexplorer.nationbuilder.com/nationbuilder#Donations
    """
    __tablename__ = 'nationbuilder_cache_donation'
    __table_args__ = (
        sa.UniqueConstraint('id', name='nationbuilder_cache_donation_uq_id'),
    )
    __versioned__ = {}
    model_title = "NationBuilder Donation"
    model_title_plural = "NationBuilder Donations"

    uuid = model.uuid_column()

    id = sa.Column(sa.Integer(), nullable=False)
    author_id = sa.Column(sa.Integer(), nullable=True)
    membership_id = sa.Column(sa.Integer(), nullable=True)
    donor_id = sa.Column(sa.Integer(), nullable=True)
    donor_external_id = sa.Column(sa.String(length=50), nullable=True)
    email = sa.Column(sa.String(length=255), nullable=True)
    amount = sa.Column(sa.Numeric(precision=10, scale=2), nullable=True)
    payment_type_name = sa.Column(sa.String(length=100), nullable=True)
    check_number = sa.Column(sa.String(length=255), nullable=True)
    tracking_code_slug = sa.Column(sa.String(length=255), nullable=True)
    note = sa.Column(sa.Text(), nullable=True)
    created_at = sa.Column(sa.DateTime(), nullable=True)
    succeeded_at = sa.Column(sa.DateTime(), nullable=True)
    failed_at = sa.Column(sa.DateTime(), nullable=True)
    canceled_at = sa.Column(sa.DateTime(), nullable=True)
    updated_at = sa.Column(sa.DateTime(), nullable=True)
