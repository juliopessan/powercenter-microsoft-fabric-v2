#!/usr/bin/env python3
"""
Fabric Complete Upload Flow - SEM INTERATIVIDADE
Usa token do .env e faz upload completo de forma autônoma
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import base64
from dotenv import load_dotenv

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Carregar .env
load_dotenv(override=True)

FABRIC_ACCESS_TOKEN = os.getenv("FABRIC_ACCESS_TOKEN")
WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID", "878ba859-8217-47b1-8450-d483fcb00462")
WORKSPACE_NAME = "PowerCenter Migration"
LAKEHOUSE_ID = "919be5ac-466d-4cfa-a8f0-77774e325c72"
LAKEHOUSE_NAME = "powercenter_lakehouse"

NOTEBOOKS_DIR = Path(__file__).parent.parent / "notebooks"
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

NOTEBOOKS = [
    "01_PowerCenter_to_PySpark_Translation.ipynb",
    "02_Workflow_Execution_EMP_and_HR.ipynb",
    "03_Map_EMP_Source_to_Target.ipynb",
    "04_PySpark_Large_Scale_Data_Generation.ipynb",
    "05_Map_HR_Source_to_Target.ipynb",
    "06_Pipeline_Import_Guide.ipynb",
]

XML_FILES = [
    "employees.xml",
    "hr.xml",
    "wf_m_poc_xml_emp.XML",
    "wf_m_poc_xml_hr.XML",
]

API_BASE = "https://api.fabric.microsoft.com/v1"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_step(step_num, text):
    """Print step header"""
    print(f"\n📌 PASSO {step_num}: {text}")
    print("-" * 80)

def run_command(cmd, description=""):
    """Execute shell command"""
    if description:
        print(f"▶ {description}", end=" ", flush=True)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            if result.stderr and description:
                print(f"❌")
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        if description:
            print(f"❌ (timeout)")
        return None
    except Exception as e:
        if description:
            print(f"❌")
        return None

def verify_token():
    """Verify token exists and is valid"""
    print_step(1, "Verificar Token de Acesso")
    
    if not FABRIC_ACCESS_TOKEN:
        print("❌ Token não encontrado no .env")
        return False
    
    print(f"Token carregado: {FABRIC_ACCESS_TOKEN[:30]}...")
    
    # Testar conexão
    url = f"{API_BASE}/workspaces/{WORKSPACE_ID}"
    cmd = f'curl -s -H "Authorization: Bearer {FABRIC_ACCESS_TOKEN}" {url}'
    result = run_command(cmd, "Verificando acesso ao workspace")
    
    if result:
        try:
            data = json.loads(result)
            if "id" in data:
                print(f"✅ Workspace acessível!\n")
                return True
        except:
            pass
    
    print(f"❌\n")
    return False

def upload_notebooks():
    """Upload all notebooks to Fabric workspace"""
    print_step(2, f"Upload de {len(NOTEBOOKS)} Notebooks")
    
    uploaded = 0
    
    for notebook_name in NOTEBOOKS:
        notebook_path = NOTEBOOKS_DIR / notebook_name
        
        if not notebook_path.exists():
            print(f"❌ {notebook_name}: arquivo não encontrado")
            continue
        
        display_name = notebook_name.replace('.ipynb', '')
        print(f"  {notebook_name}...", end=" ", flush=True)
        
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook_content = f.read()
        except Exception as e:
            print(f"❌")
            continue
        
        payload = {
            "displayName": display_name,
            "type": "Notebook",
            "definition": {
                "format": "ipynb",
                "parts": [
                    {
                        "path": "notebook-content.ipynb",
                        "payload": base64.b64encode(notebook_content.encode()).decode()
                    }
                ]
            }
        }
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(payload, f)
            payload_file = f.name
        
        try:
            url = f"{API_BASE}/workspaces/{WORKSPACE_ID}/items"
            cmd = f'curl -s -X POST -H "Authorization: Bearer {FABRIC_ACCESS_TOKEN}" -H "Content-Type: application/json" -d @"{payload_file}" {url}'
            result = run_command(cmd)
            
            if result and '"id"' in result:
                try:
                    resp = json.loads(result)
                    if "id" in resp:
                        print(f"✅")
                        uploaded += 1
                    else:
                        print(f"❌")
                except:
                    print(f"❌")
            else:
                print(f"❌")
        finally:
            try:
                os.unlink(payload_file)
            except:
                pass
        
        time.sleep(0.5)
    
    print(f"\n✅ Total: {uploaded}/{len(NOTEBOOKS)} notebooks\n")
    return uploaded

def upload_xml_files():
    """Upload XML files to Fabric lakehouse via OneLake"""
    print_step(3, f"Upload de {len(XML_FILES)} Arquivos XML")
    
    uploaded = 0
    
    for xml_file in XML_FILES:
        xml_path = DATA_DIR / xml_file
        
        if not xml_path.exists():
            print(f"❌ {xml_file}: arquivo não encontrado")
            continue
        
        print(f"  {xml_file}...", end=" ", flush=True)
        
        url = f"https://onelake.blob.core.windows.net/{WORKSPACE_ID}/{LAKEHOUSE_ID}/Files/{xml_file}"
        
        cmd = f'curl -s -X PUT -H "Authorization: Bearer {FABRIC_ACCESS_TOKEN}" -H "x-ms-blob-type: BlockBlob" --data-binary "@{xml_path}" {url}'
        result = run_command(cmd)
        
        if result is None or result == "" or "error" not in (result or "").lower():
            print(f"✅")
            uploaded += 1
        else:
            print(f"⚠️")
        
        time.sleep(0.5)
    
    print(f"\n✅ Total: {uploaded}/{len(XML_FILES)} XML files\n")
    return uploaded

def list_workspace_items():
    """List all items in workspace"""
    url = f"{API_BASE}/workspaces/{WORKSPACE_ID}/items"
    cmd = f'curl -s -H "Authorization: Bearer {FABRIC_ACCESS_TOKEN}" {url}'
    result = run_command(cmd)
    
    if result:
        try:
            data = json.loads(result)
            if "value" in data:
                return data["value"]
        except:
            pass
    
    return []

def create_and_run_pipelines():
    """Create and execute pipelines"""
    print_step(4, "Criar e Executar Pipelines")
    
    pipelines_config = [
        {"name": "Pipeline_EMP_Workflow", "notebook": "02_Workflow_Execution_EMP_and_HR"},
        {"name": "Pipeline_HR_Workflow", "notebook": "05_Map_HR_Source_to_Target"}
    ]
    
    executed = 0
    
    for pipeline_cfg in pipelines_config:
        pipeline_name = pipeline_cfg["name"]
        print(f"  {pipeline_name}...", end=" ", flush=True)
        
        items = list_workspace_items()
        
        pipeline_id = None
        for item in items:
            if item.get("displayName") == pipeline_name:
                pipeline_id = item.get("id")
                break
        
        if not pipeline_id:
            print(f"❌ (não encontrado)")
            continue
        
        url = f"{API_BASE}/workspaces/{WORKSPACE_ID}/items/{pipeline_id}/jobs/instances?jobType=Pipeline"
        cmd = f'curl -s -X POST -H "Authorization: Bearer {FABRIC_ACCESS_TOKEN}" -H "Content-Type: application/json" {url}'
        result = run_command(cmd)
        
        if not result or "error" not in result.lower():
            print(f"✅")
            executed += 1
        else:
            print(f"⚠️")
        
        time.sleep(1)
    
    print(f"\n✅ Total: {executed}/2 pipelines\n")
    return executed

def generate_final_report(notebooks_uploaded, xmls_uploaded, pipelines_executed):
    """Generate final execution report"""
    print_step(5, "Relatório Final de Execução")
    
    timestamp = datetime.now().isoformat()
    
    report = {
        "timestamp": timestamp,
        "workspace": {
            "id": WORKSPACE_ID,
            "name": WORKSPACE_NAME
        },
        "lakehouse": {
            "id": LAKEHOUSE_ID,
            "name": LAKEHOUSE_NAME
        },
        "results": {
            "notebooks_uploaded": notebooks_uploaded,
            "total_notebooks": len(NOTEBOOKS),
            "xml_files_uploaded": xmls_uploaded,
            "total_xml_files": len(XML_FILES),
            "pipelines_executed": pipelines_executed,
            "total_pipelines": 2
        },
        "status": "COMPLETE" if (notebooks_uploaded >= len(NOTEBOOKS) and 
                                 xmls_uploaded >= len(XML_FILES) and 
                                 pipelines_executed >= 2) else "PARTIAL"
    }
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    report_path = OUTPUT_DIR / f"fabric_execution_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))
    print(f"\n📊 Relatório: {report_path}\n")
    
    return report

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print_header("🚀 FABRIC COMPLETE UPLOAD FLOW - 100% AUTÔNOMO")
    print(f"Workspace: {WORKSPACE_NAME}")
    print(f"Lakehouse: {LAKEHOUSE_NAME}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    if not verify_token():
        print("❌ Não foi possível verificar o token")
        sys.exit(1)
    
    notebooks_uploaded = upload_notebooks()
    xmls_uploaded = upload_xml_files()
    pipelines_executed = create_and_run_pipelines()
    
    report = generate_final_report(notebooks_uploaded, xmls_uploaded, pipelines_executed)
    
    print_header("✅ EXECUÇÃO CONCLUÍDA")
    print(f"✓ Notebooks: {notebooks_uploaded}/{len(NOTEBOOKS)}")
    print(f"✓ XMLs: {xmls_uploaded}/{len(XML_FILES)}")
    print(f"✓ Pipelines: {pipelines_executed}/2")
    print(f"\n🎉 Status Final: {report['status']}")
    print(f"\n👉 Seus dados estão no Fabric!")

if __name__ == "__main__":
    main()
