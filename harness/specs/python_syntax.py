"""
Spec: PythonSyntax
Todo arquivo .py deve ser parseável sem erros de sintaxe.
"""

import ast
import py_compile
import tempfile
from pathlib import Path
from .base import Spec, SpecResult, Severity

_SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}


class PythonSyntaxSpec(Spec):
    name = "PythonSyntax"

    def run(self, root: Path) -> SpecResult:
        result = SpecResult(spec_name=self.name, passed=True)

        for py_file in root.rglob("*.py"):
            if any(part in _SKIP_DIRS for part in py_file.parts):
                continue

            rel = str(py_file.relative_to(root))
            result.checked += 1
            source = py_file.read_text(encoding="utf-8", errors="ignore")

            try:
                ast.parse(source, filename=str(py_file))
            except SyntaxError as e:
                result.add(Severity.ERROR, rel,
                    f"Erro de sintaxe na linha {e.lineno}: {e.msg}", e.lineno)

        return result
