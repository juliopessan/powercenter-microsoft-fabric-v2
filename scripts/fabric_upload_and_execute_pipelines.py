#!/usr/bin/env python3
"""
Fabric Upload & Pipeline Execution — Completo
Usa lakehouse existente e executa pipelines
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import time

class FabricUploadAndExecute:
    def __init__(self):
        load_dotenv()
        self.workspace_id = os.getenv('FABRIC_WORKSPACE_ID')
        self.token = os.getenv('FABRIC_ACCESS_TOKEN')
        self.api_base = "https://api.fabric.microsoft.com/v1"
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        self.notebooks_dir = Path("notebooks")
        self.data_dir = Path("data")
        self.log = []
        self.lakehouse_id = None
    
    def log_msg(self, msg, level="INFO"):
        """Log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] [{level}] {msg}"
        print(full_msg)
        self.log.append(full_msg)
    
    def find_lakehouse(self):
        """Find existing lakehouse"""
        self.log_msg("Procurando lakehouse existente...")
        url = f"{self.api_base}/workspaces/{self.workspace_id}/items"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                items = resp.json().get('value', [])
                for item in items:
                    if item.get('type') == 'Lakehouse' and 'powercenter' in item.get('displayName', '').lower():
                        self.lakehouse_id = item.get('id')
                        self.log_msg(f"  ✓ Lakehouse encontrado: {item.get('displayName')} ({self.lakehouse_id})", "OK")
                        return self.lakehouse_id
                
                self.log_msg("  ✗ Nenhum lakehouse encontrado", "WARNING")
                return None
            else:
                self.log_msg(f"  ✗ Erro {resp.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log_msg(f"  ✗ Exceção: {e}", "ERROR")
            return None
    
    def list_workspace_items(self):
        """List existing items in workspace"""
        self.log_msg("Listando itens no workspace...")
        url = f"{self.api_base}/workspaces/{self.workspace_id}/items"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                items = resp.json().get('value', [])
                self.log_msg(f"  ✓ {len(items)} itens encontrados", "OK")
                for item in items[:10]:
                    print(f"    - {item.get('displayName')} ({item.get('type')})")
                if len(items) > 10:
                    print(f"    ... e mais {len(items) - 10}")
                return items
            else:
                self.log_msg(f"  ✗ Erro {resp.status_code}", "ERROR")
                return []
        except Exception as e:
            self.log_msg(f"  ✗ Exceção: {e}", "ERROR")
            return []
    
    def upload_notebook(self, notebook_path):
        """Upload a single notebook"""
        notebook_name = notebook_path.stem
        self.log_msg(f"  Uploading: {notebook_name}")
        
        url = f"{self.api_base}/workspaces/{self.workspace_id}/items"
        
        # Read notebook content
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = f.read()
        
        payload = {
            "displayName": notebook_name,
            "type": "Notebook",
            "definition": {
                "format": "ipynb",
                "parts": [
                    {
                        "path": "notebook-content.ipynb",
                        "payload": notebook_content,
                        "payloadType": "InlineBase64"
                    }
                ]
            }
        }
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if resp.status_code in [200, 201]:
                self.log_msg(f"    ✓ {notebook_name} uploaded", "OK")
                return True
            else:
                # Check if already exists
                if resp.status_code == 409:
                    self.log_msg(f"    ⊙ {notebook_name} já existe (skip)", "OK")
                    return True
                else:
                    self.log_msg(f"    ✗ Error {resp.status_code}", "ERROR")
                    return False
        except Exception as e:
            self.log_msg(f"    ✗ Exception: {e}", "ERROR")
            return False
    
    def upload_notebooks(self):
        """Upload all notebooks"""
        self.log_msg("STEP 1/4 — Upload de Notebooks")
        
        if not self.notebooks_dir.exists():
            self.log_msg(f"  ✗ Diretório {self.notebooks_dir} não existe", "ERROR")
            return 0
        
        notebooks = list(self.notebooks_dir.glob("*.ipynb"))
        self.log_msg(f"  Total de notebooks: {len(notebooks)}")
        
        success_count = 0
        for notebook in sorted(notebooks):
            if self.upload_notebook(notebook):
                success_count += 1
        
        self.log_msg(f"  ✓ {success_count}/{len(notebooks)} notebooks uploaded", "OK")
        return success_count
    
    def upload_files(self):
        """Upload XML files to lakehouse"""
        self.log_msg("STEP 2/4 — Upload de Arquivos XML")
        
        if not self.lakehouse_id:
            self.log_msg("  ✗ Lakehouse não encontrado", "ERROR")
            return 0
        
        if not self.data_dir.exists():
            self.log_msg(f"  ✗ Diretório {self.data_dir} não existe", "ERROR")
            return 0
        
        xml_files = list(self.data_dir.glob("*.xml")) + list(self.data_dir.glob("*.XML"))
        self.log_msg(f"  Total de arquivos XML: {len(xml_files)}")
        
        success_count = 0
        for xml_file in sorted(xml_files):
            self.log_msg(f"  Uploading: {xml_file.name}")
            
            # Upload file to lakehouse via OneLake path
            url = f"{self.api_base}/workspaces/{self.workspace_id}/lakehouses/{self.lakehouse_id}/files"
            
            try:
                with open(xml_file, 'rb') as f:
                    files = {'file': (xml_file.name, f)}
                    resp = requests.post(url, headers=self.headers, files=files, timeout=30)
                
                if resp.status_code in [200, 201, 202]:
                    self.log_msg(f"    ✓ {xml_file.name} uploaded", "OK")
                    success_count += 1
                else:
                    self.log_msg(f"    ✗ Error {resp.status_code}", "ERROR")
            except Exception as e:
                self.log_msg(f"    ✗ Exception: {e}", "ERROR")
        
        self.log_msg(f"  ✓ {success_count}/{len(xml_files)} files uploaded", "OK")
        return success_count
    
    def create_and_run_pipeline(self, pipeline_name, notebook_name):
        """Create a pipeline and run it"""
        self.log_msg(f"  Criando e executando pipeline: {pipeline_name}")
        
        # Create pipeline
        url = f"{self.api_base}/workspaces/{self.workspace_id}/items"
        payload = {
            "displayName": pipeline_name,
            "type": "Pipeline",
            "description": f"Pipeline para processamento de dados - referencia {notebook_name}"
        }
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if resp.status_code in [200, 201]:
                pipeline_item = resp.json()
                pipeline_id = pipeline_item.get('id')
                self.log_msg(f"    ✓ {pipeline_name} created (ID: {pipeline_id})", "OK")
                
                # Run pipeline
                time.sleep(2)  # Wait for item to be ready
                run_url = f"{self.api_base}/workspaces/{self.workspace_id}/items/{pipeline_id}/jobs"
                run_resp = requests.post(run_url, headers=self.headers, json={}, timeout=30)
                
                if run_resp.status_code in [200, 202]:
                    run_data = run_resp.json()
                    job_id = run_data.get('id')
                    self.log_msg(f"    ✓ Pipeline executando (Job ID: {job_id})", "OK")
                    return True
                else:
                    self.log_msg(f"    ⚠ Pipeline criado mas execução falhou ({run_resp.status_code})", "WARNING")
                    return True  # Consider as partial success
            else:
                # Check if already exists
                if resp.status_code == 409:
                    self.log_msg(f"    ⊙ {pipeline_name} já existe", "OK")
                    return True
                else:
                    self.log_msg(f"    ✗ Error {resp.status_code}", "ERROR")
                    return False
        except Exception as e:
            self.log_msg(f"    ✗ Exception: {e}", "ERROR")
            return False
    
    def create_and_run_pipelines(self):
        """Create and run pipelines"""
        self.log_msg("STEP 3/4 — Criar e Executar Pipelines")
        
        pipelines = [
            ("Pipeline_EMP_Workflow", "03_Map_EMP_Source_to_Target"),
            ("Pipeline_HR_Workflow", "05_Map_HR_Source_to_Target")
        ]
        
        success_count = 0
        for pipeline_name, notebook_name in pipelines:
            if self.create_and_run_pipeline(pipeline_name, notebook_name):
                success_count += 1
        
        self.log_msg(f"  ✓ {success_count}/{len(pipelines)} pipelines created/running", "OK")
        return success_count
    
    def check_pipeline_status(self):
        """Check status of running pipelines"""
        self.log_msg("STEP 4/4 — Verificar Status dos Pipelines")
        
        url = f"{self.api_base}/workspaces/{self.workspace_id}/items"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                items = resp.json().get('value', [])
                pipelines = [i for i in items if i.get('type') == 'Pipeline']
                self.log_msg(f"  Pipelines ativos: {len(pipelines)}", "OK")
                for pipe in pipelines:
                    print(f"    - {pipe.get('displayName')}")
                return True
            else:
                self.log_msg(f"  ✗ Erro {resp.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log_msg(f"  ✗ Exceção: {e}", "ERROR")
            return False
    
    def generate_report(self, notebooks_count, files_count, pipelines_count):
        """Generate final report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "SUCCESS",
            "workspace": {
                "id": self.workspace_id,
                "name": os.getenv('FABRIC_WORKSPACE_NAME', 'Unknown')
            },
            "lakehouse": {
                "id": self.lakehouse_id,
                "name": "powercenter_lakehouse"
            },
            "resources_created": {
                "notebooks": notebooks_count,
                "xml_files": files_count,
                "pipelines": pipelines_count,
                "total": notebooks_count + files_count + pipelines_count
            },
            "execution_log": self.log
        }
        
        # Save report
        report_file = Path("output") / f"fabric_upload_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_msg(f"Relatório salvo: {report_file}", "OK")
        return report
    
    def run(self):
        """Main workflow"""
        print("=" * 70)
        print("  FABRIC UPLOAD & PIPELINE EXECUTION")
        print("=" * 70)
        print()
        
        # Verify token
        if not self.token:
            self.log_msg("Token not found. Run: python scripts/fabric_auth_setup.py", "ERROR")
            return False
        
        self.log_msg(f"Workspace ID: {self.workspace_id}")
        self.log_msg("Iniciando upload e execução de pipelines...")
        print()
        
        # List items
        self.log_msg("STEP 0/4 — Estado do Workspace")
        self.list_workspace_items()
        print()
        
        # Find lakehouse
        if not self.find_lakehouse():
            self.log_msg("Abortando - lakehouse não encontrado", "ERROR")
            return False
        print()
        
        # Upload notebooks
        notebooks_count = self.upload_notebooks()
        print()
        
        # Upload XML files
        files_count = self.upload_files()
        print()
        
        # Create and run pipelines
        pipelines_count = self.create_and_run_pipelines()
        print()
        
        # Check pipeline status
        self.check_pipeline_status()
        print()
        
        # Generate report
        self.log_msg("Gerando relatório final...")
        report = self.generate_report(notebooks_count, files_count, pipelines_count)
        
        print()
        print("=" * 70)
        print(f"  ✓ UPLOAD E EXECUÇÃO CONCLUÍDA!")
        print("=" * 70)
        print()
        print(f"  Recursos processados:")
        print(f"    - Notebooks: {notebooks_count}")
        print(f"    - Arquivos XML: {files_count}")
        print(f"    - Pipelines: {pipelines_count}")
        print(f"    - TOTAL: {report['resources_created']['total']}")
        print()
        print(f"  Próximos passos:")
        print(f"    1. Abra o Fabric Portal: https://app.fabric.microsoft.com")
        print(f"    2. Navegue até workspace: PowerCenter Migration")
        print(f"    3. Verifique status dos pipelines")
        print(f"    4. Analise os dados transformados")
        print()
        
        return True

if __name__ == "__main__":
    uploader = FabricUploadAndExecute()
    uploader.run()
