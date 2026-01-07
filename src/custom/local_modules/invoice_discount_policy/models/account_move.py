from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            if move.move_type == 'out_invoice' and move.partner_id.customer_type:
                rule = self.env['account.discount.rule'].search([
                    ('customer_type', '=', move.partner_id.customer_type)
                ], limit=1)
                
                if rule:
                    for line in move.invoice_line_ids:
                        line.discount = rule.discount_percentage
        
        return super(AccountMove, self).action_post()
