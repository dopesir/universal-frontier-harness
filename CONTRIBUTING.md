# Contributing to Universal Frontier Harness

We welcome contributions from the community to make AI coding agents more reliable, disciplined, and safe.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/universal-frontier/universal-frontier-harness.git
   cd universal-frontier-harness
   ```

2. Run the test suite:
   ```bash
   python -m unittest discover tests
   ```

3. Run the system integrity verifier:
   ```bash
   python scripts/verify_harness.py
   ```

## Contribution Principles

- **Zero Heavy Dependencies**: Core modules and hooks must rely exclusively on Python 3.10+ standard library.
- **Cross-Platform First**: All file operations must explicitly specify `encoding="utf-8"` and use `pathlib.Path` for platform neutrality.
- **Evidence-Backed PRs**: Every PR introducing or changing logic must include automated unit tests that pass with exit code 0.
