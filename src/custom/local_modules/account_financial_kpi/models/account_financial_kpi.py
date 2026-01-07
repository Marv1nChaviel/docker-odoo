from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from datetime import date

class AccountFinancialKpi(models.Model):
    _name = "account.financial.kpi"
    _description = "Financial KPI"

    name = fields.Char(required=True, translate=True)
    description = fields.Text()
    variable_ids = fields.One2many("account.financial.kpi.variable", "kpi_id", string="Variables")
    
    formula = fields.Text(required=True, default="0.0", help="Python expression using bal('code')")
    
    threshold_warning = fields.Float(string="Warning Threshold", help="Below this value, state becomes Warning")
    threshold_critical = fields.Float(string="Critical Threshold", help="Below this value, state becomes Critical")
    
    value = fields.Float(compute="_compute_kpi", string="Current Value")
    state = fields.Selection([
        ("success", "Good"),
        ("warning", "Warning"),
        ("danger", "Critical")
    ], compute="_compute_kpi", string="Status")

    @api.model
    def _get_balance(self, account_code_prefix):
        """ Helper to get balance for accounts starting with code using SQL """
        # Build domain
        domain = [
            ("account_id.code", "=like", account_code_prefix + "%"),
            ("parent_state", "=", "posted")
        ]
        
        # Apply Date Filters from Context (Search View)
        ctx = self.env.context
        if ctx.get("date_from"):
            domain.append(("date", ">=", ctx["date_from"]))
        if ctx.get("date_to"):
            domain.append(("date", "<=", ctx["date_to"]))
            
        # Flush ORM cache to ensure SQL sees recent changes (critical for tests)
        self.env["account.move.line"].flush_model(["balance", "account_id", "parent_state", "date"])
        
        # Use _where_calc for robust SQL generation
        query = self.env["account.move.line"]._where_calc(domain)
        tables, where_clause, where_params = query.get_sql()
        
        sql = f"SELECT SUM(account_move_line.balance) FROM {tables} WHERE {where_clause}"
        self.env.cr.execute(sql, where_params)
        
        res = self.env.cr.fetchone()
        return res[0] or 0.0

    def _compute_kpi(self):
        for record in self:
            try:
                # Context for eval
                localdict = {
                    "bal": self._get_balance,
                    "max": max,
                    "min": min,
                    "abs": abs,
                }
                for var in record.variable_ids:
                    localdict[var.name] = var._get_balance()
                record.value = safe_eval(record.formula, localdict)
            except Exception as e:
                print(f"Error computing KPI {record.name}: {e}")
                record.value = 0.0
            
            # Determine state
            if record.value < record.threshold_critical:
                record.state = "danger"
            elif record.value < record.threshold_warning:
                record.state = "warning"
            else:
                record.state = "success"