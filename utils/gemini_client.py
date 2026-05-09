import json
import re
import time
import requests

SYSTEM_MSG = (
    "You are an expert ATS resume analyst. "
    "You ONLY respond with valid JSON — no explanation, no markdown fences."
)

USER_MSG = """Analyze this resume against the job description.
Return ONLY a valid JSON object — no text before or after, no markdown fences.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return EXACTLY this JSON structure with real analyzed values (replace example values with real analysis):
{{
  "ats_score": 72,
  "jd_match_score": 68,
  "keyword_score": 65,
  "overall_score": 70,
  "skills_gap": {{
    "matched_skills": ["Python", "REST APIs"],
    "missing_skills": ["Docker", "Kubernetes"],
    "bonus_skills": ["Tableau", "R"]
  }},
  "keywords": {{
    "found": ["Python", "React", "Node.js"],
    "missing": ["CI/CD", "GraphQL"],
    "recommended": ["FastAPI", "TypeScript", "Redis"]
  }},
  "additional_skills_to_gain": [
    {{
      "skill": "Docker",
      "category": "DevOps",
      "why": "Required for containerizing apps in this role",
      "how_to_learn": "Docker official docs + freeCodeCamp Docker course on YouTube",
      "priority": "HIGH"
    }}
  ],
  "improvements": [
    {{
      "priority": "HIGH",
      "section": "Experience",
      "issue": "No quantified achievements",
      "suggestion": "Add metrics like Reduced load time by 40% or Built API serving 10K requests/day"
    }}
  ],
  "jd_analysis": {{
    "role_fit": "Candidate has solid foundational skills but needs to strengthen DevOps.",
    "experience_match": "Experience level matches mid-level fullstack requirement.",
    "education_match": "B.Tech in CS meets the educational requirement.",
    "top_strengths": ["Strong Python", "React experience", "REST API knowledge"],
    "critical_gaps": ["No Docker/K8s experience", "Missing CI/CD"],
    "interview_tips": [
      "Prepare a project walkthrough showing end-to-end fullstack work",
      "Study system design: load balancing, caching, database indexing"
    ]
  }}
}}"""

# ── Provider configs ────────────────────────────────────────────────────────
# Each provider tried in order. First one that works wins.
PROVIDERS = [
    {
        "name": "Groq (llama-3.3-70b)",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "groq",          # matched against api_key prefix
        "key_prefix": "gsk_",
        "headers_fn": lambda key: {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        "payload_fn": lambda txt, jd: {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user",   "content": USER_MSG.format(
                    resume_text=txt[:3000], job_description=jd[:1500])},
            ],
            "temperature": 0.1,
            "max_tokens": 2500,
        },
        "parse_fn": lambda r: r.json()["choices"][0]["message"]["content"],
    },
    {
        "name": "Groq (mixtral-8x7b)",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key_prefix": "gsk_",
        "headers_fn": lambda key: {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        "payload_fn": lambda txt, jd: {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user",   "content": USER_MSG.format(
                    resume_text=txt[:3000], job_description=jd[:1500])},
            ],
            "temperature": 0.1,
            "max_tokens": 2500,
        },
        "parse_fn": lambda r: r.json()["choices"][0]["message"]["content"],
    },
    {
        "name": "Gemini 2.0 Flash",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "key_prefix": "AIza",
        "headers_fn": lambda key: {"Content-Type": "application/json"},
        "payload_fn": lambda txt, jd: {
            "system_instruction": {"parts": [{"text": SYSTEM_MSG}]},
            "contents": [{"parts": [{"text": USER_MSG.format(
                resume_text=txt[:3000], job_description=jd[:1500])}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2500},
        },
        "parse_fn": lambda r: r.json()["candidates"][0]["content"]["parts"][0]["text"],
        "url_key": True,   # key goes in URL not header
    },
    {
        "name": "Gemini 1.5 Flash",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent",
        "key_prefix": "AIza",
        "headers_fn": lambda key: {"Content-Type": "application/json"},
        "payload_fn": lambda txt, jd: {
            "system_instruction": {"parts": [{"text": SYSTEM_MSG}]},
            "contents": [{"parts": [{"text": USER_MSG.format(
                resume_text=txt[:3000], job_description=jd[:1500])}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2500},
        },
        "parse_fn": lambda r: r.json()["candidates"][0]["content"]["parts"][0]["text"],
        "url_key": True,
    },
]

RETRY_DELAYS = [5, 15, 30, 60, 90]


def _extract_json(raw: str) -> dict | None:
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    start, end = raw.find("{"), raw.rfind("}") + 1
    if start == -1 or end <= 0:
        return None
    try:
        result = json.loads(raw[start:end])
        return result if "ats_score" in result else None
    except json.JSONDecodeError:
        return None


def analyze_resume(resume_text: str, job_description: str, api_key: str,
                   progress_callback=None) -> dict:
    """
    Try Groq first (free, fast, no quota), then fall back to Gemini.
    Auto-retries on rate limits with exponential backoff.
    """
    def notify(msg):
        if progress_callback:
            progress_callback(msg)

    for provider in PROVIDERS:
        # Skip provider if key prefix doesn't match
        prefix = provider.get("key_prefix", "")
        if prefix and not api_key.startswith(prefix):
            continue

        name = provider["name"]
        notify(f"🤖 Connecting to {name}...")

        url = provider["url"]
        if provider.get("url_key"):
            url = f"{url}?key={api_key}"

        for attempt in range(5):
            try:
                resp = requests.post(
                    url,
                    headers=provider["headers_fn"](api_key),
                    json=provider["payload_fn"](resume_text, job_description),
                    timeout=90,
                )

                if resp.status_code == 404:
                    notify(f"⚠️ {name} not available, skipping...")
                    break

                if resp.status_code in (429, 503):
                    wait = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS)-1)]
                    notify(f"⏳ {name} rate limited — auto-retrying in {wait}s "
                           f"(attempt {attempt+1}/5)...")
                    time.sleep(wait)
                    continue

                if resp.status_code == 401:
                    return {"error": (
                        "❌ Invalid API key.\n\n"
                        "For Groq: get free key at console.groq.com\n"
                        "For Gemini: get free key at aistudio.google.com"
                    )}

                if resp.status_code == 400:
                    err = ""
                    try: err = resp.json().get("error", {}).get("message", "")
                    except: pass
                    notify(f"⚠️ {name} bad request ({err}), trying next...")
                    break

                if resp.status_code >= 500:
                    wait = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS)-1)]
                    notify(f"🔄 {name} server error — retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                if resp.status_code == 200:
                    notify(f"✅ Response received from {name}, parsing...")
                    raw = provider["parse_fn"](resp)
                    result = _extract_json(raw)
                    if result:
                        return result
                    notify("⚠️ Unexpected response format, retrying...")
                    time.sleep(3)
                    continue

                notify(f"⚠️ {name} returned {resp.status_code}, trying next...")
                break

            except requests.exceptions.Timeout:
                wait = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS)-1)]
                notify(f"⏱️ Timeout — retrying in {wait}s...")
                time.sleep(wait)
            except requests.exceptions.ConnectionError:
                return {"error": "🌐 No internet connection. Check your network."}

    return {
        "error": (
            "❌ All AI providers are currently unavailable.\n\n"
            "Best fix — switch to Groq (completely free, no daily quota):\n"
            "1. Go to console.groq.com → sign up free\n"
            "2. Click API Keys → Create API Key\n"
            "3. Copy the key (starts with gsk_...)\n"
            "4. In app.py set: GEMINI_API_KEY = 'gsk_your_key_here'\n"
            "5. Restart the app"
        )
    }
