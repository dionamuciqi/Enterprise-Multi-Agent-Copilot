from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from agents.planner import run_planner
from agents.researcher import run_researcher
from agents.writer import run_writer
from agents.verifier import run_verifier

from utils.security import is_prompt_injection


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

    blocked: bool
    block_reason: str


MAX_ATTEMPTS = 2


def planner(state: AgentState):
    question = state.get("question", "")

    if is_prompt_injection(question):
        return {
            "blocked": True,
            "block_reason": "prompt_injection",
            "verified": False,
            "attempts": 0,
            "final_answer": (
                "The request attempts to override system rules or access restricted information and cannot be fulfilled. "
                "Please rephrase your question about hospital operations using the provided documents."
            ),
        }

    plan = run_planner(question)
    return {"plan": plan, "attempts": 0, "blocked": False}


def researcher(state: AgentState):
    k = state.get("k", 5)
    docs = run_researcher(state.get("question", ""), k=k)
    return {"research": docs}


def writer(state: AgentState):
    draft = run_writer(state.get("question", ""), state.get("research", []))
    return {"draft": draft}


def verifier(state: AgentState):
    verified = run_verifier(state.get("draft", ""), state.get("research", []))

    attempts = state.get("attempts", 0) + 1
    update: AgentState = {"verified": verified, "attempts": attempts}

    if not verified and attempts < MAX_ATTEMPTS:
        update["k"] = min(state.get("k", 5) + 2, 10)

    if not verified and attempts >= MAX_ATTEMPTS:
        update["failure_reason"] = "Could not produce a citation-grounded answer after retries."
        update["final_answer"] = (
            "I could not produce an answer with reliable citations from the provided documents. "
            "Try rephrasing the question or add more relevant documents."
        )

    return update


def deliver(state: AgentState):
    if state.get("final_answer"):
        return {"final_answer": state["final_answer"]}

    return {"final_answer": state.get("draft", "")}


def route_after_planner(state: AgentState) -> str:
    if state.get("blocked", False):
        return "deliver"
    return "researcher"


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

    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "researcher": "researcher",
            "deliver": "deliver",
        },
    )

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
