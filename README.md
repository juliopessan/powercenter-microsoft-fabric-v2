# PowerCenter to Microsoft Fabric - V2 🚀

> **Migração automatizada e escalável de workflows Informatica PowerCenter para Microsoft Fabric com PySpark nativo e automação via MCP Server**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()
[![Tests](https://img.shields.io/badge/Tests-7%2F7%20Passing-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)]()
[![Fabric](https://img.shields.io/badge/Microsoft%20Fabric-Compatible-orange)]()

**Última Atualização:** 2026-06-23  
**Versão:** 2.0.0

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [O Que Este Projeto Faz](#-o-que-este-projeto-faz)
- [Novidades da V2](#-novidades-da-v2)
- [Início Rápido](#-início-rápido)
  - [Opção A: Migração Automatizada via MCP](#-opção-a-migração-automatizada-via-mcp-recomendado)
  - [Opção B: Fluxo Manual Guiado](#-opção-b-fluxo-manual-guiado)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Documentação Completa](#-documentação-completa)
- [Testes e Validação](#-testes-e-validação)
- [Resultados de Execução](#-resultados-de-execução)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Visão Geral

Este projeto fornece uma solução completa e automatizada para migrar workflows do **Informatica PowerCenter** para **Microsoft Fabric**, incluindo:

- ✅ **Tradução automática** de mappings PowerCenter → PySpark
- ✅ **Notebooks Fabric prontos** para execução
- ✅ **Pipelines de automação** via MCP Server
- ✅ **Testes automatizados** com harness de validação (7/7 specs)
- ✅ **Geração de dados em escala** (datasets de 10k+ registros)
- ✅ **Documentação executiva e técnica** completa

---

## 🔍 O Que Este Projeto Faz

Transforma dois workflows PowerCenter Informatica em pipelines nativos do Microsoft Fabric:

| Workflow | Tipo | Fonte | Destino | Notebooks |
|---|---|---|---|---|
| `wf_m_poc_xml_emp` | XML flat | `employees.xml` (8 registros) | `emp_poc.csv` | `03_Map_EMP_Source_to_Target.ipynb` |
| `wf_m_poc_xml_hr` | XML hierárquico | `hr.xml` (3 depts / 8 empregados) | `hr.csv` | `05_Map_HR_Source_to_Target.ipynb` |

### Vídeos de Referência
- [Flat XML Processing](https://www.youtube.com/watch?v=ypGDbtYLQKw)
- [Hierarchical XML Processing](https://www.youtube.com/watch?v=0aKBhwFPE-Y)

---

## 🆕 Novidades da V2

### 🔧 Automação Completa via MCP
- **Microsoft Fabric MCP Server Integration** para criação automatizada de workspaces, lakehouses, notebooks e pipelines
- Script de migração completo: `scripts/fabric_mcp_migration.py`
- Suporte para execução via VS Code: `scripts/fabric_mcp_migration_vscode.py`

### 📊 Relatórios e Monitoramento
- Geração automática de relatórios de migração em JSON
- Logs detalhados de cada etapa do processo
- Checkpoint system para retomada de execução

### 📚 Documentação Expandida
- **6 novos guias** adicionados em `docs/`:
  - `QUICK_START_MCP_MIGRATION.md` - Início rápido com MCP
  - `FABRIC_MCP_MIGRATION_FLOW.md` - Fluxo detalhado da migração
  - `MIGRATION_EXECUTION_SUMMARY.md` - Resumo da última execução
  - `ARCHITECTURE_DIAGRAMS.md` - Diagramas de arquitetura
  - `CHECKPOINT_MCP_MIGRATION.md` - Sistema de checkpoints
  - `DOCUMENTATION_INDEX.md` - Índice navegável

### 🧪 Testes Robustos
- Suite de testes com harness automatizado (7/7 specs passando)
- Pre-commit hooks para validação automática
- Relatórios de teste em múltiplos formatos (JSON, HTML)

### 📦 Pipelines Fabric
- Schemas ARM validados
- Templates de pipeline prontos para import
- Documentação de referência para cada componente

---

## 🚀 Início Rápido

### ⚡ Opção A: Migração Automatizada via MCP (RECOMENDADO)

**Migração completa em 10-15 minutos** usando Microsoft Fabric MCP Server.

#### Pré-requisitos
- Python 3.11+
- Azure CLI configurado (`az login`)
- Workspace Fabric ou capacidade Premium/Trial disponível

#### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/juliopessan/powercenter-microsoft-fabric-v2.git
cd powercenter-microsoft-fabric-v2

# 2. Instale as dependências
python scripts/setup_environment.py

# 3. Autentique no Azure
az login

# 4. Execute a migração automatizada
python scripts/fabric_mcp_migration.py --workspace-name "PowerCenter Migration V2"
```

#### Resultado Esperado
- ✅ Workspace Fabric criado
- ✅ Relatório JSON gerado em `output/migration_report_mcp_*.json`
- ✅ Logs detalhados em `logs/`
- ⚠️ Passos manuais documentados (se necessário devido a limitações de API)

**Documentação Completa:** [`docs/QUICK_START_MCP_MIGRATION.md`](docs/QUICK_START_MCP_MIGRATION.md)

---

### 📘 Opção B: Fluxo Manual Guiado

Para entender cada etapa do processo de migração:

#### 1. Setup Inicial

```bash
# Clone e prepare o ambiente
git clone https://github.com/juliopessan/powercenter-microsoft-fabric-v2.git
cd powercenter-microsoft-fabric-v2

# Setup automático (valida Python, instala pacotes, cria .env)
python scripts/setup_environment.py
```

#### 2. Configurar Credenciais

```bash
# Copie o template (se necessário)
cp .env.example .env

# Edite com suas credenciais Azure/Fabric
# Nota: .env está no .gitignore e nunca será commitado
```

#### 3. Validar Ambiente

```bash
# Instalar pre-commit hooks
python scripts/install_hooks.py

# Executar suite de testes
python -m harness.runner
```

#### 4. Explorar Notebooks

Abra o VS Code e navegue pelos notebooks em ordem:

1. **`01_PowerCenter_to_PySpark_Translation.ipynb`** - Tradução dos mappings
2. **`02_Workflow_Execution_EMP_and_HR.ipynb`** - Execução dos workflows
3. **`03_Map_EMP_Source_to_Target.ipynb`** - Processamento EMP
4. **`04_PySpark_Large_Scale_Data_Generation.ipynb`** - Geração de dados em escala
5. **`05_Map_HR_Source_to_Target.ipynb`** - Processamento HR
6. **`06_Pipeline_Import_Guide.ipynb`** - Importação de pipelines

#### 5. Importar para Fabric

Consulte: [`docs/FABRIC_IMPORT_GUIDE.md`](docs/FABRIC_IMPORT_GUIDE.md)

---

## 📁 Estrutura do Projeto

```
powercenter-microsoft-fabric-v2/
│
├── 📄 README.md                    # Este arquivo
├── 📄 PROJECT.md                   # Visão geral do projeto
├── 📄 EXECUTIVE_SUMMARY.md         # Resumo executivo
├── 📄 BACKLOG.md                   # Backlog de features
│
├── 📂 notebooks/                   # Notebooks Jupyter/Fabric
│   ├── 01_PowerCenter_to_PySpark_Translation.ipynb
│   ├── 02_Workflow_Execution_EMP_and_HR.ipynb
│   ├── 03_Map_EMP_Source_to_Target.ipynb
│   ├── 04_PySpark_Large_Scale_Data_Generation.ipynb
│   ├── 05_Map_HR_Source_to_Target.ipynb
│   └── 06_Pipeline_Import_Guide.ipynb
│
├── 📂 scripts/                     # Scripts de automação
│   ├── setup_environment.py        # Setup inicial automatizado
│   ├── fabric_mcp_migration.py     # Migração via MCP Server
│   ├── fabric_mcp_migration_vscode.py  # Migração via VS Code
│   ├── generate_10k_demo.py        # Geração de dados em escala
│   ├── install_hooks.py            # Instalação de pre-commit hooks
│   └── prepare-fabric-zip.ps1      # Preparação de pacotes Fabric
│
├── 📂 data/                        # Dados de entrada
│   ├── employees.xml               # XML flat (8 registros)
│   ├── hr.xml                      # XML hierárquico (3 depts)
│   ├── wf_m_poc_xml_emp.XML        # Workflow EMP original
│   └── wf_m_poc_xml_hr.XML         # Workflow HR original
│
├── 📂 output/                      # Resultados de execução
│   ├── emp_poc.csv                 # Saída EMP
│   ├── hr.csv                      # Saída HR
│   ├── migration_report_mcp_*.json # Relatórios de migração
│   └── hr_poc_10k/                 # Dados em escala
│
├── 📂 pipelines/                   # Pipelines Fabric
│   ├── deliverables/               # ARM templates prontos
│   ├── schemas/                    # Schemas de pipeline
│   ├── validation/                 # Scripts de validação
│   └── docs/                       # Documentação de pipelines
│
├── 📂 docs/                        # Documentação completa
│   ├── QUICK_START_MCP_MIGRATION.md
│   ├── FABRIC_MCP_MIGRATION_FLOW.md
│   ├── MIGRATION_EXECUTION_SUMMARY.md
│   ├── ARCHITECTURE_DIAGRAMS.md
│   ├── CHECKPOINT_MCP_MIGRATION.md
│   ├── DOCUMENTATION_INDEX.md
│   ├── FABRIC_IMPORT_GUIDE.md
│   ├── EXECUTION_GUIDE.md
│   ├── TEST_RESULTS.md
│   └── [+ 10 outros documentos]
│
├── 📂 harness/                     # Suite de testes
│   ├── runner.py                   # Test runner
│   ├── report.py                   # Gerador de relatórios
│   └── specs/                      # Especificações de teste
│
├── 📂 test-reports/                # Relatórios de testes
│   └── harness_report_*.json
│
└── 📂 logs/                        # Logs de execução
    └── *.log
```

---

## 📚 Documentação Completa

### Guias de Início Rápido
- [QUICK_START_MCP_MIGRATION.md](docs/QUICK_START_MCP_MIGRATION.md) - Migração automatizada em 15min
- [QUICK_START_FABRIC_IMPORT.md](docs/QUICK_START_FABRIC_IMPORT.md) - Import rápido via UI

### Documentação Técnica
- [FABRIC_MCP_MIGRATION_FLOW.md](docs/FABRIC_MCP_MIGRATION_FLOW.md) - Fluxo detalhado da migração
- [ARCHITECTURE_DIAGRAMS.md](docs/ARCHITECTURE_DIAGRAMS.md) - Arquitetura e diagramas
- [POWERcenter_TO_PYSPARK_MAPPING.md](docs/POWERcenter_TO_PYSPARK_MAPPING.md) - Mapeamento de transformações

### Guias de Execução
- [EXECUTION_GUIDE.md](docs/EXECUTION_GUIDE.md) - Guia completo de execução
- [NOTEBOOK_EXECUTION_GUIDE.md](docs/NOTEBOOK_EXECUTION_GUIDE.md) - Como executar os notebooks
- [FABRIC_IMPORT_GUIDE.md](docs/FABRIC_IMPORT_GUIDE.md) - Importação para Fabric

### Referências
- [MIGRATION_EXECUTION_SUMMARY.md](docs/MIGRATION_EXECUTION_SUMMARY.md) - Resumo da última execução (2026-06-23)
- [DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) - Índice completo de docs
- [DELIVERY_CHECKLIST_FABRIC_INTEGRATION.md](docs/DELIVERY_CHECKLIST_FABRIC_INTEGRATION.md) - Checklist de entrega

---

## 🧪 Testes e Validação

### Suite de Testes Automatizados

O projeto inclui um harness de testes robusto com 7 especificações:

```bash
# Executar todos os testes
python -m harness.runner

# Ver relatório HTML
open test-reports/harness_report_*.html
```

### Especificações Validadas (7/7 ✅)

1. **Setup Report** - Validação de ambiente e dependências
2. **Mapping Translation** - Tradução PowerCenter → PySpark
3. **Workflow Execution** - Execução de workflows EMP e HR
4. **Data Generation** - Geração de datasets em escala
5. **Pipeline Schemas** - Validação de ARM templates
6. **MCP Integration** - Testes de integração com MCP Server
7. **End-to-End** - Fluxo completo de migração

### Pre-Commit Hooks

```bash
# Instalar hooks (uma vez)
python scripts/install_hooks.py

# A partir daí, testes rodam automaticamente antes de cada commit
git commit -m "feature: nova funcionalidade"
```

---

## 📊 Resultados de Execução

### Última Execução MCP (2026-06-23)

**Status:** ✅ Sucesso  
**Duração:** ~12 minutos  
**Relatório:** [`output/migration_report_mcp_20260623_105921.json`](output/migration_report_mcp_20260623_105921.json)

#### Resultados:
- ✅ **Workspace criado:** `PowerCenter Migration` (ID: `999fa43f-32d3-4a10-ad5d-b58a5962e43a`)
- ✅ **Autenticação Azure:** Device Code Flow
- ✅ **MCP Server:** Conectado e operacional
- ⚠️ **Notebooks & Pipelines:** Requerem capacidade Premium (passos manuais documentados)

**Documentação Completa:** [`docs/MIGRATION_EXECUTION_SUMMARY.md`](docs/MIGRATION_EXECUTION_SUMMARY.md)

---

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação Azure

```bash
# Re-autenticar
az login --use-device-code
```

#### 2. Dependências Faltando

```bash
# Reinstalar ambiente
python scripts/setup_environment.py --force
```

#### 3. Testes Falhando

```bash
# Ver logs detalhados
python -m harness.runner --verbose

# Verificar relatório
cat test-reports/harness_report_*.json
```

#### 4. MCP Server Não Conecta

```bash
# Verificar se o MCP Server está configurado no VS Code
# Consulte: docs/FABRIC_MCP_SERVER_GUIDE.md
```

### Logs e Diagnóstico

- **Logs de execução:** `logs/*.log`
- **Relatórios de teste:** `test-reports/harness_report_*.json`
- **Relatórios de migração:** `output/migration_report_mcp_*.json`
- **Setup report:** `logs/setup_report.json`

---

## 🗺️ Roadmap

### ✅ Concluído (V2.0)
- [x] Migração automatizada via MCP Server
- [x] Suite de testes com 7/7 specs passando
- [x] Documentação completa e navegável
- [x] Pipelines ARM validados
- [x] Geração de dados em escala (10k+)
- [x] Pre-commit hooks e validação automática

### 🚧 Em Progresso
- [ ] CI/CD com GitHub Actions
- [ ] Deploy automático para Fabric via API
- [ ] Dashboard de monitoramento de execução

### 📋 Planejado (V2.1+)
- [ ] Suporte para mais tipos de fonte (JSON, Parquet, Delta)
- [ ] Migração de mais transformações PowerCenter
- [ ] UI web para configuração de migração
- [ ] Integração com Azure DevOps
- [ ] Template de migração para outros workflows

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork este repositório
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Diretrizes
- Mantenha 100% de cobertura de testes (7/7 specs devem passar)
- Siga os padrões de código PEP 8
- Documente novas features no `docs/`
- Atualize o BACKLOG.md com novas tarefas

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📞 Contato e Suporte

- **Autor:** Julio Pessan
- **GitHub:** [@juliopessan](https://github.com/juliopessan)
- **Issues:** [GitHub Issues](https://github.com/juliopessan/powercenter-microsoft-fabric-v2/issues)

---

## 🙏 Agradecimentos

- Microsoft Fabric Team pela excelente plataforma
- Informatica PowerCenter documentation
- Comunidade open-source Python/PySpark

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

