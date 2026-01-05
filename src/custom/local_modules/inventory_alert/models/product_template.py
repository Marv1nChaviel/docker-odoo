from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
 
    min_stock_threshold = fields.Float(string="Minimum Stock", default=0.0)
    is_low_stock = fields.Boolean(
        string="Critical Stock", 
        compute='_compute_is_low_stock', 
        search='_search_is_low_stock'
    )

    @api.depends('qty_available', 'min_stock_threshold')
    def _compute_is_low_stock(self):
        for product in self:
            if product.min_stock_threshold > 0 and product.qty_available < product.min_stock_threshold:
                product.is_low_stock = True
            else:
                product.is_low_stock = False

    def _search_is_low_stock(self, operator, value):
        if operator not in ['=', '!='] or not isinstance(value, bool):
            raise UserError(("Operation not supported"))
        
        is_true = (operator == '=' and value is True) or (operator == '!=' and value is False)
        products = self.search([('min_stock_threshold', '>', 0)])
        
        matching_ids = []
        for p in products:
            if (p.qty_available < p.min_stock_threshold) == is_true:
                matching_ids.append(p.id)
                
        return [('id', 'in', matching_ids)]

    def _check_stock_levels(self):
        """////Action to check stock levels and generate notifications.////"""
        for product in self:
            if product.min_stock_threshold > 0 and product.qty_available < product.min_stock_threshold:
            
                new_message_body = f"ALERT: Critical stock for {product.name}. Available: {product.qty_available}, Minimum: {product.min_stock_threshold}"
                
                # Get the last alert message
                last_message = self.env['mail.message'].search([
                    ('res_id', '=', product.id),
                    ('model', '=', 'product.template'),
                    ('body', 'like', 'ALERT: Critical stock'),
                ], limit=1, order='date desc')
                
                # Deduplication logic (HTML aware)
                if last_message and new_message_body in last_message.body:
                    continue 
                
                product.message_post(
                    body=new_message_body,
                    subtype_xmlid="mail.mt_note"
                )
