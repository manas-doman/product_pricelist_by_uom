
from collections import defaultdict
from datetime import timedelta
from markupsafe import Markup

from odoo import models
from odoo.tools.translate import _


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def _compute_price_rule(
            self, products, quantity, *, currency=None, uom=None, date=False, compute_price=True,
            **kwargs
    ):
        if uom not in [None, '']:
            kwargs['sale_uom'] = uom
        result = super()._compute_price_rule(products, quantity, currency=currency, uom=uom, date=date, compute_price=compute_price, **kwargs)
        return result

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        domain = super()._get_applicable_rules_domain(products, date, **kwargs)
        if 'sale_uom' in kwargs and len(products) == 1:
            uom = kwargs['sale_uom']
            domain.insert(1, ('pricelist_uom_id', '=', uom.id))
        return domain