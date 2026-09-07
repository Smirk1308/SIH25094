"""
Unit tests for api_key_helper.py.
Verifies multi-layer resolution, regex extraction of unquoted keys, and diagnostics masking.
"""

from pathlib import Path
import api_key_helper


def test_mask_key():
    assert api_key_helper._mask_key("") == "Not configured"
    assert api_key_helper._mask_key("123") == "***"
    assert api_key_helper._mask_key("AQ.Ab8RN6K_test_ETlzw") == "AQ.A...Tlzw"


def test_scan_raw_file_unquoted(tmp_path):
    # Simulates what happens on Streamlit Cloud when someone forgets quotes
    fake_secrets = tmp_path / "secrets.toml"
    fake_secrets.write_text("""
    # Comment
    GOOGLE_API_KEY = AQ.Ab8RN6K_UNQUOTED_TEST_KEY_12345
    GROQ_API_KEY = gsk_UNQUOTED_GROQ_TEST_KEY_67890
    ADMIN_PASSWORD = secretAdminPass
    """, encoding="utf-8")

    extracted_g = api_key_helper._scan_raw_file_for_key(fake_secrets, ["GOOGLE_API_KEY"])
    assert extracted_g == "AQ.Ab8RN6K_UNQUOTED_TEST_KEY_12345"

    extracted_q = api_key_helper._scan_raw_file_for_key(fake_secrets, ["GROQ_API_KEY"])
    assert extracted_q == "gsk_UNQUOTED_GROQ_TEST_KEY_67890"


def test_scan_raw_file_quoted(tmp_path):
    fake_secrets = tmp_path / "secrets.toml"
    fake_secrets.write_text("""
    GOOGLE_API_KEY = "AIzaSy_QUOTED_TEST_KEY"
    GROQ_API_KEY = 'gsk_QUOTED_KEY'
    """, encoding="utf-8")

    extracted_g = api_key_helper._scan_raw_file_for_key(fake_secrets, ["GOOGLE_API_KEY"])
    assert extracted_g == "AIzaSy_QUOTED_TEST_KEY"

    extracted_q = api_key_helper._scan_raw_file_for_key(fake_secrets, ["GROQ_API_KEY"])
    assert extracted_q == "gsk_QUOTED_KEY"


def test_live_diagnostics():
    diag = api_key_helper.get_api_diagnostics()
    assert "google_configured" in diag
    assert "groq_configured" in diag
    assert "mode" in diag
    # Ensure masked values don't leak full secrets
    assert not diag["google_masked"].startswith("AQ.Ab8RN6KGtZ-")
