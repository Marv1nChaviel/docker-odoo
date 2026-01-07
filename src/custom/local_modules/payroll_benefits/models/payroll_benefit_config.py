from odoo import models, fields

class PayrollBenefitConfig(models.Model):
    _name = 'payroll.benefit.config'
    _description = 'Configuración de Beneficios'

    contract_type = fields.Selection([
        ('full_time', 'Tiempo Completo'),
        ('part_time', 'Medio Tiempo'),
        ('temporary', 'Temporal')
    ], string="Tipo de Contrato", required=True)
    
    name = fields.Char(string="Concepto", required=True)
    benefit_amount = fields.Float(string="Monto de Beneficio (%)", required=True)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('contract_type_benefit_unique', 'unique(contract_type, name, company_id)', 'Ya existe este concepto de beneficio para este tipo de contrato en esta compañía.')
    ]