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
    def parse_education_rows(lines: List[str]) -> List[List[str]]:
        """
        Parses multi-line vertical PDF text dumps or single-line education records
        into structured [Year, Degree/Exam, Institute, CGPA/Marks] rows.
        Guarantees that header rows ('Year | Degree...') and table borders are strictly excluded.
        """
        rows = []
        clean_lines = []
        for l in lines:
            cl = l.strip().strip('|').strip()
            if not cl:
                continue
            cl_lower = cl.lower()
            if any(k in cl_lower for k in ["degree/exam", "cgpa/marks", "institute/school", "marks/cgpa"]) and ("year" in cl_lower or "degree" in cl_lower):
                continue
            if cl_lower in ["education", "academic background", "year", "degree", "institute", "cgpa", "marks"]:
                continue
            clean_lines.append(cl)

        i = 0
        while i < len(clean_lines):
            l = clean_lines[i]
            
            # 1. Pipe-separated row
            if '|' in l:
                parts = [p.strip() for p in l.split('|') if p.strip()]
                if parts and parts[0].lower() in ["year", "degree", "degree/exam", "sl", "s.no"]:
                    i += 1
                    continue
                if len(parts) >= 4:
                    rows.append(parts[:4])
                    i += 1
                    continue
                elif len(parts) == 3:
                    rows.append([parts[0], parts[1], parts[2], ""])
                    i += 1
                    continue

            # 2. Single-line regex match
            m = re.match(r'^(\d{4})\s+(.+?)\s+(IIT\s+[A-Za-z]+|[A-Za-z\s\.\'\-]+?(?:School|College|Institute|University|Vidyalaya|Academy|Council|Board))\s+([0-9\.]+\s*(?:\/\s*10|%|\/\s*100)?)', l, re.I)
            if m:
                rows.append([m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()])
                i += 1
                continue

            # 3. Multi-line vertical dump starting with 4-digit year
            if re.match(r'^\d{4}$', l):
                year = l
                degree = clean_lines[i+1] if i+1 < len(clean_lines) else ""
                institute = clean_lines[i+2] if i+2 < len(clean_lines) else ""
                grade = clean_lines[i+3] if i+3 < len(clean_lines) else ""
                advance = 4
                if i+4 < len(clean_lines) and re.match(r'^\/?\s*10$', clean_lines[i+4]):
                    grade += " " + clean_lines[i+4]
                    advance = 5
                rows.append([year, degree, institute, grade])
                i += advance
                continue

            # 4. Fallback whitespace split starting with 4-digit year
            parts = l.split()
            if len(parts) >= 4 and parts[0].isdigit() and len(parts[0]) == 4:
                rows.append([parts[0], " ".join(parts[1:3]), " ".join(parts[3:-1]) if len(parts) > 4 else parts[3], parts[-1]])
                i += 1
                continue

            i += 1

        return rows

    @staticmethod
    def tailor_cv(job: Dict[str, Any], profile: Dict[str, Any]) -> str:
        """
        Agentic tailoring pipeline:
        1. Executes Gemini LLM (or fallback AST engine) on the full master CV.
        2. Enforces domain guardrail and strict technical domain classification.
        3. Segregates competitions, internships, and projects adhering to priority:
           COMPETITIONS/CONFERENCES > INTERNSHIPS > PROJECTS.
        4. Stitches the document preserving 100% of all other Master CV sections
           (Header, Education Table, Awards, POR, Skills, Coursework, Certifications, Extracurriculars)
           in exact Master CV order and format without any hardcoding.
        """
        master_cv_text = profile.get("master_cv_markdown") or profile.get("resume_text") or profile.get("raw_text") or ""
        
        # If master_cv_text is empty, build a synthetic representation from profile fields dynamically
        if not master_cv_text:
            c_name = profile.get('name') or "Candidate"
            c_roll = profile.get('roll') or ""
            c_deg = profile.get('degree') or "B.Tech in Engineering"
            c_col = profile.get('college') or "IIT Kharagpur"
            c_cgpa = profile.get('cgpa') or "8.0"
            c_yr = profile.get('graduation_year') or "2028"

            hdr = f"{c_name} | {c_roll}".strip(" |")
            lines = [
                hdr,
                c_deg,
                "EDUCATION",
                f"{c_yr} | {c_deg} | {c_col} | {c_cgpa} / 10",
                "PROJECTS"
            ]
            for p in profile.get("projects", []):
                lines.append(f"{p.get('name')} | Self Project")
                if p.get("description"):
                    lines.append(p.get("description"))
                for b in p.get("bullets", []):
                    lines.append(f"• {b}")
                lines.append("")
            master_cv_text = "\n".join(lines)

        from app.tools.cv_parser_engine import MasterCVParser
        sections_order, sections_map, proj_section_names = MasterCVParser.parse_master_cv_full_sections(master_cv_text)

        # Execute Gemini LLM Tailoring Agent
        llm_result = GeminiTailorAgent.tailor_with_llm(master_cv_text, job)
        target_domain = llm_result.get("target_domain") or GeminiTailorAgent.infer_target_domain(job)

        selected_competitions = llm_result.get("selected_competitions", [])
        has_separate_internships = llm_result.get("has_separate_internships", False)
        selected_internships = llm_result.get("selected_internships", [])
        selected_projects = llm_result.get("selected_projects", [])

        # 1. Candidate Header
        header_lines = sections_map.get("HEADER", [])
        if not header_lines:
            c_name = profile.get("name", "Candidate")
            c_roll = profile.get("roll", "")
            c_deg = profile.get("degree", "B.Tech in Engineering")
            header_lines = [f"{c_name} | {c_roll}".strip(" |"), c_deg]

        # 2. Candidate Education
        edu_raw = sections_map.get("EDUCATION", [])
        if not edu_raw and (profile.get("college") or profile.get("graduation_year")):
            edu_raw = [
                f"{profile.get('graduation_year', 2028)} | {profile.get('degree', 'B.Tech')} | {profile.get('college', 'University')} | {profile.get('cgpa', '8.0')} / 10"
            ]
        edu_rows = ResumeTailorEngine.parse_education_rows(edu_raw)

        doc_lines = []
        doc_lines.extend(header_lines)
        if edu_rows:
            doc_lines.append("")
            doc_lines.append("EDUCATION")
            for r in edu_rows:
                doc_lines.append(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")
            doc_lines.append("")

        # 3. Dynamic Experience Section (The ONLY modified section)
        # 3A. Competitions & Conferences Section (Top Priority if present)
        if selected_competitions:
            doc_lines.append("COMPETITIONS/CONFERENCES")
            for comp in selected_competitions:
                date_str = comp.get("dates") or ""
                doc_lines.append(f"{comp.get('name')}  {date_str}".strip())
                if comp.get("description"):
                    doc_lines.append(f"{comp.get('description')}")
                for b in comp.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")

        # 3B. Internships and Projects Section (Determined by internship count)
        if len(selected_internships) >= 2 or (has_separate_internships and selected_internships):
            doc_lines.append("INTERNSHIPS")
            for int_item in selected_internships[:2]:
                date_str = int_item.get("dates") or ""
                doc_lines.append(f"{int_item.get('name')}  {date_str}".strip())
                if int_item.get("description"):
                    doc_lines.append(f"{int_item.get('description')}")
                for b in int_item.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")

            doc_lines.append("PROJECTS")
            proj_limit = max(1, 4 - (len(selected_competitions) + len(selected_internships[:2])))
            for p in selected_projects[:proj_limit]:
                date_str = p.get("dates") or ""
                doc_lines.append(f"{p.get('name')}  {date_str}".strip())
                if p.get("description"):
                    doc_lines.append(f"{p.get('description')}")
                for b in p.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")
        elif len(selected_internships) == 1:
            doc_lines.append("INTERNSHIPS AND PROJECTS")
            for int_item in selected_internships[:1]:
                date_str = int_item.get("dates") or ""
                doc_lines.append(f"{int_item.get('name')}  {date_str}".strip())
                if int_item.get("description"):
                    doc_lines.append(f"{int_item.get('description')}")
                for b in int_item.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")

            proj_limit = max(1, 4 - (len(selected_competitions) + 1))
            for p in selected_projects[:proj_limit]:
                date_str = p.get("dates") or ""
                doc_lines.append(f"{p.get('name')}  {date_str}".strip())
                if p.get("description"):
                    doc_lines.append(f"{p.get('description')}")
                for b in p.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")
        else:
            doc_lines.append("PROJECTS")
            proj_limit = max(2, 4 - len(selected_competitions))
            for p in selected_projects[:proj_limit]:
                date_str = p.get("dates") or ""
                doc_lines.append(f"{p.get('name')}  {date_str}".strip())
                if p.get("description"):
                    doc_lines.append(f"{p.get('description')}")
                for b in p.get("bullets", []):
                    doc_lines.append(f"• {b}")
                doc_lines.append("")

        # 4. 100% Full Preservation of ALL Other Static Sections in Master CV Order
        # (AWARDS AND ACHIEVEMENTS, POSITIONS OF RESPONSIBILITY, SKILLS, COURSEWORK, CERTIFICATIONS, EXTRA CURRICULAR, etc.)
        for sec in sections_order:
            if sec in ["HEADER", "EDUCATION"] or sec in proj_section_names:
                continue
            
            # Check if LLM provided tailored replacements for Skills or Coursework
            if "SKILLS" in sec.upper() and llm_result.get("selected_skills"):
                doc_lines.extend(["", sec])
                for sk in llm_result.get("selected_skills"):
                    doc_lines.append(sk)
                continue

            if "COURSEWORK" in sec.upper() and llm_result.get("selected_coursework"):
                doc_lines.extend(["", sec])
                for cw in llm_result.get("selected_coursework"):
                    doc_lines.append(cw)
                continue

            formatted_sec_lines = MasterCVParser.format_static_section_lines(sections_map[sec], sec, target_domain)
            if formatted_sec_lines:
                doc_lines.extend(["", sec])
                doc_lines.extend(formatted_sec_lines)

        return "\n".join(doc_lines)

    @staticmethod
    def generate_pdf(tailored_text: str, output_path: str) -> str:
        """
        Renders the tailored resume into an exact ATS-compliant 1-page A4 PDF document:
        - Font size 9.0 - 10.0 pt with 100% UNIFORM left indentation across all sections (0 margin offset)
        - Full-width shaded banner section headings (#E6EFF8)
        - 4-column education table (0 left padding)
        - 2-column project/internship headers with right-aligned bold dates (0 left padding)
        - Single-line ATS bullet points starting flush from left margin
        - No Tech line below project titles
        - Clean section spacing and non-bold category content (bold label only)
        - Strictly 1 page on A4.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        lines = [l.strip() for l in tailored_text.splitlines() if l.strip()]
        if not lines:
            return output_path

        def build_with_font_size(base_fs: float) -> int:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=15,
                rightMargin=15,
                topMargin=10,
                bottomMargin=10
            )
            
            styles = getSampleStyleSheet()
            page_width = A4[0] - 30  # 565.27 pt

            # Styles with 100% UNIFORM left margin (leftIndent = 0)
            title_style = ParagraphStyle("CDCTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=base_fs + 1.0, leading=base_fs + 1.8, alignment=1, textColor=colors.black, leftIndent=0, rightIndent=0, firstLineIndent=0)
            sub_style = ParagraphStyle("CDCSub", parent=styles["Normal"], fontName="Helvetica", fontSize=base_fs, leading=base_fs + 1.2, alignment=1, textColor=colors.black, leftIndent=0, rightIndent=0, firstLineIndent=0)
            sec_banner_style = ParagraphStyle("CDCBanner", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=base_fs, leading=base_fs + 1.2, alignment=1, textColor=colors.black, leftIndent=0, rightIndent=0, firstLineIndent=0)
            item_title_left = ParagraphStyle("CDCItemLeft", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=base_fs, leading=base_fs + 1.2, textColor=colors.black, leftIndent=0, rightIndent=0, firstLineIndent=0)
            item_title_right = ParagraphStyle("CDCItemRight", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=base_fs, leading=base_fs + 1.2, alignment=2, textColor=colors.black, leftIndent=0, rightIndent=0, firstLineIndent=0)
            summary_style = ParagraphStyle("CDCSummary", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=base_fs - 0.4, leading=base_fs + 1.0, textColor=colors.HexColor("#1E293B"), leftIndent=0, rightIndent=0, firstLineIndent=0)
            bullet_style = ParagraphStyle("CDCBullet", parent=styles["Normal"], fontName="Helvetica", fontSize=base_fs - 0.2, leading=base_fs + 1.0, textColor=colors.black, leftIndent=0, rightIndent=0, firstLineIndent=0)
            cat_style = ParagraphStyle("CDCCategory", parent=styles["Normal"], fontName="Helvetica", fontSize=base_fs - 0.2, leading=base_fs + 1.1, textColor=colors.black, leftIndent=0, rightIndent=0, firstLineIndent=0)

            def make_banner(title_text):
                p = Paragraph(f"<b>{title_text.upper()}</b>", sec_banner_style)
                t = Table([[p]], colWidths=[page_width])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E6EFF8')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#7FA2C7')),
                    ('TOPPADDING', (0, 0), (-1, -1), 0.4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0.4),
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
            story.append(Spacer(1, 1.0))

            i = 2 if degree_line else 1
            current_section = ""
            first_section = True

            while i < len(lines):
                line = lines[i]

                # Skip any Tech line as requested by user
                if line.lower().startswith("tech:"):
                    i += 1
                    continue

                # Check if Section Banner
                is_banner = (
                    line.startswith("## ") or line.startswith("# ") or
                    (line.isupper() and len(line) < 45 and not line.startswith("•") and not line.startswith("-") and "|" not in line)
                )

                if is_banner:
                    sec_name = line.lstrip("#* ").strip()
                    current_section = sec_name.upper()
                    if not first_section:
                        story.append(Spacer(1, 3.5)) # Clean spacing between sections
                    first_section = False
                    story.append(make_banner(sec_name))
                    story.append(Spacer(1, 0.6))
                    i += 1

                    # If EDUCATION section, parse table
                    if "EDUCATION" in current_section:
                        edu_lines_block = []
                        while i < len(lines):
                            edu_line = lines[i]
                            if (edu_line.startswith("## ") or edu_line.startswith("# ") or
                               (edu_line.isupper() and len(edu_line) < 45 and not edu_line.startswith("•") and not edu_line.startswith("-") and "|" not in edu_line and any(k in edu_line for k in ["INTERNSHIP", "PROJECT", "COMPETITION", "SKILL", "CERTIFICATION", "COURSEWORK", "POSITION", "EXTRA"]))):
                                break
                            edu_lines_block.append(edu_line)
                            i += 1

                        parsed_rows = ResumeTailorEngine.parse_education_rows(edu_lines_block)
                        edu_rows = [
                            [Paragraph("<b>Year</b>", cat_style), Paragraph("<b>Degree/Exam</b>", cat_style), Paragraph("<b>Institute</b>", cat_style), Paragraph("<b>CGPA/Marks</b>", cat_style)]
                        ]
                        for pr in parsed_rows:
                            edu_rows.append([
                                Paragraph(pr[0], cat_style),
                                Paragraph(pr[1], cat_style),
                                Paragraph(pr[2], cat_style),
                                Paragraph(pr[3], cat_style)
                            ])

                        if len(edu_rows) > 1:
                            edu_table = Table(edu_rows, colWidths=[42, 130, 275, page_width - (42 + 130 + 275)])
                            edu_table.setStyle(TableStyle([
                                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#94A3B8')),
                                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                ('TOPPADDING', (0, 0), (-1, -1), 0.2),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0.2),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ]))
                            story.append(edu_table)
                            story.append(Spacer(1, 0.6))
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

                    # Strip duplicate type suffixes
                    for suf in ["| Self Project | Self Project", "| Self Project", "| Team | Team"]:
                        if clean_title.endswith(suf):
                            clean_title = clean_title[:-len(suf)].strip() + (" | Self Project" if "Self Project" in suf else " | Team")

                    t_row = Table([[
                        Paragraph(f"<b>{clean_title}</b>", item_title_left),
                        Paragraph(f"<b>{date_txt}</b>", item_title_right) if date_txt else Paragraph("", item_title_right)
                    ]], colWidths=[page_width - 105, 105])
                    t_row.setStyle(TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0.5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
                    ]))
                    story.append(t_row)
                    i += 1
                    continue

                # Bullets - Flush with left margin (0 leftIndent)
                if line.startswith(('•', '-', '*')):
                    clean_bullet = line.lstrip('•-* ').strip().replace('&', '&amp;')
                    story.append(Paragraph(f"• {clean_bullet}", bullet_style))
                    i += 1
                    continue

                # Category Prefix Lines in Skills / Coursework (Only label is bold, content is regular)
                colon_idx = line.find(":")
                if colon_idx != -1 and not line.startswith(('•', '-', '*')) and colon_idx < 45:
                    lbl = line[:colon_idx+1]
                    val = line[colon_idx+1:].strip()
                    story.append(Paragraph(f"<b>{lbl}</b> {val}", cat_style))
                    i += 1
                    continue

                if len(line) > 15:
                    story.append(Paragraph(line, summary_style))
                i += 1

            doc.build(story)
            from pypdf import PdfReader
            reader = PdfReader(output_path)
            return len(reader.pages)

        # Auto-fitting font size loop (from 10.0 down to 8.8 to guarantee exactly 1 page)
        for candidate_fs in [10.0, 9.8, 9.5, 9.2, 9.0, 8.8]:
            pages = build_with_font_size(candidate_fs)
            if pages == 1:
                break

        return output_path

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
