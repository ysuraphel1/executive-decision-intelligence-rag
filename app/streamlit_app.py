import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from rag import ask_rag

BASE_DIR = Path(__file__).parent
RAW_DIR  = BASE_DIR / "data" / "raw"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _leader_from_stem(stem: str) -> str:
    parts = stem.split("_")
    if len(parts) >= 2:
        return " ".join(p.capitalize() for p in parts[:2])
    return stem.replace("_", " ").title()


def get_available_leaders() -> list[str]:
    if not RAW_DIR.exists():
        return []
    return sorted({_leader_from_stem(f.stem) for f in RAW_DIR.glob("*.txt")})


def build_example_questions(leaders: list[str]) -> list[str]:
    generic = [
        "How do these leaders approach decisions under uncertainty?",
        "What common themes appear across their innovation strategies?",
        "How do they think about long-term vs short-term trade-offs?",
    ]
    specific = []
    prompts = [
        ("{name}", "approach risk management?"),
        ("{name}", "think about AI strategy?"),
        ("{name}", "allocate capital and prioritize investment?"),
        ("{name}", "build and sustain competitive advantage?"),
        ("{name}", "describe their leadership philosophy?"),
        ("{name}", "navigate industry disruption?"),
    ]
    for i, name in enumerate(leaders[:6]):
        _, q = prompts[i % len(prompts)]
        specific.append(f"How does {name} {q}")
    return (specific + generic)[:8]


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ClarityIQ",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hide only decorative Streamlit chrome — never touch the sidebar toggle */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
[data-testid="stDecoration"]  { display: none !important; }
[data-testid="stDeployButton"] { display: none !important; }
header[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
}

/* ── Sidebar expand arrow (shown when sidebar is collapsed) ── */
[data-testid="stSidebarCollapsedControl"] {
    display:          flex !important;
    visibility:       visible !important;
    pointer-events:   auto !important;
    background:       #1e2130 !important;
    border-radius:    0 10px 10px 0 !important;
    border:           1px solid #6366f1 !important;
    border-left:      none !important;
    top:              50% !important;
    transform:        translateY(-50%) !important;
}
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] svg {
    visibility:  visible !important;
    color:       #a5b4fc !important;
    fill:        #a5b4fc !important;
    stroke:      #a5b4fc !important;
    opacity:     1      !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0f1117;
    border-right: 1px solid #1e2130;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Push content down so logo clears Streamlit's internal header row */
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem !important;
}

.clarity-logo {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1;
    color: #ffffff !important;
    margin: 0 0 4px 0;
    padding: 0;
}
.clarity-logo span { color: #6366f1 !important; }
.clarity-sub {
    font-size: 0.75rem;
    color: #94a3b8 !important;
    margin-bottom: 0;
}

/* Sidebar section labels */
.sidebar-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b !important;
    margin: 16px 0 6px 0;
}

/* Example question buttons */
section[data-testid="stSidebar"] .stButton button {
    background: #1e2130 !important;
    border: 1px solid #2d3148 !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    text-align: left !important;
    padding: 8px 12px !important;
    line-height: 1.4 !important;
    transition: all 0.15s ease !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #2d3148 !important;
    border-color: #6366f1 !important;
    color: #e2e8f0 !important;
}

/* Clear button distinct style */
.clear-btn button {
    background: transparent !important;
    border: 1px solid #2d3148 !important;
    color: #64748b !important;
    font-size: 0.75rem !important;
}

/* ── Main area ── */
.block-container { padding-top: 1.5rem !important; }

.main-header {
    padding: 0 0 1rem 0;
    border-bottom: 1px solid #1e2130;
    margin-bottom: 1.5rem;
}
.main-title {
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -1.5px;
    line-height: 1;
    color: #f8fafc;
    margin: 0 0 6px 0;
}
.main-title span { color: #6366f1; }
.main-subtitle {
    font-size: 0.95rem;
    color: #64748b;
    margin: 0;
}

/* ── Welcome card ── */
.welcome-card {
    background: #0f1117;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 2rem;
    margin: 2rem auto;
    max-width: 640px;
    text-align: center;
}
.welcome-card h3 { color: #e2e8f0; font-size: 1.1rem; margin-bottom: 0.5rem; }
.welcome-card p  { color: #64748b; font-size: 0.875rem; line-height: 1.6; }

/* ── Source chips ── */
.source-chip {
    display: inline-block;
    background: #1e2130;
    border: 1px solid #2d3148;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.75rem;
    color: #94a3b8;
    margin: 2px 4px 2px 0;
}
.source-chip strong { color: #a5b4fc; }

/* ── Selectbox ── */
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background: #1e2130 !important;
    border-color: #2d3148 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────

leaders          = get_available_leaders()
leader_options   = ["All Leaders"] + leaders
example_qs       = build_example_questions(leaders)

if "messages"         not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="clarity-logo">Clarity<span>IQ</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="clarity-sub">Fortune 500 Executive Intelligence</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<p class="sidebar-label">Focus Area</p>', unsafe_allow_html=True)
    selected_leader = st.selectbox(
        label="leader_select",
        options=leader_options,
        index=0,
        label_visibility="collapsed",
        help="Restrict retrieval to one leader's source material.",
    )

    st.markdown(
        f'<p class="sidebar-label">{len(leaders)} leader{"s" if len(leaders) != 1 else ""} indexed</p>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown('<p class="sidebar-label">Example Questions</p>', unsafe_allow_html=True)
    for q in example_qs:
        if st.button(q, use_container_width=True, key=f"eq_{q}"):
            st.session_state.pending_question = q

    st.divider()

    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("Clear conversation", use_container_width=True, key="clear"):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<p class="clarity-sub" style="margin-top:12px">Source material: earnings calls, '
        'shareholder letters, and public interviews.</p>',
        unsafe_allow_html=True,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
  <div class="main-title">Clarity<span>IQ</span></div>
  <div class="main-subtitle">Ask how Fortune 500 executives think, decide, and lead — grounded in source material.</div>
</div>
""", unsafe_allow_html=True)

# Empty state
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
      <h3>Start a conversation</h3>
      <p>Ask any question about executive strategy, decision-making, capital allocation,
         leadership philosophy, or competitive positioning.<br><br>
         Use the sidebar to focus on a specific leader, or ask across all indexed executives at once.</p>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            chips = ""
            for s in msg["sources"]:
                name = s.get("leader", "Unknown")
                chips += f'<span class="source-chip"><strong>{name}</strong></span>'
            st.markdown(f'<div style="margin-top:8px">{chips}</div>', unsafe_allow_html=True)

# Consume pending question from sidebar button
user_input = st.session_state.pop("pending_question", None)

# Chat input
typed = st.chat_input("Ask about strategy, leadership, or decision-making...")
if typed:
    user_input = typed

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    leader_filter = None if selected_leader == "All Leaders" else selected_leader

    with st.chat_message("assistant"):
        with st.spinner("Searching source material..."):
            result = ask_rag(user_input, leader=leader_filter)

        st.markdown(result["answer"])

        if result["sources"]:
            chips = ""
            for s in result["sources"]:
                name = s.get("leader", "Unknown")
                chips += f'<span class="source-chip"><strong>{name}</strong></span>'
            st.markdown(f'<div style="margin-top:8px">{chips}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role":    "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
