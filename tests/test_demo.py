from triage.demo import classify_demo
from triage.service import ConfigurationError, run_triage


def test_demo_detects_obvious_xss_keyword_but_labels_it_as_demo():
    result = classify_demo(
        "A synthetic cross-site scripting (XSS) report with steps to reproduce "
        "and an observed response from a controlled test fixture."
    )
    assert result["category"] == "xss"
    assert result["model"] == "local-demo-rules"
    assert result["category_confidence"] is None


def test_demo_does_not_claim_confidence_or_ai_prediction():
    result = run_triage("I suspect a bug, but this is not yet reproduced or evidenced.", mode="demo")
    assert result["mode"] == "demo"
    assert result["manual_review_required"] is True
    assert result["category_confidence"] is None
    assert "local keyword heuristic" in result["demo_note"]


def test_live_mode_requires_api_key():
    try:
        run_triage("A sufficiently long synthetic report description.", mode="groq", api_key="")
    except ConfigurationError as exc:
        assert "GROQ_API_KEY" in str(exc)
    else:
        raise AssertionError("Expected ConfigurationError")


def test_demo_fallback_for_short_vague_report_is_insufficient_evidence():
    result = classify_demo("Maybe a bug")
    assert result["category"] == "insufficient_evidence"
    assert result["evidence_quality"] == "insufficient"
