from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ Inheriting res config settings to add reservation details """
    _inherit = 'res.config.settings'

    pos_interval_hours_bool = fields.Boolean(
        related="pos_config_id.interval_hours_bool",
        readonly=False,
        help="Set difference for time slots restaurant table reservation"
    )
    interval_hours = fields.Float(
        related="pos_config_id.interval_hours",
        string="Table Reservation Interval (Hours)",
        readonly=False
    )
    reservation_alert_lead_time_bool = fields.Boolean("Reservation Alert Boolean",
                                                      related="pos_config_id.reservation_alert_lead_time_bool",
                                                      readonly=False)
    reservation_alert_lead_time = fields.Float(
        related="pos_config_id.reservation_alert_lead_time",
        string="Reservation Alert Lead Time (hours)",
        default=1.0,
        readonly=False,
        help="Number of hours before a reservation to trigger an alert in POS."
    )