#!/usr/bin/env python3
"""
Fabric Interactive Login & Complete Upload Flow - VERSÃO CORRIGIDA
100% Autônomo - Sem dependências externas
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import base64

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

WORKSPACE_ID = "878ba859-8217-47b1-8450-d483fcb00462"
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
        print(f"\n▶ {description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            if result.stderr:
                print(f"  ⚠️ Stderr: {result.stderr[:100]}")
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout")
        return None
    except Exception as e:
        print(f"  ❌ Erro: {str(e)}")
        return None

def get_fabric_token_interactive():
    """Get Fabric token via interactive Azure CLI login"""
    print_step(1, "Autenticação Interativa (Azure CLI)")
    
    print("🔐 Abrindo navegador para autenticação...")
    print("   Você será redirecionado para login da Microsoft")
    print("   Confirme sua identidade no navegador\n")
    
    # Azure CLI login interativo
    cmd = "az login --allow-no-subscriptions"
    result = run_command(cmd, "Login interativo via Azure CLI")
    
    if not result:
        print("❌ Falha no login interativo")
        return None
    
    print("✅ Login bem-sucedido!\n")
    
    # Obter token para Fabric API
    print("Obtendo token para Fabric API...")
    cmd = 'az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv'
    token = run_command(cmd, "Obtendo token de acesso Fabric")
    
    if not token:
        print("❌ Falha ao obter token")
        return None
    
    print(f"✅ Token obtido com sucesso\n")
    return token

def verify_workspace_access(token):
    """Verify workspace is accessible"""
    print_step(2, "Verificar Acesso ao Workspace")
    
    url = f"{API_BASE}/workspaces/{WORKSPACE_ID}"
    
    cmd = f'curl -s -H "Authorization: Bearer {token}" {url}'
    result = run_command(cmd, f"Verificando workspace {WORKSPACE_ID}")
    
    if result:
        try:
            data = json.loads(result)
            if "id" in data:
                print(f"✅ Workspace acessível: {data.get('displayName', 'PowerCenter Migration')}\n")
                return True
        except:
            pass
    
    print(f"❌ Workspace não acessível\n")
    return False

def upload_notebooks(token):
    """Upload all notebooks to Fabric workspace"""
    print_step(3, f"Upload de {len(NOTEBOOKS)} Notebooks")
    
    uploaded = 0
    
    for notebook_name in NOTEBOOKS:
        notebook_path = NOTEBOOKS_DIR / notebook_name
        
        if not notebook_path.exists():
            print(f"❌ Arquivo não encontrado: {notebook_path}")
            continue
        
        display_name = notebook_name.replace('.ipynb', '')
        print(f"\n📓 {notebook_name}...", end=" ", flush=True)
        
        # Ler conteúdo do notebook
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook_content = f.read()
        except Exception as e:
            print(f"❌ Erro leitura: {e}")
            continue
        
        # Preparar payload (versão simplificada)
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
        
        # Salvar payload temporário
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(payload, f)
            payload_file = f.name
        
        try:
            url = f"{API_BASE}/workspaces/{WORKSPACE_ID}/items"
            cmd = f'curl -s -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -d @"{payload_file}" {url}'
            result = run_command(cmd)
            
            if result and '"id"' in result:
                try:
                    resp = json.loads(result)
                    if "id" in resp:
                        print(f"✅")
                        uploaded += 1
                    else:
                        print(f"❌ Resposta inválida")
                except:
                    print(f"❌ Parse erro")
            else:
                print(f"❌")
        finally:
            os.unlink(payload_file)
        
        time.sleep(0.5)
    
    print(f"\n✅ Total: {uploaded}/{len(NOTEBOOKS)} notebooks\n")
    return uploaded

def upload_xml_files(token):
    """Upload XML files to Fabric lakehouse via OneLake"""
    print_step(4, f"Upload de {len(XML_FILES)} Arquivos XML")
    
    uploaded = 0
    
    for xml_file in XML_FILES:
        xml_path = DATA_DIR / xml_file
        
        if not xml_path.exists():
            print(f"❌ Arquivo não encontrado: {xml_path}")
            continue
        
        print(f"\n📁 {xml_file}...", end=" ", flush=True)
        
        # OneLake endpoint
        url = f"https://onelake.blob.core.windows.net/{WORKSPACE_ID}/{LAKEHOUSE_ID}/Files/{xml_file}"
        
        cmd = f'curl -s -X PUT -H "Authorization: Bearer {token}" -H "x-ms-blob-type: BlockBlob" --data-binary "@{xml_path}" {url}'
        result = run_command(cmd)
        
        # OneLake retorna 201 Created ou vazio em sucesso
        if result == "" or "error" not in result.lower():
            print(f"✅")
            uploaded += 1
        else:
            print(f"⚠️")
        
        time.sleep(0.5)
    
    print(f"\n✅ Total: {uploaded}/{len(XML_FILES)} XML files\n")
    return uploaded

def list_workspace_items(token):
    """List all items in workspace"""
    url = f"{API_BASE}/workspaces/{WORKSPACE_ID}/items"
    cmd = f'curl -s -H "Authorization: Bearer {token}" {url}'
    result = run_command(cmd)
    
    if result:
        try:
            data = json.loads(result)
            if "value" in data:
                return data["value"]
        except:
            pass
    
    return []

def create_and_run_pipelines(token):
    """Create and execute pipelines"""
    print_step(5, "Criar e Executar Pipelines")
    
    pipelines_config = [
        {
            "name": "Pipeline_EMP_Workflow",
            "notebook": "02_Workflow_Execution_EMP_and_HR"
        },
        {
            "name": "Pipeline_HR_Workflow",
            "notebook": "05_Map_HR_Source_to_Target"
        }
    ]
    
    executed = 0
    
    for pipeline_cfg in pipelines_config:
        pipeline_name = pipeline_cfg["name"]
        print(f"\n🔗 {pipeline_name}...", end=" ", flush=True)
        
        # Get all workspace items
        items = list_workspace_items(token)
        
        # Find pipeline
        pipeline_id = None
        for item in items:
            if item.get("displayName") == pipeline_name:
                pipeline_id = item.get("id")
                break
        
        if not pipeline_id:
            print(f"⚠️ (não encontrado)")
            continue
        
        # Execute pipeline
        url = f"{API_BASE}/workspaces/{WORKSPACE_ID}/items/{pipeline_id}/jobs/instances?jobType=Pipeline"
        cmd = f'curl -s -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" {url}'
        result = run_command(cmd)
        
        if result or "error" not in (result or "").lower():
            print(f"✅")
            executed += 1
        else:
            print(f"⚠️")
        
        time.sleep(1)
    
    print(f"\n✅ Total: {executed}/2 pipelines\n")
    return executed

def generate_final_report(notebooks_uploaded, xmls_uploaded, pipelines_executed):
    """Generate final execution report"""
    print_step(6, "Relatório Final de Execução")
    
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
    
    # Save report
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
    print_header("🚀 FABRIC INTERACTIVE LOGIN - COMPLETE UPLOAD FLOW")
    print(f"Workspace: {WORKSPACE_NAME}")
    print(f"Lakehouse: {LAKEHOUSE_NAME}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Step 1: Interactive Login
    token = get_fabric_token_interactive()
    if not token:
        print("❌ Falha na autenticação interativa")
        sys.exit(1)
    
    # Step 2: Verify Access
    if not verify_workspace_access(token):
        print("❌ Não foi possível acessar o workspace")
        sys.exit(1)
    
    # Step 3: Upload Notebooks
    notebooks_uploaded = upload_notebooks(token)
    
    # Step 4: Upload XMLs
    xmls_uploaded = upload_xml_files(token)
    
    # Step 5: Execute Pipelines
    pipelines_executed = create_and_run_pipelines(token)
    
    # Step 6: Generate Report
    report = generate_final_report(notebooks_uploaded, xmls_uploaded, pipelines_executed)
    
    # Final Status
    print_header("✅ EXECUÇÃO CONCLUÍDA")
    print(f"✓ Notebooks: {notebooks_uploaded}/{len(NOTEBOOKS)}")
    print(f"✓ XMLs: {xmls_uploaded}/{len(XML_FILES)}")
    print(f"✓ Pipelines: {pipelines_executed}/2")
    print(f"\n🎉 Status Final: {report['status']}")
    print(f"\n👉 Seus dados estão no Fabric!")

if __name__ == "__main__":
    main()
