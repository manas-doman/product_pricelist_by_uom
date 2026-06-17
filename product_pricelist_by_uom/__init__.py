from . import models

def _post_init_hook(env):
    _setup_initial_price_uom(env)

def _setup_initial_price_uom(env):
    for company in env.companies:
        pricelist_items_without_uom = env['product.pricelist.item'].with_company(company).search([('product_tmpl_id', '!=', False), ('pricelist_uom_id', '=', False)])
        for item in pricelist_items_without_uom:
            if item.product_tmpl_id:
                item.pricelist_uom_id = item.product_tmpl_id.uom_id.id