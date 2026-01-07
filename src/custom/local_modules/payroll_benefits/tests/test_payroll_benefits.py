from odoo.tests.common import TransactionCase

class TestPayrollBenefits(TransactionCase):
    def setUp(self):
        super().setUp()
        # Crear configuración: Full Time = 10% (Base)
        self.env['payroll.benefit.config'].create({
            'name': 'Bono Base',
            'contract_type': 'full_time',
            'benefit_amount': 10.0
        })
        self.employee = self.env['hr.employee'].create({'name': 'Juan Pérez'})

    def test_full_time_benefit_sum(self):
        """Caso 1: Contrato definido con múltiples beneficios"""
        # Agregamos otro beneficio para el mismo tipo
        self.env['payroll.benefit.config'].create({
            'name': 'Vacaciones',
            'contract_type': 'full_time',
            'benefit_amount': 5.0
        })
        
        contract = self.env['hr.contract'].create({
            'name': 'Contrato Full',
            'employee_id': self.employee.id,
            'wage': 1000.0,
            'contract_benefit_type': 'full_time',
            'state': 'open',
        })
        payslip = self.env['hr.payslip'].create({
            'employee_id': self.employee.id,
            'contract_id': contract.id,
            'struct_id': self.env.ref('hr_payroll.structure_002').id,
        })
        payslip.compute_sheet()
        lines = payslip.line_ids.filtered(lambda l: l.code.startswith('BEN_'))
        # Total debería ser 10 + 5 = 15% de 1000 = 150
        # Ahora esperamos dos líneas separadas
        self.assertEqual(len(lines), 2, "Debería haber 2 líneas de beneficios")
        self.assertEqual(sum(lines.mapped('total')), 150.0, "El total debería ser 150")

    def test_no_type_benefit(self):
        """Caso 2: Caso límite - Contrato sin tipo definido"""
        contract = self.env['hr.contract'].create({
            'name': 'Contrato Vacío',
            'employee_id': self.employee.id,
            'wage': 1000.0,
            'contract_benefit_type': 'temporary', # No hay config para este
            'state': 'open',
        })
        payslip = self.env['hr.payslip'].create({
            'employee_id': self.employee.id,
            'contract_id': contract.id,
        })
        payslip.compute_sheet()
        lines = payslip.line_ids.filtered(lambda l: l.code.startswith('BEN_'))
        self.assertEqual(len(lines), 0, "No debería generar beneficio si no hay config")

    def test_unique_constraint(self):
        """Caso 3: Restricción de unicidad (Tipo + Nombre)"""
        # Intentar crear duplicado exacto
        with self.assertRaises(Exception): 
            self.env['payroll.benefit.config'].create({
                'name': 'Bono Base', # Ya existe para full_time
                'contract_type': 'full_time', 
                'benefit_amount': 20.0
            })
            
        # Crear mismo tipo con diferente nombre (Debería permitirlo)
        record = self.env['payroll.benefit.config'].create({
            'name': 'Otro Bono',
            'contract_type': 'full_time',
            'benefit_amount': 2.0
        })
        self.assertTrue(record.id)

    def test_multi_company_isolation(self):
        """Caso 4: Aislamiento Multi-Compañía"""
        company_b = self.env['res.company'].create({'name': 'Company B'})
        
        # Configuración para Company B
        self.env['payroll.benefit.config'].create({
            'name': 'Bono Company B',
            'contract_type': 'full_time',
            'benefit_amount': 50.0,
            'company_id': company_b.id
        })

        # Empleado en Company A (self.env.company) - Usando contrato Full Time
        # Debería tomar solo el 10% del setUp (que es de Company A por defecto)
        # NO debería sumar el 50% de Company B
        contract_a = self.env['hr.contract'].create({
            'name': 'Contrato Comp A',
            'employee_id': self.employee.id,
            'wage': 1000.0,
            'contract_benefit_type': 'full_time',
            'state': 'open',
        })
        payslip_a = self.env['hr.payslip'].create({
            'employee_id': self.employee.id,
            'contract_id': contract_a.id,
        })
        payslip_a.compute_sheet()
        lines_a = payslip_a.line_ids.filtered(lambda l: l.code.startswith('BEN_'))
        self.assertEqual(sum(lines_a.mapped('total')), 100.0, "Debería ignorar config de otra compañía")

        # Empleado en Company B
        employee_b = self.env['hr.employee'].create({'name': 'Juan B', 'company_id': company_b.id})
        contract_b = self.env['hr.contract'].create({
            'name': 'Contrato Comp B',
            'employee_id': employee_b.id,
            'wage': 1000.0,
            'contract_benefit_type': 'full_time',
            'state': 'open',
            'company_id': company_b.id
        })
        payslip_b = self.env['hr.payslip'].create({
            'employee_id': employee_b.id,
            'contract_id': contract_b.id, # Asume company del contrato
        })
        payslip_b.compute_sheet()
        lines_b = payslip_b.line_ids.filtered(lambda l: l.code.startswith('BEN_'))
        self.assertEqual(sum(lines_b.mapped('total')), 500.0, "Debería tomar config de su compañía (50%)")