"""
Harness Runner — PowerCenter to Microsoft Fabric
Executa todos os specs e reporta os resultados.

Uso:
  python -m harness.runner             # verifica tudo
  python -m harness.runner --ci        # saída compacta, exit 1 se houver ERRORs
  python -m harness.runner --fix       # corrige problemas simples automaticamente
"""

import sys
import argparse
from pathlib import Path

# Adiciona o root ao path para imports relativos funcionarem como módulo ou script
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from harness.specs.base import Severity, SpecResult
from harness.specs.path_safety      import PathSafetySpec
from harness.specs.zip_structure    import ZipStructureSpec
from harness.specs.python_syntax    import PythonSyntaxSpec
from harness.specs.pyspark_api      import PySparkAPISpec
from harness.specs.env_vars         import EnvVarsSpec
from harness.specs.csv_columns      import CsvColumnsSpec
from harness.specs.project_structure import ProjectStructureSpec
from harness import report

RESET  = "\033[0m";  BOLD = "\033[1m"
GREEN  = "\033[92m"; RED  = "\033[91m"
YELLOW = "\033[93m"; CYAN = "\033[96m"
DIM    = "\033[2m"

ALL_SPECS = [
    ProjectStructureSpec(),
    PythonSyntaxSpec(),
    PathSafetySpec(),
    PySparkAPISpec(),
    ZipStructureSpec(),
    EnvVarsSpec(),
    CsvColumnsSpec(),
]


def _severity_color(s: Severity) -> str:
    return {Severity.ERROR: RED, Severity.WARNING: YELLOW, Severity.INFO: CYAN}.get(s, "")


def print_result(r: SpecResult, ci: bool):
    icon  = f"{GREEN}✅{RESET}" if r.passed else f"{RED}❌{RESET}"
    label = f"{icon} {BOLD}{r.spec_name}{RESET}"

    if not r.findings:
        print(f"  {label}  {DIM}({r.checked} verificados){RESET}")
        return

    errors   = sum(1 for f in r.findings if f.severity == Severity.ERROR)
    warnings = sum(1 for f in r.findings if f.severity == Severity.WARNING)
    summary  = []
    if errors:   summary.append(f"{RED}{errors} erro(s){RESET}")
    if warnings: summary.append(f"{YELLOW}{warnings} aviso(s){RESET}")

    print(f"  {label}  {', '.join(summary)}")

    if not ci:
        for f in r.findings:
            col  = _severity_color(f.severity)
            loc  = f"{DIM}{f.file}:{f.line}{RESET}" if f.line else f"{DIM}{f.file}{RESET}"
            print(f"      {col}{f.severity.value:<8}{RESET} {loc}")
            print(f"             {f.message}")


def _auto_fix(root: Path):
    """Correções automáticas simples."""
    fixed = 0

    # Cria diretórios ausentes
    required_dirs = [
        "data", "notebooks", "output", "pipelines/deliverables",
        "pipelines/schemas", "pipelines/validation", "scripts",
        "docs", "logs", "test-reports", "harness", "harness/specs",
        "output/hr_poc_10k", "output/emp_poc",
    ]
    for d in required_dirs:
        p = root / d
        if not p.exists():
            p.mkdir(parents=True)
            print(f"  {GREEN}✅ Criado:{RESET} {d}/")
            fixed += 1

    # Cria .env se não existir
    env_path = root / ".env"
    if not env_path.exists():
        env_path.write_text(
            "FABRIC_TENANT_ID=\nFABRIC_CLIENT_ID=\nFABRIC_CLIENT_SECRET=\n"
            "FABRIC_WORKSPACE_ID=\nFABRIC_LAKEHOUSE_ID=\n"
        )
        print(f"  {GREEN}✅ Criado:{RESET} .env (preencha as variáveis)")
        fixed += 1

    print(f"\n  {CYAN}ℹ️  {fixed} correção(ões) automática(s) aplicada(s){RESET}")
    print(f"  {YELLOW}⚠️  Caminhos hardcoded e erros de sintaxe precisam de correção manual.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Harness — PowerCenter to Microsoft Fabric")
    parser.add_argument("--ci",  action="store_true", help="Modo CI: saída compacta, exit 1 em erros")
    parser.add_argument("--fix", action="store_true", help="Aplica correções automáticas simples")
    parser.add_argument("--no-report", action="store_true", help="Não gera relatório HTML/JSON")
    args = parser.parse_args()

    root = ROOT

    print(f"\n{BOLD}{'═'*62}")
    print(f"  HARNESS — PowerCenter to Microsoft Fabric")
    print(f"  Raiz: {root}")
    print(f"{'═'*62}{RESET}\n")

    if args.fix:
        print(f"{BOLD}  🔧 Modo --fix: aplicando correções automáticas...{RESET}")
        _auto_fix(root)
        print()

    results = []
    for spec in ALL_SPECS:
        r = spec.run(root)
        results.append(r)
        print_result(r, ci=args.ci)

    # Totais
    total_errors   = sum(1 for r in results for f in r.findings if f.severity == Severity.ERROR)
    total_warnings = sum(1 for r in results for f in r.findings if f.severity == Severity.WARNING)
    passed_all     = all(r.passed for r in results)

    print(f"\n{BOLD}{'─'*62}{RESET}")
    if passed_all:
        print(f"  {GREEN}{BOLD}✨ Todos os specs passaram!{RESET}")
    else:
        print(f"  {RED}{BOLD}❌ {total_errors} erro(s){RESET}  {YELLOW}{total_warnings} aviso(s){RESET}")
        if not args.ci:
            print(f"  {CYAN}ℹ️  Execute com --fix para correções automáticas{RESET}")

    if not args.no_report:
        out_dir = root / "test-reports"
        json_path = report.save_json(results, out_dir)
        html_path = report.save_html(results, out_dir)
        print(f"\n  {DIM}Relatórios: {json_path.relative_to(root)}{RESET}")
        print(f"  {DIM}            {html_path.relative_to(root)}{RESET}")

    print()
    sys.exit(0 if passed_all else 1)


if __name__ == "__main__":
    main()
