from graph.workflow import build_graph

app = build_graph()

result = app.invoke({
    "question": "How should a hospital adopt an AI copilot for operations?"
})

print("\nFINAL ANSWER:\n")
print(result["final_answer"])
