"""
Spec: PySparkAPI
Detecta padrões de uso incorreto da API PySpark.
Erro original: .agg({"SALARY": ["min", "max", "avg"]}) — sintaxe inválida.
"""

import ast
import re
from pathlib import Path
from .base import Spec, SpecResult, Severity

_SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", "harness"}

# Padrões textuais rápidos que indicam uso errado antes de parsear o AST
_REGEX_CHECKS = [
    (
        re.compile(r'\.agg\s*\(\s*\{[^}]+:\s*\['),
        "agg() com lista de funções no dict não é suportado pelo PySpark. "
        "Use agg(min('col'), max('col'), avg('col')) com funções explícitas.",
    ),
    (
        re.compile(r'\.agg\s*\(\s*\{\s*["\'][^"\']+["\']\s*:\s*["\']'),
        "agg() com dict de string aceita apenas UMA função por coluna. "
        "Para múltiplas, use agg(func1('col'), func2('col')).",
    ),
    (
        re.compile(r'from pyspark.*import.*\bmin\b(?!.*\bas\b)'),
        "Importar 'min' direto de pyspark.sql.functions pode conflitar com "
        "o builtin Python. Use 'from pyspark.sql.functions import min as spark_min'.",
    ),
    (
        re.compile(r'from pyspark.*import.*\bmax\b(?!.*\bas\b)'),
        "Importar 'max' direto pode conflitar com o builtin Python. "
        "Use 'max as spark_max'.",
    ),
    (
        re.compile(r'\.collect\(\)\[0\]\[\d+\]'),
        "Acesso a Row por índice numérico pode quebrar se o schema mudar. "
        "Prefira row['nome_coluna'] ou row.nome_coluna.",
    ),
    (
        re.compile(r'spark\.sql\(["\']SELECT \*'),
        "SELECT * em spark.sql() traz colunas imprevisíveis. Liste as colunas explicitamente.",
    ),
]


class PySparkAPISpec(Spec):
    name = "PySparkAPI"

    def run(self, root: Path) -> SpecResult:
        result = SpecResult(spec_name=self.name, passed=True)

        for py_file in root.rglob("*.py"):
            if any(part in _SKIP_DIRS for part in py_file.parts):
                continue

            rel = str(py_file.relative_to(root))
            source = py_file.read_text(encoding="utf-8", errors="ignore")

            # Só analisa arquivos que usam PySpark
            if "pyspark" not in source and "SparkSession" not in source:
                continue

            result.checked += 1
            lines = source.splitlines()

            for lineno, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                for pattern, message in _REGEX_CHECKS:
                    if pattern.search(line):
                        result.add(Severity.ERROR, rel, message, lineno)

        return result
