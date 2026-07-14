#!/usr/bin/env python3
"""
Fabric Authentication with Full Scopes
Regenerates token with all required scopes for MCP operations
"""

import os
import json
from dotenv import load_dotenv
from azure.identity import UsernamePasswordCredential
from datetime import datetime

class FabricFullScopesAuth:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('FABRIC_USERNAME', 'marcus@mrios.com.br')
        self.password = os.getenv('FABRIC_PASSWORD', 'Para@161')
        self.tenant_id = 'organizations'
        
        # Full scopes for Fabric API
        self.scopes_full = [
            "https://api.fabric.microsoft.com/.default",
            "https://graph.microsoft.com/.default",
        ]
    
    def get_token_with_full_scopes(self):
        """Generate token with all required scopes"""
        print("🔐 Regenerando token com escopos completos...")
        
        try:
            credential = UsernamePasswordCredential(
                client_id="04b07795-8ddb-461a-bbee-02f9e1bf7b46",  # Azure CLI client
                username=self.username,
                password=self.password,
                tenant_id=self.tenant_id
            )
            
            # Get token with full scopes
            token = credential.get_token("https://api.fabric.microsoft.com/.default")
            
            print(f"✅ Token obtido com sucesso!")
            print(f"   Expiração: {datetime.fromtimestamp(token.expires_on)}")
            
            return token.token
            
        except Exception as e:
            print(f"❌ Erro ao gerar token: {e}")
            raise
    
    def update_env_with_token(self, token):
        """Update .env file with new token"""
        print("💾 Atualizando .env com novo token...")
        
        env_file = '.env'
        
        # Read current .env
        env_content = {}
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, val = line.strip().split('=', 1)
                        env_content[key] = val
        
        # Update token
        env_content['FABRIC_ACCESS_TOKEN'] = token
        
        # Write updated .env
        with open(env_file, 'w') as f:
            for key, val in env_content.items():
                f.write(f"{key}={val}\n")
        
        os.chmod(env_file, 0o600)
        print(f"✅ .env atualizado com sucesso!")
    
    def verify_token(self, token):
        """Verify token works with Fabric API"""
        print("🔍 Verificando token com Fabric API...")
        
        import requests
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        workspace_id = os.getenv('FABRIC_WORKSPACE_ID', '999fa43f-32d3-4a10-ad5d-b58a5962e43a')
        url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}"
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                workspace_info = resp.json()
                print(f"✅ Token válido! Workspace acessível:")
                print(f"   Nome: {workspace_info.get('displayName', 'N/A')}")
                print(f"   ID: {workspace_info.get('id', 'N/A')}")
                return True
            elif resp.status_code == 403:
                print(f"⚠️  Token aceito mas permissões insuficientes: {resp.json()}")
                return False
            else:
                print(f"❌ Erro {resp.status_code}: {resp.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao verificar: {e}")
            return False
    
    def run(self):
        """Main workflow"""
        print("=" * 60)
        print("Fabric Auth — Full Scopes")
        print("=" * 60)
        
        # Get token
        token = self.get_token_with_full_scopes()
        
        # Update .env
        self.update_env_with_token(token)
        
        # Verify
        if self.verify_token(token):
            print("\n✅ Token com escopos completos gerado e validado!")
            print("\n📋 Próximos passos:")
            print("   1. Tente as operações MCP novamente")
            print("   2. Se ainda falhar: Use upload manual via portal")
            print("\n💡 Dica: Se persiste erro 403, workspace pode precisar")
            print("   de capacidade Premium para MCP criar itens via API.")
            return True
        else:
            print("\n❌ Token validado mas com permissões insuficientes")
            print("\n💡 Use upload manual: docs/UPLOAD_MANUAL_FABRIC_PORTAL.md")
            return False

if __name__ == "__main__":
    auth = FabricFullScopesAuth()
    auth.run()
