"""
llm_analyzer.py
───────────────
Handles all communication with the Groq API (blazing fast, free tier).
Sends the resume + JD and parses the structured JSON response.
"""

import json
import re
import os
from groq import Groq

# ── Model configuration ──────────────────────────────────────────────────────
MODEL_ID = "qwen/qwen3.8-27b"   # Confirmed available on Groq free tier

# ── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an elite ATS (Applicant Tracking System) expert and 
professional resume coach with 15+ years of experience at top-tier tech companies.
Your goal is to rigorously compare a candidate's resume against a target job description
and produce highly actionable, data-driven feedback.

Always respond with valid JSON only — no markdown fences, no extra text."""


# ── Core analysis function ────────────────────────────────────────────────────
def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Send resume + JD to Groq and return parsed structured analysis.

    Args:
        resume_text:     Cleaned text extracted from the candidate's PDF resume.
        job_description: The raw job description pasted by the user.

    Returns:
        A dict with keys: match_score, missing_keywords,
        profile_summary, bullet_point_suggestions.

    Raises:
        ValueError: If the API response cannot be parsed as valid JSON.
        RuntimeError: If the Groq API call fails.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not found. "
            "Please set it in your .env file or as an environment variable."
        )

    client = Groq(api_key=api_key)
    user_prompt = _build_user_prompt(resume_text, job_description)

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0,         # Zero temp → fully deterministic, same score every run
            max_tokens=2048,
        )
    except Exception as exc:
        raise RuntimeError(f"Groq API call failed: {exc}") from exc

    raw_text = response.choices[0].message.content.strip()
    return _parse_json_response(raw_text)


# ── Full 1-Click Tailored Resume Generator ─────────────────────────────────────
def generate_tailored_resume(resume_text: str, job_description: str, missing_keywords: list = None) -> str:
    """
    Generate a complete, end-to-end tailored resume by applying recommended changes
    (incorporating missing keywords, role-aligned summary, and quantified bullets)
    while preserving original candidate facts, dates, and education.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found.")

    client = Groq(api_key=api_key)
    missing_str = ", ".join(missing_keywords) if missing_keywords else "None"

    prompt = f"""You are an executive resume writer and ATS specialist.
Rewrite and tailor the candidate's full resume so it achieves top ATS match for the target job description.

═══════════════════════════════════════
ORIGINAL RESUME:
═══════════════════════════════════════
{resume_text}

═══════════════════════════════════════
TARGET JOB DESCRIPTION:
═══════════════════════════════════════
{job_description}

═══════════════════════════════════════
MISSING KEYWORDS TO INTEGRATE:
═══════════════════════════════════════
{missing_str}

═══════════════════════════════════════
INSTRUCTIONS FOR COMPLETE TAILORED RESUME:
═══════════════════════════════════════
1. Retain the candidate's actual name, contact info, companies, degrees, dates, and core career facts. Do NOT invent fake employers or fake degrees.
2. Professional Summary: Write a compelling 3-4 sentence opening targeting this specific role.
3. Skills: Group into clear categories (e.g. Technical Skills, Tools & Frameworks, Core Competencies) and seamlessly incorporate the missing keywords that match the role.
4. Experience: Rewrite existing bullet points into high-impact, quantified achievement statements starting with strong action verbs (Accomplished [X] as measured by [Y], by doing [Z]).
5. Structure: Use standard, clean ATS-friendly markdown sections:
   - CANDIDATE NAME & CONTACT
   - PROFESSIONAL SUMMARY
   - TECHNICAL SKILLS & COMPETENCIES
   - PROFESSIONAL EXPERIENCE
   - EDUCATION & CERTIFICATIONS
6. Output the COMPLETE tailored resume in clean markdown text. Do not truncate. No conversational preamble, just the resume content.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "You are a world-class ATS resume architect. Return the complete polished resume text only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=4096,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        raise RuntimeError(f"Failed to generate tailored resume: {exc}") from exc



# ── Prompt builder ────────────────────────────────────────────────────────────
def _build_user_prompt(resume_text: str, job_description: str) -> str:
    return f"""
Analyze the following resume against the provided job description.

═══════════════════════════════════════
RESUME TEXT:
═══════════════════════════════════════
{resume_text}

═══════════════════════════════════════
TARGET JOB DESCRIPTION:
═══════════════════════════════════════
{job_description}

═══════════════════════════════════════
YOUR TASK:
═══════════════════════════════════════
Return a JSON object with EXACTLY these four keys:

1. "match_score" (integer 0-100):
   - A realistic ATS compatibility score.
   - Consider keyword overlap, required skills, experience level, and formatting.
   - Be honest and strict: a score above 80 means the resume is nearly perfect for this role.

2. "missing_keywords" (array of strings):
   - List every important technical skill, tool, framework, certification, or domain term
     mentioned in the JD that is ABSENT from the resume.
   - Keep each item concise (e.g., "Kubernetes", "CI/CD pipelines", "A/B Testing").
   - Return an empty array [] if nothing is missing.

3. "profile_summary" (string):
   - Write a powerful, tailored 3-4 sentence professional summary FOR THIS SPECIFIC JOB.
   - Use the candidate's actual experience from the resume.
   - Naturally weave in top keywords from the JD.
   - Write in first person ("Results-driven AI engineer with...").

4. "bullet_point_suggestions" (array of 3-5 strings):
   - Rewrite or create high-impact resume bullet points targeting this specific role.
   - Each bullet must start with a strong action verb (e.g., "Engineered", "Optimized").
   - Quantify impact wherever possible (e.g., "reducing inference latency by 40%").
   - Directly mirror language and requirements from the job description.

IMPORTANT: Return raw JSON only. No markdown. No explanation outside the JSON.

Example structure (fill in real values):
{{
  "match_score": 72,
  "missing_keywords": ["Kubernetes", "Terraform", "MLflow"],
  "profile_summary": "Results-driven AI engineer with 3+ years of experience...",
  "bullet_point_suggestions": [
    "Engineered an end-to-end ML pipeline using...",
    "Optimized model inference latency by 35% through..."
  ]
}}
"""


# ── JSON parser ───────────────────────────────────────────────────────────────
def _parse_json_response(raw_text: str) -> dict:
    """
    Robustly parse the LLM's JSON response, even if wrapped in markdown fences.
    """
    # Strip markdown code fences if present (```json ... ```)
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
    cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Failed to parse Groq response as JSON.\n"
            f"Raw response:\n{raw_text}\n\nError: {exc}"
        ) from exc

    # Validate required keys
    required_keys = {
        "match_score", "missing_keywords",
        "profile_summary", "bullet_point_suggestions"
    }
    missing_keys = required_keys - set(data.keys())
    if missing_keys:
        raise ValueError(f"Response JSON is missing keys: {missing_keys}")

    # Coerce types for safety
    data["match_score"] = int(data.get("match_score", 0))
    data["missing_keywords"] = list(data.get("missing_keywords", []))
    data["profile_summary"] = str(data.get("profile_summary", ""))
    data["bullet_point_suggestions"] = list(data.get("bullet_point_suggestions", []))

    return data
