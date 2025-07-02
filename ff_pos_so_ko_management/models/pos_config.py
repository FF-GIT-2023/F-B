from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    delivery_time_bool = fields.Boolean("Delivery Time Boolean")

    delivery_time_options = fields.Char(
        store=True,
        string="Delivery Time Options (comma-separated)",
        help="Enter delivery time options in minutes, separated by commas. E.g. 10,20,30"
    )
