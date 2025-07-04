# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Website Easy Add to Cart",
    'version': '17.0.0.0',
    'category': 'eCommerce',
    'license':'OPL-1',
    'summary': """This Module is used for easy to Add product in cart""" ,
    'description': 'This Module is used to Add product in cart, easy to Add product in cart, '
                   'dynamic add to cart option, dynamic product add to cart option, easy add to cart option on shop',
    'author': 'BrowseInfo',
    'website' : 'https://www.browseinfo.com',
    'depends': ['base','website','sale','website_sale'],
    'data'   : [
                'views/template.xml',
    		],
    'web.assets_frontend': ['/bi_website_add_product/static/src/css/custom.css'],
	'installable': True,
	'application': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/-mOJOIblJnI',
    "images":["static/description/Banner.gif"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
