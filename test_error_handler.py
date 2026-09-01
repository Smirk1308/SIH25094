"""
Unit Tests for Personalized Error Handler System.
"""

import unittest
from error_handler import ErrorDiagnostic


class TestErrorHandler(unittest.TestCase):

    def test_01_api_key_error_classification(self):
        """Test API key missing or invalid error."""
        err = Exception("groq.AuthenticationError: Error code: 401 - Invalid API Key provided")
        diag = ErrorDiagnostic.classify(err)
        self.assertEqual(diag["category"], "authentication")
        self.assertIn("API Key", diag["title"])
        self.assertTrue(diag["fallback_available"])
        self.assertGreaterEqual(len(diag["action_steps"]), 2)

    def test_02_rate_limit_classification(self):
        """Test 429 rate limit error."""
        err = Exception("groq.RateLimitError: Error code: 429 - Rate limit reached for model")
        diag = ErrorDiagnostic.classify(err)
        self.assertEqual(diag["category"], "rate_limit")
        self.assertIn("Rate Limit", diag["title"])
        self.assertTrue(diag["fallback_available"])

    def test_03_timeout_classification(self):
        """Test connection timeout on slow network."""
        err = Exception("httpx.ConnectTimeout: Connection to api.groq.com timed out after 10000ms")
        diag = ErrorDiagnostic.classify(err)
        self.assertEqual(diag["category"], "network")
        self.assertIn("Timeout", diag["title"])
        self.assertTrue(diag["fallback_available"])

    def test_04_chroma_sync_classification(self):
        """Test Chroma vector store notice."""
        err = Exception("chromadb.errors.ChromaError: Collection sqlite lock busy")
        diag = ErrorDiagnostic.classify(err)
        self.assertEqual(diag["category"], "database")
        self.assertIn("Vector Store", diag["title"])

    def test_05_unknown_exception_fallback(self):
        """Test general exception provides safe fallback without crashing."""
        err = ValueError("Unexpected token formatting error")
        diag = ErrorDiagnostic.classify(err)
        self.assertEqual(diag["category"], "general")
        self.assertTrue(diag["fallback_available"])


if __name__ == "__main__":
    unittest.main()
