"""
app.py  ─  AI Resume Tailor & ATS Optimizer
─────────────────────────────────────────────
Professional ATS resume matcher and tailoring tool.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from pdf_extractor import extract_text_from_pdf, word_count
from llm_analyzer import analyze_resume

# ── Env & configuration ───────────────────────────────────────────────────────
load_dotenv()
try:
    if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

st.set_page_config(
    page_title="Resume Matcher & ATS Advisor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sleek Minimalist Studio Styling (Linear / Raycast aesthetic) ──────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-page:        #0b0e14;
    --bg-card:        #121720;
    --bg-card-subtle: #171e2b;
    --border-subtle:  #1e293b;
    --border-hover:   #334155;
    --text-primary:   #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted:     #64748b;
    --accent-primary: #3b82f6;
    --accent-emerald: #10b981;
    --accent-amber:   #f59e0b;
    --accent-rose:    #ef4444;
    --radius-sm:      6px;
    --radius-md:      10px;
    --radius-lg:      14px;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-page) !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.011em;
}

/* ── Scrollbars ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-page); }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }

/* ── Streamlit layout adjustments ── */
.stApp { background: var(--bg-page) !important; }
.block-container {
    padding: 2.2rem 3rem 4rem 3rem !important;
    max-width: 1240px;
}

/* ── Minimalist Studio Header ── */
.studio-header {
    margin-bottom: 2.2rem;
    padding-bottom: 1.4rem;
    border-bottom: 1px solid var(--border-subtle);
}
.studio-kicker {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent-primary);
    margin-bottom: 0.5rem;
}
.studio-title {
    font-size: 1.95rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #f8fafc;
    margin: 0 0 0.4rem 0;
}
.studio-description {
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.5;
    margin: 0;
    max-width: 720px;
}

/* ── Panels & Cards ── */
.studio-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    transition: border-color 0.15s ease;
}
.studio-card:hover {
    border-color: var(--border-hover);
}
.studio-card-title {
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* ── Minimalist Score Gauge ── */
.score-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0.8rem 0;
}
.score-badge {
    margin-top: 12px;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* ── Keyword Badges ── */
.tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-top: 0.4rem;
}
.tag-missing {
    display: inline-flex;
    align-items: center;
    padding: 4px 11px;
    border-radius: var(--radius-sm);
    font-size: 0.8rem;
    font-weight: 500;
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.28);
    color: #fca5a5;
    font-family: 'JetBrains Mono', monospace;
}
.tag-complete {
    display: inline-flex;
    align-items: center;
    padding: 6px 12px;
    border-radius: var(--radius-sm);
    font-size: 0.82rem;
    font-weight: 500;
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.28);
    color: #6ee7b7;
}

/* ── Clean Metric Row ── */
.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.metric-row:last-child { border-bottom: none; }
.metric-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
}
.metric-val {
    font-size: 0.95rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    color: #f1f5f9;
}

/* ── Content Blocks ── */
.content-preview {
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1.2rem 1.4rem;
    font-size: 0.92rem;
    line-height: 1.7;
    color: #e2e8f0;
}
.bullet-item {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 0.95rem 1.2rem;
    margin-bottom: 0.75rem;
    font-size: 0.89rem;
    line-height: 1.6;
    color: #f1f5f9;
    border-left: 3px solid var(--border-hover);
    transition: border-color 0.15s ease;
}
.bullet-item:hover {
    border-left-color: var(--accent-primary);
}

/* ── Step-by-Step Checklist ── */
.task-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 0.85rem 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    line-height: 1.5;
    color: var(--text-secondary);
}
.task-index {
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(255, 255, 255, 0.06);
    color: var(--text-primary);
    padding: 2px 7px;
    border-radius: var(--radius-sm);
    margin-top: 1px;
}

/* ── Inputs & Button ── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1px dashed var(--border-hover) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.2rem !important;
}
textarea, .stTextArea textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-size: 0.88rem !important;
    line-height: 1.5 !important;
}
textarea:focus {
    border-color: var(--accent-primary) !important;
}

/* ── Buttons (Linear-style clean solid action) ── */
.stButton > button {
    background: #2563eb !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.7rem 1.8rem !important;
    letter-spacing: -0.01em !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease !important;
}
.stButton > button:hover {
    background: #1d4ed8 !important;
}

/* ── Download Button ── */
.stDownloadButton > button {
    background: #1e293b !important;
    color: #f1f5f9 !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    border: 1px solid var(--border-hover) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.55rem 1.2rem !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease !important;
}
.stDownloadButton > button:hover {
    background: #334155 !important;
}

/* ── Tabs (Clean minimal underlines) ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 16px;
    background-color: transparent;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 0.9rem;
    font-weight: 500;
    padding: 10px 4px;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    border-bottom: 2px solid var(--accent-primary) !important;
    color: #f8fafc !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers & Minimalist Gauge
# ═══════════════════════════════════════════════════════════════════════════════

def get_score_meta(score: int) -> dict:
    """Return styling and verdict for a given score."""
    if score >= 80:
        return {
            "verdict": "Strong Match",
            "stroke": "#10b981",
            "badge_bg": "rgba(16, 185, 129, 0.1)",
            "badge_border": "rgba(16, 185, 129, 0.3)",
            "badge_color": "#6ee7b7",
        }
    elif score >= 60:
        return {
            "verdict": "Moderate Match",
            "stroke": "#3b82f6",
            "badge_bg": "rgba(59, 130, 246, 0.1)",
            "badge_border": "rgba(59, 130, 246, 0.3)",
            "badge_color": "#93c5fd",
        }
    elif score >= 40:
        return {
            "verdict": "Needs Revision",
            "stroke": "#f59e0b",
            "badge_bg": "rgba(245, 158, 11, 0.1)",
            "badge_border": "rgba(245, 158, 11, 0.3)",
            "badge_color": "#fcd34d",
        }
    else:
        return {
            "verdict": "Low Alignment",
            "stroke": "#ef4444",
            "badge_bg": "rgba(239, 68, 68, 0.1)",
            "badge_border": "rgba(239, 68, 68, 0.3)",
            "badge_color": "#fca5a5",
        }


def render_minimal_gauge(score: int) -> None:
    """Renders a clean, refined SVG circular meter without aggressive neon glow."""
    meta = get_score_meta(score)
    circumference = 376.99  # 2 * pi * 60
    safe_score = max(0, min(100, score))
    offset = circumference * (1 - (safe_score / 100))

    html = f"""
    <div class="score-container">
        <svg width="150" height="150" viewBox="0 0 150 150">
            <!-- Background track -->
            <circle cx="75" cy="75" r="60" 
                    stroke="rgba(255, 255, 255, 0.07)" 
                    stroke-width="8" 
                    fill="none" />
            <!-- Progress track -->
            <circle cx="75" cy="75" r="60" 
                    stroke="{meta['stroke']}" 
                    stroke-width="8" 
                    stroke-dasharray="{circumference}" 
                    stroke-dashoffset="{offset:.2f}" 
                    stroke-linecap="round" 
                    fill="none" 
                    transform="rotate(-90 75 75)" />
            <!-- Centered value -->
            <text x="75" y="73" text-anchor="middle" font-family="'Inter', sans-serif" 
                  font-size="36" font-weight="700" fill="#f8fafc" letter-spacing="-1px">{safe_score}</text>
            <text x="75" y="94" text-anchor="middle" font-family="'Inter', sans-serif" 
                  font-size="11" font-weight="500" fill="#64748b" letter-spacing="0.5px">OF 100</text>
        </svg>
        <div class="score-badge" style="background:{meta['badge_bg']}; border:1px solid {meta['badge_border']}; color:{meta['badge_color']};">
            {meta['verdict']}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def build_markdown_report(results: dict, resume_len: int, jd_len: int) -> str:
    """Generates clean exportable markdown text."""
    score = results.get("match_score", 0)
    meta = get_score_meta(score)
    missing = results.get("missing_keywords", [])
    bullets = results.get("bullet_point_suggestions", [])
    summary = results.get("profile_summary", "")

    missing_str = "\n".join([f"- [ ] {kw}" for kw in missing]) if missing else "None"
    bullets_str = "\n".join([f"- {b}" for b in bullets]) if bullets else "N/A"

    return f"""# Resume Match & Optimization Report

**ATS Match Score:** {score} / 100 ({meta['verdict']})  
**Resume Length:** {resume_len} words  
**Job Description Length:** {jd_len} words  

---

## Missing Keywords ({len(missing)})
{missing_str}

---

## Recommended Professional Summary
"{summary}"

---

## Suggested Bullet Points
{bullets_str}

---

## Next Steps
1. Add the missing skills into your Work Experience and Skills sections naturally.
2. Replace generic descriptions with the action-oriented bullet points above.
3. Save as a standard single-column PDF before submitting.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# Main App Layout
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="studio-header">
        <div class="studio-kicker">Resume Optimization Studio</div>
        <h1 class="studio-title">Resume Matcher &amp; ATS Advisor</h1>
        <p class="studio-description">
            Compare your resume against a target job description. Identify keyword gaps,
            check ATS compatibility, and review tailored phrasing for your application.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-Column Inputs ─────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div style="font-size:0.88rem; font-weight:600; margin-bottom:0.4rem; color:#cbd5e1;">Resume (PDF)</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            label="Upload your resume PDF",
            type=["pdf"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            st.markdown(f"""
            <div style="font-size:0.83rem; color:#94a3b8; margin-top:0.5rem;">
                Uploaded: <strong>{uploaded_file.name}</strong> ({uploaded_file.size / 1024:.1f} KB)
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="font-size:0.88rem; font-weight:600; margin-bottom:0.4rem; color:#cbd5e1;">Target Job Description</div>', unsafe_allow_html=True)
        job_description = st.text_area(
            label="Job description",
            placeholder="Paste the job description, required qualifications, and responsibilities here...",
            height=160,
            label_visibility="collapsed",
        )
        if job_description:
            st.caption(f"{len(job_description.split())} words")

    # ── Action Button ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    b_col = st.columns([1, 2, 1])[1]
    with b_col:
        analyze_clicked = st.button("Analyze Match", use_container_width=True)

    st.markdown("<hr style='border-color:#1e293b; margin: 2rem 0;'>", unsafe_allow_html=True)

    # ── Results Flow ──────────────────────────────────────────────────────────
    if analyze_clicked:
        if not uploaded_file:
            st.warning("Please upload a resume in PDF format.")
            st.stop()
        if not job_description.strip():
            st.warning("Please paste a job description to compare against.")
            st.stop()
        if not os.getenv("GROQ_API_KEY"):
            st.error("API key not found. Ensure GROQ_API_KEY is configured in your environment or secrets.")
            st.stop()

        with st.spinner("Extracting resume text..."):
            try:
                uploaded_file.seek(0)
                resume_text = extract_text_from_pdf(uploaded_file)
            except Exception as e:
                st.error(f"Error parsing PDF: {e}")
                st.stop()

        with st.spinner("Analyzing keyword coverage and role alignment..."):
            try:
                results = analyze_resume(resume_text, job_description)
            except Exception as e:
                st.error(f"Analysis error: {e}")
                st.stop()

        resume_wc = word_count(resume_text)
        jd_wc = word_count(job_description)
        missing = results.get("missing_keywords", [])
        score = results.get("match_score", 0)

        # ── Results Header with Export ────────────────────────────────────────
        r_head_col1, r_head_col2 = st.columns([3, 1])
        with r_head_col1:
            st.markdown("### Analysis Results")
        with r_head_col2:
            report_md = build_markdown_report(results, resume_wc, jd_wc)
            st.download_button(
                label="Export Report (.md)",
                data=report_md,
                file_name="resume_optimization_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        # ── Tabbed View ───────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs([
            "Overview",
            "Suggested Content",
            "Action Plan",
            "Raw Data"
        ])

        with tab1:
            r1, r2, r3 = st.columns([1.1, 1.4, 0.9], gap="medium")

            # Column 1: Score Gauge
            with r1:
                st.markdown('<div class="studio-card">', unsafe_allow_html=True)
                st.markdown('<div class="studio-card-title">ATS Match Score</div>', unsafe_allow_html=True)
                render_minimal_gauge(score)
                st.markdown('</div>', unsafe_allow_html=True)

            # Column 2: Missing Keywords
            with r2:
                st.markdown('<div class="studio-card">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="studio-card-title">Missing Keywords '
                    f'<span style="color:#f87171;font-weight:500;">({len(missing)} detected)</span></div>',
                    unsafe_allow_html=True,
                )
                if missing:
                    tags_html = "".join([f'<span class="tag-missing">{kw}</span>' for kw in missing])
                    st.markdown(f'<div class="tags-list">{tags_html}</div>', unsafe_allow_html=True)
                    st.markdown("<p style='font-size:0.8rem;color:#64748b;margin-top:0.9rem;'>These terms appear in the job description but were not identified in your resume.</p>", unsafe_allow_html=True)
                else:
                    st.markdown('<span class="tag-complete">All key terms from the job description are present.</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Column 3: Metrics
            with r3:
                st.markdown('<div class="studio-card">', unsafe_allow_html=True)
                st.markdown('<div class="studio-card-title">Document Stats</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="metric-row">
                    <span class="metric-label">Resume Words</span>
                    <span class="metric-val">{resume_wc}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">JD Words</span>
                    <span class="metric-val">{jd_wc}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Gaps Identified</span>
                    <span class="metric-val" style="color:{'#f87171' if missing else '#34d399'};">{len(missing)}</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown("#### Tailored Professional Summary")
            st.markdown(f'<div class="content-preview">"{results["profile_summary"]}"</div>', unsafe_allow_html=True)
            with st.expander("Copy Summary Text", expanded=False):
                st.code(results["profile_summary"], language="text")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Experience Bullet Point Suggestions")
            for b in results.get("bullet_point_suggestions", []):
                st.markdown(f'<div class="bullet-item">• &nbsp;{b}</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown("#### Recommendations")
            st.markdown(f"""
            <div class="task-row">
                <span class="task-index">01</span>
                <div><strong>Incorporate Keyword Gaps:</strong> Work the {len(missing)} missing keywords naturally into your Skills and relevant project bullets.</div>
            </div>
            <div class="task-row">
                <span class="task-index">02</span>
                <div><strong>Align Professional Summary:</strong> Update the top of your resume with the targeted summary from the Suggested Content tab.</div>
            </div>
            <div class="task-row">
                <span class="task-index">03</span>
                <div><strong>Quantify Results:</strong> Emphasize measurable business or engineering impact (metrics, percentages, time saved).</div>
            </div>
            <div class="task-row">
                <span class="task-index">04</span>
                <div><strong>Formatting Check:</strong> Keep formatting clean, avoiding multi-column tables or text boxes that can confuse ATS parsers.</div>
            </div>
            """, unsafe_allow_html=True)

        with tab4:
            st.markdown("#### Structured JSON Response")
            st.json(results)

    else:
        # ── Empty State ────────────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; padding: 4rem 2rem; background: var(--bg-card); border: 1px dashed var(--border-hover); border-radius: 12px;">
            <p style="font-size:1rem; color:#cbd5e1; font-weight:600; margin-bottom:0.4rem;">Upload your resume to begin</p>
            <p style="font-size:0.88rem; color:#64748b; max-width:480px; margin:0 auto; line-height:1.5;">
                Add your resume PDF and target job description above, then click <strong>Analyze Match</strong> to view your compatibility score and suggestions.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### System Status")
    if os.getenv("GROQ_API_KEY"):
        st.success("API Connected")
    else:
        st.error("GROQ_API_KEY not configured")

    st.markdown("---")
    st.markdown("### Scoring Criteria")
    st.markdown("""
    - **80 – 100:** Strong alignment with core qualifications.
    - **60 – 79:** Good fit; minor keyword additions recommended.
    - **40 – 59:** Noticeable skill or domain gaps present.
    - **0 – 39:** Limited overlap with target position.
    """)

    st.markdown("---")
    st.markdown("### Best Practices")
    st.markdown("""
    - Use exact industry terms when applicable.
    - Retain standard resume section titles.
    - Avoid complex multi-column graphic layouts for ATS screening.
    """)

    st.markdown("---")
    st.caption("Resume Matcher & ATS Advisor")


if __name__ == "__main__":
    main()
