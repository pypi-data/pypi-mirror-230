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
NationBuilder utils
"""

import warnings


def get_nationbuilder_url(config):
    warnings.warn("get_nationbuilder_url() function is deprecated; "
                  "please use nationbuilder_handler.get_url() instead",
                  DeprecationWarning, stacklevel=2)

    app = config.get_app()
    nationbuilder = app.get_nationbuilder_handler()
    return nationbuilder.get_url()
