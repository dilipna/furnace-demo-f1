"""Installed by Furnace Forge.

Guards the shared prompt prefix: every request must start with the same text, so the
serving engine can reuse the cached prefill of that prefix (prefix/KV caching).
A per-request value (id, timestamp, user name) placed before the static text would
silently disable that reuse and raise time-to-first-token.
Measured when installed: two different requests shared 3954 leading characters.
"""

from furnace_harness import render

MIN_SHARED_CHARS = 3558
QUESTIONS = ["How much does the Studio plan cost?", "How many kilns does the Workshop plan support?", "Is there a free trial?", "When are invoices issued?"]


def _text(question):
    return "".join(f"{m['role']}\n{m['content']}\n" for m in render(question))


def _shared(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def test_prompt_prefix_is_shared_across_requests():
    first = _text(QUESTIONS[0])
    for q in QUESTIONS[1:]:
        shared = _shared(first, _text(q))
        assert shared >= MIN_SHARED_CHARS, (
            f"requests diverge after {shared} characters (need {MIN_SHARED_CHARS}); "
            f"first difference: {first[shared:shared + 60]!r}"
        )
