from odoo import models, fields

class StockStorageTag(models.Model):
    _name = "stock.storage.tag"
    _description = "Stock Storage Tag"

    name = fields.Char(string="Tag Name", required=True, translate=True)
    color = fields.Integer(string="Color Index")
    description = fields.Text(string="Description")