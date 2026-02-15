from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from agents.planner import run_planner
from agents.researcher import run_research
from agents.writer import run_writer
from agents.verifier import run_verifier

MAX_ATTEMPTS = 2

class AgentState(TypedDict, total=False):
    question: str
    k: int

    plan: str
    research: List[dict]
    draft: str

    verified: bool
    attempts: int
    final_answer: str
    failure_reason: str


def planner(state: AgentState):
    plan = run_planner(state["question"])
    return {"plan": plan, "attempts": 0}


def researcher(state: AgentState):
    k = state.get("k", 5)
    docs = run_research(state["question"], k=k)
    return {"research": docs}


def writer(state: AgentState):
    draft = run_writer(state["question"], state["research"])
    return {"draft": draft}


def verifier(state: AgentState):
    verified = run_verifier(state["draft"], state["research"])
    attempts = state.get("attempts", 0) + 1
    return {"verified": verified, "attempts": attempts}

    # If not verified, increase k and retry (up to MAX_ATTEMPTS)
    if not verified and attempts < MAX_ATTEMPTS:
        update["k"] = min(state.get("k", 5) + 2, 10)

    # If exhausted attempts, set strong fallback (client-safe)
    if not verified and attempts >= MAX_ATTEMPTS:
        update["failure_reason"] = "Insufficient citation-grounded evidence in the indexed documents."
        update["final_answer"] = (
            "Subject: Unable to produce a citation-grounded answer\n"
            "To: Hospital Leadership Team\n"
            "Greeting: Hello,\n\n"
            "Executive Summary (<=150 words):\n"
            "I could not produce a reliable answer grounded in the currently indexed documents. "
            "The retrieved evidence did not provide enough support to make a client-ready recommendation with citations.\n\n"
            "Recommended Next Steps:\n"
            "- Add more relevant hospital operations / governance PDFs to the data folder.\n"
            "- Re-run indexing and try again with a more specific question.\n\n"
            "Sources Used:\n"
            "- None (insufficient evidence)\n"
        )

    return update


def deliver(state: AgentState):
    if state.get("final_answer"):
        return {"final_answer": state["final_answer"]}
    return {"final_answer": state.get("draft", "")}


def should_retry(state: AgentState) -> str:
    if state.get("verified", False):
        return "deliver"
    if state.get("attempts", 0) < MAX_ATTEMPTS:
        return "researcher"
    return "deliver"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner)
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_node("verifier", verifier)
    graph.add_node("deliver", deliver)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "verifier")

    graph.add_conditional_edges(
        "verifier",
        should_retry,
        {"researcher": "researcher", "deliver": "deliver"},
    )

    graph.add_edge("deliver", END)

    return graph.compile()
