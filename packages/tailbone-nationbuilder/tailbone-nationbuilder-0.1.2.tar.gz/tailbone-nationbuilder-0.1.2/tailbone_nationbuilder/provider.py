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
Tailbone Provider for NationBuilder Integration
"""

from tailbone.providers import TailboneProvider


class TailboneNationBuilderProvider(TailboneProvider):
    """
    View provider for tailbone-nationbuilder
    """
    key = 'tailbone_nationbuilder'

    def make_integration_menu(self, request, **kwargs):
        from tailbone_nationbuilder.menus import make_nationbuilder_menu
        return make_nationbuilder_menu(request)
