# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Reporting a Vulnerability

We take the security of KOSMOS seriously. If you discover a security vulnerability, please follow these steps:

1.  **Do not open a public issue.**
2.  Email the security team at `security@kosmos-ai.example.com`.
3.  Include a detailed description of the vulnerability, steps to reproduce, and potential impact.
4.  We will acknowledge your report within 48 hours.

### AI Safety & Governance

As an AI governance platform, KOSMOS includes specific safeguards:

*   **Kill Switch Protocol**: See `docs/01-governance/kill-switch-protocol.md`.
*   **Prompt Injection**: We use AEGIS agent for input validation.
*   **Data Privacy**: Compliance with GDPR/CCPA is enforced by Athena.

Please report any "jailbreak" or safety bypass techniques found in the agents.
