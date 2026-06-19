#!/usr/bin/env python3
"""
Agente de Setup — PowerCenter to Microsoft Fabric
Verifica e prepara automaticamente o ambiente local.
"""

import sys
import os
import subprocess
import shutil
import platform
import json
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"

def ok(msg):   print(f"  {GREEN}✅ {msg}{RESET}")
def warn(msg): print(f"  {YELLOW}⚠️  {msg}{RESET}")
def err(msg):  print(f"  {RED}❌ {msg}{RESET}")
def info(msg): print(f"  {CYAN}ℹ️  {msg}{RESET}")
def header(msg):
    print(f"\n{BOLD}{'─'*60}")
    print(f"  {msg}")
    print(f"{'─'*60}{RESET}")

def run(cmd, capture=True):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture, text=True, timeout=30
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "timeout"
    except Exception as e:
        return 1, "", str(e)

def pip_install(package, import_name=None):
    name = import_name or package
    try:
        __import__(name)
        return True
    except ImportError:
        pass
    info(f"Instalando {package}...")
    code, _, stderr = run(f"{sys.executable} -m pip install {package} -q")
    if code == 0:
        ok(f"{package} instalado")
        return True
    err(f"Falha ao instalar {package}: {stderr}")
    return False

# ─────────────────────────────────────────────────────────────────────────────
# Verificações
# ─────────────────────────────────────────────────────────────────────────────

results = {}

def check_python():
    header("1. Python")
    version = sys.version_info
    ver_str = f"{version.major}.{version.minor}.{version.micro}"
    if version >= (3, 11):
        ok(f"Python {ver_str} — compatível ✓")
        results["python"] = True
    elif version >= (3, 8):
        warn(f"Python {ver_str} — funcional, mas recomendado 3.11+")
        results["python"] = True
    else:
        err(f"Python {ver_str} — versão muito antiga. Instale 3.11+: https://python.org/downloads")
        results["python"] = False

def check_pip():
    header("2. pip")
    code, out, _ = run(f"{sys.executable} -m pip --version")
    if code == 0:
        ok(f"{out}")
        results["pip"] = True
    else:
        err("pip não encontrado. Execute: python -m ensurepip --upgrade")
        results["pip"] = False

def check_git():
    header("3. Git")
    path = shutil.which("git")
    if not path:
        err("Git não encontrado.")
        info("Instale em: https://git-scm.com/downloads")
        results["git"] = False
        return
    code, out, _ = run("git --version")
    ok(f"{out}  (em {path})")
    results["git"] = True

def check_powershell():
    header("4. PowerShell")
    system = platform.system()

    if system == "Windows":
        code, out, _ = run("powershell -Command $PSVersionTable.PSVersion.Major")
        if code == 0:
            major = int(out.strip()) if out.strip().isdigit() else 0
            if major >= 5:
                ok(f"PowerShell {major} encontrado")
                results["powershell"] = True
                return
        err("PowerShell 5.1+ não encontrado")
        info("Já vem incluído no Windows 10/11. Verifique as configurações.")
        results["powershell"] = False
    else:
        # macOS / Linux — verifica pwsh (PowerShell Core)
        path = shutil.which("pwsh")
        if path:
            code, out, _ = run("pwsh --version")
            ok(f"{out}  (em {path})")
            results["powershell"] = True
        else:
            warn("PowerShell Core (pwsh) não instalado")
            if system == "Darwin":
                info("Para instalar: brew install --cask powershell")
            else:
                info("Para instalar: https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-linux")
            info("Os scripts .ps1 são opcionais — os notebooks Python cobrem o mesmo workflow")
            results["powershell"] = "optional"

def check_python_packages():
    header("5. Pacotes Python necessários")

    packages = [
        ("requests",   "requests"),
        ("pandas",     "pandas"),
        ("openpyxl",   "openpyxl"),
        ("azure-identity", "azure.identity"),
    ]

    all_ok = True
    for pkg, imp in packages:
        installed = pip_install(pkg, imp)
        if not installed:
            all_ok = False

    results["packages"] = all_ok

def check_project_structure():
    header("6. Estrutura do projeto")
    root = Path(__file__).parent.parent
    required_dirs = ["notebooks", "pipelines", "scripts", "data", "output", "docs", "logs", "test-reports"]
    required_dirs_deliverables = ["pipelines/deliverables", "pipelines/validation", "pipelines/schemas"]

    all_ok = True
    for d in required_dirs + required_dirs_deliverables:
        p = root / d
        if p.exists():
            ok(f"{d}/")
        else:
            warn(f"{d}/ não existe — criando...")
            p.mkdir(parents=True, exist_ok=True)
            ok(f"{d}/ criado")

    results["structure"] = all_ok

def check_output_dirs():
    header("7. Diretórios de saída")
    root = Path(__file__).parent.parent
    output_dirs = [
        "output/hr_poc_10k",
        "output/emp_poc",
        "logs",
        "test-reports",
    ]
    for d in output_dirs:
        p = root / d
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            ok(f"{d}/ criado")
        else:
            ok(f"{d}/ OK")
    results["output_dirs"] = True

def check_env_file():
    header("8. Arquivo .env (opcional)")
    root = Path(__file__).parent.parent
    env_path = root / ".env"
    env_example_path = root / ".env.example"

    if env_path.exists():
        ok(".env encontrado")
    else:
        warn(".env não encontrado")
        if env_example_path.exists():
            import shutil as sh
            sh.copy(env_example_path, env_path)
            ok(".env criado a partir de .env.example — preencha as variáveis")
        else:
            # Cria template mínimo
            env_content = """# Microsoft Fabric — configurações de ambiente
# Preencha com seus dados antes de executar os scripts

FABRIC_TENANT_ID=
FABRIC_CLIENT_ID=
FABRIC_CLIENT_SECRET=
FABRIC_WORKSPACE_ID=
FABRIC_LAKEHOUSE_ID=
"""
            env_path.write_text(env_content)
            ok(".env criado com template — preencha as variáveis")
    results["env"] = True

def print_fabric_checklist():
    header("9. Microsoft Fabric — checklist manual")
    print(f"""
  Os itens abaixo precisam ser verificados manualmente no portal Fabric:

  {YELLOW}[ ]{RESET} Conta Microsoft Fabric ativa
       → https://app.fabric.microsoft.com

  {YELLOW}[ ]{RESET} Workspace Fabric com permissões de Admin
       → No Fabric: Workspaces → selecione o seu → Settings → Access

  {YELLOW}[ ]{RESET} Lakehouse configurado no workspace
       → No workspace: + New → Lakehouse

  {YELLOW}[ ]{RESET} Variáveis preenchidas no .env (TENANT_ID, WORKSPACE_ID, etc.)
       → Consulte: Azure Portal → Entra ID → App Registrations
""")
    results["fabric"] = "manual"

# ─────────────────────────────────────────────────────────────────────────────
# Relatório final
# ─────────────────────────────────────────────────────────────────────────────

def print_summary():
    header("RESUMO DO SETUP")

    status_map = {
        True:       f"{GREEN}✅ OK{RESET}",
        False:      f"{RED}❌ AÇÃO NECESSÁRIA{RESET}",
        "optional": f"{YELLOW}⚠️  Opcional{RESET}",
        "manual":   f"{YELLOW}⚠️  Verificação manual{RESET}",
    }

    labels = {
        "python":      "Python 3.11+",
        "pip":         "pip",
        "git":         "Git",
        "powershell":  "PowerShell",
        "packages":    "Pacotes Python",
        "structure":   "Estrutura do projeto",
        "output_dirs": "Diretórios de saída",
        "env":         ".env",
        "fabric":      "Microsoft Fabric",
    }

    for key, label in labels.items():
        status = results.get(key, False)
        print(f"  {label:<30} {status_map[status]}")

    errors = [k for k, v in results.items() if v is False]
    if not errors:
        print(f"\n{GREEN}{BOLD}  ✨ Ambiente pronto! Execute os notebooks no Fabric.{RESET}")
    else:
        print(f"\n{RED}  Corrija os itens marcados com ❌ antes de continuar.{RESET}")

    # Salva relatório JSON
    report_path = Path(__file__).parent.parent / "logs" / "setup_report.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(
        {"platform": platform.system(), "python": sys.version, "checks": {k: str(v) for k, v in results.items()}},
        indent=2
    ))
    info(f"Relatório salvo em logs/setup_report.json")

# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{BOLD}{'═'*60}")
    print(f"  SETUP — PowerCenter to Microsoft Fabric")
    print(f"  Sistema: {platform.system()} {platform.release()}")
    print(f"{'═'*60}{RESET}")

    check_python()
    check_pip()
    check_git()
    check_powershell()
    check_python_packages()
    check_project_structure()
    check_output_dirs()
    check_env_file()
    print_fabric_checklist()
    print_summary()
