import re

def run_verifier(draft: str) -> bool:
    pattern = r"\[[^\]]+ p\.\d+ chunk_\d+\]"
    return re.search(pattern, draft) is not None
