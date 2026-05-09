import streamlit.components.v1 as components
import json


def render_image_report(result: dict, candidate_name: str = "Candidate"):
    """
    Renders the full analysis as a beautiful visual card (HTML) with a
    'Download as Image' button using html2canvas.
    """

    ats      = result.get("ats_score", 0)
    jd       = result.get("jd_match_score", 0)
    kw       = result.get("keyword_score", 0)
    overall  = result.get("overall_score", 0)

    sg       = result.get("skills_gap", {})
    matched  = sg.get("matched_skills", [])
    missing  = sg.get("missing_skills", [])
    bonus    = sg.get("bonus_skills", [])

    kws      = result.get("keywords", {})
    kw_found = kws.get("found", [])
    kw_miss  = kws.get("missing", [])
    kw_rec   = kws.get("recommended", [])

    jda      = result.get("jd_analysis", {})
    role_fit = jda.get("role_fit", "")
    strengths= jda.get("top_strengths", [])
    gaps     = jda.get("critical_gaps", [])
    tips     = jda.get("interview_tips", [])

    skills   = result.get("additional_skills_to_gain", [])[:5]
    improves = result.get("improvements", [])[:5]

    def grade(s):
        if s >= 75: return ("Excellent", "#22d3a0")
        if s >= 55: return ("Good",      "#60a5fa")
        if s >= 35: return ("Fair",      "#fbbf24")
        return ("Needs Work", "#f87171")

    def pills(items, color, bg):
        if not items:
            return "<span style='color:#3d3354;font-size:11px;'>None</span>"
        return "".join(
            f"<span style='background:{bg};color:{color};border:1px solid {color}55;"
            f"border-radius:20px;padding:3px 11px;font-size:11px;margin:2px;"
            f"display:inline-block;font-weight:500;'>{i}</span>"
            for i in items[:10]
        )

    def score_arc(val, color):
        # SVG arc for score
        r = 42
        circ = 2 * 3.14159 * r
        dash = (val / 100) * circ
        return f"""
        <svg width="110" height="110" viewBox="0 0 110 110">
          <circle cx="55" cy="55" r="{r}" fill="none"
            stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
          <circle cx="55" cy="55" r="{r}" fill="none"
            stroke="{color}" stroke-width="8"
            stroke-dasharray="{dash:.1f} {circ:.1f}"
            stroke-dashoffset="{circ/4:.1f}"
            stroke-linecap="round"
            style="filter:drop-shadow(0 0 6px {color})"/>
          <text x="55" y="52" text-anchor="middle"
            fill="{color}" font-size="22" font-weight="900"
            font-family="'Orbitron',monospace"
            style="filter:drop-shadow(0 0 4px {color})">{val}</text>
          <text x="55" y="68" text-anchor="middle"
            fill="{color}99" font-size="9"
            font-family="'Orbitron',monospace">/ 100</text>
        </svg>"""

    p_cfg = {"HIGH":("#f87171","rgba(248,113,113,0.12)"),
             "MEDIUM":("#fbbf24","rgba(251,191,36,0.12)"),
             "LOW":("#34d399","rgba(52,211,153,0.12)")}

    skills_html = ""
    for s in skills:
        pri = s.get("priority","MEDIUM").upper()
        c, bg = p_cfg.get(pri, p_cfg["MEDIUM"])
        skills_html += f"""
        <div style='background:{bg};border-left:3px solid {c};border-radius:8px;
             padding:8px 12px;margin-bottom:7px;'>
          <div style='display:flex;justify-content:space-between;align-items:center;'>
            <span style='color:#e2dff5;font-weight:700;font-size:12px;
                font-family:Orbitron,monospace;'>{s.get('skill','')}</span>
            <span style='color:{c};font-size:9px;font-family:Orbitron,monospace;
                background:{c}22;padding:2px 8px;border-radius:10px;
                border:1px solid {c}55;'>{pri}</span>
          </div>
          <div style='color:#9c9aaa;font-size:11px;margin-top:4px;line-height:1.4;'>
            <b style='color:#c084fc;'>Why:</b> {s.get('why','')}
          </div>
          <div style='color:#c8c5d8;font-size:10px;margin-top:3px;line-height:1.4;
               background:rgba(0,0,0,0.2);border-radius:5px;padding:4px 7px;'>
            <b style='color:#00d2ff;'>📚</b> {s.get('how_to_learn','')}
          </div>
        </div>"""

    improve_html = ""
    for imp in improves:
        pri = imp.get("priority","LOW").upper()
        c, bg = p_cfg.get(pri, p_cfg["LOW"])
        improve_html += f"""
        <div style='background:{bg};border-left:3px solid {c};border-radius:8px;
             padding:8px 12px;margin-bottom:7px;'>
          <div style='color:{c};font-size:9px;font-family:Orbitron,monospace;
               margin-bottom:3px;'>● {pri} · {imp.get('section','')}</div>
          <div style='color:#9c9aaa;font-size:11px;'>
            <b style='color:#e2dff5;'>Issue:</b> {imp.get('issue','')}
          </div>
          <div style='color:#c8c5d8;font-size:11px;margin-top:3px;'>
            <b style='color:#34d399;'>Fix:</b> {imp.get('suggestion','')}
          </div>
        </div>"""

    strengths_html = "".join(
        f"<div style='color:#c8c5d8;font-size:11px;padding:3px 0;'>✅ {s}</div>"
        for s in strengths[:5])
    gaps_html = "".join(
        f"<div style='color:#c8c5d8;font-size:11px;padding:3px 0;'>❌ {g}</div>"
        for g in gaps[:5])
    tips_html = "".join(
        f"<div style='color:#c8c5d8;font-size:11px;padding:4px 0;line-height:1.4;'>"
        f"<b style='color:#fbbf24;'>{i+1}.</b> {t}</div>"
        for i, t in enumerate(tips[:4]))

    ag, ac = grade(ats)
    jg, jc = grade(jd)
    kg, kc = grade(kw)
    og, oc = grade(overall)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Syne:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#030008; font-family:'Syne',sans-serif; }}

#report {{
  width: 900px;
  background: linear-gradient(160deg, #0a0018 0%, #050010 40%, #000812 100%);
  padding: 36px 36px 40px;
  position: relative;
  overflow: hidden;
}}
#report::before {{
  content:'';
  position:absolute; top:-30%; left:-20%;
  width:80%; height:80%;
  background: radial-gradient(ellipse, rgba(120,40,220,0.18) 0%, transparent 65%);
  border-radius:50%; pointer-events:none;
}}
#report::after {{
  content:'';
  position:absolute; bottom:-25%; right:-15%;
  width:65%; height:65%;
  background: radial-gradient(ellipse, rgba(0,180,255,0.12) 0%, transparent 65%);
  border-radius:50%; pointer-events:none;
}}

.grid-overlay {{
  position:absolute; inset:0; pointer-events:none;
  background-image:
    linear-gradient(rgba(120,40,220,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(120,40,220,0.04) 1px, transparent 1px);
  background-size: 50px 50px;
}}

/* ── Header ── */
.header {{
  display:flex; align-items:center; justify-content:space-between;
  margin-bottom:28px; position:relative; z-index:2;
  border-bottom:1px solid rgba(120,40,220,0.2); padding-bottom:20px;
}}
.brand {{
  font-family:'Orbitron',monospace; font-weight:900;
  font-size:22px; letter-spacing:0.04em;
  background:linear-gradient(135deg,#fff 0%,#c084fc 40%,#00d2ff 80%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-clip:text;
}}
.brand-sub {{
  color:#4a3d6b; font-size:10px; font-family:'Orbitron',monospace;
  letter-spacing:0.18em; margin-top:3px;
}}
.candidate-badge {{
  text-align:right;
}}
.candidate-name {{
  color:#e2dff5; font-size:16px; font-weight:700;
}}
.candidate-date {{
  color:#3d3354; font-size:10px; margin-top:2px;
  font-family:'Orbitron',monospace; letter-spacing:0.1em;
}}

/* ── Score row ── */
.scores-row {{
  display:grid; grid-template-columns:repeat(4,1fr); gap:14px;
  margin-bottom:24px; position:relative; z-index:2;
}}
.score-box {{
  background:rgba(12,5,28,0.85);
  border:1px solid rgba(120,40,220,0.22);
  border-radius:16px; padding:16px 12px;
  text-align:center;
  box-shadow:0 4px 20px rgba(0,0,0,0.4);
}}
.score-label {{
  font-family:'Orbitron',monospace; font-size:8px;
  letter-spacing:0.18em; text-transform:uppercase;
  color:#4a3f6b; margin-top:6px; margin-bottom:3px;
}}
.score-grade {{
  font-size:11px; font-weight:600;
}}

/* ── Two column layout ── */
.two-col {{
  display:grid; grid-template-columns:1fr 1fr; gap:16px;
  margin-bottom:16px; position:relative; z-index:2;
}}
.three-col {{
  display:grid; grid-template-columns:repeat(3,1fr); gap:14px;
  margin-bottom:16px; position:relative; z-index:2;
}}

/* ── Cards ── */
.card {{
  background:rgba(12,5,28,0.7);
  border:1px solid rgba(120,40,220,0.18);
  border-radius:14px; padding:14px;
  position:relative; z-index:2;
}}
.card-title {{
  font-size:10px; font-family:'Orbitron',monospace;
  letter-spacing:0.14em; text-transform:uppercase;
  margin-bottom:10px; padding-bottom:7px;
  border-bottom:1px solid rgba(120,40,220,0.15);
  display:flex; align-items:center; gap:6px;
}}
.card-title::before {{
  content:'';
  width:6px; height:6px; border-radius:50%;
  flex-shrink:0;
}}

/* ── Role fit ── */
.role-fit-text {{
  color:#c8c5d8; font-size:12px; line-height:1.65;
}}

/* ── Footer ── */
.footer {{
  text-align:center; margin-top:20px;
  padding-top:16px;
  border-top:1px solid rgba(120,40,220,0.12);
  position:relative; z-index:2;
}}
.footer-text {{
  font-family:'Orbitron',monospace; font-size:8px;
  color:#1e1830; letter-spacing:0.2em;
}}

/* ── Download btn (outside report) ── */
#dl-btn {{
  display:block; margin:18px auto 0;
  background:linear-gradient(135deg,#4c1d95,#6d28d9 50%,#0891b2);
  color:#fff; border:none; border-radius:12px;
  font-family:'Orbitron',monospace; font-weight:700;
  font-size:12px; letter-spacing:0.14em;
  padding:14px 40px; cursor:pointer;
  box-shadow:0 8px 30px rgba(109,40,217,0.5);
  transition:transform .2s, box-shadow .2s;
}}
#dl-btn:hover {{
  transform:translateY(-3px);
  box-shadow:0 14px 40px rgba(109,40,217,0.65);
}}
#status {{
  text-align:center; color:#a78bfa;
  font-family:'Orbitron',monospace; font-size:10px;
  letter-spacing:0.1em; margin-top:10px; min-height:18px;
}}
</style>
</head>
<body>

<div id="report">
  <div class="grid-overlay"></div>

  <!-- HEADER -->
  <div class="header">
    <div>
      <div class="brand">⬡ RESUMEIQ</div>
      <div class="brand-sub">AI RESUME ANALYSIS REPORT</div>
    </div>
    <div class="candidate-badge">
      <div class="candidate-name">📄 {candidate_name}</div>
      <div class="candidate-date" id="rdate"></div>
    </div>
  </div>

  <!-- SCORE CARDS -->
  <div class="scores-row">
    <div class="score-box">
      {score_arc(ats, ac)}
      <div class="score-label">ATS Score</div>
      <div class="score-grade" style="color:{ac};">{ag}</div>
    </div>
    <div class="score-box">
      {score_arc(jd, jc)}
      <div class="score-label">JD Match</div>
      <div class="score-grade" style="color:{jc};">{jg}</div>
    </div>
    <div class="score-box">
      {score_arc(kw, kc)}
      <div class="score-label">Keywords</div>
      <div class="score-grade" style="color:{kc};">{kg}</div>
    </div>
    <div class="score-box">
      {score_arc(overall, oc)}
      <div class="score-label">Overall</div>
      <div class="score-grade" style="color:{oc};">{og}</div>
    </div>
  </div>

  <!-- ROLE FIT + KEYWORDS -->
  <div class="two-col">
    <div class="card">
      <div class="card-title" style="color:#60a5fa;">
        <span style="background:#60a5fa;" class="card-title"></span>
        🎯 Role Fit Summary
      </div>
      <div class="role-fit-text">{role_fit}</div>
      <div style="margin-top:10px;">
        <div style="color:#34d399;font-size:10px;font-family:Orbitron,monospace;
             letter-spacing:0.1em;margin-bottom:5px;">STRENGTHS</div>
        {strengths_html}
      </div>
      <div style="margin-top:10px;">
        <div style="color:#f87171;font-size:10px;font-family:Orbitron,monospace;
             letter-spacing:0.1em;margin-bottom:5px;">CRITICAL GAPS</div>
        {gaps_html}
      </div>
    </div>
    <div class="card">
      <div class="card-title" style="color:#c084fc;">
        🗝️ Keywords
      </div>
      <div style="margin-bottom:8px;">
        <div style="color:#34d399;font-size:9px;font-family:Orbitron,monospace;
             letter-spacing:0.12em;margin-bottom:5px;">FOUND</div>
        <div>{pills(kw_found,'#34d399','rgba(52,211,153,0.1)')}</div>
      </div>
      <div style="margin-bottom:8px;">
        <div style="color:#f87171;font-size:9px;font-family:Orbitron,monospace;
             letter-spacing:0.12em;margin-bottom:5px;">MISSING</div>
        <div>{pills(kw_miss,'#f87171','rgba(248,113,113,0.1)')}</div>
      </div>
      <div>
        <div style="color:#c084fc;font-size:9px;font-family:Orbitron,monospace;
             letter-spacing:0.12em;margin-bottom:5px;">RECOMMENDED</div>
        <div>{pills(kw_rec,'#c084fc','rgba(192,132,252,0.1)')}</div>
      </div>
    </div>
  </div>

  <!-- SKILLS GAP -->
  <div class="three-col">
    <div class="card">
      <div class="card-title" style="color:#34d399;">✅ Matched Skills</div>
      <div>{pills(matched,'#34d399','rgba(52,211,153,0.1)')}</div>
    </div>
    <div class="card">
      <div class="card-title" style="color:#f87171;">❌ Missing Skills</div>
      <div>{pills(missing,'#f87171','rgba(248,113,113,0.1)')}</div>
    </div>
    <div class="card">
      <div class="card-title" style="color:#c084fc;">⭐ Bonus Skills</div>
      <div>{pills(bonus,'#c084fc','rgba(192,132,252,0.1)')}</div>
    </div>
  </div>

  <!-- SKILLS TO GAIN + IMPROVEMENTS -->
  <div class="two-col">
    <div class="card">
      <div class="card-title" style="color:#00d2ff;">🚀 Skills to Gain</div>
      {skills_html if skills_html else "<span style='color:#3d3354;font-size:11px;'>No data</span>"}
    </div>
    <div class="card">
      <div class="card-title" style="color:#fbbf24;">✍️ Improvements</div>
      {improve_html if improve_html else "<span style='color:#3d3354;font-size:11px;'>No data</span>"}
    </div>
  </div>

  <!-- INTERVIEW TIPS -->
  <div class="card" style="position:relative;z-index:2;">
    <div class="card-title" style="color:#fbbf24;">💬 Interview Tips</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
      {tips_html}
    </div>
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <div class="footer-text">
      RESUMEIQ · POWERED BY GOOGLE GEMINI AI · REPORT GENERATED FOR {candidate_name.upper()}
    </div>
  </div>
</div>

<button id="dl-btn" onclick="downloadImage()">⬇ &nbsp; DOWNLOAD REPORT AS IMAGE</button>
<div id="status"></div>

<script>
  // Set date
  document.getElementById('rdate').textContent =
    new Date().toLocaleDateString('en-US',
      {{year:'numeric',month:'short',day:'numeric'}}).toUpperCase();

  function downloadImage() {{
    const btn = document.getElementById('dl-btn');
    const status = document.getElementById('status');
    btn.textContent = '⏳  GENERATING...';
    btn.disabled = true;
    status.textContent = 'Rendering report — this takes ~3 seconds...';

    html2canvas(document.getElementById('report'), {{
      scale: 2,
      useCORS: true,
      backgroundColor: '#030008',
      logging: false,
    }}).then(canvas => {{
      const link = document.createElement('a');
      link.download = 'ResumeIQ_Report_{candidate_name.replace(" ","_")}.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
      btn.textContent = '✅  DOWNLOADED!';
      status.textContent = 'Image saved to your Downloads folder.';
      setTimeout(() => {{
        btn.textContent = '⬇  DOWNLOAD REPORT AS IMAGE';
        btn.disabled = false;
        status.textContent = '';
      }}, 3000);
    }}).catch(err => {{
      btn.textContent = '⬇  DOWNLOAD REPORT AS IMAGE';
      btn.disabled = false;
      status.textContent = '❌ Error: ' + err.message;
    }});
  }}
</script>
</body>
</html>
"""
    components.html(html, height=1650, scrolling=True)
