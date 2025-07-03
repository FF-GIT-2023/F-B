from odoo import models, api, _
from markupsafe import escape

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def send_cust_mail(self, mail_data):
        partner_id = int(mail_data['partner'][0])
        delivery_time = mail_data['time']
        sale_order = mail_data['sale_order']
        order_lines = mail_data['lines']
        order_number = sale_order['order_line'][0]['display_name'].split(' - ')[0]
        partner = self.env['res.partner'].browse(partner_id)
        if not partner.email:
            return {'error': _('Customer has no email address.')}

        subject = _("%s, Your Order is on its Way!") % partner.name
        email_from = self.env.company.email or "no-reply@example.com"
        company = self.env.company
        order_lines_html = ""

        for line in order_lines:
            product_name = escape(line.get('product_id')[1])
            qty = line.get('product_uom_qty')
            total = float(line.get('price_total'))
            order_lines_html += f"""
                <tr>
                    <td style="text-align: left;">{product_name}</td>
                    <td style="text-align: center;">{qty}</td>
                    <td style="text-align: center;">{total:.2f}</td>
                </tr>
            """

        body_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
            <p><strong>Dear {partner.name},</strong></p>
            <p>Thank you for your order with <strong>{company.name}</strong>!</p>
            <p>We are pleased to confirm that your order has been successfully received and it’s currently being prepared.</p>
            <p>Below are the details of your order:</p>

            <hr>
            <h3>Order Summary</h3>
            <ul>
                <li><strong>Order Number:</strong> {order_number}</li>
                <li><strong>Customer Name:</strong> {partner.name}</li>
                <li><strong>Delivery Address:</strong> {partner.street}, {partner.street2}, {partner.zip}, {partner.city}, {partner.state_id.name}, {partner.country_id.name}</li>
                <li><strong>Phone Number:</strong> {partner.phone}</li>
            </ul>
            <hr>

            <h3>Items Ordered</h3>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; text-align: center; font-size: 13px;">
                <thead style="background-color: #f2f2f2;">
                    <tr>
                        <th style="text-align: left;">Item</th>
                        <th>Quantity</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {order_lines_html}
                </tbody>
            </table>

            <br>
            <h3>Delivery Details</h3>
            <ul>
                <li><strong>Estimated Delivery Time:</strong> {delivery_time} minutes</li>
                <li><strong>Delivery Type:</strong> Home Delivery</li>
            </ul>

            <hr>
            <p>If you have any questions or need to make changes to your order, please contact us at {company.email} or call us at {company.phone}.</p>
            <p>Thank you for choosing <strong>{company.name}</strong>. We hope you enjoy your meal!</p>

            <p>Best Regards,<br>
            {company.name}<br>
            {company.website} | {company.phone}</p>
        </div>
        """


        mail_values = {
            'subject': subject,
            'body_html': body_html,
            'email_to': partner.email,
            'email_from': email_from,
        }
        self.env['mail.mail'].create(mail_values).send()

        return {'success': True}


    @api.model
    def cancel_sale_order_by_id(self, order_id):
        order = self.env['sale.order'].sudo().browse(order_id)
        order.write({"state": "cancel"})
        company = self.env.company
        if order:
            order.sudo().action_cancel()
            subject = _("Your Order Has Been Cancelled – [Order #%s]" % order.name)

            reason = "The item(s) you ordered are currently unavailable due to high demand."

            body_html = f"""
                <p><strong>Subject:</strong> Your Order Has Been Cancelled – Order #{order.name}</p>
                <p><strong>Dear {order.partner_id.name},</strong></p>

                <p>We regret to inform you that your recent order placed on {order.date_order.strftime('%Y-%m-%d')} via our platform has been <strong>cancelled</strong>.</p>
                <hr>
                <p><strong>Order Number:</strong> {order.name}<br/>
                <strong>Order Time:</strong> {order.date_order.strftime('%H:%M')}<br/>
                <strong>Delivery Address:</strong> {order.partner_id.street}, {order.partner_id.street2}, {order.partner_id.zip}, {order.partner_id.city}, {order.partner_id.state_id.name}, {order.partner_id.country_id.name}</p>
                <hr>
                <p><strong>Reason for Cancellation:</strong><br/>
                {reason}</p>

                <p>We sincerely apologize for the inconvenience this may have caused. If payment has already been made, a full refund will be processed within 2 business days, depending on your payment method.</p>

                <p>If you have any questions or need further assistance, feel free to reach out to our support team at {company.email} / {company.phone}.</p>

                <p>We appreciate your understanding and hope to serve you again soon.</p>

                <p>Best Regards,<br>
                {company.name}<br>
                {company.website} | {company.phone}</p>
            """

            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': order.partner_id.email,
                'email_from': self.env.company.email or "no-reply@example.com",
            }
            self.env['mail.mail'].create(mail_values).send()
        return True