"""
PowerCenter to Fabric Migration - VS Code MCP Tool Version
Uses VS Code's built-in MCP tools instead of REST API calls
Requires: Fabric MCP extension configured in VS Code
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def run_vscode_mcp_tool(tool_name: str, params: dict = None) -> dict:
    """
    Simula chamada aos MCP tools do VS Code.
    Na prática, você executaria esses comandos manualmente ou via extensão do Copilot.
    """
    print(f"🔧 MCP Tool: {tool_name}")
    if params:
        print(f"   Params: {json.dumps(params, indent=2)}")
    
    # Retorna placeholder - na prática seria executado pelo VS Code
    return {
        "status": "manual_execution_required",
        "tool": tool_name,
        "params": params,
        "instruction": f"Execute via Copilot: @workspace use MCP tool {tool_name}"
    }


class FabricMCPMigration:
    """Orquestrador de migração usando MCP tools do VS Code"""
    
    def __init__(self, workspace_name: str, capacity_id: str = None):
        self.workspace_name = workspace_name
        self.capacity_id = capacity_id
        self.project_root = Path(__file__).parent.parent
        self.report = {
            "migration_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "workspace_name": workspace_name,
            "start_time": datetime.now().isoformat(),
            "phases": {}
        }
        
        print(f"\n{'='*70}")
        print(f"🚀 PowerCenter → Fabric Migration (MCP Tool Version)")
        print(f"{'='*70}")
        print(f"📦 Workspace: {workspace_name}")
        print(f"📁 Project Root: {self.project_root}")
        print(f"{'='*70}\n")
    
    def phase1_setup_workspace(self):
        """Fase 1: Setup Workspace + Lakehouse"""
        print("\n" + "="*70)
        print("📋 FASE 1: Setup Workspace + Lakehouse")
        print("="*70)
        
        phase_data = {"status": "pending", "steps": []}
        
        # Step 1: Verificar se workspace existe
        print("\n🔍 Step 1.1: Verificando workspaces existentes...")
        print("   Execute no Copilot:")
        print("   > Use o MCP tool: mcp_fabricmcpserv_list_workspaces")
        
        step1 = {
            "action": "list_workspaces",
            "tool": "mcp_fabricmcpserv_list_workspaces",
            "instruction": "Verifique se workspace já existe",
            "status": "manual"
        }
        phase_data["steps"].append(step1)
        
        # Step 2: Criar workspace (se não existir)
        print("\n📦 Step 1.2: Criar workspace (se não existir)...")
        print("   Execute no Copilot:")
        print(f"   > Use o MCP tool: mcp_fabricmcpserv_create_workspace")
        print(f"   > displayName: {self.workspace_name}")
        if self.capacity_id:
            print(f"   > capacityId: {self.capacity_id}")
        
        step2 = {
            "action": "create_workspace",
            "tool": "mcp_fabricmcpserv_create_workspace",
            "params": {
                "displayName": self.workspace_name,
                "capacityId": self.capacity_id
            },
            "instruction": "Criar workspace se não existir",
            "status": "manual"
        }
        phase_data["steps"].append(step2)
        
        # Step 3: Criar Lakehouse
        print("\n🏠 Step 1.3: Criar Lakehouse...")
        print("   Execute no Copilot:")
        print(f"   > Use o MCP tool: mcp_fabricmcpserv_create_item")
        print(f"   > type: Lakehouse")
        print(f"   > displayName: powercenter_lakehouse")
        
        step3 = {
            "action": "create_lakehouse",
            "tool": "mcp_fabricmcpserv_create_item",
            "params": {
                "type": "Lakehouse",
                "displayName": "powercenter_lakehouse",
                "description": "PowerCenter migration lakehouse"
            },
            "instruction": "Criar lakehouse no workspace",
            "status": "manual"
        }
        phase_data["steps"].append(step3)
        
        phase_data["status"] = "completed_manual"
        self.report["phases"]["phase1"] = phase_data
        
        print("\n✅ Fase 1: Instruções geradas")
        print("   Execute os comandos MCP acima no Copilot Chat")
        
    def phase2_upload_data(self):
        """Fase 2: Upload XML Files"""
        print("\n" + "="*70)
        print("📋 FASE 2: Upload Data Files")
        print("="*70)
        
        phase_data = {"status": "pending", "files": []}
        
        data_files = [
            "employees.xml",
            "hr.xml",
            "wf_m_poc_xml_emp.XML",
            "wf_m_poc_xml_hr.XML"
        ]
        
        for filename in data_files:
            file_path = self.project_root / "data" / filename
            
            if not file_path.exists():
                print(f"⚠️  Arquivo não encontrado: {file_path}")
                continue
                
            print(f"\n📤 Upload: {filename}")
            print(f"   Execute no Copilot:")
            print(f"   > Use o MCP tool: mcp_fabricmcpserv_update_item_definition")
            print(f"   > Local path: {file_path}")
            print(f"   > Target: lakehouse/Files/{filename}")
            
            file_data = {
                "filename": filename,
                "local_path": str(file_path),
                "remote_path": f"Files/{filename}",
                "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
                "tool": "mcp_fabricmcpserv_update_item_definition",
                "status": "manual"
            }
            phase_data["files"].append(file_data)
        
        phase_data["status"] = "completed_manual"
        self.report["phases"]["phase2"] = phase_data
        
        print(f"\n✅ Fase 2: {len(phase_data['files'])} arquivos prontos para upload")
        
    def phase3_upload_notebooks(self):
        """Fase 3: Upload Notebooks"""
        print("\n" + "="*70)
        print("📋 FASE 3: Upload Notebooks")
        print("="*70)
        
        phase_data = {"status": "pending", "notebooks": []}
        
        notebooks = [
            "01_PowerCenter_to_PySpark_Translation.ipynb",
            "02_Workflow_Execution_EMP_and_HR.ipynb",
            "03_Map_EMP_Source_to_Target.ipynb",
            "04_PySpark_Large_Scale_Data_Generation.ipynb",
            "05_Map_HR_Source_to_Target.ipynb",
            "06_Pipeline_Import_Guide.ipynb"
        ]
        
        for notebook_name in notebooks:
            notebook_path = self.project_root / "notebooks" / notebook_name
            
            if not notebook_path.exists():
                print(f"⚠️  Notebook não encontrado: {notebook_path}")
                continue
            
            print(f"\n📓 Upload: {notebook_name}")
            print(f"   Execute no Copilot:")
            print(f"   > Use o MCP tool: mcp_fabricmcpserv_create_item")
            print(f"   > type: Notebook")
            print(f"   > displayName: {notebook_name.replace('.ipynb', '')}")
            print(f"   > Depois use: mcp_fabricmcpserv_update_item_definition")
            print(f"   > Conteúdo: {notebook_path}")
            
            notebook_data = {
                "name": notebook_name,
                "local_path": str(notebook_path),
                "display_name": notebook_name.replace('.ipynb', ''),
                "size_bytes": notebook_path.stat().st_size if notebook_path.exists() else 0,
                "tools": [
                    "mcp_fabricmcpserv_create_item",
                    "mcp_fabricmcpserv_update_item_definition"
                ],
                "status": "manual"
            }
            phase_data["notebooks"].append(notebook_data)
        
        phase_data["status"] = "completed_manual"
        self.report["phases"]["phase3"] = phase_data
        
        print(f"\n✅ Fase 3: {len(phase_data['notebooks'])} notebooks prontos para upload")
        
    def phase4_create_pipelines(self):
        """Fase 4: Create Data Pipelines"""
        print("\n" + "="*70)
        print("📋 FASE 4: Create Pipelines")
        print("="*70)
        
        phase_data = {"status": "pending", "pipelines": []}
        
        pipelines = [
            {
                "name": "Pipeline_EMP_Workflow",
                "source": "pipelines/deliverables/pipeline_emp_workflow.json",
                "notebooks": ["03_Map_EMP_Source_to_Target"]
            },
            {
                "name": "Pipeline_HR_Workflow",
                "source": "pipelines/deliverables/pipeline_hr_workflow.json",
                "notebooks": ["05_Map_HR_Source_to_Target"]
            }
        ]
        
        for pipeline in pipelines:
            pipeline_path = self.project_root / pipeline["source"]
            
            print(f"\n🔄 Pipeline: {pipeline['name']}")
            print(f"   Execute no Copilot:")
            print(f"   > Use o MCP tool: mcp_fabricmcpserv_create_item")
            print(f"   > type: DataPipeline")
            print(f"   > displayName: {pipeline['name']}")
            print(f"   > Notebooks: {', '.join(pipeline['notebooks'])}")
            
            if pipeline_path.exists():
                print(f"   > Definição: {pipeline_path}")
            
            pipeline_data = {
                "name": pipeline["name"],
                "local_config": str(pipeline_path) if pipeline_path.exists() else None,
                "notebooks": pipeline["notebooks"],
                "tool": "mcp_fabricmcpserv_create_item",
                "status": "manual"
            }
            phase_data["pipelines"].append(pipeline_data)
        
        phase_data["status"] = "completed_manual"
        self.report["phases"]["phase4"] = phase_data
        
        print(f"\n✅ Fase 4: {len(phase_data['pipelines'])} pipelines prontos")
        
    def phase5_execute_workflows(self):
        """Fase 5: Execute Pipelines"""
        print("\n" + "="*70)
        print("📋 FASE 5: Execute Workflows")
        print("="*70)
        
        print("\n🎯 Execute manualmente no Fabric UI:")
        print("   1. Abra o workspace no portal: https://app.fabric.microsoft.com")
        print("   2. Navegue até o workspace: " + self.workspace_name)
        print("   3. Execute: Pipeline_EMP_Workflow")
        print("   4. Execute: Pipeline_HR_Workflow")
        print("\n   Ou use a extensão Fabric do VS Code para executar os notebooks")
        
        phase_data = {
            "status": "manual_execution_required",
            "instruction": "Execute pipelines via Fabric UI ou extensão VS Code"
        }
        self.report["phases"]["phase5"] = phase_data
        
        print("\n✅ Fase 5: Instruções de execução geradas")
        
    def phase6_validate_outputs(self):
        """Fase 6: Validate Outputs"""
        print("\n" + "="*70)
        print("📋 FASE 6: Validate Outputs")
        print("="*70)
        
        print("\n🔍 Validação manual:")
        print("   1. Verifique tabelas Delta no lakehouse:")
        print("      - emp_poc")
        print("      - hr_poc")
        print("   2. Baixe CSVs resultantes para output/")
        print("   3. Compare com outputs esperados")
        
        phase_data = {
            "status": "manual_validation_required",
            "expected_tables": ["emp_poc", "hr_poc"],
            "instruction": "Validar via Fabric UI e baixar CSVs"
        }
        self.report["phases"]["phase6"] = phase_data
        
        print("\n✅ Fase 6: Instruções de validação geradas")
        
    def phase7_generate_report(self):
        """Fase 7: Generate Final Report"""
        print("\n" + "="*70)
        print("📋 FASE 7: Generate Report")
        print("="*70)
        
        self.report["end_time"] = datetime.now().isoformat()
        self.report["status"] = "completed_with_manual_steps"
        
        # Save report
        output_dir = self.project_root / "output"
        output_dir.mkdir(exist_ok=True)
        
        report_file = output_dir / f"migration_report_mcp_{self.report['migration_id']}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Relatório gerado: {report_file}")
        print("\n" + "="*70)
        print("🎉 MIGRAÇÃO CONCLUÍDA (Manual Steps Required)")
        print("="*70)
        print(f"\n📦 Workspace: {self.workspace_name}")
        print(f"📄 Relatório: {report_file}")
        print(f"\n📚 Próximos Passos:")
        print("   1. Execute os comandos MCP listados em cada fase")
        print("   2. Valide as tabelas Delta no lakehouse")
        print("   3. Execute os pipelines no portal Fabric")
        print("   4. Baixe e valide os CSVs resultantes")
        print("\n" + "="*70 + "\n")
        
    def run_migration(self):
        """Executa todas as fases da migração"""
        try:
            self.phase1_setup_workspace()
            input("\n⏸️  Pressione ENTER após executar comandos da Fase 1...")
            
            self.phase2_upload_data()
            input("\n⏸️  Pressione ENTER após executar comandos da Fase 2...")
            
            self.phase3_upload_notebooks()
            input("\n⏸️  Pressione ENTER após executar comandos da Fase 3...")
            
            self.phase4_create_pipelines()
            input("\n⏸️  Pressione ENTER após criar pipelines...")
            
            self.phase5_execute_workflows()
            input("\n⏸️  Pressione ENTER após executar workflows...")
            
            self.phase6_validate_outputs()
            input("\n⏸️  Pressione ENTER após validar outputs...")
            
            self.phase7_generate_report()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Migração interrompida pelo usuário")
            self.report["status"] = "interrupted"
            self.report["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"\n\n❌ Erro na migração: {e}")
            self.report["status"] = "failed"
            self.report["error"] = str(e)
            self.report["end_time"] = datetime.now().isoformat()


def main():
    """Ponto de entrada principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PowerCenter to Fabric Migration (MCP Tool Version)"
    )
    parser.add_argument(
        "--workspace-name",
        required=True,
        help="Nome do workspace Fabric"
    )
    parser.add_argument(
        "--capacity-id",
        default=None,
        help="ID da capacidade Fabric (opcional)"
    )
    
    args = parser.parse_args()
    
    migration = FabricMCPMigration(
        workspace_name=args.workspace_name,
        capacity_id=args.capacity_id
    )
    
    migration.run_migration()


if __name__ == "__main__":
    main()
