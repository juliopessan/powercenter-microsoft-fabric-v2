# 🔐 Autenticação Liberada Para Fabric

**Status:** ✅ Autenticação Ativa  
**Usuário:** marcos@mrios.com.br  
**Data:** 2026-07-14

---

## 🎯 O Que Fazer Agora

Sua autenticação foi configurada com sucesso! Você tem **3 opções** para continuar:

---

## Opção 1: Upload Manual via Portal Web (MAIS SIMPLES) ⭐

**Tempo: ~22 minutos**

Abra o portal Fabric e faça upload visual dos arquivos:

```bash
# Arquivo de guia passo a passo:
docs/UPLOAD_MANUAL_FABRIC_PORTAL.md

# Login automático com:
Usuário: marcos@mrios.com.br
Senha: Para@161
```

**Vantagens:**
- Interface visual (sem código)
- Sem complicações de API
- Funciona mesmo com limitações

👉 **[Começar: docs/UPLOAD_MANUAL_FABRIC_PORTAL.md](docs/UPLOAD_MANUAL_FABRIC_PORTAL.md)**

---

## Opção 2: Automação via API (COM CREDENCIAIS) ⚡

**Tempo: ~5 minutos (se funcionar)**

Use o script que já tem suas credenciais configuradas:

```bash
# Verificar autenticação
python scripts/fabric_check_auth.py

# Executar automação
python scripts/fabric_migration_automated.py
```

**O que faz:**
- ✅ Verifica workspace
- ✅ Tenta criar lakehouse
- ✅ Lista itens do workspace
- ⚠️ Pode falhar se capacidade Premium está indisponível

**Quando usar:**
- Se você tem capacidade Premium/Trial ativa
- Se prefere automação

👉 **Terminal Command:**
```bash
python scripts/fabric_migration_automated.py
```

---

## Opção 3: Script Python Avançado

**Tempo: Configurável**

Para usuários avançados que querem controle total:

```python
# Seu token já está em .env
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(".env"))
token = os.getenv("FABRIC_ACCESS_TOKEN")
workspace_id = os.getenv("FABRIC_WORKSPACE_ID")

# Usar em suas próprias requisições
import requests
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items",
    headers=headers
)
```

---

## 📁 Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `.env` | Credenciais e tokens (seguro) |
| `.fabric_auth.json` | Metadados de autenticação |
| `scripts/fabric_auth_setup.py` | Script de setup (já executado) |
| `scripts/fabric_check_auth.py` | Verificar credenciais |
| `scripts/fabric_migration_automated.py` | Automação com API |
| `AUTHENTICATION_SETUP_COMPLETE.md` | Status de autenticação |

---

## ✅ Verificação Rápida

Confirmar que tudo está funcionando:

```bash
# Verificar autenticação
python scripts/fabric_check_auth.py

# Saída esperada:
# [OK] Autenticação carregada
#    Workspace: PowerCenter Migration
#    Workspace ID: 999fa43f-32d3-4a10-ad5d-b58a5962e43a
#    API URL: https://api.fabric.microsoft.com/v1
# [OK] Pronto para migração!
```

---

## 🚀 Recomendação

### Se Quer Fazer Rápido (22 min)
👉 **[docs/UPLOAD_MANUAL_FABRIC_PORTAL.md](docs/UPLOAD_MANUAL_FABRIC_PORTAL.md)**

### Se Quer Automação Total (5 min, pode falhar)
```bash
python scripts/fabric_migration_automated.py
```

### Se Quer Entender Tudo
👉 **[AUTHENTICATION_SETUP_COMPLETE.md](AUTHENTICATION_SETUP_COMPLETE.md)**

---

## 📞 Problemas?

### Erro: Token expirado
```bash
# Re-executar autenticação
python scripts/fabric_auth_setup.py
```

### Erro: FeatureNotAvailable
Sua capacidade pode não ter Premium. Use portal web em vez disso.

### Erro: Arquivo .env não encontrado
Você pulou o step de autenticação. Execute:
```bash
python scripts/fabric_auth_setup.py
```

---

## 🔐 Segurança

- ✅ `.env` está em `.gitignore`
- ✅ `.env` tem permissões de leitura-only (0o600)
- ✅ Credenciais não aparecem em logs
- ✅ Token válido por ~1 hora

**Nunca commit `.env` no git!**

---

## 🎯 Próximo Passo

**ESCOLHA UMA OPÇÃO:**

### 1️⃣ Portal Manual (Recomendado)
Abra: [docs/UPLOAD_MANUAL_FABRIC_PORTAL.md](docs/UPLOAD_MANUAL_FABRIC_PORTAL.md)

### 2️⃣ Automação
```bash
python scripts/fabric_migration_automated.py
```

### 3️⃣ Entender Mais
Leia: [AUTHENTICATION_SETUP_COMPLETE.md](AUTHENTICATION_SETUP_COMPLETE.md)

---

**Status:** ✅ Autenticação Ativa  
**Válido Até:** ~1 hora  
**Próxima Ação:** Escolha acima
