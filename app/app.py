import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from graph.workflow import build_graph


st.set_page_config(
    page_title="Enterprise Healthcare Copilot",
    layout="wide"
)

st.title("Enterprise Multi-Agent Copilot (Healthcare)")
st.caption("LangGraph + Retrieval (Chroma) + Citations")


# Build graph once 
@st.cache_resource
def get_app():
    return build_graph()


app = get_app()


with st.sidebar:
    st.header("Settings")
    k = st.slider(
        "Top-K retrieval chunks",
        min_value=3,
        max_value=10,
        value=5,
        step=1
    )
    st.markdown("---")
    st.write("Ask about governance, safety, adoption, ROI, workflows, etc.")


question = st.text_area(
    "Ask a question",
    value="How should a hospital adopt an AI copilot for operations?",
    height=120
)

run = st.button("Run Copilot")


if run:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Running multi-agent workflow..."):
            result = app.invoke({
                "question": question.strip(),
                "k": k
            })

        final_answer = result.get("final_answer", "")
        verified = result.get("verified", False)

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("Answer")
            st.write(final_answer)

        with col2:
            st.subheader("Status")
            st.write(f"Verified citations: {'Yes' if verified else 'No'}")
            st.write(f"Top-K: {k}")

        st.markdown("---")
        st.subheader("Raw Output (Debug)")
        st.json(result)
