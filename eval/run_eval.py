import json
from graph.workflow import build_graph


def main():
    app = build_graph()

    with open("eval/sample_queries.json", "r", encoding="utf-8") as f:
        queries = json.load(f)

    for i, q in enumerate(queries, 1):
        result = app.invoke({"question": q})
        answer = result.get("final_answer", "")

        print("\n" + "=" * 80)
        print(f"QUERY {i}: {q}")
        print("-" * 80)
        print(answer[:1200])  
        print("\n")


if __name__ == "__main__":
    main()
