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
from datetime import datetime, timedelta
from odoo import http, _
from odoo.exceptions import ValidationError
from odoo.http import request


class TableReservation(http.Controller):

    @http.route(['/table_reservation'], type='http', auth='public', website=True)
    def table_reservation(self):
        pos_config = request.env['res.config.settings'].sudo().search([], limit=1)

        try:
            opening_hour = self.float_to_time(float(pos_config.pos_opening_hour))
            closing_hour = self.float_to_time(float(pos_config.pos_closing_hour))
            interval_difference_hours = float(pos_config.interval_hours)
        except ValueError:
            opening_hour = "00:00"
            closing_hour = "23:59"

        time_slots = self.generate_time_slots(opening_hour, closing_hour, interval_difference_hours)

        return http.request.render(
            "table_reservation_on_website.table_reservation", {
                'opening_hour': opening_hour,
                'closing_hour': closing_hour,
                'time_slots': time_slots
            })

    def float_to_time(self, hour_float):
        hours = int(hour_float)
        minutes = int((hour_float - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def generate_time_slots(self, opening, closing, interval_difference_hours):
        time_format = "%H:%M"
        slots = []
        start_time = datetime.strptime(opening, time_format)
        end_time = datetime.strptime(closing, time_format)

        if not interval_difference_hours:
            interval = timedelta(minutes=30)
            gap = timedelta()
        else:
            interval = timedelta(hours=interval_difference_hours)
            gap = timedelta(minutes=30)

        while start_time + interval <= end_time:
            slot_start = start_time.strftime(time_format)
            slot_end = (start_time + interval).strftime(time_format)
            slots.append(f"{slot_start} - {slot_end}")
            start_time = start_time + interval + gap
        return slots


    @http.route(['/restaurant/floors'], type='http', auth='public', website=True)
    def restaurant_floors(self, **kwargs):
        """ To get floor details """
        floors = request.env['restaurant.floor'].sudo().search([])
        payment = request.env['ir.config_parameter'].sudo().get_param(
            "table_reservation_on_website.reservation_charge")
        refund = request.env['ir.config_parameter'].sudo().get_param(
            'table_reservation_on_website.refund')

        time_slot = kwargs.get('time_slot')
        start_time = end_time = None
        if time_slot and " - " in time_slot:
            start_time, end_time = [t.strip() for t in time_slot.split(" - ")]
        vals = {
            'floors': floors,
            'date': kwargs.get('date'),
            'start_time': start_time,
            'end_time': end_time,
            'payment': payment,
            'refund': refund,
        }
        return http.request.render(
            "table_reservation_on_website.restaurant_floors", vals)

    @http.route(['/restaurant/floors/tables'], type='json', auth='public', website=True)
    def restaurant_floors_tables(self, **kwargs):
        table_inbetween = {}
        start_time = kwargs.get("start")
        end_time = kwargs.get("end")

        floor_id = int(kwargs.get('floors_id'))
        date = datetime.strptime(kwargs.get('date'), "%Y-%m-%d")
        payment = request.env['ir.config_parameter'].sudo().get_param(
            "table_reservation_on_website.reservation_charge")

        tables = request.env['restaurant.table'].sudo().search([('floor_id', '=', floor_id)])

        reserved = request.env['table.reservation'].sudo().search([
            ('floor_id', '=', floor_id),
            ('date', '=', date),
            ('state', '=', 'reserved'),
            ("starting_at", "<", end_time),
            ("ending_at", ">", start_time)
        ])

        for rec in reserved:
            for table in rec.booked_tables_ids:
                table_inbetween[table.id] = {
                    'start': rec.starting_at,
                    'end': rec.ending_at
                }

        data_tables = {}
        for rec in tables:
            is_reserved = rec.id in table_inbetween
            data_tables[rec.id] = {
                'id': rec.id,
                'name': rec.name,
                'seats': rec.seats,
                'rate': rec.rate if payment else 0,
                'reserved': is_reserved,
                'booked_slot': table_inbetween.get(rec.id, {})
            }
        return data_tables

    @http.route(['/booking/confirm'], type="http", auth="public",
                csrf=False, website=True)
    def booking_confirm(self, **kwargs):
        """ For booking tables """
        company = request.env.company
        if kwargs.get("tables"):
            list_tables = [rec for rec in kwargs.get("tables").split(',')]
            record_tables = request.env['restaurant.table'].sudo().search(
                [('id', 'in', list_tables)])
            amount = [rec.rate for rec in record_tables]
            payment = request.env['ir.config_parameter'].sudo().get_param(
                "table_reservation_on_website.reservation_charge")
            if payment:
                table = request.env.ref(
                    'table_reservation_on_website.product_product_table_booking').sudo()
                table.write({
                    'list_price': sum(amount)
                })
                sale_order = request.website.sale_get_order(force_create=True)
                if sale_order.state != 'draft':
                    request.session['sale_order_id'] = None
                    sale_order = request.website.sale_get_order(
                        force_create=True)
                sale_order.sudo().write({
                    'tables_ids': record_tables,
                    'floors': kwargs.get('floors'),
                    'date': kwargs.get('date'),
                    'starting_at': kwargs.get('start_time'),
                    "ending_at": kwargs.get('end_time'),
                    'booking_amount': sum(amount),
                    'order_line': [
                        (0, 0, {
                            'name': table.name,
                            'product_id': table.id,
                            'product_uom_qty': 1,
                            'price_unit': sum(amount),
                        })],
                })
                sale_order.website_id = request.env['website'].sudo().search(
                    [('company_id', '=', company.id)], limit=1)
                return request.redirect("/shop/cart")
            else:
                partner_ids = request.env["res.partner"].sudo()
                partner = partner_ids.search([("email", "=", kwargs.get("email"))], limit=1)
                table_reservation_vals = {
                    "booked_tables_ids": record_tables,
                    "floor_id": kwargs.get('floors'),
                    "date": kwargs.get('date'),
                    "starting_at": kwargs.get('start_time'),
                    "ending_at": kwargs.get('end_time'),
                    'booking_amount': 0,
                    'state': 'reserved',
                    'type': 'website',
                }
                if not partner:
                    partner_id = partner_ids.create(
                        {"name": kwargs.get("customer_name"),
                         "email": kwargs.get("email"),
                         "phone": kwargs.get("phone")}
                    )
                    table_reservation_vals.update({
                        "customer_id": partner_id.id,
                        "email": kwargs.get("email"),
                        "phone": kwargs.get("phone"),
                        "no_of_persons": kwargs.get("no_of_people")
                    })
                    reservation = request.env['table.reservation'].sudo().create(table_reservation_vals)
                else:
                    table_reservation_vals.update({
                        "customer_id": partner.id,
                        "email": kwargs.get("email"),
                        "phone": kwargs.get("phone"),
                        "no_of_persons": kwargs.get("no_of_people")
                    })
                    reservation = request.env['table.reservation'].sudo().create(table_reservation_vals)

                string = (
                    f'The reservation amount for the selected table is {reservation.booking_amount}.'
                    if reservation.booking_amount > 0 else ''
                )
                list_of_tables = record_tables.mapped('name')
                if len(list_of_tables) > 1:
                    tables_sentence = ', '.join(list_of_tables[:-1]) + ', and ' + list_of_tables[-1]
                else:
                    tables_sentence = list_of_tables[0]
                final_sentence = string + f" You have reserved {tables_sentence}."

                floor = request.env['restaurant.floor'].sudo().browse(int(kwargs.get('floors')))
                company = request.env.company

                body_html = f"""
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f9f9f9; padding:20px; font-family:Arial, sans-serif; color:#333;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="20" cellspacing="0" style="background-color:#ffffff; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                                <tr>
                                    <td align="left" style="padding-bottom:0;">
                                        <p style="margin:20px 0 10px 0;">Dear {reservation.customer_id.name},</p>
                                        <p style="margin:0;">
                                            Thank you for choosing <strong>{company.name}</strong>!<br/>
                                            We’ve received your table reservation request through our website.
                                        </p>
                                        <h3 style="margin:20px 0 10px 0;">Reservation Details:</h3>
                                        <ul style="padding-left:20px; margin:0;">
                                            <li><strong>Name:</strong> {reservation.customer_id.name}</li>
                                            <li><strong>Floor:</strong> {floor.name}</li>
                                            <li><strong>Tables:</strong> {tables_sentence}</li>
                                            <li><strong>Date:</strong> {reservation.date} & <strong>Time:</strong> {reservation.starting_at} to {reservation.ending_at}</li>
                                            <li><strong>Guests:</strong> {reservation.no_of_persons}</li>
                                        </ul>
                                        <p style="margin:20px 0 0 0;">
                                            Kindly note that your reservation request is currently being reviewed. A confirmation email will be sent to you shortly.
                                        </p>
                                        <p>
                                            If you have any special requests or need to make changes, feel free to contact us at <strong>{company.phone or 'N/A'}</strong> or <strong>{company.email or 'N/A'}</strong>.
                                        </p>
                                        <p>
                                            We look forward to welcoming you soon!<br/>
                                            <strong>Warm regards,</strong><br/>
                                            <strong>{company.name}</strong><br/>
                                            <a href="{company.website}" style="color:#1a73e8;">{company.website}</a> | <span>{company.phone or ''}</span>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                """
                request.env['mail.mail'].sudo().create({
                    'subject': "Thank You For Your Table Reservation Request",
                    'email_to': reservation.customer_id.email,
                    'recipient_ids': [request.env.user.partner_id.id],
                    'body_html': body_html,
                }).send()

            return request.redirect("/contactus-thank-you")
        else:
            raise ValidationError(_("Please select table."))

    @http.route(['/table/reservation/pos'], type='json', auth='public',
                website=True)
    def table_reservation_pos(self, table_id):
        """ For pos table booking """
        table = request.env['restaurant.table'].sudo().browse(table_id)
        date_and_time = datetime.now()
        starting_at = (
            (date_and_time + timedelta(hours=5, minutes=30)).time()).strftime(
            "%H:%M")
        end_time = (
            (date_and_time + timedelta(hours=6, minutes=30)).time()).strftime(
            "%H:%M")
        payment = request.env['ir.config_parameter'].sudo().get_param(
            "table_reservation_on_website.reservation_charge")
        if payment:
            request.env['table.reservation'].sudo().create({
                'floor_id': table.floor_id.id,
                'booked_tables_ids': table,
                'date': date_and_time.date(),
                'starting_at': starting_at,
                'ending_at': end_time,
                'booking_amount': table.rate,
                'state': 'reserved',
                'type': 'pos'
            })
        else:
            request.env['table.reservation'].sudo().create({
                'floor_id': table.floor_id.id,
                'booked_tables_ids': table,
                'date': date_and_time.date(),
                'starting_at': starting_at,
                'ending_at': end_time,
                'booking_amount': 0,
                'state': 'reserved',
                'type': 'pos'
            })
        return

    @http.route(['/active/floor/tables'], type='json', auth='public',
                website=True)
    def active_floor_tables(self, floor_id):
        """ To get active floors """
        table_inbetween = []
        product_id = request.env.ref(
            'table_reservation_on_website.'
            'product_product_table_booking_pos')
        for rec in request.env['pos.category'].sudo().search([]):
            if rec:
                product_id.pos_categ_ids = [(4, rec.id, 0)]

        table_reservation = request.env['table.reservation'].sudo().search([(
            'floor_id', "=", floor_id), ('date', '=', datetime.now().date()),
            ('state', '=', 'reserved')])
        for rec in table_reservation:
            start_time = datetime.strptime(rec.starting_at, "%H:%M")
            start_at = start_time - timedelta(
                hours=int(rec.lead_time),
                minutes=int((rec.lead_time % 1) * 100))
            end_at = datetime.strptime(rec.ending_at, "%H:%M").time()
            now = (
                (datetime.now() + timedelta(hours=5,
                                            minutes=30)).time()).strftime(
                "%H:%M")
            if start_at.time() <= datetime.strptime(
                    now, "%H:%M").time() <= end_at:
                for table in rec.booked_tables_ids:
                    table_inbetween.append(table.id)
        return table_inbetween
