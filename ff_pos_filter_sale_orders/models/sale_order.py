from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pos_sale_order_filter = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done')],
        'Website Order Status', readonly=True, default='draft')