{
    "name": "Stock Storage Tags",
    "version": "1.0",
    "summary": "Add dynamic tags to products for warehouse organization",
    "description": """
        This module adds storage tags to products and allows grouping/filtering in inventory.
        
        Key Features:
        - Manage Storage Tags (Name, Color, Description).
        - Assign tags to Products.
        - Group products by tags in Kanban view.
        - Quick action to assign tags.
    """,
    "category": "Inventory/Inventory",
    "author": "Marv1nG by Binaural",
    "depends": ["stock", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_storage_tag_views.xml",
        "views/product_template_views.xml",
        "wizard/stock_tag_assign_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}