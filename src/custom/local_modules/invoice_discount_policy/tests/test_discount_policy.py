from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestDiscountPolicy(TransactionCase):

    def setUp(self):
        super(TestDiscountPolicy, self).setUp()
        self.DiscountRule = self.env['account.discount.rule']
        self.Partner = self.env['res.partner']
        self.AccountMove = self.env['account.move']
        
        # Create Partner
        self.partner_vip = self.Partner.create({
            'name': 'Test VIP Partner',
            'customer_type': 'vip'
        })
        
        # Create Discount Rule
        self.DiscountRule.create({
            'customer_type': 'vip',
            'discount_percentage': 10.0
        })
        
        # Create Product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'service',
            'list_price': 100.0,
        })

    def test_apply_discount_vip(self):
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_vip.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })]
        })
        
        # Post (validate) invoice
        invoice.action_post()
        
        # Check discount
        # Refresh record to ensure calculations are applied
        # invoice.invoice_line_ids.invalidate_cache() # Odoo 17 invalidation is different or auto
        # But for test safety we check the line
        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 10.0, "Discount should be 10%")
