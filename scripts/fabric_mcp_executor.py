#!/usr/bin/env python3
"""
Fabric MCP Executor — Executar Integração 100% Autônoma
Coordena todas as operações MCP em sequência
Script que será coordenado pelo Copilot/Agent para executar via MCP tools
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Carregar .env
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file, encoding='utf-8')
    except:
        with open(env_file, 'r', encoding='latin-1') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID", "999fa43f-32d3-4a10-ad5d-b58a5962e43a")
WORKSPACE_NAME = os.getenv("FABRIC_WORKSPACE_NAME", "PowerCenter Migration")

workspace_root = Path(__file__).parent.parent
notebooks_dir = workspace_root / "notebooks"
data_dir = workspace_root / "data"
output_dir = workspace_root / "output"

class FabricMCPExecutor:
    """Executor das operações MCP"""
    
    def __init__(self):
        self.workspace_id = WORKSPACE_ID
        self.workspace_name = WORKSPACE_NAME
        self.execution_log = []
        self.results = {
            "workspace_verified": False,
            "lakehouse_created": False,
            "notebooks_uploaded": 0,
            "files_uploaded": 0,
            "pipelines_created": 0
        }
        self.start_time = datetime.now()
    
    def log_operation(self, phase: str, status: str, message: str, details: Dict = None):
        """Registrar operação"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.execution_log.append(log_entry)
        
        status_symbol = "✓" if status == "SUCCESS" else "✗" if status == "ERROR" else "→"
        print(f"[{status_symbol}] [{phase}] {message}")
    
    def prepare_mcp_operations(self) -> List[Dict[str, Any]]:
        """Preparar lista de operações MCP para execução"""
        
        operations = []
        
        # Op 1: Verificar workspace
        operations.append({
            "id": 1,
            "sequence": 1,
            "tool": "mcp_fabricmcpserv_get_workspace",
            "description": "Verificar workspace",
            "parameters": {
                "WorkspaceId": self.workspace_id
            },
            "expected_output": "workspace_info"
        })
        
        # Op 2: Criar lakehouse
        operations.append({
            "id": 2,
            "sequence": 2,
            "tool": "mcp_fabricmcpserv_create_item",
            "description": "Criar lakehouse powercenter_lakehouse",
            "parameters": {
                "WorkspaceId": self.workspace_id,
                "Details": {
                    "displayName": "powercenter_lakehouse",
                    "type": "Lakehouse",
                    "description": "Lakehouse para migração PowerCenter"
                }
            },
            "expected_output": "item_created"
        })
        
        # Op 3-8: Upload de notebooks
        notebooks = sorted(notebooks_dir.glob("*.ipynb"))
        for idx, nb in enumerate(notebooks, start=3):
            operations.append({
                "id": idx,
                "sequence": idx,
                "tool": "mcp_fabricmcpserv_create_item",
                "description": f"Upload notebook: {nb.stem}",
                "parameters": {
                    "WorkspaceId": self.workspace_id,
                    "Details": {
                        "displayName": nb.stem,
                        "type": "Notebook",
                        "filePath": str(nb)
                    }
                },
                "expected_output": "item_created"
            })
        
        # Op 9: Upload de XMLs
        xml_files = sorted(list(data_dir.glob("*.xml")) + list(data_dir.glob("*.XML")))
        if xml_files:
            operations.append({
                "id": 9,
                "sequence": 9,
                "tool": "mcp_fabricmcpserv_create_item",
                "description": f"Upload {len(xml_files)} arquivos XML",
                "parameters": {
                    "WorkspaceId": self.workspace_id,
                    "Details": {
                        "type": "File",
                        "files": [str(f) for f in xml_files],
                        "destination": "lakehouse"
                    }
                },
                "expected_output": "files_uploaded"
            })
        
        # Op 10-11: Criar pipelines
        pipelines = [
            {
                "name": "Pipeline_EMP_Workflow",
                "notebook": "03_Map_EMP_Source_to_Target",
                "description": "Pipeline para processamento de dados EMP"
            },
            {
                "name": "Pipeline_HR_Workflow",
                "notebook": "05_Map_HR_Source_to_Target",
                "description": "Pipeline para processamento de dados HR"
            }
        ]
        
        for idx, pipeline in enumerate(pipelines, start=10):
            operations.append({
                "id": idx,
                "sequence": idx,
                "tool": "mcp_fabricmcpserv_create_item",
                "description": f"Criar pipeline: {pipeline['name']}",
                "parameters": {
                    "WorkspaceId": self.workspace_id,
                    "Details": {
                        "displayName": pipeline['name'],
                        "type": "Pipeline",
                        "notebook": pipeline['notebook'],
                        "description": pipeline['description']
                    }
                },
                "expected_output": "item_created"
            })
        
        return operations
    
    def generate_execution_instructions(self, operations: List[Dict]) -> str:
        """Gerar instruções para executar as operações"""
        
        instructions = []
        instructions.append("# FABRIC MCP INTEGRATION — EXECUTION INSTRUCTIONS")
        instructions.append(f"# Workspace: {self.workspace_name}")
        instructions.append(f"# Workspace ID: {self.workspace_id}")
        instructions.append(f"# Total Operations: {len(operations)}")
        instructions.append("")
        
        instructions.append("## EXECUTION STEPS:\n")
        
        for op in operations:
            instructions.append(f"### OPERATION {op['id']} — {op['description']}")
            instructions.append(f"Tool: {op['tool']}")
            instructions.append(f"Sequence: {op['sequence']}/{len(operations)}")
            instructions.append("")
            
            instructions.append("Parameters:")
            instructions.append("```json")
            instructions.append(json.dumps(op['parameters'], indent=2))
            instructions.append("```")
            instructions.append("")
        
        return "\n".join(instructions)
    
    def save_execution_plan(self, operations: List[Dict]):
        """Salvar plano de execução"""
        
        output_dir.mkdir(exist_ok=True)
        
        plan = {
            "migration_id": f"fabric_mcp_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "workspace": {
                "id": self.workspace_id,
                "name": self.workspace_name
            },
            "total_operations": len(operations),
            "operations": operations,
            "generated_at": datetime.now().isoformat(),
            "instructions": self.generate_execution_instructions(operations),
            "execution_log": [],
            "status": "READY_FOR_EXECUTION"
        }
        
        # Salvar como JSON
        json_file = output_dir / f"mcp_execution_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Plano de execução salvo: {json_file}")
        
        # Salvar instruções como Markdown
        md_file = output_dir / f"mcp_execution_instructions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(plan['instructions'])
        
        print(f"[OK] Instruções de execução salvo: {md_file}")
        
        return json_file, md_file
    
    def generate_final_report(self):
        """Gerar relatório final"""
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            "report_type": "FABRIC_MCP_INTEGRATION_PLAN",
            "timestamp": {
                "generated": datetime.now().isoformat(),
                "duration_seconds": duration
            },
            "workspace": {
                "id": self.workspace_id,
                "name": self.workspace_name
            },
            "execution_plan": {
                "status": "READY",
                "description": "Plano de integração MCP pronto para execução",
                "next_step": "Executar operações MCP em sequência"
            },
            "assets": {
                "notebooks": len(list(notebooks_dir.glob("*.ipynb"))),
                "xml_files": len(list(data_dir.glob("*.xml")) + list(data_dir.glob("*.XML"))),
                "pipelines": 2
            },
            "execution_log": self.execution_log
        }
        
        output_dir.mkdir(exist_ok=True)
        report_file = output_dir / f"fabric_mcp_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Relatório final salvo: {report_file}")
        
        return report_file
    
    def run_preparation(self):
        """Executar preparação da integração"""
        
        print("\n" + "="*80)
        print("FABRIC MCP INTEGRATION — COMPLETE AUTONOMOUS FLOW".center(80))
        print("="*80 + "\n")
        
        self.log_operation("INIT", "INFO", f"Iniciando preparação da integração MCP", {
            "workspace": self.workspace_name,
            "workspace_id": self.workspace_id
        })
        
        # Preparar operações
        print("\n[→] Preparando operações MCP...")
        operations = self.prepare_mcp_operations()
        self.log_operation("PREP", "SUCCESS", f"{len(operations)} operações MCP preparadas", {
            "total_operations": len(operations)
        })
        
        # Salvar plano de execução
        print("\n[→] Salvando plano de execução...")
        json_file, md_file = self.save_execution_plan(operations)
        
        # Gerar relatório final
        print("\n[→] Gerando relatório final...")
        report_file = self.generate_final_report()
        
        print("\n" + "="*80)
        print("PREPARAÇÃO CONCLUÍDA — PRONTO PARA EXECUÇÃO MCP".center(80))
        print("="*80)
        
        print("\n[✓] Arquivos gerados:")
        print(f"    - Plano JSON: {json_file}")
        print(f"    - Instruções: {md_file}")
        print(f"    - Relatório: {report_file}")
        
        print("\n[→] Próximos passos:")
        print("    1. Revisar plano de execução em:")
        print(f"       {json_file}")
        print("    2. Executar operações MCP em sequência (via Copilot/Agent)")
        print("    3. Monitorar execução via logs")
        
        print("\n" + "="*80 + "\n")
        
        return True

def main():
    """Função principal"""
    try:
        executor = FabricMCPExecutor()
        success = executor.run_preparation()
        return success
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
