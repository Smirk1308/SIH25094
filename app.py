"""
Streamlit Web Application for Margdarshak J&K - AI Career Advisor.
Knowledge base is pre-loaded from /docs at startup with no document management UI.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine, DEFAULT_GROQ_MODEL, DOCS_DIR, CHROMA_DIR

# Load environment variables (fallback support)
load_dotenv()

# Retrieve GROQ_API_KEY securely from st.secrets
def get_groq_api_key() -> str:
    try:
        if "GROQ_API_KEY" in st.secrets:
            return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "").strip()

groq_api_key = get_groq_api_key()

# Page configuration
st.set_page_config(
    page_title="Margdarshak J&K | AI Career Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# GLOBAL CSS OVERRIDES
# ==========================================
st.markdown("""
<style>
/* Gradient sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D2137 0%, #1B3A4B 60%, #1E4D63 100%);
    border-right: 1px solid #E8762C33;
    padding-top: 1rem;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton button {
    background: #E8762C; color: white;
    border: none; border-radius: 8px;
    width: 100%; margin-top: 4px;
}
[data-testid="collapsedControl"] {
    display: block; color: white;
}

/* App background texture */
.stApp {
    background: linear-gradient(135deg, #EEF2F7 0%, #E8F0F7 50%, #EDF4F0 100%);
}

/* Main content area */
.main .block-container {
    padding-top: 1.5rem;
    max-width: 860px;
}

/* User chat bubble */
[data-testid="stChatMessage"]:has(
  [data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #1B3A4B, #0D2137);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 14px 18px;
    box-shadow: 0 4px 15px rgba(27,58,75,0.25);
}

/* Bot chat bubble */
[data-testid="stChatMessage"]:has(
  [data-testid="stChatMessageAvatarAssistant"])
  [data-testid="stChatMessageContent"] {
    background: white;
    border-left: 4px solid #E8762C;
    border-radius: 4px 18px 18px 18px;
    padding: 14px 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.07);
}

/* Input */
[data-testid="stChatInput"] textarea {
    border-radius: 14px;
    border: 2px solid #1B3A4B !important;
    background: white;
    box-shadow: 0 2px 8px rgba(27,58,75,0.1);
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #E8762C !important;
    box-shadow: 0 2px 12px rgba(232,118,44,0.2) !important;
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

# Pre-load & auto-index documents from /docs if not already in ChromaDB
if "auto_indexed_once" not in st.session_state:
    stats = rag_engine.get_collection_stats()
    if stats["total_chunks"] == 0 and len(stats["pdf_files"]) > 0:
        rag_engine.index_documents(force_reindex=False)
    st.session_state.auto_indexed_once = True


# ==========================================
# SIDEBAR CONTROLS (Clean, Query-Focused)
# ==========================================
with st.sidebar:
    st.title("🎓 Margdarshak J&K")
    
    # Automatic Model Selection using loaded Groq key
    st.subheader("🤖 AI Model")
    available_models = rag_engine.get_available_groq_models(groq_api_key)
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

    # Retrieval Configuration
    st.subheader("⚙️ Settings")
    top_k = st.slider("Top Relevant Chunks (Top-K)", min_value=1, max_value=10, value=5)
    enable_stream = st.checkbox("Stream Responses", value=True)

    st.divider()

    # Clear Chat History
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# ==========================================
# MAIN INTERFACE - DASHBOARD SECTIONS (HTML CARDS)
# ==========================================

# 1. HERO SECTION
st.markdown("""
<div style="background:linear-gradient(135deg,#1B3A4B 0%,#0D2137 100%);
     border-radius:16px; padding:32px 28px; margin-bottom:20px;
     border-bottom:4px solid #E8762C;">
  <div style="color:#E8762C;font-size:11px;font-weight:700;
       letter-spacing:2px;margin-bottom:8px;">
    SMART INDIA HACKATHON 2026 · SIH25094
  </div>
  <div style="color:white;font-size:24px;font-weight:700;
       line-height:1.3;margin-bottom:10px;">
    One-Stop Career & Education Advisor
  </div>
  <div style="color:#AEC6D0;font-size:14px;line-height:1.6;">
    Free · Cited · 2G-Ready · Government data only
  </div>
</div>
""", unsafe_allow_html=True)


# 2. STAT CARDS ROW
stat_col1, stat_col2, stat_col3 = st.columns(3)

with stat_col1:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px;
         border-top:4px solid #1B3A4B;box-shadow:0 2px 12px rgba(0,0,0,0.07);">
      <div style="font-size:28px;font-weight:800;color:#1B3A4B;">2M+</div>
      <div style="font-size:12px;color:#666;margin-top:4px;">
        Students in J&K with no career guidance
      </div>
    </div>
    """, unsafe_allow_html=True)

with stat_col2:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px;
         border-top:4px solid #E8762C;box-shadow:0 2px 12px rgba(0,0,0,0.07);">
      <div style="font-size:28px;font-weight:800;color:#E8762C;">&lt;200</div>
      <div style="font-size:12px;color:#666;margin-top:4px;">
        Career counselors for the entire state
      </div>
    </div>
    """, unsafe_allow_html=True)

with stat_col3:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px;
         border-top:4px solid #27AE60;box-shadow:0 2px 12px rgba(0,0,0,0.07);">
      <div style="font-size:28px;font-weight:800;color:#27AE60;">5 sec</div>
      <div style="font-size:12px;color:#666;margin-top:4px;">
        Cited answer from government documents
      </div>
    </div>
    """, unsafe_allow_html=True)


# 3. FEATURE CHIPS
st.markdown("""
<div style="display:flex;flex-wrap:wrap;gap:10px;margin:16px 0;">
  <span style="background:#E8F4F8;color:#1B3A4B;padding:8px 16px;
        border-radius:20px;font-size:13px;font-weight:600;
        border:1px solid #C5DCE8;">⚡ 2G Operability</span>
  <span style="background:#FEF3E8;color:#C4621F;padding:8px 16px;
        border-radius:20px;font-size:13px;font-weight:600;
        border:1px solid #F5C99A;">📄 Cited Answers</span>
  <span style="background:#EAF7EF;color:#1E8449;padding:8px 16px;
        border-radius:20px;font-size:13px;font-weight:600;
        border:1px solid #A9DFBF;">🏛️ Govt. Data Only</span>
  <span style="background:#F4ECFB;color:#6C3483;padding:8px 16px;
        border-radius:20px;font-size:13px;font-weight:600;
        border:1px solid #D7BDE2;">🌐 Hindi + English</span>
  <span style="background:#FDEDEC;color:#922B21;padding:8px 16px;
        border-radius:20px;font-size:13px;font-weight:600;
        border:1px solid #F1948A;">💸 Zero Cost</span>
</div>
""", unsafe_allow_html=True)


# ==========================================
# INTERACTIVE CHAT ADVISOR
# ==========================================
st.markdown("### 💬 Ask Your Career Advisor")

# Quick suggested queries when chat is empty
if len(st.session_state.messages) == 0:
    st.caption("🌟 Select a suggested topic or type your own question below:")
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

    if selected_prompt:
        st.session_state.messages.append({"role": "user", "content": selected_prompt})
        st.rerun()

# Display Conversation History using Streamlit chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                model_label = f" (Model: {msg.get('model_used', 'LLM')})" if msg.get('model_used') else ""
                with st.expander(f"📚 View {len(msg['sources'])} Cited Source Chunks from ChromaDB{model_label}"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.caption(f"**Source {i}: {src.get('source', 'Document')} (Page {src.get('page', '?')})** • Similarity: {src.get('similarity', 0.0):.2f}")
                        st.markdown(f"> {src.get('text', '')}")

# Chat Input Handler
user_input = st.chat_input("Ask about college admissions, PMSSS, scholarships, or careers...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# If the last message is from the user, generate response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    current_prompt = st.session_state.messages[-1]["content"]

    if not groq_api_key:
        with st.chat_message("assistant"):
            st.error("GROQ_API_KEY is missing from st.secrets. Please configure it in .streamlit/secrets.toml.")
    else:
        with st.chat_message("assistant"):
            try:
                if enable_stream:
                    gen_result = rag_engine.generate_answer(
                        query=current_prompt,
                        api_key=groq_api_key,
                        model=groq_model,
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

                if retrieved_sources:
                    query_note = f" | Search: '{search_query}'" if search_query != current_prompt else ""
                    with st.expander(f"📚 View {len(retrieved_sources)} Cited Source Chunks from ChromaDB (Model: {model_used}{query_note})"):
                        for i, src in enumerate(retrieved_sources, 1):
                            st.caption(f"**Source {i}: {src.get('source', 'Document')} (Page {src.get('page', '?')})** • Similarity: {src.get('similarity', 0.0):.2f}")
                            st.markdown(f"> {src.get('text', '')}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": retrieved_sources,
                    "model_used": model_used,
                    "search_query": search_query
                })

            except Exception as e:
                st.error(f"Error communicating with Groq API: {str(e)}")
