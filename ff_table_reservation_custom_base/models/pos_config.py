from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    interval_hours_bool = fields.Boolean("Time Slot Hour",
                                         help="Set difference for time slots restaurant table reservation")
    interval_hours = fields.Float(
        string="Table Reservation Interval (Hours)",
        store=True)

    reservation_alert_lead_time_bool = fields.Boolean("Reservation Alert Boolean")
    reservation_alert_lead_time = fields.Float(
        string="Reservation Alert Lead Time (hours)",
        default=1.0,
        help="Number of hours before a reservation to trigger an alert in POS."
    )