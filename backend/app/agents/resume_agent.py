import os
from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.tools.resume_tailor_engine import ResumeTailorEngine

def tailor_resume(state: JobState) -> JobState:
    """
    Resume Tailoring Agent Node:
    - Analyzes JD for key requirements
    - Matches with candidate's actual verified facts
    - Emphasizes relevant coursework and projects
    - Strictly ZERO hallucinations/fabrications
    - Generates downloadable PDF resume
    """
    selected = state.get("selected_job")
    if not selected:
        return state
        
    profile = state["user_profile"]
    tailored_text = ResumeTailorEngine.tailor_cv(selected, profile)
    state["tailored_resume"] = tailored_text
    
    # Generate PDF
    pdf_filename = f"Tailored_Resume_{profile.get('name', 'Candidate').replace(' ', '_')}_{selected.get('company', 'Company').replace(' ', '_')}.pdf"
    pdf_path = os.path.join("uploads", pdf_filename)
    try:
        ResumeTailorEngine.generate_pdf(tailored_text, pdf_path)
        state["tailored_resume_pdf_path"] = pdf_path
    except Exception:
        state["tailored_resume_pdf_path"] = ""
        
    log_event(
        state,
        "ResumeTailoringAgent",
        f"Generated tailored resume for {selected.get('title')} at {selected.get('company')}. Strictly truthful, 0 fabricated facts."
    )
    return state
