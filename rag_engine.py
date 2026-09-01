"""
RAG Engine for Career Advisor Application.
Handles:
1. Loading and parsing PDF files from docs/
2. Token-based chunking (300 tokens with 50-token overlap)
3. Embedding with HuggingFace all-MiniLM-L6-v2
4. Persistent ChromaDB storage in chroma_db/
5. Top-5 relevant chunk retrieval
6. Contextual prompt assembly & Groq LLM querying (llama3-8b-8192)
"""

import os
import glob
import time
import hashlib
import json
from typing import List, Dict, Any, Optional, Generator
from pypdf import PdfReader
import tiktoken
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq

# Default Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "career_advisor_docs"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_GROQ_MODEL = "llama3-8b-8192"

# Token Splitting Settings
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
TOKENIZER_ENCODING = "cl100k_base"

# Singleton cached embedding function to slash cold start latency
_CACHED_EMBEDDING_FN = None

def get_embedding_function():
    """Cached singleton embedding function preventing model reload overhead."""
    global _CACHED_EMBEDDING_FN
    if _CACHED_EMBEDDING_FN is None:
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        _CACHED_EMBEDDING_FN = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
    return _CACHED_EMBEDDING_FN


class DocumentChunker:
    """Chunks text into token-based windows with configurable overlap."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP, encoding_name: str = TOKENIZER_ENCODING):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into 300-token chunks with 50-token overlap."""
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return []

        chunks = []
        step = max(1, self.chunk_size - self.chunk_overlap)
        chunk_index = 0

        for start_idx in range(0, total_tokens, step):
            end_idx = min(start_idx + self.chunk_size, total_tokens)
            chunk_tokens = tokens[start_idx:end_idx]
            
            chunk_text = self.encoding.decode(chunk_tokens).strip()
            if chunk_text:
                chunk_meta = dict(metadata)
                chunk_meta["chunk_index"] = chunk_index
                chunk_meta["token_count"] = len(chunk_tokens)
                chunk_meta["start_token"] = start_idx
                chunk_meta["end_token"] = end_idx
                
                chunks.append({
                    "id": f"{metadata.get('source', 'doc')}_p{metadata.get('page', 1)}_c{chunk_index}",
                    "text": chunk_text,
                    "metadata": chunk_meta
                })
                chunk_index += 1

            if end_idx >= total_tokens:
                break

        return chunks


class RAGEngine:
    """Manages ChromaDB vector store, document indexing, retrieval, and Groq generation."""

    def __init__(self, docs_dir: str = DOCS_DIR, chroma_dir: str = CHROMA_DIR):
        self.docs_dir = docs_dir
        self.chroma_dir = chroma_dir
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.chroma_dir, exist_ok=True)

        self.chunker = DocumentChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        
        # Cached HuggingFace all-MiniLM-L6-v2 embedding function
        self.embedding_fn = get_embedding_function()
        
        # Persistent ChromaDB client and collection
        self.chroma_client = None
        self.collection = None
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure ChromaDB client and collection handles are healthy and synchronized."""
        try:
            if self.chroma_client is None:
                self.chroma_client = chromadb.PersistentClient(path=self.chroma_dir)
            self.collection = self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
            # Lightweight verification call
            self.collection.count()
        except Exception:
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_dir)
            self.collection = self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )

    def load_and_parse_documents(self) -> List[Dict[str, Any]]:
        """Extract text page-by-page from all PDFs and TXT files in the docs directory."""
        extracted_chunks = []

        # 1. Parse PDFs
        pdf_files = glob.glob(os.path.join(self.docs_dir, "*.pdf"))
        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            try:
                reader = PdfReader(pdf_path)
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    if not page_text.strip():
                        continue
                    
                    page_meta = {
                        "source": filename,
                        "page": page_idx + 1,
                        "file_path": pdf_path
                    }
                    
                    page_chunks = self.chunker.chunk_text(page_text, page_meta)
                    extracted_chunks.extend(page_chunks)
            except Exception as e:
                print(f"Error reading PDF {filename}: {e}")

        # 2. Parse Text (.txt) Files
        txt_files = glob.glob(os.path.join(self.docs_dir, "*.txt"))
        for txt_path in txt_files:
            filename = os.path.basename(txt_path)
            try:
                with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if not content.strip():
                    continue

                txt_meta = {
                    "source": filename,
                    "page": 1,
                    "file_path": txt_path
                }
                txt_chunks = self.chunker.chunk_text(content, txt_meta)
                extracted_chunks.extend(txt_chunks)
            except Exception as e:
                print(f"Error reading TXT {filename}: {e}")

        return extracted_chunks

    def load_and_parse_pdfs(self) -> List[Dict[str, Any]]:
        """Backward-compatible wrapper for load_and_parse_documents."""
        return self.load_and_parse_documents()

    def index_documents(self, force_reindex: bool = False) -> Dict[str, Any]:
        """Index or re-index all PDFs and TXT files from docs/ into persistent ChromaDB."""
        self._ensure_collection()

        if force_reindex:
            try:
                # Clear all existing documents from collection without destroying the collection handle
                existing = self.collection.get()
                if existing and existing.get("ids") and len(existing["ids"]) > 0:
                    del_batch = 200
                    for i in range(0, len(existing["ids"]), del_batch):
                        self.collection.delete(ids=existing["ids"][i:i + del_batch])
            except Exception as e:
                # If collection state was broken, re-initialize client and collection
                try:
                    self.chroma_client.delete_collection(COLLECTION_NAME)
                except Exception:
                    pass
                self._ensure_collection()
        else:
            # Purge any stale chunks whose source files were deleted from /docs
            try:
                existing_data = self.collection.get()
                stale_ids = []
                if existing_data and existing_data.get("metadatas"):
                    for doc_id, meta in zip(existing_data["ids"], existing_data["metadatas"]):
                        src = meta.get("source")
                        if src and not os.path.exists(os.path.join(self.docs_dir, src)):
                            stale_ids.append(doc_id)
                if stale_ids:
                    del_batch = 200
                    for i in range(0, len(stale_ids), del_batch):
                        self.collection.delete(ids=stale_ids[i:i + del_batch])
            except Exception as e:
                print(f"Warning cleaning stale chunks: {e}")

        chunks = self.load_and_parse_documents()
        if not chunks:
            count = self.collection.count()
            return {
                "status": "empty",
                "indexed_chunks": 0,
                "total_chunks_in_db": count,
                "message": "No documents found in docs/ folder."
            }

        # Prepare records for ChromaDB batch insertion
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        # Use upsert in batches with error recovery for Rust/SQLite bindings
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            batch_ids = ids[i:end]
            batch_docs = documents[i:end]
            batch_metas = metadatas[i:end]
            try:
                self.collection.upsert(
                    ids=batch_ids,
                    documents=batch_docs,
                    metadatas=batch_metas
                )
            except Exception:
                # Re-sync collection handle in case of Rust/SQLite binding desync
                self._ensure_collection()
                self.collection.upsert(
                    ids=batch_ids,
                    documents=batch_docs,
                    metadatas=batch_metas
                )

        total_count = self.collection.count()
        return {
            "status": "success",
            "indexed_chunks": len(chunks),
            "total_chunks_in_db": total_count,
            "message": f"Successfully indexed {len(chunks)} chunks into ChromaDB."
        }

    def _get_docs_fingerprint(self) -> str:
        """Generate a fast timestamp/size fingerprint of all files in docs_dir."""
        files = sorted(glob.glob(os.path.join(self.docs_dir, "*")))
        sig_parts = []
        for f in files:
            if f.endswith((".pdf", ".txt")):
                st_stat = os.stat(f)
                sig_parts.append(f"{os.path.basename(f)}:{st_stat.st_mtime}:{st_stat.st_size}")
        return hashlib.md5(";".join(sig_parts).encode()).hexdigest()

    def _get_manifest_path(self) -> str:
        return os.path.join(self.chroma_dir, ".sync_manifest.json")

    def sync_documents(self, force_reindex: bool = False) -> Dict[str, Any]:
        """Fast synchronization between /docs and ChromaDB.
        Uses fingerprint cache to complete in <1ms when files haven't changed.
        """
        self._ensure_collection()
        manifest_path = self._get_manifest_path()
        current_fp = self._get_docs_fingerprint()

        # Fast path: If collection already has data and manifest matches, skip heavy sync
        if not force_reindex and os.path.exists(manifest_path) and self.collection.count() > 0:
            try:
                with open(manifest_path, "r", encoding="utf-8") as mf:
                    cached = json.load(mf)
                if cached.get("fingerprint") == current_fp:
                    return {
                        "status": "cached_up_to_date",
                        "total_chunks_in_db": self.collection.count(),
                        "fast_sync": True
                    }
            except Exception:
                pass

        # If fingerprint differs or force_reindex is requested, index documents
        res = self.index_documents(force_reindex=force_reindex)

        # Save new manifest
        try:
            with open(manifest_path, "w", encoding="utf-8") as mf:
                json.dump({
                    "fingerprint": current_fp,
                    "total_chunks": self.collection.count(),
                    "synced_at": time.time()
                }, mf)
        except Exception:
            pass

        return res

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed collection and documents."""
        self._ensure_collection()
        count = self.collection.count()
        pdf_files = [os.path.basename(f) for f in glob.glob(os.path.join(self.docs_dir, "*.pdf"))]
        txt_files = [os.path.basename(f) for f in glob.glob(os.path.join(self.docs_dir, "*.txt"))]
        return {
            "total_chunks": count,
            "pdf_files": pdf_files,
            "txt_files": txt_files,
            "all_files": pdf_files + txt_files,
            "docs_dir": self.docs_dir,
            "chroma_dir": self.chroma_dir
        }

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant chunks from ChromaDB for a given query."""
        self._ensure_collection()
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            ids = results["ids"][0] if "ids" in results else [""] * len(docs)

            for doc, meta, dist, chunk_id in zip(docs, metas, dists, ids):
                similarity = round(1 - dist, 4) if dist is not None else 0.0
                retrieved.append({
                    "id": chunk_id,
                    "text": doc,
                    "metadata": meta,
                    "distance": dist,
                    "similarity": similarity,
                    "source": meta.get("source", "Unknown"),
                    "page": meta.get("page", 1)
                })

        return retrieved

    @staticmethod
    def format_conversation_history(history: Optional[List[Dict[str, Any]]], max_exchanges: int = 3) -> str:
        """Format the last N conversation exchanges (up to 2*N messages) into a clean string for context injection."""
        if not history:
            return "No previous conversation."
        
        # Last 3 exchanges = up to 6 messages (3 user + 3 assistant)
        max_messages = max_exchanges * 2
        recent_turns = [m for m in history if m.get("role") in ["user", "assistant"]][-max_messages:]
        
        if not recent_turns:
            return "No previous conversation."
            
        formatted = []
        for turn in recent_turns:
            role = "User" if turn.get("role") == "user" else "Assistant"
            content = turn.get("content", "").strip()
            formatted.append(f"{role}: {content}")
            
        return "\n".join(formatted)

    def contextualize_query(
        self,
        query: str,
        history: Optional[List[Dict[str, Any]]],
        client: Groq,
        model: str = DEFAULT_GROQ_MODEL
    ) -> str:
        """Reformulate follow-up questions (e.g., 'what about scholarships for that?') into a standalone query using conversation history."""
        if not history or len(history) < 2:
            return query

        history_context = self.format_conversation_history(history, max_exchanges=3)
        if history_context == "No previous conversation.":
            return query

        condense_prompt = f"""Given the following conversation history between a user and a Career Advisor, and a follow-up question from the user, rephrase the follow-up question into a concise, standalone search query that includes all necessary context (such as the specific role, degree, skill, or field previously mentioned).

Conversation History (Last 3 Exchanges):
{history_context}

Follow-up Question: {query}

Instructions:
- If the question contains pronouns or references like 'that', 'it', 'for this', 'for that', replace them with the concrete subject from the conversation.
- Output ONLY the standalone search query. Do NOT answer the question.

Standalone Query:"""

        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": condense_prompt}],
                max_tokens=60,
                temperature=0.0
            )
            standalone = resp.choices[0].message.content.strip().strip('"\'')
            return standalone if standalone else query
        except Exception:
            return query

    def build_prompt(self, query: str, context_chunks: List[Dict[str, Any]], history_str: str = "") -> str:
        """Construct the prompt combining retrieved context, conversation history, and user question."""
        if not context_chunks:
            context_str = "No specific reference documents available."
        else:
            formatted_chunks = []
            for i, chunk in enumerate(context_chunks, 1):
                source = chunk.get("source", "Document")
                page = chunk.get("page", "?")
                formatted_chunks.append(
                    f"--- Source [{i}]: {source} (Page {page}) ---\n{chunk.get('text', '')}"
                )
            context_str = "\n\n".join(formatted_chunks)

        history_section = ""
        if history_str and history_str != "No previous conversation.":
            history_section = f"Conversation History (Last 3 Exchanges):\n{history_str}\n\n"

        prompt = f"""You are an expert AI Career Advisor. Guide the user with professional, actionable, and structured advice.

{history_section}Retrieved Context from Career Documents:
{context_str}

Current User Question: {query}

Instructions:
1. Provide a comprehensive, structured response (using bullet points, bold key terms, and step-by-step guidance).
2. Take into account previous conversation context and follow-up intent.
3. Ground your advice in the provided reference context wherever applicable.
4. If the context does not fully answer the question, supplement with industry-standard career best practices while clearly distinguishing general advice.
5. Reference the specific sources (e.g., [Source 1], [Source 2]) when referencing facts from the documents.
"""
        return prompt

    @staticmethod
    def get_available_groq_models(api_key: str) -> List[str]:
        """Fetch active text generation models available for this Groq API key."""
        if not api_key:
            return ["llama3-8b-8192", "llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma2-9b-it"]
        try:
            client = Groq(api_key=api_key)
            model_list = client.models.list()
            active_models = []
            for m in model_list.data:
                model_id = m.id
                # Filter out whisper, vision-preview, embedding, and safety guard models
                if any(excluded in model_id.lower() for excluded in ["whisper", "guard", "embed", "safet"]):
                    continue
                active_models.append(model_id)
            
            # Prioritize llama3-8b-8192 if present, otherwise sort
            if "llama3-8b-8192" in active_models:
                active_models.remove("llama3-8b-8192")
                active_models.insert(0, "llama3-8b-8192")
            
            return active_models if active_models else ["llama3-8b-8192", "llama-3.3-70b-versatile", "llama3-70b-8192"]
        except Exception:
            return ["llama3-8b-8192", "llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma2-9b-it"]

    def generate_answer(
        self,
        query: str,
        api_key: str,
        model: str = DEFAULT_GROQ_MODEL,
        top_k: int = 5,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Any:
        """Retrieve context and generate answer via Groq API with persistent conversation memory."""
        client = Groq(api_key=api_key)

        # 1. Contextualize query if there is conversation history (for follow-up questions like "what about scholarships for that?")
        search_query = self.contextualize_query(query, history, client=client, model=model)
        
        # 2. Retrieve top-k context chunks using the contextualized search query
        context_chunks = self.retrieve(search_query, top_k=top_k)

        # 3. Format the last 3 exchanges (up to 6 messages) as conversation history
        history_str = self.format_conversation_history(history, max_exchanges=3)
        prompt = self.build_prompt(query, context_chunks, history_str=history_str)

        # 4. Assemble messages for chat completion
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful, authoritative, and encouraging Career Advisor. "
                    "You provide actionable career guidance, resume suggestions, interview strategies, "
                    "and technical roadmaps based on provided documentation and industry standards. "
                    "Maintain continuity with the ongoing conversation."
                )
            }
        ]

        # Pass the last 3 exchanges (up to 6 turns) as role-based chat history
        if history:
            recent_turns = [turn for turn in history if turn.get("role") in ["user", "assistant"]][-6:]
            for turn in recent_turns:
                messages.append({"role": turn["role"], "content": turn["content"]})

        messages.append({"role": "user", "content": prompt})

        def try_create_completion(target_model: str, is_stream: bool):
            return client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=0.4,
                max_tokens=2048,
                stream=is_stream
            )

        # Attempt with requested model, fallback if model_not_found
        try:
            if stream:
                response_stream = try_create_completion(model, is_stream=True)
                
                def stream_generator() -> Generator[str, None, None]:
                    for chunk in response_stream:
                        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content

                return {
                    "stream": stream_generator(),
                    "sources": context_chunks,
                    "search_query": search_query,
                    "model_used": model
                }
            else:
                response = try_create_completion(model, is_stream=False)
                content = response.choices[0].message.content
                return {
                    "answer": content,
                    "sources": context_chunks,
                    "search_query": search_query,
                    "model_used": model
                }
        except Exception as e:
            err_str = str(e)
            # If model was not found (404), attempt fallback to standard llama3-8b-8192 or llama-3.3-70b-versatile
            if "model_not_found" in err_str or "404" in err_str:
                fallback_models = [m for m in ["llama3-8b-8192", "llama-3.3-70b-versatile", "llama3-70b-8192"] if m != model]
                for fb_model in fallback_models:
                    try:
                        if stream:
                            response_stream = try_create_completion(fb_model, is_stream=True)
                            def stream_generator_fb() -> Generator[str, None, None]:
                                for chunk in response_stream:
                                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                                        yield chunk.choices[0].delta.content
                            return {
                                "stream": stream_generator_fb(),
                                "sources": context_chunks,
                                "search_query": search_query,
                                "model_used": fb_model
                            }
                        else:
                            response = try_create_completion(fb_model, is_stream=False)
                            content = response.choices[0].message.content
                            return {
                                "answer": content,
                                "sources": context_chunks,
                                "search_query": search_query,
                                "model_used": fb_model
                            }
                    except Exception:
                        continue
            raise e


