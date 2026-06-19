"""
Spec: CsvColumns
Valida que os CSVs de saída possuem as colunas esperadas pelo contrato.
Impede que mudanças de schema no PySpark quebrem silenciosamente o pipeline downstream.
"""

import csv
from pathlib import Path
from .base import Spec, SpecResult, Severity

# Contrato de colunas por arquivo (caminho relativo ao root)
CSV_CONTRACTS: dict[str, list[str]] = {
    "output/emp_poc.csv": [
        "XPK_employee", "FK_employees", "EMPLOYEE_ID",
        "FIRST_NAME", "LAST_NAME", "SALARY", "DEPARTMENT_ID",
    ],
    "output/hr.csv": [
        "XPK_Department", "DEPT_ID", "DEPT_NAME",
        "XPK_Employee", "FK_Department", "EMP_ID",
        "FIRST_NAME", "LAST_NAME", "SALARY", "MANAGER_ID",
    ],
    "output/hr_poc_10k/hr_poc_10k_data.csv": [
        "XPK_Department", "DEPT_ID", "DEPT_NAME", "LOCATION",
        "XPK_Employee", "FK_Department", "EMP_ID",
        "FIRST_NAME", "LAST_NAME", "SALARY", "MANAGER_ID",
    ],
}


class CsvColumnsSpec(Spec):
    name = "CsvColumns"

    def run(self, root: Path) -> SpecResult:
        result = SpecResult(spec_name=self.name, passed=True)

        for rel_path, expected_cols in CSV_CONTRACTS.items():
            csv_path = root / rel_path
            result.checked += 1

            if not csv_path.exists():
                result.add(Severity.WARNING, rel_path,
                    "Arquivo CSV não encontrado — execute o notebook de geração de dados")
                continue

            try:
                # utf-8-sig remove BOM (﻿) gerado por ferramentas Windows/Excel
                with csv_path.open(encoding="utf-8-sig", errors="ignore", newline="") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)

                if header is None:
                    result.add(Severity.ERROR, rel_path, "CSV vazio — sem cabeçalho")
                    continue

                actual = [c.strip() for c in header]
                missing = [c for c in expected_cols if c not in actual]
                extra   = [c for c in actual if c not in expected_cols]

                if missing:
                    result.add(Severity.ERROR, rel_path,
                        f"Colunas ausentes: {missing}")
                if extra:
                    result.add(Severity.WARNING, rel_path,
                        f"Colunas extras não mapeadas no contrato: {extra}")
                if not missing and not extra:
                    pass  # perfeito

            except Exception as e:
                result.add(Severity.ERROR, rel_path, f"Erro ao ler CSV: {e}")

        return result
