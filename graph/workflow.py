from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from agents.planner import run_planner
from agents.researcher import run_research
from agents.writer import run_writer
from agents.verifier import run_verifier
from dotenv import load_dotenv
load_dotenv()



class AgentState(TypedDict):
    question: str
    plan: str
    research: List[dict]
    draft: str
    verified: bool
    final_answer: str


def planner(state: AgentState):
    plan = run_planner(state["question"])
    return {"plan": plan}


def researcher(state: AgentState):
    docs = run_research(state["question"], k=5)
    return {"research": docs}


def writer(state: AgentState):
    draft = run_writer(state["question"], state["research"])
    return {"draft": draft}


def verifier(state: AgentState):
    verified = run_verifier(state["draft"])
    return {"verified": verified}


def deliver(state: AgentState):
    # nëse s’është verified, mund ta kthejmë prapë te writer më vonë
    return {"final_answer": state["draft"]}


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
    graph.add_edge("verifier", "deliver")
    graph.add_edge("deliver", END)

    return graph.compile()
