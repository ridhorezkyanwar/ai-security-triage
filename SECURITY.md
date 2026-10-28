# Security Policy

## Intended use

This project is a triage aid for reports from systems you own or are authorized to assess. It is not a scanner, exploit, proof of exploitability, or substitute for a human security review.

## Do not submit sensitive data

- Never commit `.env` or expose `GROQ_API_KEY` in frontend code, screenshots, logs, or issues.
- Use synthetic or redacted reports. Do not send credentials, personal data, private source code, or confidential program information to an external API unless you are explicitly authorized and have reviewed the provider's current terms and data handling policy.
- For hosted/public deployment, set `REQUIRE_AUTH=true` and a strong, unique `APP_ACCESS_PASSWORD`. The Render blueprint and Dockerfile enable this fail-closed behavior: if the password is missing, non-health routes return HTTP 503 instead of becoming public. This starter still uses shared HTTP Basic authentication and does not implement individual user accounts or authorization.
- Do not auto-close reports, run tests against targets, or take security actions solely from model output.

## Reporting a vulnerability in this project

Please avoid posting secrets or live target information in a public issue. Report reproducible security concerns privately to the maintainer first.
