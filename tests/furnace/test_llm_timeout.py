"""Installed by Furnace Forge.

The LLM client must carry an explicit timeout, so a stalled model server cannot
hold a user request open for the SDK default (10 minutes for the OpenAI SDK).
"""

import app.llm as target


def test_llm_client_has_explicit_timeout():
    timeout = target.client.timeout
    seconds = getattr(timeout, "read", timeout)
    assert seconds is not None and float(seconds) <= 120
