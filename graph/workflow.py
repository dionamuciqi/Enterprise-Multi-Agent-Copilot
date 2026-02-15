from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from agents.planner import run_planner
from agents.researcher import run_research
from agents.writer import run_writer
from agents.verifier import run_verifier


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


MAX_ATTEMPTS = 2


def planner(state: AgentState):
    plan = run_planner(state["question"])
    return {"plan": plan, "attempts": 0}


def researcher(state: AgentState):
    k = state.get("k", 5)
    docs = run_research(state["question"], k=k)
    return {"research": docs}


def writer(state: AgentState):
    draft = run_writer(state["question"], state.get("research", []))
    return {"draft": draft}


def verifier(state: AgentState):
    draft = state.get("draft", "")
    research = state.get("research", [])
    verified = run_verifier(draft, research)

    attempts = state.get("attempts", 0) + 1
    update: AgentState = {"verified": verified, "attempts": attempts}

    # If not verified, increase k slightly and retry (up to MAX_ATTEMPTS)
    if not verified and attempts < MAX_ATTEMPTS:
        update["k"] = min(state.get("k", 5) + 2, 10)

    # If exhausted attempts and still not verified, set a safe fallback answer
    if not verified and attempts >= MAX_ATTEMPTS:
        update["failure_reason"] = "Could not produce a citation-grounded answer after retries."
        update["final_answer"] = (
            "I could not produce an answer with reliable citations from the provided documents. "
            "Try rephrasing the question or add more relevant documents."
        )

    return update


def deliver(state: AgentState):
    # If verifier already set a fallback final_answer, keep it
    if state.get("final_answer"):
        return {"final_answer": state["final_answer"]}

    return {"final_answer": state.get("draft", "")}


def should_retry(state: AgentState) -> str:
    verified = state.get("verified", False)
    attempts = state.get("attempts", 0)

    if verified:
        return "deliver"

    if attempts < MAX_ATTEMPTS:
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
        {
            "researcher": "researcher",
            "deliver": "deliver",
        },
    )

    graph.add_edge("deliver", END)

    return graph.compile()
