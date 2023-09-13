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
NationBuilder Cache Donation views
"""

from rattail_nationbuilder.db.model import NationBuilderCacheDonation

from .master import NationBuilderMasterView


class NationBuilderCacheDonationView(NationBuilderMasterView):
    """
    Master view for NationBuilder donations cache
    """
    model_class = NationBuilderCacheDonation
    url_prefix = '/nationbuilder/cache/donations'
    route_prefix = 'nationbuilder.cache.donations'
    has_versions = True

    labels = {
        'id': "ID",
        'author_id': "Author ID",
        'membership_id': "Membership ID",
        'donor_id': "Donor ID",
        'donor_external_id': "Donor External ID",
        'tracking_code_slug': "Tracking Code",
    }

    grid_columns = [
        'id',
        'donor_external_id',
        'amount',
        'payment_type_name',
        'check_number',
        'tracking_code_slug',
        'created_at',
        'succeeded_at',
        'failed_at',
        'canceled_at',
    ]

    form_fields = [
        'id',
        'amount',
        'payment_type_name',
        'check_number',
        'tracking_code_slug',
        'author_id',
        'membership_id',
        'donor_id',
        'donor_external_id',
        'email',
        'note',
        'created_at',
        'succeeded_at',
        'failed_at',
        'canceled_at',
        'updated_at',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)

        g.set_link('id')

        g.set_link('donor_id')

        g.set_link('donor_external_id')
        if 'donor_external_id' in g.filters:
            g.filters['donor_external_id'].default_active = True
            g.filters['donor_external_id'].default_verb = 'contains'

        g.set_type('amount', 'currency')

        g.set_sort_defaults('created_at', 'desc')

    def configure_form(self, f):
        super().configure_form(f)

        f.set_type('amount', 'currency')


def defaults(config, **kwargs):
    base = globals()

    NationBuilderCacheDonationView = kwargs.get('NationBuilderCacheDonationView', base['NationBuilderCacheDonationView'])
    NationBuilderCacheDonationView.defaults(config)


def includeme(config):
    defaults(config)
