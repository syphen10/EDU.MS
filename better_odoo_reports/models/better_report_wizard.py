from odoo import models, fields
import base64
import json
from datetime import datetime, date

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
                
                if isinstance(val, tuple): 
                    val = val[1]
                
                if isinstance(val, (datetime, date)):
                    val = str(val)
                
                if val is False or val is None:
                    val = ""
                    
                row[fname] = val
                
                if isinstance(val, (int, float)):
                    total_amount += float(val)
                    
            report_data.append(row)

        json_data = json.dumps(report_data)
        kpi_data = json.dumps({"total_records": len(records), "total_capital": total_amount})
        
        # Grab the exact server time for the snapshot
        snapshot_time = fields.Datetime.now().strftime("%d %b %Y, %H:%M:%S UTC")

        # --- THE PREMIUM ENTERPRISE SAAS UI ---
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Better Reports - Analytics</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                body { 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
                    background-color: #F9FAFB; 
                    color: #0F172A; 
                    -webkit-font-smoothing: antialiased;
                }
                
                .bg-dot-pattern {
                    background-image: radial-gradient(#CBD5E1 1px, transparent 1px);
                    background-size: 24px 24px;
                }
                
                ::-webkit-scrollbar { width: 6px; height: 6px; }
                ::-webkit-scrollbar-track { background: transparent; }
                ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 10px; }
                ::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

                .pro-card {
                    background: #FFFFFF;
                    border-radius: 16px;
                    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 12px 24px -4px rgba(15, 23, 42, 0.03);
                    border: 1px solid rgba(226, 232, 240, 0.8);
                }

                .dragging { 
                    opacity: 0.6; 
                    transform: scale(0.98); 
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                    z-index: 50;
                }
                
                .glass-header {
                    background: rgba(249, 250, 251, 0.8);
                    backdrop-filter: blur(12px);
                    -webkit-backdrop-filter: blur(12px);
                }

                .text-gradient {
                    background: linear-gradient(135deg, #0F172A 0%, #334155 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .text-gradient-blue {
                    background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }

                .dropzone-list { min-height: 200px; }
            </style>
        </head>
        <body class="h-screen flex overflow-hidden selection:bg-blue-100/50 bg-dot-pattern">

            <aside class="w-[300px] bg-white border-r border-slate-200 flex flex-col h-full shrink-0 z-30 shadow-[4px_0_24px_rgba(15,23,42,0.02)]">
                <div class="h-[72px] shrink-0 flex items-center px-6 border-b border-slate-100">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center shadow-md shadow-slate-900/20">
                            <span class="text-white font-bold text-[11px] tracking-widest">BR.</span>
                        </div>
                        <div class="flex flex-col">
                            <h1 class="text-[14px] font-bold tracking-tight text-slate-900 leading-tight">Better Reports</h1>
                            <span class="text-[10px] font-semibold text-slate-400 tracking-wider uppercase mt-0.5">Workspace</span>
                        </div>
                    </div>
                </div>

                <div class="px-5 py-6 flex-1 overflow-y-auto flex flex-col gap-8">
                    <div>
                        <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">Data Snapshot</label>
                        <div class="bg-slate-50 border border-slate-200/60 rounded-xl px-4 py-3 flex flex-col gap-1.5 shadow-sm inset-y-1">
                            <div class="flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-slate-400"></span>
                                <span class="text-slate-700 font-semibold text-[12px]">Offline Report</span>
                            </div>
                            <span class="text-[10px] text-slate-500 font-mono pl-4">REPLACE_ME_WITH_TIME</span>
                        </div>
                    </div>

                    <div class="flex-1 flex flex-col">
                        <div class="flex items-center justify-between mb-3">
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active Schema</label>
                            <span class="text-[9px] font-bold text-blue-600 bg-blue-50/80 px-2 py-0.5 rounded uppercase tracking-wider border border-blue-100">Drag to Reorder</span>
                        </div>
                        <ul id="schema-sidebar-list" class="dropzone-list space-y-2 relative z-10 flex-1">
                            </ul>
                    </div>
                </div>
            </aside>

            <main class="flex-1 flex flex-col h-full relative z-10 min-w-0">
                <header class="h-[72px] shrink-0 px-10 flex items-center justify-between glass-header border-b border-slate-200/50 z-20 sticky top-0">
                    <div class="flex items-center gap-4">
                        <h2 class="text-[20px] font-bold tracking-tight text-slate-900">Interactive Analytics</h2>
                        <div class="px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 flex items-center gap-1.5 hidden sm:flex">
                            <span class="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Local File</span>
                        </div>
                    </div>
                    <button onclick="window.print()" class="text-[13px] font-semibold text-white bg-slate-900 hover:bg-slate-800 transition-all rounded-lg px-4 py-2 shadow-md shadow-slate-900/10 flex items-center gap-2 border border-slate-900 focus:ring-2 focus:ring-slate-900/20 focus:outline-none">
                        <svg class="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        Export PDF
                    </button>
                </header>

                <div class="px-10 pb-10 pt-8 overflow-y-auto flex-1 z-10 w-full">
                    
                    <div class="grid grid-cols-2 gap-6 mb-8">
                        <div class="pro-card p-6 flex flex-col justify-center relative overflow-hidden group hover:border-slate-300 transition-colors">
                            <div class="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                                <svg class="w-16 h-16 text-slate-900" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
                            </div>
                            <span class="text-[11px] font-bold text-slate-400 uppercase tracking-widest relative z-10">Total Records</span>
                            <div class="text-[48px] font-bold tracking-tighter mt-1 relative z-10 leading-none text-gradient" id="kpi-pos">0</div>
                        </div>
                        <div class="pro-card p-6 flex flex-col justify-center relative overflow-hidden group hover:border-blue-200 transition-colors">
                            <div class="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                                <svg class="w-16 h-16 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            </div>
                            <span class="text-[11px] font-bold text-slate-400 uppercase tracking-widest relative z-10">Capital Aggregation</span>
                            <div class="flex items-baseline gap-2 mt-2 relative z-10">
                                <span class="text-[14px] font-bold text-slate-300 tracking-wider">VAL</span>
                                <div class="text-[48px] font-bold tracking-tighter leading-none text-gradient-blue" id="kpi-val">0.00</div>
                            </div>
                        </div>
                    </div>

                    <div class="pro-card flex flex-col w-full max-w-full overflow-hidden">
                        <div class="px-6 py-5 border-b border-slate-100 flex justify-between items-center bg-white relative z-10">
                            <h2 class="text-[15px] font-bold text-slate-900 tracking-tight">Output Matrix</h2>
                        </div>
                        
                        <div class="overflow-x-auto w-full relative z-10 max-h-[600px] overflow-y-auto">
                            <table class="w-full text-left whitespace-nowrap min-w-max">
                                <thead id="table-head" class="bg-slate-50/90 backdrop-blur-sm sticky top-0 z-20 shadow-sm"><tr></tr></thead>
                                <tbody id="table-body" class="divide-y divide-slate-100 bg-white"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>

            <script>
                window.ODOO_DATA = REPLACE_ME_WITH_DATA;
                window.ODOO_KPIS = REPLACE_ME_WITH_KPIS;
                const data = window.ODOO_DATA;

                document.addEventListener("DOMContentLoaded", () => {
                    document.getElementById('kpi-pos').innerText = window.ODOO_KPIS.total_records.toLocaleString();
                    document.getElementById('kpi-val').innerText = window.ODOO_KPIS.total_capital.toLocaleString(undefined, {minimumFractionDigits: 2});

                    if (data.length === 0) return;

                    const sidebarList = document.getElementById('schema-sidebar-list');
                    let currentHeaders = Object.keys(data[0]);

                    function renderTable(headersList) {
                        const theadRow = document.querySelector('#table-head tr');
                        const tbody = document.getElementById('table-body');
                        theadRow.innerHTML = '';
                        tbody.innerHTML = '';

                        headersList.forEach(h => {
                            const th = document.createElement('th');
                            th.className = "px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-widest border-b border-slate-200";
                            th.innerText = h.replace(/_/g, ' ');
                            theadRow.appendChild(th);
                        });

                        data.forEach(row => {
                            const tr = document.createElement('tr');
                            tr.className = "hover:bg-slate-50/80 transition-colors group";
                            
                            headersList.forEach((h, index) => {
                                const td = document.createElement('td');
                                if (index === 0) {
                                    td.className = "px-6 py-4 text-[13px] text-slate-900 font-semibold";
                                } else {
                                    td.className = "px-6 py-4 text-[13px] text-slate-600 font-medium";
                                }
                                td.innerText = row[h] !== null ? row[h] : '';
                                tr.appendChild(td);
                            });
                            tbody.appendChild(tr);
                        });
                    }

                    function renderSidebar(headersList) {
                        sidebarList.innerHTML = '';
                        headersList.forEach((h, index) => {
                            const li = document.createElement('li');
                            li.className = "flex items-center p-2.5 bg-white border border-slate-200 rounded-lg cursor-grab hover:border-slate-300 hover:shadow-sm transition-all group";
                            li.draggable = true;
                            li.dataset.header = h;
                            
                            li.innerHTML = `
                                <div class="mr-3 text-slate-300 group-hover:text-slate-400 transition-colors cursor-grab">
                                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M8 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM8 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM8 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM20 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM20 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM20 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0z"></path></svg>
                                </div>
                                <div class="flex items-center gap-2 overflow-hidden flex-1">
                                    <span class="text-[10px] font-bold text-slate-400 w-3 text-right shrink-0">${index + 1}.</span>
                                    <span class="text-[12px] font-semibold text-slate-700 truncate capitalize">${h.replace(/_/g, ' ')}</span>
                                </div>
                            `;

                            li.addEventListener('dragstart', (e) => {
                                li.classList.add('dragging');
                                e.dataTransfer.effectAllowed = 'move';
                            });
                            
                            li.addEventListener('dragend', () => {
                                li.classList.remove('dragging');
                                const newOrder = Array.from(sidebarList.children).map(p => p.dataset.header);
                                renderTable(newOrder);
                                renderSidebar(newOrder); 
                            });

                            sidebarList.appendChild(li);
                        });
                    }

                    renderTable(currentHeaders);
                    renderSidebar(currentHeaders);

                    sidebarList.addEventListener('dragover', e => {
                        e.preventDefault();
                        const draggable = document.querySelector('.dragging');
                        if (!draggable) return;
                        const afterElement = getDragAfterElement(sidebarList, e.clientY);
                        if (afterElement == null) {
                            sidebarList.appendChild(draggable);
                        } else {
                            sidebarList.insertBefore(draggable, afterElement);
                        }
                    });

                    function getDragAfterElement(container, y) {
                        const draggableElements = [...container.querySelectorAll('li[draggable="true"]:not(.dragging)')];
                        return draggableElements.reduce((closest, child) => {
                            const box = child.getBoundingClientRect();
                            const offset = y - box.top - box.height / 2;
                            if (offset < 0 && offset > closest.offset) {
                                return { offset: offset, element: child };
                            } else {
                                return closest;
                            }
                        }, { offset: Number.NEGATIVE_INFINITY }).element;
                    }
                });
            </script>
        </body>
        </html>
        """

        html_content = html_content.replace('REPLACE_ME_WITH_DATA', json_data)
        html_content = html_content.replace('REPLACE_ME_WITH_KPIS', kpi_data)
        html_content = html_content.replace('REPLACE_ME_WITH_TIME', snapshot_time)

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
