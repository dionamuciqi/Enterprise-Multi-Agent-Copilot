from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run_planner(question: str) -> str:
    prompt = f"""
Create a short action plan to answer this question:
{question}
"""
    return llm.invoke(prompt).content
