{
    'name': 'Invoice Discount Policy',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Apply automatic discounts on invoices based on customer type',
    'author': 'Marv1nG by Binaural',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/account_discount_rule_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
