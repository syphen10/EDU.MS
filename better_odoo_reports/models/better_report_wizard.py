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

        # --- THE PRISM KINETIC HTML MASTERPIECE v1.4 ---
        html_content = """
        <!DOCTYPE html>
        <html lang="en" class="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Better Reports - Prism Kinetic</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
            <style>
                body { 
                    font-family: 'Inter', sans-serif; 
                    background-color: #0f1115; 
                    color: #FAFAFA; 
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }
                .font-mono { font-family: 'JetBrains Mono', monospace; }
                
                ::-webkit-scrollbar { width: 4px; height: 4px; }
                ::-webkit-scrollbar-track { background: transparent; }
                ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
                ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

                @keyframes orbDrift1 {
                    0%, 100% { transform: translate(0, 0) scale(1); }
                    50% { transform: translate(4%, 6%) scale(1.1); }
                }
                @keyframes orbDrift2 {
                    0%, 100% { transform: translate(0, 0) scale(1); }
                    50% { transform: translate(-5%, -4%) scale(1.05); }
                }
                @keyframes flameDrift {
                    0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 0.7; }
                    50% { transform: translate(3%, -4%) scale(1.1) rotate(3deg); opacity: 1; }
                    100% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 0.7; }
                }

                .prism-core-1 {
                    position: fixed; top: -10%; left: -10%; width: 50vw; height: 50vh;
                    background: radial-gradient(circle, rgba(0, 229, 255, 0.04) 0%, transparent 60%);
                    filter: blur(80px); pointer-events: none; z-index: 0;
                    animation: orbDrift1 25s ease-in-out infinite;
                }
                .prism-core-2 {
                    position: fixed; bottom: -20%; right: -10%; width: 60vw; height: 60vh;
                    background: radial-gradient(circle, rgba(0, 255, 157, 0.03) 0%, transparent 60%);
                    filter: blur(100px); pointer-events: none; z-index: 0;
                    animation: orbDrift2 30s ease-in-out infinite;
                }
                
                .purple-flame-1 {
                    position: fixed; bottom: -10%; left: -5%; width: 45vw; height: 55vh;
                    background: radial-gradient(ellipse at center, rgba(168, 85, 247, 0.15) 0%, transparent 65%);
                    filter: blur(90px); pointer-events: none; z-index: 0;
                    animation: flameDrift 18s ease-in-out infinite alternate;
                }
                .purple-flame-2 {
                    position: fixed; top: -5%; right: -10%; width: 40vw; height: 50vh;
                    background: radial-gradient(ellipse at center, rgba(168, 85, 247, 0.12) 0%, transparent 60%);
                    filter: blur(80px); pointer-events: none; z-index: 0;
                    animation: flameDrift 22s ease-in-out infinite alternate-reverse;
                }

                @keyframes gridPan {
                    0% { background-position: 0 0, 0 0; }
                    100% { background-position: 60px 60px, 60px 60px; }
                }
                .architect-grid {
                    background-image: 
                        linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
                    background-size: 60px 60px;
                    mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 20%, transparent 100%);
                    -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 20%, transparent 100%);
                    z-index: 0; position: fixed; inset: -60px; pointer-events: none;
                    animation: gridPan 40s linear infinite;
                }

                .prism-card {
                    background: rgba(20, 22, 28, 0.6);
                    backdrop-filter: blur(40px) saturate(150%);
                    -webkit-backdrop-filter: blur(40px) saturate(150%);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 24px 48px -12px rgba(0, 0, 0, 0.5);
                    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
                }
                .prism-card:hover {
                    transform: translateY(-2px);
                    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 32px 64px -12px rgba(0, 0, 0, 0.6);
                }

                .spotlight { position: relative; }
                .spotlight::after {
                    content: ""; position: absolute; inset: 0; border-radius: inherit; opacity: 0; transition: opacity 0.3s ease;
                    background: radial-gradient(400px circle at var(--mouse-x) var(--mouse-y), rgba(168, 85, 247, 0.06), transparent 40%);
                    z-index: -1; pointer-events: none;
                }
                .spotlight::before {
                    content: ""; position: absolute; inset: -1px; border-radius: inherit; padding: 1px;
                    background: radial-gradient(300px circle at var(--mouse-x) var(--mouse-y), rgba(168, 85, 247, 0.5), transparent 40%);
                    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                    -webkit-mask-composite: xor; mask-composite: exclude; opacity: 0; transition: opacity 0.3s ease; pointer-events: none; z-index: 10;
                }
                .spotlight:hover::after, .spotlight:hover::before { opacity: 1; }
                
                .dragging { opacity: 0.4; transform: scale(0.95); }
                
                /* Dropzone highlight */
                .dropzone-active {
                    border-color: rgba(168, 85, 247, 0.5) !important;
                    background-color: rgba(168, 85, 247, 0.05) !important;
                }
            </style>
        </head>
        <body class="h-screen flex overflow-hidden selection:bg-[#00E5FF]/30 text-[13px]">

            <div class="prism-core-1"></div>
            <div class="prism-core-2"></div>
            <div class="purple-flame-1"></div>
            <div class="purple-flame-2"></div>
            <div class="architect-grid"></div>

            <aside class="w-[320px] bg-[#12141a]/80 backdrop-blur-3xl border-r border-white/[0.04] flex flex-col h-full shrink-0 z-20 relative">
                <div class="h-[84px] flex items-center px-8 border-b border-white/[0.03]">
                    <div class="flex items-center gap-3.5">
                        <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-white to-[#A1A1AA] flex items-center justify-center shadow-[0_4px_12px_rgba(255,255,255,0.1)]">
                            <svg class="w-4 h-4 text-black" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
                        </div>
                        <div class="flex flex-col">
                            <h1 class="text-[15px] font-semibold tracking-tight text-white leading-tight">Better Reports</h1>
                            <span class="text-[10px] font-mono text-[#71717A] tracking-widest uppercase mt-0.5">Workspace</span>
                        </div>
                    </div>
                </div>

                <div class="px-7 py-6 flex-1 overflow-y-auto">
                    <div class="mb-8">
                        <label class="text-[10px] font-medium text-[#71717A] uppercase tracking-[0.2em] mb-3 block">Data Status</label>
                        <div class="bg-[rgba(0,0,0,0.3)] border border-white/[0.05] rounded-xl px-4 py-3.5 spotlight">
                            <span class="text-[#00E5FF] font-mono text-[13px] relative z-10">ONLINE & SYNCED</span>
                        </div>
                    </div>

                    <div>
                        <label class="text-[10px] font-medium text-[#71717A] uppercase tracking-[0.2em] mb-3 block flex items-center justify-between">
                            <span>Active Schema</span>
                            <span class="text-[#a855f7] font-mono text-[9px]">LIVE ORDER</span>
                        </label>
                        <div class="bg-[rgba(0,0,0,0.3)] border border-white/[0.05] rounded-xl p-4 spotlight">
                            <ul id="schema-sidebar-list" class="space-y-2.5 relative z-10 font-mono text-[11px]">
                                </ul>
                        </div>
                    </div>
                </div>
            </aside>

            <main class="flex-1 flex flex-col h-full relative z-10">
                <header class="h-[84px] px-12 flex items-center justify-between border-b border-white/[0.04] bg-transparent z-20">
                    <div class="flex items-center gap-4">
                        <h2 class="text-[22px] font-semibold tracking-tight text-white">Interactive Analytics</h2>
                        <div class="px-2.5 py-1 rounded-md bg-[#00E5FF]/10 border border-[#00E5FF]/20 flex items-center gap-1.5">
                            <span class="w-1 h-1 rounded-full bg-[#00E5FF] animate-pulse"></span>
                            <span class="text-[10px] font-mono text-[#00E5FF] uppercase tracking-wider">Live Connection</span>
                        </div>
                    </div>
                    <button onclick="window.print()" class="text-[13px] font-medium text-[#A1A1AA] hover:text-white transition-colors flex items-center gap-2 px-4 py-2 hover:bg-white/[0.05] rounded-xl spotlight">
                        <span class="relative z-10 flex items-center gap-2">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                            Export PDF
                        </span>
                    </button>
                </header>

                <div class="p-10 overflow-y-auto flex-1 z-10">
                    
                    <div class="grid grid-cols-12 gap-6 mb-6">
                        <div class="col-span-8 flex flex-col gap-6">
                            <div class="prism-card spotlight rounded-[24px] p-8 h-full flex flex-col">
                                <div class="flex items-center justify-between mb-4 relative z-10">
                                    <h3 class="text-[11px] font-medium text-[#71717A] uppercase tracking-[0.2em]">Loaded Dimensions</h3>
                                    <span class="text-[10px] text-[#52525B] font-mono">DRAG TO REORDER</span>
                                </div>
                                <div id="selected-columns" class="flex-1 flex flex-wrap gap-3 relative z-10 p-4 border-2 border-dashed border-white/[0.05] rounded-xl bg-white/[0.01] transition-colors">
                                    </div>
                            </div>
                        </div>

                        <div class="col-span-4 flex flex-col gap-6">
                            <div class="prism-card spotlight rounded-[24px] p-8 flex-1 flex flex-col justify-center relative overflow-hidden">
                                <span class="text-[11px] font-medium text-[#71717A] uppercase tracking-[0.2em] relative z-10">Total Records</span>
                                <div class="text-[56px] font-semibold tracking-tighter text-white mt-1 relative z-10 leading-none" id="kpi-pos">0</div>
                            </div>
                            <div class="prism-card spotlight rounded-[24px] p-8 flex-1 flex flex-col justify-center relative overflow-hidden">
                                <span class="text-[11px] font-medium text-[#71717A] uppercase tracking-[0.2em] relative z-10">Capital Aggregation</span>
                                <div class="flex items-baseline gap-2 mt-2 relative z-10">
                                    <span class="text-[13px] font-mono text-[#71717A] tracking-widest">VAL</span>
                                    <div class="text-[48px] font-semibold tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-[#00FF9D] to-[#00B36E] leading-none" id="kpi-val">0.00</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="prism-card spotlight rounded-[24px] overflow-hidden flex flex-col">
                        <div class="px-8 py-5 border-b border-white/[0.04] flex justify-between items-center bg-black/10 relative z-10">
                            <h2 class="text-[14px] font-semibold text-white tracking-wide">Output Matrix</h2>
                        </div>
                        <div class="overflow-x-auto relative z-10">
                            <table class="w-full text-left whitespace-nowrap">
                                <thead id="table-head"><tr></tr></thead>
                                <tbody id="table-body"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>

            <script>
                // Odoo injects the JSON here
                window.ODOO_DATA = REPLACE_ME_WITH_DATA;
                window.ODOO_KPIS = REPLACE_ME_WITH_KPIS;
                const data = window.ODOO_DATA;

                // Wire up the spotlight tracking engine
                document.querySelectorAll('.spotlight').forEach(el => {
                    el.addEventListener('mousemove', e => {
                        const rect = el.getBoundingClientRect();
                        el.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
                        el.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
                    });
                });

                document.addEventListener("DOMContentLoaded", () => {
                    // Update KPIs
                    document.getElementById('kpi-pos').innerText = window.ODOO_KPIS.total_records.toLocaleString();
                    document.getElementById('kpi-val').innerText = window.ODOO_KPIS.total_capital.toLocaleString(undefined, {minimumFractionDigits: 2});

                    if (data.length === 0) return;

                    const columnContainer = document.getElementById('selected-columns');
                    const sidebarList = document.getElementById('schema-sidebar-list');
                    let currentHeaders = Object.keys(data[0]);

                    // Function to update the Sidebar Legend
                    function updateSidebarLegend(headersList) {
                        sidebarList.innerHTML = '';
                        headersList.forEach((h, index) => {
                            const li = document.createElement('li');
                            li.className = "flex items-center gap-3 text-[#A1A1AA] border-b border-white/[0.02] pb-2 last:border-0 last:pb-0";
                            li.innerHTML = `<span class="text-[#52525B] w-4 text-right">${index + 1}.</span> <span class="text-[#E4E4E7] truncate uppercase tracking-wider">${h.replace(/_/g, ' ')}</span>`;
                            sidebarList.appendChild(li);
                        });
                    }

                    // Render Table Engine
                    function renderTable(headersList) {
                        const theadRow = document.querySelector('#table-head tr');
                        const tbody = document.getElementById('table-body');
                        theadRow.innerHTML = '';
                        tbody.innerHTML = '';

                        // Rebuild Headers
                        headersList.forEach(h => {
                            const th = document.createElement('th');
                            th.className = "px-8 py-4 text-[10px] font-semibold text-[#71717A] uppercase tracking-[0.2em] border-b border-white/[0.04]";
                            th.innerText = h.replace(/_/g, ' ');
                            theadRow.appendChild(th);
                        });

                        // Rebuild Rows
                        data.forEach(row => {
                            const tr = document.createElement('tr');
                            tr.className = "hover:bg-white/[0.02] transition-colors group";
                            
                            headersList.forEach((h, index) => {
                                const td = document.createElement('td');
                                if (index === 0) {
                                    td.className = "px-8 py-5 text-[#E4E4E7] font-medium border-b border-white/[0.02] flex items-center gap-3";
                                    td.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-[#00E5FF] shadow-[0_0_8px_rgba(0,229,255,0.8)] group-hover:animate-pulse"></span>${row[h] !== null ? row[h] : ''}`;
                                } else {
                                    td.className = "px-8 py-5 text-[#A1A1AA] border-b border-white/[0.02] group-hover:text-white transition-colors";
                                    td.innerText = row[h] !== null ? row[h] : '';
                                }
                                tr.appendChild(td);
                            });
                            tbody.appendChild(tr);
                        });
                    }

                    // Initial Renders
                    renderTable(currentHeaders);
                    updateSidebarLegend(currentHeaders);

                    // Create Draggable Dimension Pills
                    currentHeaders.forEach(h => {
                        const pill = document.createElement('div');
                        pill.className = "bg-[rgba(0,0,0,0.6)] border border-white/[0.08] text-white px-3 py-1.5 rounded-xl flex items-center gap-2 cursor-grab hover:border-[#a855f7]/50 hover:bg-[#a855f7]/10 transition-all select-none spotlight";
                        pill.draggable = true;
                        pill.dataset.header = h;
                        pill.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-[#a855f7] shadow-[0_0_8px_rgba(168,85,247,0.8)] relative z-10"></span> <span class="font-medium text-[13px] text-[#E4E4E7] relative z-10">${h.replace(/_/g, ' ')}</span>`;
                        
                        // Re-bind hover to the individual pill so it glows
                        pill.addEventListener('mousemove', e => {
                            const rect = pill.getBoundingClientRect();
                            pill.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
                            pill.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
                        });

                        // Drag Events
                        pill.addEventListener('dragstart', (e) => {
                            pill.classList.add('dragging');
                            e.dataTransfer.effectAllowed = 'move';
                        });
                        
                        pill.addEventListener('dragend', () => {
                            pill.classList.remove('dragging');
                            const newOrder = Array.from(columnContainer.children).map(p => p.dataset.header);
                            renderTable(newOrder);
                            updateSidebarLegend(newOrder); // Update sidebar on drop
                        });

                        columnContainer.appendChild(pill);
                    });

                    // Dropzone Visual Feedback & Logic
                    columnContainer.addEventListener('dragenter', (e) => {
                        e.preventDefault();
                        columnContainer.classList.add('dropzone-active');
                    });
                    columnContainer.addEventListener('dragleave', (e) => {
                        if(e.target === columnContainer) {
                            columnContainer.classList.remove('dropzone-active');
                        }
                    });
                    columnContainer.addEventListener('drop', () => {
                        columnContainer.classList.remove('dropzone-active');
                    });

                    columnContainer.addEventListener('dragover', e => {
                        e.preventDefault();
                        const draggable = document.querySelector('.dragging');
                        if (!draggable) return;
                        const afterElement = getDragAfterElement(columnContainer, e.clientX);
                        if (afterElement == null) {
                            columnContainer.appendChild(draggable);
                        } else {
                            columnContainer.insertBefore(draggable, afterElement);
                        }
                    });

                    function getDragAfterElement(container, x) {
                        const draggableElements = [...container.querySelectorAll('div[draggable="true"]:not(.dragging)')];
                        return draggableElements.reduce((closest, child) => {
                            const box = child.getBoundingClientRect();
                            const offset = x - box.left - box.width / 2;
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
