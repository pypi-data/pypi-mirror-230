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
Config Extension
"""

from rattail.config import ConfigExtension


class RattailNationBuilderExtension(ConfigExtension):
    """
    Config extension for rattail-nationbuilder
    """
    key = 'rattail_nationbuilder'

    def configure(self, config):

        # rattail import-nationbuilder
        config.setdefault('rattail.importing', 'to_rattail.from_nationbulder.import.default_handler',
                          'rattail_nationbuilder.importing.nationbuilder:FromNationBuilderToRattail')
        config.setdefault('rattail.importing', 'to_rattail.from_nationbuilder.import.default_cmd',
                          'rattail import-nationbuilder')
