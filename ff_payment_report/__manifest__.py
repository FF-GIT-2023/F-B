{
    "name": "POS Payment Method Report",
    "version": "17.0.0.0.0",
    "summary": "Base module to prepare POS payment method reporting.",
    "author": "ForeFront Technologies",
    "depends": ["base", "point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/payment_wiz.xml",
        "report/payment_report_template.xml",
        "report/payment_report.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
