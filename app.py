"""
Streamlit Web Application for Margdarshak J&K - AI Career Advisor.
High-End Competitive UI with:
1. 🎨 Modern Glassmorphism & Plus Jakarta Sans typography.
2. ⚡ 2G Offline & Instant Query Engine (<10ms latency, zero API calls).
3. 🌐 AI Cloud Mode with Groq Llama 3 & ChromaDB vector search.
4. 🤖 Smart Auto-Detect with Zero-Downtime Fallback.
5. 🎯 3-Question Instant Scholarship & Career Eligibility Matcher.
6. 🗂️ Interactive Category Prompt Explorer (Scholarships, Medical, Engineering, Careers).
"""

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from rag_engine import RAGEngine, DEFAULT_GROQ_MODEL, DOCS_DIR, CHROMA_DIR
from offline_engine import offline_engine, get_2g_response
from error_handler import render_error_card, ErrorDiagnostic

# Load environment variables (fallback support)
load_dotenv()

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
    page_title="PathSeva | AI Career Advisor",
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
.main .block-container { padding-top: 1.5rem; max-width: 860px; }

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
  <div style="color:white;font-size:18px;font-weight:800;letter-spacing:1px;">
    PathSeva
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

    # Retrieval Configuration
    st.subheader("⚙️ Retrieval Settings")
    top_k = st.slider("Top Relevant Chunks (Top-K)", min_value=1, max_value=10, value=5)
    enable_stream = st.checkbox("Stream Responses", value=True)

    # Knowledge Base Stats
    stats = rag_engine.get_collection_stats()
    st.caption(f"📚 Knowledge Base: **{stats['total_chunks']} chunks** indexed from **{len(stats.get('all_files', []))} official documents**.")

    st.divider()

    # Clear Chat History
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# ==========================================
# MAIN INTERFACE - DASHBOARD HERO & METRICS
# ==========================================

# 1. HERO SECTION
st.markdown("""
<div style="background:linear-gradient(135deg,#0D2137 0%,#1B3A8C 60%,#1A6B3C 100%);
     border-radius:16px; padding:28px; margin-bottom:20px;
     border-bottom:4px solid #F5A623;">
  <div style="display:flex; align-items:center; gap:16px;">
    <img src="app/static/logo.png" width="70"
         style="border-radius:8px; flex-shrink:0;">
    <div>
      <div style="color:#F5A623;font-size:10px;font-weight:700;
           letter-spacing:2px;margin-bottom:4px;">
        SIH 2026 · SIH25094 · TEAM ERROR404
      </div>
      <div style="color:white;font-size:22px;font-weight:800;line-height:1.2;">
        PathSeva
      </div>
      <div style="color:#AEC6D0;font-size:13px;margin-top:4px;">
        Career & Education Advisor for J&K · Free · Cited · 2G-Ready
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


# 3. FEATURE CHIPS
st.markdown("""
<div style="display:flex;flex-wrap:wrap;gap:8px;margin:16px 0;">
  <span style="background:#E8F4F8;color:#1B3A4B;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #C5DCE8;">⚡ 2G Operability</span>
  <span style="background:#FEF3E8;color:#C4621F;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #F5C99A;">📄 Cited Answers</span>
  <span style="background:#EAF7EF;color:#1E8449;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #A9DFBF;">🏛️ Govt. Data Only</span>
  <span style="background:#F4ECFB;color:#6C3483;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #D7BDE2;">🌐 Hindi + English</span>
  <span style="background:#FDEDEC;color:#922B21;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #F1948A;">💸 Zero Cost</span>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. INTERACTIVE 3-QUESTION ELIGIBILITY WIZARD
# ==========================================
with st.expander("🎯 3-Question Instant Scholarship & Eligibility Checker", expanded=False):
    st.caption("Select your profile parameters below to see exact matching government schemes and scholarships:")
    wiz_col1, wiz_col2, wiz_col3 = st.columns(3)
    
    with wiz_col1:
        w_stream = st.selectbox(
            "🎓 Your Current Stream / Level",
            ["Class 12 Science (PCM)", "Class 12 Science (PCB)", "Commerce", "Arts & Humanities", "College Graduate"]
        )
    with wiz_col2:
        w_income = st.selectbox(
            "💰 Annual Household Income",
            ["Below ₹2.50 Lakh", "₹2.50 Lakh – ₹8.00 Lakh", "Above ₹8.00 Lakh"]
        )
    with wiz_col3:
        w_cat = st.selectbox(
            "🏛️ Domicile & Category",
            ["Open Merit (OM)", "Minority Community", "RBA / ALC / IB", "Scheduled Tribe (ST) / SC"]
        )

    # Compute matches
    matched_schemes = []
    if w_income in ["Below ₹2.50 Lakh", "₹2.50 Lakh – ₹8.00 Lakh"]:
        matched_schemes.append("🎓 **PMSSS J&K**: 5000 seats, full college fees + ₹1 Lakh/year maintenance allowance.")
    if w_income == "Below ₹2.50 Lakh":
        matched_schemes.append("💰 **Post-Matric Scholarship (NSP)**: Tuition fee reimbursement + monthly maintenance.")
    if w_cat == "Minority Community" and w_income == "Below ₹2.50 Lakh":
        matched_schemes.append("🌟 **Merit-cum-Means Minority Scholarship**: Up to ₹20,000 course fees for technical degrees.")
    if "Science" in w_stream:
        matched_schemes.append("🔬 **INSPIRE Scholarship (DST)**: ₹80,000/year for pure sciences students in top 1% board marks.")
    if w_cat in ["RBA / ALC / IB", "Scheduled Tribe (ST) / SC"]:
        matched_schemes.append("🏛️ **Category Quota & Tribal Affairs Aid**: Reserved seat allocations in JKCET & NEET + PMS-ST.")

    st.markdown("**🌟 Matching Opportunities for Your Profile:**")
    for s in matched_schemes:
        st.markdown(f"- {s}")
    
    if st.button("💬 Ask Advisor to Guide Me on These Schemes", key="btn_wiz"):
        st.session_state.messages.append({
            "role": "user",
            "content": f"Based on my profile ({w_stream}, income {w_income}, category {w_cat}), what scholarships and admissions can I apply for?"
        })
        st.rerun()


# ==========================================
# 5. CATEGORY-BASED QUERY EXPLORER
# ==========================================
if len(st.session_state.messages) == 0:
    st.markdown("### 🔍 Explore Topics or Ask Anything")
    
    cat_tab1, cat_tab2, cat_tab3, cat_tab4 = st.tabs(["💰 Scholarships", "🏥 Medical & NEET", "⚙️ Engineering", "💼 Govt & Careers"])
    selected_prompt = None
    
    with cat_tab1:
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("🎓 PMSSS J&K Eligibility & ₹1L Stipend", use_container_width=True, key="p_pmsss"):
                selected_prompt = "What are the eligibility and stipend details for PMSSS J&K Scholarship?"
            if st.button("💰 Post-Matric Scholarship (<₹2.5L Income)", use_container_width=True, key="p_post_mat"):
                selected_prompt = "How to apply for post-matric scholarship on NSP portal with 2.5 lakh income?"
        with sc2:
            if st.button("🌟 Minority Merit-cum-Means Scholarship", use_container_width=True, key="p_mcm"):
                selected_prompt = "What is the Merit-cum-Means scholarship for minority students?"
            if st.button("🔬 INSPIRE Scholarship (₹80,000/year)", use_container_width=True, key="p_inspire"):
                selected_prompt = "What are the eligibility criteria for INSPIRE Scholarship for science students?"

    with cat_tab2:
        mc1, mc2 = st.columns(2)
        with mc1:
            if st.button("🏥 GMC Srinagar & Jammu NEET Cutoffs", use_container_width=True, key="p_gmc"):
                selected_prompt = "What are the NEET UG cutoff marks for GMC Srinagar and GMC Jammu?"
            if st.button("🔬 SKIMS Soura & Bemina MBBS Admissions", use_container_width=True, key="p_skims"):
                selected_prompt = "What is the admission procedure and seat intake for SKIMS MBBS?"
        with mc2:
            if st.button("🌿 BAMS Ayurvedic & Unani AYUSH Colleges", use_container_width=True, key="p_bams"):
                selected_prompt = "What are the BAMS Ayurvedic and Unani college options in J&K?"
            if st.button("🩺 Class 12 PCB Career Roadmap (Nursing/Paramedical)", use_container_width=True, key="p_pcb"):
                selected_prompt = "What are the best career paths after Class 12 PCB besides MBBS?"

    with cat_tab3:
        ec1, ec2 = st.columns(2)
        with ec1:
            if st.button("🏛️ NIT Srinagar Branches & Home State Cutoffs", use_container_width=True, key="p_nit"):
                selected_prompt = "What are the JEE Main cutoffs and branches for NIT Srinagar Home State Quota?"
            if st.button("⚡ IUST Awantipora B.Tech Fees & Branches", use_container_width=True, key="p_iust"):
                selected_prompt = "What are the engineering branches and fee structure at IUST Awantipora?"
        with ec2:
            if st.button("📐 JKCET Engineering Exam Dates & Eligibility", use_container_width=True, key="p_jkcet"):
                selected_prompt = "What are the eligibility criteria and exam dates for JKCET engineering?"
            if st.button("💻 Software Engineering & Tech Roadmap", use_container_width=True, key="p_swe"):
                selected_prompt = "What is the complete roadmap and essential skills for Software Engineering?"

    with cat_tab4:
        gc1, gc2 = st.columns(2)
        with gc1:
            if st.button("📋 JKSSB Non-Gazetted Jobs & Exams", use_container_width=True, key="p_jkssb"):
                selected_prompt = "What government job recruitments are conducted by JKSSB in J&K?"
            if st.button("🏛️ JKPSC Civil Services (CCE / KAS)", use_container_width=True, key="p_jkpsc"):
                selected_prompt = "How to prepare for JKPSC Combined Competitive Examination (KAS)?"
        with gc2:
            if st.button("🏦 J&K Bank Banking Associate & PO Recruitment", use_container_width=True, key="p_jkbank"):
                selected_prompt = "What is the exam pattern and eligibility for J&K Bank recruitment?"
            if st.button("⚖️ Arts & Commerce Career Pathways (Law CLAT/CA)", use_container_width=True, key="p_arts_com"):
                selected_prompt = "What are the top career options in Arts and Commerce after Class 12?"

    if selected_prompt:
        st.session_state.messages.append({"role": "user", "content": selected_prompt})
        st.rerun()


# ==========================================
# 6. INTERACTIVE CHAT HISTORY DISPLAY
# ==========================================
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
user_input = st.chat_input("Ask about college admissions, PMSSS, scholarships, cutoffs, or careers...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# If the last message is from the user, generate response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    current_prompt = st.session_state.messages[-1]["content"]

    # =========================================================================
    # 1. 2G ULTRA-LITE MODE (Zero external API, Sub-10ms Instant Delivery)
    # =========================================================================
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
                # Fallback to local ChromaDB direct snippet extraction (no cloud LLM)
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

    # =========================================================================
    # 2. SMART AUTO-DETECT & AI CLOUD (Adaptive Hybrid Execution)
    # =========================================================================
    else:
        # Check 2G Cache first if in Smart Auto-Detect
        offline_match = get_2g_response(current_prompt) if network_mode == "🤖 Smart Auto-Detect" else None

        if offline_match and offline_match.get("confidence_score", 0) >= 3.5:
            # Instant delivery for high confidence pre-fed matches
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
            # Zero-downtime Fallback: Serve offline match or local Chroma chunks when API keys are missing
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
            # Full Groq RAG generation with graceful error recovery
            with st.chat_message("assistant"):
                try:
                    if enable_stream:
                        gen_result = rag_engine.generate_answer(
                            query=current_prompt,
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
                                query=current_prompt,
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
                    # Smart Fallback with personalized error diagnostic card
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
