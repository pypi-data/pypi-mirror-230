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
rattail-nationbuilder version importing
"""

from rattail.importing import versions as base


class NationBuilderVersionMixin(object):

    def add_nationbuilder_importers(self, importers):
        importers['NationBuilderCachePerson'] = NationBuilderCachePersonImporter
        importers['NationBuilderCacheDonation'] = NationBuilderCacheDonationImporter
        return importers


class NationBuilderCachePersonImporter(base.VersionImporter):

    @property
    def host_model_class(self):
        return self.model.NationBuilderCachePerson


class NationBuilderCacheDonationImporter(base.VersionImporter):

    @property
    def host_model_class(self):
        return self.model.NationBuilderCacheDonation
