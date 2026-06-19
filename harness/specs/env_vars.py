"""
Spec: EnvVars
O arquivo .env deve existir e conter todas as chaves necessárias (mesmo que vazias
é só um aviso — bloquear somente se a chave não existir).
"""

from pathlib import Path
from .base import Spec, SpecResult, Severity

REQUIRED_KEYS = [
    "FABRIC_TENANT_ID",
    "FABRIC_CLIENT_ID",
    "FABRIC_CLIENT_SECRET",
    "FABRIC_WORKSPACE_ID",
    "FABRIC_LAKEHOUSE_ID",
]


def _parse_env(text: str) -> dict:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            result[key.strip()] = val.strip()
    return result


class EnvVarsSpec(Spec):
    name = "EnvVars"

    def run(self, root: Path) -> SpecResult:
        result = SpecResult(spec_name=self.name, passed=True)
        env_path = root / ".env"
        result.checked = 1

        if not env_path.exists():
            result.add(Severity.ERROR, ".env",
                ".env não encontrado. Execute: python scripts/setup_environment.py")
            return result

        env = _parse_env(env_path.read_text(encoding="utf-8", errors="ignore"))

        for key in REQUIRED_KEYS:
            if key not in env:
                result.add(Severity.ERROR, ".env", f"Chave '{key}' ausente no .env")
            elif not env[key]:
                result.add(Severity.WARNING, ".env",
                    f"Chave '{key}' existe mas está vazia — preencha antes de executar")

        return result
