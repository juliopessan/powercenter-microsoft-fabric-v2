# PowerCenter to Microsoft Fabric Migration Project

> **Complete end-to-end transformation of Informatica PowerCenter workflows into Microsoft Fabric with native PySpark**  
> 
> Projeto: Migração de workflows PowerCenter Informatica para Microsoft Fabric com PySpark nativo

## 📋 Visão Geral

Este projeto demonstra a migração de dois workflows PowerCenter Informatica para Microsoft Fabric:

1. **Flat XML Processing** (`wf_m_poc_xml_emp.XML`)
   - Processa dados XML simples de funcionários
   - Transforma para formato CSV com validações
   - [📺 Tutorial YouTube](https://www.youtube.com/watch?v=ypGDbtYLQKw)

2. **Hierarchical XML Processing** (`wf_m_poc_xml_hr.XML`)
   - Processa dados XML hierárquicos de departamentos
   - Achata estruturas aninhadas e valida integridade
   - [📺 Tutorial YouTube](https://www.youtube.com/watch?v=0aKBhwFPE-Y)

---

## 🗂️ Estrutura do Projeto

```
Informatica-Scenarios/
├── 📁 data/                          # Arquivos de dados
│   ├── employees.xml                 # Dados simples (8 registros)
│   ├── hr.xml                        # Dados hierárquicos (3 depts, 8 employees)
│   ├── wf_m_poc_xml_emp.XML         # Workflow Informatica original (flat)
│   └── wf_m_poc_xml_hr.XML          # Workflow Informatica original (hierárquico)
│
├── 📁 notebooks/                     # Jupyter notebooks para Fabric
│   ├── 03_Map_EMP_Source_to_Target.ipynb          # XML simples → CSV
│   ├── 05_Map_HR_Source_to_Target.ipynb           # XML hierárquico → CSV
│   └── 06_Pipeline_Import_Guide.ipynb             # Guia de importação
│
├── 📁 pipelines/                     # Pipelines distribuíveis e schemas
│   ├── deliverables/                 # JSON/ZIP finais para importação
│   ├── schemas/                      # Definições fonte e versões intermediárias
│   ├── validation/                   # Scripts e relatórios de validação
│   ├── reference/                    # Modelo kb-pl_bronze_driven de referência
│   └── archive/                      # Artefatos legados preservados
│
├── 📁 docs/                          # Documentação (20+ guias)
│   ├── FABRIC_IMPORT_GUIDE.md
│   ├── POWERcenter_TO_PYSPARK_MAPPING.md
│   └── ... (guias de execução e troubleshooting)
│
├── 📁 output/                        # Dados processados
│   ├── emp_poc.csv
│   ├── hr.csv
│   └── hr_poc_10k/                   # Dados de teste em escala
│
├── 📁 scripts/                       # Automação e utilidades
│   ├── fabric-mcp-automation.ps1
│   ├── fabric_import_notebook.py
│   └── ... (scripts auxiliares)
│
├── 📁 logs/                          # Logs de execução
│
├── 📁 test-reports/                  # Relatórios de testes
│
└── README.md                         # Este arquivo
```

---

## ⚙️ Pré-Requisitos

### Ambiente Local
- ✅ Python 3.11+ com pip
- ✅ PowerShell 5.1+ (Windows)
- ✅ Git

### Microsoft Fabric
- ✅ Conta Microsoft Fabric ativa
- ✅ Workspace Fabric com permissões de admin
- ✅ Lakehouse configurado

---

## 🚀 Guia de Execução Rápida

### 1️⃣ Preparação Local (5 min)

```bash
# Clonar repositório
git clone <repo-url>
cd Informatica-Scenarios

# Ativar ambiente Python
.\.venv\Scripts\Activate.ps1

# Instalar dependências (se necessário)
pip install pyspark pandas
```

### 2️⃣ Teste Rápido com Dados Locais (10 min)

```bash
# Executar script de demonstração
python scripts/run_pyspark_10k.py
```

**Resultado esperado:** Arquivos CSV em `output/`

### 3️⃣ Importar para Microsoft Fabric (15 min)

#### **Opção A: Importar via ZIP (Recomendado)**

1. **Acesse seu Fabric Workspace**
   ```
   https://app.fabric.microsoft.com/workspace/<workspace-id>
   ```

2. **Criar novo Lakehouse**
   - Clique em **+ New** → **Lakehouse**
   - Nome: `informatica_poc`
   - Aguarde criação

3. **Upload de Dados**
   - Upload dos arquivos XML para `/lakehouse/default/Files/source/`
     - `employees.xml`
     - `hr.xml`

4. **Importar Notebooks**
   - Clique em **+ New** → **Import Notebook**
   - Selecione arquivos `.ipynb` de `notebooks/`
     - `03_Map_EMP_Source_to_Target.ipynb`
     - `05_Map_HR_Source_to_Target.ipynb`

5. **Importar Pipeline (NOVO)**
   - Clique em **+ New** → **Import from file** (ou **Pipeline**)
  - Selecione `pipelines/deliverables/pl_m_poc_xml_emp_FABRIC_DF.json`
  - Repita para `pipelines/deliverables/pl_m_poc_xml_hr_FABRIC_DF.json`
  - Se o fluxo exigir ZIP, use os arquivos `*_FABRIC_DF.zip` da mesma pasta

6. **Executar Pipeline**
   - Abra pipeline importado
   - Clique em **Run** ou **Save and run**
   - Monitore execução na aba **Run history**

#### **Opção B: Importar Manualmente (Sem ZIP)**

1. **Upload Notebooks** individualmente via Fabric UI
2. **Criar Pipeline** na UI com referências aos notebooks
3. **Configurar atividades** para chamar notebooks em sequência

### 4️⃣ Validar Resultados (5 min)

Após execução:

```
Lakehouse Files:
├── source/
│   ├── employees.xml ✓
│   └── hr.xml ✓
│
└── output/
    ├── emp_poc_target/ → emp_poc.csv ✓
  └── hr_poc_target/ → hr.csv ✓
```

✅ **Sucesso!** CSV files criados com validações aplicadas

---

## 📊 Mapeamento de Dados

### Fluxo EMP (XML Simples → CSV)

```
employees.xml (8 registros)
    ↓
[XML Parse] → spark.read.format("xml")
    ↓
[Transformações]
  • EMPLOYEE_ID: Trim + Upper
  • Salary: ByteType (1000-500000)
  • Name: String operations
    ↓
[Validações]
  • Null checks
  • Duplicate detection
  • Salary range validation
    ↓
emp_poc.csv (8 registros + validações)
```

### Fluxo HR (XML Hierárquico → CSV)

```
hr.xml (3 departments, 8 employees)
    ↓
[XML Parse] → rowTag="Department"
    ↓
[Flatten]
  • explode(col("Employees.Employee"))
  • Relationship mapping
    ↓
[Transformações]
  • Type casting: INT, DECIMAL
  • Composite key: DEPT_ID + EMP_ID
    ↓
[Validações]
  • FK integrity (dept ↔ emp)
  • Uniqueness checks
    ↓
hr.csv (8 registros + dept info)
```

---

## 📋 Checklist de Execução

- [ ] **Pré-requisitos instalados** (Python, PowerShell, Git)
- [ ] **Repositório clonado** e `.venv` ativado
- [ ] **Teste local executado** (`scripts/run_pyspark_10k.py`)
- [ ] **Fabric Workspace preparado** com Lakehouse
- [ ] **Dados XML uploaded** para `source/` no Lakehouse
- [ ] **ZIPs de pipeline importados** (ou notebooks manualmente)
- [ ] **Pipeline executado** e monitored
- [ ] **Arquivos CSV validados** em `output/`
- [ ] **Delta tables opcionais criadas** (para analytics)

---

## 🔧 Troubleshooting

### Erro: "Invalid ZIP format" ao importar

→ Use os artefatos finais em `pipelines/deliverables/`. Os ZIPs `*_FABRIC_DF.zip` contêm somente `pipeline.json`; os JSONs standalone também estão disponíveis.

### Erro: "Path not found" para XML

→ Verifique caminho correto: `/lakehouse/default/Files/source/employees.xml`

### Notebook não executa

→ Verifique:
1. Spark session está ativa
2. Lakehouse está montado
3. Caminho do arquivo está correto

### CSV vazio na saída

→ Valide:
1. Arquivo XML origem tem dados
2. Caminho de output está correto: `/lakehouse/default/Files/output/`

---

## 📚 Documentação Adicional

Consulte os guias em `docs/`:

| Guia | Descrição |
|------|-----------|
| `docs/FABRIC_IMPORT_GUIDE.md` | Instruções detalhadas de importação |
| `docs/POWERcenter_TO_PYSPARK_MAPPING.md` | Equivalência Informatica ↔ PySpark |
| `docs/FABRIC_QUICK_IMPORT_15MIN.md` | Setup rápido em 15 minutos |
| `docs/NOTEBOOK_EXECUTION_GUIDE.md` | Execução de notebooks passo a passo |
| `docs/TEST_RESULTS.md` | Resultados de validação |

---

## 🎯 Próximas Etapas

1. **Escalar dados** → Use `scripts/generate_10k_demo.py` para testes com volume
2. **Criar Delta tables** → Adicione Delta layer para analytics
3. **Integrar Power BI** → Conecte Lakehouse a dashboards
4. **Automatizar** → Configure refresh schedule do pipeline
5. **Adicionar transformações** → Estenda lógica para casos reais

---

## 📞 Suporte

- **YouTube Tutorials:**
  - [Flat XML Processing](https://www.youtube.com/watch?v=ypGDbtYLQKw)
  - [Hierarchical XML Processing](https://www.youtube.com/watch?v=0aKBhwFPE-Y)

- **Arquivos de referência:**
  - `data/wf_m_poc_xml_emp.XML` — Workflow Informatica original
  - `data/wf_m_poc_xml_hr.XML` — Workflow Informatica original

---

## 📄 Licença

Projeto para fins educacionais e de demonstração.

**Última atualização:** 2026-06-19 | **Versão:** 1.0