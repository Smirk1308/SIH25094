"""
Streamlit Web Application for J&K EduSetu - "Your Bridge to Education & Opportunities".
High-End Competitive UI with:
1. 🎨 Modern Glassmorphism & Plus Jakarta Sans typography.
2. ⚡ 2G Offline & Instant Query Engine (<10ms latency, zero API calls).
3. 🌐 AI Cloud Mode with Gemini & Groq & ChromaDB vector search.
4. 🤖 Smart Auto-Detect with Zero-Downtime Fallback.
5. 🎯 Smart Scholarship Eligibility Engine (7-field profile matching).
6. 🗂️ Interactive Category Prompt Explorer (Scholarships, Medical, Engineering, Careers).
7. 🏫 College Explorer with seat matrix & district-level filtering.
8. 💼 Job Explorer with skill-to-career matching & exam prep plans.
9. 🎤 AI Mock Interview Simulator with rubric scoring.
10. 📄 Resume Analyzer with section extraction & scoring.
11. 📊 Institutional Admin Portal with dropout risk analytics.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from rag_engine import RAGEngine, DEFAULT_GROQ_MODEL, DOCS_DIR, CHROMA_DIR
from offline_engine import offline_engine, get_2g_response
from error_handler import render_error_card, ErrorDiagnostic

# --- Advanced Feature Modules ---
from college_data import (
    search_colleges, get_seat_matrix, get_colleges_by_district,
    get_all_districts, get_all_college_types, get_cutoff_comparison,
    render_college_card, get_college_by_id, get_colleges_map_data
)
from scholarship_engine import check_eligibility, get_deadline_calendar, render_eligibility_report, get_documents_checklist, render_scholarship_card, search_scholarships
from job_intelligence import search_jobs, match_skills_to_careers, get_exam_preparation_plan, get_all_boards, get_all_skills, render_job_card, render_skill_gap_report, get_job_by_id
from mock_interview import get_all_templates, start_interview, get_next_question, submit_answer, generate_interview_report, get_interview_progress, evaluate_answer
from resume_analyzer import extract_text_from_pdf, analyze_resume, render_resume_report, get_available_target_roles, get_ai_review, compare_to_job_requirements
from student_analytics import simulate_demo_cohort, get_cohort_analytics, calculate_risk_score, generate_intervention_plan, get_priority_alerts, get_student_summary, export_cohort_report, search_students

# Load environment variables (fallback support)
load_dotenv()

# ==========================================
# TRILINGUAL LOCALIZATION (English / हिंदी / اردو)
# ==========================================
TRANSLATIONS = {
    "English": {
        "tagline": "Your Bridge to Education & Opportunities",
        "chat_placeholder": "Ask about college admissions, PMSSS, scholarships, cutoffs, or careers...",
        "explore_heading": "💡 Quick Career & Scholarship Topics",
        "btn_ask": "Ask AI Advisor",
        "lang_badge": "🌐 English Active",
        "system_instruction": "Answer in clear English.",
        "prompts": [
            ("🎓 PMSSS J&K Guide", "What are the eligibility and stipend details for PMSSS J&K Scholarship?"),
            ("🏥 Medical Cutoffs", "What are the NEET UG cutoff marks for GMC Srinagar and GMC Jammu?"),
            ("🏛️ NIT Srinagar", "What are the JEE Main cutoffs and branches for NIT Srinagar Home State Quota?"),
            ("💼 JKSSB Recruitment", "What government job recruitments are conducted by JKSSB in J&K?"),
        ]
    },
    "हिंदी (Hindi)": {
        "tagline": "शिक्षा और अवसरों का आपका सेतु",
        "chat_placeholder": "कॉलेज प्रवेश, PMSSS, छात्रवृत्ति, कटऑफ या करियर के बारे में पूछें...",
        "explore_heading": "💡 त्वरित विषय (Quick Topics)",
        "btn_ask": "सलाहकार से पूछें",
        "lang_badge": "🌐 हिंदी सक्रिय",
        "system_instruction": "कृपया उत्तर हिंदी (Hindi) में सरल और स्पष्ट भाषा में दें।",
        "prompts": [
            ("🎓 PMSSS छात्रवृत्ति", "PMSSS J&K छात्रवृत्ति की पात्रता और ₹1 लाख वजीफे का विवरण क्या है?"),
            ("🏥 GMC नीट कटऑफ", "GMC श्रीनगर और GMC जम्मू के लिए NEET UG कटऑफ क्या है?"),
            ("🏛️ NIT श्रीनगर कटऑफ", "NIT श्रीनगर होम स्टेट कोटा के लिए JEE Main कटऑफ क्या है?"),
            ("💼 JKSSB सरकारी भर्तियां", "J&K में JKSSB द्वारा कौन-सी सरकारी भर्तियां आयोजित की जाती हैं?"),
        ]
    },
    "اردو (Urdu)": {
        "tagline": "تعلیم اور مواقع کا آپ کا پُل",
        "chat_placeholder": "داخلہ، وظائف، پی ایم ایس ایس ایس، یا کیریئر کے بارے میں پوچھیں...",
        "explore_heading": "💡 اہم موضوعات (Important Topics)",
        "btn_ask": "مشیر سے پوچھیں",
        "lang_badge": "🌐 اردو فعال",
        "system_instruction": "براہ کرم اردو (Urdu) میں آسان اور واضح الفاظ میں جواب دیں۔",
        "prompts": [
            ("🎓 PMSSS وظیفہ", "PMSSS J&K اسکالرشپ کی اہلیت اور وظیفے کی تفصیلات کیا ہیں؟"),
            ("🏥 GMC میڈیکل کٹ آف", "GMC سری نگر اور GMC جموں کے لیے NEET کے کٹ آف نمبرات کیا ہیں؟"),
            ("🏛️ NIT سری نگر کٹ آف", "NIT سری نگر ہوم اسٹیٹ کوٹہ کے لیے JEE کٹ آف کیا ہے؟"),
            ("💼 JKSSB اسامیاں", "جموں و کشمیر میں JKSSB کی کون سی نوکریاں دستیاب ہیں؟"),
        ]
    }
}


# Retrieve GROQ_API_KEY securely from st.secrets or environment
def get_groq_api_key() -> str:
    try:
        if "GROQ_API_KEY" in st.secrets:
            return str(st.secrets["GROQ_API_KEY"]).strip()
        if "groq_api_key" in st.secrets:
            return str(st.secrets["groq_api_key"]).strip()
        for val in st.secrets.values():
            if isinstance(val, dict):
                if "GROQ_API_KEY" in val:
                    return str(val["GROQ_API_KEY"]).strip()
                if "groq_api_key" in val:
                    return str(val["groq_api_key"]).strip()
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", os.getenv("groq_api_key", "")).strip()

# Retrieve GOOGLE_API_KEY securely from st.secrets or environment
def get_google_api_key() -> str:
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return str(st.secrets["GOOGLE_API_KEY"]).strip()
        if "google_api_key" in st.secrets:
            return str(st.secrets["google_api_key"]).strip()
        for val in st.secrets.values():
            if isinstance(val, dict):
                if "GOOGLE_API_KEY" in val:
                    return str(val["GOOGLE_API_KEY"]).strip()
                if "google_api_key" in val:
                    return str(val["google_api_key"]).strip()
    except Exception:
        pass
    return os.getenv("GOOGLE_API_KEY", os.getenv("google_api_key", "")).strip()

groq_api_key = get_groq_api_key()
google_api_key = get_google_api_key()
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

def get_best_groq_model(client):
    try:
        models = client.models.list().data
        chat_models = [
            m for m in models
            if not any(x in m.id.lower()
               for x in ["whisper", "guard", "vision", "tool"])
        ]
        chat_models.sort(key=lambda m: m.created, reverse=True)
        return chat_models[0].id if chat_models else "openai/gpt-oss-20b"
    except Exception:
        return "openai/gpt-oss-20b"

# Page configuration
st.set_page_config(
    page_title="J&K EduSetu | Your Bridge to Education & Opportunities",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# GLOBAL CSS OVERRIDES & MODERN ANIMATIONS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Gradient sidebar with glassmorphic depth */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #091927 0%, #132D3F 50%, #1A3E54 100%);
    border-right: 1px solid rgba(232, 118, 44, 0.25);
    padding-top: 1rem;
}
[data-testid="stSidebar"] * { color: #F0F4F8 !important; }

/* Sidebar action buttons */
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #E8762C, #D35400);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    width: 100%;
    margin-top: 4px;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 4px 12px rgba(232, 118, 44, 0.25);
}
[data-testid="stSidebar"] .stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(232, 118, 44, 0.45);
}

[data-testid="collapsedControl"] {
    display: block; color: white;
}

/* App background subtle mesh gradient */
.stApp {
    background: linear-gradient(135deg, #EEF2F7 0%, #E6EDF5 50%, #EDF4EE 100%);
}

/* Main container max-width */
.main .block-container {
    padding-top: 1.25rem;
    max-width: 880px;
}

/* Smooth Chat Bubble Entrance */
@keyframes messageEntrance {
  from { opacity: 0; transform: translateY(10px) scale(0.99); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

[data-testid="stChatMessage"] {
    animation: messageEntrance 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    margin-bottom: 12px;
}

/* User chat bubble */
[data-testid="stChatMessage"]:has(
  [data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #1B3A4B 0%, #0D2137 100%);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 14px 20px;
    box-shadow: 0 4px 16px rgba(27, 58, 75, 0.25);
}

/* Bot chat bubble */
[data-testid="stChatMessage"]:has(
  [data-testid="stChatMessageAvatarAssistant"])
  [data-testid="stChatMessageContent"] {
    background: #FFFFFF;
    border-left: 4px solid #E8762C;
    border-radius: 4px 18px 18px 18px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

/* Input box with animated glowing focus */
[data-testid="stChatInput"] textarea {
    border-radius: 14px;
    border: 2px solid #1B3A4B !important;
    background: #FFFFFF;
    box-shadow: 0 2px 10px rgba(27, 58, 75, 0.08);
    font-family: inherit;
    transition: all 0.2s ease;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #E8762C !important;
    box-shadow: 0 0 0 4px rgba(232, 118, 44, 0.15) !important;
}

/* Animated Hero Banner */
@keyframes heroGlow {
  0% { border-bottom-color: #E8762C; box-shadow: 0 10px 30px rgba(232, 118, 44, 0.15); }
  50% { border-bottom-color: #2ECC71; box-shadow: 0 10px 30px rgba(46, 204, 113, 0.2); }
  100% { border-bottom-color: #E8762C; box-shadow: 0 10px 30px rgba(232, 118, 44, 0.15); }
}

.hero-container {
    background: linear-gradient(135deg, #091927 0%, #132D3F 60%, #1B3A4B 100%);
    border-radius: 18px;
    padding: 30px 28px;
    margin-bottom: 18px;
    border-bottom: 4px solid #E8762C;
    animation: heroGlow 6s infinite ease-in-out;
    position: relative;
    overflow: hidden;
}

/* Live Radar Pulse Indicator */
@keyframes pulseRadar {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
  70% { transform: scale(1.05); box-shadow: 0 0 0 8px rgba(46, 204, 113, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
}

.pulse-radar {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background-color: #2ECC71;
    display: inline-block;
    margin-right: 6px;
    animation: pulseRadar 2s infinite;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
    margin-bottom: 8px;
}
.status-pill-2g {
    background: rgba(46, 204, 113, 0.18);
    color: #2ECC71 !important;
    border: 1px solid rgba(46, 204, 113, 0.4);
}
.status-pill-cloud {
    background: rgba(52, 152, 219, 0.18);
    color: #5DADE2 !important;
    border: 1px solid rgba(93, 173, 226, 0.4);
}
.status-pill-auto {
    background: rgba(232, 118, 44, 0.18);
    color: #F39C12 !important;
    border: 1px solid rgba(243, 156, 18, 0.4);
}

/* Interactive Modern Stat Cards */
.modern-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 18px 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.04);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
}
.modern-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(27, 58, 75, 0.12) !important;
}

/* Topic Prompt Chips */
.topic-btn {
    background: #FFFFFF;
    color: #1B3A4B;
    border: 1px solid #D5E2EC;
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 600;
    transition: all 0.2s ease;
    cursor: pointer;
    text-align: left;
    width: 100%;
}
.topic-btn:hover {
    border-color: #E8762C;
    background: #FEF9F5;
    color: #C4621F;
    transform: translateX(2px);
}

/* Portal link button */
.portal-action-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #1B3A4B, #0D2137);
    color: #FFFFFF !important;
    padding: 7px 16px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
    margin-top: 8px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(27, 58, 75, 0.2);
}
.portal-action-btn:hover {
    background: linear-gradient(135deg, #E8762C, #D35400);
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(232, 118, 44, 0.35);
}

/* Sidebar gradient — logo colors */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D2137 0%, #1B3A8C 55%, #1A6B3C 100%);
    border-right: 1px solid rgba(26,107,60,0.3);
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton button {
    background: #1A6B3C; color: white;
    border: none; border-radius: 8px; width: 100%;
}
[data-testid="collapsedControl"] { display: block; color: white; }

/* App background */
.stApp {
    background: linear-gradient(135deg, #F4F8FC 0%, #EBF5F0 50%, #EEF2FA 100%);
}
.main .block-container { padding-top: 1.25rem; max-width: 1040px; }

/* Modern Tabs Navigation Bar */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255, 255, 255, 0.85);
    padding: 8px 12px;
    border-radius: 16px;
    border: 1px solid rgba(27, 58, 140, 0.15);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    backdrop-filter: blur(10px);
    margin-bottom: 16px;
}
.stTabs [data-baseweb="tab"] {
    height: 42px;
    white-space: nowrap;
    font-weight: 700;
    font-size: 13.5px;
    border-radius: 10px;
    padding: 0 16px;
    color: #1B3A8C;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    border: 1px solid transparent;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(27, 58, 140, 0.06);
    color: #0D2137;
    border-color: rgba(27, 58, 140, 0.1);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0D2137 0%, #1B3A8C 100%) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(27, 58, 140, 0.3) !important;
    border: none !important;
}

/* Visual Seat Distribution Bars */
.seat-bar-track {
    display: flex;
    height: 14px;
    border-radius: 7px;
    overflow: hidden;
    background: #E0E7EC;
    margin: 8px 0 4px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}
.seat-bar-om { background: #1B3A8C; }
.seat-bar-sc { background: #E8762C; }
.seat-bar-st { background: #8E44AD; }
.seat-bar-rba { background: #1A6B3C; }

/* Prompt suggestion chips */
.prompt-chip {
    display: inline-block;
    background: white;
    border: 1px solid rgba(27, 58, 140, 0.2);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
    color: #1B3A8C;
    margin: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}
.prompt-chip:hover {
    background: #1B3A8C;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(27, 58, 140, 0.25);
}

/* User chat bubble */
[data-testid="stChatMessage"]:has(
  [data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #1B3A8C, #0D2137);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 14px 18px;
    box-shadow: 0 4px 15px rgba(27,58,140,0.25);
}

/* Bot bubble */
[data-testid="stChatMessage"]:has(
  [data-testid="stChatMessageAvatarAssistant"])
  [data-testid="stChatMessageContent"] {
    background: white;
    border-left: 4px solid #1A6B3C;
    border-radius: 4px 18px 18px 18px;
    padding: 14px 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.07);
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    border-radius: 14px;
    border: 2px solid #1B3A8C !important;
    background: white;
    box-shadow: 0 2px 8px rgba(27,58,140,0.1);
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #1A6B3C !important;
    box-shadow: 0 2px 12px rgba(26,107,60,0.2) !important;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
    .main .block-container {
        padding: 0.8rem 0.5rem !important;
        max-width: 100% !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto;
        flex-wrap: nowrap;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 11.5px;
        padding: 0 10px;
        height: 36px;
    }
    .modern-card {
        padding: 12px !important;
    }
}

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Initializing RAG Engine & Vector DB...")
def get_rag_engine():
    """Cache and return the RAG Engine instance."""
    return RAGEngine(docs_dir=DOCS_DIR, chroma_dir=CHROMA_DIR)


# Initialize RAG Engine
rag_engine = get_rag_engine()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize automatic Groq model on first load only
if "selected_model" not in st.session_state or (groq_client and st.session_state.selected_model == "openai/gpt-oss-20b"):
    st.session_state.selected_model = get_best_groq_model(groq_client)

# Pre-load & auto-sync documents from /docs with ChromaDB (indexes new files, purges deleted)
if "auto_indexed_once" not in st.session_state:
    try:
        rag_engine.sync_documents()
    except Exception as e:
        print(f"Warning during sync_documents: {e}")
    st.session_state.auto_indexed_once = True


# ==========================================
# SIDEBAR CONTROLS (Clean, Query-Focused)
# ==========================================
with st.sidebar:
    st.sidebar.image("assets/logo.png", width=110)
    st.sidebar.markdown("""
<div style="text-align:center; padding:4px 0 12px;">
  <div style="color:white;font-size:18px;font-weight:800;letter-spacing:0.5px;">
    J&K EduSetu
  </div>
  <div style="color:#F5A623;font-size:10px;font-weight:700;margin-top:2px;">
    Your Bridge to Education & Opportunities
  </div>
  <div style="color:#AEC6D0;font-size:10px;margin-top:2px;">
    by Team Error404 · NIE Mysuru
  </div>
  <div style="color:#F5A623;font-size:9px;margin-top:2px;letter-spacing:1px;">
    SIH 2026 · SIH25094
  </div>
</div>
""", unsafe_allow_html=True)

    with st.sidebar.expander("About This Project"):
        st.markdown("""
    **Team Error404**
    NIE Mysuru · CSE · Batch 2027

    **Problem Statement:** SIH25094
    Government of Jammu & Kashmir
    Theme: Smart Education

    **Stack:** LangChain · ChromaDB · Groq · Streamlit

    *All answers sourced from official J&K government documents.*
    """)

    from model_router import render_model_badge
    render_model_badge()

    # 0. Language Selector
    st.subheader("🌐 Language / زبان / भाषा")
    selected_lang = st.selectbox(
        "Interface Language",
        options=["English", "हिंदी (Hindi)", "اردو (Urdu)"],
        index=0,
        key="app_lang_select",
        label_visibility="collapsed"
    )
    st.session_state.selected_language = selected_lang

    st.divider()

    # 1. Network & Engine Mode Selector (Major 2G Selling Point)
    st.subheader("📶 Network & Engine Mode")
    network_mode = st.radio(
        "Select Operating Mode",
        options=["🤖 Smart Auto-Detect", "⚡ 2G Ultra-Lite (Offline)", "🌐 AI Cloud (Llama 3)"],
        index=0,
        help="⚡ 2G Ultra-Lite: Sub-10ms instant responses, zero external API calls. 🌐 AI Cloud: Deep conversational generation."
    )

    # Visual Mode Status Indicator
    if network_mode == "⚡ 2G Ultra-Lite (Offline)":
        st.markdown(
            '<div class="status-pill status-pill-2g"><span class="pulse-radar"></span>⚡ 2G Offline Mode (0ms Latency)</div>',
            unsafe_allow_html=True
        )
    elif network_mode == "🌐 AI Cloud (Llama 3)":
        st.markdown(
            f'<div class="status-pill status-pill-cloud">🌐 Groq Cloud: {st.session_state.selected_model}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-pill status-pill-auto"><span class="pulse-radar"></span>🤖 Smart Auto-Detect (Zero Downtime)</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # Advanced Retrieval Configuration (Grouped for Cleanliness)
    with st.expander("⚙️ Advanced Retrieval Settings", expanded=False):
        top_k = st.slider("Top Relevant Chunks (Top-K)", min_value=1, max_value=10, value=5)
        enable_stream = st.checkbox("Stream Responses", value=True)
        stats = rag_engine.get_collection_stats()
        st.caption(f"📚 Knowledge Base: **{stats['total_chunks']} chunks** indexed from **{len(stats.get('all_files', []))} official documents**.")

    st.divider()

    # 📅 Scholarship Deadline Calendar
    st.subheader("📅 Upcoming Deadlines")
    try:
        calendar = get_deadline_calendar()
        upcoming = [c for c in calendar if c.get("status") in ("open", "upcoming")][:3]
        if upcoming:
            for item in upcoming:
                status_color = "🟢" if item["status"] == "open" else "🟡"
                st.caption(f"{status_color} **{item['name']}** — {item.get('deadline_display', item.get('application_close', 'N/A'))}")
        else:
            st.caption("No upcoming deadlines tracked.")
    except Exception:
        st.caption("Deadline calendar unavailable.")

    st.divider()

    # 🔐 Admin Portal Access
    st.subheader("🔐 Admin Portal")
    admin_password = st.text_input("Enter Admin Password", type="password", key="admin_pwd")
    if admin_password:
        expected_pwd = ""
        try:
            expected_pwd = st.secrets.get("ADMIN_PASSWORD", "admin123")
        except Exception:
            expected_pwd = os.getenv("ADMIN_PASSWORD", "admin123")
        if admin_password == expected_pwd:
            st.session_state.admin_mode = True
            st.success("✅ Admin access granted")
        else:
            st.session_state.admin_mode = False
            st.error("❌ Invalid password")
    
    st.divider()

    # Clear Chat History
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        for key in ["interview_session", "admin_mode"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


# ==========================================
# MAIN INTERFACE - DASHBOARD HERO & METRICS
# ==========================================

# Active Language Metadata
active_lang = st.session_state.get("selected_language", "English")
lang_meta = TRANSLATIONS.get(active_lang, TRANSLATIONS["English"])

# 1. HERO SECTION
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0D2137 0%,#1B3A8C 60%,#1A6B3C 100%);
     border-radius:16px; padding:24px 28px; margin-bottom:18px;
     border-bottom:4px solid #F5A623;">
  <div style="display:flex; align-items:center; gap:16px;">
    <img src="app/static/logo.png" width="68"
         style="border-radius:8px; flex-shrink:0;">
    <div>
      <div style="color:#F5A623;font-size:10px;font-weight:700;
           letter-spacing:2px;margin-bottom:4px;">
        SIH 2026 · SIH25094 · TEAM ERROR404
      </div>
      <div style="color:white;font-size:24px;font-weight:800;line-height:1.2;">
        J&K EduSetu
      </div>
      <div style="color:#F5A623;font-size:13px;font-weight:700;margin-top:2px;">
        {lang_meta['tagline']}
      </div>
      <div style="color:#AEC6D0;font-size:12px;margin-top:3px;">
        AI Career & Education Advisory for Jammu & Kashmir · Verified Government Sources · 2G-Ready
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# 2. STAT CARDS ROW (4 CARDS WITH HOVER LIFT)
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.markdown("""
    <div class="modern-card" style="border-top:4px solid #1B3A4B;">
      <div style="font-size:26px;font-weight:800;color:#1B3A4B;">2M+</div>
      <div style="font-size:11px;color:#555;font-weight:600;margin-top:2px;">
        Students in J&K needing guidance
      </div>
    </div>
    """, unsafe_allow_html=True)

with stat_col2:
    st.markdown("""
    <div class="modern-card" style="border-top:4px solid #E8762C;">
      <div style="font-size:26px;font-weight:800;color:#E8762C;">&lt;200</div>
      <div style="font-size:11px;color:#555;font-weight:600;margin-top:2px;">
        Career counselors in entire UT
      </div>
    </div>
    """, unsafe_allow_html=True)

with stat_col3:
    st.markdown("""
    <div class="modern-card" style="border-top:4px solid #27AE60;">
      <div style="font-size:26px;font-weight:800;color:#27AE60;">&lt;10 ms</div>
      <div style="font-size:11px;color:#555;font-weight:600;margin-top:2px;">
        2G Instant offline response time
      </div>
    </div>
    """, unsafe_allow_html=True)

with stat_col4:
    st.markdown("""
    <div class="modern-card" style="border-top:4px solid #8E44AD;">
      <div style="font-size:26px;font-weight:800;color:#8E44AD;">100%</div>
      <div style="font-size:11px;color:#555;font-weight:600;margin-top:2px;">
        Zero hallucination cited data
      </div>
    </div>
    """, unsafe_allow_html=True)


# 3. FEATURE CHIPS (WITH ACTIVE LANGUAGE)
st.markdown(f"""
<div style="display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 20px;">
  <span style="background:#E8F4F8;color:#1B3A4B;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #C5DCE8;">⚡ 2G Operability</span>
  <span style="background:#FEF3E8;color:#C4621F;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #F5C99A;">📄 Cited Answers</span>
  <span style="background:#EAF7EF;color:#1E8449;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #A9DFBF;">🏛️ Govt. Data Only</span>
  <span style="background:#F4ECFB;color:#6C3483;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #D7BDE2;">{lang_meta['lang_badge']}</span>
  <span style="background:#FDEDEC;color:#922B21;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #F1948A;">💸 Zero Cost</span>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. MULTI-VIEW TOP NAVIGATION TABS
# ==========================================
tab_titles = [
    "💬 AI Advisor",
    "🏫 Colleges & Seats",
    "🎯 Scholarships",
    "💼 Careers & Jobs",
    "🎤 Mock Interview",
    "📄 Resume Studio"
]
if st.session_state.get("admin_mode", False):
    tab_titles.append("📊 Admin Portal")

tabs = st.tabs(tab_titles)


# =========================================================================
# TAB 1: 💬 AI ADVISOR & CONVERSATION
# =========================================================================
with tabs[0]:
    # Persistent Quick Topics & Prompt Chips
    st.markdown(f"##### {lang_meta['explore_heading']}")
    qc1, qc2 = st.columns(2)
    for idx, (p_title, p_query) in enumerate(lang_meta["prompts"]):
        col = qc1 if idx % 2 == 0 else qc2
        with col:
            if st.button(p_title, use_container_width=True, key=f"quick_p_{idx}_{active_lang}"):
                st.session_state.messages.append({"role": "user", "content": p_query})
                st.rerun()

    st.markdown("---")

    # Conversation History Display
    st.markdown("### 💬 Advisor Conversation")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                
                # Display portal button if available
                if msg.get("portal_url"):
                    st.markdown(
                        f'<a class="portal-action-btn" href="{msg["portal_url"]}" target="_blank">'
                        f'🔗 Open Official Portal'
                        f'</a>',
                        unsafe_allow_html=True
                    )

                if "sources" in msg and msg["sources"]:
                    model_label = f" (Engine: {msg.get('model_used', 'AI')})" if msg.get('model_used') else ""
                    with st.expander(f"📚 View {len(msg['sources'])} Cited Source Chunks from Govt. Archives{model_label}"):
                        for i, src in enumerate(msg["sources"], 1):
                            st.caption(f"**Source {i}: {src.get('source', 'Document')} (Page {src.get('page', '?')})** • Similarity: {src.get('similarity', 0.0):.2f}")
                            if src.get("text"):
                                st.markdown(f"> {src.get('text', '')}")

    # Chat Input Handler
    user_input = st.chat_input(lang_meta["chat_placeholder"])

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

    # Query Execution Handler
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        current_prompt = st.session_state.messages[-1]["content"]

        # 1. 2G ULTRA-LITE MODE (Zero external API, Sub-10ms Instant Delivery)
        if network_mode == "⚡ 2G Ultra-Lite (Offline)":
            with st.chat_message("assistant"):
                offline_match = get_2g_response(current_prompt)
                if offline_match:
                    full_response = offline_match["answer"]
                    st.markdown(full_response)
                    portal_url = offline_match.get("portal_url", "")
                    if portal_url:
                        st.markdown(
                            f'<a class="portal-action-btn" href="{portal_url}" target="_blank">🔗 Open Official Portal</a>',
                            unsafe_allow_html=True
                        )
                    retrieved_sources = offline_match.get("sources", [])
                    model_used = f"⚡ 2G Offline Engine ({offline_match['latency_ms']}ms latency)"
                else:
                    retrieved_chunks = rag_engine.retrieve(current_prompt, top_k=3)
                    if retrieved_chunks:
                        full_response = "Here are the verified records retrieved directly from the offline government archive:\n\n"
                        for idx, chunk in enumerate(retrieved_chunks, 1):
                            full_response += f"**{idx}. [{chunk['source']} - Page {chunk['page']}]:**\n{chunk['text']}\n\n"
                        st.markdown(full_response)
                        retrieved_sources = retrieved_chunks
                        model_used = "⚡ 2G Local ChromaDB Vector Search (0 API calls)"
                        portal_url = ""
                    else:
                        full_response = "No matching records found in local offline storage for this query. Please try searching for scholarships, colleges, or career paths."
                        st.markdown(full_response)
                        retrieved_sources = []
                        model_used = "⚡ 2G Offline Engine"
                        portal_url = ""

                if retrieved_sources:
                    with st.expander(f"📚 View {len(retrieved_sources)} Cited Source Chunks (Engine: {model_used})"):
                        for i, src in enumerate(retrieved_sources, 1):
                            st.caption(f"**Source {i}: {src.get('source', 'Document')} (Page {src.get('page', '?')})** • Similarity: {src.get('similarity', 0.0):.2f}")
                            if src.get("text"):
                                st.markdown(f"> {src.get('text', '')}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": retrieved_sources,
                    "model_used": model_used,
                    "portal_url": portal_url,
                    "search_query": current_prompt
                })

        # 2. SMART AUTO-DETECT & AI CLOUD (Adaptive Hybrid Execution)
        else:
            offline_match = get_2g_response(current_prompt) if network_mode == "🤖 Smart Auto-Detect" else None

            if offline_match and offline_match.get("confidence_score", 0) >= 3.5:
                with st.chat_message("assistant"):
                    full_response = offline_match["answer"]
                    st.markdown(full_response)
                    portal_url = offline_match.get("portal_url", "")
                    if portal_url:
                        st.markdown(
                            f'<a class="portal-action-btn" href="{portal_url}" target="_blank">🔗 Open Official Portal</a>',
                            unsafe_allow_html=True
                        )
                    retrieved_sources = offline_match.get("sources", [])
                    model_used = f"⚡ Instant 2G Cache ({offline_match['latency_ms']}ms)"

                    if retrieved_sources:
                        with st.expander(f"📚 View {len(retrieved_sources)} Cited Source Chunks (Engine: {model_used})"):
                            for i, src in enumerate(retrieved_sources, 1):
                                st.caption(f"**Source {i}: {src.get('source', 'Document')} (Page {src.get('page', '?')})** • Similarity: {src.get('similarity', 0.0):.2f}")
                                if src.get("text"):
                                    st.markdown(f"> {src.get('text', '')}")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "sources": retrieved_sources,
                        "model_used": model_used,
                        "portal_url": portal_url,
                        "search_query": current_prompt
                    })

            elif not google_api_key and not groq_api_key:
                with st.chat_message("assistant"):
                    render_error_card(Exception("AuthenticationError: 401 Missing GOOGLE_API_KEY / GROQ_API_KEY in st.secrets"))
                    if offline_match:
                        full_response = offline_match["answer"]
                        st.markdown(full_response)
                        portal_url = offline_match.get("portal_url", "")
                        if portal_url:
                            st.markdown(
                                f'<a class="portal-action-btn" href="{portal_url}" target="_blank">🔗 Open Official Portal</a>',
                                unsafe_allow_html=True
                            )
                        retrieved_sources = offline_match.get("sources", [])
                        model_used = "⚡ 2G Offline Fallback"
                    else:
                        retrieved_chunks = rag_engine.retrieve(current_prompt, top_k=top_k)
                        if retrieved_chunks:
                            full_response = "Here are the relevant provisions from official documents:\n\n"
                            for idx, chunk in enumerate(retrieved_chunks, 1):
                                full_response += f"**{idx}. [{chunk['source']} - Page {chunk['page']}]:**\n{chunk['text']}\n\n"
                            st.markdown(full_response)
                            retrieved_sources = retrieved_chunks
                            model_used = "⚡ 2G Local ChromaDB Fallback"
                            portal_url = ""
                        else:
                            full_response = "Please configure your `GOOGLE_API_KEY` (or `GROQ_API_KEY`) in Streamlit Secrets or switch to ⚡ 2G Ultra-Lite mode."
                            st.markdown(full_response)
                            retrieved_sources = []
                            model_used = "Offline System"
                            portal_url = ""

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "sources": retrieved_sources,
                        "model_used": model_used,
                        "portal_url": portal_url,
                        "search_query": current_prompt
                    })

            else:
                with st.chat_message("assistant"):
                    try:
                        # Append language guidance if not English
                        cloud_query = current_prompt
                        if active_lang != "English":
                            cloud_query = f"{current_prompt}\n\n[Note: {lang_meta['system_instruction']}]"

                        if enable_stream:
                            gen_result = rag_engine.generate_answer(
                                query=cloud_query,
                                api_key=groq_api_key,
                                model=st.session_state.selected_model,
                                top_k=top_k,
                                history=st.session_state.messages[:-1],
                                stream=True
                            )
                            full_response = st.write_stream(gen_result["stream"])
                        else:
                            with st.spinner("Generating answer from government documents..."):
                                gen_result = rag_engine.generate_answer(
                                    query=cloud_query,
                                    api_key=groq_api_key,
                                    model=st.session_state.selected_model,
                                    top_k=top_k,
                                    history=st.session_state.messages[:-1],
                                    stream=False
                                )
                                full_response = gen_result["answer"]
                                st.markdown(full_response)

                        model_used = gen_result.get("model_used", st.session_state.selected_model)
                        retrieved_sources = gen_result.get("sources", [])
                        search_query = gen_result.get("search_query", current_prompt)

                        if retrieved_sources:
                            query_note = f" | Search: '{search_query}'" if search_query != current_prompt else ""
                            with st.expander(f"📚 View {len(retrieved_sources)} Cited Source Chunks from ChromaDB (Model: {model_used}{query_note})"):
                                for i, src in enumerate(retrieved_sources, 1):
                                    st.caption(f"**Source {i}: {src.get('source', 'Document')} (Page {src.get('page', '?')})** • Similarity: {src.get('similarity', 0.0):.2f}")
                                    if src.get("text"):
                                        st.markdown(f"> {src.get('text', '')}")

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": full_response,
                            "sources": retrieved_sources,
                            "model_used": model_used,
                            "portal_url": "",
                            "search_query": search_query
                        })

                    except Exception as e:
                        render_error_card(e)
                        if offline_match:
                            full_response = offline_match["answer"]
                            st.markdown(full_response)
                            portal_url = offline_match.get("portal_url", "")
                            if portal_url:
                                st.markdown(
                                    f'<a class="portal-action-btn" href="{portal_url}" target="_blank">🔗 Open Official Portal</a>',
                                    unsafe_allow_html=True
                                )
                            retrieved_sources = offline_match.get("sources", [])
                        else:
                            retrieved_chunks = rag_engine.retrieve(current_prompt, top_k=3)
                            full_response = "Here are the verified provisions from the local government archives:\n\n"
                            for idx, chunk in enumerate(retrieved_chunks, 1):
                                full_response += f"**{idx}. [{chunk['source']} - Page {chunk['page']}]:**\n{chunk['text']}\n\n"
                            st.markdown(full_response)
                            retrieved_sources = retrieved_chunks
                            portal_url = ""

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": full_response,
                            "sources": retrieved_sources,
                            "model_used": "⚡ 2G Offline Fallback",
                            "portal_url": portal_url,
                            "search_query": current_prompt
                        })


# =========================================================================
# TAB 2: 🏫 COLLEGES & SEATS
# =========================================================================
with tabs[1]:
    st.markdown("### 🏫 J&K Higher Education Directory & Seat Matrices")
    st.caption("Explore 26 higher education institutions across Jammu & Kashmir with official seat distributions and cutoffs.")

    ce_col1, ce_col2, ce_col3 = st.columns(3)
    with ce_col1:
        ce_district = st.selectbox("📍 District Filter", ["All"] + get_all_districts(), key="ce_district_tab")
    with ce_col2:
        ce_type = st.selectbox("🎓 College Type", ["All"] + get_all_college_types(), key="ce_type_tab")
    with ce_col3:
        ce_search = st.text_input("🔍 Search College or Branch", placeholder="e.g., NIT, GMC, IUST, CSE...", key="ce_search_tab")

    filter_district = None if ce_district == "All" else ce_district
    filter_type = None if ce_type == "All" else ce_type

    colleges_found = search_colleges(ce_search if ce_search else "", district=filter_district, college_type=filter_type)

    # 🗺️ Interactive J&K Map
    map_data = get_colleges_map_data(colleges_found)
    if map_data:
        with st.expander("🗺️ Interactive Geographic Map of J&K Institutions", expanded=True):
            st.map(map_data, zoom=7, use_container_width=True)
            st.caption(f"📍 Showing {len(map_data)} institutions across Kashmir Valley & Jammu Division.")

    st.markdown(f"#### Found {len(colleges_found)} Institutions")

    for college in colleges_found[:12]:
        card_md = render_college_card(college)
        st.markdown(card_md)

        # 📊 Visual Seat Distribution Bar
        branches = college.get("branches", [])
        if branches:
            total_intake = sum(b.get("total_seats", 0) for b in branches)
            om_seats = sum(b.get("seats_om", 0) for b in branches)
            sc_seats = sum(b.get("seats_sc", 0) for b in branches)
            st_seats = sum(b.get("seats_st", 0) for b in branches)
            rba_seats = sum(b.get("seats_rba", 0) for b in branches)

            if total_intake > 0:
                om_pct = round((om_seats / total_intake) * 100, 1)
                sc_pct = round((sc_seats / total_intake) * 100, 1)
                st_pct = round((st_seats / total_intake) * 100, 1)
                rba_pct = round((rba_seats / total_intake) * 100, 1)

                st.markdown(f"""
                <div style="background: white; border-radius: 10px; padding: 12px 16px; margin: 10px 0; border: 1px solid #DDE5EC; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                  <div style="font-size: 11.5px; font-weight: 700; color: #1B3A8C; margin-bottom: 6px;">
                    📊 Aggregate Reservation Distribution ({total_intake} Total Seats across {len(branches)} programs)
                  </div>
                  <div class="seat-bar-track">
                    <div class="seat-bar-om" style="width: {om_pct}%;" title="Open Merit: {om_seats} seats ({om_pct}%)"></div>
                    <div class="seat-bar-sc" style="width: {sc_pct}%;" title="Scheduled Caste: {sc_seats} seats ({sc_pct}%)"></div>
                    <div class="seat-bar-st" style="width: {st_pct}%;" title="Scheduled Tribe: {st_seats} seats ({st_pct}%)"></div>
                    <div class="seat-bar-rba" style="width: {rba_pct}%;" title="RBA / ALC / IB Quota: {rba_seats} seats ({rba_pct}%)"></div>
                  </div>
                  <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 11px; color: #444; margin-top: 6px;">
                    <span><strong style="color:#1B3A8C;">■ Open Merit:</strong> {om_seats} ({om_pct}%)</span>
                    <span><strong style="color:#E8762C;">■ SC:</strong> {sc_seats} ({sc_pct}%)</span>
                    <span><strong style="color:#8E44AD;">■ ST:</strong> {st_seats} ({st_pct}%)</span>
                    <span><strong style="color:#1A6B3C;">■ RBA/Border:</strong> {rba_seats} ({rba_pct}%)</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Seat matrix branch expander
        seat_data = get_seat_matrix(college["id"])
        if seat_data and seat_data.get("branches"):
            with st.expander(f"📊 Detailed Branch-by-Branch Seat Matrix — {college['name']}", expanded=False):
                for branch in seat_data["branches"]:
                    st.caption(
                        f"**{branch['name']}**: Total {branch.get('total_seats', 'N/A')} seats | "
                        f"OM: {branch.get('seats_om', '-')} | SC: {branch.get('seats_sc', '-')} | "
                        f"ST: {branch.get('seats_st', '-')} | RBA: {branch.get('seats_rba', '-')}"
                    )
        st.markdown("---")

    # Side-by-side College Comparison Tool
    st.markdown("### 📊 Side-by-Side College Cutoff Comparison")
    all_colleges = search_colleges("")
    college_names = {c["id"]: c["name"] for c in all_colleges}
    compare_ids = st.multiselect(
        "Select Colleges to Compare (2–4)",
        options=list(college_names.keys()),
        format_func=lambda x: college_names.get(x, x),
        max_selections=4,
        key="ce_compare_tab"
    )
    if len(compare_ids) >= 2:
        comparison = get_cutoff_comparison(compare_ids)
        if comparison:
            st.markdown("#### Cutoff & Seats Comparison")
            for item in comparison:
                st.markdown(f"**{item.get('college_name', item.get('id', ''))}**")
                for b in item.get("branches", [])[:5]:
                    st.caption(f"  • {b['name']}: {b.get('cutoff_info', 'N/A')} ({b.get('total_seats', 'N/A')} seats)")


# =========================================================================
# TAB 3: 🎯 SCHOLARSHIPS
# =========================================================================
with tabs[2]:
    st.markdown("### 🎯 Smart Scholarship & Eligibility Engine")
    st.caption("Fill your academic & financial profile to match against 15+ central & J&K government scholarship programs.")

    wiz_row1_c1, wiz_row1_c2, wiz_row1_c3, wiz_row1_c4 = st.columns(4)
    with wiz_row1_c1:
        w_stream = st.selectbox("🎓 Stream", ["PCM", "PCB", "Commerce", "Arts", "All"], key="sch_stream")
    with wiz_row1_c2:
        w_income_val = st.selectbox("💰 Annual Household Income", ["Below ₹2.50 Lakh", "₹2.50L – ₹8.00L", "Above ₹8.00 Lakh"], key="sch_income")
    with wiz_row1_c3:
        w_cat = st.selectbox("🏛️ Category / Domicile", ["OM", "SC", "ST", "OBC", "RBA", "Minority"], key="sch_cat")
    with wiz_row1_c4:
        w_gender = st.selectbox("👤 Gender", ["male", "female"], key="sch_gender")

    wiz_row2_c1, wiz_row2_c2, wiz_row2_c3 = st.columns(3)
    with wiz_row2_c1:
        w_percentage = st.number_input("📊 Class 12th Board %", min_value=0, max_value=100, value=75, key="sch_pct")
    with wiz_row2_c2:
        w_age = st.number_input("🎂 Age (Years)", min_value=15, max_value=45, value=18, key="sch_age")
    with wiz_row2_c3:
        w_disability = st.checkbox("♿ Person with Disability (PwD)", key="sch_pwd")

    income_map = {"Below ₹2.50 Lakh": 200000, "₹2.50L – ₹8.00L": 500000, "Above ₹8.00 Lakh": 1000000}

    profile = {
        "stream": w_stream,
        "income": income_map.get(w_income_val, 500000),
        "category": w_cat,
        "gender": w_gender,
        "percentage": w_percentage,
        "age": w_age,
        "disability": w_disability,
        "domicile": "J&K",
    }

    matches = check_eligibility(profile)

    if matches:
        strong = [m for m in matches if m.get("match_score", 0) >= 80]
        likely = [m for m in matches if 50 <= m.get("match_score", 0) < 80]

        st.markdown(f"### ✅ Found **{len(matches)}** Matching Schemes")

        if strong:
            st.markdown("#### 🟢 High-Eligibility Schemes (>80% Match)")
            for m in strong[:5]:
                sch = m.get("scholarship", m)
                name = sch.get("name", m.get("name", "Unknown"))
                benefits = sch.get("benefits", {})
                tuition = benefits.get("tuition_support", benefits.get("tuition_cap", ""))
                maint = benefits.get("maintenance_allowance", "")
                portal = sch.get("portal_url", "")
                st.markdown(f"- 🎓 **{name}** — {tuition} {f'(+ {maint})' if maint else ''}")
                if portal:
                    st.caption(f"  🔗 [Apply on Official Portal: {portal}]({portal})")

        if likely:
            st.markdown("#### 🟡 Likely Eligible Schemes (50–80% Match)")
            for m in likely[:4]:
                sch = m.get("scholarship", m)
                name = sch.get("name", m.get("name", "Unknown"))
                st.markdown(f"- 📋 {name}")

        # Required Documents Checklist
        sch_ids = [m.get("scholarship", m).get("id", m.get("id", "")) for m in matches[:5]]
        docs = get_documents_checklist(sch_ids)
        if docs:
            with st.expander(f"📋 Consolidated Documents Checklist ({len(docs)} items)", expanded=False):
                for doc in docs:
                    st.markdown(f"- ✅ {doc}")
    else:
        st.info("No scholarships matched this exact combination. Try adjusting stream or income parameters.")

    if st.button("💬 Ask AI Advisor to Guide Me on These Scholarships", key="btn_sch_to_chat"):
        schemes_text = ", ".join([m.get("scholarship", m).get("name", m.get("name", "")) for m in matches[:5]]) if matches else "available schemes"
        st.session_state.messages.append({
            "role": "user",
            "content": f"Based on my profile ({w_stream}, income {w_income_val}, category {w_cat}, Class 12: {w_percentage}%), guide me on how to apply for: {schemes_text}"
        })
        st.rerun()


# =========================================================================
# TAB 4: 💼 CAREERS & JOBS
# =========================================================================
with tabs[3]:
    st.markdown("### 💼 J&K Labor Market Intelligence & Career Navigator")
    job_sub1, job_sub2 = st.tabs(["🔍 Browse 30+ Job Profiles", "🎯 Interactive Skill Gap Analyzer"])

    with job_sub1:
        st.caption("Explore government, banking, public sector, and private job profiles tailored for J&K youth.")
        jb_col1, jb_col2 = st.columns(2)
        with jb_col1:
            jb_board = st.selectbox("🏛️ Recruitment Board / Sector", ["All"] + get_all_boards(), key="tab_jb_board")
        with jb_col2:
            jb_search = st.text_input("🔍 Search Job Title or Department", placeholder="e.g., Junior Assistant, KAS, Police, IT...", key="tab_jb_search")

        filter_board = None if jb_board == "All" else jb_board
        jobs_found = search_jobs(jb_search if jb_search else "", board=filter_board)

        st.markdown(f"#### Found {len(jobs_found)} Opportunities")
        for job in jobs_found[:8]:
            card_md = render_job_card(job)
            st.markdown(card_md)

            if st.button(f"📝 View Exam Prep Roadmap: {job['title']}", key=f"prep_tab_{job['id']}"):
                plan = get_exam_preparation_plan(job["id"])
                if plan:
                    st.markdown(f"**📚 Subject-wise Preparation Plan for {job['title']}:**")
                    for subject in plan.get("subjects", []):
                        if isinstance(subject, dict):
                            st.caption(f"• **{subject.get('name', subject)}**: {subject.get('hours_per_week', '')} hrs/week")
                        else:
                            st.caption(f"• {subject}")
                    if plan.get("timeline"):
                        st.caption(f"⏱️ Recommended duration: {plan.get('timeline', 'N/A')}")
                    if plan.get("resources"):
                        st.caption(f"📖 Curated Books: {', '.join(plan['resources'][:5]) if isinstance(plan['resources'], list) else plan['resources']}")
            st.markdown("---")

    with job_sub2:
        st.caption("Select your skills to reveal matched career pathways and missing competency requirements.")
        available_skills = get_all_skills()
        selected_skills = st.multiselect(
            "🛠️ Select Your Existing Skills & Subjects",
            options=available_skills,
            default=[],
            key="tab_skill_select"
        )

        if selected_skills:
            career_matches = match_skills_to_careers(selected_skills)
            if career_matches:
                report_md = render_skill_gap_report(career_matches)
                st.markdown(report_md)

                if st.button("💬 Ask AI for Step-by-Step Skill Upgrade Roadmap", key="btn_skill_tab_ai"):
                    skills_text = ", ".join(selected_skills)
                    top_careers = ", ".join([c.get("title", c.get("job_title", "")) for c in career_matches[:3]])
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"I currently know: {skills_text}. My target careers are: {top_careers}. Provide a month-by-month study roadmap to bridge my skill gaps."
                    })
                    st.rerun()
            else:
                st.info("No matching careers found for this specific combination.")
        else:
            st.info("Select one or more skills above to run the matching engine.")


# =========================================================================
# TAB 5: 🎤 MOCK INTERVIEW
# =========================================================================
with tabs[4]:
    st.markdown("### 🎤 AI-Powered Mock Interview Simulator")
    st.caption("Prepare for JKSSB, KAS, campus placements, and viva examinations with real-time AI rubric scoring.")

    if "interview_session" not in st.session_state:
        st.session_state.interview_session = None

    templates = get_all_templates()

    if st.session_state.interview_session is None:
        template_id = st.selectbox(
            "🎯 Select Interview Category",
            options=list(templates.keys()),
            format_func=lambda x: f"{templates[x].get('title', x)}",
            key="tab_iv_template"
        )

        if template_id and templates.get(template_id):
            tmpl = templates[template_id]
            st.markdown(f"**{tmpl.get('title', template_id)}** — {tmpl.get('description', '')}")
            st.caption(f"📋 {len(tmpl.get('rounds', []))} Rounds · {tmpl.get('questions_per_round', 3)} Questions/Round · Difficulty: **{tmpl.get('difficulty', 'moderate').upper()}**")

        if st.button("▶️ Launch Mock Interview Session", key="btn_launch_iv_tab"):
            session = start_interview(template_id)
            st.session_state.interview_session = session
            first_q = get_next_question(session)
            if first_q:
                st.session_state.current_iv_question = first_q
            st.rerun()
    else:
        session = st.session_state.interview_session

        if session.get("status") == "completed":
            st.markdown("### 🏆 Interview Session Complete!")
            report = generate_interview_report(session)
            st.markdown(report)
            if st.button("🔄 Start Another Practice Interview", key="btn_new_iv_tab"):
                st.session_state.interview_session = None
                if "current_iv_question" in st.session_state:
                    del st.session_state["current_iv_question"]
                st.rerun()
        else:
            progress = get_interview_progress(session)
            st.progress(
                progress.get("completed_questions", 0) / max(progress.get("total_questions", 1), 1),
                text=f"Round: {progress.get('current_round_name', 'N/A')} | Question {progress.get('completed_questions', 0)+1} of {progress.get('total_questions', '?')}"
            )

            current_q = st.session_state.get("current_iv_question")
            if current_q:
                st.markdown(f"#### Round {current_q.get('round_number', 0)+1}: {current_q.get('round_name', '')}")
                st.markdown(f"❓ **Question:** {current_q.get('question', 'Loading...')}")

                answer = st.text_area("Your Response (Speak your thoughts or type clearly):", key=f"iv_ans_tab_{progress.get('completed_questions', 0)}", height=130)

                btn_c1, btn_c2 = st.columns([1, 1])
                with btn_c1:
                    if st.button("📤 Submit Response for AI Evaluation", key="btn_sub_iv_tab"):
                        if answer.strip():
                            updated_session = submit_answer(session, answer.strip())
                            st.session_state.interview_session = updated_session

                            if updated_session.get("responses"):
                                last = updated_session["responses"][-1]
                                score = last.get("total_score", last.get("score_breakdown", {}).get("total_score", "N/A"))
                                feedback = last.get("feedback", "")
                                st.success(f"Evaluated Score: {score}/100 — {feedback[:200]}")

                            next_q = get_next_question(updated_session)
                            if next_q:
                                st.session_state.current_iv_question = next_q
                            else:
                                updated_session["status"] = "completed"
                                st.session_state.interview_session = updated_session
                            st.rerun()
                        else:
                            st.warning("Please provide your answer before submitting.")
                with btn_c2:
                    if st.button("⏹️ Conclude Session Early", key="btn_end_iv_tab"):
                        session["status"] = "completed"
                        st.session_state.interview_session = session
                        st.rerun()


# =========================================================================
# TAB 6: 📄 RESUME STUDIO
# =========================================================================
with tabs[5]:
    st.markdown("### 📄 AI Resume Auditor & Job-Fit Analyzer")
    st.caption("Upload your CV/resume in PDF format for automated rubric scoring, formatting critique, and role-match analysis.")

    uploaded_resume = st.file_uploader("📎 Upload Resume PDF", type=["pdf"], key="tab_resume_upload")
    target_role = st.selectbox(
        "🎯 Select Desired Career / Target Role",
        ["None"] + get_available_target_roles(),
        key="tab_resume_role"
    )
    target_role_val = None if target_role == "None" else target_role

    if uploaded_resume:
        try:
            resume_text = extract_text_from_pdf(uploaded_resume)
            if resume_text and len(resume_text.strip()) > 20:
                analysis = analyze_resume(resume_text, target_role=target_role_val)
                scores = analysis.get("scores", {})

                # Visual 4-dimension progress bars
                st.markdown("#### 📊 Resume Performance Metrics")
                s_col1, s_col2 = st.columns(2)
                with s_col1:
                    st.caption(f"Completeness: {scores.get('completeness', 0)}/25")
                    st.progress(scores.get('completeness', 0) / 25)
                    st.caption(f"Content Quality: {scores.get('content_quality', 0)}/25")
                    st.progress(scores.get('content_quality', 0) / 25)
                with s_col2:
                    st.caption(f"Role Relevance: {scores.get('relevance', 0)}/25")
                    st.progress(scores.get('relevance', 0) / 25)
                    st.caption(f"ATS Formatting: {scores.get('formatting', 0)}/25")
                    st.progress(scores.get('formatting', 0) / 25)

                report = render_resume_report(analysis)
                st.markdown(report)

                if st.button("🤖 Generate Detailed AI Narrative Review", key="btn_ai_rev_tab"):
                    with st.spinner("AI Counselor is auditing your resume structure..."):
                        try:
                            ai_review = get_ai_review(resume_text, target_role=target_role_val)
                            st.markdown("### 🤖 Senior Career Advisor Feedback")
                            st.markdown(ai_review)
                        except Exception as e:
                            st.warning(f"AI review service unavailable: {str(e)[:100]}. See the automated scorecard above.")

                if target_role_val:
                    job_results = search_jobs(target_role_val)
                    if job_results:
                        comparison = compare_to_job_requirements(
                            analysis.get("sections", {}),
                            job_results[0]
                        )
                        if comparison:
                            st.markdown("### 📊 Target Job Compatibility")
                            st.metric("Job Competency Match", f"{comparison.get('match_percentage', 0)}%")
                            if comparison.get("skill_overlap"):
                                st.markdown(f"✅ **Demonstrated Skills:** {', '.join(comparison['skill_overlap'][:8])}")
                            if comparison.get("missing_skills"):
                                st.markdown(f"❌ **Missing Competencies:** {', '.join(comparison['missing_skills'][:8])}")
                            st.caption(f"💡 {comparison.get('recommendation', '')}")
            else:
                st.warning("Insufficient readable text extracted. Please ensure the PDF is not a scanned image.")
        except Exception as e:
            st.error(f"Error auditing resume: {str(e)[:200]}")


# =========================================================================
# TAB 7: 📊 ADMIN PORTAL (CONDITIONALLY UNLOCKED)
# =========================================================================
if len(tabs) > 6:
    with tabs[6]:
        st.markdown("### 📊 Institutional Dropout Prevention & Cohort Analytics")
        st.caption("🔒 Verified Administrative View · Government of Jammu & Kashmir Education Department")

        if "admin_cohort" not in st.session_state:
            st.session_state.admin_cohort = simulate_demo_cohort(50)

        cohort = st.session_state.admin_cohort
        analytics = get_cohort_analytics(cohort)

        admin_c1, admin_c2, admin_c3, admin_c4 = st.columns(4)
        with admin_c1:
            st.metric("👥 Monitored Students", analytics["total_students"])
        with admin_c2:
            at_risk = analytics["risk_distribution"].get("High", 0) + analytics["risk_distribution"].get("Critical", 0)
            st.metric("⚠️ At-Risk Students", at_risk, delta=f"-{at_risk}" if at_risk > 0 else "0", delta_color="inverse")
        with admin_c3:
            st.metric("📊 Cohort Avg CGPA", f"{analytics['avg_cgpa']:.2f}")
        with admin_c4:
            st.metric("🎓 Scholarship Coverage", f"{analytics.get('scholarship_rate', 0):.0f}%")

        st.markdown("#### Risk Distribution Breakdown")
        risk_dist = analytics["risk_distribution"]
        dist_cols = st.columns(4)
        colors = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
        for i, (cat, count) in enumerate(risk_dist.items()):
            with dist_cols[i]:
                st.markdown(f"{colors.get(cat, '')} **{cat}**: {count} Students")

        st.bar_chart(risk_dist)

        alerts = get_priority_alerts(cohort)
        if alerts:
            st.markdown(f"#### 🚨 Priority Dropout Intervention Alerts ({len(alerts)} flagged)")
            for alert in alerts[:8]:
                student = alert.get("student", alert)
                risk = alert.get("risk_result", {})
                name = student.get("name", "Unknown")
                program = student.get("program", "")
                risk_score = risk.get("total_score", 0)
                risk_cat = risk.get("risk_category", "Unknown")
                risk_color = risk.get("risk_color", "⚪")

                with st.expander(f"{risk_color} {name} ({program}) — Risk: {risk_score:.0f}/100 [{risk_cat}]"):
                    st.markdown(get_student_summary(student))
                    interventions = alert.get("interventions", generate_intervention_plan(student, risk))
                    if interventions:
                        st.markdown("**📋 Prescribed Interventions:**")
                        for iv in interventions[:5]:
                            if isinstance(iv, dict):
                                st.caption(f"{iv.get('icon', '•')} **[{iv.get('priority', '')}]** {iv.get('action', str(iv))} — *{iv.get('responsible', '')} ({iv.get('timeline', '')})*")
                            else:
                                st.caption(f"• {iv}")

        st.markdown("#### 🔍 Student Roster Search")
        student_search = st.text_input("Search student records by name, ID, or institution...", key="admin_search_tab")
        if student_search:
            found = search_students(cohort, student_search)
            st.markdown(f"Found {len(found)} records:")
            for s in found[:8]:
                risk_r = calculate_risk_score(s)
                st.caption(f"{risk_r.get('risk_color', '⚪')} **{s['name']}** ({s['id']}) | {s['program']} @ {s['institution']} | CGPA: {s['cgpa']} | Risk: {risk_r['total_score']:.0f}/100")

        if st.button("📥 Export Comprehensive Cohort Advisory Report", key="btn_export_cohort_tab"):
            report_text = export_cohort_report(analytics)
            st.markdown(report_text)
