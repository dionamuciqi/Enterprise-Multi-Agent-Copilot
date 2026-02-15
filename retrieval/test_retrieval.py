from dotenv import load_dotenv
load_dotenv()

from retrieval.vector_store import index_documents, retrieve

print("Indexing documents...")
index_documents("data")

print("\nTesting retrieval...\n")
results = retrieve("AI copilot adoption in hospital operations", k=3)

for r in results:
    print("SOURCE:", r["source"])
    print("PAGE:", r["page"])
    print("CHUNK:", r["chunk_id"])
    print("SCORE:", r["score"])
    print("-" * 50)
