from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestStockAlert(TransactionCase):

    def setUp(self):
        super(TestStockAlert, self).setUp()
        self.ProductTemplate = self.env['product.template']
        self.test_product = self.ProductTemplate.create({
            'name': 'Test Product',
            'type': 'product',
            'min_stock_threshold': 10.0,
        })
        self.stock_location = self.env.ref('stock.stock_location_stock')

    def test_field_assignment(self):
        """ Test if min_stock_threshold usage works correctly """
        self.assertEqual(self.test_product.min_stock_threshold, 10.0)
        self.test_product.write({'min_stock_threshold': 5.0})
        self.assertEqual(self.test_product.min_stock_threshold, 5.0)

    def test_alert_generation_smart_deduplication(self):
        """ 
        Verify logic:
        1. Alert if critical.
        2. NO Alert if same quantity (simulating 2h later check).
        3. Alert if quantity changes (but still critical).
        """
        # 1. Update stock to 5 (Critical)
        quant = self.env['stock.quant'].create({
            'product_id': self.test_product.product_variant_id.id,
            'location_id': self.stock_location.id,
            'inventory_quantity': 5.0,
        })
        quant.action_apply_inventory()

        # RUN 1: Should Alert
        self.test_product._check_stock_levels()
        
        messages_1 = self.env['mail.message'].search([
            ('res_id', '=', self.test_product.id),
            ('model', '=', 'product.template'),
            ('body', 'like', 'ALERT: Critical stock'),
        ])
        self.assertEqual(len(messages_1), 1, "First alert should be generated")
        self.assertIn("Available: 5.0", messages_1[0].body)

        # RUN 2: Same Quantity (Simulate 2 check)
        self.test_product._check_stock_levels()
        
        messages_2 = self.env['mail.message'].search([
            ('res_id', '=', self.test_product.id),
            ('model', '=', 'product.template'),
            ('body', 'like', 'ALERT: Critical stock'),
        ])
        self.assertEqual(len(messages_2), 1, "Should NOT generate duplicate alert for same quantity")

        # RUN 3: Change Quantity to 4 (Still Critical)
        quant.inventory_quantity = 4.0
        quant.action_apply_inventory()
        
        # Verify quantity update
        self.assertEqual(self.test_product.qty_available, 4.0)

        self.test_product._check_stock_levels()
        
        messages_3 = self.env['mail.message'].search([
            ('res_id', '=', self.test_product.id),
            ('model', '=', 'product.template'),
            ('body', 'like', 'ALERT: Critical stock'),
        ])
        self.assertEqual(len(messages_3), 2, "Should generate NEW alert because quantity changed")
        
        sorted_msgs = messages_3.sorted(lambda m: m.id, reverse=True)
        self.assertIn("Available: 4.0", sorted_msgs[0].body)

    def test_dashboard_logic(self):
        dashboard_product = self.ProductTemplate.create({
            'name': 'Dashboard Product',
            'type': 'product',
            'min_stock_threshold': 10.0,
        })
        self.assertTrue(dashboard_product.is_low_stock, "Should be low stock (0 < 10)")
        
        dashboard_product.min_stock_threshold = 0.0
        self.assertFalse(dashboard_product.is_low_stock, "Should not be low stock (threshold 0)")
        
        dashboard_product.min_stock_threshold = 5.0
        self.env['stock.quant'].create({
            'product_id': dashboard_product.product_variant_id.id,
            'location_id': self.stock_location.id,
            'inventory_quantity': 10.0,
        }).action_apply_inventory()
        
        dashboard_product.invalidate_recordset()
        self.assertFalse(dashboard_product.is_low_stock, "Should not be low stock (10 > 5)")
