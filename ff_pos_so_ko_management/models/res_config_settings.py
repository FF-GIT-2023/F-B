from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    delivery_time_bool = fields.Boolean("Delivery Time Boolean",
                                        related='pos_config_id.delivery_time_bool',
                                        readonly=False)
    delivery_time_options = fields.Char(
        related='pos_config_id.delivery_time_options',
        readonly=False,
        string="Delivery Time Options (comma-separated)",
        help="Enter delivery time options in minutes, separated by commas. E.g. 10,20,30"
    )


