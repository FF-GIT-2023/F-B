{
    "name": "Table Reservation Report",
    "version": "1.0",
    "category": "Sales",
    "summary": "Table Reservation Report",
    "depends": ["base", "website_sale", "point_of_sale", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/table_orders.xml",
        "report/reservation_report_template.xml",
        "report/report_table_reservation.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
