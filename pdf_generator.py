"""
pdf_generator.py
────────────────
Converts markdown/plain text resumes and analysis reports into
clean, professional, ATS-friendly PDF documents using fpdf2.
"""

import re
from fpdf import FPDF


class ATSResumePDF(FPDF):
    """Custom PDF class configured for clean ATS single-column resumes."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(left=18, top=16, right=18)

    def header(self):
        # Clean ATS format - no recurring header graphics
        pass

    def footer(self):
        # Subtle page number at bottom
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def _sanitize_text(text: str) -> str:
    """Replace non-standard unicode characters with standard equivalents."""
    replacements = {
        "–": "-",
        "—": "-",
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "•": "*",
        "▸": "*",
        "…": "...",
        "\u200b": "",
        "\u00a0": " ",
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    return text


def generate_resume_pdf(markdown_text: str) -> bytes:
    """
    Convert a tailored resume markdown string into a styled, professional PDF in-memory.
    Returns: PDF content as bytes.
    """
    pdf = ATSResumePDF()
    pdf.add_page()

    lines = markdown_text.strip().split("\n")
    cleaned_lines = [_sanitize_text(line) for line in lines]

    is_first_header = True

    for line in cleaned_lines:
        line_stripped = line.strip()

        if not line_stripped:
            pdf.ln(3)
            continue

        # Level 1 Heading (e.g. # Name)
        if line_stripped.startswith("# "):
            title_text = line_stripped[2:].strip().replace("**", "").replace("*", "")
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(20, 24, 33)
            if is_first_header:
                pdf.cell(0, 9, title_text, new_x="LMARGIN", new_y="NEXT", align="C")
                is_first_header = False
            else:
                pdf.ln(4)
                pdf.cell(0, 9, title_text, new_x="LMARGIN", new_y="NEXT", align="L")
            pdf.ln(1)
            continue

        # Level 2 Heading (Section Headers e.g. ## PROFESSIONAL EXPERIENCE)
        elif line_stripped.startswith("## "):
            sec_title = line_stripped[3:].strip().replace("**", "").replace("*", "").upper()
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(37, 99, 235)  # Professional blue section header
            pdf.cell(0, 7, sec_title, new_x="LMARGIN", new_y="NEXT", align="L")
            # Subtle divider line under section header
            curr_y = pdf.get_y()
            pdf.set_draw_color(203, 213, 225)
            pdf.set_line_width(0.3)
            pdf.line(18, curr_y, 192, curr_y)
            pdf.ln(2.5)
            continue

        # Level 3 Heading (Job title / Subheading e.g. ### Senior Software Engineer)
        elif line_stripped.startswith("### "):
            sub_title = line_stripped[4:].strip().replace("**", "").replace("*", "")
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(0, 6, sub_title, new_x="LMARGIN", new_y="NEXT", align="L")
            continue

        # Horizontal rule (---)
        elif line_stripped in ("---", "___", "***"):
            pdf.ln(2)
            curr_y = pdf.get_y()
            pdf.set_draw_color(226, 232, 240)
            pdf.line(18, curr_y, 192, curr_y)
            pdf.ln(3)
            continue

        # Bullet point line
        elif line_stripped.startswith(("- ", "* ", "• ", "+ ")):
            bullet_body = line_stripped[2:].strip()
            # Clean markdown bold/italic tags
            bullet_clean = re.sub(r"\*\*(.*?)\*\*", r"\1", bullet_body)
            bullet_clean = re.sub(r"\*(.*?)\*", r"\1", bullet_clean)

            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(51, 65, 85)

            # Bullet dot
            pdf.set_x(18)
            pdf.cell(4, 5.2, "-", align="R")
            # Indented text
            pdf.set_x(23)
            pdf.multi_cell(169, 5.2, bullet_clean)
            pdf.ln(1)
            continue

        # Standard Body / Contact Line / Paragraph
        else:
            clean_body = re.sub(r"\*\*(.*?)\*\*", r"\1", line_stripped)
            clean_body = re.sub(r"\*(.*?)\*", r"\1", clean_body)

            # Check if this looks like a contact info line right after name
            if "@" in clean_body or "|" in clean_body or "linkedin" in clean_body.lower():
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(100, 116, 139)
                pdf.cell(0, 5, clean_body, new_x="LMARGIN", new_y="NEXT", align="C")
                pdf.ln(1)
            else:
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(51, 65, 85)
                pdf.multi_cell(0, 5.2, clean_body)
                pdf.ln(1.5)

    return bytes(pdf.output())


def generate_report_pdf(report_text: str) -> bytes:
    """Convert an ATS optimization report into a clean PDF."""
    return generate_resume_pdf(report_text)
