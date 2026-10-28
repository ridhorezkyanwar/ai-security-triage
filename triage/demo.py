"""Offline-only heuristic mode to exercise the UI without an API key.

This is deliberately not presented as an AI prediction or a security scanner.
"""

from __future__ import annotations

import re
from typing import Any

from triage.categories import CATEGORY_DESCRIPTIONS

PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("xss", ("cross-site scripting", "xss", "javascript alert", "script executes", "script execution in browser")),
    ("sqli", ("sql injection", "sqli", "union select", "database query injection", "' or '1'='1")),
    ("ssrf", ("server-side request forgery", "ssrf", "server side request forgery")),
    ("broken_access_control", ("idor", "insecure direct object reference", "broken access control", "horizontal privilege", "authorization bypass")),
    ("authentication_session", ("session fixation", "broken authentication", "session hijack", "authentication bypass", "session management")),
    ("sensitive_data_exposure", ("sensitive data exposure", "exposes personal data", "data leak", "leaks personal data", "confidential data exposed")),
    ("insecure_configuration", ("insecure configuration", "debug mode enabled", "default credentials", "directory listing", "misconfiguration")),
]

ACTIONABLE_MARKERS = (
    "steps to reproduce", "reproduction steps", "expected:", "observed:",
    "request:", "response:", "endpoint:", "http/1.1", "status code",
)
PARTIAL_MARKERS = ("endpoint", "request", "response", "reproduced", "screenshot", "parameter")


def classify_demo(report: str) -> dict[str, Any]:
    text = report.lower()
    category = "other"
    matched = False
    for candidate, phrases in PATTERNS:
        if any(phrase in text for phrase in phrases):
            category = candidate
            matched = True
            break

    if not matched and len(text.strip()) < 80:
        category = "insufficient_evidence"

    actionable_count = sum(marker in text for marker in ACTIONABLE_MARKERS)
    partial_count = sum(marker in text for marker in PARTIAL_MARKERS)
    if actionable_count >= 2 or ("steps to reproduce" in text and partial_count >= 1):
        evidence_quality = "actionable"
    elif partial_count >= 1 or len(text.strip()) >= 180:
        evidence_quality = "partial"
    else:
        evidence_quality = "insufficient"

    # Demo mode deliberately has no numeric confidence or model probability.
    return {
        "model": "local-demo-rules",
        "category": category,
        "category_confidence": None,
        "category_probabilities": {},
        "evidence_quality": evidence_quality,
        "evidence_confidence": None,
        "usage": {"input_tokens": 0, "output_tokens": 0},
        "demo_note": (
            "Offline local keyword heuristic for testing the application only. "
            "It does not call a hosted AI model and should not be used to decide whether a finding is valid."
        ),
    }
