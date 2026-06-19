# 🚀 Guia de Importação para Fabric (Sem MCP)

**Data:** 2026-06-19  
**Objetivo:** Importar notebooks de maps e pipelines de workflows para Microsoft Fabric  
**Status:** 📋 Pronto para Importação

---

## 📌 Resumo Executivo

| Item | Quantidade | Localização |
|------|-----------|------------|
| **Notebooks (Maps)** | 2 | `notebooks/03_*.py`, `notebooks/05_*.py` |
| **Pipelines (Workflows)** | 2 | `fabric_pipelines/*.json` |
| **Estrutura** | Hierárquica | Fabric Lakehouse nativo |
| **Dependências** | Spark/Fabric | Nativas, sem MCP |

---

## 🎯 Arquivos Criados

### 📓 Notebooks (PySpark - Maps)

#### 1️⃣ **Map EMP** (Simples)
```
notebooks/03_Map_EMP_Source_to_Target.py
├── Entrada: employees.xml
├── Saída: emp_poc_target (CSV)
├── Transformações: Flat (sem hierarquia)
├── Records: 8 employees
└── Tempo: ~5-10 segundos
```

**Funcionalidades:**
- ✓ Leitura XML com schema inference
- ✓ Transformação de tipos (ByteType → EMPLOYEE_ID)
- ✓ Validação de qualidade (nulos, duplicatas, salários válidos)
- ✓ Escrita CSV
- ✓ Criação de tabela Delta (opcional)

---

#### 2️⃣ **Map HR** (Hierárquico)
```
notebooks/05_Map_HR_Source_to_Target.py
├── Entrada: hr.xml (hierárquico: Department → Employees)
├── Saída: hr_poc_target (CSV flattened)
├── Transformações: Explode + Flatten
├── Records: 8 employees × 3 departments
└── Tempo: ~5-10 segundos
```

**Funcionalidades:**
- ✓ Leitura XML com estrutura aninhada
- ✓ Flatten de dados hierárquicos (explode)
- ✓ Validação de relacionamentos FK
- ✓ Sumarização por departamento
- ✓ Criação de tabelas Delta separadas

---

### 🔗 Pipelines (Workflows Orquestradores)

#### 1️⃣ **Pipeline EMP** (wf_m_poc_xml_emp)
```
fabric_pipelines/pipeline_wf_m_poc_xml_emp.json
├── Atividades: 6
│   ├── Start
│   ├── Execute_EMP_Map (Notebook)
│   ├── Validate_EMP_Data (Notebook)
│   ├── Handle_Error (Notebook)
│   ├── Success / Failed (End nodes)
├── Timeout: 1 hora
├── Retry: Até 3 tentativas
└── Status: Draft
```

**Fluxo:**
```
START
  ↓
[Execute EMP Map] ←→ SUCESSO
  ↓
[Validate Data]
  ↓
SUCCESS / ERRO → [Error Handler] → FAILED
```

---

#### 2️⃣ **Pipeline HR** (wf_m_poc_xml_hr)
```
fabric_pipelines/pipeline_wf_m_poc_xml_hr.json
├── Atividades: 7
│   ├── Start
│   ├── Execute_HR_Map (Notebook)
│   ├── Validate_HR_Data (Notebook - com check de hierarquia)
│   ├── Optional_Scale_to_10K (Notebook)
│   ├── Handle_Error (Notebook)
│   ├── Success / Failed (End nodes)
├── Timeout: 1 hora
├── Retry: Até 3 tentativas
└── Status: Draft
```

**Fluxo:**
```
START
  ↓
[Execute HR Map] ←→ SUCESSO
  ↓
[Validate Hierarchical Data]
  ↓
[Optional Scale 10K] (pode falhar sem impacto)
  ↓
SUCCESS / ERRO → [Error Handler] → FAILED
```

---

## ⚙️ Pré-Requisitos

### Necessário
- ✅ Acesso a Microsoft Fabric
- ✅ Workspace Fabric criado
- ✅ Lakehouse padrão (`/lakehouse/default/Files`)
- ✅ Arquivos de origem:
  - `employees.xml` → `/lakehouse/default/Files/`
  - `hr.xml` → `/lakehouse/default/Files/`
- ✅ Permissões de criação de notebooks e pipelines

### Opcional
- ⚠️ Power BI Desktop para análise posterior
- ⚠️ Git para versionamento

---

## 📥 PASSO 1: Preparar Arquivos de Origem

### 1.1 Upload de XML para Lakehouse

```powershell
# PowerShell: Upload arquivos para Lakehouse
$workspace = "seu-workspace-id"
$lakehouse = "seu-lakehouse-id"
$lakePath = "/Files"

# Upload employees.xml
az fabric item upload \
    --workspace-id $workspace \
    --lakehouse-id $lakehouse \
    --source-path "./employees.xml" \
    --dest-path "$lakePath/employees.xml"

# Upload hr.xml
az fabric item upload \
    --workspace-id $workspace \
    --lakehouse-id $lakehouse \
    --source-path "./hr.xml" \
    --dest-path "$lakePath/hr.xml"

Write-Host "✓ XMLs uploaded successfully"
```

### 1.2 Validar Arquivos (via Fabric UI)

1. Acesse seu **Workspace Fabric**
2. Clique em **Lakehouse** (seu lakehouse padrão)
3. Navegue para **Files**
4. Confirme que aparecem:
   - `employees.xml` ✓
   - `hr.xml` ✓

---

## 📓 PASSO 2: Importar Notebooks (Maps)

### Opção A: Via Portal Fabric (UI)

#### 2A.1 Criar Novo Notebook

1. **No seu Workspace Fabric**, clique em **+ New**
2. Selecione **Notebook**
3. Nomeie como: `03_Map_EMP_Source_to_Target`

#### 2A.2 Copiar Código

1. Abra o arquivo: `notebooks/03_Map_EMP_Source_to_Target.py`
2. Copie TODO o conteúdo (Ctrl+A → Ctrl+C)
3. Cola no notebook Fabric vazio
4. Clique em **Save** (Ctrl+S)

#### 2A.3 Repetir para HR Map

1. **+ New → Notebook**
2. Nome: `05_Map_HR_Source_to_Target`
3. Copie o código de `notebooks/05_Map_HR_Source_to_Target.py`
4. **Save**

---

### Opção B: Via API Fabric (Script)

```powershell
# PowerShell: Importar notebooks via API Fabric

$token = az account get-access-token --resource https://fabric.microsoft.com | ConvertFrom-Json
$headers = @{
    "Authorization" = "Bearer $($token.accessToken)"
    "Content-Type" = "application/json"
}

$workspaceId = "seu-workspace-id"

# Importar Notebook EMP
$empNotebookContent = Get-Content "notebooks/03_Map_EMP_Source_to_Target.py" -Raw
$createPayload = @{
    "displayName" = "03_Map_EMP_Source_to_Target"
    "definition" = @{
        "format" = "ipynb"
        "parts" = @(@{
            "path" = "notebook.ipynb"
            "payload" = $empNotebookContent
        })
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod `
    -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/notebooks" `
    -Method Post `
    -Headers $headers `
    -Body $createPayload

Write-Host "✓ EMP Notebook created: $($response.id)"

# Repetir para HR Notebook...
```

---

## 🔗 PASSO 3: Importar Pipelines (Workflows)

### Opção A: Via Portal Fabric (UI)

#### 3A.1 Criar Nova Pipeline

1. **No seu Workspace Fabric**, clique em **+ New**
2. Selecione **Data Pipeline**
3. Nomeie como: `wf_m_poc_xml_emp`

#### 3A.2 Importar Definição JSON

1. Clique em **Edit** na pipeline
2. Na barra lateral, clique em **{}** (View Code)
3. Substitua todo o conteúdo com o JSON de: `fabric_pipelines/pipeline_wf_m_poc_xml_emp.json`
4. Clique em **Apply**

#### 3A.3 Conectar Atividades aos Notebooks

1. Cada atividade do tipo "NotebookActivity" precisa apontar para o notebook correspondente
2. Clique em cada atividade e configure:
   - **Notebook Path:** Selecione `03_Map_EMP_Source_to_Target`
   - **Parameters:** {LAKEHOUSE_PATH, SOURCE_FILE, TARGET_LOCATION}

#### 3A.4 Repetir para HR Pipeline

1. **+ New → Data Pipeline**
2. Nome: `wf_m_poc_xml_hr`
3. Copie JSON de: `fabric_pipelines/pipeline_wf_m_poc_xml_hr.json`
4. Conecte atividades aos notebooks

---

### Opção B: Via API Fabric (Script)

```powershell
# PowerShell: Importar pipelines via API Fabric

$token = az account get-access-token --resource https://fabric.microsoft.com | ConvertFrom-Json
$headers = @{
    "Authorization" = "Bearer $($token.accessToken)"
    "Content-Type" = "application/json"
}

$workspaceId = "seu-workspace-id"

# Importar Pipeline EMP
$pipelineJson = Get-Content "fabric_pipelines/pipeline_wf_m_poc_xml_emp.json" | ConvertFrom-Json
$createPayload = @{
    "displayName" = "wf_m_poc_xml_emp"
    "definition" = $pipelineJson
} | ConvertTo-Json -Depth 20

$response = Invoke-RestMethod `
    -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/dataPipelines" `
    -Method Post `
    -Headers $headers `
    -Body $createPayload

Write-Host "✓ EMP Pipeline created: $($response.id)"

# Repetir para HR Pipeline...
```

---

## ✅ PASSO 4: Validar Setup

### 4.1 Checklist de Validação

```powershell
# Verificar estrutura no Fabric
Write-Host "📋 Validation Checklist"
Write-Host "=" * 60

# 1. Arquivos de origem
Write-Host "1. Source Files:"
Write-Host "   ☐ employees.xml exists in /Files"
Write-Host "   ☐ hr.xml exists in /Files"

# 2. Notebooks
Write-Host "2. Notebooks:"
Write-Host "   ☐ 03_Map_EMP_Source_to_Target created"
Write-Host "   ☐ 05_Map_HR_Source_to_Target created"

# 3. Pipelines
Write-Host "3. Pipelines:"
Write-Host "   ☐ wf_m_poc_xml_emp pipeline created"
Write-Host "   ☐ wf_m_poc_xml_hr pipeline created"

# 4. Conexões
Write-Host "4. Connections:"
Write-Host "   ☐ EMP pipeline → 03_Map_EMP notebook"
Write-Host "   ☐ HR pipeline → 05_Map_HR notebook"
Write-Host "   ☐ Validation notebooks linked"
Write-Host "   ☐ Error handlers configured"

Write-Host "=" * 60
```

### 4.2 Teste de Execução

#### Test 1: Executar Map EMP isoladamente

```powershell
# Via Fabric UI:
# 1. Abra notebook: 03_Map_EMP_Source_to_Target
# 2. Clique em "Run all"
# 3. Aguarde completar

# Resultado esperado:
# ✓ XML loaded: 8 records
# ✓ Transformations applied
# ✓ Data quality checks: PASSED
# ✓ Target CSV written
# ✓ SUCCESS
```

#### Test 2: Executar Map HR isoladamente

```powershell
# Via Fabric UI:
# 1. Abra notebook: 05_Map_HR_Source_to_Target
# 2. Clique em "Run all"
# 3. Aguarde completar

# Resultado esperado:
# ✓ Hierarchical XML loaded
# ✓ Flattened: 8 records (3 departments)
# ✓ Transformations applied
# ✓ Hierarchical validation: PASSED
# ✓ SUCCESS
```

#### Test 3: Executar Pipeline EMP

```powershell
# Via Fabric UI:
# 1. Abra pipeline: wf_m_poc_xml_emp
# 2. Clique em "Run"
# 3. Monitore progresso

# Etapas:
# [Start]
#   ↓
# [Execute_EMP_Map] ← aguarde 30s
#   ↓
# [Validate_EMP_Data] ← aguarde 15s
#   ↓
# [Success] ✓
```

#### Test 4: Executar Pipeline HR

```powershell
# Via Fabric UI:
# 1. Abra pipeline: wf_m_poc_xml_hr
# 2. Clique em "Run"
# 3. Monitore progresso

# Etapas:
# [Start]
#   ↓
# [Execute_HR_Map] ← aguarde 30s
#   ↓
# [Validate_HR_Data] ← aguarde 15s
#   ↓
# [Optional_Scale_10K] ← opcional, pode falhar sem impacto
#   ↓
# [Success] ✓
```

---

## 📊 PASSO 5: Validar Outputs

### 5.1 Verificar CSVs Gerados

```sql
-- Via Fabric SQL Editor

-- Visualizar EMP output
SELECT * FROM emp_poc_target 
ORDER BY EMPLOYEE_ID;

-- Visualizar HR output
SELECT DEPT_ID, DEPT_NAME, COUNT(*) as employee_count
FROM hr_poc_target
GROUP BY DEPT_ID, DEPT_NAME
ORDER BY DEPT_ID;
```

### 5.2 Verificar Tabelas Delta (se criadas)

```sql
-- Tabelas EMP
SELECT COUNT(*) FROM emp_poc;

-- Tabelas HR
SELECT COUNT(*) FROM hr_departments;
SELECT COUNT(*) FROM hr_employees;
```

### 5.3 Validação de Dados

| Item | EMP | HR |
|------|-----|-----|
| **Total Records** | 8 | 8 |
| **Departments** | N/A | 3 |
| **Duplicates** | 0 ✓ | 0 ✓ |
| **Nulls (key fields)** | 0 ✓ | 0 ✓ |
| **Salary Validation** | 100% ✓ | 100% ✓ |
| **FK Integrity** | N/A | 100% ✓ |

---

## 🔄 PASSO 6: Configurar Agendamento (Opcional)

### 6.1 Agendar Pipeline EMP

```powershell
# Via Fabric UI:
# 1. Abra pipeline: wf_m_poc_xml_emp
# 2. Clique em "Schedule"
# 3. Defina:
#    - Frequência: Diária
#    - Horário: 02:00 AM UTC
#    - Retry: 3 tentativas
# 4. Salve
```

### 6.2 Agendar Pipeline HR

```powershell
# Via Fabric UI:
# 1. Abra pipeline: wf_m_poc_xml_hr
# 2. Clique em "Schedule"
# 3. Defina:
#    - Frequência: Diária
#    - Horário: 02:30 AM UTC (após EMP)
#    - Retry: 3 tentativas
# 4. Salve
```

---

## 📁 ESTRUTURA FINAL (Fabric)

```
Workspace: seu-workspace
├── Notebooks
│   ├── 02_Workflow_Execution_EMP_and_HR (existente)
│   ├── 03_Map_EMP_Source_to_Target ✅ NOVO
│   ├── 04_PySpark_Large_Scale_Data_Generation (existente)
│   └── 05_Map_HR_Source_to_Target ✅ NOVO
│
├── Pipelines
│   ├── wf_m_poc_xml_emp ✅ NOVO
│   └── wf_m_poc_xml_hr ✅ NOVO
│
└── Lakehouse (default)
    └── /Files
        ├── employees.xml
        ├── hr.xml
        ├── emp_poc_target/ ← Output
        └── hr_poc_target/ ← Output
```

---

## 🚀 Próximos Passos

1. ✅ **Importar Notebooks** → Execute testes isolados
2. ✅ **Importar Pipelines** → Configure com os notebooks
3. ✅ **Testar Fluxo** → Execute ambas as pipelines
4. ✅ **Validar Dados** → Confirme outputs
5. ⚠️ **Agendar** → Configure rodadas automáticas (opcional)
6. 📈 **Monitorar** → Configurar alertas se necessário

---

## 📞 Troubleshooting

### Problema: Notebook não encontrado na pipeline
**Solução:** Na atividade "NotebookActivity", clique em "..." e selecione o notebook novamente

### Problema: XML não lido corretamente
**Solução:** Verifique que `employees.xml` e `hr.xml` estão em `/lakehouse/default/Files/`

### Problema: Erro de tipo de dados na transformação
**Solução:** Verifique que os XMLs têm o esquema esperado (EMPLOYEE_ID: byte, SALARY: short, etc.)

### Problema: Pipeline falha no erro handler
**Solução:** Verifique logs do notebook — clique na atividade falhada → "Output"

---

## ✨ Resumo

| Etapa | Status | Tempo |
|-------|--------|-------|
| Preparar XMLs | ⏱️ 2 min | Via upload UI |
| Importar 2 Notebooks | ⏱️ 5 min | Copy/paste ou API |
| Importar 2 Pipelines | ⏱️ 10 min | JSON UI ou API |
| Conectar Componentes | ⏱️ 5 min | Via UI |
| Testar Pipelines | ⏱️ 2 min | Run completos |
| **TOTAL** | **⏱️ ~25 min** | |

---

**🎉 Parabéns!** Seus workflows PowerCenter estão agora prontos para executar em Fabric!

