# 📚 Índice de Documentação — PowerCenter to Fabric

**Navegação completa para migração Informatica PowerCenter → Microsoft Fabric**

---

## 🚀 Início Rápido

### Para Usuários Novos

1. **[START_HERE.md](../START_HERE.md)** — Começe aqui! Fluxo manual passo a passo
2. **[README.md](../README.md)** — Visão geral do projeto e estrutura
3. **[QUICK_START_MCP_MIGRATION.md](QUICK_START_MCP_MIGRATION.md)** ⭐ **NOVO!** — Automação via MCP em 3 comandos

### Para Migração Automatizada (Recomendado)

- **[QUICK_START_MCP_MIGRATION.md](QUICK_START_MCP_MIGRATION.md)** — Quick start com MCP (10-15 min)
- **[FABRIC_MCP_MIGRATION_FLOW.md](FABRIC_MCP_MIGRATION_FLOW.md)** — Fluxo completo detalhado via MCP
- **Script:** `scripts/fabric_mcp_migration.py` — Automação Python end-to-end

### Para Migração Manual

- **[FABRIC_IMPORT_GUIDE.md](FABRIC_IMPORT_GUIDE.md)** — Guia completo (UI + API)
- **[FABRIC_QUICK_IMPORT_15MIN.md](FABRIC_QUICK_IMPORT_15MIN.md)** — Import rápido 15min
- **[FABRIC_IMPORT_GUIDE_NO_MCP.md](FABRIC_IMPORT_GUIDE_NO_MCP.md)** — Import sem MCP

---

## 📋 Por Categoria

### 🎯 Planejamento e Overview

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| [EXECUTIVE_SUMMARY.md](../EXECUTIVE_SUMMARY.md) | Sumário executivo do projeto | Para stakeholders / apresentações |
| [PROJECT_STATUS.md](../PROJECT_STATUS.md) | Status atual e métricas | Check-in rápido de progresso |
| [PROJECT_FORMALIZATION_COMPLETE.md](../PROJECT_FORMALIZATION_COMPLETE.md) | Formalização do projeto | Documentação formal |
| [BACKLOG.md](../BACKLOG.md) | Issues e épicos do projeto | Planejamento de sprints |

### 🔄 Migração para Fabric

#### Via MCP (Automatizado) ⭐

| Documento | Descrição | Tempo |
|-----------|-----------|-------|
| **[QUICK_START_MCP_MIGRATION.md](QUICK_START_MCP_MIGRATION.md)** | Quick start com MCP | 10-15 min |
| **[FABRIC_MCP_MIGRATION_FLOW.md](FABRIC_MCP_MIGRATION_FLOW.md)** | Fluxo completo detalhado | 30-45 min |
| Script: `fabric_mcp_migration.py` | Automação Python | Executável |

#### Via UI/API Manual

| Documento | Descrição | Tempo |
|-----------|-----------|-------|
| [FABRIC_IMPORT_GUIDE.md](FABRIC_IMPORT_GUIDE.md) | Guia completo (20-30 min) | 20-30 min |
| [FABRIC_QUICK_IMPORT_15MIN.md](FABRIC_QUICK_IMPORT_15MIN.md) | Import rápido | 15 min |
| [FABRIC_IMPORT_GUIDE_NO_MCP.md](FABRIC_IMPORT_GUIDE_NO_MCP.md) | Import sem MCP | 25 min |

#### Guias Complementares

| Documento | Descrição |
|-----------|-----------|
| [FABRIC_COMPLETE_INTEGRATION_INDEX.md](FABRIC_COMPLETE_INTEGRATION_INDEX.md) | Índice de integração completa |
| [FABRIC_E2E_COMPLETE.md](../FABRIC_E2E_COMPLETE.md) | Jornada E2E completa |
| [FABRIC_EXECUTIVE_SUMMARY.md](FABRIC_EXECUTIVE_SUMMARY.md) | Sumário executivo Fabric |

### 📓 Notebooks e Execução

| Documento | Descrição |
|-----------|-----------|
| [NOTEBOOK_EXECUTION_GUIDE.md](NOTEBOOK_EXECUTION_GUIDE.md) | Como executar notebooks no Fabric |
| [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) | Guia de execução geral |
| Notebook: `06_Pipeline_Import_Guide.ipynb` | Tutorial interativo |

### 🔧 Referências Técnicas

| Documento | Descrição |
|-----------|-----------|
| [POWERcenter_TO_PYSPARK_MAPPING.md](POWERcenter_TO_PYSPARK_MAPPING.md) | Mapeamento PowerCenter ↔ PySpark |
| [FABRIC_MAPS_PIPELINES_REFERENCE.md](FABRIC_MAPS_PIPELINES_REFERENCE.md) | Referência de pipelines |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Referência rápida |

### 🎯 Delivery e Setup

| Documento | Descrição |
|-----------|-----------|
| [DELIVERY_SUMMARY_FABRIC_INTEGRATION.md](DELIVERY_SUMMARY_FABRIC_INTEGRATION.md) | Sumário de entrega |
| [DELIVERY_CHECKLIST_FABRIC_INTEGRATION.md](DELIVERY_CHECKLIST_FABRIC_INTEGRATION.md) | Checklist de entrega |
| [README_FABRIC_INTEGRATION_DELIVERY.md](README_FABRIC_INTEGRATION_DELIVERY.md) | README de entrega |
| [README_FABRIC_SETUP.md](README_FABRIC_SETUP.md) | Setup do ambiente Fabric |
| [START_HERE_FABRIC_INTEGRATION.md](START_HERE_FABRIC_INTEGRATION.md) | Início da integração |

### 📊 Testes e Validação

| Documento | Descrição |
|-----------|-----------|
| [TEST_RESULTS.md](TEST_RESULTS.md) | Resultados de testes |
| [CORRECTION_ARM_TEMPLATE_FORMAT.md](../CORRECTION_ARM_TEMPLATE_FORMAT.md) | Correções de templates ARM |

### 🎯 Pipelines

| Diretório | Descrição |
|-----------|-----------|
| `pipelines/deliverables/` | ZIPs prontos para import |
| `pipelines/schemas/` | Schemas JSON dos pipelines |
| `pipelines/validation/` | Scripts de validação |
| `pipelines/reference/` | Documentação de referência |
| `pipelines/docs/` | Documentação adicional |

---

## 🎯 Fluxogramas de Decisão

### Como devo migrar?

```
┌─────────────────────────────────────┐
│ Você tem MCP configurado?           │
└─────────┬───────────────────────────┘
          │
    ┌─────┴─────┐
    │           │
   Sim         Não
    │           │
    │           ├──→ [FABRIC_IMPORT_GUIDE.md]
    │           │    (UI manual, 20-30 min)
    │           │
    │           └──→ [FABRIC_QUICK_IMPORT_15MIN.md]
    │                (Quick import, 15 min)
    │
    ├──→ [QUICK_START_MCP_MIGRATION.md] ⭐
    │    (Automação, 10-15 min)
    │
    └──→ [FABRIC_MCP_MIGRATION_FLOW.md]
         (Detalhes completos)
```

### Qual notebook executar?

```
┌─────────────────────────────────────┐
│ O que você quer fazer?              │
└─────────┬───────────────────────────┘
          │
    ┌─────┴─────────────────────┐
    │                            │
Aprender conversão         Executar workflows
    │                            │
    │                            ├──→ Notebook 02: Workflow Execution
    │                            │
    │                            ├──→ Notebook 03: Map EMP
    │                            │
    │                            └──→ Notebook 05: Map HR
    │
    ├──→ Notebook 01: Translation Guide
    │
    └──→ Notebook 06: Pipeline Import Guide
```

---

## 🔑 Arquivos Principais

### Scripts de Automação

| Script | Descrição | Uso |
|--------|-----------|-----|
| `scripts/fabric_mcp_migration.py` | Migração completa via MCP | `python scripts/fabric_mcp_migration.py` |
| `scripts/fabric-mcp-automation.ps1` | Automação PowerShell | `.\scripts\fabric-mcp-automation.ps1` |
| `scripts/setup_environment.py` | Setup do ambiente local | `python scripts/setup_environment.py` |
| `scripts/prepare-fabric-zip.ps1` | Preparar ZIPs para import | `.\scripts\prepare-fabric-zip.ps1` |
| `scripts/prepare-fabric-import.ps1` | Preparar import | `.\scripts\prepare-fabric-import.ps1` |

### Notebooks

| Notebook | Descrição | Tipo |
|----------|-----------|------|
| `01_PowerCenter_to_PySpark_Translation.ipynb` | Lógica de conversão | Educacional |
| `02_Workflow_Execution_EMP_and_HR.ipynb` | Execução de workflows | Operacional |
| `03_Map_EMP_Source_to_Target.ipynb` | Mapping EMP | Operacional |
| `04_PySpark_Large_Scale_Data_Generation.ipynb` | Geração 10K+ records | Testes |
| `05_Map_HR_Source_to_Target.ipynb` | Mapping HR | Operacional |
| `06_Pipeline_Import_Guide.ipynb` | Guia de import | Tutorial |

### Dados

| Arquivo | Descrição | Registros |
|---------|-----------|-----------|
| `data/employees.xml` | XML flat | 8 |
| `data/hr.xml` | XML hierárquico | 3 depts, 8 emp |
| `data/wf_m_poc_xml_emp.XML` | Workflow EMP | - |
| `data/wf_m_poc_xml_hr.XML` | Workflow HR | - |

---

## 🎯 Jornadas Recomendadas

### 1. Migração Rápida (Automatizada)

**Tempo:** 10-15 minutos  
**Pré-requisito:** MCP configurado

1. [QUICK_START_MCP_MIGRATION.md](QUICK_START_MCP_MIGRATION.md)
2. Execute: `python scripts/fabric_mcp_migration.py`
3. Verifique: `migration_report.json`
4. Explore: Workspace no portal Fabric

### 2. Migração Manual (Primeira Vez)

**Tempo:** 30-45 minutos  
**Pré-requisito:** Conta Fabric

1. [START_HERE.md](../START_HERE.md)
2. [FABRIC_IMPORT_GUIDE.md](FABRIC_IMPORT_GUIDE.md)
3. [NOTEBOOK_EXECUTION_GUIDE.md](NOTEBOOK_EXECUTION_GUIDE.md)
4. Validar outputs

### 3. Aprendizado Completo

**Tempo:** 2-3 horas  
**Pré-requisito:** Tempo para estudar

1. [README.md](../README.md)
2. [POWERcenter_TO_PYSPARK_MAPPING.md](POWERcenter_TO_PYSPARK_MAPPING.md)
3. Notebook `01_PowerCenter_to_PySpark_Translation.ipynb`
4. [FABRIC_MCP_MIGRATION_FLOW.md](FABRIC_MCP_MIGRATION_FLOW.md)
5. [FABRIC_E2E_COMPLETE.md](../FABRIC_E2E_COMPLETE.md)

### 4. Desenvolvimento e Extensão

**Tempo:** Variável  
**Pré-requisito:** Migração concluída

1. [FABRIC_MAPS_PIPELINES_REFERENCE.md](FABRIC_MAPS_PIPELINES_REFERENCE.md)
2. Customizar notebooks
3. Adicionar novos workflows
4. [BACKLOG.md](../BACKLOG.md) para ideias

---

## 📞 Suporte e Contribuição

- **Issues:** [GitHub Issues](https://github.com/juliopessan/powercenter-microsoft-fabric/issues)
- **PRs:** Bem-vindos! Veja [BACKLOG.md](../BACKLOG.md)
- **Dúvidas:** Abra uma Issue com tag `question`

---

## 🔄 Histórico de Atualizações

| Data | Mudança |
|------|---------|
| 2026-06-23 | ➕ Adicionado fluxo MCP automatizado |
| 2026-06-19 | 📝 Documentação completa Fabric E2E |
| 2026-06-18 | 🔧 Scripts de preparação e validação |
| 2026-06-17 | 📓 6 notebooks criados |

---

**Última atualização:** 2026-06-23  
**Versão:** 2.0  
**Mantenedor:** Julio Pessan
