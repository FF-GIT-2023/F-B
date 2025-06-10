from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools import format_date


class PosPaymentReportWizard(models.TransientModel):
    _name = "payment.report.wiz"
    _description = "POS Payment Report Wizard"

    start_date = fields.Date(
        string="Start Date",
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    end_date = fields.Date(
        string="End Date",
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    payment_method_id = fields.Many2one(
        "pos.payment.method",
        string="Payment Method",
    )

    def action_generate_report(self):
        self.ensure_one()

        if self.start_date > self.end_date:
            raise UserError(_("Start Date cannot be after End Date."))

        domain = [
            ("date_order", ">=", self.start_date),
            ("date_order", "<=", self.end_date),
        ]
        if self.payment_method_id:
            domain.append(
                ("payment_ids.payment_method_id", "=", self.payment_method_id.id)
            )

        orders = self.env["pos.order"].search(domain)
        if not orders:
            raise UserError(_("No POS orders found for the selected period."))

        currency_symbol = self.env.user.company_id.currency_id.symbol
        order_data, total_amount = [], 0.0

        for order in orders:
            payments = order.payment_ids
            if self.payment_method_id:
                payments = payments.filtered(
                    lambda p: p.payment_method_id == self.payment_method_id
                )

            payment_names = ", ".join(payments.mapped("payment_method_id.name"))
            customer = order.partner_id.display_name or _("Not Assigned")
            order_data.append(
                {
                    "reference": order.name,
                    "customer": customer,
                    "payment_method": payment_names,
                    "amount": round(order.amount_total, 2),
                }
            )
            total_amount += order.amount_total

        return self.env.ref("ff_payment_report.report_payment").report_action(
            None,
            data={
                "orders": order_data,
                "total_amount": round(total_amount, 2),
                "currency_symbol": currency_symbol,
                "start_date": format_date(self.env, self.start_date),
                "end_date": format_date(self.env, self.end_date),

            },
        )
