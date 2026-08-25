"""
Streamlit Web Application for Margdarshak J&K - AI Career Advisor.
Uses only the targeted CSS block requested by the user.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine, DEFAULT_GROQ_MODEL, DOCS_DIR, CHROMA_DIR

# Load environment variables
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
# TARGETED CSS OVERRIDES ONLY
# ==========================================
st.markdown("""
<style>
/* Chat — user bubble */
[data-testid="stChatMessage"]:has(
  [data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] {
    background-color: #1B3A4B;
    color: white;
    border-radius: 12px;
    padding: 12px 16px;
}

/* Chat — bot bubble */
[data-testid="stChatMessage"]:has(
  [data-testid="stChatMessageAvatarAssistant"])
  [data-testid="stChatMessageContent"] {
    background-color: white;
    border-left: 4px solid #E8762C;
    border-radius: 12px;
    padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* Input box */
[data-testid="stChatInput"] textarea {
    border-radius: 12px;
    border: 2px solid #E8762C !important;
    background: white;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1B3A4B;
    padding-top: 1rem;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton button {
    background: #E8762C; color: white;
    border: none; border-radius: 8px;
    width: 100%;
}
[data-testid="collapsedControl"] {
    display: block; color: white;
}

/* Hide Streamlit chrome */
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

if "auto_indexed_once" not in st.session_state:
    stats = rag_engine.get_collection_stats()
    if stats["total_chunks"] == 0 and len(stats["pdf_files"]) > 0:
        rag_engine.index_documents(force_reindex=False)
    st.session_state.auto_indexed_once = True


# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.title("🎓 Margdarshak J&K")
    
    st.subheader("🤖 AI Model")
    available_models = rag_engine.get_available_groq_models(groq_api_key)
    default_index = 0
    if "llama3-8b-8192" in available_models:
        default_index = available_models.index("llama3-8b-8192")

    groq_model = st.selectbox(
        "Model",
        options=available_models,
        index=default_index,
        label_visibility="collapsed"
    )

    st.divider()

    st.subheader("📚 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload PDF Guide(s)",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(DOCS_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Saved {len(uploaded_files)} file(s) to docs/.")

    if st.button("🚀 Re-index All Documents"):
        with st.spinner("Chunking PDFs & generating embeddings..."):
            result = rag_engine.index_documents(force_reindex=True)
            if result["status"] == "success":
                st.success(f"Indexed {result['indexed_chunks']} chunks into ChromaDB!")
            else:
                st.warning(result["message"])

    stats = rag_engine.get_collection_stats()
    st.write(f"• **Indexed Chunks:** {stats['total_chunks']}")
    st.write(f"• **PDFs in `/docs`:** {len(stats['pdf_files'])}")

    if stats["pdf_files"]:
        with st.expander("📄 View PDF Files"):
            for f in stats["pdf_files"]:
                st.caption(f"• {f}")

    st.divider()

    st.subheader("⚙️ Settings")
    top_k = st.slider("Top Chunks (Top-K)", min_value=1, max_value=10, value=5)
    enable_stream = st.checkbox("Stream Responses", value=True)

    st.divider()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# ==========================================
# MAIN INTERFACE - DASHBOARD SECTIONS
# ==========================================

# 1. HERO BANNER
st.title("🎓 Margdarshak J&K")
st.markdown("### *Free. Cited. Offline-ready. Career guidance for every student in J&K.*")

st.divider()

# 2. WHY THIS PLATFORM EXISTS
st.subheader("💡 Why this platform exists")
st.markdown(
    "J&K has fewer than 200 career counselors for 2 million students. Most rural schools have none. "
    "This platform gives every student a free, 24/7 AI advisor that answers from real government documents."
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Career Counselors", "< 200")
m2.metric("Students in J&K", "2.0M+")
m3.metric("Availability", "24/7")
m4.metric("Cost to Students", "₹0 Free")

st.divider()

# 3. WHO IT'S FOR
st.subheader("👥 Who it's for")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### 🎓 Class 12 Students")
    st.write("Deciding stream, degree courses, entrance examinations (CUET, JEE, NEET), and college options across Jammu & Kashmir and all-India universities.")
with c2:
    st.markdown("#### 💰 Scholarships & Financial Aid")
    st.write("Discovering PMSSS (Prime Minister's Special Scholarship Scheme for J&K), National Scholarship Portal (NSP), minority grants, and fee waivers.")
with c3:
    st.markdown("#### 🌱 First-Generation Learners")
    st.write("Step-by-step guidance for students with no family guidance navigating admissions, paperwork, eligibility criteria, and job readiness.")

st.divider()

# 4. KEY FEATURES
st.subheader("⚡ Key Features")
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("##### 📶 2G Operability")
    st.caption("Works on slow connections and rural networks.")
with f2:
    st.markdown("##### 📑 Cited Answers")
    st.caption("Every response links to verified source documents.")
with f3:
    st.markdown("##### 🌐 Multilingual")
    st.caption("Supports queries in Hindi and English.")

f4, f5, f6 = st.columns(3)
with f4:
    st.markdown("##### 💸 Zero Cost")
    st.caption("Completely free for every student.")
with f5:
    st.markdown("##### 🏛️ Government Data Only")
    st.caption("Grounded in authentic notifications — no hallucination.")
with f6:
    st.markdown("##### 💾 Offline Cache")
    st.caption("Top queries and indices pre-loaded for high speed.")

st.divider()

# 5. HOW TO USE
st.subheader("📋 How to use")
r1, r2, r3 = st.columns(3)
with r1:
    st.info("📏 **Rule 1: Under 200 Characters**\n\nKeep queries under 200 characters for best results.")
with r2:
    st.success("🎯 **Rule 2: Be Specific**\n\nInclude your **marks**, **district**, and **stream** (e.g. *'Class 12 Medical, 85%, Anantnag'*).")
with r3:
    st.info("❓ **Rule 3: One Question at a Time**\n\nAsk one question at a time for precise answers.")

st.divider()

# ==========================================
# INTERACTIVE CHAT ADVISOR
# ==========================================
st.subheader("💬 Ask Your Career Advisor")

if not groq_api_key:
    st.error("⚠️ Groq API key is not configured in st.secrets['GROQ_API_KEY']. Please set it in .streamlit/secrets.toml.")

stats = rag_engine.get_collection_stats()
if stats["total_chunks"] == 0:
    st.warning("⚠️ No documents are currently indexed in `/docs`. Please upload PDFs in the sidebar and click **Re-index All Documents**.")

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
