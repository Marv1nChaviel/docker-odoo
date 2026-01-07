from odoo.tests.common import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestStockStorageTags(TransactionCase):

    def setUp(self):
        super(TestStockStorageTags, self).setUp()
        self.tag_heavy = self.env["stock.storage.tag"].create({
            "name": "Heavy",
            "color": 1,
            "description": "Heavy items (> 50kg)"
        })
        self.tag_fragile = self.env["stock.storage.tag"].create({
            "name": "Fragile",
            "color": 2
        })
        self.product = self.env["product.template"].create({
            "name": "Test Product",
            "type": "product"
        })

    def test_assign_tags_to_product(self):
        """ Test assigning tags to a product """
        self.product.write({"storage_tag_ids": [(4, self.tag_heavy.id)]})
        self.assertIn(self.tag_heavy, self.product.storage_tag_ids)
        
        # Add another tag
        self.product.write({"storage_tag_ids": [(4, self.tag_fragile.id)]})
        self.assertEqual(len(self.product.storage_tag_ids), 2)

    def test_search_by_tag(self):
        """ Test searching products by tag """
        self.product.storage_tag_ids = [(6, 0, [self.tag_heavy.id])]
        
        products = self.env["product.template"].search([("storage_tag_ids", "in", self.tag_heavy.id)])
        self.assertIn(self.product, products)
        
        products_fragile = self.env["product.template"].search([("storage_tag_ids", "in", self.tag_fragile.id)])
        self.assertNotIn(self.product, products_fragile)