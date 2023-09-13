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
NationBuilder Cache Person views
"""

from rattail_nationbuilder.db.model import NationBuilderCachePerson

from webhelpers2.html import HTML

from .master import NationBuilderMasterView


class NationBuilderCachePersonView(NationBuilderMasterView):
    """
    Master view for NationBuilder Users
    """
    model_class = NationBuilderCachePerson
    url_prefix = '/nationbuilder/cache/people'
    route_prefix = 'nationbuilder.cache.people'
    has_versions = True

    labels = {
        'id': "ID",
        'external_id': "External ID",
        'primary_image_url_ssl': "Primary Image URL",
        'primary_address_address1': "Address 1",
        'primary_address_address2': "Address 2",
        'primary_address_city': "City",
        'primary_address_state': "State",
        'primary_address_zip': "Zip",
    }

    grid_columns = [
        'id',
        'external_id',
        'first_name',
        'last_name',
        'email',
        'mobile',
        'updated_at',
    ]

    form_fields = [
        'id',
        'signup_type',
        'external_id',
        'first_name',
        'middle_name',
        'last_name',
        'email',
        'email_opt_in',
        'mobile',
        'mobile_opt_in',
        'phone',
        'primary_address_address1',
        'primary_address_address2',
        'primary_address_city',
        'primary_address_state',
        'primary_address_zip',
        'primary_image_url_ssl',
        'tags',
        'note',
        'created_at',
        'updated_at',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)

        g.set_link('external_id')
        if 'external_id' in g.filters:
            g.filters['external_id'].default_active = True
            g.filters['external_id'].default_verb = 'contains'

        g.set_link('id')
        g.set_link('first_name')
        g.set_link('last_name')
        g.set_link('email')

        g.set_sort_defaults('updated_at', 'desc')

    def render_tags(self, person, field):
        tags = getattr(person, field)
        if not tags:
            return

        items = []
        for tag in self.rattail_config.parse_list(tags):
            items.append(HTML.tag('li', c=[tag]))
        return HTML.tag('ul', c=items)

    def configure_form(self, f):
        super().configure_form(f)

        f.set_renderer('tags', self.render_tags)


def defaults(config, **kwargs):
    base = globals()

    NationBuilderCachePersonView = kwargs.get('NationBuilderCachePersonView', base['NationBuilderCachePersonView'])
    NationBuilderCachePersonView.defaults(config)


def includeme(config):
    defaults(config)
