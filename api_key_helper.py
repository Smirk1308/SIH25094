"""
Centralized API Key Resolver for J&K EduSetu.
Handles resilient key extraction from Streamlit Secrets, unquoted TOML files,
.env files, and environment variables across local and cloud environments.
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any

# Cache discovered keys in module-level memory for instant access
_KEY_CACHE: Dict[str, str] = {
    "google": "",
    "groq": "",
    "admin": "",
}


def _mask_key(key: str) -> str:
    """Safely mask a key for logging/diagnostics without leaking secrets."""
    if not key:
        return "Not configured"
    k = key.strip()
    if len(k) <= 8:
        return "***"
    return f"{k[:4]}...{k[-4:]}"


def _scan_raw_file_for_key(file_path: Path, key_names: List[str]) -> str:
    """Read a file line-by-line using regex to extract keys even if TOML is malformed or unquoted."""
    try:
        if not file_path.is_file():
            return ""
        
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for name in key_names:
                # Match KEY = "value", KEY = 'value', or KEY = value (unquoted)
                pattern = rf"(?i)^\s*{re.escape(name)}\s*[:=]\s*[\"']?([A-Za-z0-9_\-\.\:\/]+)[\"']?\s*$"
                match = re.match(pattern, line)
                if match:
                    val = match.group(1).strip().strip("'").strip('"').strip()
                    if val and not val.lower().startswith("your_"):
                        return val
    except Exception:
        pass
    return ""


def _find_key_in_candidate_files(key_names: List[str]) -> str:
    """Check common locations for secrets.toml or .env files."""
    candidate_paths = [
        Path.cwd() / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml",
        Path("/home/appuser/.streamlit/secrets.toml"),
        Path("/mount/src/sih25094/.streamlit/secrets.toml"),
        Path.cwd() / ".env",
        Path.home() / ".env",
    ]

    custom_secrets = os.getenv("STREAMLIT_SECRETS_FILE")
    if custom_secrets:
        candidate_paths.insert(0, Path(custom_secrets))

    for p in candidate_paths:
        val = _scan_raw_file_for_key(p, key_names)
        if val:
            return val
    return ""


def get_google_api_key() -> str:
    """
    Resolve Google Gemini API key with multi-layer resilience:
    1. Memory cache
    2. Streamlit secrets (root + nested tables, multiple name variants)
    3. Direct regex file scanner (handles unquoted Streamlit Cloud secrets)
    4. Environment variables
    """
    if _KEY_CACHE["google"]:
        return _KEY_CACHE["google"]

    key_names = [
        "GOOGLE_API_KEY", "google_api_key", "GEMINI_API_KEY", "gemini_api_key",
        "GEMINI_KEY", "gemini_key", "GOOGLE_KEY", "google_key", "API_KEY"
    ]

    resolved = ""

    # 1. Attempt Streamlit Secrets object
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k in key_names:
                if k in st.secrets:
                    resolved = str(st.secrets[k]).strip().strip("'").strip('"').strip()
                    if resolved:
                        break

            if not resolved:
                for k, v in st.secrets.items():
                    if isinstance(v, str) and any(term in k.lower() for term in ["gemini", "google"]):
                        resolved = str(v).strip().strip("'").strip('"').strip()
                        if resolved:
                            break

            if not resolved:
                for table in st.secrets.values():
                    if isinstance(table, dict):
                        for k in key_names:
                            if k in table:
                                resolved = str(table[k]).strip().strip("'").strip('"').strip()
                                if resolved:
                                    break
                        if resolved:
                            break
    except Exception:
        # st.secrets threw an error (e.g. TomlDecodeError due to unquoted strings on cloud)
        resolved = ""

    # 2. Attempt raw file scanner fallback (handles unquoted secrets)
    if not resolved:
        resolved = _find_key_in_candidate_files(key_names)

    # 3. Attempt Environment variables
    if not resolved:
        for env_var in key_names:
            val = os.getenv(env_var, "").strip().strip("'").strip('"').strip()
            if val and not val.lower().startswith("your_"):
                resolved = val
                break

    if resolved:
        _KEY_CACHE["google"] = resolved
        # Mirror to environment variables for sub-libraries (google-genai, langchain)
        os.environ["GOOGLE_API_KEY"] = resolved
        os.environ["GEMINI_API_KEY"] = resolved

    return resolved


def get_groq_api_key() -> str:
    """
    Resolve Groq API key with multi-layer resilience:
    1. Memory cache
    2. Streamlit secrets
    3. Direct regex file scanner
    4. Environment variables
    """
    if _KEY_CACHE["groq"]:
        return _KEY_CACHE["groq"]

    key_names = ["GROQ_API_KEY", "groq_api_key", "GROQ_KEY", "groq_key"]
    resolved = ""

    # 1. Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k in key_names:
                if k in st.secrets:
                    resolved = str(st.secrets[k]).strip().strip("'").strip('"').strip()
                    if resolved:
                        break
            if not resolved:
                for k, v in st.secrets.items():
                    if isinstance(v, str) and "groq" in k.lower():
                        resolved = str(v).strip().strip("'").strip('"').strip()
                        if resolved:
                            break
            if not resolved:
                for table in st.secrets.values():
                    if isinstance(table, dict):
                        for k in key_names:
                            if k in table:
                                resolved = str(table[k]).strip().strip("'").strip('"').strip()
                                if resolved:
                                    break
                        if resolved:
                            break
    except Exception:
        resolved = ""

    # 2. Raw file scanner fallback
    if not resolved:
        resolved = _find_key_in_candidate_files(key_names)

    # 3. Environment variables
    if not resolved:
        for env_var in key_names:
            val = os.getenv(env_var, "").strip().strip("'").strip('"').strip()
            if val and not val.lower().startswith("your_"):
                resolved = val
                break

    if resolved:
        _KEY_CACHE["groq"] = resolved
        os.environ["GROQ_API_KEY"] = resolved

    return resolved


def get_admin_password() -> str:
    """Resolve Admin password from secrets or default."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "ADMIN_PASSWORD" in st.secrets:
            return str(st.secrets["ADMIN_PASSWORD"]).strip()
    except Exception:
        pass

    raw_pw = _find_key_in_candidate_files(["ADMIN_PASSWORD", "admin_password"])
    if raw_pw:
        return raw_pw

    return os.getenv("ADMIN_PASSWORD", "admin123")


def get_api_diagnostics() -> Dict[str, Any]:
    """Return non-sensitive status details for internal health monitoring."""
    g_key = get_google_api_key()
    q_key = get_groq_api_key()

    return {
        "google_configured": bool(g_key),
        "google_masked": _mask_key(g_key),
        "groq_configured": bool(q_key),
        "groq_masked": _mask_key(q_key),
        "mode": "Dual Engine (Gemini + Groq)" if (g_key and q_key) else ("Gemini Primary" if g_key else ("Groq Fallback" if q_key else "2G Mountain Edge Mode")),
    }
