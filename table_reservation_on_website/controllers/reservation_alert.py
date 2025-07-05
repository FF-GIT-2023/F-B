from odoo import http
from odoo.http import request
from datetime import datetime, timedelta


class POSReservationAlert(http.Controller):

    @http.route('/pos/reservation_alert', type='json', auth='user')
    def reservation_alert(self):
        now = datetime.now()
        config = request.env['pos.config'].sudo().search([], limit=1)
        lead_hours = config.reservation_alert_lead_time or 1
        current_date = now.date()

        reservations = request.env['table.reservation'].sudo().search([
            ('date', '=', current_date),
        ])

        alerts = []
        for res in reservations:
            try:
                start_time_str = res.starting_at.strip()
                if len(start_time_str.split(":")) == 3:
                    res_start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
                else:
                    res_start_time = datetime.strptime(start_time_str, "%H:%M").time()

                res_datetime = datetime.combine(res.date, res_start_time)
                lead_alert_time = res_datetime - timedelta(hours=lead_hours)
                if lead_alert_time.strftime("%Y-%m-%d %H:%M") == now.strftime("%Y-%m-%d %H:%M"):
                    alerts.append({
                        'sequence': res.sequence,
                        'customer': res.customer_id.name,
                        'start_time': res.starting_at,
                    })

            except Exception as e:
                print("Reservation parse error:", res.sequence, "Error:", e)
                continue

        return {'alerts': alerts}
