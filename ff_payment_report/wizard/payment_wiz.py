from odoo import models, fields
from odoo.exceptions import UserError


class PosPaymentReportWizard(models.TransientModel):
    _name = 'payment.report.wiz'
    _description = 'POS Payment Report Wizard'

    start_date = fields.Date(string="Start Date", default=fields.Date.today)
    end_date = fields.Date(string="End Date", default=fields.Date.today)
    payment_method_id = fields.Many2one('pos.payment.method', string="Payment Method")

    def action_generate_report(self):
        if self.start_date > self.end_date:
            raise UserError("Start Date cannot be after End Date.")

        domain = [
            ("date_order", ">=", self.start_date),
            ("date_order", "<=", self.end_date),
        ]

        orders = self.env["pos.order"].search(domain, order="date_order asc")

        if not orders:
            raise UserError("No POS orders found for the selected date range.")

        currency_symbol = self.env.user.currency_id.symbol
        order_data = []
        total_amount = 0.0

        for order in orders:
            customer = order.partner_id.name or "Walk-in Customer"
            payment_methods = ', '.join(order.payment_ids.mapped('payment_method_id.name'))
            total_amount += order.amount_total

            order_data.append({
                "reference": order.name,
                "customer": customer,
                "payment_method": payment_methods,
                "amount":round(order.amount_total,2),
            })
        return self.env.ref("ff_payment_report.report_payment").report_action(
            None,
            data={
                "orders": order_data,
                "total_amount": round(total_amount,2),
                "currency_symbol":currency_symbol,
                "start_date": self.start_date.strftime("%d/%m/%Y"),
                "end_date": self.end_date.strftime("%d/%m/%Y"),
            },
        )