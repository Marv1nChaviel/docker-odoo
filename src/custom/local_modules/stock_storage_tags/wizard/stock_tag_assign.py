from odoo import models, fields, api

class StockTagAssignWizard(models.TransientModel):
    _name = "stock.tag.assign.wizard"
    _description = "Assign/Remove Stock Tags"

    tag_ids = fields.Many2many("stock.storage.tag", string="Tags")
    mode = fields.Selection([
        ("add", "Add Tags"),
        ("remove", "Remove Tags"),
        ("set", "Set Tags (Replace)")
    ], default="add", string="Action", required=True)

    def action_assign_tags(self):
        self.ensure_one()
        context = self.env.context or {}
        active_ids = context.get("active_ids", [])
        products = self.env["product.template"].browse(active_ids)
        
        for product in products:
            if self.mode == "add":
                product.storage_tag_ids = [(4, tag.id) for tag in self.tag_ids]
            elif self.mode == "remove":
                product.storage_tag_ids = [(3, tag.id) for tag in self.tag_ids]
            elif self.mode == "set":
                product.storage_tag_ids = [(6, 0, self.tag_ids.ids)]
        return {"type": "ir.actions.act_window_close"}