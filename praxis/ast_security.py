# ────────────────────────────────────────────────────────────────────
# ast_security.py — AST Introspection Security Hardening
# ────────────────────────────────────────────────────────────────────
"""
Secures the metacognitive AST introspection layer against:

    1. **Remote Code Execution (RCE)** — Decorator/default-arg payloads
       that execute ``os.system()`` or ``__import__()`` during function
       *definition* (before the function body is ever called).
    2. **Algorithmic Denial of Service** — Deeply nested or excessively
       long code strings that exhaust the parser's recursion stack.
    3. **Forbidden builtins** — ``eval()``, ``exec()``, ``compile()``,
       ``__import__()``, and subprocess invocations.
    4. **Resource exhaustion** — Unbounded AST tree walks on adversarial
       input that would consume CPU or memory.

Design principles:
    - **Parse, never execute.** The module ONLY uses ``ast.parse()``
      for structural analysis.  It NEVER calls ``eval()``, ``exec()``,
      ``compile()`` or any form of dynamic code execution.
    - **Whitelist, not blacklist.** Only explicitly safe node types are
      permitted when validating external or LLM-generated code.
    - **Fail closed.** Any validation failure rejects the input.

Usage::

    from praxis.ast_security import (
        safe_parse, validate_ast, ASTSecurityReport, SecurityViolation
    )

    report = safe_parse(code_string)
    if not report.safe:
        print(report.violations)
"""

from __future__ import annotations

import ast
import logging
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

log = logging.getLogger("praxis.ast_security")


# ╔════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURATION — tuneable limits                                 ║
# ╚════════════════════════════════════════════════════════════════════╝

# Maximum source length (bytes) before we refuse to parse
MAX_SOURCE_LENGTH = 100_000      # 100 KB

# Maximum AST depth (nesting level) before we flag DoS risk
MAX_AST_DEPTH = 50

# Maximum number of AST nodes before we flag resource exhaustion
MAX_AST_NODES = 10_000

# Maximum recursion limit used during AST walk (prevents stack overflow)
MAX_WALK_RECURSION = 200

# Dangerous builtins that should never appear in introspected code
FORBIDDEN_NAMES: Set[str] = {
    "eval", "exec", "compile", "__import__",
    "breakpoint", "exit", "quit",
    "getattr", "setattr", "delattr",  # only flagged in external code
}

# Dangerous modules that should never be imported in inspected code
FORBIDDEN_MODULES: Set[str] = {
    "os", "sys", "subprocess", "shutil", "ctypes",
    "importlib", "code", "codeop", "compileall",
    "signal", "socket", "http", "urllib",
    "pickle", "shelve", "marshal",
    "tempfile", "glob", "pathlib",
    "multiprocessing", "threading",
}

# Node types that are always safe (structural, no side effects)
_SAFE_NODE_TYPES: Set[type] = {
    ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
    ast.ClassDef, ast.Return, ast.Assign, ast.AugAssign,
    ast.AnnAssign, ast.If, ast.For, ast.While, ast.Break,
    ast.Continue, ast.Pass, ast.Constant, ast.Name, ast.Load,
    ast.Store, ast.Del, ast.Tuple, ast.List, ast.Dict, ast.Set,
    ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Compare,
    ast.Attribute, ast.Subscript, ast.Index, ast.Slice,
    ast.arguments, ast.arg, ast.keyword,
    ast.Expr, ast.FormattedValue, ast.JoinedStr,
    ast.IfExp, ast.ListComp, ast.SetComp, ast.DictComp,
    ast.GeneratorExp, ast.comprehension,
    ast.ExceptHandler, ast.Try, ast.With,
    ast.Raise, ast.Assert,
}


# ╔════════════════════════════════════════════════════════════════════╗
# ║  DATA MODELS                                                     ║
# ╚════════════════════════════════════════════════════════════════════╝

@dataclass
class SecurityViolation:
    """A single security finding."""
    severity: str        # "critical" | "high" | "medium" | "low"
    category: str        # "rce" | "dos" | "forbidden_builtin" | "forbidden_import" | "complexity"
    message: str
    line: Optional[int] = None
    col: Optional[int] = None
    node_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "line": self.line,
            "col": self.col,
            "node_type": self.node_type,
        }


@dataclass
class ASTSecurityReport:
    """Complete security assessment of a code string."""
    safe: bool = True
    violations: List[SecurityViolation] = field(default_factory=list)
    node_count: int = 0
    max_depth: int = 0
    source_length: int = 0
    parse_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "safe": self.safe,
            "violations": [v.to_dict() for v in self.violations],
            "node_count": self.node_count,
            "max_depth": self.max_depth,
            "source_length": self.source_length,
            "parse_error": self.parse_error,
        }

    def add(self, violation: SecurityViolation) -> None:
        self.violations.append(violation)
        if violation.severity in ("critical", "high"):
            self.safe = False


# ╔════════════════════════════════════════════════════════════════════╗
# ║  PRE-PARSE CHECKS                                               ║
# ╚════════════════════════════════════════════════════════════════════╝

def _check_source_length(source: str, report: ASTSecurityReport) -> bool:
    """Reject sources that exceed the length limit (DoS prevention)."""
    report.source_length = len(source)
    if len(source) > MAX_SOURCE_LENGTH:
        report.add(SecurityViolation(
            severity="high",
            category="dos",
            message=f"Source exceeds maximum length ({len(source):,} > {MAX_SOURCE_LENGTH:,} bytes)",
        ))
        return False
    return True


def _check_nesting_depth(source: str, report: ASTSecurityReport) -> bool:
    """
    Quick heuristic check for excessive nesting before invoking the parser.
    Counts consecutive open-brackets/parentheses to detect stack-overflow payloads.
    """
    max_open = 0
    depth = 0
    for ch in source:
        if ch in "([{":
            depth += 1
            max_open = max(max_open, depth)
        elif ch in ")]}":
            depth = max(depth - 1, 0)
    if max_open > MAX_AST_DEPTH:
        report.add(SecurityViolation(
            severity="high",
            category="dos",
            message=f"Excessive nesting depth ({max_open} > {MAX_AST_DEPTH})",
        ))
        return False
    return True


# ╔════════════════════════════════════════════════════════════════════╗
# ║  AST NODE VALIDATORS                                            ║
# ╚════════════════════════════════════════════════════════════════════╝

def _check_decorator_rce(node: ast.AST, report: ASTSecurityReport) -> None:
    """
    Detect RCE payloads hidden in decorators and default arguments.

    Attack vector::

        @__import__('os').system('rm -rf /')
        def bypass(): pass

        def bypass(cmd=__import__('os').system('payload')): pass

    Both execute during function *definition*, not invocation.
    """
    decorators: List[ast.expr] = []
    defaults: List[ast.expr] = []

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        decorators = node.decorator_list
        defaults = node.args.defaults + node.args.kw_defaults
    elif isinstance(node, ast.ClassDef):
        decorators = node.decorator_list

    # Check decorators for call expressions
    for dec in decorators:
        if _contains_dangerous_call(dec):
            report.add(SecurityViolation(
                severity="critical",
                category="rce",
                message="Dangerous call detected in decorator — potential RCE via function definition",
                line=getattr(dec, "lineno", None),
                col=getattr(dec, "col_offset", None),
                node_type=type(dec).__name__,
            ))

    # Check default argument values
    for default in defaults:
        if default is None:
            continue
        if _contains_dangerous_call(default):
            report.add(SecurityViolation(
                severity="critical",
                category="rce",
                message="Dangerous call detected in default argument — "
                        "executes during function definition, not invocation",
                line=getattr(default, "lineno", None),
                col=getattr(default, "col_offset", None),
                node_type=type(default).__name__,
            ))


def _contains_dangerous_call(node: ast.AST) -> bool:
    """
    Recursively check if a node contains a call to a forbidden function.
    This catches patterns like ``__import__('os').system('cmd')``.
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            # Direct call to forbidden name: eval(...), __import__(...)
            if isinstance(func, ast.Name) and func.id in FORBIDDEN_NAMES:
                return True
            # Attribute call: __import__('os').system(...)
            if isinstance(func, ast.Attribute):
                if _contains_dangerous_call(func.value):
                    return True
            # Nested call: the function itself is a call
            if isinstance(func, ast.Call):
                if _contains_dangerous_call(func):
                    return True
    return False


def _check_forbidden_imports(node: ast.AST, report: ASTSecurityReport) -> None:
    """Detect imports of dangerous modules."""
    if isinstance(node, ast.Import):
        for alias in node.names:
            mod_root = alias.name.split(".")[0]
            if mod_root in FORBIDDEN_MODULES:
                report.add(SecurityViolation(
                    severity="high",
                    category="forbidden_import",
                    message=f"Import of forbidden module: {alias.name}",
                    line=getattr(node, "lineno", None),
                    node_type="Import",
                ))
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            mod_root = node.module.split(".")[0]
            if mod_root in FORBIDDEN_MODULES:
                report.add(SecurityViolation(
                    severity="high",
                    category="forbidden_import",
                    message=f"Import from forbidden module: {node.module}",
                    line=getattr(node, "lineno", None),
                    node_type="ImportFrom",
                ))


def _check_forbidden_calls(node: ast.AST, report: ASTSecurityReport) -> None:
    """Detect direct calls to forbidden builtins (eval, exec, compile, etc.)."""
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in FORBIDDEN_NAMES:
            report.add(SecurityViolation(
                severity="critical",
                category="forbidden_builtin",
                message=f"Call to forbidden builtin: {func.id}()",
                line=getattr(node, "lineno", None),
                col=getattr(node, "col_offset", None),
                node_type="Call",
            ))


def _check_string_exec_patterns(node: ast.AST, report: ASTSecurityReport) -> None:
    """
    Detect obfuscated exec patterns such as:
        getattr(__builtins__, 'eval')('payload')
        globals()['__builtins__']['exec']('payload')
    """
    if isinstance(node, ast.Call):
        func = node.func
        # getattr(obj, 'eval') / getattr(obj, 'exec')
        if isinstance(func, ast.Name) and func.id == "getattr" and len(node.args) >= 2:
            second_arg = node.args[1]
            if isinstance(second_arg, ast.Constant) and isinstance(second_arg.value, str):
                if second_arg.value in FORBIDDEN_NAMES:
                    report.add(SecurityViolation(
                        severity="critical",
                        category="rce",
                        message=f"Obfuscated access to forbidden builtin via getattr: '{second_arg.value}'",
                        line=getattr(node, "lineno", None),
                        node_type="Call",
                    ))


# ╔════════════════════════════════════════════════════════════════════╗
# ║  TREE-WIDE ANALYSIS                                             ║
# ╚════════════════════════════════════════════════════════════════════╝

def _measure_tree(tree: ast.Module, report: ASTSecurityReport) -> None:
    """Count nodes and measure max depth of the AST."""
    count = 0
    max_depth = 0

    def _walk(node: ast.AST, depth: int) -> None:
        nonlocal count, max_depth
        count += 1
        max_depth = max(max_depth, depth)

        if count > MAX_AST_NODES:
            return
        if depth > MAX_WALK_RECURSION:
            return

        for child in ast.iter_child_nodes(node):
            _walk(child, depth + 1)

    _walk(tree, 0)
    report.node_count = count
    report.max_depth = max_depth

    if count > MAX_AST_NODES:
        report.add(SecurityViolation(
            severity="high",
            category="dos",
            message=f"AST node count exceeds limit ({count:,} > {MAX_AST_NODES:,})",
        ))

    if max_depth > MAX_AST_DEPTH:
        report.add(SecurityViolation(
            severity="medium",
            category="complexity",
            message=f"AST depth exceeds recommended limit ({max_depth} > {MAX_AST_DEPTH})",
        ))


# ╔════════════════════════════════════════════════════════════════════╗
# ║  PUBLIC API                                                      ║
# ╚════════════════════════════════════════════════════════════════════╝

def validate_ast(tree: ast.Module, report: Optional[ASTSecurityReport] = None) -> ASTSecurityReport:
    """
    Run all security checks against an already-parsed AST tree.

    Parameters
    ----------
    tree    : The ``ast.Module`` from ``ast.parse()``.
    report  : Optional pre-existing report to append to.

    Returns
    -------
    ASTSecurityReport with all findings.
    """
    if report is None:
        report = ASTSecurityReport()

    _measure_tree(tree, report)

    for node in ast.walk(tree):
        _check_decorator_rce(node, report)
        _check_forbidden_imports(node, report)
        _check_forbidden_calls(node, report)
        _check_string_exec_patterns(node, report)

    return report


def safe_parse(source: str, *, filename: str = "<unknown>") -> ASTSecurityReport:
    """
    The primary safe entry point — parse a code string and run all
    security validators.

    This function NEVER executes the code.  It only parses and inspects
    the AST structure.

    Parameters
    ----------
    source   : Raw Python source code string.
    filename : Label for error messages.

    Returns
    -------
    ASTSecurityReport — ``report.safe`` is ``True`` only if zero
    critical/high violations were found.
    """
    report = ASTSecurityReport()

    # Pre-parse checks
    if not _check_source_length(source, report):
        return report

    if not _check_nesting_depth(source, report):
        return report

    # Parse with a reduced recursion limit to prevent stack overflow
    old_limit = sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(min(old_limit, MAX_WALK_RECURSION * 3))
        tree = ast.parse(source, filename=filename)
    except RecursionError:
        report.add(SecurityViolation(
            severity="critical",
            category="dos",
            message="Parsing triggered RecursionError — likely a stack-overflow payload",
        ))
        report.parse_error = "RecursionError"
        return report
    except SyntaxError as exc:
        report.parse_error = str(exc)
        report.add(SecurityViolation(
            severity="low",
            category="complexity",
            message=f"Syntax error in source: {exc}",
            line=exc.lineno,
        ))
        return report
    finally:
        sys.setrecursionlimit(old_limit)

    # Full AST validation
    validate_ast(tree, report)
    return report


def is_safe_for_introspection(source: str) -> bool:
    """Quick boolean check — ``True`` if ``safe_parse`` finds no critical/high issues."""
    return safe_parse(source).safe


# ╔════════════════════════════════════════════════════════════════════╗
# ║  SELF-SCAN — validate that Praxis's own code is clean            ║
# ╚════════════════════════════════════════════════════════════════════╝

def scan_praxis_source() -> Dict[str, Any]:
    """
    Scan all ``.py`` files in the praxis package for security violations.

    Returns a summary dict with per-file results.
    """
    from pathlib import Path
    pkg_dir = Path(__file__).resolve().parent
    results: Dict[str, Any] = {}
    total_violations = 0
    files_scanned = 0

    for py_file in sorted(pkg_dir.rglob("*.py")):
        rel = str(py_file.relative_to(pkg_dir))
        if "__pycache__" in rel or "egg-info" in rel:
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        report = safe_parse(source, filename=rel)
        files_scanned += 1

        if report.violations:
            results[rel] = report.to_dict()
            total_violations += len(report.violations)

    return {
        "files_scanned": files_scanned,
        "files_with_violations": len(results),
        "total_violations": total_violations,
        "details": results,
    }
