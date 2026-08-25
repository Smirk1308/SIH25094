"""
Streamlit Web Application for Margdarshak J&K - AI Career Advisor.
Features:
- Full responsive Dashboard with 5 specific ordered sections
- RAG pipeline powered by ChromaDB, all-MiniLM-L6-v2 embeddings, and Groq API
- Persistent conversation memory (last 3 exchanges) with multi-turn query contextualization
"""

import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine, DEFAULT_GROQ_MODEL, DOCS_DIR, CHROMA_DIR

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Margdarshak J&K | AI Career Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling and mobile responsiveness
st.markdown("""
<style>
    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 50%, #047857 100%);
        color: white;
        padding: 32px 28px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        color: #FFFFFF;
    }
    .hero-tagline {
        font-size: 1.15rem;
        font-weight: 500;
        color: #E0E7FF;
        margin-bottom: 0;
        line-height: 1.5;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(4px);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 12px;
        color: #F8FAFC;
    }

    /* Section Headings */
    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-top: 18px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-desc {
        font-size: 0.98rem;
        color: #334155;
        line-height: 1.6;
        margin-bottom: 16px;
    }

    /* Audience Cards */
    .audience-card {
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-top: 4px solid #1E40AF;
        border-radius: 10px;
        padding: 18px 16px;
        margin-bottom: 14px;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .audience-icon {
        font-size: 1.8rem;
        margin-bottom: 8px;
    }
    .audience-title {
        font-weight: 700;
        font-size: 1.05rem;
        color: #0F172A;
        margin-bottom: 6px;
    }
    .audience-desc {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.45;
    }

    /* Feature Cards */
    .feature-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 14px;
        margin-bottom: 12px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        min-height: 110px;
    }
    .feature-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.08);
    }
    .feature-icon {
        font-size: 1.6rem;
        margin-bottom: 6px;
    }
    .feature-name {
        font-weight: 700;
        font-size: 0.98rem;
        color: #1E293B;
        margin-bottom: 4px;
    }
    .feature-sub {
        font-size: 0.84rem;
        color: #64748B;
        line-height: 1.35;
    }

    /* Source chunk card styling */
    .source-card {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        margin-bottom: 10px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .source-badge {
        display: inline-block;
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .similarity-badge {
        display: inline-block;
        background-color: #DCFCE7;
        color: #166534;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .stat-box {
        background-color: #F1F5F9;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
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
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/parse-resumes.png", width=70)
    st.title("Advisor Settings")
    
    # 1. Groq API Key
    st.subheader("🔑 Groq API Settings")
    env_api_key = os.getenv("GROQ_API_KEY", "")
    api_key_input = st.text_input(
        "Groq API Key",
        value=env_api_key,
        type="password",
        help="Get your free API key from https://console.groq.com/keys"
    )
    
    # Dynamically fetch available models for this key
    available_models = rag_engine.get_available_groq_models(api_key_input)
    default_index = 0
    if "llama3-8b-8192" in available_models:
        default_index = available_models.index("llama3-8b-8192")

    groq_model = st.selectbox(
        "LLM Model",
        options=available_models,
        index=default_index,
        help="Models available for your Groq account. Default: llama3-8b-8192"
    )

    st.divider()

    # 2. Knowledge Base & Document Management
    st.subheader("📚 Knowledge Base (`/docs`)")
    
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
        <div class="stat-box">
            <b>📊 Knowledge Base Stats</b><br>
            • Indexed Chunks: <b>{stats['total_chunks']}</b><br>
            • PDFs in <code>/docs</code>: <b>{len(stats['pdf_files'])}</b><br>
            • Storage: <code>/chroma_db</code>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if stats["pdf_files"]:
        with st.expander("📄 View Files in /docs"):
            for f in stats["pdf_files"]:
                st.caption(f"• {f}")

    st.divider()

    # 3. Retrieval Configuration
    st.subheader("⚙️ Retrieval Settings")
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
<div class="hero-banner">
    <span class="hero-badge">🎓 AI CAREER GUIDANCE PORTAL</span>
    <div class="hero-title">Margdarshak J&K</div>
    <div class="hero-tagline">Free. Cited. Offline-ready. Career guidance for every student in J&K.</div>
</div>
""", unsafe_allow_html=True)

# 2. WHY THIS PLATFORM EXISTS
st.markdown('<div class="section-title">💡 Why this platform exists</div>', unsafe_allow_html=True)
st.markdown("""
<p class="section-desc">
    <b>J&K has fewer than 200 career counselors for 2 million students. Most rural schools have none. This platform gives every student a free, 24/7 AI advisor that answers from real government documents.</b>
</p>
""", unsafe_allow_html=True)

# Visual Metric Counters
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric(label="Career Counselors", value="< 200", delta="Severe shortage", delta_color="inverse")
with m_col2:
    st.metric(label="Students in J&K", value="2.0 Million", delta="Target audience")
with m_col3:
    st.metric(label="Advisor Availability", value="24 / 7", delta="Instant access")
with m_col4:
    st.metric(label="Cost to Students", value="₹0 Free", delta="Open for all")

st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

# 3. WHO IT'S FOR
st.markdown('<div class="section-title">👥 Who it\'s for</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="audience-card">
        <div class="audience-icon">🎓</div>
        <div class="audience-title">Class 12 Students</div>
        <div class="audience-desc">
            Deciding stream, degree courses, entrance examinations (CUET, JEE, NEET), and college options across Jammu & Kashmir and all-India universities.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="audience-card" style="border-top-color: #059669;">
        <div class="audience-icon">💰</div>
        <div class="audience-title">Scholarships & Aid Seekers</div>
        <div class="audience-desc">
            Discovering PMSSS (Prime Minister's Special Scholarship Scheme for J&K), National Scholarship Portal (NSP), minority grants, and fee waivers.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="audience-card" style="border-top-color: #7C3AED;">
        <div class="audience-icon">🌱</div>
        <div class="audience-title">First-Generation Learners</div>
        <div class="audience-desc">
            Clear, step-by-step guidance for students with no family guidance navigating admissions, paperwork, eligibility criteria, and job readiness.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

# 4. KEY FEATURES
st.markdown('<div class="section-title">⚡ Key Features</div>', unsafe_allow_html=True)

f_row1_col1, f_row1_col2, f_row1_col3 = st.columns(3)
with f_row1_col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📶</div>
        <div class="feature-name">2G Operability</div>
        <div class="feature-sub">Works on slow connections and low-bandwidth rural networks.</div>
    </div>
    """, unsafe_allow_html=True)

with f_row1_col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📑</div>
        <div class="feature-name">Cited Answers</div>
        <div class="feature-sub">Every response links directly to verified source documents.</div>
    </div>
    """, unsafe_allow_html=True)

with f_row1_col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <div class="feature-name">Multilingual</div>
        <div class="feature-sub">Supports queries in Hindi and English.</div>
    </div>
    """, unsafe_allow_html=True)

f_row2_col1, f_row2_col2, f_row2_col3 = st.columns(3)
with f_row2_col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💸</div>
        <div class="feature-name">Zero Cost</div>
        <div class="feature-sub">Completely free with no paywalls or hidden subscriptions.</div>
    </div>
    """, unsafe_allow_html=True)

with f_row2_col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🏛️</div>
        <div class="feature-name">Government Data Only</div>
        <div class="feature-sub">Grounded strictly in authentic notifications — no hallucination.</div>
    </div>
    """, unsafe_allow_html=True)

with f_row2_col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💾</div>
        <div class="feature-name">Offline Cache</div>
        <div class="feature-sub">Top queries and vector indices pre-loaded for high speed.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

# 5. HOW TO USE
st.markdown('<div class="section-title">📋 How to Use — 3 Simple Rules</div>', unsafe_allow_html=True)

r_col1, r_col2, r_col3 = st.columns(3)
with r_col1:
    st.info("📏 **Rule 1: Keep queries under 200 characters**\n\nConcise questions give the fastest and most accurate matching.")
with r_col2:
    st.success("🎯 **Rule 2: Be specific**\n\nInclude your **marks**, **district**, and **stream** (e.g., *'Class 12 Medical, 85%, Anantnag'*).")
with r_col3:
    st.info("❓ **Rule 3: Ask one question at a time**\n\nBreak multi-part queries into single, focused questions for precise answers.")

st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

# ==========================================
# INTERACTIVE CHAT ADVISOR
# ==========================================
st.markdown('<div class="section-title">💬 Ask Your Career Advisor</div>', unsafe_allow_html=True)

# Notification if no API key or empty vector DB
if not api_key_input:
    st.info("💡 Please enter your **Groq API Key** in the sidebar to start asking questions.", icon="🔑")

stats = rag_engine.get_collection_stats()
if stats["total_chunks"] == 0:
    st.warning("⚠️ No documents are currently indexed in `/docs`. Please upload PDFs in the sidebar and click **Re-index All Documents**.", icon="📁")

# Quick Prompt Suggestions (when chat is empty)
if len(st.session_state.messages) == 0:
    st.caption("🌟 **Click any suggested question to get started:**")
    col1, col2 = st.columns(2)
    
    sample_queries = [
        "What are the eligibility and stipend details for PMSSS J&K Scholarship?",
        "What are the best career paths after Class 12 Science (Medical vs Non-Medical)?",
        "How do I apply for government scholarships on National Scholarship Portal (NSP)?",
        "What are the essential technical skills and roadmap for Software Engineering?"
    ]

    selected_prompt = None
    with col1:
        if st.button(f"🎓 {sample_queries[0]}", use_container_width=True):
            selected_prompt = sample_queries[0]
        if st.button(f"🔬 {sample_queries[1]}", use_container_width=True):
            selected_prompt = sample_queries[1]
    with col2:
        if st.button(f"💰 {sample_queries[2]}", use_container_width=True):
            selected_prompt = sample_queries[2]
        if st.button(f"💻 {sample_queries[3]}", use_container_width=True):
            selected_prompt = sample_queries[3]

    if selected_prompt:
        st.session_state.messages.append({"role": "user", "content": selected_prompt})
        st.rerun()

# Display Conversation History at the start of each rerender
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="💼"):
            st.markdown(msg["content"])
            # Display source citations if attached
            if "sources" in msg and msg["sources"]:
                model_label = f" (Model: {msg.get('model_used', 'LLM')})" if msg.get('model_used') else ""
                with st.expander(f"📚 View {len(msg['sources'])} Cited Source Chunks from ChromaDB{model_label}"):
                    for i, src in enumerate(msg["sources"], 1):
                        source_name = src.get("source", "Unknown Document")
                        page_num = src.get("page", "?")
                        sim = src.get("similarity", 0.0)
                        dist = src.get("distance", 0.0)
                        text_preview = src.get("text", "")
                        
                        st.markdown(
                            f"""
                            <div class="source-card">
                                <div>
                                    <span class="source-badge">Source {i}: {source_name} (Page {page_num})</span>
                                    <span class="similarity-badge">Similarity: {sim:.2f} (Dist: {dist:.3f})</span>
                                </div>
                                <div style="margin-top: 6px; color: #334155;">
                                    {text_preview}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

# Chat Input Handler
user_input = st.chat_input("Ask about college admissions, PMSSS, scholarships, or careers (e.g. 'PMSSS eligibility for Class 12')...")

# Process user input (either from chat_input or pre-seeded prompt)
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# If the last message is from the user, generate response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    current_prompt = st.session_state.messages[-1]["content"]

    if not api_key_input:
        with st.chat_message("assistant", avatar="💼"):
            st.error("Please provide your Groq API Key in the sidebar to generate an answer.")
    else:
        with st.chat_message("assistant", avatar="💼"):
            try:
                # Call Groq LLM with persistent conversation history (last 3 exchanges)
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
                    with st.spinner("Generating advice grounded in your documents..."):
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

                # Show sources expander
                if retrieved_sources:
                    query_note = f" | Search: '{search_query}'" if search_query != current_prompt else ""
                    with st.expander(f"📚 View {len(retrieved_sources)} Cited Source Chunks from ChromaDB (Model: {model_used}{query_note})"):
                        for i, src in enumerate(retrieved_sources, 1):
                            source_name = src.get("source", "Unknown Document")
                            page_num = src.get("page", "?")
                            sim = src.get("similarity", 0.0)
                            dist = src.get("distance", 0.0)
                            text_preview = src.get("text", "")
                            
                            st.markdown(
                                f"""
                                <div class="source-card">
                                    <div>
                                        <span class="source-badge">Source {i}: {source_name} (Page {page_num})</span>
                                        <span class="similarity-badge">Similarity: {sim:.2f} (Dist: {dist:.3f})</span>
                                    </div>
                                    <div style="margin-top: 6px; color: #334155;">
                                        {text_preview}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

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
