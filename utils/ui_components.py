import streamlit as st
from collections import defaultdict


# ─────────────────────────────────────────────
# Score card
# ─────────────────────────────────────────────
def render_ats_score(col, score: int, label: str, color: str):
    score = max(0, min(100, int(score)))
    if score >= 75:
        grade, emoji = "Excellent", "🟢"
    elif score >= 55:
        grade, emoji = "Good", "🟡"
    elif score >= 35:
        grade, emoji = "Fair", "🟠"
    else:
        grade, emoji = "Needs Work", "🔴"

    with col:
        st.markdown(f"""
        <div class='score-card' style='--accent:{color};'>
            <div class='score-ring'>
                <svg viewBox='0 0 80 80' class='ring-svg'>
                    <circle cx='40' cy='40' r='34' class='ring-bg'/>
                    <circle cx='40' cy='40' r='34' class='ring-fill'
                        style='stroke:{color};
                               stroke-dasharray:{int(score*2.136)} 213.6;'/>
                </svg>
                <div class='score-number' style='color:{color};'>{score}</div>
            </div>
            <div class='score-label'>{label}</div>
            <div class='score-grade' style='color:{color};'>{emoji} {grade}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100)


# ─────────────────────────────────────────────
# Skills Gap
# ─────────────────────────────────────────────
def render_skills_gap(skills_gap: dict):
    matched = skills_gap.get("matched_skills", [])
    missing = skills_gap.get("missing_skills", [])
    bonus   = skills_gap.get("bonus_skills", [])

    st.markdown("<h3 class='section-h'>🎯 Skills Gap Analysis</h3>", unsafe_allow_html=True)
    st.caption(f"**{len(matched)}** matched · **{len(missing)}** missing · **{len(bonus)}** bonus")

    c1, c2, c3 = st.columns(3)
    for col, items, title, color, cls in [
        (c1, matched, "✅ Matched Skills",  "#34d399", "tag-found"),
        (c2, missing, "❌ Missing Skills",  "#f87171", "tag-missing"),
        (c3, bonus,   "⭐ Bonus Skills",    "#c084fc", "tag-neutral"),
    ]:
        with col:
            st.markdown(f"""
            <div class='section-card'>
                <div class='section-card-title' style='color:{color};'>{title}</div>
            """, unsafe_allow_html=True)
            if items:
                pills = " ".join([f"<span class='tag-pill {cls}'>{s}</span>" for s in items])
                st.markdown(pills, unsafe_allow_html=True)
            else:
                no_msg = "No critical gaps! ✨" if "Missing" in title else "None listed"
                st.markdown(f"<span style='color:#3d3b4f;font-size:0.82rem;'>{no_msg}</span>",
                            unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Keywords
# ─────────────────────────────────────────────
def render_keywords(keywords: dict):
    found       = keywords.get("found", [])
    missing     = keywords.get("missing", [])
    recommended = keywords.get("recommended", [])

    st.markdown("<h3 class='section-h'>🗝️ Keyword Analysis</h3>", unsafe_allow_html=True)

    k1, k2 = st.columns(2)
    with k1:
        st.markdown("""<div class='section-card'>
            <div class='section-card-title' style='color:#34d399;'>✅ Found in Resume</div>""",
                    unsafe_allow_html=True)
        if found:
            st.markdown(" ".join([f"<span class='tag-pill tag-found'>{k}</span>" for k in found]),
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with k2:
        st.markdown("""<div class='section-card'>
            <div class='section-card-title' style='color:#f87171;'>❌ Missing Keywords</div>""",
                    unsafe_allow_html=True)
        if missing:
            st.markdown(" ".join([f"<span class='tag-pill tag-missing'>{k}</span>" for k in missing]),
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""<div class='section-card' style='margin-top:1rem;'>
        <div class='section-card-title' style='color:#c084fc;'>💡 Recommended to Add</div>""",
                unsafe_allow_html=True)
    if recommended:
        st.markdown(" ".join([f"<span class='tag-pill tag-neutral'>{k}</span>" for k in recommended]),
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Additional Skills to Gain
# ─────────────────────────────────────────────
def render_additional_skills(skills: list):
    st.markdown("<h3 class='section-h'>🚀 Skills to Gain</h3>", unsafe_allow_html=True)
    st.caption("Personalized learning roadmap based on job requirements vs your resume")

    if not skills:
        st.info("No additional skills data. Try re-analyzing with a more detailed job description.")
        return

    priority_cfg = {
        "HIGH":   ("#f87171", "rgba(248,113,113,0.08)", "rgba(248,113,113,0.35)"),
        "MEDIUM": ("#f59e0b", "rgba(245,158,11,0.08)",  "rgba(245,158,11,0.35)"),
        "LOW":    ("#34d399", "rgba(52,211,153,0.08)",  "rgba(52,211,153,0.35)"),
    }
    cat_icons = {
        "devops": "⚙️", "cloud": "☁️", "ai": "🤖", "ml": "🧠",
        "backend": "🔧", "frontend": "🎨", "database": "🗄️",
        "security": "🔒", "data": "📊", "framework": "🏗️",
        "language": "💻", "tool": "🛠️", "soft": "💬",
    }

    grouped = defaultdict(list)
    for s in skills:
        grouped[s.get("category", "General")].append(s)

    for category, items in grouped.items():
        icon = next((v for k, v in cat_icons.items() if k in category.lower()), "📌")
        st.markdown(f"""
        <div class='cat-header'>{icon} {category}</div>
        """, unsafe_allow_html=True)

        for item in items:
            name     = item.get("skill", "")
            why      = item.get("why", "")
            how      = item.get("how_to_learn", "")
            priority = item.get("priority", "MEDIUM").upper()
            color, bg, border = priority_cfg.get(priority, priority_cfg["MEDIUM"])

            st.markdown(f"""
            <div class='skill-card' style='background:{bg};border-color:{border};
                        border-left-color:{color};'>
                <div class='skill-card-header'>
                    <span class='skill-name'>{name}</span>
                    <span class='priority-badge' style='color:{color};background:{color}22;
                          border-color:{color}66;'>● {priority}</span>
                </div>
                <div class='skill-why'>
                    <b style='color:#c084fc;'>Why needed →</b> {why}
                </div>
                <div class='skill-how'>
                    <b style='color:#00d2ff;'>📚 How to learn →</b> {how}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Improvements
# ─────────────────────────────────────────────
def render_improvements(improvements: list):
    st.markdown("<h3 class='section-h'>✍️ Resume Improvements</h3>", unsafe_allow_html=True)

    priority_cfg = {
        "HIGH":   ("🔴", "#f87171", "rgba(248,113,113,0.08)"),
        "MEDIUM": ("🟡", "#f59e0b", "rgba(245,158,11,0.08)"),
        "LOW":    ("🟢", "#34d399", "rgba(52,211,153,0.08)"),
    }
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    improvements = sorted(improvements, key=lambda x: order.get(x.get("priority", "LOW"), 3))

    for item in improvements:
        priority   = item.get("priority", "LOW")
        section    = item.get("section", "General")
        issue      = item.get("issue", "")
        suggestion = item.get("suggestion", "")
        emoji, color, bg = priority_cfg.get(priority, ("⚪", "#ccc", "rgba(200,200,200,0.05)"))

        st.markdown(f"""
        <div class='improve-card' style='background:{bg};border-left-color:{color};
             border-color:{color}44;'>
            <div class='improve-header'>
                <span style='font-size:1rem;'>{emoji}</span>
                <span style='font-family:Orbitron,monospace;font-weight:700;font-size:0.78rem;
                             color:{color};letter-spacing:0.08em;'>{priority}</span>
                <span class='section-badge'>📂 {section}</span>
            </div>
            <div class='improve-issue'><b style='color:#e2dff5;'>Issue:</b> {issue}</div>
            <div class='improve-fix'><b style='color:#34d399;'>✅ Fix:</b> {suggestion}</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# JD Match
# ─────────────────────────────────────────────
def render_jd_match(jd_analysis: dict):
    role_fit       = jd_analysis.get("role_fit", "")
    exp_match      = jd_analysis.get("experience_match", "")
    edu_match      = jd_analysis.get("education_match", "")
    strengths      = jd_analysis.get("top_strengths", [])
    critical_gaps  = jd_analysis.get("critical_gaps", [])
    interview_tips = jd_analysis.get("interview_tips", [])

    st.markdown("<h3 class='section-h'>📋 Job Description Match</h3>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='section-card'>
        <div class='section-card-title' style='color:#60a5fa;'>🎯 Role Fit Summary</div>
        <div style='color:#c8c5d8;font-size:0.9rem;line-height:1.75;'>{role_fit}</div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class='section-card'>
            <div class='section-card-title' style='color:#a78bfa;'>💼 Experience Match</div>
            <div style='color:#c8c5d8;font-size:0.87rem;line-height:1.6;'>{exp_match}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class='section-card'>
            <div class='section-card-title' style='color:#a78bfa;'>🎓 Education Match</div>
            <div style='color:#c8c5d8;font-size:0.87rem;line-height:1.6;'>{edu_match}</div>
        </div>""", unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        st.markdown("""<div class='section-card'>
            <div class='section-card-title' style='color:#34d399;'>🏆 Top Strengths</div>""",
                    unsafe_allow_html=True)
        for s in strengths:
            st.markdown(f"<div class='list-item'>✅ {s}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with s2:
        st.markdown("""<div class='section-card'>
            <div class='section-card-title' style='color:#f87171;'>⚠️ Critical Gaps</div>""",
                    unsafe_allow_html=True)
        for g in critical_gaps:
            st.markdown(f"<div class='list-item'>❌ {g}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""<div class='section-card'>
        <div class='section-card-title' style='color:#f59e0b;'>💬 Interview Tips</div>""",
                unsafe_allow_html=True)
    for i, tip in enumerate(interview_tips, 1):
        st.markdown(
            f"<div class='list-item'><b style='color:#f59e0b;'>{i}.</b> {tip}</div>",
            unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
