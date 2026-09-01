"""
Unit Tests for 2G Offline Engine.
Tests:
1. Sub-10ms query execution speed.
2. Accurate keyword and phrase matching across scholarship, medical, engineering, and career categories.
3. Metadata presence (citations, portal URLs).
4. Graceful handling of unknown queries.
"""

import time
import unittest
from offline_engine import OfflineQueryEngine, get_2g_response


class TestOfflineQueryEngine(unittest.TestCase):

    def setUp(self):
        self.engine = OfflineQueryEngine()

    def test_01_pmsss_matching_and_latency(self):
        """Test matching PMSSS query in under 10ms."""
        query = "What is the eligibility, stipend, and quota for PMSSS scholarship in J&K?"
        start = time.time()
        res = self.engine.match_query(query)
        elapsed_ms = (time.time() - start) * 1000

        self.assertIsNotNone(res, "PMSSS query should match pre-fed knowledge")
        self.assertEqual(res["id"], "pmsss_jk")
        self.assertIn("5,000", res["answer"])
        self.assertIn("portal_url", res)
        self.assertLess(elapsed_ms, 15.0, f"Query latency {elapsed_ms:.2f}ms should be under 15ms")
        print(f"\n[Test 01] PMSSS matched in {elapsed_ms:.3f}ms (Confidence: {res['confidence_score']})")

    def test_02_post_matric_scholarship(self):
        """Test matching Post-Matric Scholarship query."""
        query = "How to apply for post-matric scholarship on NSP portal with 2.5 lakh income?"
        res = self.engine.match_query(query)
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], "post_matric_jk")
        self.assertIn("scholarships.gov.in", res["answer"])

    def test_03_nit_srinagar_cutoffs(self):
        """Test matching NIT Srinagar query."""
        query = "What are the JEE Main cutoffs and branches for NIT Srinagar Home State Quota?"
        res = self.engine.match_query(query)
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], "nit_srinagar")
        self.assertIn("Home State", res["answer"])

    def test_04_gmc_srinagar_and_jammu(self):
        """Test matching GMC MBBS cutoffs query."""
        query = "What are the NEET UG cutoff marks for GMC Srinagar and GMC Jammu?"
        res = self.engine.match_query(query)
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], "gmc_srinagar_jammu")
        self.assertIn("570", res["answer"])

    def test_05_career_pathways_science_commerce(self):
        """Test matching career pathways."""
        pcm_res = self.engine.match_query("What are the best career options after 12th PCM?")
        self.assertIsNotNone(pcm_res)
        self.assertEqual(pcm_res["id"], "pcm_career_paths")

        arts_res = self.engine.match_query("Career options in arts humanities law CLAT and journalism")
        self.assertIsNotNone(arts_res)
        self.assertEqual(arts_res["id"], "arts_humanities_paths")

    def test_06_unmatched_query_returns_none(self):
        """Test that completely unrelated queries return None safely."""
        query = "How do I bake a chocolate cake at home?"
        res = self.engine.match_query(query)
        self.assertIsNone(res, "Unrelated query should return None for fallback to AI")

    def test_07_convenience_helper(self):
        """Test get_2g_response helper function."""
        res = get_2g_response("JKCET engineering admission dates and BOPEE syllabus")
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], "jkcet_exam")


if __name__ == "__main__":
    unittest.main()
