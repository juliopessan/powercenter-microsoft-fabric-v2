"""Base classes para specs e resultados do harness."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List


class Severity(str, Enum):
    ERROR   = "ERROR"
    WARNING = "WARNING"
    INFO    = "INFO"


@dataclass
class Finding:
    severity: Severity
    spec:     str
    file:     str
    message:  str
    line:     int = 0

    def __str__(self):
        loc = f"{self.file}:{self.line}" if self.line else self.file
        icon = {"ERROR": "❌", "WARNING": "⚠️ ", "INFO": "ℹ️ "}[self.severity]
        return f"{icon} [{self.spec}] {loc} — {self.message}"


@dataclass
class SpecResult:
    spec_name:  str
    passed:     bool
    findings:   List[Finding] = field(default_factory=list)
    checked:    int = 0

    def add(self, severity: Severity, file: str, message: str, line: int = 0):
        self.findings.append(Finding(severity, self.spec_name, file, message, line))
        if severity == Severity.ERROR:
            self.passed = False


class Spec:
    """Contrato base. Subclasses implementam `run(root) -> SpecResult`."""
    name = "base"

    def run(self, root: Path) -> SpecResult:
        raise NotImplementedError
