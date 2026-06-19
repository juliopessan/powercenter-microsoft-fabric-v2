# Guia Completo: Importar Outputs para Microsoft Fabric

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-Requisitos](#pré-requisitos)
3. [Passo 1: Criar Ambiente Fabric](#passo-1-criar-ambiente-fabric)
4. [Passo 2: Criar Lakehouse](#passo-2-criar-lakehouse)
5. [Passo 3: Preparar Dados](#passo-3-preparar-dados)
6. [Passo 4: Importar via UI](#passo-4-importar-via-ui)
7. [Passo 5: Importar via API](#passo-5-importar-via-api)
8. [Passo 6: Validar Dados](#passo-6-validar-dados)
9. [Passo 7: Criar Tabelas Delta](#passo-7-criar-tabelas-delta)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Este guia orienta você a:
- ✅ Criar um workspace Fabric
- ✅ Configurar um Lakehouse
- ✅ Importar CSVs gerados (emp_poc.csv, hr_poc.csv)
- ✅ Validar dados
- ✅ Criar tabelas Delta para consultas

**Arquivos de Input:**
- `output/emp_poc.csv` — 8 registros de employees
- `output/hr_poc.csv` — 8 registros flattened (3 departments)

**Tempo Estimado:** 20-30 minutos

---

## ✅ Pré-Requisitos

### Necessário
- ✅ Conta Microsoft com acesso ao Azure
- ✅ Capacidade Fabric (trial ou premium)
- ✅ Permissões para criar workspaces
- ✅ Os arquivos CSV gerados (`output/emp_poc.csv`, `output/hr_poc.csv`)
- ✅ Fabric Core MCP Server configurado

### Fabric Core MCP Server

1. **Enter the Fabric Core MCP Server URL:**
   ```
   https://api.fabric.microsoft.com/v1/mcp/core
   ```

2. **Autenticação:**
   ```
   - Tipo: Azure AD (Entra ID)
   - Escopo: https://fabric.microsoft.com/.default
   - Permissões: Workspace.ReadWrite.All, Item.ReadWrite.All
   ```

3. **Verificar Conexão:**
   ```powershell
   # Testar conectividade
   $uri = "https://api.fabric.microsoft.com/v1/mcp/core/workspaces"
   $headers = @{
       "Authorization" = "Bearer $token"
       "Content-Type" = "application/json"
   }
   
   $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
   Write-Host "✓ Connection successful" -ForegroundColor Green
   ```

### Opcional
- ⚠️ Power BI Desktop (para análise posterior)
- ⚠️ Azure Storage Explorer (para debug)
- ⚠️ Postman (para testar API Fabric)

### Verificar

```powershell
# Verificar se os CSVs existem
Get-ChildItem -Path "output\*.csv" -Recurse

# Output esperado:
# emp_poc.csv  (0.44 KB)
# hr_poc.csv   (0.57 KB)
```

---

## 🚀 Passo 1: Criar Ambiente Fabric

### Opção A: Via Portal Azure (5 minutos)

1. **Acesse Fabric**
   ```
   URL: https://app.powerbi.com/
   ```

2. **Crie uma Workspace**
   - Clique em "Workspaces" (lado esquerdo)
   - Clique em "New workspace"
   - Nome: `informatica-poc-workspace`
   - Descrição: `Informatica PowerCenter to Fabric Migration POC`
   - Capacidade: Trial ou Premium (à sua escolha)
   - Clique em "Apply"

3. **Aguarde a criação**
   - Status: "Creating workspace..."
   - Tempo: ~30 segundos

4. **Verifique**
   - Workspace agora aparece na lista
   - Você é o owner/admin

### Opção B: Via PowerShell (Automação)

```powershell
# Script: Create-FabricWorkspace.ps1
# Requisite: Azure CLI + Fabric CLI (beta)

# Autenticar
az login --tenant <your-tenant-id>

# Criar workspace
az fabric workspace create \
  --name "informatica-poc-workspace" \
  --description "Informatica POC" \
  --capacity-id "<your-capacity-id>"
```

---

## 📦 Passo 2: Criar Lakehouse

### Via UI (Recomendado - 3 minutos)

1. **No Workspace**
   - Clique em "+ New"
   - Selecione "Lakehouse"

2. **Configure**
   - Nome: `informatica_poc_data`
   - Clique em "Create"

3. **Aguarde**
   - Status: "Creating lakehouse..."
   - Tempo: ~20 segundos

4. **Verifique**
   ```
   Lakehouse criado com:
   ├── Tables folder (para tabelas Delta)
   ├── Files folder (para arquivos CSV/Parquet)
   └── Shortcuts (para dados externos)
   ```

### Via Python (Dentro de Notebook)

```python
# Dentro de um notebook Fabric
from notebookutils import mssparkutils

# Criar lakehouse
workspace_id = "your-workspace-id"
lakehouse_name = "informatica_poc_data"

# PySpark pode acessar automaticamente
# após a criação via UI
```

---

## � Passo 2B: Configurar Fabric Core MCP Server

### O que é MCP Server?

Model Context Protocol (MCP) é um protocolo aberto para integração com Claude e outras ferramentas de IA. O Fabric Core MCP permite automação de operações Fabric via API.

### URL Base do Fabric Core MCP Server

```
https://api.fabric.microsoft.com/v1/mcp/core
```

### Endpoints Disponíveis

| Operação | Endpoint | Método |
|----------|----------|--------|
| Listar Workspaces | `/workspaces` | GET |
| Criar Workspace | `/workspaces` | POST |
| Criar Lakehouse | `/lakehouses` | POST |
| Upload Arquivo | `/files/{path}` | PUT |
| Listar Arquivos | `/files` | GET |
| Executar Query | `/query/execute` | POST |

### Autenticação com Azure AD

```powershell
# Script: Authenticate-FabricMCP.ps1

# 1. Obter token
$tenantId = "<your-tenant-id>"
$clientId = "<your-app-registration-id>"
$clientSecret = "<your-client-secret>"

$tokenUri = "https://login.microsoftonline.com/$tenantId/oauth2/v2.0/token"

$body = @{
    grant_type    = "client_credentials"
    client_id     = $clientId
    client_secret = $clientSecret
    scope         = "https://fabric.microsoft.com/.default"
}

$response = Invoke-RestMethod -Uri $tokenUri -Method Post -Body $body
$token = $response.access_token

Write-Host "✓ Token obtained successfully" -ForegroundColor Green

# 2. Testar conexão MCP
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$mcp_uri = "https://api.fabric.microsoft.com/v1/mcp/core/workspaces"

try {
    $workspaces = Invoke-RestMethod -Uri $mcp_uri -Headers $headers -Method Get
    Write-Host "✓ MCP Connection successful" -ForegroundColor Green
    Write-Host "  Found $($workspaces.Count) workspaces"
} catch {
    Write-Host "✗ MCP Connection failed: $($_.Exception.Message)" -ForegroundColor Red
}
```

### Criar Workspace via MCP API

```powershell
# Criar novo workspace via MCP

$body = @{
    displayName = "informatica-poc-workspace"
    description = "Informatica PowerCenter to Fabric Migration POC"
    capacityId = "<your-capacity-id>"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "https://api.fabric.microsoft.com/v1/mcp/core/workspaces" `
    -Headers $headers `
    -Method Post `
    -Body $body

$workspaceId = $response.id

Write-Host "✓ Workspace created: $workspaceId" -ForegroundColor Green
```

### Criar Lakehouse via MCP API

```powershell
# Criar Lakehouse no workspace

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

Write-Host "✓ Lakehouse created: $lakehouseId" -ForegroundColor Green
```

### Upload Arquivo via MCP API

```powershell
# Upload CSV file ao Lakehouse

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

Write-Host "✓ File uploaded: $fileName" -ForegroundColor Green
```

---

## �📁 Passo 3: Preparar Dados

### Verificar Integridade dos CSVs

```powershell
# Script: Verify-CSVs.ps1

$csvFiles = @(
    "output/emp_poc.csv",
    "output/hr_poc.csv"
)

foreach ($file in $csvFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        $lines = @(Get-Content $file).Count
        Write-Host "✓ $file : $lines lines, $size bytes"
    } else {
        Write-Host "✗ $file : NOT FOUND"
    }
}
```

### Inspecionar Conteúdo

```powershell
# Ver primeiras 3 linhas
Get-Content "output/emp_poc.csv" | Select-Object -First 3

# Saída esperada:
# XPK_employee,FK_employees,EMPLOYEE_ID,FIRST_NAME,LAST_NAME,SALARY,DEPARTMENT_ID
# 1,1,101,John,Smith,85000,1
# 2,1,102,Jane,Doe,90000,1
```

---

## 🖥️ Passo 4: Importar via UI (Recomendado)

### Método A: Drag & Drop (Mais Simples)

1. **Acesse o Lakehouse**
   - Workspace → informatica_poc_data
   - Clique em "Files" tab

2. **Arraste os Arquivos**
   ```
   Arraste para a área "Files":
   ├── output/emp_poc.csv
   └── output/hr_poc.csv
   ```

3. **Confirmação**
   ```
   Upload em progresso:
   ├── emp_poc.csv ... 100% ✓
   └── hr_poc.csv ... 100% ✓
   ```

4. **Verifique**
   ```
   Files/
   ├── emp_poc.csv  (uploaded)
   └── hr_poc.csv   (uploaded)
   ```

### Método B: Upload Via Botão

1. **No Lakehouse Files**
   - Clique em "Upload" button (topo)
   - Selecione "Upload files"

2. **Selecione os CSVs**
   - Browse para `output/emp_poc.csv`
   - Também adicione `output/hr_poc.csv`
   - Clique em "Upload"

3. **Aguarde Conclusão**
   - Barra de progresso = 100%
   - Status = "Upload complete"

---

## ⚙️ Passo 5: Importar via API (Automação)

### Usando Azure Storage Account

```powershell
# Script: Upload-ToFabricViaAPI.ps1

param(
    [string]$WorkspaceId,
    [string]$LakehouseId,
    [string]$FilePath,
    [string]$DestinationFolder = "Files"
)

# Autenticar com Bearer token
$token = (az account get-access-token --resource https://fabric.microsoft.com | ConvertFrom-Json).accessToken

# Upload via REST API
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/lakehouses/$LakehouseId/files"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/octet-stream"
}

$fileName = Split-Path -Leaf $FilePath
$fullUri = "$uri/$DestinationFolder/$fileName"

$response = Invoke-RestMethod -Uri $fullUri `
    -Method Put `
    -Headers $headers `
    -InFile $FilePath

Write-Host "Upload Status: $($response.status)"
```

### Usando Python + Fabric SDK

```python
# Dentro de Notebook Fabric

from pyspark.sql import SparkSession
import os

spark = SparkSession.builder.appName("FabricImport").getOrCreate()

# Carregar CSV
df_emp = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("/Workspace/informatica_poc_data/Files/emp_poc.csv")

df_hr = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("/Workspace/informatica_poc_data/Files/hr_poc.csv")

print(f"emp_poc: {df_emp.count()} rows")
print(f"hr_poc: {df_hr.count()} rows")
```

---

## ✅ Passo 6: Validar Dados

### Verificação Manual (UI)

1. **No Lakehouse**
   - Files → emp_poc.csv
   - Clique em "Preview"
   - Verifique:
     - ✓ Headers corretos
     - ✓ 8 linhas de dados
     - ✓ Sem caracteres corrompidos

2. **Repita para hr_poc.csv**
   - ✓ 8 linhas flattened
   - ✓ 9 colunas

### Verificação Automática (Notebook)

```python
# Notebook: Validate_Import.ipynb

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Carregar
df_emp = spark.read.csv("/Workspace/informatica_poc_data/Files/emp_poc.csv", header=True, inferSchema=True)
df_hr = spark.read.csv("/Workspace/informatica_poc_data/Files/hr_poc.csv", header=True, inferSchema=True)

# Validar
print("=== EMP_POC Validation ===")
print(f"Row Count: {df_emp.count()} (expected: 8)")
print(f"Column Count: {len(df_emp.columns)} (expected: 7)")
print(f"Columns: {df_emp.columns}")
print(f"Data Types:\n{df_emp.dtypes}")
print(f"Nulls: {df_emp.select([count(when(col(c).isNull(), c)) for c in df_emp.columns]).collect()}")

print("\n=== HR_POC Validation ===")
print(f"Row Count: {df_hr.count()} (expected: 8)")
print(f"Column Count: {len(df_hr.columns)} (expected: 9)")
print(f"Columns: {df_hr.columns}")
print(f"Nulls Check: {df_hr.select([count(when(col(c).isNull(), c)) for c in df_hr.columns]).collect()}")

# Mostrar amostra
df_emp.show(3)
df_hr.show(3)
```

**Output Esperado:**
```
=== EMP_POC Validation ===
Row Count: 8 (expected: 8) ✓
Column Count: 7 (expected: 7) ✓
Columns: ['XPK_employee', 'FK_employees', 'EMPLOYEE_ID', 'FIRST_NAME', 'LAST_NAME', 'SALARY', 'DEPARTMENT_ID']
Nulls: [0, 0, 0, 0, 0, 0, 0] ✓

=== HR_POC Validation ===
Row Count: 8 (expected: 8) ✓
Column Count: 9 (expected: 9) ✓
Nulls: [0, 0, 0, 0, 0, 0, 0, 0, 0] ✓
```

---

## 🗂️ Passo 7: Criar Tabelas Delta

### Via Notebook (Recomendado)

```python
# Notebook: Create_Delta_Tables.ipynb

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Carregar CSVs
df_emp = spark.read.csv("/Workspace/informatica_poc_data/Files/emp_poc.csv", header=True, inferSchema=True)
df_hr = spark.read.csv("/Workspace/informatica_poc_data/Files/hr_poc.csv", header=True, inferSchema=True)

# Criar tabelas Delta
df_emp.write.mode("overwrite").format("delta").option("path", "/lakehouse/default/Tables/emp_poc") \
    .saveAsTable("emp_poc")

df_hr.write.mode("overwrite").format("delta").option("path", "/lakehouse/default/Tables/hr_poc") \
    .saveAsTable("hr_poc")

print("✓ Tabelas Delta criadas")
print("  - emp_poc (8 rows, 7 columns)")
print("  - hr_poc (8 rows, 9 columns)")

# Consultar para validar
spark.sql("SELECT COUNT(*) as total FROM emp_poc").show()
spark.sql("SELECT COUNT(*) as total FROM hr_poc").show()
```

### Via Fabric Studio (SQL)

```sql
-- Dentro de SQL Editor no Fabric

-- Criar tabela EMP_POC
CREATE TABLE IF NOT EXISTS emp_poc (
    XPK_employee INT,
    FK_employees INT,
    EMPLOYEE_ID INT,
    FIRST_NAME STRING,
    LAST_NAME STRING,
    SALARY DOUBLE,
    DEPARTMENT_ID INT
)
USING DELTA
LOCATION '/lakehouse/default/Tables/emp_poc'

-- Criar tabela HR_POC
CREATE TABLE IF NOT EXISTS hr_poc (
    XPK_Department INT,
    DEPT_ID INT,
    DEPT_NAME STRING,
    XPK_Employee INT,
    FK_Department INT,
    EMP_ID INT,
    FIRST_NAME STRING,
    LAST_NAME STRING,
    SALARY DOUBLE
)
USING DELTA
LOCATION '/lakehouse/default/Tables/hr_poc'

-- Validar
SELECT COUNT(*) FROM emp_poc
SELECT COUNT(*) FROM hr_poc
```

---

## 🔍 Troubleshooting

### Problema 1: "File not found" ao fazer upload

**Causa:** Caminho incorreto ou arquivo não existe

**Solução:**
```powershell
# Verificar arquivo
Test-Path "output/emp_poc.csv"

# Se False, regenerar
.\run-informatica-poc.ps1 -WorkflowType all
```

### Problema 2: "Invalid file format" no import

**Causa:** CSV corrompido ou encoding errado

**Solução:**
```powershell
# Verificar encoding
$content = Get-Content "output/emp_poc.csv" -Encoding UTF8
# Re-salvar se necessário
$content | Out-File "output/emp_poc.csv" -Encoding UTF8
```

### Problema 3: "Access denied" ao fazer upload

**Causa:** Permissões insuficientes no Lakehouse

**Solução:**
1. Verifique se você é Owner/Admin do workspace
2. Tente criar novo Lakehouse com permissões full
3. Contacte Fabric admin se necessário

### Problema 4: Dados aparecem truncados

**Causa:** Tipos de dados mal inferidos

**Solução:**
```python
# Use inferSchema=False e especifique tipos
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

schema = StructType([
    StructField("XPK_employee", IntegerType()),
    StructField("FK_employees", IntegerType()),
    StructField("EMPLOYEE_ID", IntegerType()),
    StructField("FIRST_NAME", StringType()),
    StructField("LAST_NAME", StringType()),
    StructField("SALARY", DoubleType()),
    StructField("DEPARTMENT_ID", IntegerType())
])

df = spark.read.csv("/path/to/emp_poc.csv", schema=schema, header=True)
```

---

## 📊 Estrutura Final no Fabric

Após completar todos os passos:

```
Workspace: informatica-poc-workspace
│
├── Lakehouse: informatica_poc_data
│   │
│   ├── Files/
│   │   ├── emp_poc.csv
│   │   └── hr_poc.csv
│   │
│   ├── Tables/
│   │   ├── emp_poc (Delta table, 8 rows)
│   │   └── hr_poc (Delta table, 8 rows)
│   │
│   └── Shortcuts/
│       └── (external data sources, if needed)
│
├── Notebooks/
│   ├── 01_PowerCenter_to_PySpark_Translation
│   ├── 02_Workflow_Execution_EMP_and_HR
│   ├── Validate_Import
│   └── Create_Delta_Tables
│
└── Semantic Models/
    └── (Power BI models, if needed)
```

---

## ✨ Checklist Final

- [ ] Workspace Fabric criado
- [ ] Lakehouse criado
- [ ] emp_poc.csv uploaded
- [ ] hr_poc.csv uploaded
- [ ] Dados validados (8 + 8 registros)
- [ ] Tabelas Delta criadas
- [ ] Consultas SQL funcionando
- [ ] Notebooks importados (opcional)
- [ ] Documentação arquivada

---

## 📞 Próximos Passos

1. **Criar Dashboard** (Power BI)
   - Conectar ao Lakehouse
   - Visualizar emp_poc e hr_poc
   - Criar relatórios

2. **Automação Contínua**
   - Criar Pipeline Fabric
   - Agendar execuções diárias
   - Monitorar dados

3. **Otimização**
   - Particionar tabelas grandes
   - Criar índices
   - Tunar queries

4. **Integração com PowerCenter** (Opcional)
   - Migrar workflows restantes
   - Comparar dados entre sistemas
   - Planejar cutover

---

**Status:** ✅ PRONTO PARA IMPORT  
**Última Atualização:** 2026-06-16  
**Versão:** 1.0  

Para suporte: data-engineering@company.com
