#!/usr/bin/env python3
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
