{
    'name': 'Automated Benefit Calculations',
    'version': '1.0',
    'author': 'Marv1nG by Binaural',
    'category': 'Human Resources/Payroll',
    'depends': ['hr_payroll', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'security/payroll_benefit_security.xml',
        'data/salary_rule_data.xml',
        'views/payroll_benefit_config_views.xml',
        'views/hr_contract_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}