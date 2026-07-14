#!/usr/bin/env python3
"""
Fabric MCP Migration — Usar Autenticação Configurada
Reutiliza as credenciais do .env para migração completa
"""

import os
import json
import sys
from pathlib import Path

# Carregar .env com encoding correto
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file, encoding='utf-8')
    except Exception as e:
        # Fallback: ler manualmente com encoding latino
        try:
            with open(env_file, 'r', encoding='latin-1') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip().strip('"').strip("'")
        except Exception as e2:
            print(f"[ERROR] Nao consegui ler .env: {str(e2)}")
            sys.exit(1)

FABRIC_API_URL = os.getenv("FABRIC_API_URL", "https://api.fabric.microsoft.com/v1")
FABRIC_ACCESS_TOKEN = os.getenv("FABRIC_ACCESS_TOKEN")
FABRIC_WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID")
FABRIC_WORKSPACE_NAME = os.getenv("FABRIC_WORKSPACE_NAME")

def get_fabric_headers():
    """Headers para requisições Fabric"""
    return {
        "Authorization": f"Bearer {FABRIC_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def check_credentials():
    """Verificar se credenciais estão configuradas"""
    if not FABRIC_ACCESS_TOKEN:
        print("[ERROR] Token não encontrado. Execute primeiro:")
        print("   python scripts/fabric_auth_setup.py")
        return False
    
    print(f"[OK] Autenticação carregada")
    print(f"   Workspace: {FABRIC_WORKSPACE_NAME}")
    print(f"   Workspace ID: {FABRIC_WORKSPACE_ID}")
    print(f"   API URL: {FABRIC_API_URL}")
    return True

if __name__ == "__main__":
    import sys
    if not check_credentials():
        sys.exit(1)
    print("[OK] Pronto para migração!")
    print("   Use os dados acima para continuar")
