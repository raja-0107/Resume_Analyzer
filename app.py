import os
import streamlit as st
from utils.pdf_parser import extract_text_from_pdf
from utils.gemini_client import analyze_resume
from utils.image_report import render_image_report
from utils.ui_components import (
    render_ats_score,
    render_skills_gap,
    render_keywords,
    render_additional_skills,
    render_improvements,
    render_jd_match,
)
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
# ╔══════════════════════════════════════════════════════════════╗
# ║  RECOMMENDED: USE GROQ (free, fast, no daily quota)         ║
# ║  1. Go to console.groq.com → sign up free                   ║
# ║  2. API Keys → Create API Key (starts with gsk_...)         ║
# ║  3. Paste key below                                         ║
# ║                                                              ║
# ║  ALTERNATIVE: Google Gemini (aistudio.google.com)           ║
# ║  Key starts with AIza... — but has daily quota limits       ║
# ╚══════════════════════════════════════════════════════════════╝
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=GROQ_API_KEY
)  # ← paste Groq (gsk_...) OR Gemini (AIza...) key

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS + Animations ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Syne:wght@300;400;500;600;700&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    overflow-x: hidden;
}

/* ── Deep space background ── */
.stApp {
    background: #060010;
    color: #e2dff5;
    min-height: 100vh;
}

/* ── Animated nebula orb 1 ── */
.stApp::before {
    content: '';
    position: fixed;
    top: -20%;
    left: -15%;
    width: 70vw;
    height: 70vw;
    background: radial-gradient(ellipse,
        rgba(120,40,220,0.22) 0%,
        rgba(80,10,180,0.08) 40%,
        transparent 70%);
    animation: orb1 16s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
    border-radius: 50%;
    filter: blur(2px);
}
/* ── Animated nebula orb 2 ── */
.stApp::after {
    content: '';
    position: fixed;
    bottom: -20%;
    right: -15%;
    width: 60vw;
    height: 60vw;
    background: radial-gradient(ellipse,
        rgba(0,180,255,0.14) 0%,
        rgba(0,120,200,0.06) 40%,
        transparent 70%);
    animation: orb2 20s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
    border-radius: 50%;
    filter: blur(3px);
}
@keyframes orb1 {
    0%   { transform: translate(0,0) scale(1) rotate(0deg); }
    100% { transform: translate(10vw,8vh) scale(1.25) rotate(15deg); }
}
@keyframes orb2 {
    0%   { transform: translate(0,0) scale(1) rotate(0deg); }
    100% { transform: translate(-8vw,-10vh) scale(1.3) rotate(-20deg); }
}

/* ── Star field ── */
.stars-layer {
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background:
        radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 25% 60%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 40% 30%, rgba(192,132,252,0.8) 0%, transparent 100%),
        radial-gradient(1px 1px at 55% 80%, rgba(255,255,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 70% 20%, rgba(0,210,255,0.7) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 82% 55%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 92% 10%, rgba(192,132,252,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 15% 85%, rgba(0,210,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 60% 45%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 35% 90%, rgba(192,132,252,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 78% 75%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 5% 40%, rgba(0,210,255,0.4) 0%, transparent 100%);
    animation: starTwinkle 6s ease-in-out infinite alternate;
}
@keyframes starTwinkle {
    0%   { opacity: 0.6; }
    100% { opacity: 1; }
}

/* ── Grid overlay ── */
.grid-bg {
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(120,40,220,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(120,40,220,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridPulse 8s ease-in-out infinite alternate;
}
@keyframes gridPulse { 0%{opacity:.3} 100%{opacity:.8} }

/* ── Scanlines ── */
.scanlines {
    position: fixed; inset: 0; pointer-events: none; z-index: 1;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 3px,
        rgba(0,0,0,0.018) 3px, rgba(0,0,0,0.018) 4px
    );
}

/* ── Floating particles ── */
.particles { position:fixed; inset:0; pointer-events:none; z-index:1; overflow:hidden; }
.pt {
    position: absolute; border-radius: 50%;
    animation: ptDrift linear infinite;
    filter: blur(0.5px);
}
@keyframes ptDrift {
    0%   { transform:translateY(105vh) scale(0) rotate(0deg); opacity:0; }
    5%   { opacity:1; }
    90%  { opacity:.8; }
    100% { transform:translateY(-8vh) translateX(40px) scale(1.6) rotate(180deg); opacity:0; }
}

/* ── Shooting stars ── */
.shooting-star {
    position: fixed;
    width: 120px; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(192,132,252,0.9), transparent);
    border-radius: 50%;
    pointer-events: none; z-index: 1;
    animation: shoot linear infinite;
}
@keyframes shoot {
    0%   { transform: translateX(-200px) translateY(0) rotate(-30deg); opacity:0; }
    10%  { opacity:1; }
    90%  { opacity:.5; }
    100% { transform: translateX(110vw) translateY(50vh) rotate(-30deg); opacity:0; }
}

/* ── Hide sidebar ── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
section[data-testid="stSidebarContent"] {
    display: none !important;
}

/* ── Main container padding (mobile safe) ── */
.main .block-container {
    padding: 1rem 1rem 3rem 1rem !important;
    max-width: 1200px !important;
}
@media (min-width: 768px) {
    .main .block-container {
        padding: 2rem 2.5rem 4rem 2.5rem !important;
    }
}

/* ════════════════════════════════════════
   HERO SECTION
════════════════════════════════════════ */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    animation: heroIn 0.9s cubic-bezier(0.22,1,0.36,1) forwards;
    position: relative;
}
@keyframes heroIn {
    0%   { opacity:0; transform:translateY(-30px); }
    100% { opacity:1; transform:translateY(0); }
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(120,40,220,0.12);
    border: 1px solid rgba(120,40,220,0.4);
    color: #b97eff;
    font-family: 'Orbitron', monospace;
    font-size: clamp(0.52rem, 1.5vw, 0.62rem);
    letter-spacing: 0.2em;
    padding: 6px 18px;
    border-radius: 24px;
    margin-bottom: 1.3rem;
    animation: badgePulse 3.5s ease-in-out infinite;
    white-space: nowrap;
}
.badge-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #9333ea;
    box-shadow: 0 0 10px #9333ea;
    animation: dotBlink 1.8s ease-in-out infinite;
    flex-shrink: 0;
}
@keyframes badgePulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(120,40,220,0.3); }
    50%      { box-shadow: 0 0 25px 8px rgba(120,40,220,0.16); }
}
@keyframes dotBlink {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.3; transform:scale(.6); }
}

.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.8rem, 6vw, 4rem);
    font-weight: 900;
    background: linear-gradient(135deg,
        #fff 0%, #d8b4fe 25%, #c084fc 45%,
        #00d2ff 65%, #38bdf8 80%, #fff 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 6s ease-in-out infinite;
    line-height: 1.08;
    letter-spacing: -0.01em;
}
@keyframes shimmer {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.hero-sub {
    font-size: clamp(0.82rem, 2vw, 1rem);
    color: #6b5e8a;
    font-weight: 400;
    margin-top: 0.8rem;
    letter-spacing: 0.02em;
    line-height: 1.6;
    padding: 0 1rem;
}

.hero-powered {
    margin-top: 1.2rem;
    font-size: 0.72rem;
    color: #3d334d;
    font-family: 'Orbitron', monospace;
    letter-spacing: 0.1em;
}
.hero-powered span {
    color: #4285f4;
    font-weight: 700;
}

/* ════════════════════════════════════════
   INPUT CARDS
════════════════════════════════════════ */
.input-card {
    background: rgba(12,5,28,0.75);
    border: 1px solid rgba(120,40,220,0.25);
    border-radius: 20px;
    padding: 1.3rem 1.5rem 0.3rem;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    position: relative;
    overflow: hidden;
    margin-bottom: 0.5rem;
    transition: border-color .35s, box-shadow .35s;
}
.input-card:hover {
    border-color: rgba(192,132,252,0.5);
    box-shadow: 0 0 40px rgba(120,40,220,0.14), 0 4px 20px rgba(0,0,0,0.3);
}
.input-card::before {
    content: '';
    position: absolute;
    top: 0; left: -100%; right: -100%; height: 1px;
    background: linear-gradient(90deg,
        transparent 0%, rgba(192,132,252,0.6) 50%, transparent 100%);
    animation: topSweep 4s ease-in-out infinite;
}
@keyframes topSweep {
    0%   { left:-100%; opacity:0; }
    20%  { opacity:1; }
    80%  { opacity:1; }
    100% { left:100%; opacity:0; }
}
.input-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% -20%,
        rgba(120,40,220,0.1) 0%, transparent 60%);
    pointer-events: none;
}

.card-label {
    font-family: 'Orbitron', monospace;
    font-size: clamp(0.55rem, 1.5vw, 0.62rem);
    font-weight: 600;
    letter-spacing: 0.2em;
    color: #7c44cc;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-label::before {
    content: '';
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #9333ea;
    box-shadow: 0 0 12px #9333ea, 0 0 24px rgba(147,51,234,0.4);
    animation: dotBlink 2s ease-in-out infinite;
    flex-shrink: 0;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(120,40,220,0.05) !important;
    border: 1.5px dashed rgba(120,40,220,0.35) !important;
    border-radius: 14px !important;
    transition: all .35s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(192,132,252,0.6) !important;
    background: rgba(120,40,220,0.1) !important;
    box-shadow: 0 0 20px rgba(120,40,220,0.12) !important;
}
[data-testid="stFileUploader"] * { color: #a78bfa !important; }
[data-testid="stFileUploader"] svg { color: #7c3aed !important; }

/* ── Text area ── */
.stTextArea textarea {
    background: rgba(120,40,220,0.05) !important;
    border: 1px solid rgba(120,40,220,0.28) !important;
    border-radius: 13px !important;
    color: #e2dff5 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    transition: border-color .3s, box-shadow .3s !important;
    resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: rgba(192,132,252,.7) !important;
    box-shadow: 0 0 25px rgba(120,40,220,0.2), inset 0 0 15px rgba(120,40,220,0.04) !important;
}
.stTextArea textarea::placeholder { color: #3d3050 !important; }

/* ── Upload success ── */
.upload-ok {
    background: rgba(52,211,153,0.07);
    border: 1px solid rgba(52,211,153,0.25);
    border-radius: 10px;
    padding: 0.55rem 1rem;
    color: #34d399;
    font-size: 0.84rem;
    margin-top: 0.6rem;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: fadeSlideUp 0.4s ease-out;
}
@keyframes fadeSlideUp {
    0%   { opacity:0; transform:translateY(8px); }
    100% { opacity:1; transform:translateY(0); }
}

/* ════════════════════════════════════════
   ANALYZE BUTTON
════════════════════════════════════════ */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #3b0d8f, #6d28d9 40%, #0369a1 80%, #0891b2) !important;
    background-size: 300% 300% !important;
    color: #fff !important;
    border: none !important;
    border-radius: 16px !important;
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    font-size: clamp(0.72rem, 2vw, 0.82rem) !important;
    letter-spacing: 0.15em !important;
    padding: 1rem 2rem !important;
    animation: btnShift 6s ease infinite !important;
    transition: transform .25s ease, box-shadow .25s ease !important;
    position: relative !important;
    overflow: hidden !important;
    cursor: pointer !important;
}
@keyframes btnShift {
    0%,100% { background-position:0% 50%; }
    50%      { background-position:100% 50%; }
}
.stButton > button::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(105deg,
        transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
    background-size: 300% 100%;
    animation: btnSheen 2.8s linear infinite;
}
@keyframes btnSheen {
    0%   { background-position: 200% 0; }
    100% { background-position: -100% 0; }
}
.stButton > button::after {
    content: '';
    position: absolute; inset: 0;
    border-radius: 16px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.15),
                inset 0 -1px 0 rgba(0,0,0,0.2);
}
.stButton > button:hover {
    transform: translateY(-4px) scale(1.01) !important;
    box-shadow: 0 16px 48px rgba(109,40,217,.55),
                0 0 60px rgba(8,145,178,.2),
                0 4px 12px rgba(0,0,0,0.4) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.99) !important;
}

/* ════════════════════════════════════════
   DIVIDER
════════════════════════════════════════ */
.divider {
    height: 1px;
    background: linear-gradient(90deg,
        transparent, rgba(120,40,220,.5), rgba(0,210,255,.35), transparent);
    margin: 2rem 0;
    position: relative;
}
.divider::after {
    content: '◆';
    position: absolute; top:50%; left:50%;
    transform: translate(-50%,-50%);
    color: #7c3aed; font-size: 0.48rem;
    background: #060010; padding: 0 10px;
    animation: diamondSpin 10s linear infinite;
}
@keyframes diamondSpin {
    0%   { transform:translate(-50%,-50%) rotate(0deg) scale(1); }
    50%  { transform:translate(-50%,-50%) rotate(180deg) scale(1.4); }
    100% { transform:translate(-50%,-50%) rotate(360deg) scale(1); }
}

/* ════════════════════════════════════════
   RESULTS HEADING
════════════════════════════════════════ */
.results-h {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.1rem, 3vw, 1.5rem);
    font-weight: 700;
    background: linear-gradient(90deg, #c084fc, #60a5fa, #00d2ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 1rem 0 1.5rem;
    animation: heroIn 0.6s ease-out;
}

/* ════════════════════════════════════════
   SCORE CARDS
════════════════════════════════════════ */
.score-card {
    background: rgba(12,5,28,0.85);
    border: 1px solid rgba(120,40,220,0.2);
    border-radius: 20px;
    padding: 1.6rem 1rem 1.2rem;
    text-align: center;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    position: relative;
    overflow: hidden;
    transition: transform .35s cubic-bezier(0.34,1.56,0.64,1), box-shadow .35s;
    animation: cardIn 0.6s cubic-bezier(0.22,1,0.36,1) both;
    cursor: default;
}
.score-card::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(circle at 50% -10%,
        rgba(120,40,220,.15) 0%, transparent 65%);
}
.score-card:hover {
    transform: translateY(-7px) scale(1.02);
    box-shadow: 0 20px 55px rgba(120,40,220,.3),
                0 0 30px rgba(var(--accent-rgb), .15);
}
@keyframes cardIn {
    0%   { opacity:0; transform:scale(0.88) translateY(16px); }
    100% { opacity:1; transform:scale(1) translateY(0); }
}

.score-ring {
    position: relative;
    width: 80px; height: 80px;
    margin: 0 auto 0.8rem;
}
.ring-svg {
    width: 80px; height: 80px;
    transform: rotate(-90deg);
}
.ring-bg {
    fill: none;
    stroke: rgba(120,40,220,0.12);
    stroke-width: 5;
}
.ring-fill {
    fill: none;
    stroke-width: 5;
    stroke-linecap: round;
    transition: stroke-dasharray 1.2s cubic-bezier(0.22,1,0.36,1);
    filter: drop-shadow(0 0 4px currentColor);
    animation: ringDraw 1.4s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes ringDraw {
    0%   { stroke-dasharray: 0 213.6; }
}
.score-number {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    font-family: 'Orbitron', monospace;
    font-size: 1.55rem;
    font-weight: 900;
    line-height: 1;
    text-shadow: 0 0 20px currentColor;
    animation: numCount 1.4s ease-out both;
}
@keyframes numCount {
    0%   { opacity:0; transform: translate(-50%,-50%) scale(0.5); }
    60%  { transform: translate(-50%,-50%) scale(1.15); }
    100% { opacity:1; transform: translate(-50%,-50%) scale(1); }
}
.score-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4a3f6b;
    margin-bottom: 0.45rem;
}
.score-grade {
    font-size: 0.8rem;
    font-weight: 600;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #7c3aed, #0891b2) !important;
    border-radius: 99px !important;
    box-shadow: 0 0 10px rgba(124,58,237,.5) !important;
    transition: width 1.2s cubic-bezier(0.22,1,0.36,1) !important;
}
.stProgress > div {
    background: rgba(120,40,220,.08) !important;
    border-radius: 99px !important;
    height: 5px !important;
}

/* ════════════════════════════════════════
   SECTION CARDS
════════════════════════════════════════ */
.section-card {
    background: rgba(12,5,28,0.65);
    border: 1px solid rgba(120,40,220,0.18);
    border-radius: 16px;
    padding: 1.3rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    transition: border-color .3s, box-shadow .3s;
    animation: fadeSlideUp 0.5s ease-out both;
}
.section-card:hover {
    border-color: rgba(120,40,220,.38);
    box-shadow: 0 8px 32px rgba(120,40,220,.1);
}
.section-card-title {
    font-weight: 700;
    font-size: 0.88rem;
    margin-bottom: 0.8rem;
    letter-spacing: 0.02em;
}
.section-h {
    font-family: 'Orbitron', monospace;
    font-size: clamp(0.85rem, 2.5vw, 1.05rem);
    font-weight: 700;
    color: #a78bfa;
    letter-spacing: 0.04em;
    margin: 1.2rem 0 0.8rem;
}

/* ── Category header ── */
.cat-header {
    font-family: 'Orbitron', monospace;
    font-size: clamp(0.62rem, 1.5vw, 0.72rem);
    font-weight: 700;
    color: #7c55cc;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.7rem;
    border-left: 3px solid #7c55cc;
    padding-left: 10px;
    box-shadow: -3px 0 12px rgba(124,85,204,0.4);
}

/* ── Skill cards ── */
.skill-card {
    border: 1px solid;
    border-left: 4px solid;
    border-radius: 15px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.85rem;
    animation: fadeSlideUp 0.5s ease-out both;
    transition: transform .2s;
}
.skill-card:hover { transform: translateX(4px); }
.skill-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 0.65rem;
}
.skill-name {
    font-family: 'Orbitron', monospace;
    font-weight: 700;
    font-size: clamp(0.82rem, 2vw, 0.95rem);
    color: #e2dff5;
}
.priority-badge {
    font-size: 0.6rem;
    font-family: 'Orbitron', monospace;
    letter-spacing: 0.1em;
    padding: 3px 12px;
    border-radius: 20px;
    border: 1px solid;
    white-space: nowrap;
}
.skill-why {
    font-size: clamp(0.78rem, 2vw, 0.85rem);
    color: #9c9aaa;
    margin-bottom: 0.5rem;
    line-height: 1.55;
}
.skill-how {
    font-size: clamp(0.78rem, 2vw, 0.85rem);
    color: #c8c5d8;
    background: rgba(0,0,0,0.25);
    border-radius: 10px;
    padding: 0.5rem 0.85rem;
    line-height: 1.55;
}

/* ── Improvement cards ── */
.improve-card {
    border: 1px solid;
    border-left: 4px solid;
    border-radius: 13px;
    padding: 1rem 1.3rem;
    margin-bottom: 0.85rem;
    animation: fadeSlideUp 0.5s ease-out both;
    transition: transform .2s;
}
.improve-card:hover { transform: translateX(4px); }
.improve-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 0.55rem;
    flex-wrap: wrap;
}
.section-badge {
    font-size: 0.73rem;
    color: #6b6880;
    background: rgba(255,255,255,0.04);
    padding: 2px 9px;
    border-radius: 10px;
}
.improve-issue {
    font-size: clamp(0.78rem, 2vw, 0.86rem);
    color: #9c9aaa;
    margin-bottom: 0.4rem;
    line-height: 1.55;
}
.improve-fix {
    font-size: clamp(0.78rem, 2vw, 0.86rem);
    color: #c8c5d8;
    background: rgba(0,0,0,0.15);
    border-radius: 9px;
    padding: 0.42rem 0.8rem;
    line-height: 1.55;
}

/* ── List items ── */
.list-item {
    color: #c8c5d8;
    font-size: clamp(0.78rem, 2vw, 0.85rem);
    padding: 4px 0;
    line-height: 1.6;
}

/* ── Pills ── */
.tag-pill {
    display: inline-block;
    padding: 4px 13px;
    border-radius: 20px;
    font-size: clamp(0.7rem, 1.8vw, 0.77rem);
    font-weight: 500;
    margin: 3px;
    transition: transform .2s, box-shadow .2s;
    cursor: default;
    animation: fadeSlideUp 0.4s ease-out both;
}
.tag-pill:hover {
    transform: scale(1.1) translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.tag-found   { background:rgba(52,211,153,.1);  color:#34d399; border:1px solid rgba(52,211,153,.3); }
.tag-missing { background:rgba(248,113,113,.1); color:#f87171; border:1px solid rgba(248,113,113,.3); }
.tag-neutral { background:rgba(192,132,252,.1); color:#c084fc; border:1px solid rgba(192,132,252,.3); }

/* ════════════════════════════════════════
   TABS
════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(12,5,28,.7) !important;
    border-radius: 14px !important;
    padding: 5px !important;
    border: 1px solid rgba(120,40,220,.2) !important;
    gap: 3px !important;
    flex-wrap: wrap !important;
    overflow-x: auto !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', monospace !important;
    font-size: clamp(0.52rem, 1.5vw, 0.62rem) !important;
    letter-spacing: .06em !important;
    color: #4a3f6b !important;
    border-radius: 10px !important;
    transition: all .25s !important;
    white-space: nowrap !important;
    padding: 8px 12px !important;
}
.stTabs [aria-selected="true"] {
    color: #e2dff5 !important;
    background: rgba(120,40,220,.38) !important;
    border-bottom: none !important;
    box-shadow: 0 2px 12px rgba(120,40,220,.3) !important;
}

/* ════════════════════════════════════════
   EXPANDER
════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: rgba(12,5,28,.7) !important;
    border-radius: 12px !important;
    color: #a78bfa !important;
    font-family: 'Orbitron', monospace !important;
    font-size: clamp(0.6rem, 1.5vw, 0.68rem) !important;
    border: 1px solid rgba(120,40,220,.2) !important;
    transition: all .25s !important;
}
.streamlit-expanderHeader:hover {
    border-color: rgba(192,132,252,.4) !important;
    background: rgba(120,40,220,.12) !important;
}

/* ════════════════════════════════════════
   SPINNER / ERROR / SUCCESS
════════════════════════════════════════ */
.stSpinner > div { border-top-color: #7c3aed !important; }
.stAlert {
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
}

/* ════════════════════════════════════════
   SCROLLBAR
════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #060010; }
::-webkit-scrollbar-thumb {
    background: rgba(120,40,220,.4);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(120,40,220,.7); }

/* ════════════════════════════════════════
   MOBILE OVERRIDES
════════════════════════════════════════ */
@media (max-width: 640px) {
    .hero { padding: 1.8rem 0.5rem 1rem; }
    .hero-sub { font-size: 0.78rem; }
    .input-card { padding: 1rem 1rem 0.2rem; border-radius: 16px; }
    .score-card { padding: 1.2rem 0.7rem 0.9rem; border-radius: 16px; }
    .score-ring { width: 64px; height: 64px; }
    .ring-svg { width: 64px; height: 64px; }
    .score-number { font-size: 1.25rem; }
    .score-label { font-size: 0.52rem; }
    .score-grade { font-size: 0.72rem; }
    .section-card { padding: 1rem; }
    .skill-card { padding: 0.9rem 1rem; }
    .improve-card { padding: 0.9rem 1rem; }
}
</style>

<!-- Background layers -->
<div class="stars-layer"></div>
<div class="grid-bg"></div>
<div class="scanlines"></div>

<!-- Floating particles -->
<div class="particles">
  <div class="pt" style="left:4%;width:3px;height:3px;background:rgba(192,132,252,.8);animation-duration:10s;animation-delay:0s;"></div>
  <div class="pt" style="left:12%;width:2px;height:2px;background:rgba(0,210,255,.7);animation-duration:14s;animation-delay:1.2s;"></div>
  <div class="pt" style="left:22%;width:3px;height:3px;background:rgba(192,132,252,.55);animation-duration:9s;animation-delay:3.5s;"></div>
  <div class="pt" style="left:34%;width:2px;height:2px;background:rgba(0,210,255,.6);animation-duration:16s;animation-delay:0.6s;"></div>
  <div class="pt" style="left:45%;width:3px;height:3px;background:rgba(192,132,252,.85);animation-duration:11s;animation-delay:5s;"></div>
  <div class="pt" style="left:57%;width:2px;height:2px;background:rgba(0,210,255,.75);animation-duration:8s;animation-delay:2s;"></div>
  <div class="pt" style="left:66%;width:3px;height:3px;background:rgba(147,51,234,.9);animation-duration:12s;animation-delay:7s;"></div>
  <div class="pt" style="left:76%;width:2px;height:2px;background:rgba(0,210,255,.55);animation-duration:15s;animation-delay:4s;"></div>
  <div class="pt" style="left:85%;width:3px;height:3px;background:rgba(192,132,252,.5);animation-duration:10s;animation-delay:1s;"></div>
  <div class="pt" style="left:93%;width:2px;height:2px;background:rgba(0,210,255,.7);animation-duration:13s;animation-delay:8s;"></div>
  <div class="pt" style="left:28%;width:2px;height:2px;background:rgba(147,51,234,.65);animation-duration:11s;animation-delay:6s;"></div>
  <div class="pt" style="left:51%;width:3px;height:3px;background:rgba(192,132,252,.45);animation-duration:17s;animation-delay:2.8s;"></div>
</div>

<!-- Shooting stars -->
<div class="shooting-star" style="top:18%;animation-duration:7s;animation-delay:0s;"></div>
<div class="shooting-star" style="top:42%;animation-duration:11s;animation-delay:3.5s;opacity:0.6;"></div>
<div class="shooting-star" style="top:68%;animation-duration:9s;animation-delay:7s;opacity:0.4;width:80px;"></div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">
        <span class="badge-dot"></span>
        POWERED BY GROQ  
        <span class="badge-dot"></span>
    </div>
    <div class="hero-title">AI RESUME ANALYZER</div>
    <div class="hero-sub">
        Upload your resume · Instant ATS scores · Skills gap analysis · Land your dream job
    </div>
    <div class="hero-powered">
        Running on <span>Groq LLaMA-3.3</span> 
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input section ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown(
        '<div class="input-card"><div class="card-label">📄 Resume Upload</div></div>',
        unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
    if uploaded_file:
        st.markdown(
            f'<div class="upload-ok">✅ &nbsp;<b>{uploaded_file.name}</b> &nbsp;ready for analysis</div>',
            unsafe_allow_html=True)

with col2:
    st.markdown(
        '<div class="input-card"><div class="card-label">💼 Job Description</div></div>',
        unsafe_allow_html=True)
    job_description = st.text_area(
        "Job Description",
        placeholder="Paste the full job description here...\n\nMore detail = better analysis!",
        height=190,
        label_visibility="collapsed",
    )

st.markdown("<br>", unsafe_allow_html=True)

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze_clicked = st.button("⚡  ANALYZE MY RESUME", use_container_width=True)

# ── Analysis logic ────────────────────────────────────────────────────────────
if analyze_clicked:
    if not uploaded_file:
        st.error("📄 Please upload your resume PDF.")
        st.stop()
    if not job_description.strip():
        st.error("💼 Please paste the job description.")
        st.stop()
    if GROQ_API_KEY in ("YOUR_API_KEY_HERE", "YOUR_GEMINI_API_KEY_HERE", ""):
        st.error(
            "🔑 Add your Gemini API key in app.py → GEMINI_API_KEY = 'AIza...'\n\n"
            "Get a free key at: aistudio.google.com (no credit card needed)"
        )
        st.stop()

    with st.spinner("📖 Extracting resume content..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    if not resume_text.strip():
        st.error(
            "❌ Could not extract text from the PDF. "
            "Please use a text-based PDF (not a scanned image)."
        )
        st.stop()

    status_box = st.empty()

    def update_status(msg):
        status_box.markdown(
            f"<div style='background:rgba(120,40,220,0.08);border:1px solid rgba(120,40,220,0.25);"
            f"border-radius:10px;padding:10px 16px;color:#a78bfa;"
            f"font-family:Orbitron,monospace;font-size:0.72rem;letter-spacing:0.08em;'>"
            f"⚡ {msg}</div>",
            unsafe_allow_html=True
        )

    update_status("Connecting to Gemini AI...")
    result = analyze_resume(
        resume_text, job_description, GROQ_API_KEY,
        progress_callback=update_status
    )
    status_box.empty()

    if "error" in result:
        st.error(result["error"])
        st.stop()

    # ── Results ───────────────────────────────────────────────────────────────
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='results-h'>📊 Analysis Results</div>", unsafe_allow_html=True)

    sc1, sc2, sc3, sc4 = st.columns(4)
    render_ats_score(sc1, result.get("ats_score", 0),      "ATS Score",     "#c084fc")
    render_ats_score(sc2, result.get("jd_match_score", 0), "JD Match",      "#00d2ff")
    render_ats_score(sc3, result.get("keyword_score", 0),  "Keywords",      "#34d399")
    render_ats_score(sc4, result.get("overall_score", 0),  "Overall",       "#f59e0b")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visual Image Report Card ───────────────────────────────────────────────
    st.markdown("""
    <div style='font-family:Orbitron,monospace;font-size:0.62rem;font-weight:700;
         color:#7c44cc;letter-spacing:0.2em;text-transform:uppercase;
         margin-bottom:0.6rem;'>
         🖼️ &nbsp; VISUAL REPORT CARD — Click button below to download as PNG
    </div>
    """, unsafe_allow_html=True)

    candidate_name = uploaded_file.name.replace('.pdf','').replace('_',' ').replace('-',' ').title()
    render_image_report(result, candidate_name)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='results-h'>🔬 Detailed Breakdown</div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Skills Gap",
        "🗝️ Keywords",
        "🚀 Skills to Gain",
        "✍️ Improvements",
        "📋 JD Match",
    ])
    with tab1: render_skills_gap(result.get("skills_gap", {}))
    with tab2: render_keywords(result.get("keywords", {}))
    with tab3: render_additional_skills(result.get("additional_skills_to_gain", []))
    with tab4: render_improvements(result.get("improvements", []))
    with tab5: render_jd_match(result.get("jd_analysis", {}))

    with st.expander("📃 View Extracted Resume Text"):
        st.text_area("", resume_text, height=280, label_visibility="collapsed")

    st.markdown("""
    <div style='text-align:center;margin-top:3rem;padding:1.5rem;
         border-top:1px solid rgba(120,40,220,0.15);'>
        <div style='font-family:Orbitron,monospace;font-size:0.58rem;
             color:#2e2540;letter-spacing:0.18em;'>
            RESUMEIQ · POWERED BY GOOGLE GEMINI 1.5 FLASH · FREE TIER
        </div>
    </div>
    """, unsafe_allow_html=True)
