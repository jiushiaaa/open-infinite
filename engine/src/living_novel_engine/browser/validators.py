"""Input validators for the read-only worldline browser.

All HTTP-facing identifier inputs must pass through :func:`safe_id` before
being concatenated onto disk paths. Centralising the rule here makes the
audit surface explicit:

URL parameter audit (v0.4.1):

    GET /api/stories/<slug>                           -> safe_id(slug)
    GET /api/runs?story_slug=<slug>                   -> safe_id(slug)
    GET /api/tree?story_slug=<slug>                   -> safe_id(slug)
    GET /api/runs/<run_id>                            -> safe_id(run_id)
    GET /api/runs/<run_id>/branches/<branch_id>       -> safe_id(both)

Static asset paths (``/static/<rel>``) are validated separately via
``Path.resolve()`` + ``startswith(static_root)`` because they need to allow
sub-directories like ``static/img/foo.svg``.
"""

from __future__ import annotations

import re

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

MAX_ID_LEN = 128


def safe_id(value: str | None) -> str | None:
    """Return ``value`` if it is a safe filesystem identifier, else ``None``.

    The accepted alphabet is ``[A-Za-z0-9._-]`` with a leading alphanumeric;
    ``..`` substrings are rejected to defend against path traversal even
    though the regex already forbids them in practice. The length cap matches
    typical filesystem identifier limits without being overly restrictive.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    if len(value) > MAX_ID_LEN:
        return None
    if not _SAFE_ID_RE.match(value):
        return None
    if ".." in value:
        return None
    return value
