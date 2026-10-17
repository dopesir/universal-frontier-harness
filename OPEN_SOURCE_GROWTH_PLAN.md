# OPEN SOURCE GROWTH PLAN — Universal Frontier Harness

**Goal**: Sustainable, developer-led discovery and adoption driven by technical utility and evidence, rather than marketing hype.

---

## 1. Zero-Cringe Technical Demonstration Script

A reproducible, 60-second recorded terminal or text walkthrough demonstrating the real problem and mechanical fix:

```bash
# 1. Start in an empty/clean test project
mkdir my-demo-service && cd my-demo-service
git init

# 2. Install the harness with safe defaults
python /path/to/universal-frontier-harness/scripts/init_harness.py .

# 3. Simulate an unmanaged/hallucinating agent attempt (Deliberate Failure)
# Agent mutates a file without running tests and attempts turn completion:
python .agents/hooks/stop_gate.py << 'EOF'
{
  "conversationId": "demo-session"
}
EOF
# Output:
# {"decision": "continue", "reason": "Completion blocked: acceptance criteria lack fresh passing evidence..."}

# 4. Agent runs the test suite to produce verified evidence
pytest tests/  # Exit code: 0

# 5. Stop gate now validates fresh evidence and approves completion
python .agents/hooks/stop_gate.py
# Output:
# {"decision": "allow"}
```

---

## 2. High-Signal Technical Content Topics

Avoid generic promotional posts. Share substantive engineering write-ups based on the empirical discoveries from this audit:

1. **"Why Passive Prompt Invariants Degrade Past 30k Tokens (And Why Mechanical Stop Gates Work)"**:
   - Focus: Softmax attention decay, U-shaped recall curves, and autoregressive self-conditioning.
   - Channel: Hacker News, Lobste.rs, Dev.to.
2. **"Building a Sub-15ms AST Linter Using Pure Python Standard Library"**:
   - Focus: Zero-dependency engineering, lexical delimiter tracking, avoiding heavy native binaries.
   - Channel: Python subreddit (`r/Python`), Medium / personal blog.
3. **"How We Tested for False Evidence in AI Coding Agent Frameworks"**:
   - Focus: String exit codes, contradictory outputs, stale timestamp invalidation on file mutation.
   - Channel: `r/ClaudeAI`, `r/Cursor`, AI agent developer Discords.
4. **"What Universal Frontier Harness Deliberately Does NOT Claim to Solve"**:
   - Focus: Intellectual honesty, model stochasticity, avoiding premature SWE-bench benchmark hype.
   - Channel: GitHub Discussions, LinkedIn builder post.

---

## 3. Structured Developer Feedback Protocol

When inviting peer engineers and beta testers to try the harness, ask these 5 specific diagnostic questions:

1. Did `init_harness.py` cleanly install into your project without clobbering existing configuration?
2. Did the pre-tool read-before-write check catch any uninspected file edits?
3. Did the completion gate ever falsely block you when tests were legitimately passing?
4. Did you experience any latency degradation during tool execution?
5. What was the single most confusing or unhelpful diagnostic message you encountered?

---

## 4. Honest Adoption Telemetry & Metrics

Monitor public, tamper-proof GitHub signals:
- **Repository Traffic & Unique Clones** (via GitHub Insights).
- **External PRs & Issues**: Community bug reports and edge-case contributions.
- **Third-Party Mentions**: Genuine mentions in Cursor, Windsurf, or Antigravity rule sets.
- **Zero Engagement Gaming**: No buying stars, no spamming irrelevant subreddits, no bot upvoting.
