"""Installed by Furnace Forge.

`create_ticket` (app/tickets.py:10) performs an external side effect and is guarded by
`if not approved`. This test fails if that guard is removed: calling it with
approved=False must not perform any outbound write.
"""

import pytest

import app.tickets as target


class _NoOutbound(Exception):
    pass


def _forbid(*args, **kwargs):
    raise _NoOutbound("outbound call attempted without approval")


def test_create_ticket_requires_approval(monkeypatch):
    monkeypatch.setattr(target.httpx, "post", _forbid)
    with pytest.raises(Exception) as exc:
        target.create_ticket(summary="furnace-test", email="furnace-test", approved=False)
    assert not isinstance(exc.value, _NoOutbound), "side effect executed without approval"
