from langchain_openai import ChatOpenAI


def run_writer(question: str, research: list):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    context = "\n\n".join(
        [
            f"[{r['source']} p.{r['page']} {r['chunk_id']}]\n{r['text']}"
            for r in research
        ]
    )

    prompt = f"""
You are an enterprise healthcare AI consultant.

CRITICAL CITATION RULES:
- Use ONLY citation tags that appear in the Context EXACTLY as written.
- NEVER invent citation tags.
- Every factual claim must include an inline citation tag.

You must produce a structured response with the following sections:

1. Executive Summary (MAX 150 words)
   - STRICT LIMIT: 150 words maximum.
   - If longer than 150 words, rewrite until it is <=150 words.
   - Must include inline citation tags like [HIMSS_AI_Adoption_Hospitals.pdf p.1 chunk_576].

2. Client-ready Email
   - Professional tone
   - Subject line
   - Clear greeting and closing

3. Action List
   - Table with columns: Owner | Due Date | Confidence

4. Key Risks and Mitigation
   - Bullet format
   - Grounded in provided sources

5. Sources
   - List all citation tags used (must match Context exactly)

Only use information from the context below.
Do not invent facts.
Do not fabricate citations.

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)
    return response.content
