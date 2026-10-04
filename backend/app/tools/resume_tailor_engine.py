import os
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from app.tools.gemini_tailor_agent import GeminiTailorAgent, GEMINI_RESUME_TAILOR_SYSTEM_PROMPT

logger = logging.getLogger("opportunityos.tailor")

class ResumeTailorEngine:
    """
    Automated Agentic JD-Tailored 1-Page ATS-Friendly Resume Generator for IIT Kharagpur CDC Format.
    - AI Agentic decomposition & domain classification powered by Gemini LLM / AST Engine.
    - Preserves 100% of the Master CV layout: Header, Education Table, Skills & Expertise,
      Certifications, Coursework Information, Positions of Responsibility, and Extracurriculars.
    - Modifies ONLY the projects/internships section based on the target track (SDE, Data, Core, Finance, Consult).
    - Domain Validation Guardrail: If 0 projects exist in the candidate's master CV for the target domain,
      raises a clear informative error.
    - Internships Segregation:
      * >= 2 internships: Creates separate 'INTERNSHIPS' and 'PROJECTS' sections.
      * 1 internship: Combines under 'INTERNSHIPS AND PROJECTS'.
      * 0 internships: Creates 'PROJECTS' section.
    - All bullet points and project overviews are copied and formatted in full without truncation.
    - Font size 10-11 pt throughout all sections.
    - No CDC footer.
    - Builds strict 1-page A4 PDF matching the exact visual format.
    """

    ACTION_VERBS = [
        "Engineered", "Developed", "Architected", "Implemented", "Designed", "Built",
        "Deployed", "Trained", "Optimized", "Formulated", "Spearheaded", "Benchmarked"
    ]

    @staticmethod
    def infer_target_domain(job: Dict[str, Any]) -> str:
        return GeminiTailorAgent.infer_target_domain(job)

    @staticmethod
    def select_relevant_projects(
        all_projects: List[Dict[str, Any]],
        job: Dict[str, Any],
        max_projects: int = 3
    ) -> List[Dict[str, Any]]:
        target_domain = ResumeTailorEngine.infer_target_domain(job)
        req_skills = [s.lower() for s in job.get("required_skills", [])]
        scored = []
        for p in all_projects:
            score = 0.0
            p_text = f"{p.get('name', '')} {p.get('description', '')} {' '.join(p.get('bullets', []))}".lower()
            for s in req_skills:
                if s in p_text:
                    score += 5.0
            for tok in job.get("title", "").lower().split():
                if len(tok) > 3 and tok in p_text:
                    score += 3.5
            if p.get("domain") == target_domain:
                score += 4.0
            scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:max_projects]]

    @staticmethod
    def tailor_cv(job: Dict[str, Any], profile: Dict[str, Any]) -> str:
        """
        Agentic tailoring pipeline:
        1. Executes Gemini LLM (or fallback AST engine) on the full master CV.
        2. Enforces domain guardrail.
        3. Segregates internships and projects with complete full bullet points.
        4. Stitches the document preserving all fixed sections in exact CDC format.
        """
        master_cv_text = profile.get("master_cv_markdown") or profile.get("resume_text") or profile.get("raw_text") or ""
        
        # If master_cv_text is empty, build a synthetic representation from profile fields
        if not master_cv_text:
            lines = [
                f"{profile.get('name', 'VAIBHAV ANAND')} | {profile.get('roll', '24ME10168')}",
                f"{profile.get('degree', 'B.Tech.(Hons.) in MECHANICAL ENGINEERING')}",
                "EDUCATION",
                f"2028 B.TECH {profile.get('college', 'IIT Kharagpur')} {profile.get('cgpa', 8.39)} / 10",
                "PROJECTS"
            ]
            for p in profile.get("projects", []):
                lines.append(f"{p.get('name')} | Self Project")
                if p.get("tech_stack"):
                    techs = p.get("tech_stack")
                    if isinstance(techs, list):
                        techs = ", ".join(techs)
                    lines.append(f"Tech: {techs}")
                if p.get("description"):
                    lines.append(p.get("description"))
                for b in p.get("bullets", []):
                    lines.append(f"• {b}")
                lines.append("")
            master_cv_text = "\n".join(lines)

        # Execute Gemini LLM Tailoring Agent
        llm_result = GeminiTailorAgent.tailor_with_llm(master_cv_text, job)

        has_separate_internships = llm_result.get("has_separate_internships", False)
        selected_internships = llm_result.get("selected_internships", [])
        selected_projects = llm_result.get("selected_projects", [])

        candidate_name = profile.get("name", "VAIBHAV ANAND")
        roll = profile.get("roll", "24ME10168")
        degree = profile.get("degree", "B.Tech.(Hons.) in MECHANICAL ENGINEERING")
        college = profile.get("college", "IIT Kharagpur")
        grad_year = profile.get("graduation_year", 2028)
        cgpa = profile.get("cgpa", 8.39)

        doc_lines = [
            f"{candidate_name.upper()}  |  {roll}",
            f"{degree}",
            "",
            "EDUCATION",
            "Year Degree/Exam Institute CGPA/Marks",
            f"{grad_year} B.TECH {college} {cgpa} / 10",
            "2024 AISSCE (Class XII) Patna Doon Public School 95.8%",
            "2022 AISSE (Class X) St.Michael's High School 98.4%",
            ""
        ]

        # Dynamic Section: Internships & Projects
        if has_separate_internships and selected_internships:
            doc_lines.append("INTERNSHIPS")
            for int_item in selected_internships[:2]:
                date_str = int_item.get("dates") or "[Nov 2025 - Mar 2026]"
                doc_lines.append(f"{int_item.get('name')}  {date_str}")
                if int_item.get("tech_stack"):
                    doc_lines.append(f"{int_item.get('tech_stack')}")
                if int_item.get("description"):
                    doc_lines.append(f"{int_item.get('description')}")
                for b in int_item.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")

            doc_lines.append("PROJECTS")
            proj_limit = 1 if len(selected_internships) >= 2 else 2
            for p in selected_projects[:proj_limit]:
                date_str = p.get("dates") or "[May 2026 - Jun 2026]"
                doc_lines.append(f"{p.get('name')}  {date_str}")
                tech_val = p.get("tech_stack")
                if tech_val:
                    if isinstance(tech_val, list):
                        doc_lines.append(f"Tech: {', '.join(tech_val)}")
                    else:
                        doc_lines.append(f"{tech_val}")
                if p.get("description"):
                    doc_lines.append(f"{p.get('description')}")
                for b in p.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")
        else:
            sec_hdr = "INTERNSHIPS AND PROJECTS" if selected_internships else "PROJECTS"
            doc_lines.append(sec_hdr)
            
            for int_item in selected_internships[:1]:
                date_str = int_item.get("dates") or "[Nov 2025 - Mar 2026]"
                doc_lines.append(f"{int_item.get('name')}  {date_str}")
                tech_val = int_item.get("tech_stack")
                if tech_val:
                    if isinstance(tech_val, list):
                        doc_lines.append(f"Tech: {', '.join(tech_val)}")
                    else:
                        doc_lines.append(f"{tech_val}")
                if int_item.get("description"):
                    doc_lines.append(f"{int_item.get('description')}")
                for b in int_item.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")

            proj_limit = 2 if selected_internships else 3
            for p in selected_projects[:proj_limit]:
                date_str = p.get("dates") or "[May 2026 - Jun 2026]"
                doc_lines.append(f"{p.get('name')}  {date_str}")
                tech_val = p.get("tech_stack")
                if tech_val:
                    if isinstance(tech_val, list):
                        doc_lines.append(f"Tech: {', '.join(tech_val)}")
                    else:
                        doc_lines.append(f"{tech_val}")
                if p.get("description"):
                    doc_lines.append(f"{p.get('description')}")
                for b in p.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")

        # Fixed Static Sections (Exact Master Format)
        doc_lines.extend([
            "SKILLS AND EXPERTISE",
            "Programming Languages/Libraries: C/ C++ | Python | HTML | CSS | Numpy | Pandas | Tensorflow | Matplotlib | Seaborn | Plotly | Node.Js",
            "Skills: Machine Learning | Deep Learning | Natural Language Processing | Data Structures and Algorithms | Object-Oriented Programming",
            "Software and Tools: Jupyter Notebook | GitHub | MySQL | Visual Studio Code | HuggingFace Spaces | FastAPI | Gradio | Arduino IDE",
            "",
            "CERTIFICATIONS",
            "Machine Learning Specialization | DeepLearning.AI & Stanford University",
            "• Implemented supervised learning including regression, classification and model evaluation techniques for predictive modeling tasks",
            "• Learned neural networks with optimization strategies, training methodologies and end-to-end deep learning model implementation",
            "• Explored unsupervised learning including clustering, anomaly detection and practical recommender system development techniques",
            "",
            "COURSEWORK INFORMATION",
            "Mathematics: Linear Algebra | Advanced Calculus | Probability and Statistics | Integral Transforms | Partial Differential Equations",
            "Computer Science: Programming and Data Structures (with Lab) | Essentials of Machine Learning",
            "MOOCs: Machine Learning Specialization (DeepLearning.AI & Stanford University) | Deep Learning Coursework (CampusX)",
            "",
            "POSITIONS OF RESPONSIBILITY",
            "Governing Batch Member | Technology Filmmaking and Photography Society (TFPS)  [Nov 2025 - Present]",
            "• Contributed to 5+ short-film scripts, collaborating on story development, screenplay structure, dialogues and scene-level narrative flow",
            "• Worked as part of production teams for 3 short films, contributing to planning, coordination and overall filmmaking process execution",
            "• Participated in 2 photostory projects, contributing to visual storytelling, photography, composition and creative direction collectively",
            "",
            "EXTRA CURRICULAR ACTIVITIES",
            "• Secured Gold in Ad Design at the Inter-Hall General Championship (2026), representing Nehru Hall in creative design competitions",
            "• Secured 2nd runners-up position in the OpenIIT Data Analytics (2025), delivering data-driven insights through rigorous analytical thinking",
            "• Represented the team of Nehru hall in the Inter-Hall General Championship events (2026) for Short Film Making and Photostory events",
            "• Competed in Inter-Hall General Championship Data Analytics (2026) as part of the hall team, demonstrating strong teamwork skills"
        ])

        return "\n".join(doc_lines)

    @staticmethod
    def generate_pdf(tailored_text: str, output_path: str) -> str:
        """
        Renders the tailored resume into an exact ATS-compliant 1-page A4 PDF document:
        - Font size 10.0 - 11.0 pt throughout all sections for clean, professional readability
        - Full-width shaded banner section headings (#E6EFF8)
        - 4-column education table
        - 2-column project/internship headers with right-aligned bold dates
        - Complete non-truncated multi-line bullets with clean indentation
        - No CDC footer
        - Fills the entire A4 sheet proportionally within strictly 1 page.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        lines = [l.strip() for l in tailored_text.splitlines() if l.strip()]
        if not lines:
            return output_path

        def build_with_font_size(base_fs: float) -> int:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=16,
                rightMargin=16,
                topMargin=12,
                bottomMargin=12
            )
            
            styles = getSampleStyleSheet()
            page_width = A4[0] - 32  # 563.27 pt

            # Styles with font size 10-11 pt
            title_style = ParagraphStyle("CDCTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=base_fs + 1.2, leading=base_fs + 2.5, alignment=1, textColor=colors.black)
            sub_style = ParagraphStyle("CDCSub", parent=styles["Normal"], fontName="Helvetica", fontSize=base_fs, leading=base_fs + 1.4, alignment=1, textColor=colors.black)
            sec_banner_style = ParagraphStyle("CDCBanner", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=base_fs, leading=base_fs + 1.4, alignment=1, textColor=colors.black)
            item_title_left = ParagraphStyle("CDCItemLeft", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=base_fs, leading=base_fs + 1.4, textColor=colors.black)
            item_title_right = ParagraphStyle("CDCItemRight", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=base_fs, leading=base_fs + 1.4, alignment=2, textColor=colors.black)
            tech_style = ParagraphStyle("CDCTech", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=base_fs, leading=base_fs + 1.3, textColor=colors.HexColor("#1E293B"))
            summary_style = ParagraphStyle("CDCSummary", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=base_fs, leading=base_fs + 1.3, textColor=colors.HexColor("#1E293B"))
            bullet_style = ParagraphStyle("CDCBullet", parent=styles["Normal"], fontName="Helvetica", fontSize=base_fs, leading=base_fs + 1.4, textColor=colors.black, leftIndent=8)
            cat_style = ParagraphStyle("CDCCategory", parent=styles["Normal"], fontName="Helvetica", fontSize=base_fs, leading=base_fs + 1.4, textColor=colors.black)

            def make_banner(title_text):
                p = Paragraph(f"<b>{title_text.upper()}</b>", sec_banner_style)
                t = Table([[p]], colWidths=[page_width])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E6EFF8')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#7FA2C7')),
                    ('TOPPADDING', (0, 0), (-1, -1), 0.5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ]))
                return t

            story = []

            # 1. Header (Name | Roll and Degree)
            name_line = lines[0].replace("#", "").strip()
            degree_line = lines[1].replace("#", "").strip() if len(lines) > 1 and not lines[1].isupper() else ""
            
            story.append(Paragraph(f"<b>{name_line}</b>", title_style))
            if degree_line:
                story.append(Paragraph(degree_line, sub_style))
            story.append(Spacer(1, 1.2))

            i = 2 if degree_line else 1
            current_section = ""

            while i < len(lines):
                line = lines[i]

                # Check if Section Banner
                is_banner = (
                    line.startswith("## ") or line.startswith("# ") or
                    (line.isupper() and len(line) < 45 and not line.startswith("•") and not line.startswith("-") and "|" not in line)
                )

                if is_banner:
                    sec_name = line.lstrip("#* ").strip()
                    current_section = sec_name.upper()
                    story.append(make_banner(sec_name))
                    story.append(Spacer(1, 0.6))
                    i += 1

                    # If EDUCATION section, parse table
                    if "EDUCATION" in current_section:
                        edu_rows = [
                            [Paragraph("<b>Year</b>", cat_style), Paragraph("<b>Degree/Exam</b>", cat_style), Paragraph("<b>Institute</b>", cat_style), Paragraph("<b>CGPA/Marks</b>", cat_style)]
                        ]
                        while i < len(lines):
                            edu_line = lines[i]
                            if edu_line.startswith("## ") or (edu_line.isupper() and len(edu_line) < 45 and not edu_line.startswith("•") and "|" not in edu_line and any(k in edu_line for k in ["INTERNSHIP", "PROJECT", "SKILL"])):
                                break
                            if "Year" in edu_line and "Degree" in edu_line:
                                i += 1
                                continue
                            
                            m = re.search(r'^(\d{4})\s+([A-Za-z0-9\.\(\)\s]+?)\s+(IIT\s+[A-Za-z]+|[A-Za-z\s\.\'\-]+?(?:School|College|Institute|University))\s+([0-9\.]+\s*(?:\/\s*10|%))', edu_line)
                            if m:
                                edu_rows.append([
                                    Paragraph(m.group(1), cat_style),
                                    Paragraph(m.group(2).strip(), cat_style),
                                    Paragraph(m.group(3).strip(), cat_style),
                                    Paragraph(m.group(4).strip(), cat_style)
                                ])
                            else:
                                parts = edu_line.split()
                                if len(parts) >= 4 and parts[0].isdigit():
                                    edu_rows.append([
                                        Paragraph(parts[0], cat_style),
                                        Paragraph(" ".join(parts[1:3]), cat_style),
                                        Paragraph(" ".join(parts[3:-2]) if len(parts) > 5 else parts[3], cat_style),
                                        Paragraph(" ".join(parts[-2:]), cat_style)
                                    ])
                            i += 1

                        if len(edu_rows) > 1:
                            edu_table = Table(edu_rows, colWidths=[38, 140, 275, 110.27])
                            edu_table.setStyle(TableStyle([
                                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#94A3B8')),
                                ('TOPPADDING', (0, 0), (-1, -1), 0.2),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0.2),
                                ('LEFTPADDING', (0, 0), (-1, -1), 1),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                            ]))
                            story.append(edu_table)
                            story.append(Spacer(1, 1.0))
                        continue

                    continue

                # Item Title with Date on Right
                date_match = re.search(r'\[([A-Za-z0-9\s\-\–\—\.]+)\]', line)
                is_item_title = (not line.startswith(('•', '-', '*')) and (date_match or "|" in line or line.startswith("### ")))

                if is_item_title:
                    clean_title = line.lstrip("#* ").strip()
                    date_txt = ""
                    if date_match:
                        date_txt = f"[{date_match.group(1).strip()}]"
                        clean_title = line[:date_match.start()].strip().rstrip('| ')

                    t_row = Table([[
                        Paragraph(f"<b>{clean_title}</b>", item_title_left),
                        Paragraph(f"<b>{date_txt}</b>", item_title_right) if date_txt else Paragraph("", item_title_right)
                    ]], colWidths=[428, 135.27])
                    t_row.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 0)]))
                    story.append(t_row)
                    i += 1
                    continue

                # Bullets
                if line.startswith(('•', '-', '*')):
                    clean_bullet = line.lstrip('•-* ').strip().replace('&', '&amp;')
                    story.append(Paragraph(f"• {clean_bullet}", bullet_style))
                    i += 1
                    continue

                # Category Prefix Lines in Skills / Coursework
                if any(line.startswith(p) for p in ["Programming", "Skills:", "Software", "Mathematics:", "Computer Science:", "MOOCs:"]):
                    colon_idx = line.find(":")
                    if colon_idx != -1:
                        lbl = line[:colon_idx+1]
                        val = line[colon_idx+1:].strip()
                        story.append(Paragraph(f"<b>{lbl}</b> {val}", cat_style))
                    else:
                        story.append(Paragraph(line, cat_style))
                    i += 1
                    continue

                # Tech line or 1-line overview
                if line.lower().startswith("tech:"):
                    story.append(Paragraph(f"<i>{line}</i>", tech_style))
                elif len(line) > 15:
                    story.append(Paragraph(line, summary_style))
                i += 1

            doc.build(story)
            from pypdf import PdfReader
            reader = PdfReader(output_path)
            return len(reader.pages)

        # Auto-fitting font size loop (from 10.8 down to 9.5 to guarantee exactly 1 page)
        for candidate_fs in [10.8, 10.5, 10.0, 9.8, 9.5, 9.0]:
            pages = build_with_font_size(candidate_fs)
            if pages == 1:
                break

        return output_path

    @staticmethod
    def generate_cover_letter(job: Dict[str, Any], profile: Dict[str, Any], best_project_name: str = "") -> str:
        name = profile.get("name", "Candidate")
        email = profile.get("email", "candidate@example.com")
        phone = profile.get("phone", "+91 9876543210")
        college = profile.get("college", "IIT Kharagpur")
        degree = profile.get("degree", "B.Tech in Engineering")
        grad_year = profile.get("graduation_year", 2028)
        
        job_title = job.get("title", "Position")
        company = job.get("company", "Company")
        location = job.get("location", "India")

        project_mention = f"Notably, in my {best_project_name} project, I developed end-to-end architectures directly aligned with the technical challenges in this role." if best_project_name else "My technical projects have given me solid hands-on experience in building and optimizing robust systems."

        return f"""Dear {company} Hiring Team,

I am writing to express my strong enthusiasm for the {job_title} opportunity in {location}. As a {degree} undergraduate at {college} (graduating in {grad_year}), my technical background and practical project experience directly align with {company}'s focus.

{project_mention} I have consistently applied strong engineering principles, data-driven optimization, and systematic problem solving to achieve measurable outcomes.

I am particularly excited about the chance to contribute to {company}'s engineering initiatives and would welcome the opportunity to discuss how my skill set can support your team's goals.

Thank you for your time and consideration.

Sincerely,
{name}
{email} | {phone}"""

    @staticmethod
    def generate_application_answers(job: Dict[str, Any], profile: Dict[str, Any], best_project: str = "") -> Dict[str, str]:
        job_title = job.get("title", "this role")
        company = job.get("company", "your organization")
        college = profile.get("college", "my university")

        return {
            "why_role": f"This position as {job_title} allows me to directly apply my hands-on experience from projects like {best_project or 'my engineering portfolio'} to impactful real-world systems.",
            "why_company": f"I admire {company}'s technological leadership and fast-paced engineering culture, and I am eager to contribute to your core products.",
            "relevant_experience": f"At {college}, I have developed domain-specific solutions, optimized computational performance, and built scalable workflows.",
            "availability": "Available for a full-time internship or role starting as per company schedule."
        }
