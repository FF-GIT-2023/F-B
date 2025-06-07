# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Aysha Shalin (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import SUPERUSER_ID


class WebsiteSalePayment(WebsiteSale):
    """ For creating new record for table reservation """
    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, sale_order_id=None, **post):
        """ Payment Validate page """
        if sale_order_id is None:
            order = request.website.sale_get_order()
            if not order and 'sale_last_order_id' in request.session:
                last_order_id = request.session['sale_last_order_id']
                order = request.env['sale.order'].sudo().browse(last_order_id).exists()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        errors = self._get_shop_payment_errors(order)
        if errors:
            first_error = errors[0]
            raise ValidationError(f"{first_error[0]}\n{first_error[1]}")

        tx_sudo = order.get_portal_last_transaction() if order else order.env['payment.transaction']
        if order.tables_ids:
            reservation = request.env['table.reservation'].sudo().create({
                "customer_id": order.partner_id.id,
                "booked_tables_ids": order.tables_ids,
                "floor_id": order.floors,
                "date": order.date,
                "email": order.partner_id.email,
                "phone": order.partner_id.phone,
                "starting_at": order.starting_at,
                "ending_at": order.ending_at,
                'booking_amount': order.booking_amount,
                'state': 'reserved',
                'type': 'website'
            })

            price = order.order_line[0].price_unit
            string = f'The reservation amount for the selected table is {price}.' if price > 0 else ''
            list_of_tables = reservation.booked_tables_ids.mapped('name')
            tables_sentence = ', '.join(list_of_tables[:-1]) + ', and ' + list_of_tables[-1] if len(list_of_tables) > 1 else list_of_tables[0]
            final_sentence = f"{string} You have reserved table {tables_sentence}."

            company = request.env.company
            floor_name = request.env['restaurant.floor'].sudo().browse(int(order.floors)).name
            user_name = request.env.user.name

            body_html = f"""
            <table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;">
                <tr><td align="center">
                    <table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: white; color: #454748; border-collapse:separate;">
                        <tbody>
                            <!-- HEADER -->
                            <tr>
                                <td align="center" style="min-width: 590px;">
                                    <table border="0" cellpadding="0" cellspacing="0" width="590" style="background-color: white; padding: 0px 8px;">
                                        <tr>
                                            <td valign="middle">
                                                <span style="font-size: 10px;">{reservation.sequence}</span><br/>
                                                <span style="font-size: 20px; font-weight: bold;">Table Reservation</span>
                                            </td>
                                            <td valign="middle" align="right">
                                                <img src="/logo.png?company={company.id}" style="width: 80px;"/>
                                            </td>
                                        </tr>
                                        <tr><td colspan="2" style="text-align:center;">
                                            <hr style="background-color:rgb(204,204,204); border:none; height:1px; margin: 16px 0;" />
                                        </td></tr>
                                    </table>
                                </td>
                            </tr>

                            <!-- CONTENT -->
                            <tr>
                                <td align="center" style="min-width: 590px;">
                                    <table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 0px 8px;">
                                        <tr>
                                            <td valign="top" style="font-size: 13px;">
                                                <div>
                                                    Dear {user_name},<br/><br/>
                                                    Your table booking at {floor_name} has been confirmed on {reservation.date} for {reservation.starting_at} to {reservation.ending_at}. {final_sentence}
                                                    <br/><br/>
                                                    Best regards<br/>
                                                </div>
                                            </td>
                                        </tr>
                                        <tr><td style="text-align:center;">
                                            <hr style="background-color:rgb(204,204,204); border:none; height:1px; margin: 16px 0;" />
                                        </td></tr>
                                    </table>
                                </td>
                            </tr>

                            <!-- FOOTER -->
                            <tr>
                                <td align="center">
                                    <table border="0" cellpadding="0" cellspacing="0" width="590" style="font-size: 11px; padding: 0px 8px;">
                                        <tr>
                                            <td align="left">
                                                {company.name}<br/>
                                                {company.phone or ''}
                                            </td>
                                            <td align="right">
                                                <a href="mailto:{company.email}" style="text-decoration:none; color: #5e6061;">{company.email}</a><br/>
                                                <a href="{company.website}" style="text-decoration:none; color: #5e6061;">{company.website}</a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td></tr>
            </table>
            """

            request.env['mail.mail'].sudo().create({
                'subject': "Table reservation",
                'email_to': reservation.customer_id.email,
                'recipient_ids': [request.env.user.partner_id.id],
                'body_html': body_html,
            }).send()

            order.table_reservation_id = reservation.id

        if not order or (order.amount_total and not tx_sudo):
            return request.redirect('/shop')

        if order and not order.amount_total and not tx_sudo:
            order.with_context(send_email=True).with_user(SUPERUSER_ID).action_confirm()
            return request.redirect(order.get_portal_url())

        request.website.sale_reset()

        if tx_sudo and tx_sudo.state == 'draft':
            return request.redirect('/shop')

        return request.redirect('/shop/confirmation')
