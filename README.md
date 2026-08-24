# Walkthrough - RAG Career Advisor Streamlit Application

We have built and verified the complete **RAG-based Career Advisor Streamlit App** powered by **ChromaDB**, HuggingFace **`all-MiniLM-L6-v2`**, and the **Groq API** (`llama3-8b-8192`).

---

## 🏗️ Architecture & Component Overview

```
 ┌────────────────────────────────────────────────────────┐
 │                    Streamlit UI                        │
 │  • Chat Input (st.chat_input)                          │
 │  • Real-time Streaming Responses                       │
 │  • Top-5 Expandable Source Citations & Similarity      │
 │  • PDF File Uploader & Re-index Controls               │
 └─────────────┬────────────────────────────▲─────────────┘
               │ (User Query)               │ (Answer + Sources)
               ▼                            │
 ┌──────────────────────────┐    ┌──────────┴─────────────┐
 │       RAG Engine         │    │       Groq API         │
 │  • 300-token chunker     │───►│ • Model: llama3-8b-8192│
 │  • 50-token overlap      │    │ • Grounded Synthesis   │
 └─────────────┬────────────┘    └────────────────────────┘
               │
    (Embeddings: all-MiniLM-L6-v2)
               │
               ▼
 ┌──────────────────────────┐
 │    Persistent ChromaDB   │
 │     Folder: /chroma_db   │
 │   • Top-5 Cosine Search  │
 └──────────────────────────┘
```

---

## 📁 Implemented Files & Deliverables

| File | Purpose |
|---|---|
| [`requirements.txt`](file:///c:/Users/shubh/Downloads/sih25094/requirements.txt) | Python dependencies (`streamlit`, `chromadb`, `sentence-transformers`, `groq`, `pypdf`, `tiktoken`, `python-dotenv`, `reportlab`). |
| [`rag_engine.py`](file:///c:/Users/shubh/Downloads/sih25094/rag_engine.py) | Document chunker (300 tokens, 50 overlap), HuggingFace embedding generator, ChromaDB manager (`/chroma_db`), Top-5 retriever, and Groq LLM interface (`llama3-8b-8192`). |
| [`app.py`](file:///c:/Users/shubh/Downloads/sih25094/app.py) | Full Streamlit web UI with chat interface, expandable source citations, live knowledge base metrics, and PDF upload capabilities. |
| [`create_sample_docs.py`](file:///c:/Users/shubh/Downloads/sih25094/create_sample_docs.py) | Generates sample career guide PDFs in `/docs` (SWE Career Guide, Data Science & AI Roadmap). |
| [`test_rag.py`](file:///c:/Users/shubh/Downloads/sih25094/test_rag.py) | Unit and integration test suite validating chunking, indexing, retrieval, and prompt formatting. |
| [`.env.example`](file:///c:/Users/shubh/Downloads/sih25094/.env.example) | Environment variable template for `GROQ_API_KEY`. |
| [`README.md`](file:///c:/Users/shubh/Downloads/sih25094/README.md) | Comprehensive setup, configuration, and execution guide. |

---

## 🧪 Verification Results

We executed the automated test suite [`test_rag.py`](file:///c:/Users/shubh/Downloads/sih25094/test_rag.py) which verified all components:

```bash
> python test_rag.py

test_01_token_chunker: Test that text is chunked into <= 300 token pieces with overlap. ... OK
test_02_pdf_loading_and_indexing: Test indexing PDFs into persistent ChromaDB. ... OK
test_03_top_5_retrieval: Test retrieving top-5 chunks from ChromaDB for career queries. ... OK
test_04_prompt_construction: Test that prompt contains the retrieved context and citation markers. ... OK
test_05_collection_stats: Test get_collection_stats returns valid info. ... OK

----------------------------------------------------------------------
Ran 5 tests in 82.828s
OK

[Test 03] Query: 'How to write a resume using Google XYZ formula and prepare for coding rounds?' -> Retrieved 5 chunks.
[Top Result Source]: software_engineering_career_guide.pdf (Page 1) - Sim: 0.5754
```

---

