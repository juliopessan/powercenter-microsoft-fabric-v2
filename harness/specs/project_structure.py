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
    "pipelines/deliverables/fabric-ready",
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
    "scripts/install_hooks.py",
    "pipelines/validation/validate_zips.py",
    "pipelines/validation/validate_final_zips.py",
    "pipelines/deliverables/fabric-ready/pl_m_poc_xml_emp_FABRIC.zip",
    "pipelines/deliverables/fabric-ready/pl_m_poc_xml_hr_FABRIC.zip",
    ".env.example",
    ".gitignore",
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
