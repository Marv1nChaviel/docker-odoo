from odoo.tests.common import TransactionCase

class TestFinancialKPI(TransactionCase):

    def setUp(self):
        super(TestFinancialKPI, self).setUp()
        self.KPI = self.env['account.financial.kpi']
        
        # Create a KPI
        self.kpi = self.KPI.create({
            'name': 'Test KPI',
            'formula': 'bal("1") - bal("2")',
            'threshold_warning': 50.0,
            'threshold_critical': 10.0,
        })

    def test_kpi_computation_and_state(self):
        # Mocking values by creating another KPI that just returns a fixed value 
        # or by manually setting value if it wasn't computed.
        # However, since we rely on _get_balance which queries account.move.line,
        # we should create some move lines or mock _get_balance.
        # Creating moves is cleaner but heavier.
        # For simplicity in this environment, let's mock _get_balance (patch) or just create moves.
        # Given we have time, creating moves is safer to skip patching.
        
        # But wait, creating moves requires accounts, journals, etc.
        # Let's try to just test the formula engine logic by overriding _get_balance via a subclass or mock?
        # Odoo tests usually allow creating moves.
        
        # Let's simplify: Test the eval logic with a formula that doesn't strictly depend on DB if possible,
        # OR create minimal moves. 
        
        # Actually, let's test a simple formula '100 - 20' first to verify engine.
        self.kpi.formula = '100 - 20'
        # Trigger compute
        self.kpi.invalidate_model() # invalidating cache to force recompute? 
        # Computed fields are computed on access.
        
        self.assertEqual(self.kpi.value, 80.0)
        self.assertEqual(self.kpi.state, 'success') # 80 > 50 (warning)
        
        # Change thresholds
        self.kpi.threshold_warning = 90.0
        self.kpi.invalidate_model() 
        self.assertEqual(self.kpi.state, 'warning') # 80 < 90 but > 10 (critical)
        
        self.kpi.threshold_critical = 85.0
        self.kpi.invalidate_model()
        self.assertEqual(self.kpi.state, 'danger') # 80 < 85


    def test_kpi_balance_calculation(self):
        # Create a test account (ensure unique code)
        account = self.env['account.account'].create({
            'name': 'Test Account 101009',
            'code': '101009',
            'account_type': 'asset_current',
        })
        
        # Create a journal entry
        move = self.env['account.move'].create({
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'date': '2026-01-01',
            'line_ids': [
                (0, 0, {
                    'name': 'Debit',
                    'account_id': account.id,
                    'debit': 1000.0,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'name': 'Credit',
                    'account_id': self.env['account.account'].search([('code', '!=', '101009')], limit=1).id,
                    'debit': 0.0,
                    'credit': 1000.0,
                }),
            ]
        })
        move.action_post()
        
        # Create KPI using this account
        kpi = self.KPI.create({
            'name': 'Real Balance Test',
            'formula': "bal('101009')",
            'threshold_warning': 500.0,
            'threshold_critical': 0.0,
        })
        
        # Verify value matches the debit amount
        # Note: bal() returns sum(balance). For asset, debit is positive balance.
        self.assertEqual(kpi.value, 1000.0)
        self.assertEqual(kpi.state, 'success')

    def test_formula_error_handling(self):
        self.kpi.formula = '1 / 0'
        self.assertEqual(self.kpi.value, 0.0)

    def test_kpi_variables(self):
        # Create tag
        tag = self.env['account.account.tag'].create({'name': 'Test Tag', 'applicability': 'accounts'})
        
        # Create account with tag
        account = self.env['account.account'].create({
            'name': 'Test Var Account',
            'code': '999999',
            'account_type': 'asset_current',
            'tag_ids': [(4, tag.id)]
        })
        
        # Post move
        move = self.env['account.move'].create({
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'date': '2026-01-01',
            'line_ids': [
                (0, 0, {
                    'name': 'Debit', 
                    'account_id': account.id, 
                    'debit': 200.0, 
                    'credit': 0.0,
                }),
                (0, 0, {
                    'name': 'Credit', 
                    'account_id': self.env['account.account'].search([('code', '!=', '999999')], limit=1).id, 
                    'debit': 0.0, 
                    'credit': 200.0,
                }),
            ]
        })
        move.action_post()
        
        # Create KPI with variable
        kpi = self.KPI.create({
            'name': 'Variable KPI',
            'formula': 'my_var',
            'threshold_warning': 150.0,
            'threshold_critical': 50.0,
            'variable_ids': [(0, 0, {
                'name': 'my_var',
                'account_tag_ids': [(4, tag.id)]
            })]
        })
        
        # Verify value matches the debit amount
        self.assertEqual(kpi.value, 200.0)
