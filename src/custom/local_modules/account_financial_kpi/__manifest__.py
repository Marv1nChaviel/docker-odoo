{
    "name": "Financial Health Indicators",
    "version": "1.0",
    "summary": "Dashboard for Financial KPIs",
    "description": """
        Define and monitor financial KPIs with custom formulas based on account balances.
        
        Features:
        - Custom Formula Engine (Python expressions).
        - Traffic Light Indicators (Green, Yellow, Red).
        - Dashboard View.
    """,
    "category": "Accounting/Accounting",
    "author": "Marv1nG by Binaural",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_financial_kpi_views.xml",
        "data/kpi_data.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}