from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from retrieval.vector_store import retrieve


# --- STATE ---
class AgentState(TypedDict):
    question: str
    plan: str
    research: List[dict]
    draft: str
    verified: bool
    final_answer: str


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# --- NODES ---

def planner(state: AgentState):
    prompt = f"""
    Create a short action plan to answer this question:
    {state['question']}
    """
    plan = llm.invoke(prompt).content
    return {"plan": plan}


def researcher(state: AgentState):
    docs = retrieve(state["question"], k=5)
    return {"research": docs}


def writer(state: AgentState):
    evidence_text = "\n\n".join(
        [f"{d['text']}\n(Source: {d['source']} p.{d['page']})"
         for d in state["research"]]
    )

    prompt = f"""
    Using ONLY the following evidence, write a structured answer.

    {evidence_text}

    Question:
    {state['question']}
    """

    draft = llm.invoke(prompt).content
    return {"draft": draft}


def verifier(state: AgentState):
    verified = "Source:" in state["draft"]
    return {"verified": verified}


def deliver(state: AgentState):
    return {"final_answer": state["draft"]}


# --- GRAPH ---

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