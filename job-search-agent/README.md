# Autonomous Real-Time Job Search System

A high-performance, real-time job opportunity discovery engine that searches LinkedIn (and optional portals like Indeed, Glassdoor) across key engineering & business roles without auto-applying.

---

## 🎯 Supported Pre-Configured Categories

- **`sde`**: Software Development Engineer, Backend Engineer, Frontend Engineer, Full Stack Developer, DevOps Engineer
- **`data`**: Data Engineer, Data Scientist, Machine Learning Engineer, Data Analyst, AI Engineer
- **`core`**: Embedded Software Engineer, Hardware Engineer, Robotics Engineer, VLSI Design Engineer, Mechanical Engineer
- **`finance`**: Quantitative Analyst, Financial Analyst, Risk Analyst, Fintech Software Engineer, Investment Banking Analyst
- **`custom`**: Any keyword or phrase you provide via `--query`.

---

## 🚀 How to Run

### 1. Search a Specific Category
```bash
# Search SDE roles in India (last 72 hours)
python app.py -c sde --location "India"

# Search Finance & Quant roles (last 24 hours)
python app.py -c finance --location "Remote" --hours 24

# Search Data & AI roles
python app.py -c data --location "Bengaluru"
```

### 2. Search a Custom Role or Query
```bash
python app.py --query "Staff Golang Engineer" --location "Remote"
```

### 3. Run a Full Batch Sweep across ALL Categories
```bash
python app.py --all --location "India" --count 5
```

---

## 📊 Outputs & Visual Dashboard

Every search automatically updates:
1. **Interactive HTML Dashboard**: `results/jobs_dashboard.html` (Filter by Category, Location, Search terms in real-time, click to apply/view on LinkedIn).
2. **CSV Export**: `results/jobs_latest.csv` (Spreadsheet friendly).
3. **JSON Export**: `results/jobs_latest.json` (For CV tailoring or LLM prompt pipelines).
4. **SQLite Database**: `jobs_database.db` (Persistent storage with automatic deduplication).
