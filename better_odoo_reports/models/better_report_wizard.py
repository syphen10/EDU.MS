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

        # --- THE CLEAN ENTERPRISE UI (LIGHT MODE) ---
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Better Reports - Analytics</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=SF+Pro+Display:wght@400;600;700&display=swap" rel="stylesheet">
            <style>
                body { 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
                    background-color: #F5F5F7; /* Apple's signature light grey */
                    color: #1D1D1F; 
                    -webkit-font-smoothing: antialiased;
                }
                
                ::-webkit-scrollbar { width: 8px; height: 8px; }
                ::-webkit-scrollbar-track { background: transparent; }
                ::-webkit-scrollbar-thumb { background: #D2D2D7; border-radius: 10px; }
                ::-webkit-scrollbar-thumb:hover { background: #86868B; }

                /* Clean, soft shadow cards */
                .clean-card {
                    background: #FFFFFF;
                    border-radius: 24px;
                    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
                    border: 1px solid rgba(0, 0, 0, 0.02);
                }

                /* Dragging visual feedback */
                .dragging { 
                    opacity: 0.5; 
                    transform: scale(0.98); 
                    background-color: #F5F5F7;
                }
                
                .dropzone-list { min-height: 200px; }
            </style>
        </head>
        <body class="h-screen flex overflow-hidden selection:bg-blue-100">

            <aside class="w-[320px] bg-white border-r border-gray-200 flex flex-col h-full shrink-0 z-20 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
                <div class="h-[84px] shrink-0 flex items-center px-8 border-b border-gray-100">
                    <div class="flex items-center gap-3.5">
                        <div class="w-8 h-8 rounded-xl bg-[#1D1D1F] flex items-center justify-center shadow-sm">
                            <span class="text-white font-bold text-[11px] tracking-widest">BR.</span>
                        </div>
                        <div class="flex flex-col">
                            <h1 class="text-[15px] font-semibold tracking-tight text-[#1D1D1F] leading-tight">Better Reports</h1>
                            <span class="text-[10px] font-medium text-gray-500 tracking-wider uppercase mt-0.5">Workspace</span>
                        </div>
                    </div>
                </div>

                <div class="px-7 py-8 flex-1 overflow-y-auto flex flex-col gap-8">
                    <div>
                        <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3 block">Connection</label>
                        <div class="bg-gray-50 border border-gray-200 rounded-2xl px-4 py-3 flex items-center gap-3">
                            <span class="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]"></span>
                            <span class="text-[#1D1D1F] font-semibold text-[13px]">Online & Synced</span>
                        </div>
                    </div>

                    <div class="flex-1 flex flex-col">
                        <div class="flex items-center justify-between mb-3">
                            <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Active Schema</label>
                            <span class="text-[9px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md">DRAG TO REORDER</span>
                        </div>
                        <ul id="schema-sidebar-list" class="dropzone-list space-y-2 relative z-10 flex-1">
                            </ul>
                    </div>
                </div>
            </aside>

            <main class="flex-1 flex flex-col h-full relative z-10 min-w-0">
                <header class="h-[84px] shrink-0 px-12 flex items-center justify-between bg-[#F5F5F7] z-20">
                    <div class="flex items-center gap-4">
                        <h2 class="text-[24px] font-bold tracking-tight text-[#1D1D1F]">Interactive Analytics</h2>
                    </div>
                    <button onclick="window.print()" class="text-[14px] font-medium text-white bg-[#0066CC] hover:bg-[#0077ED] transition-colors rounded-full px-5 py-2 shadow-sm flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        Export PDF
                    </button>
                </header>

                <div class="px-12 pb-12 overflow-y-auto flex-1 z-10 w-full">
                    
                    <div class="grid grid-cols-2 gap-6 mb-8">
                        <div class="clean-card p-8 flex flex-col justify-center relative overflow-hidden">
                            <span class="text-[11px] font-bold text-gray-400 uppercase tracking-widest relative z-10">Total Records</span>
                            <div class="text-[56px] font-bold tracking-tighter text-[#1D1D1F] mt-1 relative z-10 leading-none" id="kpi-pos">0</div>
                        </div>
                        <div class="clean-card p-8 flex flex-col justify-center relative overflow-hidden">
                            <span class="text-[11px] font-bold text-gray-400 uppercase tracking-widest relative z-10">Capital Aggregation</span>
                            <div class="flex items-baseline gap-2 mt-2 relative z-10">
                                <span class="text-[14px] font-semibold text-gray-400 tracking-wider">VAL</span>
                                <div class="text-[48px] font-bold tracking-tighter text-[#1D1D1F] leading-none" id="kpi-val">0.00</div>
                            </div>
                        </div>
                    </div>

                    <div class="clean-card flex flex-col w-full max-w-full overflow-hidden">
                        <div class="px-8 py-6 border-b border-gray-100 flex justify-between items-center bg-white relative z-10">
                            <h2 class="text-[16px] font-bold text-[#1D1D1F] tracking-tight">Output Matrix</h2>
                        </div>
                        
                        <div class="overflow-x-auto w-full relative z-10">
                            <table class="w-full text-left whitespace-nowrap min-w-max">
                                <thead id="table-head" class="bg-gray-50/50"><tr></tr></thead>
                                <tbody id="table-body" class="divide-y divide-gray-100"></tbody>
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

                    // Render Table Engine
                    function renderTable(headersList) {
                        const theadRow = document.querySelector('#table-head tr');
                        const tbody = document.getElementById('table-body');
                        theadRow.innerHTML = '';
                        tbody.innerHTML = '';

                        // Rebuild Headers
                        headersList.forEach(h => {
                            const th = document.createElement('th');
                            th.className = "px-8 py-4 text-[11px] font-bold text-gray-400 uppercase tracking-widest border-b border-gray-200";
                            th.innerText = h.replace(/_/g, ' ');
                            theadRow.appendChild(th);
                        });

                        // Rebuild Rows
                        data.forEach(row => {
                            const tr = document.createElement('tr');
                            tr.className = "hover:bg-gray-50/80 transition-colors group";
                            
                            headersList.forEach((h, index) => {
                                const td = document.createElement('td');
                                if (index === 0) {
                                    td.className = "px-8 py-5 text-[#1D1D1F] font-semibold";
                                } else {
                                    td.className = "px-8 py-5 text-gray-600 font-medium";
                                }
                                td.innerText = row[h] !== null ? row[h] : '';
                                tr.appendChild(td);
                            });
                            tbody.appendChild(tr);
                        });
                    }

                    // Render Sidebar Interactive Engine
                    function renderSidebar(headersList) {
                        sidebarList.innerHTML = '';
                        headersList.forEach((h, index) => {
                            const li = document.createElement('li');
                            li.className = "flex items-center justify-between p-3 bg-white border border-gray-200 rounded-xl cursor-grab hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm group";
                            li.draggable = true;
                            li.dataset.header = h;
                            
                            // Drag Handle Icon & Text
                            li.innerHTML = `
                                <div class="flex items-center gap-3 overflow-hidden">
                                    <span class="text-[10px] font-bold text-gray-400 w-4 text-right shrink-0">${index + 1}.</span>
                                    <span class="text-[13px] font-semibold text-[#1D1D1F] truncate capitalize">${h.replace(/_/g, ' ')}</span>
                                </div>
                                <svg class="w-4 h-4 text-gray-300 group-hover:text-gray-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"></path></svg>
                            `;

                            // Drag Events
                            li.addEventListener('dragstart', (e) => {
                                li.classList.add('dragging');
                                e.dataTransfer.effectAllowed = 'move';
                            });
                            
                            li.addEventListener('dragend', () => {
                                li.classList.remove('dragging');
                                const newOrder = Array.from(sidebarList.children).map(p => p.dataset.header);
                                renderTable(newOrder);
                                renderSidebar(newOrder); // Refresh numbers
                            });

                            sidebarList.appendChild(li);
                        });
                    }

                    // Initial Render
                    renderTable(currentHeaders);
                    renderSidebar(currentHeaders);

                    // Dropzone logic for vertical list
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
