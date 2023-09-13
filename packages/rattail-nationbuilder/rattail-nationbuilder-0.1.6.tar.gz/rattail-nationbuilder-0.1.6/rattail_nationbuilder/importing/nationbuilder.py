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
NationBuilder -> Rattail importing
"""

import datetime
from collections import OrderedDict

from rattail import importing
from rattail_nationbuilder import importing as nationbuilder_importing
from rattail_nationbuilder.nationbuilder.webapi import NationBuilderWebAPI


class FromNationBuilderToRattail(importing.ToRattailHandler):
    """
    Import handler for NationBuilder -> Rattail
    """
    host_key = 'nationbuilder'
    host_title = "NationBuilder"
    generic_host_title = "NationBuilder"

    def get_importers(self):
        importers = OrderedDict()
        importers['NationBuilderCachePerson'] = NationBuilderCachePersonImporter
        return importers


class FromNationBuilder(importing.Importer):
    """
    Base class for all NationBuilder importers
    """

    def setup(self):
        super().setup()
        self.setup_api()

    def setup_api(self):
        self.nationbuilder = NationBuilderWebAPI(self.config)


class NationBuilderCachePersonImporter(FromNationBuilder, nationbuilder_importing.model.NationBuilderCachePersonImporter):
    """
    Importer for NB Person cache
    """
    key = 'id'

    primary_address_fields = [
        'primary_address_address1',
        'primary_address_address2',
        'primary_address_city',
        'primary_address_state',
        'primary_address_zip',
    ]

    supported_fields = [
        'id',
        'created_at',
        'email',
        'email_opt_in',
        'external_id',
        'first_name',
        'middle_name',
        'last_name',
        'mobile',
        'mobile_opt_in',
        'note',
        'phone',
        'primary_image_url_ssl',
        'signup_type',
        'tags',
        'updated_at',
    ] + primary_address_fields

    def get_host_objects(self):
        return self.nationbuilder.get_people(page_size=500)

    def normalize_timestamp(self, value):
        if not value:
            return

        dt = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        dt = self.app.localtime(dt)
        return self.app.make_utc(dt)

    def normalize_host_object(self, person):

        # nb. some fields may not be present in person dict
        data = dict([(field, person.get(field))
                     for field in self.fields])
        if data:

            for field in ('created_at', 'updated_at'):
                data[field] = self.normalize_timestamp(data[field])

            if 'tags' in self.fields:
                tags = data['tags']
                if tags:
                    data['tags'] = self.config.make_list_string(tags)

            if self.fields_active(self.primary_address_fields):
                address = person.get('primary_address')
                if address:
                    data.update({
                        'primary_address_address1': address['address1'],
                        'primary_address_address2': address['address2'],
                        'primary_address_state': address['state'],
                        'primary_address_city': address['city'],
                        'primary_address_zip': address['zip'],
                    })

            return data
