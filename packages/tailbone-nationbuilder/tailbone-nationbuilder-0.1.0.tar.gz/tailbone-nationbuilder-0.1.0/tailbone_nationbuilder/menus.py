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
Common menus for NationBuilder
"""

from rattail_nationbuilder.nationbuilder.util import get_nationbuilder_url


def make_nationbuilder_menu(request):
    url = request.route_url

    nationbuilder_menu = {
        'title': "NationBuilder",
        'type': 'menu',
        'items': [
            {
                'title': "People",
                'route': 'nationbuilder.cache.people',
                'perm': 'nationbuilder.cache.people.list',
            },
        ],
    }

    url = get_nationbuilder_url(request.rattail_config)
    if url:
        nationbuilder_menu['items'].insert(
            0, {
                'title': "Go to NationBuilder",
                'url': f'{url}/admin/',
                'target': '_blank',
            })
        nationbuilder_menu['items'].insert(
            1, {'type': 'sep'})

    return nationbuilder_menu
