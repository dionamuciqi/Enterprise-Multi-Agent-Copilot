from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run_writer(question: str, research):
    evidence_blocks = []

    for d in research:
        tag = f"[{d['source']} p.{d['page']} {d['chunk_id']}]"
        evidence_blocks.append(f"{tag}\n{d['text']}")

    evidence_text = "\n\n---\n\n".join(evidence_blocks)

    prompt = f"""
You are an AI strategy consultant writing a client-ready hospital advisory report.

STRICT RULES:
- Use ONLY the evidence below.
- Every section must include citation tags exactly like: [DocumentName p.X chunk_Y]
- If something cannot be supported, write: "Not found in sources."
- Executive Summary must be MAX 150 words.

FORMAT YOUR OUTPUT EXACTLY AS:

1. Executive Summary (≤150 words)

2. Recommended Actions (bullet points)

3. Key Risks and Mitigation

4. Implementation Roadmap (Owner | Timeline | Confidence Level)

5. Sources (list citation tags used)

EVIDENCE:
{evidence_text}

QUESTION:
{question}
"""

    return llm.invoke(prompt).content
