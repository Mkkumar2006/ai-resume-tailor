"""
app.py  ─  AI Resume Tailor & ATS Score Optimizer
──────────────────────────────────────────────────
Main Streamlit application entry point.

Run with:
    streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv
from pdf_extractor import extract_text_from_pdf, word_count
from llm_analyzer import analyze_resume

# ── Env & page config ─────────────────────────────────────────────────────────
load_dotenv()  # Load GROQ_API_KEY from .env

st.set_page_config(
    page_title="AI Resume Tailor & ATS Optimizer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS with Modern Glassmorphism & Micro-Interactions ─────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Design Tokens ── */
:root {
    --bg-base:        #090d16;
    --bg-surface:     rgba(17, 24, 39, 0.75);
    --bg-surface-alt: rgba(30, 41, 59, 0.55);
    --border-glass:   rgba(255, 255, 255, 0.09);
    --border-hover:   rgba(99, 102, 241, 0.45);
    --accent-indigo:  #6366f1;
    --accent-purple:  #a855f7;
    --accent-cyan:    #06b6d4;
    --accent-emerald: #10b981;
    --accent-amber:   #f59e0b;
    --accent-rose:    #f43f5e;
    --text-main:      #f8fafc;
    --text-sub:       #94a3b8;
    --text-dim:       #64748b;
    --radius-lg:      18px;
    --radius-md:      12px;
    --shadow-glow:    0 0 35px rgba(99, 102, 241, 0.18);
    --shadow-card:    0 12px 36px -8px rgba(0, 0, 0, 0.6);
}

/* ── Global Styles ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--text-main) !important;
}

/* ── Scrollbars ── */
::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.4); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-indigo); }

/* ── Streamlit Containers ── */
.stApp {
    background: radial-gradient(ellipse at 15% 10%, rgba(99, 102, 241, 0.08) 0%, transparent 45%),
                radial-gradient(ellipse at 85% 90%, rgba(168, 85, 247, 0.08) 0%, transparent 45%),
                var(--bg-base) !important;
}
.block-container {
    padding: 2.2rem 3rem 4rem 3rem !important;
    max-width: 1280px;
}

/* ── Modern Hero Banner ── */
.hero-wrapper {
    position: relative;
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.4) 0%, rgba(15, 23, 42, 0.7) 60%, rgba(30, 41, 59, 0.3) 100%);
    border: 1px solid var(--border-glass);
    border-radius: var(--radius-lg);
    padding: 2.6rem 3rem;
    margin-bottom: 2rem;
    overflow: hidden;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: var(--shadow-glow), var(--shadow-card);
}
.hero-wrapper::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.6), rgba(6, 182, 212, 0.6), transparent);
}
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.6px;
    color: #a5b4fc;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.8px;
    line-height: 1.15;
    background: linear-gradient(135deg, #ffffff 15%, #c7d2fe 65%, #67e8f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.75rem 0;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: var(--text-sub);
    max-width: 820px;
    line-height: 1.6;
    margin: 0;
}

/* ── Modern Glass Cards ── */
.glass-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-glass);
    border-radius: var(--radius-lg);
    padding: 1.8rem;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: var(--shadow-card);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    height: 100%;
    margin-bottom: 1.25rem;
}
.glass-card:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow-glow), var(--shadow-card);
}
.card-header {
    font-size: 0.95rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.75px;
    color: var(--text-sub);
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* ── Step Section Labels ── */
.step-header {
    font-size: 0.95rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #cbd5e1;
    margin-bottom: 0.65rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Donut Gauge Container ── */
.score-center-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1rem 0;
}
.donut-svg {
    filter: drop-shadow(0 0 16px rgba(99, 102, 241, 0.25));
}
.donut-verdict-badge {
    margin-top: 14px;
    padding: 6px 20px;
    border-radius: 999px;
    font-size: 0.88rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* ── Missing Keywords Chips ── */
.tags-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 0.5rem;
}
.tag-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 13px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(244, 63, 94, 0.12);
    border: 1px solid rgba(244, 63, 94, 0.35);
    color: #fecdd3;
    transition: all 0.2s ease;
}
.tag-badge:hover {
    background: rgba(244, 63, 94, 0.25);
    border-color: rgba(244, 63, 94, 0.7);
    transform: translateY(-1px);
}
.tag-badge-green {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #a7f3d0;
}

/* ── Stats Metric Cards ── */
.stat-item {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: var(--radius-md);
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.stat-title {
    font-size: 0.85rem;
    color: var(--text-sub);
    font-weight: 500;
}
.stat-val {
    font-size: 1.25rem;
    font-weight: 800;
    color: #38bdf8;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Summary & Suggestions ── */
.content-box {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: var(--radius-md);
    padding: 1.4rem 1.6rem;
    font-size: 0.96rem;
    line-height: 1.75;
    color: #e2e8f0;
    position: relative;
    border-left: 4px solid var(--accent-indigo);
}
.bullet-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-left: 4px solid var(--accent-emerald);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.9rem;
    font-size: 0.93rem;
    line-height: 1.65;
    color: #f1f5f9;
    transition: all 0.2s ease;
}
.bullet-card:hover {
    border-left-color: var(--accent-cyan);
    transform: translateX(4px);
    background: rgba(15, 23, 42, 0.85);
}

/* ── Action Checklist ── */
.checklist-item {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: var(--radius-md);
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.7rem;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 0.9rem;
    color: #cbd5e1;
}

/* ── Primary CTA Button ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.3px !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.85rem 2rem !important;
    box-shadow: 0 4px 25px rgba(99, 102, 241, 0.4) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.stButton > button:hover {
    opacity: 0.95 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 35px rgba(99, 102, 241, 0.6) !important;
}

/* ── Download Button Styling ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1.8rem !important;
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.35) !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important;
}

/* ── Input Styling ── */
[data-testid="stFileUploader"] {
    background: var(--bg-surface) !important;
    border: 2px dashed rgba(99, 102, 241, 0.35) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.2rem !important;
    transition: border-color 0.2s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent-indigo) !important;
}
textarea, .stTextArea textarea {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-main) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s ease;
}
textarea:focus {
    border-color: var(--accent-indigo) !important;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.25) !important;
}

/* ── Tabs Styling ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: transparent;
    border-bottom: 1px solid var(--border-glass);
    padding-bottom: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px 10px 0 0;
    color: var(--text-sub);
    font-weight: 600;
    padding: 10px 20px;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: rgba(99, 102, 241, 0.2) !important;
    border-color: var(--accent-indigo) !important;
    color: #ffffff !important;
}

/* ── Divider ── */
hr { border-color: rgba(255, 255, 255, 0.08) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Circular Gauge & UI Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def get_score_meta(score: int) -> dict:
    """Return color palette, grade, and verdict text for a given ATS score."""
    if score >= 80:
        return {
            "verdict": "🏆 Top Match Candidate",
            "grade": "EXCELLENT",
            "c1": "#10b981",
            "c2": "#06b6d4",
            "badge_bg": "rgba(16, 185, 129, 0.15)",
            "badge_border": "rgba(16, 185, 129, 0.45)",
            "badge_color": "#6ee7b7",
        }
    elif score >= 60:
        return {
            "verdict": "✅ Strong Compatibility",
            "grade": "GOOD MATCH",
            "c1": "#06b6d4",
            "c2": "#6366f1",
            "badge_bg": "rgba(6, 182, 212, 0.15)",
            "badge_border": "rgba(6, 182, 212, 0.45)",
            "badge_color": "#67e8f9",
        }
    elif score >= 40:
        return {
            "verdict": "⚠️ Moderate Keyword Gap",
            "grade": "NEEDS WORK",
            "c1": "#f59e0b",
            "c2": "#ea580c",
            "badge_bg": "rgba(245, 158, 11, 0.15)",
            "badge_border": "rgba(245, 158, 11, 0.45)",
            "badge_color": "#fcd34d",
        }
    else:
        return {
            "verdict": "❌ Critical Keywords Missing",
            "grade": "LOW MATCH",
            "c1": "#f43f5e",
            "c2": "#e11d48",
            "badge_bg": "rgba(244, 63, 94, 0.2)",
            "badge_border": "rgba(244, 63, 94, 0.5)",
            "badge_color": "#fda4af",
        }


def render_circular_gauge(score: int) -> None:
    """Renders a smooth, glowing SVG donut gauge representing the ATS score."""
    meta = get_score_meta(score)
    # Circumference for r=70 is 2 * pi * 70 = 439.82
    circumference = 439.82
    safe_score = max(0, min(100, score))
    offset = circumference * (1 - (safe_score / 100))

    donut_html = f"""
    <div class="score-center-box">
        <svg width="200" height="200" viewBox="0 0 200 200" class="donut-svg">
            <defs>
                <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{meta['c1']}"/>
                    <stop offset="100%" stop-color="{meta['c2']}"/>
                </linearGradient>
                <filter id="scoreGlow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="5" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
            </defs>
            <!-- Background ring -->
            <circle cx="100" cy="100" r="70" 
                    stroke="rgba(255,255,255,0.06)" 
                    stroke-width="12" 
                    fill="none" />
            <!-- Progress ring -->
            <circle cx="100" cy="100" r="70" 
                    stroke="url(#scoreGrad)" 
                    stroke-width="12" 
                    stroke-dasharray="{circumference}" 
                    stroke-dashoffset="{offset:.2f}" 
                    stroke-linecap="round" 
                    fill="none" 
                    transform="rotate(-90 100 100)" 
                    filter="url(#scoreGlow)" />
            <!-- Center score text -->
            <text x="100" y="96" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" 
                  font-size="46" font-weight="800" fill="#ffffff" letter-spacing="-1px">{safe_score}</text>
            <text x="100" y="122" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" 
                  font-size="12" font-weight="600" fill="#94a3b8" letter-spacing="1.5px">OUT OF 100</text>
        </svg>
        <div class="donut-verdict-badge" style="background:{meta['badge_bg']}; border:1px solid {meta['badge_border']}; color:{meta['badge_color']};">
            {meta['verdict']}
        </div>
    </div>
    """
    st.markdown(donut_html, unsafe_allow_html=True)


def generate_export_report(results: dict, resume_len: int, jd_len: int) -> str:
    """Compile the full analysis into a clean markdown document for download."""
    score = results.get("match_score", 0)
    meta = get_score_meta(score)
    missing = results.get("missing_keywords", [])
    bullets = results.get("bullet_point_suggestions", [])
    summary = results.get("profile_summary", "")

    missing_md = "\n".join([f"- [ ] {kw}" for kw in missing]) if missing else "None — complete keyword coverage!"
    bullets_md = "\n".join([f"- {b}" for b in bullets]) if bullets else "N/A"

    return f"""# 🎯 AI Resume Tailor & ATS Optimization Report

**Date:** Generated via AI Resume Tailor  
**ATS Match Score:** {score} / 100 ({meta['grade']} — {meta['verdict']})  
**Resume Word Count:** {resume_len} words  
**Target Job Description:** {jd_len} words  

---

## 🔍 Missing Keywords & Skill Gaps ({len(missing)} detected)
The following skills/terms were identified in the Job Description but are missing or under-emphasized in your resume:

{missing_md}

---

## ✍️ AI-Tailored Professional Summary
Place this calibrated summary directly beneath your resume header:

> "{summary}"

---

## 🚀 Tailored High-Impact Bullet Points
Incorporate or adapt these achievement-focused bullet points into your Work Experience section:

{bullets_md}

---

## 📋 Recommended Action Plan
1. **Keyword Injection**: Add the missing keywords above into your Skills, Experience, and Certifications sections naturally.
2. **Impact Framing**: Utilize quantified metrics (%, $, time saved) as demonstrated in the bullet point suggestions.
3. **Re-Test**: Re-upload your revised resume to verify your match score rises to 80%+.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# Main App Layout
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # ── Top Hero Banner ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-wrapper">
        <div class="hero-pill">✦ Powered by Groq Ultra-Fast AI Engine</div>
        <h1 class="hero-title">AI Resume Tailor &amp; ATS Optimizer</h1>
        <p class="hero-subtitle">
            Instantly benchmark your resume against any job description. Get real-time ATS scoring,
            uncover missing keyword gaps, and receive tailored bullet points designed to pass automated filters.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Input Columns ─────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="step-header">📄 Step 1 — Upload Resume (PDF)</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            label="Upload your PDF resume",
            type=["pdf"],
            label_visibility="collapsed",
            help="Upload your existing resume in PDF format"
        )
        if uploaded_file:
            st.markdown(f"""
            <div style="background:rgba(99, 102, 241, 0.1); border:1px solid rgba(99, 102, 241, 0.3); border-radius:10px; padding:0.8rem 1.2rem; margin-top:0.75rem; font-size:0.88rem; color:#cbd5e1;">
                📄 <strong>{uploaded_file.name}</strong> &nbsp;·&nbsp; {uploaded_file.size / 1024:.1f} KB &nbsp;·&nbsp; <span style="color:#10b981;">Ready to parse</span>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="step-header">💼 Step 2 — Paste Target Job Description</div>', unsafe_allow_html=True)
        job_description = st.text_area(
            label="Job description text",
            placeholder="Paste the full job description (responsibilities, required qualifications, tech stack)...",
            height=180,
            label_visibility="collapsed",
        )
        if job_description:
            wc = len(job_description.split())
            st.caption(f"📝 {wc} words detected · Tip: Include both required and preferred qualifications.")

    # ── Analyze Action Button ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    btn_col = st.columns([1, 2, 1])[1]
    with btn_col:
        analyze_clicked = st.button("🚀 Run Intelligent ATS Analysis", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Analysis & Results View ───────────────────────────────────────────────
    if analyze_clicked:
        if not uploaded_file:
            st.error("⚠️ Please upload your resume PDF before analyzing.")
            st.stop()
        if not job_description.strip():
            st.error("⚠️ Please paste a job description before analyzing.")
            st.stop()
        if not os.getenv("GROQ_API_KEY"):
            st.error("🔑 GROQ_API_KEY not set. Check your `.env` file and restart the app.")
            st.stop()

        with st.spinner("📖 Extracting resume text..."):
            try:
                uploaded_file.seek(0)
                resume_text = extract_text_from_pdf(uploaded_file)
            except Exception as e:
                st.error(f"Error reading PDF: {e}")
                st.stop()

        with st.spinner("🤖 Groq AI is analyzing keyword overlap, qualification match, and crafting suggestions..."):
            try:
                results = analyze_resume(resume_text, job_description)
            except Exception as e:
                st.error(f"Analysis Error: {e}")
                st.stop()

        resume_wc = word_count(resume_text)
        jd_wc = word_count(job_description)
        missing = results.get("missing_keywords", [])
        score = results.get("match_score", 0)

        # ── Results Header with Export Action ──────────────────────────────────
        top_res_col1, top_res_col2 = st.columns([2, 1])
        with top_res_col1:
            st.markdown("## 📊 Optimization Results")
        with top_res_col2:
            report_markdown = generate_export_report(results, resume_wc, jd_wc)
            st.download_button(
                label="📥 Download Full Report (.md)",
                data=report_markdown,
                file_name="ATS_Resume_Optimization_Report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        # ── Tabbed Interface ──────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 ATS Score & Match Overview",
            "✍️ AI-Tailored Content",
            "📋 Action Checklist",
            "🔩 Raw Data & Insights"
        ])

        with tab1:
            r1, r2, r3 = st.columns([1.1, 1.3, 0.9], gap="large")

            # Column 1: Donut Gauge
            with r1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">🎯 Match Score</div>', unsafe_allow_html=True)
                render_circular_gauge(score)
                st.markdown('</div>', unsafe_allow_html=True)

            # Column 2: Missing Keywords Tags
            with r2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="card-header">🔍 Missing Keywords '
                    f'<span style="color:#f43f5e;font-size:0.85rem;font-weight:700;">'
                    f'({len(missing)} detected)</span></div>',
                    unsafe_allow_html=True,
                )
                if missing:
                    tags_html = "".join([f'<span class="tag-badge">⚠️ {kw}</span>' for kw in missing])
                    st.markdown(f'<div class="tags-wrap">{tags_html}</div>', unsafe_allow_html=True)
                    st.markdown("<br><p style='font-size:0.82rem;color:#94a3b8;'>Incorporate these exact terms in your skills and bullet points to pass automated screening.</p>", unsafe_allow_html=True)
                else:
                    st.markdown('<span class="tag-badge-green">🎉 No critical keywords missing! Excellent alignment.</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Column 3: Quick Stats
            with r3:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">📈 Content Metrics</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="stat-item">
                    <span class="stat-title">Resume Words</span>
                    <span class="stat-val">{resume_wc}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-title">Job Description Words</span>
                    <span class="stat-val">{jd_wc}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-title">Keyword Gaps</span>
                    <span class="stat-val" style="color:{'#f43f5e' if missing else '#10b981'};">{len(missing)}</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown("### ✍️ AI-Calibrated Professional Summary")
            st.caption("Place this targeted summary at the very top of your resume beneath your contact info:")
            st.markdown(f'<div class="content-box">"{results["profile_summary"]}"</div>', unsafe_allow_html=True)
            with st.expander("📋 Copyable Summary Text", expanded=False):
                st.code(results["profile_summary"], language="text")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🚀 High-Impact Experience Bullet Points")
            st.caption("Replace generic bullet points in your experience section with these quantified, targeted achievements:")
            for b in results.get("bullet_point_suggestions", []):
                st.markdown(f'<div class="bullet-card">▸ &nbsp;{b}</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown("### 📋 Step-by-Step Optimization Roadmap")
            st.caption("Follow these prioritized steps to elevate your resume into the 90th percentile for this position:")

            st.markdown(f"""
            <div class="checklist-item">
                <span style="font-size:1.3rem;">1️⃣</span>
                <div>
                    <strong>Inject High-Priority Gaps:</strong> Add the {len(missing)} missing keywords (such as {', '.join(missing[:3]) if missing else 'specialized skills'}) to your technical skills matrix and throughout your recent project descriptions.
                </div>
            </div>
            <div class="checklist-item">
                <span style="font-size:1.3rem;">2️⃣</span>
                <div>
                    <strong>Adopt the Tailored Summary:</strong> Replace your generic objective statement with the role-calibrated summary provided in Tab 2.
                </div>
            </div>
            <div class="checklist-item">
                <span style="font-size:1.3rem;">3️⃣</span>
                <div>
                    <strong>Action &amp; Metric Formulas:</strong> Rewrite passive bullet points using the <em>Google X-Y-Z formula</em> (Accomplished [X] as measured by [Y], by doing [Z]).
                </div>
            </div>
            <div class="checklist-item">
                <span style="font-size:1.3rem;">4️⃣</span>
                <div>
                    <strong>Clean Formatting:</strong> Save your final tailored resume as an ATS-friendly single-column PDF without tables, multi-column layouts, or header/footer text boxes.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab4:
            st.markdown("### 🔩 Raw Structured Response & Inspection")
            st.json(results)

    else:
        # ── Empty state ────────────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; padding: 4rem 2rem; background: rgba(17, 24, 39, 0.4); border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 20px;">
            <div style="font-size:3.5rem; filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.4));">🎯</div>
            <h3 style="font-size:1.3rem; margin-top:1.2rem; color:#f8fafc; font-weight:700;">Ready to Optimize Your Resume</h3>
            <p style="font-size:0.95rem; color:#94a3b8; max-width:540px; margin:0.5rem auto 1.5rem auto; line-height:1.6;">
                Upload your resume PDF on the left, paste the target job description on the right, and click
                <strong>Run Intelligent ATS Analysis</strong> to receive instant scoring and tailor-made suggestions.
            </p>
            <div style="display:flex; justify-content:center; gap:24px; font-size:0.85rem; color:#64748b;">
                <span>🔒 Secure In-Memory Processing</span>
                <span>⚡ Instant Groq Execution</span>
                <span>🎯 Precision Keyword Matching</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Engine Status")
    if os.getenv("GROQ_API_KEY"):
        st.success("✅ Groq LPU Connected")
    else:
        st.error("❌ GROQ_API_KEY Missing")
        st.caption("Add your key to `.env` and restart the application.")

    st.markdown("---")
    st.markdown("### 🎯 ATS Scoring System")
    st.markdown("""
    | Score Range | Status |
    |---|---|
    | **80 – 100** | 🏆 Top Match |
    | **60 – 79**  | ✅ Strong Fit |
    | **40 – 59**  | ⚠️ Gaps Detected |
    | **0 – 39**   | ❌ Low Alignment |
    """)

    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.markdown("""
    - **Exact Phrasing:** If the JD asks for *"Kubernetes"*, don't just say *"Container Orchestration"*.
    - **Standard Headings:** Use *"Work Experience"*, *"Education"*, and *"Skills"*.
    - **PDF Format:** Keep PDF single-column so parsers read top-to-bottom.
    """)

    st.markdown("---")
    st.caption("AI Resume Tailor & ATS Optimizer · Groq LPU High-Speed Edition")


if __name__ == "__main__":
    main()
