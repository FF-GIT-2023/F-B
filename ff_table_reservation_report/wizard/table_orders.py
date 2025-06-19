from odoo import _, fields, models
from odoo.exceptions import UserError


class FloorReportWizard(models.TransientModel):
    _name = "floor.report.wiz"
    _description = "Table Reservation Report Wizard"

    start_date = fields.Date(
        string="Start Date", default=lambda self: fields.Date.context_today(self)
    )
    end_date = fields.Date(
        string="End Date", default=lambda self: fields.Date.context_today(self)
    )
    floor_ids = fields.Many2many(
        comodel_name="restaurant.floor",
        string="Select Floor",
        required=True,
    )

    def action_generate_report(self):
        self.ensure_one()

        if self.start_date > self.end_date:
            raise UserError(_("Start date must not be after end date."))

        reservations = self.env["table.reservation"].search(
            [
                ("floor_id", "in", self.floor_ids.ids),
                ("date", ">=", self.start_date),
                ("date", "<=", self.end_date),
            ]
        )

        if not reservations:
            raise UserError(
                _("No reservations found for the selected period and floor.")
            )

        data = []
        for res in reservations:
            data.append(
                {
                    "sequence": res.sequence or "",
                    "customer": res.customer_id.name or "",
                    "phone": res.phone or "",
                    "no_of_persons": res.no_of_persons or 0,
                    "date": res.date,
                    "tables": ", ".join(res.booked_tables_ids.mapped("name")),
                    "floor": res.floor_id.name or "",
                    "starting_at": res.starting_at or "",
                    "ending_at": res.ending_at or "",
                }
            )
        return self.env.ref(
            "ff_table_reservation_report.action_report_table_reservation"
        ).report_action(
            self,
            data={
                "reservations": data,
                "start_date": self.start_date,
                "end_date": self.end_date,
            },
        )
