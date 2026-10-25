# 🎯 AI Resume Tailor & ATS Score Optimizer

An intelligent, full-stack ATS (Applicant Tracking System) optimizer and resume tailoring web application powered by **Streamlit** and **Groq (Qwen 2.5 / Llama 3 on LPU)**.

---

## ✨ Features

- **📄 PDF Resume Parsing**: Fast in-memory text extraction from PDF resumes using `pypdf`.
- **⚡ Ultra-Fast LLM Processing**: Powered by Groq's high-speed inference engine with zero-temperature deterministic scoring.
- **🎯 Dynamic Circular ATS Gauge**: Interactive SVG donut chart with real-time color gradation (Emerald for 80+, Cyan for 60+, Amber for 40+, Rose for <40).
- **🔍 Gap Analysis & Missing Keywords**: Automatically detects key technologies, frameworks, and qualifications mentioned in the Job Description but absent from the resume.
- **✍️ Role-Tailored Summary & Bullet Points**: AI-generated professional summary and quantifiable, action-oriented bullet points (following the Google X-Y-Z formula) ready to paste.
- **📋 Step-by-Step Optimization Roadmap**: Actionable checklist to iteratively raise your match score.
- **📥 1-Click Export**: Download the full analysis report as a clean Markdown (`.md`) file.
- **🎨 Glassmorphic Dark UI**: Premium typography (`Plus Jakarta Sans`), glass cards, smooth glowing accents, and responsive layout.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit**: Web interface and reactive UI
- **Groq Python SDK**: High-speed LLM inference
- **pypdf**: PDF text extraction
- **python-dotenv**: Environment configuration

---

## 🚀 Getting Started

### 1. Clone or Open the Project Directory
```bash
cd "d:/Games/my proj"
```

### 2. Activate Virtual Environment
```bash
# Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key
Create or verify your `.env` file with your Groq API key:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```
*(Get a free API key at [console.groq.com](https://console.groq.com/keys))*

### 5. Launch the Application
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your browser.

---

## 🔒 Privacy & Security

- PDF resumes are processed strictly in-memory and are never stored to disk.
- `.env` and personal keys are strictly ignored by `.gitignore`.
