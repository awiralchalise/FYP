from __future__ import annotations
from pathlib import Path
import sys
import time
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import json

PROJ_ROOT = Path(__file__).resolve().parents[1]
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

try:
    from src.parsing.ml.skill_matcher_db import analyze_resume
    from src.database import AuthService, ResumeRepository, SkillRepository, init_supabase
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

UPLOADS_DIR = PROJ_ROOT / "app" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ MODERN PROFESSIONAL UI - Like Popular Websites
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Poppins', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* ============================================
       LOGIN PAGE STYLING - Modern Card Design
    ============================================ */
    .login-container {
        max-width: 450px;
        margin: 60px auto;
        background: white;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.6s ease;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }

    .login-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }

    .login-subtitle {
        color: #666;
        font-size: 0.95rem;
        font-weight: 400;
    }

    /* ============================================
       DASHBOARD STYLING - Modern Layout
    ============================================ */
    .dashboard-header {
        background: white;
        padding: 20px 40px;
        margin: -70px -70px 30px -70px;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .dashboard-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }

    .dashboard-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 40px;
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        margin-top: 20px;
    }

    /* Welcome Banner */
    .welcome-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }

    .welcome-banner h2 {
        margin: 0 0 8px 0;
        font-size: 1.8rem;
        font-weight: 600;
        color: white !important;
        border: none !important;
        padding: 0 !important;
    }

    .welcome-banner p {
        margin: 0;
        opacity: 0.95;
        font-size: 1rem;
    }

    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }

    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        border: none;
    }

    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 10px 0;
    }

    .stat-label {
        font-size: 0.85rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color:#ffffff;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Buttons - Modern Style */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* Tabs - Clean Design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f9fafb;
        padding: 8px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        color: #6b7280;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: #667eea;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    /* Input Fields - Modern */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        padding: 12px 16px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* File Uploader */
    .uploadedFile {
        background: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s ease;
    }

    .uploadedFile:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }

    /* Skill Badges */
    .skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        font-weight: 600;
        font-size: 0.85rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    .skill-badge-missing {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }

    /* Message Boxes */
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    .warning-box {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }

    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #f9fafb;
        border-radius: 10px;
        font-weight: 600;
        color: #374151;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
    }

    /* Remove padding from block container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }

    /* Content area cards */
    .content-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
    }

    /* Sign out button */
    .sign-out-btn button {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        padding: 8px 20px !important;
        font-size: 0.9rem !important;
    }

    .sign-out-btn button:hover {
        background: #667eea !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-main: #f4f1ea;
        --surface: rgba(255, 255, 255, 0.90);
        --surface-strong: #ffffff;
        --border: rgba(72, 56, 43, 0.10);
        --border-strong: rgba(72, 56, 43, 0.16);
        --text-main: #1d1a17;
        --text-soft: #6f665d;
        --text-faint: #9a9086;
        --brand: #0f766e;
        --brand-deep: #115e59;
        --accent: #c08457;
        --danger: #b54d42;
        --danger-soft: #fbeae6;
        --success: #1f7a52;
        --success-soft: #e8f6ef;
        --info: #295c9b;
        --info-soft: #eaf1fb;
        --warning: #9a6700;
        --warning-soft: #fff5dd;
        --shadow-soft: 0 24px 70px rgba(63, 46, 32, 0.08);
        --shadow-card: 0 16px 40px rgba(63, 46, 32, 0.08);
    }

    * {
        font-family: 'Manrope', sans-serif;
    }

    .stApp {
        color: var(--text-main);
        background:
            radial-gradient(circle at top left, rgba(15, 118, 110, 0.12), transparent 32%),
            radial-gradient(circle at top right, rgba(192, 132, 87, 0.14), transparent 28%),
            linear-gradient(180deg, #f8f4ee 0%, var(--bg-main) 45%, #efe7dd 100%);
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(255,255,255,0.24) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.24) 1px, transparent 1px);
        background-size: 72px 72px;
        mask-image: linear-gradient(180deg, rgba(0,0,0,0.35), transparent 78%);
        opacity: 0.3;
    }

    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 1.5rem;
        position: relative;
        z-index: 1;
    }

    .page-shell {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 32px;
        padding: 22px;
        box-shadow: var(--shadow-soft);
        backdrop-filter: blur(18px);
    }

    .auth-stage {
        background:
            radial-gradient(circle at top left, rgba(255,255,255,0.20), transparent 25%),
            linear-gradient(145deg, #0f766e 0%, #115e59 34%, #1f4f8c 100%);
        border-radius: 30px;
        padding: 34px;
        min-height: 100%;
        position: relative;
        overflow: hidden;
        box-shadow: 0 28px 50px rgba(17, 94, 89, 0.24);
    }

    .auth-stage::before,
    .auth-stage::after {
        content: "";
        position: absolute;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
    }

    .auth-stage::before {
        width: 240px;
        height: 240px;
        right: -80px;
        top: -60px;
    }

    .auth-stage::after {
        width: 180px;
        height: 180px;
        left: -40px;
        bottom: -60px;
    }

    .auth-stage-inner {
        position: relative;
        z-index: 1;
    }

    .auth-stage-kicker {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.18);
        color: rgba(255,255,255,0.92);
        font-size: 0.76rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 800;
        margin-bottom: 20px;
    }

    .auth-stage-title {
        font-size: 3.1rem;
        line-height: 0.95;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.05em;
        max-width: 520px;
        margin-bottom: 18px;
    }

    .auth-stage-copy {
        max-width: 520px;
        color: rgba(244, 251, 250, 0.82);
        font-size: 1rem;
        line-height: 1.8;
        margin-bottom: 28px;
    }

    .auth-highlight-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
        margin-bottom: 28px;
    }

    .auth-highlight-card {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 20px;
        padding: 18px;
        backdrop-filter: blur(10px);
    }

    .auth-highlight-value {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 8px;
    }

    .auth-highlight-label {
        color: rgba(244, 251, 250, 0.70);
        font-size: 0.84rem;
        line-height: 1.5;
    }

    .auth-proof {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .auth-proof-chip {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.14);
        color: rgba(255,255,255,0.9);
        font-size: 0.84rem;
        font-weight: 700;
    }

    .dashboard-shell {
        display: flex;
        flex-direction: column;
        gap: 26px;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.45fr 0.9fr;
        gap: 22px;
        align-items: stretch;
    }

    .hero-card {
        background:
            radial-gradient(circle at top right, rgba(255,255,255,0.20), transparent 28%),
            linear-gradient(135deg, #0f766e 0%, #155e75 52%, #1f4f8c 100%);
        border-radius: 28px;
        padding: 32px;
        color: #f8fffe;
        min-height: 220px;
        box-shadow: 0 24px 45px rgba(21, 94, 89, 0.22);
        position: relative;
        overflow: hidden;
    }

    .hero-card::after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -70px;
        bottom: -95px;
        border-radius: 50%;
        background: rgba(255,255,255,0.10);
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.16);
        font-size: 0.76rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .hero-title {
        font-size: 2.15rem;
        line-height: 1.08;
        font-weight: 800;
        margin: 0 0 14px 0;
        max-width: 580px;
        color: #ffffff;
    }

    .hero-copy {
        margin: 0;
        max-width: 560px;
        color: rgba(248,255,254,0.86);
        font-size: 1rem;
        line-height: 1.7;
    }

    .hero-side-card {
        background: linear-gradient(180deg, #fffdf9 0%, #f7f0e7 100%);
        border-radius: 28px;
        border: 1px solid rgba(192, 132, 87, 0.18);
        padding: 26px 24px;
        box-shadow: var(--shadow-card);
    }

    .hero-side-label {
        color: var(--text-faint);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        font-size: 0.72rem;
        margin-bottom: 10px;
    }

    .hero-side-title {
        font-size: 1.35rem;
        line-height: 1.25;
        font-weight: 800;
        color: var(--text-main);
        margin-bottom: 10px;
    }

    .hero-side-copy {
        color: var(--text-soft);
        line-height: 1.65;
        font-size: 0.96rem;
        margin-bottom: 18px;
    }

    .mini-stat {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 12px 0;
        border-top: 1px solid rgba(72, 56, 43, 0.08);
        color: var(--text-soft);
        font-size: 0.92rem;
    }

    .mini-stat strong {
        color: var(--text-main);
        font-size: 1.02rem;
    }

    .login-container {
        max-width: none;
        margin: 0;
        background: transparent;
        border-radius: 0;
        padding: 0;
        box-shadow: none;
        animation: none;
    }

    .login-header {
        margin-bottom: 26px;
        text-align: left;
    }

    .login-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--text-main);
        line-height: 1.02;
        letter-spacing: -0.04em;
        margin-bottom: 14px;
        background: none;
        -webkit-text-fill-color: initial;
    }

    .login-subtitle {
        color: var(--text-soft);
        font-size: 1rem;
        line-height: 1.7;
        max-width: 520px;
    }

    .login-feature-list {
        display: grid;
        gap: 12px;
        margin-top: 22px;
    }

    .login-feature-item {
        display: flex;
        align-items: center;
        gap: 12px;
        color: var(--text-soft);
        font-size: 0.95rem;
    }

    .login-feature-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--brand) 0%, var(--accent) 100%);
        box-shadow: 0 0 0 6px rgba(15, 118, 110, 0.08);
    }

    .login-form-shell,
    .content-card {
        background: rgba(255, 255, 255, 0.82);
        border-radius: 24px;
        padding: 24px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-card);
    }

    .login-form-shell {
        background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(251,247,241,0.94) 100%);
        padding: 30px;
        position: relative;
        overflow: hidden;
    }

    .login-form-shell::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 5px;
        background: linear-gradient(90deg, var(--brand) 0%, var(--accent) 100%);
    }

    .auth-form-heading {
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--text-main);
        letter-spacing: -0.03em;
        margin-bottom: 8px;
    }

    .auth-form-copy {
        color: var(--text-soft);
        line-height: 1.7;
        margin-bottom: 22px;
    }

    .dashboard-container {
        max-width: 100%;
        margin: 0 auto;
        padding: 0;
        background: transparent;
        border-radius: 0;
        box-shadow: none;
        margin-top: 0;
    }

    .stat-card {
        background: linear-gradient(180deg, #ffffff 0%, #fbf7f1 100%);
        padding: 24px;
        border-radius: 22px;
        min-height: 168px;
        color: var(--text-main);
        box-shadow: var(--shadow-card);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: 1px solid rgba(72, 56, 43, 0.09);
        position: relative;
        overflow: hidden;
    }

    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 34px rgba(63, 46, 32, 0.12);
    }

    .stat-card::before {
        content: "";
        position: absolute;
        inset: 0 auto auto 0;
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, var(--brand) 0%, var(--accent) 100%);
    }

    .stat-number {
        font-size: 2.45rem;
        font-weight: 800;
        margin: 14px 0 8px;
        line-height: 1;
        color: var(--text-main);
    }

    .stat-label {
        font-size: 0.74rem;
        color: var(--text-faint);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
        opacity: 1;
    }

    .stat-copy {
        color: var(--text-soft);
        font-size: 0.92rem;
        line-height: 1.55;
    }

    .section-header {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--text-main);
        margin: 0 0 8px 0;
        letter-spacing: -0.02em;
        border: none;
        padding: 0;
    }

    .section-subtext {
        color: var(--text-soft);
        margin-bottom: 22px;
        line-height: 1.65;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--brand) 0%, var(--brand-deep) 100%);
        color: white;
        border: 1px solid rgba(15, 118, 110, 0.16);
        border-radius: 14px;
        padding: 0.84rem 1.2rem;
        font-weight: 700;
        font-size: 0.96rem;
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
        box-shadow: 0 14px 22px rgba(15, 118, 110, 0.18);
        min-height: 3rem;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.02);
        box-shadow: 0 18px 28px rgba(15, 118, 110, 0.22);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.6);
        padding: 8px;
        border: 1px solid var(--border);
        border-radius: 18px;
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 54px;
        background: transparent;
        border-radius: 14px;
        padding: 12px 20px;
        font-weight: 700;
        color: var(--text-soft);
        border: 1px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f4ee 100%);
        color: var(--text-main);
        border-color: rgba(15, 118, 110, 0.14);
        box-shadow: 0 10px 20px rgba(63, 46, 32, 0.08);
    }

    .stTextInput label, .stSelectbox label, .stFileUploader label {
        color: var(--text-main) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }

    .stTextInput > div > div > input {
        border-radius: 14px;
        border: 1px solid var(--border-strong);
        background: rgba(255, 255, 255, 0.98);
        color: var(--text-main);
        padding: 14px 16px;
        font-size: 0.98rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(15, 118, 110, 0.38);
        box-shadow: 0 0 0 4px rgba(15, 118, 110, 0.10);
    }

    .stSelectbox > div > div {
        border-radius: 14px;
        border: 1px solid var(--border-strong);
        background: rgba(255, 255, 255, 0.98);
    }

    [data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(249,244,236,0.96) 100%);
        border: 1.5px dashed rgba(15, 118, 110, 0.24);
        border-radius: 22px;
        padding: 18px;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(15, 118, 110, 0.46);
        background: linear-gradient(180deg, #ffffff 0%, #f5fbf8 100%);
    }

    .skill-badge {
        display: inline-block;
        background: linear-gradient(180deg, #ffffff 0%, #f4fbf8 100%);
        color: var(--brand-deep);
        padding: 9px 14px;
        border-radius: 999px;
        margin: 0 8px 8px 0;
        font-weight: 700;
        font-size: 0.84rem;
        border: 1px solid rgba(15, 118, 110, 0.16);
        box-shadow: none;
    }

    .skill-badge-missing {
        color: var(--danger);
        background: linear-gradient(180deg, #fff6f4 0%, var(--danger-soft) 100%);
        border-color: rgba(181, 77, 66, 0.16);
    }

    .success-box, .warning-box, .info-box {
        padding: 16px 18px;
        border-radius: 16px;
        margin: 14px 0;
        font-weight: 700;
        border: 1px solid transparent;
        box-shadow: none;
    }

    .success-box {
        color: var(--success);
        background: linear-gradient(180deg, #ffffff 0%, var(--success-soft) 100%);
        border-color: rgba(31, 122, 82, 0.15);
    }

    .warning-box {
        color: var(--warning);
        background: linear-gradient(180deg, #ffffff 0%, var(--warning-soft) 100%);
        border-color: rgba(154, 103, 0, 0.16);
    }

    .info-box {
        color: var(--info);
        background: linear-gradient(180deg, #ffffff 0%, var(--info-soft) 100%);
        border-color: rgba(41, 92, 155, 0.16);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--brand) 0%, var(--accent) 100%);
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 20px;
        background: rgba(255,255,255,0.84);
        box-shadow: var(--shadow-card);
        overflow: hidden;
    }

    .streamlit-expanderHeader {
        background: transparent;
        border-radius: 10px;
        font-weight: 700;
        color: var(--text-main);
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, #faf6ef 100%);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 12px 16px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-soft);
        font-weight: 700;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--brand-deep);
    }

    .sign-out-btn button {
        background: linear-gradient(180deg, #ffffff 0%, #f6f2ec 100%) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-strong) !important;
        padding: 0.82rem 1rem !important;
        font-size: 0.95rem !important;
        box-shadow: none !important;
    }

    .sign-out-btn button:hover {
        background: #ffffff !important;
        color: var(--brand-deep) !important;
        border-color: rgba(15, 118, 110, 0.24) !important;
    }

    .chart-card-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--text-main);
        margin-bottom: 14px;
    }

    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.84);
        border: 1px solid var(--border);
        border-radius: 18px;
        overflow: hidden;
    }

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(72, 56, 43, 0.14) 15%, rgba(72, 56, 43, 0.14) 85%, transparent 100%);
        margin: 28px 0;
    }

    @media (max-width: 992px) {
        .hero-grid {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .page-shell, .login-form-shell, .content-card {
            padding: 18px;
            border-radius: 22px;
        }

        .auth-stage {
            padding: 24px;
        }

        .auth-stage-title {
            font-size: 2.35rem;
        }

        .hero-card {
            padding: 24px;
            min-height: unset;
        }

        .hero-title {
            font-size: 1.8rem;
        }

        .login-title {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'auth'
    if 'auth_service' not in st.session_state:
        try:
            init_supabase()
            st.session_state.auth_service = AuthService()
            st.session_state.resume_repo = ResumeRepository()
            st.session_state.skill_repo = SkillRepository()
        except Exception as e:
            st.error(f"Database connection error: {e}")
            st.stop()

def show_auth_page():
    """Show modern authentication page"""
    # Center the login card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div class="login-title"> AI Resume Analyzer Pro</div>
                <div class="login-subtitle">Advanced Resume Analysis & Skill Gap Detection</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Sign Up"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signin_form", clear_on_submit=False):
                email = st.text_input("📧 Email Address", placeholder="your.email@example.com", key="signin_email")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="signin_password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    if email and password:
                        with st.spinner("Signing in..."):
                            result = st.session_state.auth_service.sign_in(email, password)
                            if result['success']:
                                st.session_state.authenticated = True
                                st.session_state.user = result['user']
                                st.session_state.page = 'dashboard'
                                st.success("✅ " + result['message'])
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ " + result['message'])
                    else:
                        st.warning("⚠️ Please fill in all fields")
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signup_form", clear_on_submit=False):
                full_name = st.text_input("👤 Full Name", placeholder="Your Name", key="signup_name")
                email = st.text_input("📧 Email Address", placeholder="your.email@example.com", key="signup_email")
                password = st.text_input("🔒 Password", type="password", placeholder="Choose a strong password", key="signup_password")
                password_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password", key="signup_confirm")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if all([full_name, email, password, password_confirm]):
                        if password == password_confirm:
                            if len(password) >= 6:
                                with st.spinner("Creating account..."):
                                    result = st.session_state.auth_service.sign_up(email, password, full_name)
                                    if result['success']:
                                        st.success("✅ " + result['message'])
                                        st.info("💡 Please use the Sign In tab to access your account")
                                    else:
                                        st.error("❌ " + result['message'])
                            else:
                                st.error("❌ Password must be at least 6 characters")
                        else:
                            st.error("❌ Passwords do not match!")
                    else:
                        st.warning("⚠️ Please fill in all fields")

def show_dashboard():
    """Show modern dashboard"""
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    
    # Header with sign out
    col1, col2 = st.columns([4, 1])
    with col1:
        user_name = st.session_state.user.email.split('@')[0].title() if st.session_state.user else "User"
        st.markdown(f"""
        <div class="welcome-banner">
            <h2>👋 Welcome back, {user_name}!</h2>
            <p>Track your resume analysis, match scores, and skill development journey</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sign-out-btn">', unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.auth_service.sign_out()
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = 'auth'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Statistics Cards
    stats = st.session_state.resume_repo.get_resume_statistics(st.session_state.user.id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">📁 Total Resumes</div>
            <div class="stat-number">{stats['total_resumes']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">📊 Analyses Done</div>
            <div class="stat-number">{stats['total_analyses']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">🎯 Avg Match</div>
            <div class="stat-number">{stats['average_match_score']}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">💡 Unique Skills</div>
            <div class="stat-number">{stats['unique_skills']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Analyze", "📁 My Resumes", "📊 Analytics"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_my_resumes()
    
    with tab3:
        show_analytics()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_upload_section():
    """Upload and analyze resume section"""
    st.markdown('<div class="section-header">📤 Upload Your Resume</div>', unsafe_allow_html=True)
    st.markdown("**Supports PDF and DOCX files. Scanned documents automatically processed with OCR.**")
    
    uploaded = st.file_uploader(
        "Choose your resume file",
        type=["pdf", "docx"],
        help="Upload your resume for AI-powered analysis"
    )
    
    if uploaded:
        ts = time.strftime("%Y%m%d-%H%M%S")
        safe_name = uploaded.name.replace(" ", "_")
        saved_path = UPLOADS_DIR / f"{ts}__{safe_name}"
        
        with saved_path.open("wb") as f:
            f.write(uploaded.getbuffer())
        
        st.markdown('<div class="success-box">✅ Resume uploaded successfully! Analyzing now...</div>', unsafe_allow_html=True)
        
        with st.spinner("🔍 Analyzing your resume with AI..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
            
            roles_map = st.session_state.skill_repo.get_all_job_roles()
            result = analyze_resume(str(saved_path))
            
            resume_record = st.session_state.resume_repo.save_resume(
                user_id=st.session_state.user.id,
                filename=uploaded.name,
                file_type=uploaded.type.split('/')[-1],
                raw_text="",
                parsed_data=result["parsed"],
                file_size=uploaded.size
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="section-header">🧩 Extracted Information</div>', unsafe_allow_html=True)
            
            skills = result["parsed"].get("skills", [])
            edu = result["parsed"].get("education", [])
            exp = result["parsed"].get("experience", [])
            
            st.markdown("**💡 Skills Found:**")
            if skills:
                skills_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' 
                                       for skill in sorted(skills)[:20]])
                st.markdown(skills_html, unsafe_allow_html=True)
                if len(skills) > 20:
                    st.info(f"+ {len(skills) - 20} more skills")
            else:
                st.markdown('<div class="warning-box">⚠️ No skills detected</div>', unsafe_allow_html=True)
            
            st.markdown("<br>**🎓 Education:**")
            if edu:
                for e in edu[:3]:
                    st.write(f"• {e}")
            else:
                st.write("—")
            
            st.markdown("<br>**💼 Experience:**")
            if exp:
                for e in exp[:3]:
                    st.write(f"• {e}")
            else:
                st.write("—")
        
        with col2:
            st.markdown('<div class="section-header"> Job Role Analysis</div>', unsafe_allow_html=True)
            
            preds = result.get("predictions", [])
            if preds:
                st.markdown("**Top Matching Roles:**")
                for role, score in preds[:3]:
                    st.markdown(f"**{role}** — {score:.1f}%")
                    st.progress(score / 100)
                    st.markdown("<br>", unsafe_allow_html=True)
                
                default_role = preds[0][0]
            else:
                default_role = list(roles_map.keys())[0] if roles_map else "Junior Data Scientist"
            
            st.markdown("<br>", unsafe_allow_html=True)
            chosen = st.selectbox(
                "🎯 Select Target Role for Detailed Analysis",
                options=list(roles_map.keys()),
                index=list(roles_map.keys()).index(default_role) if default_role in roles_map else 0
            )
            
            if chosen != result["chosen_role"]:
                with st.spinner("Recalculating..."):
                    result = analyze_resume(str(saved_path), chosen_role=chosen)
            
            matched = result["gap"].get("matched", [])
            missing = result["gap"].get("missing", [])
            match_score = result.get('match_score', 0)
            
            st.markdown(f"<br>**Match Score: {match_score:.1f}%**", unsafe_allow_html=True)
            st.progress(match_score / 100)
            
            if resume_record:
                st.session_state.resume_repo.save_skill_gap_analysis(
                    user_id=st.session_state.user.id,
                    resume_id=resume_record['id'],
                    target_role=chosen,
                    matched_skills=matched,
                    missing_skills=missing,
                    match_score=match_score
                )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header">✅ Matched Skills</div>', unsafe_allow_html=True)
            if matched:
                matched_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' 
                                        for skill in sorted(matched)])
                st.markdown(matched_html, unsafe_allow_html=True)
            else:
                st.write("—")
        
        with col2:
            st.markdown('<div class="section-header">❌ Skills to Learn</div>', unsafe_allow_html=True)
            if missing:
                missing_html = " ".join([f'<span class="skill-badge skill-badge-missing">{skill.title()}</span>' 
                                        for skill in sorted(missing)])
                st.markdown(missing_html, unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box">🎉 Perfect match! No skills missing!</div>', unsafe_allow_html=True)
        
        if saved_path.exists():
            saved_path.unlink()

def show_my_resumes():
    """Show user's uploaded resumes"""
    st.markdown('<div class="section-header">📁 Your Resume History</div>', unsafe_allow_html=True)
    
    resumes = st.session_state.resume_repo.get_user_resumes(st.session_state.user.id)
    
    if not resumes:
        st.markdown('<div class="info-box">📭 No resumes yet. Upload your first resume in the "Upload & Analyze" tab!</div>', unsafe_allow_html=True)
        return
    
    for resume in resumes:
        with st.expander(f"📄 {resume['filename']} — {resume['upload_date'][:10]}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📦 File Size", f"{resume['file_size'] / 1024:.1f} KB")
            
            with col2:
                skills_count = len(json.loads(resume['parsed_skills'])) if isinstance(resume['parsed_skills'], str) else len(resume['parsed_skills'])
                st.metric("💡 Skills", skills_count)
            
            with col3:
                st.metric("📝 Type", resume['file_type'].upper())
            
            skills = json.loads(resume['parsed_skills']) if isinstance(resume['parsed_skills'], str) else resume['parsed_skills']
            if skills:
                st.markdown("<br>**Skills:**", unsafe_allow_html=True)
                skills_html = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in skills[:15]])
                st.markdown(skills_html, unsafe_allow_html=True)
            
            if st.button(f"🗑️ Delete Resume", key=f"del_{resume['id']}", use_container_width=True):
                st.session_state.resume_repo.delete_resume(resume['id'], st.session_state.user.id)
                st.success("✅ Resume deleted!")
                st.rerun()

def show_analytics():
    """Show analytics and visualizations"""
    st.markdown('<div class="section-header">📊 Your Analytics Dashboard</div>', unsafe_allow_html=True)
    
    analyses = st.session_state.resume_repo.get_user_analyses(st.session_state.user.id, limit=50)
    
    if not analyses:
        st.markdown('<div class="info-box">📊 No analyses yet. Complete your first resume analysis to see insights!</div>', unsafe_allow_html=True)
        return
    
    df = pd.DataFrame(analyses)
    df['analysis_date'] = pd.to_datetime(df['analysis_date'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Match Score Progress**")
        fig = px.line(
            df,
            x='analysis_date',
            y='match_score',
            title='Your Improvement Over Time',
            labels={'match_score': 'Match Score (%)', 'analysis_date': 'Date'}
        )
        fig.update_traces(line_color='#667eea', line_width=3)
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Poppins")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**🎯 Roles Analyzed**")
        role_counts = df['target_role'].value_counts()
        fig = px.pie(
            values=role_counts.values,
            names=role_counts.index,
            title='Distribution of Analyzed Roles'
        )
        fig.update_traces(marker=dict(colors=px.colors.sequential.Purples))
        fig.update_layout(
            paper_bgcolor='white',
            font=dict(family="Poppins")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>**🏆 Top Performing Analyses**", unsafe_allow_html=True)
    top_analyses = df.nlargest(5, 'match_score')[['target_role', 'match_score', 'analysis_date']]
    top_analyses['analysis_date'] = top_analyses['analysis_date'].dt.strftime('%Y-%m-%d')
    top_analyses.columns = ['Role', 'Match Score (%)', 'Date']
    st.dataframe(top_analyses, use_container_width=True, hide_index=True)

# ============================================
# 🌐 CUSTOM FOOTER SECTION (Modern Gradient)
# ============================================
def show_footer():
    st.markdown("""
    <style>
        .footer {
            position: relative;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 25px 0;
            margin-top: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
            box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
        }
        .footer a {
            color: white;
            text-decoration: none;
            font-weight: 600;
            margin: 0 12px;
            transition: color 0.3s ease;
        }
        .footer a:hover {
            color: #ffd700;
        }
        .footer p {
            margin: 5px 0 0 0;
            font-size: 0.95rem;
            opacity: 0.9;
        }
        .social-icons {
            margin-top: 10px;
        }
        .social-icons a {
            margin: 0 8px;
            display: inline-block;
            font-size: 1.2rem;
        }
    </style>

    <div class="footer">
        <p> Built by <strong>Samir Khanal, Sijan Poudel and Ishan Chalise</strong></p>
        <div class="social-icons">
            <a href="https://github.com/samir-khanal" target="_blank">GitHub</a> |
            <a href="https://www.linkedin.com/in/samir-khanal7/" target="_blank">🔗 LinkedIn</a> |
        </div>
        <p>© 2025 AI Resume Analyzer Pro — All Rights Reserved.</p>
    </div>
    """, unsafe_allow_html=True)

def show_auth_page():
    """Show redesigned authentication page"""
    left, right = st.columns([1.08, 0.92], gap="large")

    with left:
        st.markdown("""
        <div class="page-shell">
            <div class="auth-stage">
                <div class="auth-stage-inner">
                    <div class="auth-stage-kicker">Resume Intelligence Platform</div>
                    <div class="auth-stage-title">Build a resume workflow that actually feels premium.</div>
                    <div class="auth-stage-copy">
                        Upload resumes, compare role fit, and track improvement inside a workspace that looks polished enough for a real product instead of a classroom demo.
                    </div>
                    <div class="auth-highlight-grid">
                        <div class="auth-highlight-card">
                            <div class="auth-highlight-value">Role Fit</div>
                            <div class="auth-highlight-label">Targeted match scoring with skill-gap visibility for every upload.</div>
                        </div>
                        <div class="auth-highlight-card">
                            <div class="auth-highlight-value">History</div>
                            <div class="auth-highlight-label">Past resumes and analysis snapshots stay easy to revisit.</div>
                        </div>
                    </div>
                    <div class="login-feature-list">
                        <div class="login-feature-item"><span class="login-feature-dot"></span><span>Role-fit scoring with targeted skill-gap analysis</span></div>
                        <div class="login-feature-item"><span class="login-feature-dot"></span><span>Resume history, analytics, and reusable progress tracking</span></div>
                        <div class="login-feature-item"><span class="login-feature-dot"></span><span>Fast upload flow for PDF and DOCX resumes</span></div>
                    </div>
                    <div class="auth-proof">
                        <span class="auth-proof-chip">PDF + DOCX Ready</span>
                        <span class="auth-proof-chip">Skill Gap Detection</span>
                        <span class="auth-proof-chip">Analytics Dashboard</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="auth-form-heading">Welcome in</div>
        <div class="auth-form-copy">Access your analysis workspace or create a new account to start building a more polished resume pipeline.</div>
        """, unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            with st.form("signin_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="your.email@example.com", key="signin_email")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="signin_password")
                submit = st.form_submit_button("Sign In", use_container_width=True)

                if submit:
                    if email and password:
                        with st.spinner("Signing in..."):
                            result = st.session_state.auth_service.sign_in(email, password)
                            if result['success']:
                                st.session_state.authenticated = True
                                st.session_state.user = result['user']
                                st.session_state.page = 'dashboard'
                                st.success("Success: " + result['message'])
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Sign in failed: " + result['message'])
                    else:
                        st.warning("Please fill in all fields")

        with tab2:
            with st.form("signup_form", clear_on_submit=False):
                full_name = st.text_input("Full Name", placeholder="Your name", key="signup_name")
                email = st.text_input("Email Address", placeholder="your.email@example.com", key="signup_email")
                password = st.text_input("Password", type="password", placeholder="Choose a strong password", key="signup_password")
                password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="signup_confirm")
                submit = st.form_submit_button("Create Account", use_container_width=True)

                if submit:
                    if all([full_name, email, password, password_confirm]):
                        if password == password_confirm:
                            if len(password) >= 6:
                                with st.spinner("Creating account..."):
                                    result = st.session_state.auth_service.sign_up(email, password, full_name)
                                    if result['success']:
                                        st.success("Success: " + result['message'])
                                        st.info("Next step: use the Sign In tab to access your account")
                                    else:
                                        st.error("Account creation failed: " + result['message'])
                            else:
                                st.error("Password must be at least 6 characters")
                        else:
                            st.error("Passwords do not match")
                    else:
                        st.warning("Please fill in all fields")

def show_dashboard():
    """Show redesigned dashboard"""
    st.markdown('<div class="dashboard-container"><div class="page-shell dashboard-shell">', unsafe_allow_html=True)

    user_name = st.session_state.user.email.split('@')[0].title() if st.session_state.user else "User"
    stats = st.session_state.resume_repo.get_resume_statistics(st.session_state.user.id)

    hero_col, side_col = st.columns([1.55, 0.85], gap="large")
    with hero_col:
        st.markdown(f"""
        <div class="hero-card">
            <div class="hero-kicker">Professional Workspace</div>
            <div class="hero-title">Welcome back, {user_name}.</div>
            <p class="hero-copy">
                Review uploaded resumes, track match quality over time, and uncover the next skills that will improve alignment for your target roles.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with side_col:
        st.markdown(f"""
        <div class="hero-side-card">
            <div class="hero-side-label">Snapshot</div>
            <div class="hero-side-title">Your resume lab is active.</div>
            <div class="hero-side-copy">Everything below stays connected to the same upload, analytics, and history workflows you already have.</div>
            <div class="mini-stat"><span>Latest average match</span><strong>{stats['average_match_score']}%</strong></div>
            <div class="mini-stat"><span>Total analyses stored</span><strong>{stats['total_analyses']}</strong></div>
            <div class="mini-stat"><span>Distinct skills captured</span><strong>{stats['unique_skills']}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="sign-out-btn">', unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.auth_service.sign_out()
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = 'auth'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Resumes</div>
            <div class="stat-number">{stats['total_resumes']}</div>
            <div class="stat-copy">Stored resume submissions available for review and comparison.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Analyses Done</div>
            <div class="stat-number">{stats['total_analyses']}</div>
            <div class="stat-copy">Completed role-fit evaluations captured in your workspace.</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Average Match</div>
            <div class="stat-number">{stats['average_match_score']}%</div>
            <div class="stat-copy">Current average fit score across your saved analyses.</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Unique Skills</div>
            <div class="stat-number">{stats['unique_skills']}</div>
            <div class="stat-copy">Distinct skill tags extracted from your uploaded resumes.</div>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Upload & Analyze", "My Resumes", "Analytics"])

    with tab1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        show_upload_section()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        show_my_resumes()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        show_analytics()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

def show_upload_section():
    """Upload and analyze resume section"""
    st.markdown('<div class="section-header">Upload Your Resume</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtext">Upload a PDF or DOCX resume to extract skills, review likely roles, and measure role fit without changing the existing analysis workflow.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Choose your resume file",
        type=["pdf", "docx"],
        help="Upload your resume for AI-powered analysis"
    )

    if uploaded:
        ts = time.strftime("%Y%m%d-%H%M%S")
        safe_name = uploaded.name.replace(" ", "_")
        saved_path = UPLOADS_DIR / f"{ts}__{safe_name}"

        with saved_path.open("wb") as f:
            f.write(uploaded.getbuffer())

        st.markdown('<div class="success-box">Resume uploaded successfully. Analysis is starting now.</div>', unsafe_allow_html=True)

        with st.spinner("Analyzing your resume with AI..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            roles_map = st.session_state.skill_repo.get_all_job_roles()
            try:
                result = analyze_resume(str(saved_path))
            except StopIteration:
                st.markdown('<div class="warning-box">Resume parsing hit an internal iterator error. Showing a safe fallback result instead.</div>', unsafe_allow_html=True)
                result = {
                    "parsed": {"skills": [], "education": [], "experience": []},
                    "predictions": [],
                    "chosen_role": "Unassigned Role",
                    "required_skills": [],
                    "gap": {"matched": [], "missing": []},
                    "match_score": 0.0,
                }
            except Exception as e:
                st.markdown(f'<div class="warning-box">Analysis failed: {str(e)}</div>', unsafe_allow_html=True)
                result = {
                    "parsed": {"skills": [], "education": [], "experience": []},
                    "predictions": [],
                    "chosen_role": "Unassigned Role",
                    "required_skills": [],
                    "gap": {"matched": [], "missing": []},
                    "match_score": 0.0,
                }

            resume_record = st.session_state.resume_repo.save_resume(
                user_id=st.session_state.user.id,
                filename=uploaded.name,
                file_type=uploaded.type.split('/')[-1],
                raw_text="",
                parsed_data=result["parsed"],
                file_size=uploaded.size
            )

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown('<div class="section-header">Extracted Information</div>', unsafe_allow_html=True)

            skills = result["parsed"].get("skills", [])
            edu = result["parsed"].get("education", [])
            exp = result["parsed"].get("experience", [])

            st.markdown("**Skills Found**")
            if skills:
                skills_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' for skill in sorted(skills)[:20]])
                st.markdown(skills_html, unsafe_allow_html=True)
                if len(skills) > 20:
                    st.info(f"+ {len(skills) - 20} more skills")
            else:
                st.markdown('<div class="warning-box">No skills were detected in this resume.</div>', unsafe_allow_html=True)

            st.markdown("<br>**Education**", unsafe_allow_html=True)
            if edu:
                for e in edu[:3]:
                    st.write(f"- {e}")
            else:
                st.caption("No education details were extracted from this resume.")

            st.markdown("<br>**Experience**", unsafe_allow_html=True)
            if exp:
                for e in exp[:3]:
                    st.write(f"- {e}")
            else:
                st.caption("No experience details were extracted from this resume.")

        with col2:
            st.markdown('<div class="section-header">Role Analysis</div>', unsafe_allow_html=True)

            preds = result.get("predictions", [])
            if preds:
                st.markdown("**Top Matching Roles**")
                for role, score in preds[:3]:
                    st.markdown(f"**{role}** - {score:.1f}%")
                    st.progress(score / 100)
                    st.markdown("<br>", unsafe_allow_html=True)

                default_role = preds[0][0]
            else:
                default_role = list(roles_map.keys())[0] if roles_map else "Junior Data Scientist"

            role_options = list(roles_map.keys()) or [role for role, _ in preds]
            if role_options:
                chosen = st.selectbox(
                    "Select Target Role for Detailed Analysis",
                    options=role_options,
                    index=role_options.index(default_role) if default_role in role_options else 0
                )

                if chosen != result["chosen_role"]:
                    with st.spinner("Recalculating..."):
                        result = analyze_resume(str(saved_path), chosen_role=chosen)
            else:
                chosen = result.get("chosen_role") or "Unassigned Role"
                st.markdown('<div class="warning-box">No job roles are configured in the database yet. Showing resume extraction only.</div>', unsafe_allow_html=True)

            matched = result["gap"].get("matched", [])
            missing = result["gap"].get("missing", [])
            match_score = result.get('match_score', 0)

            st.markdown(f"<br>**Match Score: {match_score:.1f}%**", unsafe_allow_html=True)
            st.progress(match_score / 100)

            if resume_record:
                st.session_state.resume_repo.save_skill_gap_analysis(
                    user_id=st.session_state.user.id,
                    resume_id=resume_record['id'],
                    target_role=chosen,
                    matched_skills=matched,
                    missing_skills=missing,
                    match_score=match_score
                )

        st.markdown("---")

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown('<div class="section-header">Matched Skills</div>', unsafe_allow_html=True)
            if matched:
                matched_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' for skill in sorted(matched)])
                st.markdown(matched_html, unsafe_allow_html=True)
            else:
                st.caption("No matched skills yet for the selected role.")

        with col2:
            st.markdown('<div class="section-header">Skills to Learn</div>', unsafe_allow_html=True)
            if missing:
                missing_html = " ".join([f'<span class="skill-badge skill-badge-missing">{skill.title()}</span>' for skill in sorted(missing)])
                st.markdown(missing_html, unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box">Perfect match. No missing skills were identified.</div>', unsafe_allow_html=True)

        if saved_path.exists():
            saved_path.unlink()

def show_my_resumes():
    """Show user's uploaded resumes"""
    st.markdown('<div class="section-header">Your Resume History</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtext">Review previously uploaded resumes, inspect extracted skills, and remove outdated entries when needed.</div>', unsafe_allow_html=True)

    resumes = st.session_state.resume_repo.get_user_resumes(st.session_state.user.id)

    if not resumes:
        st.markdown('<div class="info-box">No resumes yet. Upload your first resume in the Upload & Analyze tab.</div>', unsafe_allow_html=True)
        return

    for resume in resumes:
        with st.expander(f"{resume['filename']} - {resume['upload_date'][:10]}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("File Size", f"{resume['file_size'] / 1024:.1f} KB")

            with col2:
                skills_count = len(json.loads(resume['parsed_skills'])) if isinstance(resume['parsed_skills'], str) else len(resume['parsed_skills'])
                st.metric("Skills", skills_count)

            with col3:
                st.metric("Type", resume['file_type'].upper())

            skills = json.loads(resume['parsed_skills']) if isinstance(resume['parsed_skills'], str) else resume['parsed_skills']
            if skills:
                st.markdown("<br>**Skills**", unsafe_allow_html=True)
                skills_html = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in skills[:15]])
                st.markdown(skills_html, unsafe_allow_html=True)

            if st.button("Delete Resume", key=f"del_{resume['id']}", use_container_width=True):
                deleted = st.session_state.resume_repo.delete_resume(resume['id'], st.session_state.user.id)
                if deleted:
                    st.success("Resume deleted.")
                    st.rerun()
                else:
                    st.error("Could not delete this resume. Please try again.")

def show_analytics():
    """Show analytics and visualizations"""
    st.markdown('<div class="section-header">Your Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtext">Monitor match trends, see which roles you analyze most often, and surface your strongest results at a glance.</div>', unsafe_allow_html=True)

    analyses = st.session_state.resume_repo.get_user_analyses(st.session_state.user.id, limit=50)

    if not analyses:
        st.markdown('<div class="info-box">No analyses yet. Complete your first resume analysis to unlock analytics.</div>', unsafe_allow_html=True)
        return

    df = pd.DataFrame(analyses)
    df['analysis_date'] = pd.to_datetime(df['analysis_date'])

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="chart-card-title">Match Score Progress</div>', unsafe_allow_html=True)
        fig = px.line(
            df,
            x='analysis_date',
            y='match_score',
            title='Your Improvement Over Time',
            labels={'match_score': 'Match Score (%)', 'analysis_date': 'Date'}
        )
        fig.update_traces(line_color='#0f766e', line_width=3)
        fig.update_layout(
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='rgba(255,255,255,0)',
            font=dict(family="Manrope", color="#1d1a17"),
            margin=dict(l=10, r=10, t=60, b=10),
            title_font=dict(size=18),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='rgba(29, 26, 23, 0.08)')
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="chart-card-title">Roles Analyzed</div>', unsafe_allow_html=True)
        role_counts = df['target_role'].value_counts()
        fig = px.pie(
            values=role_counts.values,
            names=role_counts.index,
            title='Distribution of Analyzed Roles'
        )
        fig.update_traces(marker=dict(colors=['#0f766e', '#c08457', '#295c9b', '#7c6957', '#6aa88f', '#d8b18e']))
        fig.update_layout(
            paper_bgcolor='rgba(255,255,255,0)',
            font=dict(family="Manrope", color="#1d1a17"),
            margin=dict(l=10, r=10, t=60, b=10),
            title_font=dict(size=18)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="chart-card-title">Top Performing Analyses</div>', unsafe_allow_html=True)
    top_analyses = df.nlargest(5, 'match_score')[['target_role', 'match_score', 'analysis_date']]
    top_analyses['analysis_date'] = top_analyses['analysis_date'].dt.strftime('%Y-%m-%d')
    top_analyses.columns = ['Role', 'Match Score (%)', 'Date']
    st.dataframe(top_analyses, use_container_width=True, hide_index=True)

def show_footer():
    st.markdown("""
    <style>
        .footer {
            width: 100%;
            margin-top: 40px;
            padding: 24px 28px;
            background: rgba(255,255,255,0.75);
            border: 1px solid rgba(72, 56, 43, 0.10);
            border-radius: 24px 24px 0 0;
            box-shadow: 0 -8px 24px rgba(63, 46, 32, 0.05);
            text-align: center;
            backdrop-filter: blur(14px);
        }

        .footer a {
            color: #115e59;
            text-decoration: none;
            font-weight: 700;
            margin: 0 10px;
        }

        .footer a:hover {
            color: #0f766e;
        }

        .footer p {
            margin: 6px 0;
            color: #6f665d;
        }
    </style>

    <div class="footer">
        <p><strong>Built by Samir Khanal, Sijan Poudel and Ishan Chalise</strong></p>
        <p>
            <a href="https://github.com/samir-khanal" target="_blank">GitHub</a>
            <a href="https://www.linkedin.com/in/samir-khanal7/" target="_blank">LinkedIn</a>
        </p>
        <p>AI Resume Analyzer Pro</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application logic"""
    init_session_state()

    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()

show_footer()
