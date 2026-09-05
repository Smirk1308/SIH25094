"""
Smart model router for PathSeva.
Routes queries to the appropriate Gemini model based on complexity
while tracking per-model usage to avoid hitting rate limits.
"""

import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# Model tier definitions
MODELS = {
    "simple": {
        "id": "gemini-2.0-flash",
        "max_tokens": 300,
        "label": "Fast",
        "emoji": "⚡",
        "daily_limit": 1500,
    },
    "medium": {
        "id": "gemini-3.7-flash",
        "max_tokens": 512,
        "label": "Standard",
        "emoji": "🎯",
        "daily_limit": 500,
    },
    "complex": {
        "id": "gemini-3.8-flash",
        "max_tokens": 1024,
        "label": "Deep Analysis",
        "emoji": "🧠",
        "daily_limit": 200,
    },
}

# Keywords that signal query complexity
COMPLEX_SIGNALS = [
    "based on my profile", "based on my", "all scholarships",
    "comprehensive", "full analysis", "everything i can",
    "what are all my options", "complete guide", "step by step plan",
    "both admission and scholarship", "analyze my", "eligibility for all",
]

MEDIUM_SIGNALS = [
    "eligible", "qualify", "should i", "recommend", "suggest",
    "difference between", "which is better", "compare", "options for",
    "what can i apply", "how to apply", "what documents",
]


def classify_complexity(query: str, history_length: int = 0) -> str:
    """Classify query as simple, medium, or complex."""
    q = query.lower().strip()
    word_count = len(q.split())

    # Long conversation history = model needs more context = bump up
    if history_length > 8:
        return "complex"

    # Check complex signals first
    if any(signal in q for signal in COMPLEX_SIGNALS) or word_count > 30:
        return "complex"

    # Check medium signals
    if any(signal in q for signal in MEDIUM_SIGNALS) or word_count > 15:
        return "medium"

    return "simple"


def _init_usage():
    """Initialize per-model usage tracking in session state."""
    if hasattr(st, "session_state"):
        if "model_usage" not in st.session_state:
            st.session_state.model_usage = {
                tier: 0 for tier in MODELS
            }


def _get_fallback_tier(tier: str) -> str:
    """Return next lower tier if current tier is exhausted."""
    order = ["complex", "medium", "simple"]
    idx = order.index(tier)
    return order[idx + 1] if idx + 1 < len(order) else "simple"


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

    google_api_key = None
    try:
        if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
            google_api_key = str(st.secrets["GOOGLE_API_KEY"]).strip()
    except Exception:
        pass
    if not google_api_key:
        google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    # Build LLM — 3.8 Flash gets thinking enabled, others don't
    llm_kwargs = dict(
        model=model_cfg["id"],
        google_api_key=google_api_key or "dummy_key",
        max_output_tokens=model_cfg["max_tokens"],
        temperature=0.2,
    )
    if tier == "complex":
        llm_kwargs["thinking"] = "medium"

    return ChatGoogleGenerativeAI(**llm_kwargs)


def render_model_badge():
    """Render the active model indicator in the sidebar."""
    _init_usage()
    tier = st.session_state.get("active_model_tier", "simple") if hasattr(st, "session_state") else "simple"
    model_id = st.session_state.get("active_model_id", "gemini-2.0-flash") if hasattr(st, "session_state") else "gemini-2.0-flash"
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
