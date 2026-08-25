"""
Automated Test Suite for RAG Career Advisor.
Tests:
1. Token chunking with 300-token size and 50-token overlap.
2. PDF text extraction from docs/
3. ChromaDB persistent index creation with HuggingFace all-MiniLM-L6-v2 embeddings.
4. Top-5 relevant chunk retrieval.
5. Prompt construction and source formatting.
"""

import os
import sys
import unittest
from rag_engine import (
    DocumentChunker,
    RAGEngine,
    DOCS_DIR,
    CHROMA_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)
from create_sample_docs import generate_swe_guide, generate_ds_ai_guide


class TestRAGCareerAdvisor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Generate sample docs for testing
        generate_swe_guide()
        generate_ds_ai_guide()
        cls.engine = RAGEngine(docs_dir=DOCS_DIR, chroma_dir=CHROMA_DIR)

    def test_01_token_chunker(self):
        """Test that text is chunked into <= 300 token pieces with overlap."""
        chunker = DocumentChunker(chunk_size=300, chunk_overlap=50)
        # Create a text with ~700 tokens
        sample_text = ("Software engineering is the branch of computer science that deals with the design, "
                       "development, testing, and maintenance of software applications. ") * 40
        
        chunks = chunker.chunk_text(sample_text, {"source": "test.pdf", "page": 1})
        self.assertGreater(len(chunks), 1, "Should produce multiple chunks for long text")
        
        for c in chunks:
            token_count = c["metadata"]["token_count"]
            self.assertLessEqual(token_count, 300, f"Chunk size {token_count} exceeds 300 tokens")
            self.assertTrue(len(c["text"]) > 0, "Chunk text should not be empty")

    def test_02_pdf_loading_and_indexing(self):
        """Test indexing PDFs into persistent ChromaDB."""
        stats = self.engine.index_documents(force_reindex=True)
        self.assertEqual(stats["status"], "success")
        self.assertGreater(stats["indexed_chunks"], 0, "Should have indexed at least 1 chunk")
        self.assertGreaterEqual(stats["total_chunks_in_db"], stats["indexed_chunks"])

        # Check ChromaDB persistent files exist
        self.assertTrue(os.path.exists(CHROMA_DIR), "ChromaDB directory must exist")
        self.assertTrue(len(os.listdir(CHROMA_DIR)) > 0, "ChromaDB directory must contain persistent files")

    def test_03_top_5_retrieval(self):
        """Test retrieving top-5 chunks from ChromaDB for career queries."""
        query = "How to write a resume using Google XYZ formula and prepare for coding rounds?"
        retrieved = self.engine.retrieve(query, top_k=5)
        
        self.assertGreater(len(retrieved), 0, "Should retrieve at least one result")
        self.assertLessEqual(len(retrieved), 5, "Should retrieve at most 5 results")
        
        # Verify retrieved structure
        first = retrieved[0]
        self.assertIn("text", first)
        self.assertIn("source", first)
        self.assertIn("page", first)
        self.assertIn("similarity", first)
        self.assertIn("distance", first)
        print(f"\n[Test 03] Query: '{query}' -> Retrieved {len(retrieved)} chunks.")
        print(f"[Top Result Source]: {first['source']} (Page {first['page']}) - Sim: {first['similarity']}")

    def test_04_prompt_construction(self):
        """Test that prompt contains the retrieved context and citation markers."""
        query = "What skills are needed for Machine Learning and AI?"
        chunks = self.engine.retrieve(query, top_k=3)
        prompt = self.engine.build_prompt(query, chunks)
        
        self.assertIn("User Question:", prompt)
        self.assertIn("Source [1]:", prompt)
        self.assertIn(query, prompt)

    def test_05_collection_stats(self):
        """Test get_collection_stats returns valid info."""
        stats = self.engine.get_collection_stats()
        self.assertGreater(stats["total_chunks"], 0)
        self.assertTrue(len(stats["pdf_files"]) >= 2)

    def test_06_conversation_history_formatting(self):
        """Test formatting the last 3 exchanges (up to 6 messages) for context."""
        # 5 exchanges (10 messages)
        mock_history = [
            {"role": "user", "content": "Question 1: What is SWE?"},
            {"role": "assistant", "content": "Answer 1: SWE is software engineering."},
            {"role": "user", "content": "Question 2: What about Data Science?"},
            {"role": "assistant", "content": "Answer 2: Data Science is analyzing data."},
            {"role": "user", "content": "Question 3: How to become a ML Engineer?"},
            {"role": "assistant", "content": "Answer 3: Master PyTorch and MLOps."},
            {"role": "user", "content": "Question 4: What is the salary?"},
            {"role": "assistant", "content": "Answer 4: Salary ranges from $100k-$200k."},
            {"role": "user", "content": "Question 5: Can I get remote jobs?"},
            {"role": "assistant", "content": "Answer 5: Yes, remote jobs are common."}
        ]
        
        formatted = self.engine.format_conversation_history(mock_history, max_exchanges=3)
        # Should contain Question 3, 4, 5 and Answer 3, 4, 5 (last 3 exchanges)
        self.assertIn("Question 3", formatted)
        self.assertIn("Question 4", formatted)
        self.assertIn("Question 5", formatted)
        # Should NOT contain Question 1 and 2 (older exchanges)
        self.assertNotIn("Question 1", formatted)
        self.assertNotIn("Question 2", formatted)
        
        # Verify prompt with history
        prompt = self.engine.build_prompt("What about scholarships for that?", [], history_str=formatted)
        self.assertIn("Conversation History (Last 3 Exchanges):", prompt)
        self.assertIn("Question 5: Can I get remote jobs?", prompt)
        self.assertIn("Current User Question: What about scholarships for that?", prompt)

    def test_07_contextualize_query_fallback(self):
        """Test contextualize_query behavior when no client or empty history."""
        # When history is empty, should return original query
        query = "What are the job prospects?"
        result = self.engine.contextualize_query(query, [], client=None)
        self.assertEqual(result, query)


if __name__ == "__main__":
    unittest.main(verbosity=2)

