# OpportunityOS: Autonomous Agentic Job Application Platform

> **"The user gives the agent a goal. The agent autonomously discovers opportunities, decides which ones are worth pursuing, prepares everything required, pauses for human approval at the critical point, executes the application via browser automation, and tracks progress afterward."**

---

## 🎯 Executive Overview

**OpportunityOS** is an autonomous multi-agent job-search and application platform designed to replace fixed pipelines with dynamic agentic reasoning. A candidate provides their resume, skills, preferred roles, locations, and salary/stipend floor. 

The system autonomously:
1. **Understands Goals & Plans Search Strategy**
2. **Loops Dynamic Multi-Query Discovery** across sources until target opportunity quotas are satisfied
3. **Extracts Normalized Job Specs** (JDs, skills, eligibility, deadlines)
4. **Applies Hard Eligibility Constraints** (degrees, graduation years, required experience floor, work authorization)
5. **Calculates Multi-Dimensional Fit & Explains Recommendations** ("Why this job?" breakdown)
6. **Researches Target Companies** (domain, size, technology stack, milestone news, culture)
7. **Tailors Resumes Truthfully** (Zero hallucinations: strictly highlights actual candidate facts and renders PDF)
8. **Prepares Application Packages** (Cover letters, motivation answers, detects missing info)
9. **Enforces Human-in-the-Loop Review** (candidate reviews, edits, and authorizes)
10. **Executes Browser Automation** via Playwright (form inspection, document upload, submission, confirmation capture)
11. **Tracks Application Lifecycle & Automates Follow-Ups** (status monitoring, interview detection, prep copilot)

---

## 🏗️ 14-Stage End-to-End Workflow Architecture

```
1. User Input & Setup (Resume PDF, Preferences, Constraints)
   ↓
2. Supervisor Agent (Goal Parsing & Search Strategy Planning)
   ↓
3. Job Search Agent (Autonomous Multi-Query Iterative Loop)
   ├── [Opportunities < Target Quota] ──> Generate New Queries ──> Search Again
   └── [Enough Opportunities Found] ──> Continue
   ↓
4. Job Information Extraction (Normalized Specifications & Database)
   ↓
5. Eligibility & Filtering Agent (Hard Rule Enforcement)
   ├── [Ineligible] ──> Discard with explicit rationale
   └── [Eligible] ──> Pass to Next Stage
   ↓
6. Job Matching & Ranking Agent (Multi-factor Fit Score & "Why this job?" Breakdown)
   ├── [Score < Threshold] ──> Discard
   └── [Score ≥ 70%] ──> Shortlist & Rank
   ↓
7. Company Research Agent (Domain, Technology Stack, Recent News)
   ↓
8. Resume Tailoring Agent (Truth-Preserving Reorganization + PDF Generation)
   ↓
9. Application Preparation Agent (Cover Letter, Answers, Missing Info Detection)
   ↓
10. Human Review & Approval (HUMAN-IN-THE-LOOP CHECKPOINT: Edit / Reject / Approve)
   ↓
11. Browser / Application Agent (Playwright Form Automation & Confirmation Receipt)
   ↓
12. Application Tracker (Lifecycle Status: Discovered → Submitted → Interview → Offer)
   ↓
13. Follow-up Agent (Reminders, Detected Interview Invitations, Interview Prep Copilot)
   ↓
14. Dashboard & Notifications (Real-time Metrics, Activity Stream, Time Saved)
```

---

## 🛡️ Core Safety & Ethical Principles

- **Zero Qualification Fabrication:** The agent never invents experience, employment, projects, dates, or credentials. It only reorganizes and highlights verified candidate facts.
- **Mandatory Human-in-the-Loop Authorization:** The browser agent will **never** submit without explicit user review and approval.
- **Emergency Kill Switch:** A hardware/UI interrupt allows the user to immediately freeze all active agent operations.
- **Strict Eligibility Filtering:** Ineligible candidates are never applied to jobs they do not qualify for.
- **Deterministic vs. LLM Separation:**
  - *Deterministic Python:* Database transactions, hard constraint filtering, score weights, deduplication, schema validation.
  - *LLMs (Gemini / OpenAI / Fallback):* Reasoning, semantic matching, dynamic query generation, truthful resume rewriting, interview prep.

---

## 📂 Modular Repository Structure

```
opportunity_os/
├── .gitignore                      # Git ignore rules (node_modules, .venv, DB, logs)
├── README.md                       # Complete platform documentation
├── docker-compose.yml              # Container orchestration
├── backend/
│   ├── .env.example                # Environment template
│   ├── Dockerfile                  # Production container definition
│   ├── requirements.txt            # Python dependencies
│   ├── app/
│   │   ├── main.py                 # FastAPI application, static mounts & startup seeder
│   │   ├── core/
│   │   │   ├── config.py           # Typed settings & LLM configuration
│   │   │   ├── security.py         # Guardrails & safety checks
│   │   │   └── logging.py          # Structured activity & audit logging
│   │   ├── db/
│   │   │   ├── session.py          # SQLAlchemy session & database initialization
│   │   │   └── seed.py             # Pre-seeded candidate profile, jobs & interview events
│   │   ├── models/
│   │   │   ├── profile.py          # UserProfile schema & preferences
│   │   │   ├── job.py              # Normalized Job schema
│   │   │   ├── application.py      # Application state, tailored resume, cover letter
│   │   │   └── follow_up.py        # FollowUpEvent & Interview invitation tracking
│   │   ├── schemas/
│   │   │   ├── profile.py          # Profile & Resume upload schemas
│   │   │   ├── job.py              # Job query & metadata schemas
│   │   │   ├── application.py      # Review, approval, & edits schemas
│   │   │   └── agent.py            # Search goal & agent run schemas
│   │   ├── agents/
│   │   │   ├── state.py            # TypedDict JobState
│   │   │   ├── graph.py            # LangGraph multi-agent loop with approval gate
│   │   │   ├── supervisor.py       # Supervisor Agent (search planner)
│   │   │   ├── search_agent.py     # Autonomous iterative search loop
│   │   │   ├── extraction_agent.py # Job info extraction
│   │   │   ├── eligibility_agent.py# Strict eligibility checker
│   │   │   ├── matching_agent.py   # Fit ranker & explanation engine
│   │   │   ├── research_agent.py   # Company intelligence researcher
│   │   │   ├── resume_agent.py     # Truthful resume tailor & PDF generator
│   │   │   ├── application_agent.py# Cover letter & answer preparer
│   │   │   ├── browser_agent.py    # Playwright browser form filler
│   │   │   └── tracker_agent.py    # Status monitor & reminder scheduler
│   │   ├── tools/
│   │   │   ├── llm_adapter.py      # Abstraction layer (Gemini, OpenAI, Fallback)
│   │   │   ├── search_tools.py     # Multi-source job search & query generator
│   │   │   ├── extraction_tools.py # Page reader & specification extractor
│   │   │   ├── matching_tools.py   # Fit score & "Why this job?" engine
│   │   │   ├── research_tools.py   # Company research knowledge base
│   │   │   ├── resume_tools.py     # PDF parser & ReportLab PDF generator
│   │   │   ├── application_tools.py# Cover letter & answer generation
│   │   │   ├── browser_tools.py    # Playwright form automation
│   │   │   └── tracking_tools.py   # Application tracking & follow-up scheduler
│   │   ├── services/
│   │   │   └── mock_portal.py      # Built-in realistic ATS portal for browser automation
│   │   └── api/
│   │       ├── routes.py           # Unified router
│   │       └── endpoints/
│   │           ├── profiles.py     # Candidate profile & resume upload
│   │           ├── jobs.py         # Job listing & discovery
│   │           ├── applications.py # Review packages & approval endpoints
│   │           ├── agent.py        # Autonomous agent runner & kill switch
│   │           └── tracker.py      # Dashboard stats & interview prep copilot
│   └── tests/
│       ├── test_agent_flow.py      # Multi-agent LangGraph workflow test
│       └── test_matching.py        # Fit scoring & eligibility rules test
└── frontend/
    ├── package.json                # React, Vite, Lucide-React, Canvas-Confetti
    ├── vite.config.js              # Vite React & API proxy configuration
    ├── index.html                  # HTML5 entrypoint
    └── src/
        ├── main.jsx                # Full platform dashboard application
        ├── index.css               # Modern glassmorphism dark design system
        ├── services/
        │   └── api.js              # Centralized API service
        └── components/
            ├── Navbar.jsx          # Top bar with status pulse, kill switch, brand
            ├── Sidebar.jsx         # Navigation sidebar
            ├── StatsOverview.jsx   # Metrics cards (Total, Eligible, Saved Time)
            ├── AgentPipeline.jsx   # Interactive visual 14-stage workflow diagram
            ├── AgentActivityLog.jsx# Real-time streaming log with timestamps
            ├── TopOpportunities.jsx# Shortlisted jobs & "Why this job?" tags
            ├── ApplicationReviewModal.jsx # Human-in-the-Loop review & edit card
            ├── ApplicationsTable.jsx # Complete application lifecycle tracker
            ├── ProfileEditor.jsx   # Candidate profile & PDF resume upload parser
            └── InterviewPrepModal.jsx # AI Interview Copilot with company briefing
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server with hot reload
uvicorn app.main:app --reload --port 8000
```
Backend API and mock career portal will be live at `http://localhost:8000`.
Interactive OpenAPI docs are available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🧪 Running Tests
```bash
cd backend
.\.venv\Scripts\pytest -v
```
All test suites verify:
- End-to-end multi-agent LangGraph orchestration
- Deterministic eligibility gating
- Multi-dimensional skill and project match scoring

---

## 🌐 Built-In ATS Career Portal & Playwright Automation
OpportunityOS includes a dedicated local ATS application portal at `/portal/apply/{external_id}`.
When an application is authorized by the candidate:
1. Playwright opens the application URL.
2. Analyzes page inputs (Name, Email, Phone, College, Why Role, Resume File Upload).
3. Types verified candidate data.
4. Uploads the generated tailored PDF resume.
5. Clicks Submit Application.
6. Extracts the confirmation reference code (e.g. `APP-A3B91C2D`) and records screenshot evidence.

---

## 📝 License
MIT License. Built for autonomous agentic job application discovery and tracking.
