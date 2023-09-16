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
App Handler supplement
"""

from rattail.app import RattailProvider, GenericHandler


class NationBuilderProvider(RattailProvider):
    """
    App provider for NationBuilder integration.
    """

    def get_nationbuilder_handler(self, **kwargs):
        if 'nationbuilder' not in self.handlers:
            spec = self.config.get('rattail', 'nationbuilder.handler',
                                   default='rattail_nationbuilder.app:NationBuilderHandler')
            factory = self.load_object(spec)
            self.handlers['nationbuilder'] = factory(self.config, **kwargs)
        return self.handlers['nationbuilder']


class NationBuilderHandler(GenericHandler):
    """
    Handler for NationBuilder integration.
    """

    def get_url(self, require=False, **kwargs):
        """
        Returns the base URL for the NationBuilder web app.
        """
        getter = self.config.require if require else self.config.get
        url = getter('nationbuilder', 'url')
        if url:
            return url.rstrip('/')
