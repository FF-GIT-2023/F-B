from odoo import models
from odoo.fields import Command

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _invoice_sale_orders(self):
        for tx in self.filtered(lambda tx: tx.sale_order_ids):
            tx = tx.with_company(tx.company_id)

            confirmed_orders = tx.sale_order_ids.filtered(lambda so: so.state == 'sale')
            if confirmed_orders:
                fully_paid_orders = confirmed_orders.filtered(lambda so: so._is_paid())

                downpayment_invoices = (
                    confirmed_orders - fully_paid_orders
                )._generate_downpayment_invoices()

                fully_paid_orders._force_lines_to_invoice_policy_order()

                invoices = downpayment_invoices

                for invoice in invoices:
                    invoice._portal_ensure_token()
                tx.invoice_ids = [Command.set(invoices.ids)]


    # def _invoice_sale_orders(self):
    #     for tx in self.filtered(lambda tx: tx.sale_order_ids):
    #         tx = tx.with_company(tx.company_id)
    #
    #         confirmed_orders = tx.sale_order_ids.filtered(lambda so: so.state == 'sale')
    #         if confirmed_orders:
    #             fully_paid_orders = confirmed_orders.filtered(lambda so: so._is_paid())
    #
    #             downpayment_invoices = (
    #                 confirmed_orders - fully_paid_orders
    #             )._generate_downpayment_invoices()
    #
    #             final_invoices = self.env['account.move']
    #
    #             for order in fully_paid_orders:
    #                 order.message_post(body="Invoice creation skipped due to customization.")
    #
    #             invoices = downpayment_invoices + final_invoices
    #
    #             for invoice in invoices:
    #                 invoice._portal_ensure_token()
    #
    #             tx.invoice_ids = [Command.set(invoices.ids)]
