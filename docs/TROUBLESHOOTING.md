# Troubleshooting & FAQs

This document addresses common edge cases, error diagnostics, and resolution steps when working with the Universal Frontier Harness.

---

## 1. "Read-before-write violation: file exists but has not been inspected"

### Cause
The agent attempted to edit or write to a file that exists on disk without first viewing or reading it in the active session. This violates Invariant 1 (Reconnaissance Before Mutation).

### Resolution
Instruct the agent to inspect the file first:
```bash
# Antigravity / Agent command
view_file [path/to/file]
```
Once the file path is recorded in `.agents/sessions/<id>/reads.jsonl`, subsequent mutations are automatically permitted.

---

## 2. "Completion blocked: acceptance criteria lack fresh passing evidence"

### Cause
The agent attempted to complete its turn or task, but either:
1. No test suite was executed.
2. The executed test suite failed (`exit_code != 0`).
3. Code was mutated *after* the test was run (stale evidence).
4. The test command did not record passing evidence into `evidence.jsonl`.

### Resolution
Run the project's test suite to produce fresh passing evidence:
```bash
python -m unittest discover tests
# or
pytest tests/
```
The post-tool hook intercepts the passing exit code (`0`) and logs it into `.agents/sessions/<id>/evidence.jsonl`.

---

## 3. "Circuit breaker: tool call fingerprint previously failed"

### Cause
The agent attempted to run an identical tool call (e.g. same failing command or edit) that already failed in the current session.

### Resolution
The circuit breaker prevents infinite retry loops. Instruct the agent:
> *"Stop retrying the command. Inspect the error diagnostic, switch to diagnostic mode, and form an alternative hypothesis."*

To manually reset the circuit breaker for a session, remove or clear:
`.agents/sessions/<id>/failures.jsonl`

---

## 4. "Contract enforcement failure: contract.json is corrupted"

### Cause
A session's `contract.json` was truncated or written with malformed JSON. The harness fails closed to prevent unverified completion.

### Resolution
Delete or fix the corrupted contract file:
```bash
rm .agents/sessions/<id>/contract.json
```
Re-initialize the task contract using `core.contract.save_contract` or start a fresh session.
