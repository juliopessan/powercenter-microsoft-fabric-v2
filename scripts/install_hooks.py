#!/usr/bin/env python3
"""
Instala o pre-commit hook que executa o harness antes de cada commit.
Execute uma vez após clonar: python scripts/install_hooks.py
"""

import sys
import stat
from pathlib import Path

ROOT = Path(__file__).parent.parent
HOOK_PATH = ROOT / ".git" / "hooks" / "pre-commit"

HOOK_CONTENT = f"""#!/bin/sh
# Harness pre-commit hook — PowerCenter to Microsoft Fabric
echo "\\n🔍 Executando harness antes do commit...\\n"
python3 "{ROOT}/harness/runner.py" --ci --no-report
if [ $? -ne 0 ]; then
  echo "\\n❌ Harness encontrou erros. Corrija antes de commitar.\\n"
  exit 1
fi
echo "\\n✅ Harness passou — prosseguindo com o commit.\\n"
"""

def main():
    if not (ROOT / ".git").exists():
        print("❌ Diretório .git não encontrado. Execute dentro do repositório.")
        sys.exit(1)

    HOOK_PATH.parent.mkdir(exist_ok=True)
    HOOK_PATH.write_text(HOOK_CONTENT)
    HOOK_PATH.chmod(HOOK_PATH.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print(f"✅ Pre-commit hook instalado em {HOOK_PATH}")
    print("   O harness será executado automaticamente antes de cada commit.")

if __name__ == "__main__":
    main()
