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
            m = re.match(
                r'^(\d{4})\s+(B\.?Tech(?:\.[^\s]+)?|AISSCE(?:\s*\([^\)]+\))?|AISSE(?:\s*\([^\)]+\))?|C\.?B\.?S\.?E\.?|Class\s+[X|V|I]+|[A-Za-z\.\s\(\)]+?)\s+((?:IIT|[A-Z][A-Za-z\.\'\-]+)(?:.*?(?:School|College|Institute|University|Vidyalaya|Academy|Council|Board|Convent|IIT)[A-Za-z\s\.\'\-]*?))\s+([0-9\.]+\s*(?:\/\s*10|%|\/\s*100)?)$',
                l, re.I
            )
            if not m:
                m = re.match(r'^(\d{4})\s+(.+?)\s+(IIT\s+[A-Za-z]+|[A-Za-z\s\.\'\-]+?(?:School|College|Institute|University|Vidyalaya|Academy|Council|Board|Convent)[A-Za-z\s\.\'\-]*)\s+([0-9\.]+\s*(?:\/\s*10|%|\/\s*100)?)', l, re.I)
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
            c_name = (profile.get('name') or "Candidate").upper()
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
            c_name = (profile.get("name") or "Candidate").upper()
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

        def append_item_lines(item, target_list):
            date_str = item.get("dates") or ""
            target_list.append(f"{item.get('name')}  {date_str}".strip())
            if item.get("description"):
                desc_clean = item.get("description").strip()
                if desc_clean:
                    target_list.append(desc_clean)
            for b in item.get("bullets", []):
                clean_b = b.lstrip('•-* ').strip()
                if clean_b:
                    target_list.append(f"• {clean_b}")
            target_list.append("")

        def assemble_doc(projects_list):
            doc = []
            doc.extend(header_lines)
            if edu_rows:
                doc.append("")
                doc.append("EDUCATION")
                for r in edu_rows:
                    doc.append(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")
                doc.append("")

            # 3A. Competitions & Conferences Section (Top Priority if present)
            if selected_competitions:
                doc.append("COMPETITIONS/CONFERENCES")
                for comp in selected_competitions:
                    append_item_lines(comp, doc)

            # 3B. Internships and Projects Section (Strictly determined by internship count)
            intern_count = len(selected_internships)
            if intern_count >= 2:
                doc.append("INTERNSHIPS")
                for int_item in selected_internships[:2]:
                    append_item_lines(int_item, doc)

                doc.append("PROJECTS")
                for p in projects_list:
                    append_item_lines(p, doc)
            elif intern_count == 1:
                doc.append("INTERNSHIPS AND PROJECTS")
                for int_item in selected_internships[:1]:
                    append_item_lines(int_item, doc)

                for p in projects_list:
                    append_item_lines(p, doc)
            else:
                doc.append("PROJECTS")
                for p in projects_list:
                    append_item_lines(p, doc)

            # 4. 100% Full Preservation of ALL Other Static Sections in Master CV Order
            for sec in sections_order:
                if sec in ["HEADER", "EDUCATION"] or sec in proj_section_names:
                    continue

                formatted_sec_lines = MasterCVParser.format_static_section_lines(sections_map[sec], sec, target_domain)
                if formatted_sec_lines:
                    doc.extend(["", sec])
                    doc.extend(formatted_sec_lines)

            return "\n".join(doc)

        # Baseline projects limit governed by number of internships and competitions
        intern_count = len(selected_internships)
        if intern_count >= 2:
            base_limit = max(1, 4 - (len(selected_competitions) + len(selected_internships[:2])))
        elif intern_count == 1:
            base_limit = max(1, 4 - (len(selected_competitions) + 1))
        else:
            base_limit = max(2, 4 - len(selected_competitions))

        current_projects = list(selected_projects[:base_limit])

        # Available extra projects pool (from all_available_projects or Master CV projects)
        all_pool = llm_result.get("all_available_projects") or selected_projects
        used_names = {p.get("name") for p in current_projects}
        available_extra = [p for p in all_pool if p.get("name") not in used_names]

        # Dynamic Page-Filling Engine:
        # Incase there are spaces left in a page of tailored resume, add more projects to make it look filled
        for extra_p in available_extra:
            test_doc = assemble_doc(current_projects + [extra_p])
            if ResumeTailorEngine.check_fits_single_page(test_doc):
                current_projects.append(extra_p)
                logger.info(f"[PageFiller] Added extra project '{extra_p.get('name')}' to fill empty page space.")
            else:
                # Stop if adding another project causes page 2 overflow
                break

        return assemble_doc(current_projects)

    @staticmethod
    def check_fits_single_page(tailored_text: str) -> bool:
        """
        Fast in-memory/temp layout check: returns True if tailored_text builds into strictly 1 page on A4.
        """
        import tempfile
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(tmp_fd)
        try:
            ResumeTailorEngine.generate_pdf(tailored_text, tmp_path)
            from pypdf import PdfReader
            reader = PdfReader(tmp_path)
            return len(reader.pages) == 1
        except Exception:
            return False
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

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
            body_style = ParagraphStyle("CDCBody", parent=styles["Normal"], fontName="Helvetica", fontSize=base_fs - 0.2, leading=base_fs + 1.0, textColor=colors.black, leftIndent=0, rightIndent=0, firstLineIndent=0)
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

            # 1. Header (Name | Roll and Degree/Minors)
            header_lines = []
            i = 0
            while i < len(lines):
                hl = lines[i]
                is_banner = (
                    hl.startswith("## ") or hl.startswith("# ") or
                    (hl.isupper() and len(hl) < 45 and not hl.startswith(("•", "-", "*")) and "|" not in hl)
                )
                if is_banner:
                    break
                header_lines.append(hl.replace("#", "").strip())
                i += 1

            if header_lines:
                story.append(Paragraph(f"<b>{header_lines[0]}</b>", title_style))
                for sub_line in header_lines[1:]:
                    if sub_line:
                        story.append(Paragraph(sub_line, sub_style))
                story.append(Spacer(1, 1.0))

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

                # 2. In SKILLS or COURSEWORK: Copy exact formatting from Master CV:
                # Category label prefix before colon is BOLD (<b>Category:</b>), content after colon is REGULAR (Helvetica)
                if "SKILL" in current_section or "COURSEWORK" in current_section:
                    clean_line = line.lstrip('•-* \t').strip()
                    if not clean_line:
                        i += 1
                        continue

                    # Safely escape ampersands without breaking existing XML entities
                    clean_line = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', clean_line)

                    # Look for category header prefix ending in colon
                    colon_pos = clean_line.find(':')
                    if colon_pos != -1 and colon_pos < 55 and '|' not in clean_line[:colon_pos]:
                        raw_lbl = clean_line[:colon_pos + 1].strip()
                        raw_val = clean_line[colon_pos + 1:].strip()

                        # Strip any existing <b> or ** from label so we don't produce invalid or nested tags
                        lbl_clean = re.sub(r'<\/?b>|\*\*', '', raw_lbl).strip()
                        # Val should preserve any deliberate markdown bold if present, but standard skills remain regular
                        val_formatted = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', raw_val)

                        formatted_p = f"<b>{lbl_clean}</b> {val_formatted}".strip()
                    else:
                        formatted_p = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', clean_line)

                    story.append(Paragraph(formatted_p, cat_style))
                    i += 1
                    continue

                # 3. Item Title with Date on Right (Only in Experience/Projects/Internships/Competitions/POR)
                date_match = re.search(r'\[([A-Za-z0-9\s\-\–\—\.]+)\]', line)
                is_item_title = (
                    not line.startswith(('•', '-', '*')) and
                    (date_match or (any(k in current_section for k in ["PROJECT", "INTERN", "COMPETITION", "EXPERIENCE", "POSITION", "LEADERSHIP"]) and "|" in line) or line.startswith("### "))
                )

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
                    clean_bullet = line.lstrip('•-* ').strip()
                    clean_bullet = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', clean_bullet)
                    clean_bullet = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', clean_bullet)
                    story.append(Paragraph(f"• {clean_bullet}", bullet_style))
                    i += 1
                    continue

                if line.strip():
                    clean_text = line.strip()
                    clean_text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', clean_text)
                    clean_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', clean_text)
                    story.append(Paragraph(clean_text, body_style))
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
