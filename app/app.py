import sys
from pathlib import Path

# Ensure project root is in PYTHONPATH (fix Streamlit module imports)
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from graph.workflow import build_graph

st.set_page_config(page_title="Enterprise Healthcare Copilot", layout="wide")

st.title("Enterprise Multi-Agent Copilot (Healthcare)")
st.caption("LangGraph + Retrieval (Chroma) + Citations")



@st.cache_resource
def get_app():
    return build_graph()

app = get_app()

with st.sidebar:
    st.header("Settings")
    k = st.slider("Top-K retrieval chunks", min_value=3, max_value=10, value=5, step=1)
    st.markdown("---")
    st.write("Ask about governance, safety, adoption, ROI, workflows, etc.")

question = st.text_area(
    "Ask a question",
    value="How should a hospital adopt an AI copilot for operations?",
    height=120
)

run = st.button("Run")

if run:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Running workflow..."):
            result = app.invoke({"question": question.strip(), "k": k})

        final_answer = result.get("final_answer", "")
        verified = result.get("verified", False)
        attempts = result.get("attempts", 0)
        plan = result.get("plan", "")
        research = result.get("research", [])
        failure_reason = result.get("failure_reason", "")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("Answer")
            st.write(final_answer)

        with col2:
            st.subheader("Status")
            st.write("Verified citations:", "Yes" if verified else "No")
            st.write("Attempts:", attempts)
            st.write("Top-K:", k)
            if failure_reason:
                st.write("Failure reason:", failure_reason)

        st.markdown("---")
        st.subheader("Agent Trace")

        st.write("Planner output")
        st.code(plan or "(empty)")

        st.write("Research sources")
        if research:
            for i, r in enumerate(research, start=1):
                st.write(f"{i}. {r.get('source')} p.{r.get('page')} {r.get('chunk_id')} (score={r.get('score')})")
        else:
            st.write("(no research returned)")

        st.markdown("---")
        st.subheader("Raw Output (Debug)")
        st.json(result)
