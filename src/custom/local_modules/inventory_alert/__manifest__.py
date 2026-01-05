{
    'name': 'Critical Stock Alerts',
    'version': '17.0.1.0.0',
    'author': 'Marv1nG by Binaural',
    'category': 'Inventory',
    'depends': ['stock', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/product_template_views.xml',
        'views/inventory_alert_dashboard.xml',
    ],
    'installable': True,
    'application': True,
}
