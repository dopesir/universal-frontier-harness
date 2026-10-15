"""Fast AST and syntax integrity guard (<15ms).

Deterministic syntax validation for Python, JSON, JavaScript, and TypeScript.
Operates with zero external dependencies using Python standard library.
"""

from __future__ import annotations

import ast
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LintResult:
    valid: bool
    errors: list[str]
    duration_ms: float
    file_type: str


def check_delimiter_balance(source: str) -> list[str]:
    """Scans for unclosed brackets, braces, parentheses, and string literals."""
    errors = []
    stack = []
    matching = {")": "(", "}": "{", "]": "["}
    openings = set(matching.values())
    closings = set(matching.keys())

    # Strip single and multi-line comments for JS/TS/C/Java
    cleaned = []
    i = 0
    n = len(source)
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    escaped = False

    while i < n:
        char = source[i]
        nxt = source[i + 1] if i + 1 < n else ""

        if escaped:
            escaped = False
            i += 1
            continue

        if char == "\\":
            escaped = True
            i += 1
            continue

        # String handling
        if char == "'" and not in_double_quote and not in_backtick:
            in_single_quote = not in_single_quote
            i += 1
            continue
        if char == '"' and not in_single_quote and not in_backtick:
            in_double_quote = not in_double_quote
            i += 1
            continue
        if char == "`" and not in_single_quote and not in_double_quote:
            in_backtick = not in_backtick
            i += 1
            continue

        if in_single_quote or in_double_quote or in_backtick:
            i += 1
            continue

        # Comment handling
        if char == "/" and nxt == "/":
            # Skip until newline
            while i < n and source[i] != "\n":
                i += 1
            continue
        if char == "/" and nxt == "*":
            # Skip until */
            i += 2
            while i < n - 1 and not (source[i] == "*" and source[i + 1] == "/"):
                i += 1
            i += 2
            continue

        # Delimiter stacking
        if char in openings:
            stack.append((char, i))
        elif char in closings:
            if not stack:
                errors.append(f"Unmatched closing delimiter '{char}' at character position {i}")
            else:
                last_open, last_pos = stack.pop()
                if matching[char] != last_open:
                    errors.append(f"Mismatched delimiter: opened '{last_open}' at {last_pos}, closed with '{char}' at {i}")

        i += 1

    if in_single_quote:
        errors.append("Unterminated single quote (') string literal")
    if in_double_quote:
        errors.append("Unterminated double quote (\") string literal")
    if in_backtick:
        errors.append("Unterminated template literal (`) string")
    if stack:
        for unclosed, pos in stack:
            errors.append(f"Unclosed opening delimiter '{unclosed}' at character position {pos}")

    return errors


def lint_file(file_path: str | Path) -> LintResult:
    """Deterministically validates file syntax."""
    start = time.perf_counter()
    path = Path(file_path)
    if not path.is_file():
        return LintResult(
            valid=False,
            errors=[f"File not found: {file_path}"],
            duration_ms=(time.perf_counter() - start) * 1000,
            file_type="unknown",
        )

    ext = path.suffix.lower()
    errors: list[str] = []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return LintResult(
            valid=False,
            errors=[f"Failed to read file: {e}"],
            duration_ms=(time.perf_counter() - start) * 1000,
            file_type=ext,
        )

    file_type = ext.lstrip(".") or "txt"

    if ext == ".py":
        try:
            ast.parse(content, filename=str(path))
        except SyntaxError as e:
            errors.append(f"Python SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}")
    elif ext == ".json":
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            errors.append(f"JSONDecodeError at line {e.lineno}, col {e.colno}: {e.msg}")
    elif ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
        errors.extend(check_delimiter_balance(content))
    else:
        # Default delimiter check for general source code
        errors.extend(check_delimiter_balance(content))

    duration_ms = (time.perf_counter() - start) * 1000
    return LintResult(
        valid=len(errors) == 0,
        errors=errors,
        duration_ms=duration_ms,
        file_type=file_type,
    )
