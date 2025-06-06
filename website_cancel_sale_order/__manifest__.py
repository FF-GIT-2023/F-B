
{
    'name': "Website Cancel Order",
    'version': '17.0.1.0.0',
    'category': 'Website',
    'summary': " This app allows you to cancel the sale order by specifying "
               " the reason from website.",
    'description': " This application provides users with the convenience of "
                   " canceling their sale orders directly through the website."
                   " By incorporating a user-friendly interface, it enables"
                   " customers to easily navigate and find the necessary "
                   " options to cancel their orders. ",
    'depends': ['website_sale', 'sale_management'],
    'data': [
        'views/sale_portal_templates.xml',
        'views/sale_order_views.xml'],
    'assets': {
        'web.assets_frontend': [
            'website_cancel_sale_order/static/src/js/sale_order_portal.js'],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
