from retrieval.vector_store import retrieve

def run_researcher(question: str, k: int = 5):
    overfetch = max(30, k * 10)

    queries = [
        question,
        f"hospital AI adoption operations workflow integration {question}",
        f"AI copilot hospital operations governance oversight EHR integration",
        f"alert fatigue privacy-preserving techniques regulatory compliance",
    ]

    all_results = []
    for q in queries:
        all_results.extend(retrieve(q, k=overfetch))

    # dedupe by (source,page,chunk_id), keep best (lowest distance score)
    best = {}
    for r in all_results:
        key = (r.get("source"), r.get("page"), r.get("chunk_id"))
        if key not in best or r["score"] < best[key]["score"]:
            best[key] = r

    # sort by score ascending (Chroma distance: smaller = closer)
    merged = sorted(best.values(), key=lambda x: x["score"])
    return merged[:max(10, k)]  
