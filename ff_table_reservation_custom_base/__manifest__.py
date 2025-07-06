{
    'name': 'Table Reservation Custom Base',
    'version': '17.0.0.0.0',
    'category': 'eCommerce,Point of Sale',
    'summary': 'Reserve tables in POS from website',
    'description': """This module enables to reserve tables in POS from website.
     User will be able to select the floor, table, date and time.""",
    'author': 'Forefront Technologies',
    'company': 'Forefront Technologies',
    'maintainer': 'Forefront Technologies',
    'depends': ['table_reservation_on_website'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ff_table_reservation_custom_base/static/src/js/table_reservation_notification.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}