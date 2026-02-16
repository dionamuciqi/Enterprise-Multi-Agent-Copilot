import re


def _extract_exec_summary(text: str) -> str:
    # Find section that starts with "Executive Summary"
    m = re.search(r"Executive Summary\s*(.*?)(\n###|\n\d\.|\Z)", text, flags=re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    return m.group(1).strip()


def run_verifier(draft: str, research: list = None) -> bool:
    # 1) block fake tag 
    if "[source" in draft.lower():
        return False

    # 2) must contain at least one citation tag like [something]
    if not re.search(r"\[[^\]]+\]", draft):
        return False

    # 3) enforce executive summary word count
    exec_summary = _extract_exec_summary(draft)
    if exec_summary:
        words = len(exec_summary.split())
        if words > 150:
            return False
    else:
        # if can't find the section, fail
        return False

    return True
