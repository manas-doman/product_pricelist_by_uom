from odoo import api, fields, models
from odoo.tools.translate import _


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    pricelist_uom_id = fields.Many2one('uom.uom', string='Pricelist UoM', help="Unit of Measure used for this pricelist item. If not set, the product's default unit of measure will be used.")


    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        super()._onchange_product_tmpl_id()
        if self.product_tmpl_id and not self.pricelist_uom_id:
            self.pricelist_uom_id = self.product_tmpl_id.uom_id
        else :
            self.pricelist_uom_id = False
