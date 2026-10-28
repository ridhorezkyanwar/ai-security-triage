"""Controlled vulnerability taxonomy and analyst-facing guidance."""

CATEGORY_DESCRIPTIONS = {
    "xss": "Cross-site scripting (XSS)",
    "sqli": "SQL injection",
    "ssrf": "Server-side request forgery (SSRF)",
    "broken_access_control": "Broken access control / IDOR",
    "authentication_session": "Authentication or session management",
    "sensitive_data_exposure": "Sensitive data exposure",
    "insecure_configuration": "Insecure configuration",
    "other": "Other vulnerability category",
    "insufficient_evidence": "Insufficient evidence to classify",
}

CATEGORY_CRITERIA = {
    "xss": (
        "Evidence that attacker-controlled input is interpreted as active "
        "script or HTML in a browser, rather than merely being reflected as text."
    ),
    "sqli": (
        "Evidence that untrusted input changes the structure or behavior of a "
        "database query, not just a database error without further evidence."
    ),
    "ssrf": (
        "Evidence that a server-side component makes a request to a destination "
        "influenced by the user, with enough detail to distinguish SSRF from a client-side request."
    ),
    "broken_access_control": (
        "Evidence that a user can access or change a resource or action that the "
        "server should deny, including a plausible IDOR or authorization bypass."
    ),
    "authentication_session": (
        "Evidence of a flaw in authentication, session creation, session handling, "
        "or identity verification."
    ),
    "sensitive_data_exposure": (
        "Evidence that confidential or personal data is exposed to an unauthorized "
        "party or stored/transmitted without appropriate protection."
    ),
    "insecure_configuration": (
        "Evidence that a security-relevant deployment or application setting is "
        "unsafe, such as exposed debug functionality or default credentials."
    ),
    "other": (
        "A plausible security issue that does not best fit the other defined categories."
    ),
    "insufficient_evidence": (
        "The report lacks enough concrete information to classify a specific "
        "vulnerability reliably, or describes impact without reproducible technical evidence."
    ),
}

EVIDENCE_CRITERIA = {
    "actionable": (
        "Includes concrete, sanitized technical details such as an affected endpoint, "
        "reproduction steps, and observed versus expected behavior. Evidence supports review; it does not prove exploitability."
    ),
    "partial": (
        "Contains some relevant technical details, but important reproduction steps, "
        "scope, impact, or observed behavior are missing."
    ),
    "insufficient": (
        "Mostly a claim, suspicion, or impact statement without enough concrete technical evidence to assess it."
    ),
}

RECOMMENDATIONS = {
    "xss": (
        "In an authorized test environment, verify how the application handles "
        "untrusted output and apply context-appropriate output encoding or sanitization."
    ),
    "sqli": (
        "Review database access paths and use parameterized queries or safe query APIs; "
        "validate with non-destructive tests in an authorized environment."
    ),
    "ssrf": (
        "Review server-side URL fetching, destination allowlists, redirect handling, "
        "and network egress controls. Validate only against systems you are authorized to test."
    ),
    "broken_access_control": (
        "Check server-side authorization for every resource and action using separate "
        "authorized test accounts; do not access other users' real data."
    ),
    "authentication_session": (
        "Review identity verification, session rotation, expiration, cookie flags, and "
        "re-authentication requirements in a controlled test environment."
    ),
    "sensitive_data_exposure": (
        "Confirm the data classification and intended access policy using synthetic or "
        "redacted evidence, then review authorization, data minimization, and transport/storage protections."
    ),
    "insecure_configuration": (
        "Compare the observed configuration with a secure baseline and remove exposed "
        "debug, administrative, or default-access functionality where appropriate."
    ),
    "other": (
        "Have a security reviewer map the evidence to the application's threat model "
        "and the program's published scope before taking action."
    ),
    "insufficient_evidence": (
        "Request the affected in-scope component, sanitized reproduction steps, expected "
        "versus observed behavior, and a minimal redacted request/response pair where relevant."
    ),
}
