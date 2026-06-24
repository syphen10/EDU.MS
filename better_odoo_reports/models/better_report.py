from odoo import models, fields

class BetterReport(models.Model):
    _name = 'better.report'
    _description = 'Financial Report Engine'

    name = fields.Char(string='Report Name', required=True)
    
    report_type = fields.Selection([
        ('ar_aging', 'A/R Aging Summary'),
        ('ap_aging', 'A/P Aging Summary'),
        ('bank_statement', 'Bank Statement'),
        ('pl', 'Profit and Loss Statement'),
        ('balance_sheet', 'Balance Sheet'),
        ('trial_balance', 'Trial Balance'),
        ('soa', 'Statement of Account'),
        ('gl', 'General Ledger'),
        ('partner_ledger', 'Partner Ledger'),
    ], string='Report Type', required=True, default='trial_balance')

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    
    allowed_group_ids = fields.Many2many('res.groups', string='Allowed User Groups', 
                                         help="Leave blank to allow all users to see this report.")

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
