# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | ✅                 |
| 0.x     | ❌                 |

Older versions are not supported. Please upgrade to the latest release to benefit from security patches and governance improvements.

---

## Reporting a Vulnerability

If you discover a security vulnerability in this project:

1. **Do not open a public issue.**
2. Please report it privately via GitHub Security Advisories or email the maintainers at:  
   **security@octaneecho.systems** (replace with your preferred contact).
3. Include:
   - A clear description of the vulnerability.
   - Steps to reproduce.
   - Any potential impact or affected components.

---

## Response Process

- We will acknowledge receipt of your report within **72 hours**.
- You will receive updates at least **weekly** until resolution.
- If the vulnerability is accepted:
  - A fix will be developed and tested.
  - A patched release will be published.
  - Security notes will be added to the changelog.
- If the vulnerability is declined:
  - We will provide a clear explanation of why it is not considered a security issue.

---

## Security Practices

- **No secrets in code**: API keys and credentials are never stored in the repository.
- **Governance enforcement**: All prompts and responses are checked against `fintech-policy.yaml`.
- **Logging**: Currently all prompts/responses are logged for audit. In production, only violations will be logged.
- **Rate limiting**: Requests are capped per minute to prevent abuse.
- **Integrity hashing**: Responses are signed with HMAC for tamper detection.
- **Dependency monitoring**: We use Dependabot and GitHub security alerts to patch vulnerabilities quickly.

---

## Responsible Disclosure

We ask that you:
- Give us reasonable time to fix issues before public disclosure.
- Avoid exploiting vulnerabilities beyond proof‑of‑concept.
- Respect user data and privacy during testing.
