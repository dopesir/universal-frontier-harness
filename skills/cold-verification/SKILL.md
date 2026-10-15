---
name: cold-verification
description: Fresh-context independent verification procedure for completed work. Evaluates deliverables against specifications with fresh eyes, devoid of producer bias.
---

# Cold Verification Gate

## Protocol
1. **Fresh Context**: Conducted without relying on conversational assumptions or intermediate work notes.
2. **Independent Check**: Re-run the automated test suite from clean terminal state.
3. **Specification Audit**: Compare git diff directly against the user's initial requirements and constraints.
4. **Verification Levels**:
   - **BUILT**: Code bundles/compiles without errors.
   - **TESTED**: Automated test suite passes with exit code 0.
   - **RUNTIME VERIFIED**: Server responded with HTTP 200 or UI element verified.
   - **NOT VERIFIED**: Explicitly disclosed if any check was skipped.
