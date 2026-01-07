from odoo import models, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        """
        Override to inject separate benefit lines after standard computation.
        """
        # Run standard computation first
        super().compute_sheet()
        
        # Inject our custom lines
        for payslip in self:
            payslip._compute_dynamic_benefit_lines()
            
    def _compute_dynamic_benefit_lines(self):
        """
        Generates separate payslip lines for each benefit configuration.
        """
        self.ensure_one()
        contract = self.contract_id
        if not contract:
            return

        # Find the template rule (we use the existing one to keep accounting links if any)
        # We search by the XMLID code or just the code field if we trust it
        rule = self.env.ref('payroll_benefits.rule_dynamic_benefit', raise_if_not_found=False)
        if not rule:
            # Fallback search by code if XMLI is problematic (though known from data file)
            rule = self.env['hr.salary.rule'].search([('code', '=', 'BIN_DYN_BENEFIT'), ('struct_id', '=', self.struct_id.id)], limit=1)
            
        if not rule:
            return

        # Find active configurations
        configs = self.env['payroll.benefit.config'].search([
            ('contract_type', '=', contract.contract_benefit_type),
            ('company_id', '=', contract.company_id.id)
        ])
        
        new_lines_vals = []
        for config in configs:
            amount = contract.wage * (config.benefit_amount / 100.0)
            if amount != 0:
                line_vals = {
                    'slip_id': self.id,
                    'salary_rule_id': rule.id,
                    'contract_id': contract.id,
                    'name': config.name,  # Use the specific benefit name!
                    'code': 'BEN_%s' % config.id, # Unique code per line
                    'category_id': rule.category_id.id,
                    'sequence': rule.sequence,
                    'appears_on_payslip': True,
                    'quantity': 1.0,
                    'rate': 100.0,
                    'amount': amount,
                    'total': amount,
                }
                new_lines_vals.append(line_vals)
        
        if new_lines_vals:
            self.env['hr.payslip.line'].create(new_lines_vals)
