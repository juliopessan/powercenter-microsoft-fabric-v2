"""Gera relatórios do harness em JSON e HTML."""

import json
from datetime import datetime
from pathlib import Path
from typing import List
from .specs.base import SpecResult, Severity


def to_dict(results: List[SpecResult]) -> dict:
    total_findings = sum(len(r.findings) for r in results)
    errors   = sum(1 for r in results for f in r.findings if f.severity == Severity.ERROR)
    warnings = sum(1 for r in results for f in r.findings if f.severity == Severity.WARNING)

    return {
        "timestamp": datetime.now().isoformat(),
        "passed":  all(r.passed for r in results),
        "summary": {"specs": len(results), "findings": total_findings, "errors": errors, "warnings": warnings},
        "specs": [
            {
                "name":    r.spec_name,
                "passed":  r.passed,
                "checked": r.checked,
                "findings": [
                    {"severity": f.severity, "file": f.file, "line": f.line, "message": f.message}
                    for f in r.findings
                ],
            }
            for r in results
        ],
    }


def save_json(results: List[SpecResult], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "harness_report.json"
    path.write_text(json.dumps(to_dict(results), indent=2, ensure_ascii=False))
    return path


def save_html(results: List[SpecResult], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    data = to_dict(results)

    overall_color = "#22c55e" if data["passed"] else "#ef4444"
    overall_label = "PASSOU" if data["passed"] else "FALHOU"

    rows = ""
    for spec in data["specs"]:
        status_icon = "✅" if spec["passed"] else "❌"
        for f in spec["findings"]:
            sev_color = {"ERROR": "#ef4444", "WARNING": "#f59e0b", "INFO": "#3b82f6"}.get(f["severity"], "#888")
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            rows += f"""
            <tr>
              <td>{status_icon} {spec['name']}</td>
              <td style="color:{sev_color};font-weight:600">{f['severity']}</td>
              <td style="font-family:monospace;font-size:12px">{loc}</td>
              <td>{f['message']}</td>
            </tr>"""
        if not spec["findings"]:
            rows += f"""
            <tr>
              <td>✅ {spec['name']}</td>
              <td colspan="3" style="color:#22c55e">Sem findings — {spec['checked']} itens verificados</td>
            </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Harness Report — PowerCenter to Fabric</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
    header {{ background: {overall_color}22; border-bottom: 2px solid {overall_color}; padding: 24px 32px; }}
    h1 {{ margin: 0; font-size: 22px; }}
    .badge {{ display:inline-block; background:{overall_color}; color:#fff; padding:4px 14px;
              border-radius:999px; font-weight:700; font-size:14px; margin-left:12px; }}
    .meta {{ font-size:13px; color:#94a3b8; margin-top:8px; }}
    .summary {{ display:flex; gap:24px; padding:16px 32px; background:#1e293b; }}
    .card {{ background:#0f172a; border:1px solid #334155; border-radius:8px; padding:12px 20px; }}
    .card-val {{ font-size:28px; font-weight:700; }}
    .card-lbl {{ font-size:12px; color:#94a3b8; }}
    .err {{ color:#ef4444; }} .warn {{ color:#f59e0b; }} .ok {{ color:#22c55e; }}
    main {{ padding: 24px 32px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th {{ text-align:left; padding:10px 12px; background:#1e293b; color:#94a3b8;
          font-size:11px; text-transform:uppercase; letter-spacing:.05em; }}
    td {{ padding:10px 12px; border-bottom:1px solid #1e293b; vertical-align:top; }}
    tr:hover td {{ background:#1e293b22; }}
  </style>
</head>
<body>
  <header>
    <h1>Harness Report — PowerCenter to Microsoft Fabric
      <span class="badge">{overall_label}</span>
    </h1>
    <div class="meta">{data['timestamp']} &nbsp;·&nbsp; {data['summary']['specs']} specs</div>
  </header>
  <div class="summary">
    <div class="card"><div class="card-val {'err' if data['summary']['errors'] else 'ok'}">{data['summary']['errors']}</div><div class="card-lbl">Erros</div></div>
    <div class="card"><div class="card-val {'warn' if data['summary']['warnings'] else 'ok'}">{data['summary']['warnings']}</div><div class="card-lbl">Avisos</div></div>
    <div class="card"><div class="card-val">{data['summary']['findings']}</div><div class="card-lbl">Total findings</div></div>
  </div>
  <main>
    <table>
      <thead><tr><th>Spec</th><th>Severidade</th><th>Localização</th><th>Mensagem</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </main>
</body>
</html>"""

    path = out_dir / "harness_report.html"
    path.write_text(html, encoding="utf-8")
    return path
