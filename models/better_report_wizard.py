from odoo import models, fields
import base64
import json

class BetterReportWizard(models.TransientModel):
    _name = 'better.report.wizard'
    _description = 'Report Results'

    report_id = fields.Many2one('better.report', string='Report', required=True)
    interactive_html_file = fields.Binary(string='Download Report', readonly=True)
    interactive_filename = fields.Char(readonly=True)

    def action_generate_interactive_report(self):
        report = self.report_id
        Model = self.env[report.model_name]
        field_names = report.field_ids.mapped('name')
        
        records = Model.search_read([], field_names, limit=report.record_limit or 500)
        
        report_data = []
        total_amount = 0.0
        
        for rec in records:
            row = {}
            for fname in field_names:
                val = rec.get(fname, '')
                if isinstance(val, tuple): val = val[1]
                row[fname] = val
                if isinstance(val, (int, float)):
                    total_amount += float(val)
            report_data.append(row)

        json_data = json.dumps(report_data)
        kpi_data = json.dumps({"total_records": len(records), "total_capital": total_amount})

        html_content = f"""
        <script>
            window.ODOO_DATA = {json_data};
            window.ODOO_KPIS = {kpi_data};
        </script>
        """

        self.write({
            'interactive_html_file': base64.b64encode(html_content.encode('utf-8')),
            'interactive_filename': f'{report.name.replace(" ", "_")}_Prism.html',
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'better.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }