from odoo import models, fields

class AccountDiscountRule(models.Model):
    _name = 'account.discount.rule'
    _description = 'Discount Rules'
    _rec_name = 'customer_type'

    customer_type = fields.Selection([
        ('retail', 'Minorista'),
        ('wholesale', 'Mayorista'),
        ('vip', 'VIP')
    ], string='Tipo de Cliente', required=True)
    
    discount_percentage = fields.Float(string='Descuento (%)', required=True)
    
    _sql_constraints = [
        ('customer_type_uniq', 'unique (customer_type)', 'Only one rule per customer type is allowed!')
    ]
