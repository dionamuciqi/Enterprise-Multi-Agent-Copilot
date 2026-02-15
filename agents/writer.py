from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run_writer(question: str, research):
    # evidence me citation tags
    evidence_blocks = []
    for d in research:
        tag = f"[{d['source']} p.{d['page']} {d['chunk_id']}]"
        evidence_blocks.append(f"{tag}\n{d['text']}")

    evidence_text = "\n\n---\n\n".join(evidence_blocks)

    prompt = f"""
You are writing a client-ready answer for a hospital.

STRICT RULES:
- Use ONLY the evidence below.
- Every paragraph MUST include at least one citation tag exactly like: [DocumentName p.X chunk_Y]
- If you cannot support a claim from evidence, write: "Not found in sources."

EVIDENCE:
{evidence_text}

QUESTION:
{question}
"""
    return llm.invoke(prompt).content
