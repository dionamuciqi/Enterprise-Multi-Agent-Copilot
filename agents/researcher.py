from retrieval.vector_store import retrieve

def run_research(question: str, k: int = 5):
    return retrieve(question, k=k)
