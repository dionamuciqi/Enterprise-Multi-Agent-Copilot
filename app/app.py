import sys
import json
from pathlib import Path
from typing import List, Any

sys.path.append(str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from graph.workflow import build_graph

# Prompt injection guard
from utils.security import is_prompt_injection


# Page config
st.set_page_config(page_title="Enterprise Healthcare Copilot", layout="wide")



# Load CSS from file
def load_css(css_path: Path) -> None:
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {css_path}")


CSS_FILE = Path(__file__).with_name("styles.css")
load_css(CSS_FILE)


# Session state init
DEFAULT_QUESTION = ""

if "question" not in st.session_state:
    st.session_state["question"] = DEFAULT_QUESTION
if "status" not in st.session_state:
    st.session_state["status"] = "Ready"
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "last_error" not in st.session_state:
    st.session_state["last_error"] = None

# sample queries UI state
if "selected_example" not in st.session_state:
    st.session_state["selected_example"] = ""

# security UI state
if "show_security_details" not in st.session_state:
    st.session_state["show_security_details"] = False



# App (LangGraph) cache
@st.cache_resource
def get_app():
    return build_graph()


app = get_app()



# Helpers
def clear_all():
    st.session_state["question"] = ""
    st.session_state["selected_example"] = ""
    st.session_state["status"] = "Ready"
    st.session_state["last_result"] = None
    st.session_state["last_error"] = None
    st.rerun()


def normalize_answer_sections(answer: str) -> str:
    """
    Removes duplicated consecutive headings (e.g., 'Executive Summary' twice).
    Keeps the first occurrence.
    """
    if not answer:
        return answer

    lines = answer.splitlines()
    out = []
    prev_norm = None

    def norm_heading(line: str):
        s = line.strip()
        if not s:
            return None
        if s.startswith("#"):
            return s.lstrip("#").strip().lower()
        lowered = s.lower()
        if lowered in {
            "executive summary",
            "client-ready email",
            "action list",
            "key risks and mitigation",
            "sources",
            "answer",
        }:
            return lowered
        return None

    for line in lines:
        h = norm_heading(line)
        if h and prev_norm == h:
            continue
        out.append(line)
        prev_norm = h if h else prev_norm

    return "\n".join(out).strip()


def render_sources_list(research):
    if not research:
        st.info("No research chunks returned.")
        return
    for i, r in enumerate(research, start=1):
        source = r.get("source", "unknown_source")
        page = r.get("page", "?")
        chunk_id = r.get("chunk_id", "chunk_?")
        score = r.get("score", None)
        if score is None:
            st.write(f"{i}. {source} p.{page} {chunk_id}")
        else:
            st.write(f"{i}. {source} p.{page} {chunk_id} (score={score})")


def load_sample_queries(path: Path) -> List[str]:
    """
    Supports:
    - ["q1", "q2", ...]
    - [{"question": "..."}, ...]
    - {"queries": ["..."]}
    - {"queries": [{"question": "..."}]}
    - {"samples": [...]}, {"questions": [...]}
    """
    if not path.exists():
        return []

    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    def extract_from_list(lst: list) -> List[str]:
        out: List[str] = []
        for x in lst:
            if isinstance(x, str) and x.strip():
                out.append(x.strip())
            elif isinstance(x, dict):
                q = x.get("question") or x.get("q") or x.get("prompt")
                if isinstance(q, str) and q.strip():
                    out.append(q.strip())
        return out

    # Case A: list
    if isinstance(data, list):
        return extract_from_list(data)

    # Case B: dict
    if isinstance(data, dict):
        qs = data.get("queries") or data.get("samples") or data.get("questions")
        if isinstance(qs, list):
            return extract_from_list(qs)

    return []


def set_question_from_example():
    selected = st.session_state.get("selected_example") or ""
    if selected.strip():
        st.session_state["question"] = selected.strip()


def security_summary_text() -> str:
    return (
        "Injection Guard is enabled. Queries that try to override system rules, request hidden prompts, "
        "or include common prompt-injection patterns will be blocked before reaching the workflow."
    )


# Header
col_logo, col_title = st.columns([1, 8], vertical_alignment="center")

with col_logo:
    st.image("app/logo.png", width=200)

with col_title:
    st.markdown(
        """
        <h1 style='margin:0; font-weight:700;'>
            Healthcare Agent Copilot
        </h1>
        """,
        unsafe_allow_html=True
    )


# Sidebar
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_QUERIES_FILE = PROJECT_ROOT / "eval" / "sample_queries.json"
sample_queries = load_sample_queries(SAMPLE_QUERIES_FILE)

with st.sidebar:
    st.image("app/logo.png", width=200)
    st.title("Healthcare Agent Copilot")
    st.header("Settings")
    k = st.slider("Top-K retrieval chunks", min_value=3, max_value=10, value=5, step=1)

    st.markdown("---")
    show_trace = st.checkbox("Show agent trace", value=True)
    show_debug = st.checkbox("Show debug (raw JSON)", value=False)

    st.markdown("---")
    st.subheader("Security")
    st.caption("Prompt injection protection: ON")
    st.checkbox("Show security details", key="show_security_details")

    if st.session_state.get("show_security_details"):
        st.info(security_summary_text())

    # Sample queries in UI
    st.markdown("---")
    st.subheader("Example questions")

    if sample_queries:
        st.selectbox(
            "Choose an example",
            options=[""] + sample_queries,
            key="selected_example",
            on_change=set_question_from_example,
            help="Selecting an example will populate the question box.",
        )
    else:
        st.caption("No sample queries found at eval/sample_queries.json")

    st.markdown("---")
    st.subheader("Tips")
    st.write("- Prefer questions matching your PDFs.")
    st.write("- If citations fail, increase Top-K or add documents.")
    st.write("- Use governance / safety / ROI type questions.")

# Question + Buttons
st.subheader("Ask a question")

q_col, btn_col = st.columns([6, 1], vertical_alignment="top")

with q_col:
    st.text_area(
        label="",
        key="question",
        height=120,
        placeholder="Type your question here...",
    )

with btn_col:
    run_clicked = st.button("Run", use_container_width=True)
    st.button("Clear", use_container_width=True, on_click=clear_all)


# Run workflow
if run_clicked:
    st.session_state["last_error"] = None
    st.session_state["status"] = "Running..."

    q = (st.session_state.get("question") or "").strip()
    if not q:
        st.warning("Please enter a question.")
        st.session_state["status"] = "Ready"
    else:
        # Prompt injection protection (block before workflow)
        if is_prompt_injection(q):
            st.session_state["last_result"] = None
            st.session_state["status"] = "Blocked"
            st.session_state["last_error"] = "Prompt injection detected. Query blocked."
        else:
            try:
                with st.spinner("Running workflow..."):
                    result = app.invoke({"question": q, "k": k})

                st.session_state["last_result"] = result
                st.session_state["status"] = "Ready"

            except Exception as e:
                st.session_state["last_error"] = f"{type(e).__name__}: {e}"
                st.session_state["last_result"] = None
                st.session_state["status"] = "Error"



# Metrics row
result = st.session_state.get("last_result")
last_error = st.session_state.get("last_error")
status = st.session_state.get("status", "Ready")

verified = False
attempts = 0
topk_used = k

if result:
    verified = bool(result.get("verified", False))
    attempts = int(result.get("attempts", 0) or 0)
    topk_used = int(result.get("k", k) or k)

verified_text = "Yes" if verified else "No"
verified_color = "#22c55e" if verified else "#ef4444"

# Security badge
security_text = "Injection Guard: ON"
security_color = "#2563eb"

st.markdown(
    f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="metric-label">Verified citations</div>
    <div class="metric-value" style="color:{verified_color}">{verified_text}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Attempts</div>
    <div class="metric-value">{attempts}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Top-K</div>
    <div class="metric-value">{topk_used}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Security</div>
    <div class="metric-value" style="color:{security_color}">{security_text}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Status</div>
    <div class="metric-value">{status}</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

if last_error:
    st.error(last_error)


# Tabs
tab_answer, tab_sources, tab_trace, tab_debug = st.tabs(["Answer", "Sources", "Trace", "Debug"])

with tab_answer:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.header("Answer")

    if not result:
        st.info("Run a query to see an answer.")
    else:
        final_answer = normalize_answer_sections(result.get("final_answer", "") or "")
        st.markdown(final_answer)

    st.markdown("</div>", unsafe_allow_html=True)

with tab_sources:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.header("Sources")

    if not result:
        st.info("Run a query to see sources.")
    else:
        render_sources_list(result.get("research", []) or [])

    st.markdown("</div>", unsafe_allow_html=True)

with tab_trace:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.header("Trace")

    if not show_trace:
        st.info("Enable 'Show agent trace' in the sidebar to view trace.")
    else:
        if not result:
            st.info("Run a query to see trace.")
        else:
            st.subheader("Planner output")
            plan = result.get("plan", "") or ""
            st.code(plan if plan.strip() else "(empty)")

            st.subheader("Draft (writer output)")
            draft = result.get("draft", "") or ""
            st.code(draft if draft.strip() else "(empty)")

            failure_reason = result.get("failure_reason", "") or ""
            if failure_reason.strip():
                st.subheader("Failure reason")
                st.write(failure_reason)

    st.markdown("</div>", unsafe_allow_html=True)

with tab_debug:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.header("Debug")

    if not show_debug:
        st.info("Enable 'Show debug (raw JSON)' in the sidebar to view raw output.")
    else:
        if not result:
            st.info("Run a query to see raw JSON.")
        else:
            st.json(result)

    st.markdown("</div>", unsafe_allow_html=True)