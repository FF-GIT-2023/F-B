{
    "name": "Pos Filter Website Sale Orders & Pos Product Screen Popup",
    "version": "17.0.0.0.0",
    "category": "Point of Sale",
    "summary": "Pos Filter Quotation Sent Sale Orders",
    "author": "Forefront Technologies",
    "depends": ["base", "point_of_sale", "pos_sale", "sale"],
    "data": ['views/sale_order.xml',],
    'assets': {
        'point_of_sale._assets_pos': [
            'ff_pos_filter_sale_orders/static/src/js/sale_order_fetcher_patch.js',
            'ff_pos_filter_sale_orders/static/src/js/BookingsPopup.js',
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3"
}
