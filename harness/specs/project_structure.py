"""
Spec: ProjectStructure
Garante que todos os diretórios e arquivos obrigatórios do projeto existem.
"""

from pathlib import Path
from .base import Spec, SpecResult, Severity

REQUIRED_DIRS = [
    "data",
    "notebooks",
    "output",
    "pipelines/deliverables",
    "pipelines/schemas",
    "pipelines/validation",
    "scripts",
    "docs",
    "logs",
    "test-reports",
    "harness",
    "harness/specs",
]

REQUIRED_FILES = [
    "scripts/setup_environment.py",
    "pipelines/validation/validate_zips.py",
    "pipelines/validation/validate_final_zips.py",
    "pipelines/deliverables/pl_m_poc_xml_emp.zip",
    "pipelines/deliverables/pl_m_poc_xml_hr.zip",
    "pipelines/deliverables/pl_m_poc_xml_emp_FABRIC_DF.zip",
    "pipelines/deliverables/pl_m_poc_xml_hr_FABRIC_DF.zip",
    ".env",
]


class ProjectStructureSpec(Spec):
    name = "ProjectStructure"

    def run(self, root: Path) -> SpecResult:
        result = SpecResult(spec_name=self.name, passed=True)

        for d in REQUIRED_DIRS:
            result.checked += 1
            if not (root / d).is_dir():
                result.add(Severity.ERROR, d, f"Diretório obrigatório ausente: {d}/")

        for f in REQUIRED_FILES:
            result.checked += 1
            if not (root / f).is_file():
                result.add(Severity.WARNING, f, f"Arquivo obrigatório ausente: {f}")

        return result
