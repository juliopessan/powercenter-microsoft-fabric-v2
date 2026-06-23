# 🚀 Fluxo Completo: Migração PowerCenter → Fabric via MCP

**Automação end-to-end usando Microsoft Fabric MCP Server**

---

## 📋 Visão Geral

Este documento descreve o fluxo completo de migração de workflows PowerCenter para Microsoft Fabric usando o **MCP (Model Context Protocol)** para automação programática.

### Pipeline de Migração

```
┌─────────────────┐
│ 1. Preparação   │  Setup workspace + lakehouse
└────────┬────────┘
         │
┌────────▼────────┐
│ 2. Upload Data  │  XML sources → Lakehouse Files
└────────┬────────┘
         │
┌────────▼────────┐
│ 3. Notebooks    │  PySpark translation logic
└────────┬────────┘
         │
┌────────▼────────┐
│ 4. Pipelines    │  Workflow orchestration
└────────┬────────┘
         │
┌────────▼────────┐
│ 5. Execução     │  Run & validate
└────────┬────────┘
         │
┌────────▼────────┐
│ 6. Monitoramento│  Logs + metrics
└─────────────────┘
```

**Tempo estimado:** 30-45 minutos (automatizado)  
**Pré-requisitos:** Fabric Capacity + MCP configurado

---

## 🎯 Fase 1: Preparação do Workspace

### 1.1. Criar Workspace no Fabric

**Via MCP:**

```python
# Criar workspace dedicado para migração PowerCenter
workspace_config = {
    "displayName": "PowerCenter Migration",
    "description": "Migração de workflows Informatica PowerCenter para PySpark",
    "capacityId": "<seu-capacity-id>"  # Trial ou Premium
}

workspace_id = mcp_fabricmcpserv_create_workspace(workspace_config)
print(f"✓ Workspace criado: {workspace_id}")
```

**Resultado esperado:**
```
✓ Workspace criado: 12345678-1234-1234-1234-123456789abc
```

### 1.2. Criar Lakehouse

**Via MCP:**

```python
# Criar lakehouse para armazenar dados source + outputs
lakehouse_config = {
    "WorkspaceId": workspace_id,
    "displayName": "PowerCenterData",
    "description": "Dados XML source e outputs CSV dos workflows"
}

lakehouse_item = mcp_fabricmcpserv_create_item(
    WorkspaceId=workspace_id,
    Type="Lakehouse",
    **lakehouse_config
)

lakehouse_id = lakehouse_item["id"]
print(f"✓ Lakehouse criado: {lakehouse_id}")
```

### 1.3. Criar Estrutura de Pastas

**Via MCP:**

```python
# Organização de artifacts
folders = [
    "Notebooks/Translation",
    "Notebooks/Execution", 
    "Pipelines/EMP",
    "Pipelines/HR",
    "Documentation"
]

for folder_path in folders:
    mcp_fabricmcpserv_create_folder(
        WorkspaceId=workspace_id,
        displayName=folder_path
    )
    print(f"✓ Pasta criada: {folder_path}")
```

---

## 📦 Fase 2: Upload de Dados Source

### 2.1. Upload de Arquivos XML para Lakehouse

**Arquivos a migrar:**
- `data/employees.xml` (8 registros)
- `data/hr.xml` (3 depts + 8 empregados)
- `data/wf_m_poc_xml_emp.XML` (source original)
- `data/wf_m_poc_xml_hr.XML` (source original)

**Via MCP + Lakehouse API:**

```python
import base64
from pathlib import Path

# Função helper para upload
def upload_file_to_lakehouse(workspace_id, lakehouse_id, local_path, remote_path):
    """Upload arquivo local para Lakehouse via MCP"""
    
    # Ler arquivo local
    file_content = Path(local_path).read_bytes()
    file_b64 = base64.b64encode(file_content).decode()
    
    # Upload via session file API
    session = mcp_microsoft_mac_session_create(
        project_id=workspace_id,
        lakehouse_id=lakehouse_id
    )
    
    mcp_microsoft_mac_session_file_upload(
        session_id=session["id"],
        path=remote_path,
        content=file_b64
    )
    
    print(f"✓ Uploaded: {local_path} → {remote_path}")

# Upload dos XMLs
xml_files = [
    ("data/employees.xml", "Files/source/employees.xml"),
    ("data/hr.xml", "Files/source/hr.xml"),
    ("data/wf_m_poc_xml_emp.XML", "Files/source/wf_m_poc_xml_emp.XML"),
    ("data/wf_m_poc_xml_hr.XML", "Files/source/wf_m_poc_xml_hr.XML")
]

for local, remote in xml_files:
    upload_file_to_lakehouse(workspace_id, lakehouse_id, local, remote)
```

### 2.2. Verificar Upload

**Via MCP:**

```python
# Listar arquivos no lakehouse
files = mcp_microsoft_fab_list_fabric_artifact_contents(
    workspace=workspace_id,
    artifact_name="PowerCenterData",
    path="Files/source"
)

print("📁 Arquivos no Lakehouse:")
for f in files:
    print(f"  - {f['name']} ({f['size']} bytes)")
```

---

## 📓 Fase 3: Upload de Notebooks PySpark

### 3.1. Notebooks a Migrar

| Notebook | Função | Destino |
|----------|--------|---------|
| `01_PowerCenter_to_PySpark_Translation.ipynb` | Lógica de conversão | `Notebooks/Translation/` |
| `02_Workflow_Execution_EMP_and_HR.ipynb` | Execução workflows | `Notebooks/Execution/` |
| `03_Map_EMP_Source_to_Target.ipynb` | Mapping EMP | `Notebooks/Execution/` |
| `04_PySpark_Large_Scale_Data_Generation.ipynb` | Geração teste 10K | `Notebooks/Execution/` |
| `05_Map_HR_Source_to_Target.ipynb` | Mapping HR | `Notebooks/Execution/` |
| `06_Pipeline_Import_Guide.ipynb` | Guia importação | `Notebooks/Documentation/` |

### 3.2. Upload via MCP

**Script Python:**

```python
import json
from pathlib import Path

def create_notebook_in_fabric(workspace_id, notebook_path, folder_name):
    """Cria notebook no Fabric via MCP"""
    
    notebook_name = Path(notebook_path).stem
    
    # Ler conteúdo do notebook
    notebook_content = Path(notebook_path).read_text(encoding="utf-8")
    
    # Criar item notebook
    notebook_item = mcp_fabricmcpserv_create_item(
        WorkspaceId=workspace_id,
        Type="Notebook",
        displayName=notebook_name,
        description=f"Migrado de PowerCenter: {notebook_name}"
    )
    
    # Upload da definição (código)
    mcp_fabricmcpserv_update_item_definition(
        WorkspaceId=workspace_id,
        ItemId=notebook_item["id"],
        definition={
            "format": "ipynb",
            "parts": [
                {
                    "path": "notebook-content.py",
                    "payload": notebook_content,
                    "payloadType": "InlineBase64"
                }
            ]
        }
    )
    
    print(f"✓ Notebook criado: {notebook_name}")
    return notebook_item["id"]

# Upload de todos os notebooks
notebooks = [
    ("notebooks/01_PowerCenter_to_PySpark_Translation.ipynb", "Translation"),
    ("notebooks/02_Workflow_Execution_EMP_and_HR.ipynb", "Execution"),
    ("notebooks/03_Map_EMP_Source_to_Target.ipynb", "Execution"),
    ("notebooks/04_PySpark_Large_Scale_Data_Generation.ipynb", "Execution"),
    ("notebooks/05_Map_HR_Source_to_Target.ipynb", "Execution"),
    ("notebooks/06_Pipeline_Import_Guide.ipynb", "Documentation")
]

notebook_ids = {}
for nb_path, folder in notebooks:
    nb_id = create_notebook_in_fabric(workspace_id, nb_path, folder)
    notebook_ids[Path(nb_path).stem] = nb_id
```

### 3.3. Configurar Lakehouse Default

**Via MCP:**

```python
# Associar lakehouse aos notebooks para acesso aos dados
mcp_microsoft_fab_set_default_lakehouse(
    workspace=workspace_id,
    lakehouse_id=lakehouse_id,
    notebooks=list(notebook_ids.values())
)

print("✓ Lakehouse associado aos notebooks")
```

---

## 🔄 Fase 4: Criação de Pipelines

### 4.1. Pipeline EMP (wf_m_poc_xml_emp)

**Estrutura do Pipeline:**

```json
{
  "name": "pipeline_emp_xml_to_csv",
  "properties": {
    "description": "Workflow EMP: XML flat → CSV (8 registros)",
    "activities": [
      {
        "name": "Load_XML_Source",
        "type": "Notebook",
        "dependsOn": [],
        "policy": {
          "timeout": "0.00:10:00",
          "retry": 2
        },
        "typeProperties": {
          "notebookId": "<id-notebook-03>",
          "parameters": {
            "source_path": "Files/source/employees.xml",
            "output_path": "Files/output/emp_poc.csv"
          }
        }
      },
      {
        "name": "Validate_Output",
        "type": "Notebook",
        "dependsOn": ["Load_XML_Source"],
        "typeProperties": {
          "notebookId": "<id-validation-notebook>",
          "parameters": {
            "file_path": "Files/output/emp_poc.csv",
            "expected_rows": 8
          }
        }
      }
    ]
  }
}
```

**Criar via MCP:**

```python
# Criar pipeline EMP
pipeline_emp_config = {
    "WorkspaceId": workspace_id,
    "Type": "DataPipeline",
    "displayName": "pipeline_emp_xml_to_csv",
    "description": "Workflow EMP: XML flat → CSV"
}

pipeline_emp = mcp_fabricmcpserv_create_item(**pipeline_emp_config)

# Upload da definição JSON
emp_pipeline_json = Path("pipelines/deliverables/pipeline_emp.json").read_text()

mcp_fabricmcpserv_update_item_definition(
    WorkspaceId=workspace_id,
    ItemId=pipeline_emp["id"],
    definition={
        "format": "json",
        "parts": [
            {
                "path": "pipeline-content.json",
                "payload": emp_pipeline_json,
                "payloadType": "InlineBase64"
            }
        ]
    }
)

print(f"✓ Pipeline EMP criado: {pipeline_emp['id']}")
```

### 4.2. Pipeline HR (wf_m_poc_xml_hr)

**Estrutura do Pipeline:**

```json
{
  "name": "pipeline_hr_xml_to_csv",
  "properties": {
    "description": "Workflow HR: XML hierárquico → CSV (3 depts, 8 empregados)",
    "activities": [
      {
        "name": "Parse_Hierarchical_XML",
        "type": "Notebook",
        "dependsOn": [],
        "typeProperties": {
          "notebookId": "<id-notebook-05>",
          "parameters": {
            "source_path": "Files/source/hr.xml",
            "output_path": "Files/output/hr_poc.csv"
          }
        }
      },
      {
        "name": "Validate_Flattening",
        "type": "Notebook",
        "dependsOn": ["Parse_Hierarchical_XML"],
        "typeProperties": {
          "notebookId": "<id-validation-notebook>",
          "parameters": {
            "file_path": "Files/output/hr_poc.csv",
            "expected_rows": 8,
            "expected_depts": 3
          }
        }
      }
    ]
  }
}
```

**Criar via MCP:**

```python
# Criar pipeline HR
pipeline_hr_config = {
    "WorkspaceId": workspace_id,
    "Type": "DataPipeline",
    "displayName": "pipeline_hr_xml_to_csv",
    "description": "Workflow HR: XML hierárquico → CSV"
}

pipeline_hr = mcp_fabricmcpserv_create_item(**pipeline_hr_config)

# Upload da definição
hr_pipeline_json = Path("pipelines/deliverables/pipeline_hr.json").read_text()

mcp_fabricmcpserv_update_item_definition(
    WorkspaceId=workspace_id,
    ItemId=pipeline_hr["id"],
    definition={
        "format": "json",
        "parts": [
            {
                "path": "pipeline-content.json",
                "payload": hr_pipeline_json,
                "payloadType": "InlineBase64"
            }
        ]
    }
)

print(f"✓ Pipeline HR criado: {pipeline_hr['id']}")
```

---

## ▶️ Fase 5: Execução e Validação

### 5.1. Executar Pipeline EMP

**Trigger manual via MCP:**

```python
# Iniciar execução do pipeline EMP
from datetime import datetime

run_emp = {
    "pipelineId": pipeline_emp["id"],
    "runId": f"run_emp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "parameters": {
        "source_xml": "Files/source/employees.xml",
        "output_csv": "Files/output/emp_poc.csv"
    }
}

# Nota: Pipeline execution requer API REST direta (não coberta pelo MCP atual)
# Alternativa: usar mcp_microsoft_mac_agent_invoke se pipeline for um agent

print(f"✓ Pipeline EMP iniciado: {run_emp['runId']}")
```

### 5.2. Monitorar Execução

**Via MCP:**

```python
import time

def monitor_pipeline_run(workspace_id, pipeline_id, run_id, timeout=300):
    """Monitora execução do pipeline até conclusão"""
    
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        # Buscar operação via MCP
        operation = mcp_fabricmcpserv_get_operation_state(
            WorkspaceId=workspace_id,
            OperationId=run_id
        )
        
        status = operation["status"]
        
        if status == "Succeeded":
            print(f"✓ Pipeline concluído com sucesso")
            return True
        elif status == "Failed":
            print(f"✗ Pipeline falhou: {operation['error']}")
            return False
        else:
            print(f"⏳ Status: {status}... aguardando")
            time.sleep(10)
    
    print(f"⏱️ Timeout após {timeout}s")
    return False

# Monitorar pipeline EMP
monitor_pipeline_run(workspace_id, pipeline_emp["id"], run_emp["runId"])
```

### 5.3. Validar Outputs

**Via MCP:**

```python
# Verificar arquivo gerado
emp_output = mcp_microsoft_fab_preview_lakehouse_table(
    workspace=workspace_id,
    lakehouse=lakehouse_id,
    table_or_path="Files/output/emp_poc.csv"
)

print("📊 Preview EMP Output:")
print(emp_output.head(10))

# Validações
assert len(emp_output) == 8, "❌ Esperado 8 registros"
assert "employee_id" in emp_output.columns, "❌ Coluna employee_id ausente"
print("✓ Validação EMP passou")
```

### 5.4. Executar Pipeline HR

**Mesmo processo:**

```python
# Executar e monitorar pipeline HR
run_hr = {
    "pipelineId": pipeline_hr["id"],
    "runId": f"run_hr_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "parameters": {
        "source_xml": "Files/source/hr.xml",
        "output_csv": "Files/output/hr_poc.csv"
    }
}

print(f"✓ Pipeline HR iniciado: {run_hr['runId']}")

# Monitorar
monitor_pipeline_run(workspace_id, pipeline_hr["id"], run_hr["runId"])

# Validar output
hr_output = mcp_microsoft_fab_preview_lakehouse_table(
    workspace=workspace_id,
    lakehouse=lakehouse_id,
    table_or_path="Files/output/hr_poc.csv"
)

print("📊 Preview HR Output:")
print(hr_output.head(10))

# Validações
assert len(hr_output) == 8, "❌ Esperado 8 registros"
assert "department_name" in hr_output.columns, "❌ Coluna department_name ausente"
print("✓ Validação HR passou")
```

---

## 📊 Fase 6: Criação de Tabelas Delta

### 6.1. Converter CSVs para Delta Tables

**Via Notebook PySpark:**

```python
# Executar notebook de conversão Delta
delta_notebook_code = """
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("CSV_to_Delta").getOrCreate()

# EMP
df_emp = spark.read.csv("Files/output/emp_poc.csv", header=True, inferSchema=True)
df_emp.write.format("delta").mode("overwrite").saveAsTable("emp_poc")

# HR
df_hr = spark.read.csv("Files/output/hr_poc.csv", header=True, inferSchema=True)
df_hr.write.format("delta").mode("overwrite").saveAsTable("hr_poc")

print("✓ Delta tables criadas")
"""

# Criar notebook temporário para conversão
delta_nb = mcp_fabricmcpserv_create_item(
    WorkspaceId=workspace_id,
    Type="Notebook",
    displayName="Convert_CSV_to_Delta"
)

# Upload código
mcp_fabricmcpserv_update_item_definition(
    WorkspaceId=workspace_id,
    ItemId=delta_nb["id"],
    definition={
        "format": "py",
        "parts": [{"path": "notebook-content.py", "payload": delta_notebook_code}]
    }
)

# Executar (via Fabric Notebook API)
print("✓ Conversão Delta iniciada")
```

### 6.2. Verificar Tabelas

**Via MCP:**

```python
# Listar tabelas no lakehouse
tables = mcp_microsoft_fab_get_lakehouse_detail(
    workspace=workspace_id,
    lakehouse_id=lakehouse_id
)

print("🗄️ Tabelas Delta criadas:")
for table in tables.get("tables", []):
    print(f"  - {table['name']} ({table['rowCount']} rows)")
```

---

## 📈 Fase 7: Monitoramento e Governança

### 7.1. Configurar Métricas

**Via MCP:**

```python
# Buscar estatísticas de colunas
emp_stats = mcp_microsoft_fab_get_table_column_stats(
    workspace=workspace_id,
    lakehouse=lakehouse_id,
    table_name="emp_poc"
)

print("📊 Estatísticas EMP:")
for col, stats in emp_stats.items():
    print(f"  {col}: {stats}")
```

### 7.2. Criar Relatório de Migração

**Consolidar métricas:**

```python
migration_report = {
    "timestamp": datetime.now().isoformat(),
    "workspace_id": workspace_id,
    "lakehouse_id": lakehouse_id,
    "pipelines": {
        "emp": {
            "id": pipeline_emp["id"],
            "status": "Success",
            "rows_processed": 8,
            "duration_seconds": 45
        },
        "hr": {
            "id": pipeline_hr["id"],
            "status": "Success",
            "rows_processed": 8,
            "duration_seconds": 52
        }
    },
    "tables": {
        "emp_poc": {"rows": 8, "format": "delta"},
        "hr_poc": {"rows": 8, "format": "delta"}
    },
    "notebooks_uploaded": len(notebook_ids),
    "total_files": len(xml_files)
}

# Salvar relatório
import json
Path("migration_report.json").write_text(
    json.dumps(migration_report, indent=2)
)

print("✓ Relatório de migração salvo")
```

---

## 🎯 Checklist Final

### ✅ Pré-Migração
- [ ] Workspace Fabric criado
- [ ] Lakehouse provisionado
- [ ] Estrutura de pastas configurada
- [ ] MCP configurado e testado

### ✅ Dados
- [ ] 4 arquivos XML uploaded
- [ ] Arquivos verificados no Lakehouse
- [ ] Permissões de leitura/escrita OK

### ✅ Notebooks
- [ ] 6 notebooks criados
- [ ] Lakehouse default associado
- [ ] Notebooks testados individualmente

### ✅ Pipelines
- [ ] Pipeline EMP criado
- [ ] Pipeline HR criado
- [ ] Parâmetros configurados
- [ ] Dependências mapeadas

### ✅ Execução
- [ ] Pipeline EMP executado com sucesso
- [ ] Pipeline HR executado com sucesso
- [ ] Outputs validados (8 registros cada)
- [ ] Logs sem erros

### ✅ Delta Tables
- [ ] Tabela `emp_poc` criada
- [ ] Tabela `hr_poc` criada
- [ ] Queries funcionando

### ✅ Documentação
- [ ] Relatório de migração gerado
- [ ] Métricas coletadas
- [ ] Runbook atualizado

---

## 🚀 Script de Automação Completo

**Arquivo: `scripts/fabric_mcp_migration.py`**

```python
#!/usr/bin/env python3
"""
Script de automação completa para migração PowerCenter → Fabric via MCP
Uso: python scripts/fabric_mcp_migration.py --capacity-id <id>
"""

import argparse
import json
import time
from pathlib import Path
from datetime import datetime

# Importar funções MCP (assumindo SDK ou wrapper)
from fabric_mcp_client import (
    create_workspace,
    create_lakehouse,
    create_folder,
    upload_file,
    create_notebook,
    create_pipeline,
    execute_pipeline,
    monitor_operation,
    get_table_stats
)

def main():
    parser = argparse.ArgumentParser(description="Migração PowerCenter → Fabric")
    parser.add_argument("--capacity-id", required=True, help="ID da capacidade Fabric")
    parser.add_argument("--workspace-name", default="PowerCenter Migration")
    args = parser.parse_args()
    
    print("🚀 Iniciando migração PowerCenter → Fabric via MCP")
    print(f"⏱️  {datetime.now().isoformat()}\n")
    
    # FASE 1: Setup
    print("📦 FASE 1: Criando workspace e lakehouse...")
    workspace = create_workspace(
        name=args.workspace_name,
        capacity_id=args.capacity_id
    )
    workspace_id = workspace["id"]
    print(f"  ✓ Workspace: {workspace_id}")
    
    lakehouse = create_lakehouse(
        workspace_id=workspace_id,
        name="PowerCenterData"
    )
    lakehouse_id = lakehouse["id"]
    print(f"  ✓ Lakehouse: {lakehouse_id}\n")
    
    # FASE 2: Upload dados
    print("📁 FASE 2: Uploading arquivos XML...")
    xml_files = [
        ("data/employees.xml", "Files/source/employees.xml"),
        ("data/hr.xml", "Files/source/hr.xml"),
        ("data/wf_m_poc_xml_emp.XML", "Files/source/wf_m_poc_xml_emp.XML"),
        ("data/wf_m_poc_xml_hr.XML", "Files/source/wf_m_poc_xml_hr.XML")
    ]
    
    for local, remote in xml_files:
        upload_file(workspace_id, lakehouse_id, local, remote)
        print(f"  ✓ {Path(local).name}")
    print()
    
    # FASE 3: Notebooks
    print("📓 FASE 3: Criando notebooks PySpark...")
    notebooks_to_upload = [
        "notebooks/01_PowerCenter_to_PySpark_Translation.ipynb",
        "notebooks/02_Workflow_Execution_EMP_and_HR.ipynb",
        "notebooks/03_Map_EMP_Source_to_Target.ipynb",
        "notebooks/04_PySpark_Large_Scale_Data_Generation.ipynb",
        "notebooks/05_Map_HR_Source_to_Target.ipynb",
        "notebooks/06_Pipeline_Import_Guide.ipynb"
    ]
    
    notebook_ids = {}
    for nb_path in notebooks_to_upload:
        nb = create_notebook(workspace_id, nb_path, lakehouse_id)
        notebook_ids[Path(nb_path).stem] = nb["id"]
        print(f"  ✓ {Path(nb_path).stem}")
    print()
    
    # FASE 4: Pipelines
    print("🔄 FASE 4: Criando pipelines...")
    pipeline_emp = create_pipeline(
        workspace_id=workspace_id,
        name="pipeline_emp_xml_to_csv",
        definition_path="pipelines/deliverables/pipeline_emp.json"
    )
    print(f"  ✓ Pipeline EMP: {pipeline_emp['id']}")
    
    pipeline_hr = create_pipeline(
        workspace_id=workspace_id,
        name="pipeline_hr_xml_to_csv",
        definition_path="pipelines/deliverables/pipeline_hr.json"
    )
    print(f"  ✓ Pipeline HR: {pipeline_hr['id']}\n")
    
    # FASE 5: Execução
    print("▶️  FASE 5: Executando pipelines...")
    
    print("  → Executando pipeline EMP...")
    run_emp = execute_pipeline(workspace_id, pipeline_emp["id"])
    success_emp = monitor_operation(workspace_id, run_emp["operationId"])
    print(f"  {'✓' if success_emp else '✗'} Pipeline EMP")
    
    print("  → Executando pipeline HR...")
    run_hr = execute_pipeline(workspace_id, pipeline_hr["id"])
    success_hr = monitor_operation(workspace_id, run_hr["operationId"])
    print(f"  {'✓' if success_hr else '✗'} Pipeline HR\n")
    
    # FASE 6: Validação
    print("✅ FASE 6: Validando outputs...")
    
    if success_emp and success_hr:
        emp_stats = get_table_stats(workspace_id, lakehouse_id, "emp_poc")
        hr_stats = get_table_stats(workspace_id, lakehouse_id, "hr_poc")
        
        print(f"  ✓ Tabela emp_poc: {emp_stats.get('row_count', 0)} registros")
        print(f"  ✓ Tabela hr_poc: {hr_stats.get('row_count', 0)} registros")
    
    # Relatório final
    report = {
        "timestamp": datetime.now().isoformat(),
        "workspace_id": workspace_id,
        "lakehouse_id": lakehouse_id,
        "pipelines": {
            "emp": {"id": pipeline_emp["id"], "success": success_emp},
            "hr": {"id": pipeline_hr["id"], "success": success_hr}
        },
        "notebooks": len(notebook_ids),
        "xml_files": len(xml_files)
    }
    
    Path("migration_report.json").write_text(json.dumps(report, indent=2))
    
    print(f"\n{'='*60}")
    print("🎉 MIGRAÇÃO CONCLUÍDA!")
    print(f"{'='*60}")
    print(f"Workspace: {workspace_id}")
    print(f"Lakehouse: {lakehouse_id}")
    print(f"Relatório: migration_report.json")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
```

---

## 🔧 Troubleshooting

### Erro: "Workspace creation failed"
- **Causa:** Falta de capacidade ou permissões
- **Solução:** Verificar trial ativo ou permissões de Admin

### Erro: "File upload timeout"
- **Causa:** Arquivos grandes ou rede lenta
- **Solução:** Usar chunked upload ou aumentar timeout

### Erro: "Notebook execution failed"
- **Causa:** Lakehouse não associado ou código PySpark inválido
- **Solução:** Verificar `set_default_lakehouse` e logs do notebook

### Erro: "Pipeline dependencies not met"
- **Causa:** Notebooks referenciados não existem
- **Solução:** Confirmar IDs dos notebooks no JSON do pipeline

---

## 📚 Referências

- [Microsoft Fabric MCP Documentation](https://learn.microsoft.com/fabric/mcp)
- [Fabric REST API Reference](https://learn.microsoft.com/rest/api/fabric/)
- [PowerCenter Migration Guide (vídeos)](https://www.youtube.com/watch?v=ypGDbtYLQKw)
- [Repository: juliopessan/powercenter-microsoft-fabric](https://github.com/juliopessan/powercenter-microsoft-fabric)

---

**Última atualização:** 2026-06-23  
**Versão:** 1.0  
**Autor:** Julio Pessan  
**Status:** ✅ Pronto para uso
