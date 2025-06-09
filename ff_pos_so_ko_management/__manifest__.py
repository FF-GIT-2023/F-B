{
    'name': 'Pos So Ko Management',
    'version': '17.0.1.0.0',
    'summary': """change the sale order management functionality""",
    'description': """change the sale order management functionality""",
    'author': 'ForeFront Technologies',
    'company': 'ForeFront Technologies',
    'maintainer': 'ForeFront Technologies',
    'category': 'Point Of Sale',
    'depends': ['point_of_sale', 'pos_sale', 'sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'ff_pos_so_ko_management/static/src/js/so_management_patch.js',
        ]
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}