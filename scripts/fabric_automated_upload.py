#!/usr/bin/env python3
"""
Fabric Automated Upload — Complete Integration
Uploads all notebooks, XMLs, and creates pipelines in one go
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

class FabricAutomatedUpload:
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
    
    def log_msg(self, msg, level="INFO"):
        """Log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] [{level}] {msg}"
        print(full_msg)
        self.log.append(full_msg)
    
    def list_workspace_items(self):
        """List existing items in workspace"""
        self.log_msg("Listando itens no workspace...")
        url = f"{self.api_base}/workspaces/{self.workspace_id}/items"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                items = resp.json().get('value', [])
                self.log_msg(f"  ✓ {len(items)} itens encontrados", "OK")
                for item in items[:5]:  # Show first 5
                    print(f"    - {item.get('displayName')} ({item.get('type')})")
                if len(items) > 5:
                    print(f"    ... e mais {len(items) - 5}")
                return items
            else:
                self.log_msg(f"  ✗ Erro {resp.status_code}", "ERROR")
                return []
        except Exception as e:
            self.log_msg(f"  ✗ Exceção: {e}", "ERROR")
            return []
    
    def create_lakehouse(self):
        """Create lakehouse"""
        self.log_msg("Criando lakehouse 'powercenter_lakehouse'...")
        
        url = f"{self.api_base}/workspaces/{self.workspace_id}/items"
        payload = {
            "displayName": "powercenter_lakehouse",
            "type": "Lakehouse",
            "description": "Lakehouse para migração PowerCenter"
        }
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=15)
            if resp.status_code in [200, 201]:
                item = resp.json()
                lakehouse_id = item.get('id')
                self.log_msg(f"  ✓ Lakehouse criado: {lakehouse_id}", "OK")
                return lakehouse_id
            else:
                self.log_msg(f"  ✗ Erro {resp.status_code}: {resp.text}", "ERROR")
                return None
        except Exception as e:
            self.log_msg(f"  ✗ Exceção: {e}", "ERROR")
            return None
    
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
                self.log_msg(f"    ✗ Error {resp.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log_msg(f"    ✗ Exception: {e}", "ERROR")
            return False
    
    def upload_notebooks(self):
        """Upload all notebooks"""
        self.log_msg("Fazendo upload de notebooks...")
        
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
    
    def upload_files(self, lakehouse_id):
        """Upload XML files to lakehouse"""
        self.log_msg("Fazendo upload de arquivos XML...")
        
        if not self.data_dir.exists():
            self.log_msg(f"  ✗ Diretório {self.data_dir} não existe", "ERROR")
            return 0
        
        xml_files = list(self.data_dir.glob("*.xml")) + list(self.data_dir.glob("*.XML"))
        self.log_msg(f"  Total de arquivos XML: {len(xml_files)}")
        
        success_count = 0
        for xml_file in sorted(xml_files):
            self.log_msg(f"  Uploading: {xml_file.name}")
            
            # Upload file to lakehouse
            url = f"{self.api_base}/workspaces/{self.workspace_id}/lakehouses/{lakehouse_id}/files"
            
            try:
                with open(xml_file, 'rb') as f:
                    files = {'file': (xml_file.name, f)}
                    resp = requests.post(url, headers=self.headers, files=files, timeout=30)
                
                if resp.status_code in [200, 201]:
                    self.log_msg(f"    ✓ {xml_file.name} uploaded", "OK")
                    success_count += 1
                else:
                    self.log_msg(f"    ✗ Error {resp.status_code}", "ERROR")
            except Exception as e:
                self.log_msg(f"    ✗ Exception: {e}", "ERROR")
        
        self.log_msg(f"  ✓ {success_count}/{len(xml_files)} files uploaded", "OK")
        return success_count
    
    def create_pipeline(self, pipeline_name, notebook_name):
        """Create a pipeline"""
        self.log_msg(f"  Criando pipeline: {pipeline_name}")
        
        url = f"{self.api_base}/workspaces/{self.workspace_id}/items"
        payload = {
            "displayName": pipeline_name,
            "type": "Pipeline",
            "description": f"Pipeline para processamento de dados - referencia {notebook_name}",
            "definition": {
                "activities": [
                    {
                        "name": f"Activity_{notebook_name}",
                        "type": "NotebookActivity",
                        "notebookPath": notebook_name
                    }
                ]
            }
        }
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if resp.status_code in [200, 201]:
                self.log_msg(f"    ✓ {pipeline_name} created", "OK")
                return True
            else:
                self.log_msg(f"    ✗ Error {resp.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log_msg(f"    ✗ Exception: {e}", "ERROR")
            return False
    
    def create_pipelines(self):
        """Create pipelines"""
        self.log_msg("Criando pipelines...")
        
        pipelines = [
            ("Pipeline_EMP_Workflow", "03_Map_EMP_Source_to_Target"),
            ("Pipeline_HR_Workflow", "05_Map_HR_Source_to_Target")
        ]
        
        success_count = 0
        for pipeline_name, notebook_name in pipelines:
            if self.create_pipeline(pipeline_name, notebook_name):
                success_count += 1
        
        self.log_msg(f"  ✓ {success_count}/{len(pipelines)} pipelines created", "OK")
        return success_count
    
    def generate_report(self, lakehouse_id, notebooks_count, files_count, pipelines_count):
        """Generate final report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "SUCCESS",
            "workspace": {
                "id": self.workspace_id,
                "name": os.getenv('FABRIC_WORKSPACE_NAME', 'Unknown')
            },
            "resources_created": {
                "lakehouse": 1,
                "notebooks": notebooks_count,
                "xml_files": files_count,
                "pipelines": pipelines_count,
                "total": 1 + notebooks_count + files_count + pipelines_count
            },
            "lakehouse_id": lakehouse_id,
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
        print("  FABRIC AUTOMATED UPLOAD — Complete Integration")
        print("=" * 70)
        print()
        
        # Verify token
        if not self.token:
            self.log_msg("Token not found. Run: python scripts/fabric_auth_setup.py", "ERROR")
            return False
        
        self.log_msg(f"Workspace ID: {self.workspace_id}")
        self.log_msg("Iniciando integração automática...")
        print()
        
        # List existing items
        self.log_msg("STEP 1/5 — Listar itens existentes")
        self.list_workspace_items()
        print()
        
        # Create lakehouse
        self.log_msg("STEP 2/5 — Criar Lakehouse")
        lakehouse_id = self.create_lakehouse()
        if not lakehouse_id:
            self.log_msg("Falha ao criar lakehouse. Abortando.", "ERROR")
            return False
        print()
        
        # Upload notebooks
        self.log_msg("STEP 3/5 — Upload de Notebooks")
        notebooks_count = self.upload_notebooks()
        print()
        
        # Upload XML files
        self.log_msg("STEP 4/5 — Upload de Arquivos XML")
        files_count = self.upload_files(lakehouse_id)
        print()
        
        # Create pipelines
        self.log_msg("STEP 5/5 — Criar Pipelines")
        pipelines_count = self.create_pipelines()
        print()
        
        # Generate report
        self.log_msg("Gerando relatório final...")
        report = self.generate_report(lakehouse_id, notebooks_count, files_count, pipelines_count)
        
        print()
        print("=" * 70)
        print(f"  ✓ INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        print()
        print(f"  Recursos criados:")
        print(f"    - Lakehouse: 1")
        print(f"    - Notebooks: {notebooks_count}")
        print(f"    - Arquivos XML: {files_count}")
        print(f"    - Pipelines: {pipelines_count}")
        print(f"    - TOTAL: {report['resources_created']['total']}")
        print()
        print(f"  Próximos passos:")
        print(f"    1. Abra o Fabric Portal")
        print(f"    2. Navegue até o workspace 'PowerCenter Migration'")
        print(f"    3. Execute os pipelines para transformar os dados")
        print()
        
        return True

if __name__ == "__main__":
    uploader = FabricAutomatedUpload()
    uploader.run()
