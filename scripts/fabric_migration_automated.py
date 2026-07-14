#!/usr/bin/env python3
"""
Fabric Automated Migration — Usar Credenciais Autenticadas
Automação completa após setup de autenticação
"""

import os
import json
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("[ERROR] requests não instalado. Execute: pip install requests")
    sys.exit(1)

# Carregar credenciais
env_file = Path(__file__).parent.parent / ".env"
if not env_file.exists():
    print("[ERROR] .env não encontrado!")
    print("Execute primeiro: python scripts/fabric_auth_setup.py")
    sys.exit(1)

load_dotenv(env_file)

FABRIC_API_URL = os.getenv("FABRIC_API_URL", "https://api.fabric.microsoft.com/v1")
FABRIC_ACCESS_TOKEN = os.getenv("FABRIC_ACCESS_TOKEN")
FABRIC_WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID")
FABRIC_WORKSPACE_NAME = os.getenv("FABRIC_WORKSPACE_NAME")

class FabricAutomation:
    """Automação de migração usando credenciais autenticadas"""
    
    def __init__(self):
        self.api_url = FABRIC_API_URL
        self.workspace_id = FABRIC_WORKSPACE_ID
        self.headers = {
            "Authorization": f"Bearer {FABRIC_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        self.workspace_root = Path(__file__).parent.parent
    
    def print_step(self, step, text):
        print(f"\n[{step}] {text}")
    
    def print_success(self, text):
        print(f"    [OK] {text}")
    
    def print_error(self, text):
        print(f"    [ERROR] {text}")
    
    def print_info(self, text):
        print(f"    [INFO] {text}")
    
    def check_workspace(self):
        """Verificar workspace"""
        self.print_step("1/6", "Verificando workspace...")
        
        try:
            response = requests.get(
                f"{self.api_url}/workspaces/{self.workspace_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Workspace encontrado: {data.get('displayName')}")
                return True
            else:
                self.print_error(f"HTTP {response.status_code}: {response.text[:100]}")
                return False
        except Exception as e:
            self.print_error(f"Falha: {str(e)}")
            return False
    
    def create_lakehouse(self, name="powercenter_lakehouse"):
        """Criar lakehouse"""
        self.print_step("2/6", f"Criando lakehouse '{name}'...")
        
        try:
            payload = {
                "displayName": name,
                "description": "Lakehouse para migracão PowerCenter"
            }
            
            response = requests.post(
                f"{self.api_url}/workspaces/{self.workspace_id}/lakehouses",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                data = response.json()
                lakehouse_id = data.get('id')
                self.print_success(f"Lakehouse criado: {lakehouse_id}")
                return lakehouse_id
            else:
                self.print_error(f"HTTP {response.status_code}")
                if "FeatureNotAvailable" in response.text:
                    self.print_error("Capacidade Premium necessária")
                self.print_info(f"Resposta: {response.text[:200]}")
                return None
        except Exception as e:
            self.print_error(f"Falha: {str(e)}")
            return None
    
    def upload_notebook(self, notebook_path):
        """Upload de notebook"""
        notebook_path = Path(notebook_path)
        
        if not notebook_path.exists():
            self.print_error(f"Arquivo não encontrado: {notebook_path}")
            return None
        
        notebook_name = notebook_path.stem  # Sem extensão
        file_size = notebook_path.stat().st_size / 1024  # KB
        
        self.print_info(f"Upload: {notebook_name} ({file_size:.1f} KB)")
        
        try:
            with open(notebook_path, 'rb') as f:
                files = {'file': (notebook_path.name, f, 'application/json')}
                
                # Nota: Endpoint exato depende da versão da API
                # Simplificado aqui - pode precisar de ajuste
                
                response = requests.post(
                    f"{self.api_url}/workspaces/{self.workspace_id}/notebooks",
                    headers={
                        "Authorization": f"Bearer {FABRIC_ACCESS_TOKEN}"
                    },
                    files=files,
                    timeout=60
                )
                
                if response.status_code in [200, 201, 202]:
                    self.print_success(f"Notebook enviado: {notebook_name}")
                    return response.json().get('id')
                else:
                    self.print_error(f"HTTP {response.status_code}")
                    if "FeatureNotAvailable" in response.text:
                        self.print_error("Capacidade Premium necessária")
                    return None
        except Exception as e:
            self.print_error(f"Falha: {str(e)}")
            return None
    
    def list_items(self):
        """Listar itens do workspace"""
        self.print_step("3/6", "Listando itens do workspace...")
        
        try:
            response = requests.get(
                f"{self.api_url}/workspaces/{self.workspace_id}/items",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('value', [])
                self.print_success(f"Total de itens: {len(items)}")
                
                for item in items[:5]:  # Mostrar primeiros 5
                    item_type = item.get('type', 'Unknown')
                    item_name = item.get('displayName', 'N/A')
                    self.print_info(f"- {item_name} ({item_type})")
                
                if len(items) > 5:
                    self.print_info(f"... e {len(items) - 5} mais")
                
                return len(items)
            else:
                self.print_error(f"HTTP {response.status_code}")
                return 0
        except Exception as e:
            self.print_error(f"Falha: {str(e)}")
            return 0
    
    def run_all_checks(self):
        """Executar todas as verificações"""
        print("\n" + "="*60)
        print("FABRIC AUTOMATED MIGRATION - AUTHENTICATED".center(60))
        print("="*60)
        
        print(f"\nWorkspace: {FABRIC_WORKSPACE_NAME}")
        print(f"Workspace ID: {FABRIC_WORKSPACE_ID}")
        print(f"API URL: {FABRIC_API_URL}")
        
        success = True
        
        # Check 1: Workspace
        if not self.check_workspace():
            success = False
        
        # Check 2: Try to create lakehouse (peut échouer si pas de Premium)
        lakehouse_id = self.create_lakehouse()
        
        # Check 3: List items
        item_count = self.list_items()
        
        print("\n" + "="*60)
        if success:
            print("STATUS: [OK] Autenticacao ativa, pronto para migracao".center(60))
        else:
            print("STATUS: [WARN] Algumas verificacoes falharam".center(60))
        print("="*60)
        
        print("\nProximos passos:")
        if lakehouse_id:
            print("  1. Lakehouse criado - pronto para upload de arquivos")
            print("  2. Execute: python scripts/fabric_upload_files.py")
        else:
            print("  1. API retornou erro (pode ser Premium capacity)")
            print("  2. Alternativa: Use portal web (docs/UPLOAD_MANUAL_FABRIC_PORTAL.md)")
        
        print(f"\nTotal de itens encontrados: {item_count}")

def main():
    try:
        automation = FabricAutomation()
        automation.run_all_checks()
    except KeyboardInterrupt:
        print("\n[CANCELLED] Operacao cancelada pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
