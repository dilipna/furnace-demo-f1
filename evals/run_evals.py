"""Installed by Furnace Forge: run the app's answer path on an eval dataset and
apply deterministic checks. Needs a reachable model endpoint (the app's own
LLM_BASE_URL); it is run by Furnace Guard on PRs, not by plain `pytest`.

    python evals/run_evals.py evals/datasets/questions.jsonl --out evals/results.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from furnace_harness import render  # noqa: E402
from app.llm import client as client  # noqa: E402

CITATION = re.compile(r"\[doc:([A-Za-z0-9_.\-]+)\]")
NOT_FOUND = re.compile(r"(?i)could not find (?:that|this|it) in")


def check_citations(answer, retrieved):
    cited = set(CITATION.findall(answer))
    if not cited:
        if NOT_FOUND.search(answer):
            return "PASS", "documented not-found answer"
        return "FAIL", "answer has no citation"
    unknown = sorted(cited - set(retrieved))
    if unknown:
        return "FAIL", "cites ids that were not retrieved: " + ", ".join(unknown)
    return "PASS", f"{len(cited)} cited id(s), all retrieved"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--model", default="lab")
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--out", default="evals/results.json")
    a = ap.parse_args()
    rows = [json.loads(line) for line in Path(a.dataset).read_text(encoding="utf-8").splitlines() if line.strip()]
    results = []
    for row in rows:
        messages = render(row["question"])
        context = messages[-1]["content"]
        retrieved = CITATION.findall(context)
        resp = client.chat.completions.create(model=a.model, messages=messages, max_tokens=a.max_tokens, temperature=0)
        answer = resp.choices[0].message.content or ""
        verdict, reason = check_citations(answer, retrieved)
        results.append({"id": row["id"], "question": row["question"], "answer": answer, "retrieved": retrieved,
                        "expected_doc": row.get("expected_doc"), "citation_required": verdict, "reason": reason})
    passed = sum(r["citation_required"] == "PASS" for r in results)
    Path(a.out).write_text(json.dumps({"n": len(results), "citation_required_pass": passed, "results": results}, indent=2), encoding="utf-8")
    print(f"citation_required: {passed}/{len(results)} PASS")


if __name__ == "__main__":
    main()
