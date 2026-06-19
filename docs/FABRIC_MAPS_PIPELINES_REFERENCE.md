# 🔑 Referência Rápida: Maps × Pipelines

**Criado:** 2026-06-19  
**Objetivo:** Mapear relacionamentos entre notebooks (maps) e pipelines (workflows)

---

## 📊 Matriz de Componentes

```
INFORMATICA PowerCenter
│
├── Workflow: wf_m_poc_xml_emp
│   ├── Session Task: Sesión_EMP
│   │   └── Map: EMP_Source_to_CSV
│   │       ├── SOURCE: employees.xml
│   │       └── TARGET: emp_poc.csv
│   └── Validation Task
│
└── Workflow: wf_m_poc_xml_hr
    ├── Session Task: Sesión_HR
    │   └── Map: HR_Source_to_CSV_Hierarchical
    │       ├── SOURCE: hr.xml (hierarchical)
    │       └── TARGET: hr_poc.csv (flattened)
    └── Validation Task

           ↓↓↓ TRADUZIDO PARA FABRIC ↓↓↓

MICROSOFT FABRIC
│
├── Pipeline: wf_m_poc_xml_emp
│   ├── Activity 1: Execute_EMP_Map
│   │   └── Notebook: 03_Map_EMP_Source_to_Target
│   │       ├── Lê: /lakehouse/default/Files/employees.xml
│   │       ├── Transforma: 8 registros
│   │       └── Escreve: /lakehouse/default/Files/emp_poc_target
│   ├── Activity 2: Validate_EMP_Data
│   │   └── Notebook: 02_Workflow_Execution_EMP_and_HR
│   └── Activity 3: Error_Handler (on failure)
│
└── Pipeline: wf_m_poc_xml_hr
    ├── Activity 1: Execute_HR_Map
    │   └── Notebook: 05_Map_HR_Source_to_Target
    │       ├── Lê: /lakehouse/default/Files/hr.xml (nested)
    │       ├── Transforma: Flatten de 8 employees × 3 depts
    │       └── Escreve: /lakehouse/default/Files/hr_poc_target
    ├── Activity 2: Validate_HR_Data (check hierarchy)
    │   └── Notebook: 02_Workflow_Execution_EMP_and_HR
    ├── Activity 3: Optional_Scale_10K
    │   └── Notebook: 04_PySpark_Large_Scale_Data_Generation
    └── Activity 4: Error_Handler (on failure)
```

---

## 🗂️ Mapeamento de Arquivos

### INPUT SOURCES

| Arquivo | Tipo | Localização | Registros | Estrutura |
|---------|------|-----------|-----------|-----------|
| `employees.xml` | XML | `/lakehouse/default/Files/` | 8 | Plana (1 nível) |
| `hr.xml` | XML | `/lakehouse/default/Files/` | 3 depts + 8 emps | Hierárquica (2 níveis) |

### NOTEBOOKS (Maps)

| Notebook | Map Name | Entrada | Saída | Tipo | Lógica |
|----------|----------|---------|-------|------|--------|
| `03_Map_EMP_Source_to_Target.py` | EMP_Source_to_CSV | employees.xml | emp_poc_target | Map | Simples (schema cast) |
| `05_Map_HR_Source_to_Target.py` | HR_Source_to_CSV_Hierarchical | hr.xml | hr_poc_target | Map | Complexo (explode + flatten) |

### PIPELINES (Workflows)

| Pipeline | Workflow Name | Atividades | Lógica | Timeout |
|----------|---------------|-----------|--------|---------|
| `wf_m_poc_xml_emp.json` | wf_m_poc_xml_emp | 3 (exec + validate + error) | Linear | 1h |
| `wf_m_poc_xml_hr.json` | wf_m_poc_xml_hr | 4 (exec + validate + scale + error) | Linear + opcional | 1h |

### OUTPUT TARGETS

| Target | Pipeline | Registros | Localização | Tipo | Tabela Delta |
|--------|----------|-----------|-----------|------|--------------|
| emp_poc_target | wf_m_poc_xml_emp | 8 | `/lakehouse/default/Files/` | CSV | `emp_poc` |
| hr_poc_target | wf_m_poc_xml_hr | 8 | `/lakehouse/default/Files/` | CSV | `hr_employees`, `hr_departments` |

---

## 🔗 Dependências Entre Componentes

```
📥 INPUTS
  │
  ├─ employees.xml
  │  └─→ 03_Map_EMP_Source_to_Target.py
  │      └─→ emp_poc_target (CSV)
  │          └─→ emp_poc (Delta Table)
  │
  └─ hr.xml
     └─→ 05_Map_HR_Source_to_Target.py
         └─→ hr_poc_target (CSV)
             ├─→ hr_employees (Delta Table)
             └─→ hr_departments (Delta Table)

🔄 ORCHESTRATION (Pipelines)

Pipeline: wf_m_poc_xml_emp
  ├─ [START]
  ├─ 03_Map_EMP_Source_to_Target (Notebook)
  │  └─ Produce: emp_poc_target
  ├─ Validation (Notebook: 02_*)
  │  └─ Consume: emp_poc_target
  ├─ [SUCCESS] or [ERROR HANDLER]
  └─ [END]

Pipeline: wf_m_poc_xml_hr
  ├─ [START]
  ├─ 05_Map_HR_Source_to_Target (Notebook)
  │  └─ Produce: hr_poc_target
  ├─ Validation (Notebook: 02_* + hierarchy check)
  │  └─ Consume: hr_poc_target
  ├─ Optional Scale 10K (Notebook: 04_*)
  │  └─ Produce: hr_poc_10k (if enabled)
  ├─ [SUCCESS] or [ERROR HANDLER]
  └─ [END]
```

---

## 📋 Configuração de Cada Notebook em Pipeline

### Pipeline: wf_m_poc_xml_emp

#### Activity 1: Execute_EMP_Map
```json
{
  "type": "NotebookActivity",
  "name": "Execute_EMP_Map",
  "notebookPath": "notebooks/03_Map_EMP_Source_to_Target",
  "parameters": {
    "LAKEHOUSE_PATH": "/lakehouse/default/Files",
    "SOURCE_FILE": "employees.xml",
    "TARGET_LOCATION": "emp_poc_target"
  },
  "timeout": "00:30:00"
}
```

#### Activity 2: Validate_EMP_Data
```json
{
  "type": "NotebookActivity",
  "name": "Validate_EMP_Data",
  "notebookPath": "notebooks/02_Workflow_Execution_EMP_and_HR",
  "parameters": {
    "workflow": "wf_m_poc_xml_emp",
    "validation_mode": "true"
  },
  "timeout": "00:15:00"
}
```

#### Activity 3: Handle_Error (on failure only)
```json
{
  "type": "NotebookActivity",
  "name": "Handle_Error",
  "notebookPath": "notebooks/02_Workflow_Execution_EMP_and_HR",
  "parameters": {
    "error_mode": "true",
    "workflow": "wf_m_poc_xml_emp"
  },
  "timeout": "00:10:00"
}
```

---

### Pipeline: wf_m_poc_xml_hr

#### Activity 1: Execute_HR_Map
```json
{
  "type": "NotebookActivity",
  "name": "Execute_HR_Map",
  "notebookPath": "notebooks/05_Map_HR_Source_to_Target",
  "parameters": {
    "LAKEHOUSE_PATH": "/lakehouse/default/Files",
    "SOURCE_FILE": "hr.xml",
    "TARGET_LOCATION": "hr_poc_target"
  },
  "timeout": "00:30:00"
}
```

#### Activity 2: Validate_HR_Data
```json
{
  "type": "NotebookActivity",
  "name": "Validate_HR_Data",
  "notebookPath": "notebooks/02_Workflow_Execution_EMP_and_HR",
  "parameters": {
    "workflow": "wf_m_poc_xml_hr",
    "validation_mode": "true",
    "check_hierarchy": "true"
  },
  "timeout": "00:15:00"
}
```

#### Activity 3: Optional_Scale_to_10K
```json
{
  "type": "NotebookActivity",
  "name": "Optional_Scale_to_10K",
  "notebookPath": "notebooks/04_PySpark_Large_Scale_Data_Generation",
  "parameters": {
    "scale_factor": "10000",
    "workflow": "wf_m_poc_xml_hr",
    "optional": "true"
  },
  "timeout": "00:20:00"
}
```

#### Activity 4: Handle_Error (on failure only)
```json
{
  "type": "NotebookActivity",
  "name": "Handle_Error",
  "notebookPath": "notebooks/02_Workflow_Execution_EMP_and_HR",
  "parameters": {
    "error_mode": "true",
    "workflow": "wf_m_poc_xml_hr"
  },
  "timeout": "00:10:00"
}
```

---

## ⏱️ Tempos de Execução Esperados

| Componente | Operação | Tempo Típico | Range |
|------------|----------|-------------|-------|
| **EMP Map** | Leitura XML | 2-3s | 1-5s |
| | Transformação | 1-2s | 1-3s |
| | Escrita CSV | 2-3s | 1-5s |
| | **Total** | **5-8s** | 3-13s |
| **HR Map** | Leitura XML | 2-3s | 1-5s |
| | Flatten + Transform | 3-5s | 2-8s |
| | Escrita CSV | 2-3s | 1-5s |
| | **Total** | **7-11s** | 4-18s |
| **EMP Validation** | Verificação | 2-3s | 1-5s |
| **HR Validation** | Verificação + Hierarquia | 3-5s | 2-8s |
| **Scale 10K** | Geração de dados | 10-20s | 5-30s |
| **Error Handler** | Logging + Report | 2-3s | 1-5s |

---

## 🎯 Fluxo Completo (Ambas Pipelines)

```
TEMPO: 0:00 → INICIO
        │
        ├─ [wf_m_poc_xml_emp] INICIA
        │  ├─ Execute_EMP_Map: 0:00-0:08 (8s)
        │  ├─ Validate_EMP_Data: 0:08-0:10 (2s)
        │  └─ [EMP FINALIZA: 0:10] ✓ SUCCESS
        │
        ├─ [wf_m_poc_xml_hr] INICIA (paralelo ou sequencial)
        │  ├─ Execute_HR_Map: 0:00-0:11 (11s)
        │  ├─ Validate_HR_Data: 0:11-0:15 (4s)
        │  ├─ Optional_Scale_10K: 0:15-0:25 (10s, opcional)
        │  └─ [HR FINALIZA: 0:25] ✓ SUCCESS
        │
        └─ [FIM: 0:25 (paralelo) ou 0:35 (sequencial)]

TEMPO TOTAL (paralelo): ~25s
TEMPO TOTAL (sequencial): ~35s
TEMPO TOTAL (com scale): ~45s
```

---

## 📝 Checklist de Validação Pós-Import

### Notebooks
- ☐ `03_Map_EMP_Source_to_Target` importado
- ☐ `05_Map_HR_Source_to_Target` importado
- ☐ Ambos executam sem erros (Run All)
- ☐ Outputs (emp_poc_target, hr_poc_target) criados

### Pipelines
- ☐ `wf_m_poc_xml_emp` pipeline criado
- ☐ `wf_m_poc_xml_hr` pipeline criado
- ☐ Todas atividades apontam para notebooks corretos
- ☐ Parâmetros configurados corretamente
- ☐ Conexões de sucesso/erro estabelecidas

### Execução
- ☐ EMP pipeline executa → SUCCESS
- ☐ HR pipeline executa → SUCCESS
- ☐ CSVs aparecem em /lakehouse/default/Files/
- ☐ Tabelas Delta são criadas (opcional)

### Dados
- ☐ emp_poc: 8 registros validados
- ☐ hr_poc: 8 registros flattened validados
- ☐ Nenhuma duplicata
- ☐ Integridade referencial em HR

---

## 🚀 Próximo Passo

👉 Consulte: **FABRIC_IMPORT_GUIDE_NO_MCP.md** para instruções passo-a-passo de importação

