"""
Smart model router for J&K EduSetu ("Your Bridge to Education & Opportunities").
Routes queries to the appropriate Gemini model based on complexity
while tracking per-model usage to avoid hitting rate limits.
"""

import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# Complete active Gemini 3.x Fleet specifications aligned with user's Google AI Studio free tier limits
MODEL_FLEET = {
    "gemini-3.8-flash": {
        "tier": "complex",
        "label": "Flash 3.8 Flagship",
        "emoji": "🧠",
        "daily_limit": 20,
        "rpm_limit": 5,
        "max_tokens": 4500,
        "supports_thinking": True,
        "description": "Deep multi-parameter reasoning & flagship analysis",
    },
    "gemini-3.6-flash": {
        "tier": "medium",
        "label": "Flash 3.6 Pro",
        "emoji": "🎯",
        "daily_limit": 20,
        "rpm_limit": 5,
        "max_tokens": 3500,
        "supports_thinking": False,
        "description": "Fast, high-fidelity reasoning & standard queries",
    },
    "gemini-3.5-flash": {
        "tier": "medium",
        "label": "Flash 3.5 Standard",
        "emoji": "🎯",
        "daily_limit": 20,
        "rpm_limit": 5,
        "max_tokens": 3500,
        "supports_thinking": False,
        "description": "High stability general knowledge & document QA",
    },
    "gemini-3.7-flash": {
        "tier": "complex",
        "label": "Flash 3.7 Reasoning",
        "emoji": "🧠",
        "daily_limit": 20,
        "rpm_limit": 5,
        "max_tokens": 4500,
        "supports_thinking": True,
        "description": "Advanced analytical reasoning & step-by-step logic",
    },
    "gemini-3.5-flash-lite": {
        "tier": "simple",
        "label": "Flash-Lite 3.5",
        "emoji": "⚡",
        "daily_limit": 500,
        "rpm_limit": 15,
        "max_tokens": 2500,
        "supports_thinking": False,
        "description": "Sub-second lightweight conversational responses",
    },
    "gemini-3.1-flash-lite": {
        "tier": "simple",
        "label": "Flash-Lite 3.1",
        "emoji": "⚡",
        "daily_limit": 500,
        "rpm_limit": 15,
        "max_tokens": 2500,
        "supports_thinking": False,
        "description": "High-throughput 500 RPD rapid information retrieval",
    },
}

# Simplified tier mapping for backwards compatibility
MODELS = {
    "simple": {
        "id": "gemini-3.5-flash-lite",
        "max_tokens": 2500,
        "label": "Fast (Flash-Lite)",
        "emoji": "⚡",
        "daily_limit": 500,
    },
    "medium": {
        "id": "gemini-3.6-flash",
        "max_tokens": 3500,
        "label": "Standard (Flash)",
        "emoji": "🎯",
        "daily_limit": 20,
    },
    "complex": {
        "id": "gemini-3.8-flash",
        "max_tokens": 4500,
        "label": "Deep Analysis (Flash 3.8)",
        "emoji": "🧠",
        "daily_limit": 20,
    },
}

# Ordered candidate pools per complexity tier to balance load
TIER_CANDIDATE_POOLS = {
    "simple": [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    ],
    "medium": [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    ],
    "complex": [
        "gemini-3.8-flash",
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    ],
}

# Resilient fallback sequence across all active models in the fleet
GEMINI_FALLBACK_POOL = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.7-flash",
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
    "eligible", "eligib", "qualify", "should i", "recommend", "suggest",
    "difference between", "which is better", "compare", "options for",
    "options i have", "what can i apply", "how to apply", "what documents", "document", "documents",
    "college", "seats", "quota", "reservation", "merit", "fee", "jkcet", "neet", "jee", "criteria",
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
            st.session_state.model_usage = {m: 0 for m in MODEL_FLEET}
            for tier in ["simple", "medium", "complex"]:
                st.session_state.model_usage[tier] = 0
        if "active_model_tier" not in st.session_state:
            st.session_state.active_model_tier = "simple"
        if "active_model_id" not in st.session_state:
            st.session_state.active_model_id = "gemini-3.5-flash-lite"
        if "exhausted_models" not in st.session_state:
            st.session_state.exhausted_models = set()


def get_routed_model_info(query: str = "", history_length: int = 0) -> dict:
    """Return model tier, ID, max tokens, and metadata dynamically balanced across the active fleet."""
    _init_usage()
    tier = classify_complexity(query, history_length)

    candidates = TIER_CANDIDATE_POOLS.get(tier, TIER_CANDIDATE_POOLS["simple"])
    exhausted = st.session_state.get("exhausted_models", set()) if hasattr(st, "session_state") else set()
    usage = st.session_state.get("model_usage", {}) if hasattr(st, "session_state") else {}

    selected_model = None

    # Filter out models that are known to be exhausted (429) or reached safety limit in this session
    healthy_candidates = []
    for cand in candidates:
        if cand in exhausted:
            continue
        cand_limit = MODEL_FLEET[cand]["daily_limit"]
        used = usage.get(cand, 0)
        safety_buf = 3 if cand_limit <= 20 else 50
        if used < (cand_limit - safety_buf):
            healthy_candidates.append(cand)

    if healthy_candidates:
        if tier == "simple":
            # Round-robin / balance between 3.5-lite and 3.1-lite based on least used
            selected_model = min(healthy_candidates, key=lambda m: usage.get(m, 0))
        elif tier == "medium":
            # Prefer 20 RPD models (3.6-flash, 3.5-flash) if available, otherwise lite models
            standard_cands = [m for m in healthy_candidates if MODEL_FLEET[m]["tier"] == "medium"]
            if standard_cands:
                selected_model = min(standard_cands, key=lambda m: usage.get(m, 0))
            else:
                selected_model = min(healthy_candidates, key=lambda m: usage.get(m, 0))
        else:  # complex
            # Prefer flagship reasoning models (3.8-flash, 3.6-flash, 3.7-flash)
            flagship_cands = [m for m in healthy_candidates if MODEL_FLEET[m]["tier"] in ["complex", "medium"]]
            if flagship_cands:
                selected_model = min(flagship_cands, key=lambda m: usage.get(m, 0))
            else:
                selected_model = min(healthy_candidates, key=lambda m: usage.get(m, 0))
    else:
        # Emergency fail-safe: choose any non-exhausted lite model with massive 500 RPD
        for lite in ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]:
            if lite not in exhausted:
                selected_model = lite
                break
        if not selected_model:
            selected_model = "gemini-3.5-flash-lite"

    model_info = MODEL_FLEET.get(selected_model, MODEL_FLEET["gemini-3.5-flash-lite"])

    # Determine token budget based on query complexity tier
    tier_token_budgets = {
        "simple": 2500,
        "medium": 3500,
        "complex": 4500,
    }
    max_tokens = tier_token_budgets.get(tier, 3500)

    # Non-English / Multilingual responses consume 3-4x more tokens per word due to subword byte encoding.
    # We guarantee a generous minimum token allocation of 4,000 tokens so Urdu/Hindi/Kashmiri never truncates.
    is_multi = is_multilingual_query(query)
    if hasattr(st, "session_state") and st.session_state.get("selected_language", "English") != "English":
        is_multi = True
    if is_multi:
        max_tokens = max(max_tokens, 4000)

    if hasattr(st, "session_state"):
        st.session_state.active_model_tier = tier
        st.session_state.active_model_id = selected_model
        st.session_state.model_usage[selected_model] = usage.get(selected_model, 0) + 1
        st.session_state.model_usage[tier] = usage.get(tier, 0) + 1

    return {
        "tier": tier,
        "model_id": selected_model,
        "max_tokens": max_tokens,
        "label": model_info["label"],
        "emoji": model_info["emoji"],
    }


def get_llm(query: str = "", history_length: int = 0):
    """
    Returns the appropriate LangChain LLM for this query.
    Automatically load balances across the Gemini 3.x fleet.
    """
    model_info = get_routed_model_info(query, history_length)

    import api_key_helper

    google_api_key = api_key_helper.get_google_api_key()
    groq_api_key = api_key_helper.get_groq_api_key()

    if google_api_key:
        llm_kwargs = dict(
            model=model_info["model_id"],
            google_api_key=google_api_key,
            max_output_tokens=model_info["max_tokens"],
            temperature=0.2,
        )
        return ChatGoogleGenerativeAI(**llm_kwargs)

    if groq_api_key:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model_name="qwen/qwen3.8-27b",
            groq_api_key=groq_api_key,
            temperature=0.2,
            max_tokens=model_info["max_tokens"],
        )

    # Fallback if no keys configured
    return ChatGoogleGenerativeAI(
        model=model_info["model_id"],
        google_api_key="dummy_key",
        max_output_tokens=model_info["max_tokens"],
        temperature=0.2,
    )


def render_model_badge():
    """Render the active model indicator and fleet usage monitor in the sidebar."""
    _init_usage()
    tier = st.session_state.get("active_model_tier", "simple") if hasattr(st, "session_state") else "simple"
    model_id = st.session_state.get("active_model_id", "gemini-3.5-flash-lite") if hasattr(st, "session_state") else "gemini-3.5-flash-lite"
    model_info = MODEL_FLEET.get(model_id, MODEL_FLEET["gemini-3.5-flash-lite"])
    exhausted = st.session_state.get("exhausted_models", set()) if hasattr(st, "session_state") else set()
    usage = st.session_state.get("model_usage", {}) if hasattr(st, "session_state") else {}

    st.sidebar.markdown(f"""
    <div style="background:rgba(255,255,255,0.08);border-radius:8px;
         padding:10px 12px;margin-top:8px;border:1px solid rgba(255,255,255,0.12);">
      <div style="color:#F5A623;font-size:9px;font-weight:700;
           letter-spacing:1px;margin-bottom:6px;">ACTIVE MODEL (FLEET BALANCED)</div>
      <div style="color:white;font-size:12px;font-weight:700;">
        {model_info['emoji']} {model_info['label']}
      </div>
      <div style="color:#AEC6D0;font-size:9.5px;margin-top:2px;">
        ID: <code>{model_id}</code>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar.expander("📊 Fleet Quota Monitor (6 Models)"):
        st.markdown("<div style='font-size:11px;color:#94A3B8;margin-bottom:6px;'>Dynamically balanced across your AI Studio allocations:</div>", unsafe_allow_html=True)
        for mid, mcfg in MODEL_FLEET.items():
            used = usage.get(mid, 0)
            lim = mcfg["daily_limit"]
            pct = min(100, int((used / lim) * 100))
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            status_tag = ""
            if mid in exhausted:
                status_tag = " <span style='color:#EF4444;font-size:9px;font-weight:700;'>[EXHAUSTED]</span>"
            elif mid == model_id:
                status_tag = " <span style='color:#10B981;font-size:9px;font-weight:700;'>[ACTIVE]</span>"
            st.markdown(
                f"<div style='font-size:11px;margin-bottom:4px;'>"
                f"{mcfg['emoji']} <b>{mcfg['label']}</b>{status_tag}<br>"
                f"<code style='font-size:10px;'>{bar} {used}/{lim} RPD ({pct}%)</code>"
                f"</div>",
                unsafe_allow_html=True
            )


def render_query_info(query: str, history_length: int = 0):
    """Show which model was selected and why — shown above the answer."""
    tier = classify_complexity(query, history_length)
    actual_tier = st.session_state.get("active_model_tier", tier) if hasattr(st, "session_state") else tier
    actual_model_id = st.session_state.get("active_model_id", "gemini-3.5-flash-lite") if hasattr(st, "session_state") else "gemini-3.5-flash-lite"
    actual_cfg = MODEL_FLEET.get(actual_model_id, MODEL_FLEET["gemini-3.5-flash-lite"])

    st.caption(
        f"{actual_cfg['emoji']} **{actual_cfg['label']}** "
        f"· `{actual_model_id}` · Complexity: *{actual_tier.capitalize()}*"
    )

