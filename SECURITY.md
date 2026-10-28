# Security Policy

## Intended use

This project is a triage aid for reports from systems you own or are authorized to assess. It is not a scanner, exploit, proof of exploitability, or substitute for a human security review.

## Do not submit sensitive data

- Never commit `.env` or expose `GROQ_API_KEY` in frontend code, screenshots, logs, or issues.
- Use synthetic or redacted reports. Do not send credentials, personal data, private source code, or confidential program information to an external API unless you are explicitly authorized and have reviewed the provider's current terms and data handling policy.
- Keep the app behind authentication before exposing it to an untrusted network. This starter does not implement user accounts or authorization.
- Do not auto-close reports, run tests against targets, or take security actions solely from model output.

## Reporting a vulnerability in this project

Please avoid posting secrets or live target information in a public issue. Report reproducible security concerns privately to the maintainer first.
