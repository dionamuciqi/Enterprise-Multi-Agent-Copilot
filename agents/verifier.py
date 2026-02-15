import re


def run_verifier(draft: str, research: list[dict]) -> bool:
    if not draft or not research:
        return False

    # Extract citation tags inside brackets [...]
    citation_pattern = r"\[([^\]]+)\]"
    citations = re.findall(citation_pattern, draft)

    if not citations:
        return False

    # Build a set of valid citation identifiers from research
    valid_chunks = set()
    for doc in research:
        source = doc.get("source", "")
        page = doc.get("page", "")
        chunk_id = doc.get("chunk_id", "")
        tag = f"{source} p.{page} {chunk_id}"
        valid_chunks.add(tag)

    # Check each citation
    for citation in citations:
        citation_clean = citation.strip()
        if citation_clean not in valid_chunks:
            return False

    return True
