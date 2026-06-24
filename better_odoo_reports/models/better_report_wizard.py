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
                
                # Clean up relational fields
                if isinstance(val, tuple): 
                    val = val[1]
                
                # THE FIX: Convert Date/Time to Strings
                if isinstance(val, (datetime, date)):
                    val = str(val)
                
                # Handle empty values
                if val is False or val is None:
                    val = ""
                    
                row[fname] = val
                
                # Aggregate totals
                if isinstance(val, (int, float)):
                    total_amount += float(val)
                    
            report_data.append(row)

        json_data = json.dumps(report_data)
        kpi_data = json.dumps({"total_records": len(records), "total_capital": total_amount})

        # --- THE PRISM KINETIC HTML MASTERPIECE ---
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
                    background-color: #030303; 
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
                .prism-core-1 {
                    position: fixed; top: -10%; left: -10%; width: 50vw; height: 50vh;
                    background: radial-gradient(circle, rgba(0, 229, 255, 0.05) 0%, transparent 60%);
                    filter: blur(80px); pointer-events: none; z-index: 0;
                    animation: orbDrift1 25s ease-in-out infinite;
                }
                .prism-core-2 {
                    position: fixed; bottom: -20%; right: -10%; width: 60vw; height: 60vh;
                    background: radial-gradient(circle, rgba(0, 255, 157, 0.04) 0%, transparent 60%);
                    filter: blur(100px); pointer-events: none; z-index: 0;
                    animation: orbDrift2 30s ease-in-out infinite;
                }

                @keyframes gridPan {
                    0% { background-position: 0 0, 0 0; }
                    100% { background-position: 60px 60px, 60px 60px; }
                }
                .architect-grid {
                    background-image: 
                        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
                    background-size: 60px 60px;
                    mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 20%, transparent 100%);
                    -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 20%, transparent 100%);
                    z-index: 0; position: fixed; inset: -60px; pointer-events: none;
                    animation: gridPan 40s linear infinite;
                }

                @keyframes spatialEntrance {
                    0% { opacity: 0; transform: translateY(24px) scale(0.98); filter: blur(4px); }
                    100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
                }
                .animate-enter { opacity: 0; animation: spatialEntrance 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
                .delay-100 { animation-delay: 100ms; }
                .delay-200 { animation-delay: 200ms; }
                .delay-300 { animation-delay: 300ms; }
                .delay-400 { animation-delay: 400ms; }
                .delay-500 { animation-delay: 500ms; }

                .prism-card {
                    background: rgba(12, 12, 14, 0.5);
                    backdrop-filter: blur(40px) saturate(150%);
                    -webkit-backdrop-filter: blur(40px) saturate(150%);
                    border: 1px solid rgba(255, 255, 255, 0.06);
                    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 24px 48px -12px rgba(0, 0, 0, 0.5);
                    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
                }
                .prism-card:hover {
                    transform: translateY(-2px);
                    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 32px 64px -12px rgba(0, 0, 0, 0.6);
                }

                .spotlight { position: relative; }
                .spotlight::after {
                    content: ""; position: absolute; inset: 0; border-radius: inherit; opacity: 0; transition: opacity 0.3s ease;
                    background: radial-gradient(400px circle at var(--mouse-x) var(--mouse-y), rgba(0, 229, 255, 0.06), transparent 40%);
                    z-index: -1; pointer-events: none;
                }
                .spotlight::before {
                    content: ""; position: absolute; inset: -1px; border-radius: inherit; padding: 1px;
                    background: radial-gradient(300px circle at var(--mouse-x) var(--mouse-y), rgba(0, 229, 255, 0.4), transparent 40%);
                    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                    -webkit-mask-composite: xor; mask-composite: exclude; opacity: 0; transition: opacity 0.3s ease; pointer-events: none; z-index: 10;
                }
                .spotlight:hover::after, .spotlight:hover::before { opacity: 1; }

                .btn-fiber {
                    background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                }
                .btn-fiber:hover {
                    background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.3);
                    box-shadow: 0 0 20px rgba(255,255,255,0.05), inset 0 0 15px rgba(255,255,255,0.05); transform: translateY(-1px) scale(1.02);
                }
                .fade-enter { animation: spatialEntrance 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
            </style>
        </head>
        <body class="h-screen flex overflow-hidden selection:bg-[#00E5FF]/30 text-[13px]">

            <div class="prism-core-1"></div>
            <div class="prism-core-2"></div>
            <div class="architect-grid"></div>

            <aside class="w-[320px] bg-[#050507]/60 backdrop-blur-3xl border-r border-white/[0.06] flex flex-col h-full shrink-0 z-20 relative animate-enter">
                <div class="h-[84px] flex items-center px-8 border-b border-white/[0.04]">
                    <div class="flex items-center gap-3.5">
                        <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-white to-[#A1A1AA] flex items-center justify-center shadow-[0_4px_12px_rgba(255,255,255,0.1)] transition-transform hover:scale-105 hover:rotate-3 duration-300">
                            <svg class="w-4 h-4 text-black" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="3" y1="9" x2="21" y2="9"></line>
                                <line x1="9" y1="21" x2="9" y2="9"></line>
                            </svg>
                        </div>
                        <div class="flex flex-col">
                            <h1 class="text-[15px] font-semibold tracking-tight text-white leading-tight">Better Reports</h1>
                            <span class="text-[10px] font-mono text-[#71717A] tracking-widest uppercase mt-0.5">Workspace</span>
                        </div>
                    </div>
                </div>

                <div class="px-7 py-6 flex-1 overflow-y-auto space-y-10">
                    <div class="animate-enter delay-100">
                        <label class="text-[10px] font-medium text-[#71717A] uppercase tracking-[0.2em] mb-3 block">Data Status</label>
                        <div class="relative group bg-[rgba(0,0,0,0.4)] border border-white/[0.05] rounded-xl hover:border-[#00E5FF]/30 transition-all spotlight px-4 py-3.5">
                            <span class="text-[#00E5FF] font-mono text-[13px]">ONLINE & SYNCED</span>
                        </div>
                    </div>
                </div>
            </aside>

            <main class="flex-1 flex flex-col h-full relative z-10">
                
                <header class="h-[84px] px-12 flex items-center justify-between border-b border-white/[0.04] bg-transparent z-20 animate-enter delay-100">
                    <div class="flex items-center gap-4">
                        <h2 class="text-[22px] font-semibold tracking-tight text-white">Interactive Analytics</h2>
                        <div class="px-2.5 py-1 rounded-md bg-[#00E5FF]/10 border border-[#00E5FF]/20 flex items-center gap-1.5">
                            <span class="w-1 h-1 rounded-full bg-[#00E5FF] animate-pulse"></span>
                            <span class="text-[10px] font-mono text-[#00E5FF] uppercase tracking-wider">Live Connection</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-4">
                        <button onclick="window.print()" class="text-[13px] font-medium text-[#A1A1AA] hover:text-white transition-colors flex items-center gap-2 px-4 py-2 hover:bg-white/[0.05] rounded-xl spotlight">
                            <span class="relative z-10 flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                                Export PDF
                            </span>
                        </button>
                    </div>
                </header>

                <div class="p-10 overflow-y-auto flex-1 z-10">
                    
                    <div class="grid grid-cols-12 gap-6 mb-6">
                        <div class="col-span-8 flex flex-col gap-6">
                            <div class="prism-card rounded-[24px] p-8 animate-enter delay-300 spotlight h-full">
                                <h3 class="text-[11px] font-medium text-[#71717A] uppercase tracking-[0.2em] mb-6 relative z-10">Loaded Dimensions</h3>
                                <div id="selected-columns" class="flex flex-wrap gap-3 relative z-10">
                                    </div>
                            </div>
                        </div>

                        <div class="col-span-4 flex flex-col gap-6">
                            <div class="prism-card rounded-[24px] p-8 flex-1 flex flex-col justify-center relative overflow-hidden animate-enter delay-200 spotlight">
                                <div class="absolute -top-10 -right-10 w-40 h-40 bg-[#00E5FF]/10 blur-[40px] rounded-full transition-transform duration-700 hover:scale-150"></div>
                                <span class="text-[11px] font-medium text-[#71717A] uppercase tracking-[0.2em] relative z-10">Total Records</span>
                                <div class="text-[56px] font-semibold tracking-tighter text-white mt-1 relative z-10 leading-none transition-all duration-300" id="kpi-pos">0</div>
                            </div>
                            <div class="prism-card rounded-[24px] p-8 flex-1 flex flex-col justify-center relative overflow-hidden animate-enter delay-300 spotlight">
                                <div class="absolute -top-10 -right-10 w-40 h-40 bg-[#00FF9D]/10 blur-[40px] rounded-full transition-transform duration-700 hover:scale-150"></div>
                                <span class="text-[11px] font-medium text-[#71717A] uppercase tracking-[0.2em] relative z-10">Capital Aggregation</span>
                                <div class="flex items-baseline gap-2 mt-2 relative z-10">
                                    <span class="text-[13px] font-mono text-[#71717A] tracking-widest">VAL</span>
                                    <div class="text-[48px] font-semibold tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-[#00FF9D] to-[#00B36E] leading-none transition-all duration-300" id="kpi-val">0.00</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="prism-card rounded-[24px] overflow-hidden flex flex-col animate-enter delay-400 spotlight">
                        <div class="px-8 py-5 border-b border-white/[0.06] flex justify-between items-center bg-black/20 relative z-10">
                            <div class="flex items-center gap-3">
                                <h2 class="text-[14px] font-semibold text-white tracking-wide">Output Matrix</h2>
                            </div>
                        </div>
                        
                        <div class="overflow-x-auto relative z-10">
                            <table class="w-full text-left whitespace-nowrap">
                                <thead id="table-head">
                                    <tr>
                                        </tr>
                                </thead>
                                <tbody id="table-body">
                                    </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>

            <script>
                // Odoo injects the JSON here
                window.ODOO_DATA = REPLACE_ME_WITH_DATA;
                window.ODOO_KPIS = REPLACE_ME_WITH_KPIS;

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

                    const data = window.ODOO_DATA;
                    if (data.length === 0) return;

                    const headers = Object.keys(data[0]);
                    
                    // Render Active Columns Pill
                    const columnContainer = document.getElementById('selected-columns');
                    headers.forEach(h => {
                        const pill = document.createElement('div');
                        pill.className = "bg-[rgba(0,0,0,0.4)] border border-white/[0.08] text-white px-3 py-1.5 rounded-xl flex items-center gap-2 relative z-10";
                        pill.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-[#00E5FF] shadow-[0_0_8px_rgba(0,229,255,0.8)]"></span> <span class="font-medium text-[13px] text-[#E4E4E7]">${h.replace(/_/g, ' ')}</span>`;
                        columnContainer.appendChild(pill);
                    });

                    // Render Table Headers
                    const theadRow = document.querySelector('#table-head tr');
                    headers.forEach(h => {
                        const th = document.createElement('th');
                        th.className = "px-8 py-4 text-[10px] font-semibold text-[#71717A] uppercase tracking-[0.2em] border-b border-white/[0.04]";
                        th.innerText = h.replace(/_/g, ' ');
                        theadRow.appendChild(th);
                    });

                    // Render Table Rows
                    const tbody = document.getElementById('table-body');
                    data.forEach(row => {
                        const tr = document.createElement('tr');
                        tr.className = "hover:bg-white/[0.03] transition-colors group";
                        
                        headers.forEach((h, index) => {
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
