# Validation Record

## Scope

Validation performed on the generated project files locally. No real Groq API request was sent, no key was used, and no hosting deployment was performed.

## Automated checks

Run from the repository root:

```bash
python -m pytest
```

The test suite uses mocked HTTP responses to verify request shape, output validation, rate-limit/auth error handling, key secrecy in API responses, offline demo behavior, optional HTTP Basic protection, fail-closed behavior when hosted authentication is required but its password is missing, and the secure-by-default behavior when REQUIRE_AUTH is unset. The tests do not prove that the current Groq service, account, model access, or deployment will work live.

## Live validation still required by the user

1. Confirm Vercel is using the Hobby plan and the intended repository/production branch.
2. Set `REQUIRE_AUTH=true`, a strong unique `APP_ACCESS_PASSWORD`, and `APP_ACCESS_USERNAME` in the deployment environment.
3. Create a Groq API key in the console if available under the user's account plan and store it as a deployment secret.
4. Confirm the configured `GROQ_MODEL` is listed by the account, using `/api/models` or Groq's model documentation.
5. Run a single synthetic sample in Groq mode.
6. If live testing succeeds, optionally run a five-case synthetic benchmark and save actual results. Check rate limits before running more.

## Limitations

- The bundled dataset contains 36 synthetic starter examples and is not a representative external benchmark.
- Groq classification outputs do not include calibrated probabilities in this app.
- Human review remains required.
- Cloud inference sends report content to Groq; use synthetic or sanitized reports only.
- Availability, terms, limits, and model identifiers can change. Check official Groq docs before production use.
