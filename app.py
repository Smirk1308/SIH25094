"""
Streamlit Web Application for RAG-based Career Advisor.
Uses ChromaDB vector store, HuggingFace all-MiniLM-L6-v2 embeddings,
and Groq API (llama3-8b-8192) for fast, grounded career advice.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine, DEFAULT_GROQ_MODEL, DOCS_DIR, CHROMA_DIR

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Career Advisor | RAG Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main title and header */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
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
    /* Stat box in sidebar */
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
    # Check if DB is empty and documents exist; if so, run initial indexing
    stats = rag_engine.get_collection_stats()
    if stats["total_chunks"] == 0 and len(stats["pdf_files"]) > 0:
        rag_engine.index_documents(force_reindex=False)
    st.session_state.auto_indexed_once = True


# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/parse-resumes.png", width=70)
    st.title("Career Advisor Config")
    
    # 1. Groq API Key
    st.subheader("🔑 Groq API Settings")
    env_api_key = os.getenv("GROQ_API_KEY", "")
    api_key_input = st.text_input(
        "Groq API Key",
        value=env_api_key,
        type="password",
        help="Get your free API key from https://console.groq.com/keys"
    )
    
    groq_model = st.selectbox(
        "LLM Model",
        options=[
            "llama3-8b-8192",
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768"
        ],
        index=0,
        help="Default model requested: llama3-8b-8192"
    )

    st.divider()

    # 2. Knowledge Base & Document Management
    st.subheader("📚 Knowledge Base (`/docs`)")
    
    # Upload new PDF files
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

    # Re-index Button
    if st.button("🚀 Re-index All Documents", use_container_width=True):
        with st.spinner("Chunking PDFs & generating embeddings with all-MiniLM-L6-v2..."):
            result = rag_engine.index_documents(force_reindex=True)
            if result["status"] == "success":
                st.success(f"Indexed {result['indexed_chunks']} chunks into ChromaDB!")
            else:
                st.warning(result["message"])

    # Collection Stats
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
# MAIN INTERFACE
# ==========================================
st.markdown('<div class="main-header">💼 AI Career Advisor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Personalized career roadmaps, resume tips, and interview preparation '
    'grounded in your documents via <b>ChromaDB</b> & <b>Groq LLaMA-3</b>.</div>',
    unsafe_allow_html=True
)

# Notification if no API key or empty vector DB
if not api_key_input:
    st.info("💡 **Welcome!** Please enter your **Groq API Key** in the sidebar to start asking questions.", icon="🔑")

stats = rag_engine.get_collection_stats()
if stats["total_chunks"] == 0:
    st.warning("⚠️ No documents are currently indexed. Please place PDF files in the `/docs` folder or upload them in the sidebar and click **Re-index All Documents**.", icon="📁")

# Quick Prompt Suggestions (when chat is empty)
if len(st.session_state.messages) == 0:
    st.markdown("##### 🌟 Suggested Topics to Explore:")
    col1, col2 = st.columns(2)
    
    sample_queries = [
        "What are the essential technical skills for a Software Engineer?",
        "How should I structure my resume using the Google XYZ formula?",
        "What is the roadmap to transition into Data Science and AI?",
        "How should I prepare for coding and system design interviews?"
    ]

    selected_prompt = None
    with col1:
        if st.button(f"💡 {sample_queries[0]}", use_container_width=True):
            selected_prompt = sample_queries[0]
        if st.button(f"📄 {sample_queries[1]}", use_container_width=True):
            selected_prompt = sample_queries[1]
    with col2:
        if st.button(f"🤖 {sample_queries[2]}", use_container_width=True):
            selected_prompt = sample_queries[2]
        if st.button(f"🎯 {sample_queries[3]}", use_container_width=True):
            selected_prompt = sample_queries[3]

    if selected_prompt:
        st.session_state.messages.append({"role": "user", "content": selected_prompt})
        st.rerun()

# Display Conversation History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="💼"):
            st.markdown(msg["content"])
            # Display source citations if attached
            if "sources" in msg and msg["sources"]:
                with st.expander(f"📚 View {len(msg['sources'])} Cited Source Chunks from ChromaDB"):
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
user_input = st.chat_input("Ask about career paths, resume strategies, interview roadmaps, or skills...")

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
                # 1. Retrieve top-k chunks
                retrieved_sources = rag_engine.retrieve(current_prompt, top_k=top_k)
                
                # 2. Call Groq LLM
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

                # Show sources expander
                if retrieved_sources:
                    with st.expander(f"📚 View {len(retrieved_sources)} Cited Source Chunks from ChromaDB"):
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

                # Save assistant response to state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": retrieved_sources
                })

            except Exception as e:
                st.error(f"Error communicating with Groq API: {str(e)}")
