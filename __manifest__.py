{
    'name': 'Product Pricelist By UOM',
    'category': 'Sales/Sales',
    'summary': 'Customize adding condition sale uom on pricelist',
    'version': '19.0.1.0.0',
    'description': """
Product Pricelist by UOM
========================

Overview
--------
Extends Odoo's standard pricelist functionality to support price rules based
on a sales Unit of Measure (UOM) that differs from the product's base UOM.

Problem Solved
--------------
By default, Odoo pricelist rules are tied to the product's base unit only.
This module allows merchants to define separate pricing per alternative UOM —
for example:

  - Product base UOM : Unit   → 5 THB / Unit
  - Alternative UOM  : Dozen  → 45 THB / Dozen

Features
--------
- Add a "Sales UOM" condition field on pricelist items.
- Price lookup respects the UOM chosen on the sale order line.
- Fully compatible with existing Odoo pricelist strategies (fixed price,
  discount, formula).
- Works alongside standard UOM conversion; no double-conversion risk.

Use Case
--------
Suitable for businesses that sell the same product in multiple packaging
units with independent pricing (retail vs. wholesale packs, pieces vs. boxes,
etc.).
    """,
    'depends': ['sale'],
    'data': [
        'views/product_pricelist_item_views.xml',
    ],
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'auto_install': False,
    'author': 'Doman Soft',
    'license': 'LGPL-3',
    'price' : 15.00,
    'currency': 'USD',
}
