"""
Spec: PathSafety
Garante que nenhum script Python contém caminhos absolutos hardcoded.
Erro original: validate_final_zips.py com C:\\Users\\julio.cesar.d.pessan\\...
"""

import re
from pathlib import Path
from .base import Spec, SpecResult, Severity

# Padrões que indicam caminho absoluto hardcoded.
# \\\\n e \\\\t são escapes Python comuns — excluídos explicitamente.
_PATTERNS = [
    # Drive letter + colon + backslash + pelo menos 2 chars alfanuméricos (exclui \n, \t, \r)
    (re.compile(r'[A-Za-z]:\\\\(?!n|t|r)[A-Za-z_][^"\']{2,}'),
     "Caminho Windows hardcoded (ex: C:\\\\Users\\\\...)"),
    (re.compile(r'r"[A-Za-z]:\\[A-Za-z_]'),
     "Raw string com caminho Windows"),
    (re.compile(r"r'[A-Za-z]:\\[A-Za-z_]"),
     "Raw string com caminho Windows"),
    (re.compile(r"/home/[a-zA-Z0-9_]{2,}/"),
     "Caminho Linux /home/<user>/ hardcoded"),
    (re.compile(r'(?<!["\'])(?<!\w)/Users/[a-zA-Z0-9_]{2,}/'),
     "Caminho macOS /Users/<user>/ hardcoded"),
]

# Diretórios ignorados nas buscas
_SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", "harness"}


class PathSafetySpec(Spec):
    name = "PathSafety"

    def run(self, root: Path) -> SpecResult:
        result = SpecResult(spec_name=self.name, passed=True)

        for py_file in root.rglob("*.py"):
            if any(part in _SKIP_DIRS for part in py_file.parts):
                continue

            rel = py_file.relative_to(root)
            lines = py_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            result.checked += 1

            for lineno, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                for pattern, description in _PATTERNS:
                    if pattern.search(line):
                        result.add(
                            Severity.ERROR,
                            str(rel),
                            f"{description}: `{stripped[:80]}`",
                            lineno,
                        )
                        break  # um erro por linha é suficiente

        return result
