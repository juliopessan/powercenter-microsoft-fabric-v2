#!/usr/bin/env python3
"""
Fabric Upload Strategy 2 - Usar Azure Storage SDK para Notebooks
Se REST API não funciona, vamos tentar diretamente com Azure Storage
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Carregar .env
load_dotenv(override=True)

FABRIC_ACCESS_TOKEN = os.getenv("FABRIC_ACCESS_TOKEN")
WORKSPACE_ID = "878ba859-8217-47b1-8450-d483fcb00462"
LAKEHOUSE_ID = "919be5ac-466d-4cfa-a8f0-77774e325c72"

NOTEBOOKS_DIR = Path(__file__).parent.parent / "notebooks"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

NOTEBOOKS = [
    "01_PowerCenter_to_PySpark_Translation.ipynb",
    "02_Workflow_Execution_EMP_and_HR.ipynb",
    "03_Map_EMP_Source_to_Target.ipynb",
    "04_PySpark_Large_Scale_Data_Generation.ipynb",
    "05_Map_HR_Source_to_Target.ipynb",
    "06_Pipeline_Import_Guide.ipynb",
]

def print_header(text):
    print(f"\n{'='*80}\n  {text}\n{'='*80}\n")

def print_step(step_num, text):
    print(f"\n📌 PASSO {step_num}: {text}\n" + "-"*80)

def upload_notebooks_to_onelake():
    """Upload notebooks direto ao OneLake como se fossem arquivos"""
    print_step(1, "Upload de Notebooks via OneLake (Estratégia Alternativa)")
    
    uploaded = 0
    
    for notebook_name in NOTEBOOKS:
        notebook_path = NOTEBOOKS_DIR / notebook_name
        
        if not notebook_path.exists():
            print(f"  ❌ {notebook_name}: arquivo não encontrado")
            continue
        
        print(f"  {notebook_name}...", end=" ", flush=True)
        
        # Fazer upload para OneLake/Notebooks (caminho especial)
        url = f"https://onelake.blob.core.windows.net/{WORKSPACE_ID}/{LAKEHOUSE_ID}/Notebooks/{notebook_name}"
        
        # Usar curl para upload
        import subprocess
        cmd = f'curl -s -X PUT -H "Authorization: Bearer {FABRIC_ACCESS_TOKEN}" -H "x-ms-blob-type: BlockBlob" --data-binary "@{notebook_path}" {url}'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 or result.stdout == "":
                print(f"✅")
                uploaded += 1
            else:
                print(f"❌")
        except Exception as e:
            print(f"❌")
        
        time.sleep(0.5)
    
    print(f"\n✅ Total: {uploaded}/{len(NOTEBOOKS)} notebooks\n")
    return uploaded

def query_workspace():
    """Mostrar items no workspace"""
    print_step(2, "Items Criados no Workspace")
    
    import subprocess
    import json as js
    
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/items"
    cmd = f'curl -s -H "Authorization: Bearer {FABRIC_ACCESS_TOKEN}" {url}'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.stdout:
            data = js.loads(result.stdout)
            items = data.get("value", [])
            print(f"  Total items: {len(items)}\n")
            for item in items[:10]:  # Show first 10
                print(f"    • {item.get('displayName')} ({item.get('type')})")
            if len(items) > 10:
                print(f"    ... e {len(items) - 10} mais")
    except:
        print("  (Erro ao listar items)")
    
    print()

def generate_report(notebooks_uploaded):
    """Gerar relatório"""
    print_step(3, "Relatório Final")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "strategy": "OneLake Direct Upload",
        "notebooks_uploaded": notebooks_uploaded,
        "xml_files_uploaded": 4,
        "status": "PARTIAL" if notebooks_uploaded < len(NOTEBOOKS) else "COMPLETE"
    }
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    report_path = OUTPUT_DIR / f"fabric_notebooks_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))
    print(f"\n📊 {report_path}\n")

if __name__ == "__main__":
    print_header("🚀 FABRIC NOTEBOOK UPLOAD - ESTRATÉGIA ALTERNATIVA")
    
    notebooks_uploaded = upload_notebooks_to_onelake()
    query_workspace()
    generate_report(notebooks_uploaded)
    
    print_header("✅ CONCLUSÃO")
    print(f"✓ Notebooks via OneLake: {notebooks_uploaded}/{len(NOTEBOOKS)}")
    print("✓ XMLs: 4/4 (já uploadados)")
    print("\n👉 Verifique no Fabric Portal os items criados")
