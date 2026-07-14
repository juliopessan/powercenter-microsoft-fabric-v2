#!/usr/bin/env python3
"""
Fabric Authentication Setup — Configure credenciais para migração
Autentica com marcos@mrios.com.br e gera tokens para Fabric API
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

try:
    from azure.identity import UsernamePasswordCredential, DefaultAzureCredential
    from azure.core.exceptions import ClientAuthenticationError
    import requests
except ImportError:
    print("❌ Dependências ausentes. Instale com:")
    print("   pip install azure-identity azure-core requests")
    sys.exit(1)

# Cores para output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

class FabricAuthSetup:
    """Configurar autenticação Fabric com credenciais do usuário"""
    
    def __init__(self):
        self.workspace_root = Path(__file__).parent.parent
        self.env_file = self.workspace_root / ".env"
        self.config_file = self.workspace_root / ".fabric_auth.json"
        self.tenant_id = "organizations"  # Multi-tenant
        
        # Credenciais fornecidas
        self.username = "marcos@mrios.com.br"
        self.password = "Para@161"
        
        # URLs
        self.fabric_api_url = "https://api.fabric.microsoft.com/v1"
        self.graph_api_url = "https://graph.microsoft.com"
        self.arm_url = "https://management.azure.com"
        
    def print_header(self, text):
        print(f"\n{BLUE}{'='*60}")
        print(f"{text:^60}")
        print(f"{'='*60}{RESET}\n")
    
    def print_success(self, text):
        print(f"{GREEN}[OK] {text}{RESET}")
    
    def print_error(self, text):
        print(f"{RED}[ERROR] {text}{RESET}")
    
    def print_info(self, text):
        print(f"{BLUE}[INFO] {text}{RESET}")
    
    def print_warning(self, text):
        print(f"{YELLOW}[WARN] {text}{RESET}")
    
    def authenticate_username_password(self):
        """Autenticar com username/password"""
        self.print_info("Autenticando com credenciais fornecidas...")
        
        try:
            # Credencial via username/password
            credential = UsernamePasswordCredential(
                client_id="04b07795-8ddb-461a-bbee-02f9e1bf7b46",  # Azure CLI client ID
                username=self.username,
                password=self.password,
                tenant_id="organizations"  # Use organizations para multi-tenant
            )
            
            # Tentar obter token (sem /v1 no escopo)
            token = credential.get_token("https://api.fabric.microsoft.com/.default")
            self.print_success(f"Token obtido para {self.username}")
            
            return credential, token
            
        except ClientAuthenticationError as e:
            self.print_error(f"Erro de autenticação: {str(e)}")
            self.print_info("Possíveis causas:")
            print("  1. Credenciais incorretas")
            print("  2. Usuário requer MFA/2FA")
            print("  3. Conta não tem acesso ao Fabric")
            return None, None
    
    def test_fabric_connection(self, token):
        """Testar conexão com Fabric API"""
        self.print_info("Testando conexão com Fabric API...")
        
        try:
            headers = {
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json"
            }
            
            # Testar endpoint de workspaces
            response = requests.get(
                f"{self.fabric_api_url}/workspaces",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Conexão com Fabric API estabelecida!")
                self.print_info(f"Total de workspaces encontrados: {len(data.get('value', []))}")
                
                # Buscar workspace "PowerCenter Migration"
                for ws in data.get('value', []):
                    if ws.get('displayName') == 'PowerCenter Migration':
                        self.print_success(f"Workspace encontrado: {ws['id']}")
                        return True
                
                return True
            else:
                self.print_error(f"Erro na conexão (HTTP {response.status_code})")
                self.print_info(f"Resposta: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_error(f"Erro de conexão: {str(e)}")
            return False
    
    def save_credentials(self, credential, token):
        """Salvar credenciais e tokens em arquivo seguro"""
        self.print_info("Salvando credenciais...")
        
        try:
            # Criar arquivo .env
            env_content = f"""# Fabric Authentication Credentials
# Gerado em: {datetime.now().isoformat()}

# Credenciais do Usuário
FABRIC_USERNAME="{self.username}"
FABRIC_PASSWORD="{self.password}"

# URLs da API
FABRIC_API_URL="{self.fabric_api_url}"
GRAPH_API_URL="{self.graph_api_url}"
ARM_URL="{self.arm_url}"

# Tenant
AZURE_TENANT_ID="{self.tenant_id}"

# Client ID (Azure CLI)
AZURE_CLIENT_ID="04b07795-8ddb-461a-bbee-02f9e1bf7b46"

# Token (válido por ~1 hora)
FABRIC_ACCESS_TOKEN="{token.token}"
TOKEN_EXPIRES_ON={token.expires_on}

# Workspace
FABRIC_WORKSPACE_ID="999fa43f-32d3-4a10-ad5d-b58a5962e43a"
FABRIC_WORKSPACE_NAME="PowerCenter Migration"
"""
            
            # Salvar .env
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            
            # Tornar arquivo seguro (leitura apenas para o usuário)
            os.chmod(self.env_file, 0o600)
            
            self.print_success(f".env criado: {self.env_file}")
            
            # Criar arquivo JSON com metadados
            config_data = {
                "username": self.username,
                "tenant_id": self.tenant_id,
                "workspace_id": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
                "workspace_name": "PowerCenter Migration",
                "token_generated": datetime.now().isoformat(),
                "token_expires_on": token.expires_on,
                "api_endpoints": {
                    "fabric": self.fabric_api_url,
                    "graph": self.graph_api_url,
                    "arm": self.arm_url
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            os.chmod(self.config_file, 0o600)
            
            self.print_success(f"Configuração salva: {self.config_file}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro ao salvar credenciais: {str(e)}")
            return False
    
    def create_auth_script(self):
        """Criar script para reutilizar autenticação"""
        self.print_info("Criando script de autenticação reutilizável...")
        
        script_content = '''#!/usr/bin/env python3
"""Reutilizar autenticação Fabric do .env"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env
env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)

FABRIC_API_URL = os.getenv("FABRIC_API_URL")
FABRIC_ACCESS_TOKEN = os.getenv("FABRIC_ACCESS_TOKEN")
FABRIC_WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID")

def get_fabric_headers():
    """Retornar headers para requisições Fabric"""
    return {
        "Authorization": f"Bearer {FABRIC_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def get_workspace_id():
    """Retornar workspace ID"""
    return FABRIC_WORKSPACE_ID

if __name__ == "__main__":
    print("✅ Configuração carregada")
    print(f"   Workspace: {FABRIC_WORKSPACE_ID}")
    print(f"   API URL: {FABRIC_API_URL}")
'''
        
        auth_helper_file = self.workspace_root / "scripts" / "fabric_auth_helper.py"
        with open(auth_helper_file, 'w') as f:
            f.write(script_content)
        
        self.print_success(f"Script criado: {auth_helper_file}")
    
    def setup(self):
        """Executar setup completo"""
        self.print_header("🔐 FABRIC AUTHENTICATION SETUP")
        
        print(f"Usuário: {self.username}")
        print(f"Workspace: PowerCenter Migration")
        print(f"Workspace ID: 999fa43f-32d3-4a10-ad5d-b58a5962e43a\n")
        
        # Step 1: Autenticar
        self.print_header("Step 1: Autenticação")
        credential, token = self.authenticate_username_password()
        
        if not credential or not token:
            self.print_error("Falha na autenticação")
            return False
        
        # Step 2: Testar conexão
        self.print_header("Step 2: Teste de Conexão")
        if not self.test_fabric_connection(token):
            self.print_warning("Conexão com Fabric não foi bem-sucedida")
            # Continuar mesmo com falha, pode ser MFA
        
        # Step 3: Salvar credenciais
        self.print_header("Step 3: Salvar Credenciais")
        if not self.save_credentials(credential, token):
            return False
        
        # Step 4: Criar script helper
        self.print_header("Step 4: Criar Scripts")
        self.create_auth_script()
        
        # Resumo final
        self.print_header("✅ SETUP CONCLUÍDO")
        print("Arquivos criados:")
        print(f"  📄 {self.env_file}")
        print(f"  📄 {self.config_file}")
        print(f"  📄 {self.workspace_root / 'scripts' / 'fabric_auth_helper.py'}\n")
        
        print("Próximos passos:")
        print("  1. Arquivos .env e .fabric_auth.json criados")
        print("  2. Use fabric_auth_helper.py para reutilizar a autenticação")
        print("  3. Execute: python scripts/fabric_mcp_migration.py")
        print("  4. OU execute: python docs/UPLOAD_MANUAL_FABRIC_PORTAL.md (manual)\n")
        
        print(f"{GREEN}✨ Você está pronto para migração!{RESET}\n")
        
        return True

def main():
    setup = FabricAuthSetup()
    success = setup.setup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
