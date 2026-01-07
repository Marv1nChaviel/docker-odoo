from odoo import models, fields, api

class AccountFinancialKPIVariable(models.Model):
    _name = 'account.financial.kpi.variable'
    _description = 'KPI Variable'
    
    kpi_id = fields.Many2one('account.financial.kpi', string='KPI', required=True, ondelete='cascade')
    name = fields.Char(string='Variable Name', required=True, help="Name used in the formula (e.g., 'assets')")
    account_tag_ids = fields.Many2many('account.account.tag', string='Account Tags')
    account_group_ids = fields.Many2many('account.group', string='Account Groups')
    
    def _get_balance(self):
        self.ensure_one()
        
        # Build Account ID filter
        account_ids = self.env['account.account']
        
        if self.account_tag_ids:
            account_ids |= self.env['account.account'].search([('tag_ids', 'in', self.account_tag_ids.ids)])
            
        if self.account_group_ids:
            account_ids |= self.env['account.account'].search([('group_id', 'in', self.account_group_ids.ids)])
            
        if not account_ids:
            return 0.0
            
        # Build Domain with manual Context application
        domain = [
            ('account_id', 'in', account_ids.ids),
            ('parent_state', '=', 'posted')
        ]
        
        # Apply Date Filters from Context (Search View)
        ctx = self.env.context
        if ctx.get('date_from'):
            domain.append(('date', '>=', ctx['date_from']))
        if ctx.get('date_to'):
            domain.append(('date', '<=', ctx['date_to']))
        
        # Flush ORM cache
        self.env["account.move.line"].flush_model(["balance", "account_id", "parent_state", "date"])
        
        # Use _where_calc for robust SQL generation
        query = self.env['account.move.line']._where_calc(domain)
        tables, where_clause, where_params = query.get_sql()
        
        sql = f"SELECT SUM(account_move_line.balance) FROM {tables} WHERE {where_clause}"
        self.env.cr.execute(sql, where_params)
        
        res = self.env.cr.fetchone()
        return res[0] or 0.0