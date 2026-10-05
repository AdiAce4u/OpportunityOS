# OpportunityOS: Autonomous Multi-Agent Job Discovery, Tailoring, and Application Platform

OpportunityOS is an autonomous multi-agent job search and application execution platform engineered to automate the end-to-end recruitment lifecycle. By replacing static pipelines with an agentic workflow, the system discovers opportunities across multiple job portals, evaluates multi-factor candidate eligibility, truthfuly tailors institutional-standard ATS resumes, prepares comprehensive application packages, pauses for mandatory human-in-the-loop review, and executes automated browser submissions via Playwright.

---

## Table of Contents

- [Executive Overview](#executive-overview)
- [System Architecture and Workflow](#system-architecture-and-workflow)
- [Core Engineering Pillars](#core-engineering-pillars)
  - [1. Master CV Intelligence and Domain Parsing](#1-master-cv-intelligence-and-domain-parsing)
  - [2. Dual-Engine ATS Resume Tailoring](#2-dual-engine-ats-resume-tailoring)
  - [3. CDC-Standard 1-Page A4 PDF Generation](#3-cdc-standard-1-page-a4-pdf-generation)
  - [4. Multi-Source Live Job Discovery](#4-multi-source-live-job-discovery)
  - [5. Human-in-the-Loop Governance and Safety](#5-human-in-the-loop-governance-and-safety)
  - [6. Browser Automation and Confirmation Receipts](#6-browser-automation-and-confirmation-receipts)
- [Technical Domain Tracks and Section Governance](#technical-domain-tracks-and-section-governance)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Installation and Setup](#installation-and-setup)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Docker Deployment](#docker-deployment)
- [Configuration and Environment Variables](#configuration-and-environment-variables)
- [API Reference](#api-reference)
- [Testing and Verification](#testing-and-verification)
- [Safety and Ethical Principles](#safety-and-ethical-principles)
- [License](#license)

---

## Executive Overview

Job seekers frequently face repetitive manual application workflows across fragmented hiring platforms, while standard resume tailor tools often hallucinate qualifications or produce poorly formatted documents that fail applicant tracking systems (ATS).

OpportunityOS addresses this challenge through an autonomous multi-agent system:

1. **Autonomous Search Strategy**: Evaluates candidate career goals and executes targeted multi-query job searches across LinkedIn, Indeed, Glassdoor, Google Jobs, Wellfound, and custom job specifications until target quotas are met.
2. **Hard Eligibility Gating**: Enforces deterministic filtering on degrees, graduation timelines, minimum experience requirements, and work authorization prior to evaluation.
3. **Truthful Resume Tailoring**: Employs an AST-driven decomposition engine that extracts verified candidate experiences from a comprehensive Master CV, classifying projects into distinct domain tracks (SDE, Data/AI, Core Engineering, Quantitative Finance, and Consulting) without fabricating credentials.
4. **CDC-Compliant PDF Rendering**: Generates strict 1-page A4 PDF documents formatted to IIT Kharagpur Career Development Centre (CDC) standards, featuring shaded section banners, 4-column academic tables, and single-line bullet points optimized for horizontal printable width.
5. **Human-in-the-Loop Checkpoint**: Requires explicit candidate inspection, editing, and approval of tailored resumes, cover letters, and custom application responses before any external submission occurs.
6. **Automated Submission and Auditing**: Executes headless browser automation via Playwright to navigate portal application forms, attach documents, capture submission confirmation codes, and archive screenshot receipts.

---

## System Architecture and Workflow

```
[Candidate Master CV & Profile Constraints]
                     │
                     ▼
       [Supervisor Planning Agent]
                     │
                     ▼
         [Job Search Agent Loop] <────────────────────────┐
   (LinkedIn, Indeed, Glassdoor, Google, Wellfound)       │ (Quota Not Met)
                     │                                    │
                     ▼                                    │
       [Job Specification Extraction] ────────────────────┘
                     │
                     ▼
       [Eligibility & Gating Agent] ───[Ineligible]──> [Archived with Rationale]
                     │
                 [Eligible]
                     │
                     ▼
       [Job Matching & Ranking Agent]
   (Multi-Factor Match Score & Evidence Breakdown)
                     │
                     ▼
       [Company Intelligence Researcher]
   (Tech Stack, Domain, News, Culture Analysis)
                     │
                     ▼
       [Resume Tailoring Engine]
   (Dual-Engine: Gemini LLM / High-Precision AST Fallback)
                     │
                     ▼
       [Application Preparation Agent]
   (Tailored Cover Letter & Situational Q&A Generation)
                     │
                     ▼
   [MANDATORY HUMAN-IN-THE-LOOP REVIEW GATE]
   (Candidate inspects, edits materials, and approves)
         │                           │
     [Rejected]                  [Approved]
         │                           │
         ▼                           ▼
[Application Discarded]     [Browser Automation Agent]
                            (Playwright Form Filling & Upload)
                                     │
                                     ▼
                            [Confirmation Receipt]
                            (Ref Code & Screenshot Archived)
                                     │
                                     ▼
                            [Application Tracker & Copilot]
                            (Status, Reminders, Interview Prep)
```

---

## Core Engineering Pillars

### 1. Master CV Intelligence and Domain Parsing

Candidates maintain an exhaustive Master CV containing 30 to 50+ projects, internships, publications, and leadership activities. The `MasterCVParser` engine decomposes this unstructured Markdown or PDF text into structured candidate representations:
- **Hierarchical Tokenization**: Identifies sections, sub-entries, date boundaries, and bullet points.
- **Continuation Line Joining**: Unwraps fragmented lines caused by PDF text extractors, preventing mid-sentence breaks.
- **Verbatim Static Preservation**: Preserves Header, Education, Skills and Expertise, Certifications, Coursework, Positions of Responsibility, and Extracurricular Activities exactly as entered by the candidate.

### 2. Dual-Engine ATS Resume Tailoring

The tailoring architecture combines large language model reasoning with a deterministic Abstract Syntax Tree (AST) fallback:
- **Primary LLM Engine**: Utilizes Google Gemini (`gemini-2.5-flash` or `gemini-flash-latest`) to semantically evaluate the target job description against candidate projects, selecting domain-relevant experience items.
- **Circuit Breaker for Quota Limits**: On encountering HTTP 429 rate limits (`ResourceExhausted`), the system breaks immediately out of the retry loop within 100 milliseconds, switching to the local AST engine without causing timeout delays.
- **Deterministic AST Engine**: Scores projects using token overlap, skill co-occurrence, and domain matching weights, returning an optimized experience selection deterministically in under one second.

### 3. CDC-Standard 1-Page A4 PDF Generation

Resumes are rendered using ReportLab to match institutional placement standards (IIT Kharagpur Career Development Centre):
- **Full-Width Shaded Section Banners**: Uses `#E6EFF8` background fills with `#7FA2C7` border strokes.
- **Structured Academic Table**: Clean 4-column layout (`Year | Degree/Exam | Institute | CGPA/Marks`) with zero left margin offsets and clean divider rules.
- **Single-Line High-Density Bullets**: Tailors bullet lengths to horizontal printable limits (95 to 118 characters) to maximize whitespace utilization while preserving quantitative metrics, technical libraries, and outcomes.
- **Dynamic Page-Filling Optimization**: Progressively includes domain-aligned candidate projects until the A4 page is filled to the bottom margin, automatically adjusting font sizes between 8.8 pt and 10.0 pt to guarantee a strict 1-page output.

### 4. Multi-Source Live Job Discovery

The portal search engine aggregates opportunities across career portals:
- **Integrated Portals**: LinkedIn, Indeed, Glassdoor, Google Jobs, and Wellfound (AngelList), supplemented by direct Custom Job Description input.
- **Real-Time Client-Side Filtering**: Interactive filtering by target track (SDE, Data, Core, Finance, Consulting), compensation/stipend floors with robust numeric parsing, source portal, and configurable display limits.
- **Evidence-Based Matching**: Computes weighted match scores across skills (35%), experience (25%), domain relevance (20%), education (10%), and location (10%), providing transparent "Why this job?" rationales.

### 5. Human-in-the-Loop Governance and Safety

Automation without oversight risks submitting mismatched applications. OpportunityOS enforces strict governance:
- **No Automatic Submissions**: Applications pause in an `AWAITING_APPROVAL` state. The candidate must explicitly inspect the tailored PDF resume, cover letter, and application answers.
- **Material Persistence**: Live inline modifications made by candidates in the review modal or profile editor are immediately persisted to the database.
- **Emergency Kill Switch**: A global top-level control halts all background search loops, agent workflows, and browser automation instances immediately.

### 6. Browser Automation and Confirmation Receipts

Once an application is candidate-authorized, the `BrowserAgent` executes automated submission:
- **Form Inspection**: Playwright inspects input elements, dropdowns, and file upload triggers on the target portal.
- **Document Dispatch**: Injects candidate profile information and uploads the tailored PDF resume.
- **Auditable Confirmation**: Extracts confirmation tracking numbers and saves timestamped screenshots to `uploads/screenshots/` for candidate records.

---

## Technical Domain Tracks and Section Governance

### Domain Definitions

Candidate experience items are categorized into technical domains:

| Domain Key | Category | Scope and Technologies |
| :--- | :--- | :--- |
| `sde` | Software Development | Full-Stack Web, Backend, Frontend, Distributed Systems, Microservices, REST APIs, Database Architecture, Compilers, Cloud Infrastructure. |
| `data` | Data Science / AI / ML | Machine Learning, Deep Learning, Generative AI, Large Language Models, NLP, Computer Vision, ETL Pipelines, Time-Series Forecasting. |
| `core` | Core Engineering / Robotics | Robotics, Autonomous Systems, ROS/ROS2, Gazebo, Embedded Systems, Microcontrollers, SolidWorks, ANSYS, FEA, Kinematics, Control Systems. |
| `finance` | Quantitative Finance | Quantitative Trading, Algorithmic Trading, Portfolio Optimization, Risk Modeling, Options Pricing, Financial Analytics. |
| `consult` | Strategy / Management | Management Consulting, Market Entry Strategy, Business Intelligence, Supply Chain Optimization, Product Management Case Studies. |

### Section Priority Order and Internship Count Governance

The tailored resume strictly enforces the following visual priority hierarchy:

$$\text{Priority: } \text{COMPETITIONS/CONFERENCES} > \text{INTERNSHIPS} > \text{PROJECTS}$$

The naming and structure of experience sections are governed by the number of domain-relevant internships:

- **0 Domain Internships** (e.g., SDE role when candidate has no SDE internships):
  - Section Header: `PROJECTS`
  - Content: Domain-aligned software projects.
- **1 Domain Internship** (e.g., Core role with one vocational or research internship):
  - Section Header: `INTERNSHIPS AND PROJECTS`
  - Content: The domain internship followed by domain-aligned projects under the combined banner.
- **2 or More Domain Internships** (e.g., Data role with multiple research internships):
  - Section Headers: `INTERNSHIPS` followed by `PROJECTS`
  - Content: Internships under the primary banner, followed by independent projects under the secondary banner.
- **Competitions and Conferences**:
  - Whenever domain competitions exist (e.g., Rover Challenges, Hackathons), they are placed under `COMPETITIONS/CONFERENCES` at the top of the technical experience section.

### Static Section Verbatim Preservation

All remaining sections outside of dynamic projects are copied from the candidate's Master CV without alteration or omission:
- `HEADER`: Candidate Name, Roll Number, Degree, and Institute.
- `EDUCATION`: Complete academic qualification records.
- `SKILLS AND EXPERTISE`: Categorized technical toolsets and languages.
- `CERTIFICATIONS`: Professional certifications and credential details.
- `COURSEWORK INFORMATION`: Core curricula, mathematics, CS, and verified MOOCs.
- `POSITIONS OF RESPONSIBILITY`: Leadership, society, and governing body roles.
- `EXTRA CURRICULAR ACTIVITIES`: Competitive and cultural achievements.

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.10+) with Pydantic v2 data validation
- **Database & ORM**: SQLAlchemy with SQLite (local development) and PostgreSQL compatibility
- **Document Processing & PDF**: ReportLab (vector graphics, table styling, flowables) and PyPDF
- **Multi-Agent Orchestration**: LangGraph, LangChain Core, and deterministic state machine graphs
- **Browser Automation**: Playwright (headless browser interaction, file uploads, screenshot capture)
- **AI / LLM Integration**: Google Generative AI SDK (`gemini-2.5-flash`), with extensible adapters for OpenAI and local deterministic fallbacks

### Frontend
- **Framework**: React 18 with Vite
- **UI Architecture**: Modular component system with dark-mode aesthetic
- **Icons & Visuals**: Lucide React
- **Network Layer**: Native Fetch API with centralized host resolution

### DevOps and Deployment
- **Containerization**: Docker and Docker Compose (multi-stage container definitions)
- **Cloud Compatibility**: Designed for zero-downtime container hosting (Render, AWS ECS, GCP Cloud Run)

---

## Repository Structure

```
OpportunityOS/
├── Dockerfile                      # Root multi-stage container build definition
├── docker-compose.yml              # Local orchestration for frontend and backend
├── README.md                       # Comprehensive platform documentation
├── backend/
│   ├── Dockerfile                  # Production backend container definition
│   ├── requirements.txt            # Python dependencies
│   ├── tests/
│   │   └── test_master_cv_and_portals.py # Automated test suite
│   └── app/
│       ├── main.py                 # FastAPI application entrypoint
│       ├── agents/
│       │   ├── supervisor.py       # Goal decomposition and search planner
│       │   ├── search_agent.py     # Multi-source iterative discovery loop
│       │   ├── extraction_agent.py # Specification normalizer
│       │   ├── eligibility_agent.py# Hard constraint gating
│       │   ├── matching_agent.py   # Multi-factor candidate scoring
│       │   ├── research_agent.py   # Company profile researcher
│       │   ├── resume_agent.py     # Resume generation coordinator
│       │   ├── application_agent.py# Cover letter and response generator
│       │   ├── browser_agent.py    # Playwright browser form automation
│       │   ├── tracker_agent.py    # Status monitor and reminders
│       │   ├── state.py            # Typed agent state definitions
│       │   └── graph.py            # LangGraph execution graph
│       ├── api/
│       │   ├── routes.py           # Unified router aggregator
│       │   └── endpoints/
│       │       ├── agent.py        # Autonomous execution and kill switch
│       │       ├── applications.py # Tailoring and approval workflows
│       │       ├── jobs.py         # Search, discovery, and custom JD ingestion
│       │       ├── profiles.py     # Master CV upload and profile management
│       │       └── tracker.py      # Lifecycle metrics and interview copilot
│       ├── core/
│       │   ├── config.py           # Typed environment and model configuration
│       │   ├── logging.py          # Structured activity logging
│       │   └── security.py         # Application safety checks
│       ├── db/
│       │   ├── session.py          # SQLAlchemy engine and session factory
│       │   └── seed.py             # Default initial profile and opportunities
│       ├── models/
│       │   ├── application.py      # Application entity and status model
│       │   ├── follow_up.py        # Lifecycle event and interview model
│       │   ├── job.py              # Normalized job entity model
│       │   └── profile.py          # Candidate master profile model
│       ├── schemas/
│       │   ├── agent.py            # Agent execution schemas
│       │   ├── application.py      # Application review and edit schemas
│       │   ├── job.py              # Job query and response schemas
│       │   └── profile.py          # Profile and CV upload schemas
│       ├── services/
│       │   ├── browser.py          # Playwright service wrapper
│       │   └── mock_portal.py      # Built-in career application portal
│       └── tools/
│           ├── cv_parser_engine.py # Master CV section and project parser
│           ├── gemini_tailor_agent.py # LLM tailor agent with 429 fallback
│           ├── llm_adapter.py      # Unified LLM provider abstraction
│           ├── portal_search_engine.py # Multi-source live job search engine
│           ├── resume_tailor_engine.py # ATS PDF layout generator
│           └── tracking_tools.py   # Application tracking utilities
└── frontend/
    ├── package.json                # Frontend dependencies
    ├── vite.config.js              # Vite configuration and proxy setup
    ├── index.html                  # Single-page application entrypoint
    └── src/
        ├── main.jsx                # Application root
        ├── index.css               # Global stylesheets
        ├── services/
        │   └── api.js              # Centralized API client
        └── components/
            ├── AgentActivityLog.jsx# Real-time event log
            ├── AgentPipeline.jsx   # Visual 14-stage workflow pipeline
            ├── ApplicationReviewModal.jsx # Review, edit, and approval modal
            ├── ApplicationsTable.jsx # Application tracking table
            ├── CustomJDModal.jsx   # Manual job description ingestion
            ├── InterviewPrepModal.jsx # AI interview preparation copilot
            ├── MasterCVVault.jsx   # Master CV inspection interface
            ├── Navbar.jsx          # Top navigation with kill switch
            ├── PortalJobDiscovery.jsx # Job search and filtering panel
            ├── ProfileEditor.jsx   # Candidate profile and materials editor
            ├── Sidebar.jsx         # Collapsible fixed navigation sidebar
            ├── StatsOverview.jsx   # Metric overview cards
            └── TopOpportunities.jsx# Ranked opportunities cards
```

---

## Installation and Setup

### Prerequisites

- **Python**: Version 3.10 or higher
- **Node.js**: Version 18.x or higher with npm
- **Google Gemini API Key** (optional, recommended for LLM tailoring; system functions offline with deterministic fallback)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # On macOS / Linux:
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows (PowerShell):
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to supply your `GEMINI_API_KEY` and set application host URLs.

5. Start the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend will be accessible at `http://localhost:8000`. OpenAPI documentation is available at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The user interface will be accessible at `http://localhost:5173`.

### Docker Deployment

To launch the full stack (FastAPI backend and React frontend) inside Docker containers:

```bash
docker-compose up --build
```

The application will be served at `http://localhost:8000` (Backend API) and `http://localhost:5173` (Frontend UI).

---

## Configuration and Environment Variables

### Backend Configuration (`backend/.env`)

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `APP_HOST` | string | `http://localhost:8000` | Base URL of the backend API service. Used for document downloads and callback routes. |
| `FRONTEND_URL` | string | `http://localhost:5173` | Allowed CORS origin for the frontend interface. |
| `DATABASE_URL` | string | `sqlite:///./opportunityos.db` | SQLAlchemy database connection URI. |
| `LLM_PROVIDER` | string | `gemini` | Primary LLM provider (`gemini`, `openai`, or `fallback`). |
| `LLM_MODEL` | string | `gemini-2.5-flash` | LLM model identifier for tailoring and research agents. |
| `GEMINI_API_KEY` | string | `""` | Google Gemini API key. |
| `LLM_API_KEY` | string | `""` | Alternative API key variable for OpenAI or generic LLMs. |
| `TARGET_JOBS_COUNT`| integer| `15` | Target number of opportunities to discover per search run. |
| `MIN_MATCH_SCORE` | float | `70.0` | Minimum match percentage threshold for shortlisting. |
| `PLAYWRIGHT_HEADLESS`| bool | `true` | Runs Playwright automation in headless mode when set to `true`. |

### Frontend Configuration (`frontend/.env`)

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `VITE_API_URL` | string | `http://localhost:8000/api` | API root consumed by the React application. |

---

## API Reference

The FastAPI backend provides RESTful endpoints organized by responsibility:

### Profiles and Master CV
- `GET /api/profiles/` - Retrieve candidate profile, categorized projects, and saved CVs.
- `POST /api/profiles/upload-master-cv` - Upload raw Master CV (Markdown or text) for AST parsing.
- `POST /api/profiles/upload-resume` - Upload candidate PDF resume and extract structured fields.
- `GET /api/profiles/{profile_id}/master-cv-pdf` - Generate and download a PDF representation of the Master CV.
- `POST /api/profiles/tailored-cvs` - Persist modified tailored CV markdown and metadata.

### Job Discovery and Search
- `GET /api/jobs/` - List discovered jobs with eligibility, match score, and company information.
- `POST /api/jobs/search-portals` - Execute live portal search across LinkedIn, Indeed, Glassdoor, Google Jobs, and Wellfound.
- `POST /api/jobs/custom-jd` - Ingest custom job description and compute match breakdown.

### Application Packaging and Tailoring
- `POST /api/applications/tailor-for-job/{job_id}` - Generate a domain-tailored 1-page ATS resume, cover letter, and answers.
- `GET /api/applications/` - List all applications across lifecycle statuses.
- `POST /api/applications/{id}/approve` - Authorize an application package for browser submission.
- `POST /api/applications/{id}/reject` - Discard an opportunity package.
- `POST /api/applications/{id}/submit-browser` - Execute Playwright browser submission for an authorized application.
- `GET /api/applications/{id}/resume-pdf` - Download the generated tailored PDF resume.

### Autonomous Agent and Controls
- `POST /api/agent/run` - Start the autonomous multi-agent search and discovery loop.
- `POST /api/agent/stop` - Trigger emergency kill switch to immediately halt all active agent execution.
- `GET /api/agent/status` - Check current agent lifecycle state and progress metrics.

### Application Tracking and Copilot
- `GET /api/tracker/stats` - Summary metrics (total applied, awaiting approval, interviews scheduled, time saved).
- `GET /api/tracker/events` - Follow-up events, reminders, and detected interview invitations.
- `POST /api/tracker/copilot-briefing` - Generate AI interview preparation briefings with company intelligence.

---

## Testing and Verification

OpportunityOS includes unit and integration tests covering the complete pipeline:

```bash
cd backend
python -m unittest tests/test_master_cv_and_portals.py
```

The test suite validates:
1. **Master CV Deconstruction**: Verifies extraction of projects, internships, competitions, and skills across technical tracks without missing items.
2. **Multi-Source Job Search**: Tests portal query dispatch, match scoring, and evidence generation.
3. **Multi-Track Resume Tailoring**: Verifies section naming rules (0 interns $\rightarrow$ `PROJECTS`; 1 intern $\rightarrow$ `INTERNSHIPS AND PROJECTS`; $\ge 2$ interns $\rightarrow$ `INTERNSHIPS` + `PROJECTS`), priority ordering, and strict 1-page A4 PDF rendering.
4. **Approval Workflow State Transitions**: Validates permission gates, application status tracking, and database integrity.

Frontend production build verification:
```bash
cd frontend
npm run build
```

---

## Safety and Ethical Principles

OpportunityOS adheres to strict operational boundaries:

1. **Zero Fabrication Policy**: The system strictly reorganizes and highlights verified candidate facts. It will never invent employment history, credentials, metrics, or project achievements.
2. **Mandatory Human Authorization**: The browser automation engine will never submit an application without explicit candidate review and approval.
3. **Emergency Stop Capability**: The user can halt all background processes at any time using the global kill switch.
4. **Transparent Decision-Making**: Every job match displays explicit scoring breakdowns ("Why this job?") detailing why an opportunity was recommended or discarded.
5. **Private and Local Data Control**: Candidate profiles and application records remain stored locally or within user-controlled infrastructure.

---

## License

This project is licensed under the MIT License. Detailed terms are available in the LICENSE file.
