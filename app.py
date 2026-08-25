"""
Streamlit Web Application for Margdarshak J&K - AI Career Advisor.
Complete Custom Visual Theme:
- Deep teal (#1B3A4B) & Saffron orange (#E8762C) palette on light (#F7F9FC) background
- Google Font Inter typography
- Custom user & bot chat bubbles with source citations
- Pill-shaped suggested query chips in a 2-column grid
- Custom HTML dashboard cards with subtle shadow and 4px saffron top border
- Persistent conversation memory (last 3 exchanges) with Groq LLaMA-3
"""

import os
import html
import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine, DEFAULT_GROQ_MODEL, DOCS_DIR, CHROMA_DIR

# Load environment variables
load_dotenv()

# Page configuration - Wide layout and custom title
st.set_page_config(
    page_title="Margdarshak J&K | AI Career Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SINGLE INJECTED CSS BLOCK AT STARTUP
# ==========================================
st.markdown("""
<style>
    /* 1. Import Google Font Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* 2. Global Resets & Typography */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #F7F9FC !important;
        color: #1B3A4B !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #1B3A4B !important;
        letter-spacing: -0.3px;
    }

    p, span, label, div, li {
        font-family: 'Inter', sans-serif !important;
        font-weight: 400;
    }

    /* 3. Remove Default Streamlit Branding & Menus */
    #MainMenu { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    header { visibility: hidden !important; display: none !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* 4. Page Container Padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1200px;
    }

    /* 5. Solid Deep Teal Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1B3A4B !important;
        color: #FFFFFF !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    .sidebar-brand-header {
        font-size: 1.25rem;
        font-weight: 800;
        color: #FFFFFF;
        padding: 10px 0 16px 0;
        border-bottom: 1.5px solid rgba(232, 118, 44, 0.5);
        margin-bottom: 16px;
        letter-spacing: -0.3px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #132A37 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }

    .sidebar-stat-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
        color: #F1F5F9;
        font-size: 0.85rem;
        line-height: 1.5;
    }

    /* 6. Saffron Orange Buttons */
    div.stButton > button {
        background-color: #E8762C !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(232, 118, 44, 0.25) !important;
    }
    div.stButton > button:hover {
        background-color: #C4621F !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(196, 98, 31, 0.35) !important;
    }
    div.stButton > button:active {
        transform: scale(0.98);
    }

    /* 7. Pill-Shaped Suggested Query Chips (2-column grid) */
    .chip-container div.stButton > button {
        border-radius: 20px !important;
        background-color: transparent !important;
        color: #1B3A4B !important;
        border: 1.5px solid #1B3A4B !important;
        font-weight: 500 !important;
        font-size: 0.86rem !important;
        padding: 10px 16px !important;
        box-shadow: none !important;
        text-align: left !important;
        width: 100% !important;
        height: 100% !important;
        white-space: normal !important;
        line-height: 1.3 !important;
    }
    .chip-container div.stButton > button:hover {
        background-color: #1B3A4B !important;
        color: #FFFFFF !important;
        border-color: #1B3A4B !important;
        box-shadow: 0 3px 8px rgba(27, 58, 75, 0.2) !important;
    }

    /* 8. Hero Banner */
    .hero-banner-custom {
        background: linear-gradient(135deg, #1B3A4B 0%, #244D63 55%, #152E3C 100%);
        color: #FFFFFF;
        padding: 36px 30px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(27, 58, 75, 0.12);
        border-bottom: 4px solid #E8762C;
    }
    .hero-tag-badge {
        display: inline-block;
        background: rgba(232, 118, 44, 0.2);
        border: 1px solid #E8762C;
        color: #FFD8BA;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
    }
    .hero-main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .hero-tagline-text {
        font-size: 1.15rem;
        color: #E2E8F0;
        font-weight: 400;
        line-height: 1.5;
    }

    /* 9. Dashboard Cards */
    .dash-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #E8762C;
        border-radius: 12px;
        padding: 20px 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .dash-card-icon {
        font-size: 1.8rem;
        margin-bottom: 10px;
    }
    .dash-card-title {
        font-weight: 700;
        font-size: 1.05rem;
        color: #1B3A4B;
        margin-bottom: 6px;
    }
    .dash-card-body {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.5;
    }

    /* Metric counter cards */
    .metric-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #E8762C;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 600;
        margin-top: 4px;
    }

    /* 10. Section Headings */
    .section-title-custom {
        font-size: 1.35rem;
        font-weight: 700;
        color: #1B3A4B;
        margin-top: 24px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-desc-custom {
        font-size: 0.98rem;
        color: #334155;
        line-height: 1.6;
        margin-bottom: 16px;
    }

    /* 11. Custom Chat Bubbles */
    .chat-bubble-container {
        display: flex;
        flex-direction: column;
        gap: 14px;
        margin-top: 16px;
        margin-bottom: 20px;
    }
    .chat-row-user {
        display: flex;
        justify-content: flex-end;
        width: 100%;
        margin-bottom: 10px;
    }
    .chat-bubble-user {
        background-color: #1B3A4B;
        color: #FFFFFF !important;
        padding: 14px 18px;
        border-radius: 16px 16px 4px 16px;
        max-width: 78%;
        font-size: 0.94rem;
        line-height: 1.5;
        box-shadow: 0 2px 10px rgba(27, 58, 75, 0.15);
        word-break: break-word;
    }
    .chat-bubble-user * {
        color: #FFFFFF !important;
    }
    .chat-row-bot {
        display: flex;
        justify-content: flex-start;
        width: 100%;
        margin-bottom: 14px;
    }
    .chat-bubble-bot {
        background-color: #FFFFFF;
        color: #1E293B;
        border-left: 3px solid #E8762C;
        padding: 18px 22px;
        border-radius: 4px 16px 16px 16px;
        max-width: 85%;
        font-size: 0.94rem;
        line-height: 1.6;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        word-break: break-word;
    }
    .chat-bubble-bot-title {
        font-weight: 700;
        color: #1B3A4B;
        font-size: 0.92rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .sources-container {
        margin-top: 14px;
        padding-top: 10px;
        border-top: 1px solid #F1F5F9;
        font-size: 0.82rem;
        color: #64748B;
    }
    .source-pill-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 3px solid #E8762C;
        padding: 8px 12px;
        border-radius: 6px;
        margin-top: 6px;
        color: #475569;
        font-size: 0.8rem;
    }
    .source-tag {
        display: inline-block;
        background-color: #FFF0E6;
        color: #C4621F;
        font-weight: 600;
        font-size: 0.72rem;
        padding: 2px 8px;
        border-radius: 10px;
        margin-right: 6px;
    }

    /* 12. Chat Input Container */
    [data-testid="stChatInput"] {
        border-radius: 12px !important;
        border: 1.5px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #E8762C !important;
    }
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

if "auto_indexed_once" not in st.session_state:
    stats = rag_engine.get_collection_stats()
    if stats["total_chunks"] == 0 and len(stats["pdf_files"]) > 0:
        rag_engine.index_documents(force_reindex=False)
    st.session_state.auto_indexed_once = True


# ==========================================
# SIDEBAR CONTROLS (Solid #1B3A4B Theme)
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-brand-header">🎓 Margdarshak J&K</div>', unsafe_allow_html=True)
    
    # 1. Groq API Key
    st.markdown("<p style='font-weight:600; font-size:0.95rem; margin-bottom:4px;'>🔑 Groq API Settings</p>", unsafe_allow_html=True)
    env_api_key = os.getenv("GROQ_API_KEY", "")
    api_key_input = st.text_input(
        "Groq API Key",
        value=env_api_key,
        type="password",
        help="Get your free API key from https://console.groq.com/keys",
        label_visibility="collapsed"
    )
    
    # Dynamically fetch available models for this key
    available_models = rag_engine.get_available_groq_models(api_key_input)
    default_index = 0
    if "llama3-8b-8192" in available_models:
        default_index = available_models.index("llama3-8b-8192")

    st.markdown("<p style='font-weight:600; font-size:0.9rem; margin-top:8px; margin-bottom:2px;'>LLM Model</p>", unsafe_allow_html=True)
    groq_model = st.selectbox(
        "LLM Model",
        options=available_models,
        index=default_index,
        help="Models available for your Groq account. Default: llama3-8b-8192",
        label_visibility="collapsed"
    )

    st.divider()

    # 2. Knowledge Base & Document Management
    st.markdown("<p style='font-weight:600; font-size:0.95rem; margin-bottom:4px;'>📚 Knowledge Base (/docs)</p>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Upload PDF Guide(s)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Files will be saved into the /docs directory and indexed."
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(DOCS_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Saved {len(uploaded_files)} file(s) to docs/.")

    if st.button("🚀 Re-index All Documents", use_container_width=True):
        with st.spinner("Chunking PDFs & generating embeddings with all-MiniLM-L6-v2..."):
            result = rag_engine.index_documents(force_reindex=True)
            if result["status"] == "success":
                st.success(f"Indexed {result['indexed_chunks']} chunks into ChromaDB!")
            else:
                st.warning(result["message"])

    stats = rag_engine.get_collection_stats()
    st.markdown(
        f"""
        <div class="sidebar-stat-card">
            <b>📊 Vector Index Status</b><br>
            • Indexed Chunks: <b>{stats['total_chunks']}</b><br>
            • PDFs in <code>/docs</code>: <b>{len(stats['pdf_files'])}</b><br>
            • Storage: <code>/chroma_db</code>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if stats["pdf_files"]:
        with st.expander("📄 View PDF Files in /docs"):
            for f in stats["pdf_files"]:
                st.caption(f"• {f}")

    st.divider()

    # 3. Retrieval Configuration
    st.markdown("<p style='font-weight:600; font-size:0.95rem; margin-bottom:4px;'>⚙️ Retrieval Settings</p>", unsafe_allow_html=True)
    top_k = st.slider("Top Relevant Chunks (Top-K)", min_value=1, max_value=10, value=5)
    enable_stream = st.checkbox("Stream Responses", value=True)

    st.divider()

    # 4. Clear Chat
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ==========================================
# MAIN INTERFACE - REDESIGNED DASHBOARD
# ==========================================

# 1. HERO BANNER
st.markdown("""
<div class="hero-banner-custom">
    <span class="hero-tag-badge">🎓 AI CAREER GUIDANCE PORTAL</span>
    <div class="hero-main-title">Margdarshak J&K</div>
    <div class="hero-tagline-text">Free. Cited. Offline-ready. Career guidance for every student in J&K.</div>
</div>
""", unsafe_allow_html=True)


# 2. WHY THIS PLATFORM EXISTS
st.markdown('<div class="section-title-custom">💡 Why this platform exists</div>', unsafe_allow_html=True)
st.markdown("""
<p class="section-desc-custom">
    <b>J&K has fewer than 200 career counselors for 2 million students. Most rural schools have none. This platform gives every student a free, 24/7 AI advisor that answers from real government documents.</b>
</p>
""", unsafe_allow_html=True)

# 4 Metric Cards
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">&lt; 200</div>
        <div class="metric-label">Career Counselors in J&K</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">2.0M+</div>
        <div class="metric-label">Students Needing Guidance</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">24 / 7</div>
        <div class="metric-label">Free AI Advisor Access</div>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">₹0</div>
        <div class="metric-label">Cost to Students (Zero Cost)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)


# 3. WHO IT'S FOR
st.markdown('<div class="section-title-custom">👥 Who it\'s for</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">🎓</div>
        <div class="dash-card-title">Class 12 Students</div>
        <div class="dash-card-body">
            Deciding stream, degree courses, entrance examinations (CUET, JEE, NEET), and college options across Jammu & Kashmir and all-India universities.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">💰</div>
        <div class="dash-card-title">Scholarships & Financial Aid</div>
        <div class="dash-card-body">
            Discovering PMSSS (Prime Minister's Special Scholarship Scheme for J&K), National Scholarship Portal (NSP), minority grants, and fee waivers.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">🌱</div>
        <div class="dash-card-title">First-Generation Learners</div>
        <div class="dash-card-body">
            Step-by-step navigation for students with no family mentorship, guiding admission processes, eligibility criteria, and job readiness.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)


# 4. KEY FEATURES
st.markdown('<div class="section-title-custom">⚡ Key Features</div>', unsafe_allow_html=True)

f_row1_col1, f_row1_col2, f_row1_col3 = st.columns(3)
with f_row1_col1:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">📶</div>
        <div class="dash-card-title">2G Operability</div>
        <div class="dash-card-body">Works smoothly on slow connections and low-bandwidth networks in rural J&K.</div>
    </div>
    """, unsafe_allow_html=True)

with f_row1_col2:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">📑</div>
        <div class="dash-card-title">Cited Answers</div>
        <div class="dash-card-body">Every response links directly to verified official government source documents.</div>
    </div>
    """, unsafe_allow_html=True)

with f_row1_col3:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">🌐</div>
        <div class="dash-card-title">Multilingual</div>
        <div class="dash-card-body">Full support for questions asked in Hindi and English.</div>
    </div>
    """, unsafe_allow_html=True)

f_row2_col1, f_row2_col2, f_row2_col3 = st.columns(3)
with f_row2_col1:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">💸</div>
        <div class="dash-card-title">Zero Cost</div>
        <div class="dash-card-body">Completely free with no paywalls, subscriptions, or hidden charges.</div>
    </div>
    """, unsafe_allow_html=True)

with f_row2_col2:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">🏛️</div>
        <div class="dash-card-title">Government Data Only</div>
        <div class="dash-card-body">Grounded strictly in authentic notifications and verified curricula — zero hallucination.</div>
    </div>
    """, unsafe_allow_html=True)

with f_row2_col3:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">💾</div>
        <div class="dash-card-title">Offline Cache</div>
        <div class="dash-card-body">Top queries and vector indices pre-loaded locally for ultra-fast response times.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)


# 5. HOW TO USE (Custom HTML Cards - No Default st.info/st.success)
st.markdown('<div class="section-title-custom">📋 How to Use — 3 Simple Rules</div>', unsafe_allow_html=True)

r_col1, r_col2, r_col3 = st.columns(3)
with r_col1:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">📏</div>
        <div class="dash-card-title">Rule 1: Under 200 Characters</div>
        <div class="dash-card-body">Keep queries under 200 characters for the fastest and most accurate document matching.</div>
    </div>
    """, unsafe_allow_html=True)

with r_col2:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">🎯</div>
        <div class="dash-card-title">Rule 2: Be Specific</div>
        <div class="dash-card-body">Include your <b>marks</b>, <b>district</b>, and <b>stream</b> (e.g. <i>'Class 12 Medical, 85%, Anantnag'</i>).</div>
    </div>
    """, unsafe_allow_html=True)

with r_col3:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-icon">❓</div>
        <div class="dash-card-title">Rule 3: One Question at a Time</div>
        <div class="dash-card-body">Ask focused single queries to get clear, precise answers with verified citations.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 28px 0; border: none; border-top: 1.5px solid #E2E8F0;'>", unsafe_allow_html=True)


# ==========================================
# INTERACTIVE CHAT ADVISOR
# ==========================================
st.markdown('<div class="section-title-custom">💬 Ask Your Career Advisor</div>', unsafe_allow_html=True)

if not api_key_input:
    st.markdown("""
    <div style="background: #FFF7ED; border-left: 4px solid #E8762C; padding: 12px 16px; border-radius: 6px; font-size: 0.92rem; color: #9A3412; margin-bottom: 16px;">
        🔑 <b>Welcome!</b> Please enter your <b>Groq API Key</b> in the sidebar to start asking career and scholarship questions.
    </div>
    """, unsafe_allow_html=True)

stats = rag_engine.get_collection_stats()
if stats["total_chunks"] == 0:
    st.markdown("""
    <div style="background: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px 16px; border-radius: 6px; font-size: 0.92rem; color: #991B1B; margin-bottom: 16px;">
        📁 No documents are currently indexed in <code>/docs</code>. Please upload PDFs in the sidebar and click <b>Re-index All Documents</b>.
    </div>
    """, unsafe_allow_html=True)

# 7. Suggested Query Chips in a 2-Column Grid
if len(st.session_state.messages) == 0:
    st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #64748B; margin-bottom: 8px;'>🌟 Select a suggested topic or type your own question below:</p>", unsafe_allow_html=True)
    
    st.markdown('<div class="chip-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    sample_queries = [
        "🎓 What are the eligibility and stipend details for PMSSS J&K Scholarship?",
        "🔬 What are the best career paths after Class 12 Science (Medical vs Non-Medical)?",
        "💰 How do I apply for government scholarships on National Scholarship Portal (NSP)?",
        "💻 What are the essential technical skills and roadmap for Software Engineering?"
    ]

    selected_prompt = None
    with col1:
        if st.button(sample_queries[0], key="chip_0", use_container_width=True):
            selected_prompt = sample_queries[0]
        if st.button(sample_queries[1], key="chip_1", use_container_width=True):
            selected_prompt = sample_queries[1]
    with col2:
        if st.button(sample_queries[2], key="chip_2", use_container_width=True):
            selected_prompt = sample_queries[2]
        if st.button(sample_queries[3], key="chip_3", use_container_width=True):
            selected_prompt = sample_queries[3]
    st.markdown('</div>', unsafe_allow_html=True)

    if selected_prompt:
        st.session_state.messages.append({"role": "user", "content": selected_prompt})
        st.rerun()


# Display Conversation History with Custom Styled Chat Bubbles
for msg in st.session_state.messages:
    if msg["role"] == "user":
        # Right-aligned User Bubble (#1B3A4B background, white text)
        user_text = html.escape(msg["content"]).replace("\n", "<br>")
        st.markdown(f"""
        <div class="chat-row-user">
            <div class="chat-bubble-user">
                <b>🧑‍🎓 You:</b><br>{user_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Left-aligned Bot Bubble (#FFFFFF background, saffron left border #E8762C, gray citations)
        bot_text = msg["content"]
        
        # Build Citations HTML if available
        citations_html = ""
        if "sources" in msg and msg["sources"]:
            citations_items = []
            for i, src in enumerate(msg["sources"], 1):
                source_name = html.escape(src.get("source", "Government Document"))
                page_num = src.get("page", "?")
                sim = src.get("similarity", 0.0)
                preview = html.escape(src.get("text", "")[:180])
                citations_items.append(
                    f'<div class="source-pill-card">'
                    f'<span class="source-tag">Source {i}</span> <b>{source_name} (Page {page_num})</b> • Similarity: {sim:.2f}<br>'
                    f'<span style="color: #64748B;">"{preview}..."</span>'
                    f'</div>'
                )
            citations_html = f"""
            <div class="sources-container">
                <b>📑 Verified Reference Sources:</b>
                {''.join(citations_items)}
            </div>
            """
        
        model_badge = f" <span style='font-size:0.75rem; color:#64748B; font-weight:400;'>({msg.get('model_used', 'LLM')})</span>" if msg.get("model_used") else ""
        
        # Render markdown content inside clean bot card
        with st.container():
            st.markdown(f"""
            <div class="chat-row-bot">
                <div class="chat-bubble-bot">
                    <div class="chat-bubble-bot-title">💼 Margdarshak Career Advisor {model_badge}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(bot_text)
            if citations_html:
                st.markdown(citations_html, unsafe_allow_html=True)


# Chat Input Handler
user_input = st.chat_input("Ask about college admissions, PMSSS, scholarships, or careers...")

# Process user input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# If the last message is from the user, generate response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    current_prompt = st.session_state.messages[-1]["content"]

    if not api_key_input:
        st.markdown("""
        <div style="background: #FFF7ED; border-left: 4px solid #E8762C; padding: 12px 16px; border-radius: 6px; font-size: 0.92rem; color: #9A3412; margin-top: 12px;">
            Please provide your <b>Groq API Key</b> in the sidebar to generate an answer.
        </div>
        """, unsafe_allow_html=True)
    else:
        try:
            # Call Groq LLM with persistent conversation memory (last 3 exchanges)
            if enable_stream:
                gen_result = rag_engine.generate_answer(
                    query=current_prompt,
                    api_key=api_key_input,
                    model=groq_model,
                    top_k=top_k,
                    history=st.session_state.messages[:-1],
                    stream=True
                )
                full_response = st.write_stream(gen_result["stream"])
            else:
                with st.spinner("Generating grounded advice from official documents..."):
                    gen_result = rag_engine.generate_answer(
                        query=current_prompt,
                        api_key=api_key_input,
                        model=groq_model,
                        top_k=top_k,
                        history=st.session_state.messages[:-1],
                        stream=False
                    )
                    full_response = gen_result["answer"]
                    st.markdown(full_response)

            model_used = gen_result.get("model_used", groq_model)
            retrieved_sources = gen_result.get("sources", [])
            search_query = gen_result.get("search_query", current_prompt)

            # Display source citations below answer
            if retrieved_sources:
                citations_items = []
                for i, src in enumerate(retrieved_sources, 1):
                    source_name = html.escape(src.get("source", "Government Document"))
                    page_num = src.get("page", "?")
                    sim = src.get("similarity", 0.0)
                    preview = html.escape(src.get("text", "")[:180])
                    citations_items.append(
                        f'<div class="source-pill-card">'
                        f'<span class="source-tag">Source {i}</span> <b>{source_name} (Page {page_num})</b> • Similarity: {sim:.2f}<br>'
                        f'<span style="color: #64748B;">"{preview}..."</span>'
                        f'</div>'
                    )
                citations_html = f"""
                <div class="sources-container">
                    <b>📑 Verified Reference Sources:</b>
                    {''.join(citations_items)}
                </div>
                """
                st.markdown(citations_html, unsafe_allow_html=True)

            # Save assistant response to persistent session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sources": retrieved_sources,
                "model_used": model_used,
                "search_query": search_query
            })

        except Exception as e:
            st.error(f"Error communicating with Groq API: {str(e)}")
