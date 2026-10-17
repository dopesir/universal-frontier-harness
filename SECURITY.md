# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 7.0.x   | :white_check_mark: |
| < 7.0   | :x:                |

---

## Security & Data Privacy Guarantees

Universal Frontier Harness is designed with a **privacy-first, local-only architecture**:

1. **Zero Telemetry**: The harness contains zero telemetry, analytics, or outbound network calls.
2. **Zero Secrets Logging**: File inspection and evidence recording run strictly locally inside `.agents/sessions/`. Command line logs do not extract or send environment variables or credentials.
3. **Local Scope Fencing**: The pre-tool hook restricts file writes to the target project directory. It cannot modify files outside the declared workspace scope.
4. **Sandboxed Integration Tests**: All unit and integration test fixtures run inside isolated temporary directories (`tempfile.mkdtemp`) and clean up after execution.

---

## Reporting a Vulnerability

If you discover a security vulnerability or bypass in the harness:

1. **Do not open a public issue.**
2. Email details to: **nobuswork.services@gmail.com**
3. Include:
   - Description of the bypass or vulnerability.
   - Minimal reproduction script or test case.
   - Impact assessment across supported agent hosts.
4. You will receive an initial response within 48 hours. Fixes will be prepared in an isolated branch and tagged as a patch release.
