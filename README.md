# 🧠 ResumeIQ — AI Resume Analyzer

Analyze your resume against any job description using **Google Gemini 1.5 Flash** (free).

---

## ⚡ Quick Setup (3 steps)

### 1. Get a free Gemini API key
1. Go to → **https://aistudio.google.com**
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API key"**
4. Copy the key (starts with `AIza...`)

### 2. Add your key
Open `app.py` and replace line:
```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```
with:
```python
GEMINI_API_KEY = "AIzaSy...your_actual_key..."
```

### 3. Run the app
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📦 Project Structure
```
resume_iq/
├── app.py                    # Main Streamlit app
├── requirements.txt
└── utils/
    ├── gemini_client.py      # Google Gemini API integration
    ├── pdf_parser.py         # PDF text extraction
    └── ui_components.py      # Streamlit UI components
```

---

## 🎯 Features
- **ATS Score** — How well your resume passes applicant tracking systems
- **JD Match Score** — Alignment with the specific job description
- **Keyword Analysis** — Found, missing, and recommended keywords
- **Skills Gap** — Matched, missing, and bonus skills
- **Learning Roadmap** — Prioritized skills to gain with "how to learn" guides
- **Improvement Suggestions** — Actionable resume fixes ranked by priority
- **JD Analysis** — Role fit, experience match, interview tips

---

## 🆓 Free Tier Limits
- **1,500 requests/day** (Gemini 1.5 Flash)
- **15 requests/minute**
- No credit card required

---

## 🌟 Animations & Design
- Deep space nebula background with animated orbs
- Floating particles + shooting stars
- SVG ring progress indicators on score cards
- Shimmer gradient hero title
- Glowing button with light-sheen effect
- Mobile-responsive layout (works on phones & tablets)
