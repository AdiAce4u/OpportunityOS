import os
import json
import pandas as pd
from db import JobDatabase
from cv_matcher import CVProjectMatcher
from config import DEFAULT_SETTINGS

def generate_html_dashboard(db_path=None, cv_path=None, output_file="results/jobs_dashboard.html", sort_by="match"):
    db = JobDatabase(db_path or DEFAULT_SETTINGS["db_path"])
    jobs = db.get_all_jobs(sort_by=sort_by)
    
    matcher = CVProjectMatcher(cv_path or DEFAULT_SETTINGS["default_cv_path"])
    projects = matcher.projects
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save CSV and JSON exports
    if jobs:
        df = pd.DataFrame(jobs)
        df.to_csv("results/jobs_latest.csv", index=False)
        with open("results/jobs_latest.json", "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2)

    jobs_json_str = json.dumps(jobs)
    projects_json_str = json.dumps(projects)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Multi-Platform Job Radar & Project Matcher</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .custom-scrollbar::-webkit-scrollbar {{ width: 6px; }}
        .custom-scrollbar::-webkit-scrollbar-track {{ background: #0f172a; }}
        .custom-scrollbar::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 3px; }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans">
    <div class="max-w-7xl mx-auto px-4 py-8">
        
        <!-- Header -->
        <header class="flex flex-col md:flex-row md:items-center justify-between pb-6 mb-8 border-b border-slate-800 gap-4">
            <div>
                <div class="flex items-center gap-3">
                    <div class="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-2xl shadow-lg shadow-blue-500/20">
                        <i class="fa-solid fa-crosshairs text-2xl"></i>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                            Autonomous Job Matcher & Radar
                            <span class="text-xs font-medium px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">v2.0 Multi-Portal</span>
                        </h1>
                        <p class="text-slate-400 text-sm mt-0.5">LinkedIn • Indeed • Glassdoor • Wellfound | Ranked by Master CV Project Similarity & Stipend</p>
                    </div>
                </div>
            </div>
            
            <div class="flex flex-wrap items-center gap-2.5">
                <button onclick="toggleCVModal()" class="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-indigo-400 border border-indigo-500/30 hover:border-indigo-500/60 rounded-xl text-xs font-semibold transition flex items-center gap-2">
                    <i class="fa-solid fa-file-lines"></i> View Master CV ({len(projects)} Projects)
                </button>
                <span id="total-badge" class="px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    <i class="fa-solid fa-briefcase mr-1.5"></i> {len(jobs)} Opportunities
                </span>
                <a href="jobs_latest.csv" download class="px-3 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium rounded-xl border border-slate-800 transition flex items-center gap-1.5">
                    <i class="fa-solid fa-download"></i> CSV
                </a>
                <a href="jobs_latest.json" download class="px-3 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium rounded-xl border border-slate-800 transition flex items-center gap-1.5">
                    <i class="fa-solid fa-code"></i> JSON
                </a>
            </div>
        </header>

        <!-- Filters & Priority Sorting Controls -->
        <div class="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-4 mb-8 shadow-xl">
            <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                
                <!-- Live Search Bar -->
                <div class="md:col-span-4 relative">
                    <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3.5 text-slate-500 text-sm"></i>
                    <input type="text" id="searchInput" placeholder="Search keywords, company, skills..." 
                        class="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm focus:outline-none focus:border-blue-500 text-white placeholder-slate-500 transition">
                </div>

                <!-- Priority Ranking / Sorting Dropdown -->
                <div class="md:col-span-3">
                    <label class="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                        <i class="fa-solid fa-arrow-down-short-wide text-blue-400 mr-1"></i> Priority Ranking:
                    </label>
                    <select id="sortByDropdown" class="w-full px-3.5 py-2 bg-slate-950 border border-blue-500/40 rounded-xl text-sm font-medium focus:outline-none focus:border-blue-400 text-blue-300">
                        <option value="match">🎯 JD Similarity with CV Projects (Highest First)</option>
                        <option value="salary">💰 Stipend / Salary (Decreasing Order)</option>
                        <option value="recent">🕒 Most Recent Postings First</option>
                    </select>
                </div>

                <!-- Category Filter -->
                <div class="md:col-span-3">
                    <label class="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Category:</label>
                    <select id="categoryFilter" class="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm focus:outline-none focus:border-blue-500 text-slate-200">
                        <option value="ALL">All Categories</option>
                        <option value="sde">💻 SDE / Software</option>
                        <option value="data">📊 Data / AI / ML</option>
                        <option value="core">⚡ Core Engineering</option>
                        <option value="finance">📈 Finance & Quant</option>
                        <option value="custom">🔍 Custom Searches</option>
                    </select>
                </div>

                <!-- Platform Filter -->
                <div class="md:col-span-2">
                    <label class="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Portal:</label>
                    <select id="siteFilter" class="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm focus:outline-none focus:border-blue-500 text-slate-200">
                        <option value="ALL">All Portals</option>
                        <option value="linkedin">LinkedIn</option>
                        <option value="indeed">Indeed</option>
                        <option value="glassdoor">Glassdoor</option>
                        <option value="wellfound">Wellfound</option>
                    </select>
                </div>

            </div>
        </div>

        <!-- Job Cards Grid -->
        <div id="jobsList" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- Populated via JavaScript -->
        </div>

        <!-- Empty State -->
        <div id="emptyState" class="hidden text-center py-20">
            <div class="inline-flex p-5 bg-slate-900 rounded-2xl text-slate-500 mb-3 border border-slate-800">
                <i class="fa-solid fa-filter-circle-xmark text-3xl"></i>
            </div>
            <h3 class="text-lg font-semibold text-slate-300">No matching opportunities found</h3>
            <p class="text-sm text-slate-500 mt-1">Try switching the category or clearing the search keyword filter.</p>
        </div>

    </div>

    <!-- Master CV Modal Drawer -->
    <div id="cvModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 rounded-3xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl">
            <div class="p-6 border-b border-slate-800 flex items-center justify-between">
                <div>
                    <h3 class="text-lg font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-layer-group text-indigo-400"></i> Master CV Project Repository
                    </h3>
                    <p class="text-xs text-slate-400 mt-0.5">Projects automatically classified & matched against Job Descriptions</p>
                </div>
                <button onclick="toggleCVModal()" class="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
            </div>
            <div id="cvProjectsContainer" class="p-6 overflow-y-auto space-y-4 custom-scrollbar">
                <!-- Injected via JS -->
            </div>
        </div>
    </div>

    <script>
        const jobs = {jobs_json_str};
        const projects = {projects_json_str};

        const jobsList = document.getElementById('jobsList');
        const searchInput = document.getElementById('searchInput');
        const sortByDropdown = document.getElementById('sortByDropdown');
        const categoryFilter = document.getElementById('categoryFilter');
        const siteFilter = document.getElementById('siteFilter');
        const emptyState = document.getElementById('emptyState');
        const cvModal = document.getElementById('cvModal');
        const cvProjectsContainer = document.getElementById('cvProjectsContainer');

        function toggleCVModal() {{
            cvModal.classList.toggle('hidden');
        }}

        // Render projects in CV modal
        projects.forEach((p, idx) => {{
            const div = document.createElement('div');
            div.className = "p-4 bg-slate-950 border border-slate-800/80 rounded-2xl";
            div.innerHTML = `
                <div class="flex items-center justify-between gap-2 mb-2">
                    <h4 class="font-semibold text-sm text-indigo-300">#${{idx + 1}} ${{p.title}}</h4>
                    <span class="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">${{p.inferred_domain}}</span>
                </div>
                <pre class="text-xs text-slate-400 whitespace-pre-wrap font-sans leading-relaxed">${{p.content.split('\\n').slice(1).join('\\n')}}</pre>
            `;
            cvProjectsContainer.appendChild(div);
        }});

        function getPlatformBadge(site) {{
            const s = (site || 'linkedin').toLowerCase();
            const map = {{
                'linkedin': {{ bg: 'bg-blue-600/10', text: 'text-blue-400', border: 'border-blue-500/30', icon: 'fa-brands fa-linkedin', label: 'LinkedIn' }},
                'indeed': {{ bg: 'bg-indigo-600/10', text: 'text-indigo-400', border: 'border-indigo-500/30', icon: 'fa-solid fa-briefcase', label: 'Indeed' }},
                'glassdoor': {{ bg: 'bg-emerald-600/10', text: 'text-emerald-400', border: 'border-emerald-500/30', icon: 'fa-solid fa-door-open', label: 'Glassdoor' }},
                'wellfound': {{ bg: 'bg-orange-600/10', text: 'text-orange-400', border: 'border-orange-500/30', icon: 'fa-brands fa-angellist', label: 'Wellfound' }},
            }};
            const p = map[s] || {{ bg: 'bg-slate-800', text: 'text-slate-300', border: 'border-slate-700', icon: 'fa-solid fa-globe', label: site }};
            return `<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold ${{p.bg}} ${{p.text}} border ${{p.border}}"><i class="${{p.icon}}"></i> ${{p.label}}</span>`;
        }}

        function getMatchScoreBadge(score) {{
            const num = parseFloat(score || 0);
            let color = "from-emerald-500 to-teal-500 text-emerald-300 border-emerald-500/30 bg-emerald-500/10";
            if (num < 50) {{
                color = "from-slate-500 to-slate-600 text-slate-400 border-slate-700 bg-slate-800/50";
            }} else if (num < 75) {{
                color = "from-blue-500 to-cyan-500 text-blue-300 border-blue-500/30 bg-blue-500/10";
            }}
            return `
                <div class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold ${{color}} border shadow-sm">
                    <i class="fa-solid fa-fire text-[11px]"></i> ${{num.toFixed(0)}}% Match
                </div>
            `;
        }}

        function renderJobs() {{
            const query = searchInput.value.toLowerCase().trim();
            const sortBy = sortByDropdown.value;
            const cat = categoryFilter.value;
            const site = siteFilter.value;

            let filtered = jobs.filter(j => {{
                const matchesQuery = !query || 
                    (j.title && j.title.toLowerCase().includes(query)) ||
                    (j.company && j.company.toLowerCase().includes(query)) ||
                    (j.description && j.description.toLowerCase().includes(query)) ||
                    (j.best_matching_project && j.best_matching_project.toLowerCase().includes(query));
                
                const matchesCat = cat === 'ALL' || (j.category && j.category.toLowerCase() === cat.toLowerCase());
                const matchesSite = site === 'ALL' || (j.site && j.site.toLowerCase() === site.toLowerCase());

                return matchesQuery && matchesCat && matchesSite;
            }});

            // Priority sorting logic
            if (sortBy === 'match') {{
                filtered.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
            }} else if (sortBy === 'salary') {{
                filtered.sort((a, b) => (b.normalized_salary || 0) - (a.normalized_salary || 0));
            }} else if (sortBy === 'recent') {{
                filtered.sort((a, b) => new Date(b.first_seen_at || 0) - new Date(a.first_seen_at || 0));
            }}

            jobsList.innerHTML = '';
            if (filtered.length === 0) {{
                emptyState.classList.remove('hidden');
            }} else {{
                emptyState.classList.add('hidden');
                filtered.forEach(j => {{
                    const card = document.createElement('div');
                    card.className = "bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-3xl p-5 flex flex-col justify-between transition-all duration-200 hover:shadow-2xl hover:shadow-indigo-500/10 group relative";
                    
                    const salaryDisplay = j.display_salary && j.display_salary !== 'Not Disclosed' 
                        ? `<span class="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/30"><i class="fa-solid fa-sack-dollar text-[11px]"></i> ${{j.display_salary}}</span>`
                        : `<span class="text-xs text-slate-500 font-medium"><i class="fa-solid fa-coins text-[10px] mr-1"></i> Salary not listed</span>`;

                    const keywordsHtml = (j.matched_keywords && Array.isArray(j.matched_keywords) && j.matched_keywords.length > 0)
                        ? j.matched_keywords.slice(0, 4).map(k => `<span class="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[10px] font-mono border border-slate-700">${{k}}</span>`).join(' ')
                        : '';

                    const descSnippet = j.description ? (j.description.length > 170 ? j.description.substring(0, 170) + '...' : j.description) : 'No description snippet available.';

                    card.innerHTML = `
                        <div>
                            <!-- Top Bar: Platform & Match Badge -->
                            <div class="flex items-center justify-between gap-2 mb-3">
                                ${{getPlatformBadge(j.site)}}
                                ${{getMatchScoreBadge(j.match_score)}}
                            </div>

                            <!-- Job Title & Company -->
                            <h2 class="text-base font-bold text-white group-hover:text-blue-400 transition line-clamp-2 leading-snug">
                                ${{j.title || 'Untitled Opportunity'}}
                            </h2>
                            <p class="text-sm font-semibold text-slate-300 mt-1 flex items-center gap-1.5">
                                <i class="fa-regular fa-building text-slate-500 text-xs"></i> ${{j.company || 'Confidential'}}
                            </p>
                            <p class="text-xs text-slate-400 mt-0.5 flex items-center gap-1.5">
                                <i class="fa-solid fa-location-dot text-slate-500 text-xs"></i> ${{j.location || 'Remote / Unspecified'}}
                            </p>

                            <!-- Compensation & Date -->
                            <div class="flex items-center justify-between mt-3 pt-3 border-t border-slate-800/80">
                                ${{salaryDisplay}}
                                <span class="text-[11px] text-slate-500"><i class="fa-regular fa-clock"></i> ${{j.date_posted || 'Recent'}}</span>
                            </div>

                            <!-- Best Matching Master CV Project Box -->
                            <div class="mt-3.5 p-3 rounded-2xl bg-slate-950/70 border border-slate-800/80">
                                <div class="text-[10px] font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1 mb-1">
                                    <i class="fa-solid fa-wand-magic-sparkles text-[10px]"></i> Top Project Match
                                </div>
                                <div class="text-xs font-semibold text-slate-200 line-clamp-1">
                                    ${{j.best_matching_project || 'General Candidate Profile'}}
                                </div>
                                ${{keywordsHtml ? `<div class="flex flex-wrap gap-1 mt-2">${{keywordsHtml}}</div>` : ''}}
                            </div>

                            <!-- Snippet -->
                            <div class="mt-3 text-xs text-slate-400 line-clamp-2 leading-relaxed">
                                ${{descSnippet}}
                            </div>
                        </div>

                        <!-- Action Footer -->
                        <div class="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                            <span class="text-[11px] text-slate-500 font-mono capitalize">
                                ${{j.category || 'General'}}
                            </span>
                            <a href="${{j.job_url}}" target="_blank" rel="noopener noreferrer" 
                                class="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl transition shadow-lg shadow-blue-600/20">
                                View & Apply <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
                            </a>
                        </div>
                    `;
                    jobsList.appendChild(card);
                }});
            }}
        }}

        searchInput.addEventListener('input', renderJobs);
        sortByDropdown.addEventListener('change', renderJobs);
        categoryFilter.addEventListener('change', renderJobs);
        siteFilter.addEventListener('change', renderJobs);

        renderJobs();
    </script>
</body>
</html>
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"[+] Dashboard generated at: {os.path.abspath(output_file)}")
    return os.path.abspath(output_file)

if __name__ == "__main__":
    generate_html_dashboard()
