from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_benefit_type = fields.Selection([
        ('full_time', 'Tiempo Completo'),
        ('part_time', 'Medio Tiempo'),
        ('temporary', 'Temporal')
    ], string="Tipo de Beneficio de Contrato", default='full_time')