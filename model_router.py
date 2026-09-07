"""
Smart model router for J&K EduSetu ("Your Bridge to Education & Opportunities").
Routes queries to the appropriate Gemini model based on complexity
while tracking per-model usage to avoid hitting rate limits.
"""

import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# Model tier definitions (aligned with Google AI Studio free tier limits & dynamic capability)
MODELS = {
    "simple": {
        "id": "gemini-3.5-flash-lite",
        "max_tokens": 2500,
        "label": "Fast",
        "emoji": "⚡",
        "daily_limit": 1500,
    },
    "medium": {
        "id": "gemini-3.6-flash",
        "max_tokens": 3500,
        "label": "Standard",
        "emoji": "🎯",
        "daily_limit": 1500,
    },
    "complex": {
        "id": "gemini-3.6-flash",
        "max_tokens": 4500,
        "label": "Deep Analysis",
        "emoji": "🧠",
        "daily_limit": 1500,
    },
}

# In-family fallback sequence for Gemini models if a specific model encounters quota (429) or spikes (503)
GEMINI_FALLBACK_POOL = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
]

# Keywords that signal query complexity
COMPLEX_SIGNALS = [
    "based on my profile", "based on my", "all scholarships",
    "comprehensive", "full analysis", "everything i can",
    "what are all my options", "complete guide", "step by step plan",
    "both admission and scholarship", "analyze my", "eligibility for all",
    "pcm", "pcb", "percentage", "marks", "cutoff", "category",
    # Urdu complex signals
    "سکالرشپ", "مکمل تفصیل", "اہلیت برائے", "پوری تفصیل", "تمام وظائف", "رہنمائی اور داخلہ",
    # Hindi complex signals
    "सभी छात्रवृत्ति", "विस्तृत जानकारी", "पूरी जानकारी", "प्रोफाइल के आधार पर",
]

MEDIUM_SIGNALS = [
    "eligible", "qualify", "should i", "recommend", "suggest",
    "difference between", "which is better", "compare", "options for",
    "options i have", "what can i apply", "how to apply", "what documents",
    "college", "seats", "quota", "reservation", "merit", "fee",
    # Urdu medium signals
    "کالج", "داخلہ", "رہنمائی", "موازنہ", "کونسا بہتر", "دستاویزات", "درخواست کیسے",
    # Hindi medium signals
    "पात्रता", "प्रवेश", "कटऑफ", "तुलना", "दस्तावेज़", "आवेदन कैसे",
]


def is_multilingual_query(text: str) -> bool:
    """Check if query is non-English (e.g. Urdu, Kashmiri, Hindi) or contains non-Latin scripts."""
    if not text:
        return False
    for char in text:
        code = ord(char)
        # Arabic / Perso-Arabic (Urdu, Kashmiri) or Devanagari (Hindi)
        if (0x0600 <= code <= 0x06FF) or (0x0750 <= code <= 0x077F) or (0xFB50 <= code <= 0xFEFF) or (0x0900 <= code <= 0x097F):
            return True
    lower_t = text.lower()
    if "[note: " in lower_t and any(lang in lower_t for lang in ["urdu", "hindi", "kashmiri", "اردو", "हिंदी", "کٲشُر"]):
        return True
    return False


def classify_complexity(query: str, history_length: int = 0) -> str:
    """Classify query as simple, medium, or complex."""
    q = query.lower().strip()
    word_count = len(q.split())

    # Long conversation history = model needs more context = bump up
    if history_length > 8:
        return "complex"

    # Check complex signals first
    if any(signal in q for signal in COMPLEX_SIGNALS) or word_count > 25:
        return "complex"

    # Check medium signals
    if any(signal in q for signal in MEDIUM_SIGNALS) or word_count > 12:
        return "medium"

    # Non-Latin / Multilingual scripts (Urdu, Hindi, Kashmiri) require richer vocabulary and context
    if is_multilingual_query(query) and word_count >= 4:
        return "medium"

    return "simple"


def _init_usage():
    """Initialize per-model usage tracking in session state."""
    if hasattr(st, "session_state"):
        if "model_usage" not in st.session_state:
            st.session_state.model_usage = {
                tier: 0 for tier in MODELS
            }
        if "active_model_tier" not in st.session_state:
            st.session_state.active_model_tier = "simple"
        if "active_model_id" not in st.session_state:
            st.session_state.active_model_id = MODELS["simple"]["id"]


def _get_fallback_tier(tier: str) -> str:
    """Return next lower tier if current tier is exhausted."""
    order = ["complex", "medium", "simple"]
    idx = order.index(tier)
    return order[idx + 1] if idx + 1 < len(order) else "simple"


def get_routed_model_info(query: str = "", history_length: int = 0) -> dict:
    """Return model tier, ID, max tokens, and metadata for direct google.genai client."""
    _init_usage()
    tier = classify_complexity(query, history_length)
    while tier != "simple" and hasattr(st, "session_state"):
        usage = st.session_state.model_usage.get(tier, 0)
        limit = MODELS[tier]["daily_limit"]
        if usage >= int(limit * 0.85):   # back off at 85% of limit
            tier = _get_fallback_tier(tier)
        else:
            break
    model_cfg = MODELS[tier]

    # Non-English / Multilingual responses consume 3-4x more tokens per word due to subword byte encoding.
    # We guarantee a generous minimum token allocation of 3,500 tokens so Urdu/Hindi/Kashmiri never truncates.
    max_tokens = model_cfg["max_tokens"]
    is_multi = is_multilingual_query(query)
    if hasattr(st, "session_state") and st.session_state.get("selected_language", "English") != "English":
        is_multi = True
    if is_multi:
        max_tokens = max(max_tokens, 4000)

    if hasattr(st, "session_state"):
        st.session_state.active_model_tier = tier
        st.session_state.active_model_id = model_cfg["id"]
        st.session_state.model_usage[tier] = st.session_state.model_usage.get(tier, 0) + 1
    return {
        "tier": tier,
        "model_id": model_cfg["id"],
        "max_tokens": max_tokens,
        "label": model_cfg["label"],
        "emoji": model_cfg["emoji"],
    }


def get_llm(query: str = "", history_length: int = 0):
    """
    Returns the appropriate LangChain LLM for this query.
    Automatically falls back to lower tiers if usage limits approached.
    """
    _init_usage()

    tier = classify_complexity(query, history_length)

    # Check usage — if this tier is near its daily limit, fall back
    while tier != "simple" and hasattr(st, "session_state"):
        usage = st.session_state.model_usage.get(tier, 0)
        limit = MODELS[tier]["daily_limit"]
        if usage >= int(limit * 0.85):   # back off at 85% of limit
            tier = _get_fallback_tier(tier)
        else:
            break

    model_cfg = MODELS[tier]

    if hasattr(st, "session_state"):
        # Store what model is active for sidebar display
        st.session_state.active_model_tier = tier
        st.session_state.active_model_id = model_cfg["id"]

        # Increment usage counter
        st.session_state.model_usage[tier] = \
            st.session_state.model_usage.get(tier, 0) + 1

    import api_key_helper

    google_api_key = api_key_helper.get_google_api_key()
    groq_api_key = api_key_helper.get_groq_api_key()

    if google_api_key:
        llm_kwargs = dict(
            model=model_cfg["id"],
            google_api_key=google_api_key,
            max_output_tokens=model_cfg["max_tokens"],
            temperature=0.2,
        )
        return ChatGoogleGenerativeAI(**llm_kwargs)

    if groq_api_key:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model_name="qwen/qwen3.8-27b",
            groq_api_key=groq_api_key,
            temperature=0.2,
            max_tokens=model_cfg["max_tokens"],
        )

    # Fallback if no keys configured
    return ChatGoogleGenerativeAI(
        model=model_cfg["id"],
        google_api_key="dummy_key",
        max_output_tokens=model_cfg["max_tokens"],
        temperature=0.2,
    )


def render_model_badge():
    """Render the active model indicator in the sidebar."""
    _init_usage()
    tier = st.session_state.get("active_model_tier", "simple") if hasattr(st, "session_state") else "simple"
    model_id = st.session_state.get("active_model_id", MODELS["simple"]["id"]) if hasattr(st, "session_state") else MODELS["simple"]["id"]
    cfg = MODELS.get(tier, MODELS["simple"])

    usage_lines = []
    if hasattr(st, "session_state") and "model_usage" in st.session_state:
        for t, cnt in st.session_state.model_usage.items():
            lim = MODELS[t]["daily_limit"]
            pct = int((cnt / lim) * 100)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            usage_lines.append(
                f"{MODELS[t]['emoji']} `{MODELS[t]['id'].split('-', 1)[1]}` "
                f"{bar} {cnt}/{lim}"
            )

    st.sidebar.markdown(f"""
    <div style="background:rgba(255,255,255,0.08);border-radius:8px;
         padding:10px 12px;margin-top:8px;border:1px solid rgba(255,255,255,0.12);">
      <div style="color:#F5A623;font-size:9px;font-weight:700;
           letter-spacing:1px;margin-bottom:6px;">ACTIVE MODEL</div>
      <div style="color:white;font-size:12px;font-weight:700;">
        {cfg['emoji']} {cfg['label']} Mode
      </div>
      <div style="color:#AEC6D0;font-size:9px;margin-top:2px;">
        {model_id}
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar.expander("📊 Model Usage Today"):
        for line in usage_lines:
            st.markdown(line)


def render_query_info(query: str, history_length: int = 0):
    """Show which model was selected and why — shown above the answer."""
    tier = classify_complexity(query, history_length)
    cfg = MODELS[tier]
    actual_tier = st.session_state.get("active_model_tier", tier) if hasattr(st, "session_state") else tier
    actual_cfg = MODELS.get(actual_tier, cfg)

    note = ""
    if actual_tier != tier:
        note = f" *(downgraded from {cfg['label']} — quota)*"

    st.caption(
        f"{actual_cfg['emoji']} **{actual_cfg['label']} Mode** "
        f"· `{actual_cfg['id']}`{note}"
    )
