# Security Policy

## Supported Versions

The following versions of AUI currently receive security updates:

| Version | Supported          |
|---------|--------------------|
| latest  | ✅ Yes             |
| < latest | ❌ No             |

We recommend always running the latest release. Once a new version is published, security patches for previous versions are provided only for critical vulnerabilities at the maintainers' discretion.

## Reporting a Vulnerability

**⚠️ Please do NOT report security vulnerabilities through public GitHub Issues.**

If you discover a security vulnerability in AUI, we appreciate your responsible disclosure. Please report it through one of the following channels:

### Preferred: GitHub Private Vulnerability Reporting

1. Navigate to the [AUI Security Advisories](https://github.com/axtoncarroll/aui/security/advisories) page.
2. Click **"Report a vulnerability"**.
3. Provide a detailed description of the vulnerability, including:
   - **Description** — a clear explanation of the vulnerability and its impact.
   - **Reproduction steps** — a minimal, step-by-step guide to reproduce the issue.
   - **Affected versions** — which version(s) of AUI are affected.
   - **Impact assessment** — what an attacker could achieve by exploiting this vulnerability.
   - **Suggested fix** — if you have one, include a patch or mitigation strategy.

### What to Expect

- **Acknowledgment** — we will confirm receipt of your report within **3 business days**.
- **Assessment** — we will investigate and assess the severity within **10 business days**.
- **Resolution** — critical vulnerabilities will be patched and released as quickly as possible. We aim to resolve high-severity issues within **30 days** of confirmation.
- **Credit** — with your permission, we will credit you in the release notes and security advisory.

### Disclosure Policy

- We follow [coordinated vulnerability disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure).
- We ask that you give us reasonable time to address the vulnerability before any public disclosure.
- We will coordinate with you on the timing and content of any public advisory.

## Security Considerations for AUI Users

AUI is a cross-process UI automation system that interacts with operating system accessibility APIs and other process boundaries. Users should be aware of the following:

- **Principle of least privilege** — run AUI with the minimum permissions necessary for your automation task. Avoid running as administrator or root unless explicitly required by the target application.
- **Input validation** — if your automation scripts accept external input (e.g., element names, window titles), sanitize and validate that input before passing it to AUI APIs.
- **Process isolation** — AUI communicates across process boundaries. Ensure that the host environment is trusted and that inter-process communication channels are not exposed to untrusted actors.
- **Dependency auditing** — regularly audit AUI's dependencies for known vulnerabilities using tools like `pip-audit` or GitHub Dependabot.

## Security-Related Configuration

AUI does not require or store credentials. It does not open network sockets or listen on any ports. All automation occurs through local operating system APIs (e.g., Windows UI Automation, AT-SPI2 on Linux).

---

Thank you for helping keep AUI and its users safe.
