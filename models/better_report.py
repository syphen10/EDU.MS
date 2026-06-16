from odoo import models, fields

class BetterReport(models.Model):
    _name = 'better.report'
    _description = 'Custom Report Template'

    name = fields.Char(string='Report Name', required=True)
    model_id = fields.Many2one('ir.model', string='Data Model', required=True)
    model_name = fields.Char(related='model_id.model', store=True)
    field_ids = fields.Many2many('ir.model.fields', string='Columns', domain="[('model_id', '=', model_id)]")
    record_limit = fields.Integer(string='Row Limit', default=500)

    def action_run_report(self):
        self.ensure_one()
        wizard = self.env['better.report.wizard'].create({'report_id': self.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compile Report',
            'res_model': 'better.report.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }