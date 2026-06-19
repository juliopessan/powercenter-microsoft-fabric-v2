# PowerCenter to Microsoft Fabric

> Migração completa de workflows Informatica PowerCenter para Microsoft Fabric com PySpark nativo.

**Status:** ✅ Produção | **Harness:** 7/7 specs passando | **Atualizado:** 2026-06-19

---

## O que este projeto faz

Transforma dois workflows PowerCenter Informatica em pipelines nativos do Microsoft Fabric:

| Workflow | Tipo | Fonte | Saída |
|---|---|---|---|
| `wf_m_poc_xml_emp` | XML simples | `employees.xml` (8 registros) | `emp_poc.csv` |
| `wf_m_poc_xml_hr` | XML hierárquico | `hr.xml` (3 depts / 8 empregados) | `hr.csv` |

Referências em vídeo:
- [Flat XML Processing](https://www.youtube.com/watch?v=ypGDbtYLQKw)
- [Hierarchical XML Processing](https://www.youtube.com/watch?v=0aKBhwFPE-Y)

---

## Início rápido

### 1. Clonar e preparar o ambiente

```bash
git clone https://github.com/juliopessan/powercenter-microsoft-fabric.git
cd powercenter-microsoft-fabric

# Prepara o ambiente automaticamente (instala pacotes, cria .env, valida estrutura)
python3 scripts/setup_environment.py
```

O script de setup verifica Python 3.11+, pip, Git, PowerShell, instala os pacotes necessários e gera o arquivo `.env` a partir do template `.env.example`.

### 2. Configurar credenciais

```bash
cp .env.example .env   # se o setup não criou automaticamente
# edite .env com suas credenciais Azure/Fabric
```

> O arquivo `.env` está no `.gitignore` — **nunca será commitado**.  
> Commite somente o `.env.example` com valores vazios.

### 3. Instalar o pre-commit hook (uma vez)

```bash
python3 scripts/install_hooks.py
```

A partir daí o harness roda automaticamente antes de cada commit.

### 4. Verificar integridade do projeto

```bash
python3 -m harness.runner
```

### 5. Gerar dados de teste localmente

```bash
python3 scripts/generate_10k_demo.py
```

### 6. Importar para o Microsoft Fabric

Siga o [Passo a Passo](START_HERE.md) ou o guia detalhado em [`docs/FABRIC_IMPORT_GUIDE.md`](docs/FABRIC_IMPORT_GUIDE.md).

---

## Pré-requisitos

### Ambiente local

| Requisito | Versão mínima | Verificado por |
|---|---|---|
| Python | 3.11+ | `setup_environment.py` |
| pip | qualquer | `setup_environment.py` |
| Git | qualquer | `setup_environment.py` |
| PowerShell | 5.1+ (Windows) / pwsh (Mac/Linux) | `setup_environment.py` (opcional) |

### Microsoft Fabric (manual)

- Conta Microsoft Fabric ativa → [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
- Workspace com permissão de Admin
- Lakehouse configurado no workspace
- Variáveis preenchidas no `.env` (gerado pelo setup)

---

## Estrutura do projeto

```
powercenter-microsoft-fabric/
│
├── data/                          # XMLs de entrada
│   ├── employees.xml              # Dados planos (8 registros)
│   ├── hr.xml                     # Dados hierárquicos (3 depts)
│   ├── wf_m_poc_xml_emp.XML       # Workflow PowerCenter original
│   └── wf_m_poc_xml_hr.XML        # Workflow PowerCenter original
│
├── notebooks/                     # Jupyter notebooks para Fabric
│   ├── 01_PowerCenter_to_PySpark_Translation.ipynb
│   ├── 02_Workflow_Execution_EMP_and_HR.ipynb
│   ├── 03_Map_EMP_Source_to_Target.ipynb
│   ├── 04_PySpark_Large_Scale_Data_Generation.ipynb
│   ├── 05_Map_HR_Source_to_Target.ipynb
│   └── 06_Pipeline_Import_Guide.ipynb
│
├── pipelines/
│   ├── deliverables/
│   │   └── fabric-ready/                       # ZIPs prontos para importação no Fabric
│   │       ├── pl_m_poc_xml_emp_FABRIC.zip     # Pipeline EMP — ARM template
│   │       └── pl_m_poc_xml_hr_FABRIC.zip      # Pipeline HR  — ARM template
│   ├── schemas/                   # Schemas ARM template e versões intermediárias
│   ├── validation/                # Scripts de validação de ZIPs
│   ├── reference/                 # Modelo de referência Fabric
│   └── archive/                   # Artefatos legados preservados
│
├── scripts/
│   ├── setup_environment.py       # Prepara o ambiente automaticamente
│   ├── install_hooks.py           # Instala pre-commit hook do harness
│   ├── generate_10k_demo.py       # Gera 10 mil registros sintéticos (sem Spark)
│   ├── run_pyspark_10k.py         # Gera dados com PySpark (para Fabric)
│   └── fabric_import_notebook.py  # Importa CSVs e cria Delta tables no Fabric
│
├── harness/                       # Sistema de specs e validação automática
│   ├── runner.py                  # CLI: --ci | --fix | --no-report
│   ├── report.py                  # Geração de relatórios JSON e HTML
│   └── specs/
│       ├── project_structure.py   # Diretórios e arquivos obrigatórios
│       ├── python_syntax.py       # Sintaxe Python válida em todos os .py
│       ├── path_safety.py         # Zero caminhos hardcoded
│       ├── pyspark_api.py         # Anti-padrões de PySpark
│       ├── zip_structure.py       # Estrutura dos ZIPs Fabric
│       ├── env_vars.py            # Chaves obrigatórias no .env
│       └── csv_columns.py         # Contrato de colunas por CSV
│
├── output/                        # CSVs gerados
│   ├── emp_poc.csv
│   ├── hr.csv
│   └── hr_poc_10k/
│
├── docs/                          # 20+ guias de documentação
├── logs/                          # Logs de execução e setup
├── test-reports/                  # Relatórios HTML e JSON do harness
│
├── .env                           # Variáveis de ambiente — NÃO commitado (.gitignore)
├── .env.example                   # Template seguro para credenciais (commitado)
├── .gitignore                     # Exclui __pycache__, .env, .pyc, .DS_Store
├── .github/workflows/harness.yml  # CI no GitHub Actions
└── README.md
```

---

## Harness — sistema de qualidade

O harness previne os erros que ocorreram durante o desenvolvimento do projeto:

| Spec | O que detecta |
|---|---|
| `ProjectStructure` | Diretórios ou arquivos obrigatórios ausentes |
| `PythonSyntax` | Erros de sintaxe em qualquer `.py` |
| `PathSafety` | Caminhos absolutos hardcoded (`C:\Users\...`, `/Users/...`) |
| `PySparkAPI` | `.agg()` com dict de listas, acesso a Row por índice, imports sem alias |
| `ZipStructure` | ZIPs sem pasta raiz, sem `manifest.json`, campos ausentes |
| `EnvVars` | Chaves obrigatórias ausentes no `.env` |
| `CsvColumns` | Colunas do CSV divergindo do contrato esperado |

```bash
# Verificação completa
python3 -m harness.runner

# Modo CI (saída compacta, exit 1 em erros)
python3 -m harness.runner --ci

# Corrigir problemas simples automaticamente
python3 -m harness.runner --fix
```

Relatórios em `test-reports/harness_report.html` e `harness_report.json`.

---

## Mapeamento de dados

### Fluxo EMP (XML plano → CSV)

```
employees.xml
    → spark.read.format("xml")
    → EMPLOYEE_ID: Trim + Upper
    → SALARY: ByteType + validação de range
    → null checks + deduplicação
    → emp_poc.csv
```

### Fluxo HR (XML hierárquico → CSV)

```
hr.xml  (rowTag="Department")
    → explode(col("Employees.Employee"))
    → DEPT_ID + EMP_ID: chave composta
    → FK integrity (dept ↔ emp)
    → hr.csv
```

---

## Importar no Microsoft Fabric

### Opção A — Pipeline via ZIP (recomendado)

1. Acesse seu workspace Fabric
2. **+ New → Data pipeline → Import** → selecione o ZIP em `pipelines/deliverables/fabric-ready/`
   - `pl_m_poc_xml_emp_FABRIC.zip` — pipeline EMP
   - `pl_m_poc_xml_hr_FABRIC.zip` — pipeline HR
3. Configure os parâmetros de Lakehouse
4. Clique em **Run**

### Opção B — Notebooks manualmente

1. **+ New → Import notebook** → selecione os `.ipynb` de `notebooks/`
2. Execute na ordem: `03_Map_EMP` → `05_Map_HR`
3. Verifique saída em `Files/output/` no Lakehouse

---

## Troubleshooting

**"Invalid ZIP format"** → Use os ZIPs de `pipelines/deliverables/fabric-ready/`. Não use os de `pipelines/schemas/` ou `pipelines/archive/`.

**"Path not found" para XML** → Caminho correto: `/lakehouse/default/Files/source/employees.xml`

**Notebook não executa** → Verifique se o Lakehouse está montado e a Spark session está ativa.

**Harness falha com erros de caminho** → Execute `python3 -m harness.runner --fix` para correções automáticas.

---

## Documentação adicional

| Documento | Conteúdo |
|---|---|
| [`START_HERE.md`](START_HERE.md) | Passo a passo completo do zero ao Fabric |
| [`docs/FABRIC_IMPORT_GUIDE.md`](docs/FABRIC_IMPORT_GUIDE.md) | Importação detalhada no Fabric |
| [`docs/POWERcenter_TO_PYSPARK_MAPPING.md`](docs/POWERcenter_TO_PYSPARK_MAPPING.md) | Equivalência Informatica ↔ PySpark |
| [`docs/FABRIC_QUICK_IMPORT_15MIN.md`](docs/FABRIC_QUICK_IMPORT_15MIN.md) | Setup em 15 minutos |
| [`docs/NOTEBOOK_EXECUTION_GUIDE.md`](docs/NOTEBOOK_EXECUTION_GUIDE.md) | Execução de notebooks |
| [`docs/EXECUTION_GUIDE.md`](docs/EXECUTION_GUIDE.md) | Guia de execução dos workflows |

---

## Próximas etapas

1. **Escalar** → `scripts/generate_10k_demo.py` para teste com volume
2. **Delta tables** → `scripts/fabric_import_notebook.py` cria tabelas Delta no Lakehouse
3. **Power BI** → Conecte o Lakehouse a um relatório via Direct Lake
4. **Agendamento** → Configure schedule no pipeline Fabric

---

**Licença:** Projeto educacional e de demonstração.  
**Última atualização:** 2026-06-19 | **Versão:** 2.2
