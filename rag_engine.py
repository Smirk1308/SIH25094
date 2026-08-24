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
        
        # HuggingFace all-MiniLM-L6-v2 embedding function
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        
        # Persistent ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def load_and_parse_pdfs(self) -> List[Dict[str, Any]]:
        """Extract text page-by-page from all PDFs in the docs directory."""
        pdf_files = glob.glob(os.path.join(self.docs_dir, "*.pdf"))
        extracted_chunks = []

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

        return extracted_chunks

    def index_documents(self, force_reindex: bool = False) -> Dict[str, Any]:
        """Index or re-index all PDFs from docs/ into persistent ChromaDB."""
        if force_reindex:
            try:
                self.chroma_client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass
            self.collection = self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )

        chunks = self.load_and_parse_pdfs()
        if not chunks:
            count = self.collection.count()
            return {
                "status": "empty",
                "indexed_chunks": 0,
                "total_chunks_in_db": count,
                "message": "No PDF documents found in docs/ folder."
            }

        # Prepare records for ChromaDB batch insertion
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        # Use upsert to prevent duplication
        # Chroma handles batching automatically or in batches of 100
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            self.collection.upsert(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end]
            )

        total_count = self.collection.count()
        return {
            "status": "success",
            "indexed_chunks": len(chunks),
            "total_chunks_in_db": total_count,
            "message": f"Successfully indexed {len(chunks)} chunks into ChromaDB."
        }

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed collection and documents."""
        count = self.collection.count()
        pdf_files = [os.path.basename(f) for f in glob.glob(os.path.join(self.docs_dir, "*.pdf"))]
        return {
            "total_chunks": count,
            "pdf_files": pdf_files,
            "docs_dir": self.docs_dir,
            "chroma_dir": self.chroma_dir
        }

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant chunks from ChromaDB for a given query."""
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

    def build_prompt(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Construct the prompt combining retrieved context and user question."""
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

        prompt = f"""You are an expert AI Career Advisor. Guide the user with professional, actionable, and structured advice.

Here is the retrieved context from career guidance documents:
{context_str}

User Question: {query}

Instructions:
1. Provide a comprehensive, structured response (using bullet points, bold key terms, and step-by-step guidance).
2. Ground your advice in the provided context wherever applicable.
3. If the context does not fully answer the question, supplement with industry-standard career best practices while clearly distinguishing general advice.
4. Reference the specific sources (e.g., [Source 1], [Source 2]) when referencing facts from the documents.
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
        """Retrieve context and generate answer via Groq API with fallback support."""
        context_chunks = self.retrieve(query, top_k=top_k)
        prompt = self.build_prompt(query, context_chunks)

        client = Groq(api_key=api_key)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful, authoritative, and encouraging Career Advisor. "
                    "You provide actionable career guidance, resume suggestions, interview strategies, "
                    "and technical roadmaps based on provided documentation and industry standards."
                )
            }
        ]

        # Add conversation history if available (last 4 turns)
        if history:
            for turn in history[-4:]:
                if turn.get("role") in ["user", "assistant"]:
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
                    "model_used": model
                }
            else:
                response = try_create_completion(model, is_stream=False)
                content = response.choices[0].message.content
                return {
                    "answer": content,
                    "sources": context_chunks,
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
                                "model_used": fb_model
                            }
                        else:
                            response = try_create_completion(fb_model, is_stream=False)
                            content = response.choices[0].message.content
                            return {
                                "answer": content,
                                "sources": context_chunks,
                                "model_used": fb_model
                            }
                    except Exception:
                        continue
            raise e

