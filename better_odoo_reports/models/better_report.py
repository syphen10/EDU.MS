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
                # Clean up relational fields so they show the name, not an ID tuple
                if isinstance(val, tuple): 
                    val = val[1]
                # Handle empty values
                if val is False or val is None:
                    val = ""
                    
                row[fname] = val
                
                if isinstance(val, (int, float)):
                    total_amount += float(val)
            report_data.append(row)

        json_data = json.dumps(report_data)
        kpi_data = json.dumps({"total_records": len(records), "total_capital": total_amount})

        # We use a standard string here to avoid f-string curly brace conflicts with CSS/JS
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Prism Engine - Interactive Report</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body { background-color: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }
                .glass-panel { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
                th { text-transform: uppercase; letter-spacing: 0.05em; }
            </style>
        </head>
        <body class="p-8">
            
            <div class="max-w-7xl mx-auto">
                <div class="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
                    <h1 class="text-3xl font-bold text-cyan-400">Prism Engine Analytics</h1>
                    <button onclick="window.print()" class="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded shadow">
                        Export PDF
                    </button>
                </div>

                <div class="grid grid-cols-2 gap-6 mb-8">
                    <div class="glass-panel p-6 rounded-xl shadow-lg">
                        <h3 class="text-slate-400 text-sm font-semibold mb-1">TOTAL RECORDS EXPORTED</h3>
                        <p class="text-4xl font-bold text-white" id="kpi-records">0</p>
                    </div>
                    <div class="glass-panel p-6 rounded-xl shadow-lg">
                        <h3 class="text-slate-400 text-sm font-semibold mb-1">AGGREGATED NUMERICS</h3>
                        <p class="text-4xl font-bold text-emerald-400" id="kpi-totals">0.00</p>
                    </div>
                </div>

                <div class="glass-panel rounded-xl shadow-lg overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead class="bg-slate-800 text-slate-300 text-xs">
                                <tr id="table-head">
                                    </tr>
                            </thead>
                            <tbody id="table-body" class="text-sm divide-y divide-slate-700/50">
                                </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <script>
                // Python will replace these strings with actual JSON before saving the file
                window.ODOO_DATA = REPLACE_ME_WITH_DATA;
                window.ODOO_KPIS = REPLACE_ME_WITH_KPIS;

                document.addEventListener("DOMContentLoaded", () => {
                    // 1. Render KPIs
                    document.getElementById('kpi-records').innerText = window.ODOO_KPIS.total_records.toLocaleString();
                    document.getElementById('kpi-totals').innerText = window.ODOO_KPIS.total_capital.toLocaleString(undefined, {minimumFractionDigits: 2});

                    const data = window.ODOO_DATA;
                    if (data.length === 0) return;

                    // 2. Render Table Headers
                    const headers = Object.keys(data[0]);
                    const thead = document.getElementById('table-head');
                    headers.forEach(h => {
                        const th = document.createElement('th');
                        th.className = "px-6 py-4 font-medium";
                        th.innerText = h.replace(/_/g, ' '); // Clean up system field names
                        thead.appendChild(th);
                    });

                    // 3. Render Table Rows
                    const tbody = document.getElementById('table-body');
                    data.forEach((row, index) => {
                        const tr = document.createElement('tr');
                        tr.className = "hover:bg-slate-800/50 transition-colors";
                        
                        headers.forEach(h => {
                            const td = document.createElement('td');
                            td.className = "px-6 py-4 text-slate-300";
                            td.innerText = row[h];
                            tr.appendChild(td);
                        });
                        tbody.appendChild(tr);
                    });
                });
            </script>
        </body>
        </html>
        """

        # Safely inject the JSON into the HTML string
        html_content = html_content.replace('REPLACE_ME_WITH_DATA', json_data)
        html_content = html_content.replace('REPLACE_ME_WITH_KPIS', kpi_data)

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
