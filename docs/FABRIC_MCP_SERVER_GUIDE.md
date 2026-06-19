# Fabric Core MCP Server - Guia Completo de Integração

## 📌 Overview

**Fabric Core MCP Server** é uma API REST que permite automação completa de operações Fabric usando Model Context Protocol (MCP).

**URL Base:**
```
https://api.fabric.microsoft.com/v1/mcp/core
```

**Caso de Uso:** Criar workspaces, lakehouses e fazer upload de arquivos CSV automaticamente.

---

## 🔑 Autenticação

### Credenciais Necessárias

Para usar a API MCP, você precisa de um App Registration no Azure AD:

1. **TenantId** — Seu Azure AD tenant ID
2. **ClientId** — Application (client) ID
3. **ClientSecret** — Client secret do App Registration

### Como Obter Credenciais

#### Via Portal Azure

1. Acesse: https://portal.azure.com/
2. Navegue para: Azure AD → App registrations
3. Clique em "+ New registration"
4. Nome: `informatica-fabric-automation`
5. Clique em "Register"

6. Na página do app:
   - Copie: **Application (client) ID** → salve como `ClientId`
   - Clique em "Certificates & secrets"
   - Clique em "+ New client secret"
   - Descrição: `FabricImportSecret`
   - Expira em: 24 meses
   - Copie o valor → salve como `ClientSecret`

7. Clique em "API permissions"
   - Clique em "+ Add a permission"
   - Selecione "APIs my organization uses"
   - Procure: "PowerBI Service"
   - Selecione: "Application permissions"
   - Marque: `Workspace.ReadWrite.All`, `Item.ReadWrite.All`
   - Clique em "Grant admin consent"

### Bearer Token

```powershell
# Obter token
$body = @{
    grant_type    = "client_credentials"
    client_id     = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"
    scope         = "https://fabric.microsoft.com/.default"
}

$response = Invoke-RestMethod `
    -Uri "https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/v2.0/token" `
    -Method Post `
    -Body $body

$token = $response.access_token

# Usar em headers
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
```

---

## 📚 Referência de Endpoints

### Workspaces

#### Listar Workspaces
```
GET /workspaces
```

**PowerShell:**
```powershell
$response = Invoke-RestMethod `
    -Uri "https://api.fabric.microsoft.com/v1/mcp/core/workspaces" `
    -Headers $headers `
    -Method Get

$response | Select-Object id, displayName, description
```

#### Criar Workspace
```
POST /workspaces
```

**PowerShell:**
```powershell
$body = @{
    displayName = "informatica-poc-workspace"
    description = "Informatica to Fabric Migration"
    capacityId = "YOUR_CAPACITY_ID"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "https://api.fabric.microsoft.com/v1/mcp/core/workspaces" `
    -Headers $headers `
    -Method Post `
    -Body $body

$workspaceId = $response.id
Write-Host "Workspace created: $workspaceId"
```

### Lakehouses

#### Criar Lakehouse
```
POST /workspaces/{workspaceId}/lakehouses
```

**PowerShell:**
```powershell
$body = @{
    displayName = "informatica_poc_data"
    description = "Data lakehouse for Informatica POC"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "https://api.fabric.microsoft.com/v1/mcp/core/workspaces/$workspaceId/lakehouses" `
    -Headers $headers `
    -Method Post `
    -Body $body

$lakehouseId = $response.id
```

#### Listar Lakehouses
```
GET /workspaces/{workspaceId}/lakehouses
```

### Files

#### Upload Arquivo
```
PUT /workspaces/{workspaceId}/lakehouses/{lakehouseId}/files/Files/{fileName}
```

**PowerShell:**
```powershell
$filePath = "output/emp_poc.csv"
$fileName = Split-Path -Leaf $filePath
$fileContent = [System.IO.File]::ReadAllBytes($filePath)

$uri = "https://api.fabric.microsoft.com/v1/mcp/core/workspaces/$workspaceId/lakehouses/$lakehouseId/files/Files/$fileName"

$response = Invoke-RestMethod `
    -Uri $uri `
    -Headers $headers `
    -Method Put `
    -Body $fileContent `
    -ContentType "application/octet-stream"

Write-Host "File uploaded: $fileName"
```

#### Listar Arquivos
```
GET /workspaces/{workspaceId}/lakehouses/{lakehouseId}/files
```

**PowerShell:**
```powershell
$response = Invoke-RestMethod `
    -Uri "https://api.fabric.microsoft.com/v1/mcp/core/workspaces/$workspaceId/lakehouses/$lakehouseId/files" `
    -Headers $headers `
    -Method Get

$response | Select-Object name, size, type
```

---

## 🚀 Automação Completa via Script

### Script: fabric-mcp-automation.ps1

**Configurar Variáveis de Ambiente:**
```powershell
$env:AZURE_TENANT_ID = "your-tenant-id"
$env:AZURE_CLIENT_ID = "your-client-id"
$env:AZURE_CLIENT_SECRET = "your-client-secret"
```

**Executar Full Setup (Criar workspace + Lakehouse + Upload):**
```powershell
.\fabric-mcp-automation.ps1 `
    -TenantId "your-tenant-id" `
    -ClientId "your-client-id" `
    -ClientSecret "your-client-secret" `
    -CapacityId "your-capacity-id" `
    -Action Full
```

**Opções de Action:**
- `Create` — Criar apenas workspace e lakehouse
- `Upload` — Upload de arquivos a um workspace existente
- `Verify` — Verificar conteúdo de um lakehouse
- `Full` — Tudo (padrão)

**Output do Script:**
```
╔════════════════════════════════════════════════════════════════╗
║            AUTHENTICATING WITH AZURE AD                       ║
╚════════════════════════════════════════════════════════════════╝
  ✓ Requesting token from: https://login.microsoftonline.com/...
  ✓ Token obtained (expires in 3599 seconds)

╔════════════════════════════════════════════════════════════════╗
║            TESTING MCP SERVER CONNECTION                       ║
╚════════════════════════════════════════════════════════════════╝
  ✓ MCP Connection successful
  ℹ Endpoint: https://api.fabric.microsoft.com/v1/mcp/core
  ℹ Response: Received 5 workspaces

╔════════════════════════════════════════════════════════════════╗
║            CREATING FABRIC WORKSPACE                           ║
╚════════════════════════════════════════════════════════════════╝
  ℹ Workspace Name: informatica-poc-workspace
  ℹ Capacity ID: abc-123-def
  ✓ Workspace created successfully
  ℹ Workspace ID: 12345678-1234-1234-1234-123456789012

✅ FABRIC ENVIRONMENT SETUP COMPLETE
```

---

## 📊 Fluxo Completo de Importação via MCP

```
┌─────────────────────────────────────────────────────┐
│ 1. AUTHENTICATE                                     │
│    Get Azure AD token                               │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│ 2. TEST CONNECTION                                  │
│    Verify MCP endpoint is accessible                │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│ 3. CREATE WORKSPACE                                 │
│    POST /workspaces                                 │
│    → Returns: workspaceId                           │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│ 4. CREATE LAKEHOUSE                                 │
│    POST /workspaces/{id}/lakehouses                 │
│    → Returns: lakehouseId                           │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│ 5. UPLOAD CSV FILES                                 │
│    PUT /files/Files/{fileName}                      │
│    - emp_poc.csv (8 rows)                           │
│    - hr_poc.csv (8 rows)                            │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│ 6. VERIFY UPLOAD                                    │
│    GET /files                                       │
│    Confirm all files present                        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│ 7. CREATE DELTA TABLES (IN NOTEBOOK)               │
│    Read CSVs and create tables                      │
│    - emp_poc (Delta table)                          │
│    - hr_poc (Delta table)                           │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│ ✅ READY FOR ANALYSIS                               │
│    Query tables via Power BI, SQL, etc.             │
└─────────────────────────────────────────────────────┘
```

---

## 🔍 Exemplos de Uso

### Exemplo 1: Criar Environment Fabric Completo

```powershell
# Define credentials (pode usar env vars também)
$creds = @{
    TenantId = "contoso.onmicrosoft.com"
    ClientId = "12345678-1234-1234-1234-123456789012"
    ClientSecret = "client_secret_value"
    CapacityId = "premium-capacity-id"
}

# Run automation
.\fabric-mcp-automation.ps1 @creds -Action Full

# Output:
# ✓ Workspace created: workspace-id-xxx
# ✓ Lakehouse created: lakehouse-id-yyy
# ✓ emp_poc.csv uploaded (0.44 KB)
# ✓ hr_poc.csv uploaded (0.57 KB)
```

### Exemplo 2: Upload para Workspace Existente

```powershell
.\fabric-mcp-automation.ps1 `
    -TenantId "contoso.onmicrosoft.com" `
    -ClientId "your-client-id" `
    -ClientSecret "your-secret" `
    -Action Upload

# Script pedirá:
# Enter Workspace ID: [seu-workspace-id]
# Enter Lakehouse ID: [seu-lakehouse-id]
```

### Exemplo 3: Verificar Conteúdo do Lakehouse

```powershell
.\fabric-mcp-automation.ps1 `
    -TenantId "your-tenant" `
    -ClientId "your-id" `
    -ClientSecret "your-secret" `
    -Action Verify

# Output:
# ✓ Files in Lakehouse:
#    - emp_poc.csv (456 bytes)
#    - hr_poc.csv (589 bytes)
```

---

## 🐛 Troubleshooting

### Erro: "Invalid token"

**Causa:** Credenciais expiradas ou incorretas

**Solução:**
```powershell
# Regenerar token
$env:AZURE_CLIENT_SECRET = "new-secret-value"
# Executar script novamente
```

### Erro: "Unauthorized (401)"

**Causa:** App Registration não tem permissões

**Solução:**
1. Acesse Azure Portal → App Registration
2. API permissions → Grant admin consent
3. Aguarde ~5 minutos para propagação
4. Tente novamente

### Erro: "Not found (404)"

**Causa:** WorkspaceId ou LakehouseId incorreto

**Solução:**
```powershell
# Listar workspaces
.\fabric-mcp-automation.ps1 -Action Verify
# Copiar ID correto e tentar novamente
```

### Erro: "File size exceeds limit"

**Causa:** Arquivo muito grande (limite: 2 GB)

**Solução:**
1. Compactar arquivo: `Compress-Archive emp_poc.csv emp_poc.zip`
2. Upload do .zip
3. Descompactar dentro do Fabric notebook

---

## 📋 Checklist de Configuração

- [ ] App Registration criado no Azure AD
- [ ] ClientId copiado
- [ ] ClientSecret gerado e salvo
- [ ] API permissions concedidas (Workspace.ReadWrite.All, Item.ReadWrite.All)
- [ ] Capacity ID obtido
- [ ] Credenciais configuradas (variáveis de ambiente ou parâmetros)
- [ ] Script fabric-mcp-automation.ps1 executado com sucesso
- [ ] Workspace e Lakehouse criados
- [ ] Arquivos CSV uploaded
- [ ] Notebook fabric_import_notebook.py criado no Fabric
- [ ] Tabelas Delta criadas
- [ ] Dados validados

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [Fabric REST API](https://learn.microsoft.com/en-us/rest/api/fabric/)
- [Workspace APIs](https://learn.microsoft.com/en-us/rest/api/fabric/workspace)
- [Lakehouse APIs](https://learn.microsoft.com/en-us/rest/api/fabric/lakehouse)

### Scripts Inclusos
- `fabric-mcp-automation.ps1` — Automação completa via PowerShell
- `fabric_import_notebook.py` — Notebook Fabric para processar dados
- `FABRIC_IMPORT_GUIDE.md` — Guia de importação (este arquivo)

---

**Versão:** 1.0  
**Data:** 2026-06-16  
**Status:** ✅ Production Ready  

Para suporte: data-engineering@company.com
