# 📊 Informatica PowerCenter - POC Execution Guide

## 📋 Estrutura do Projeto

```
Informatica-Scenarios/
├── README.md                      # Documentação
├── wf_m_poc_xml_emp.XML          # Workflow Informatica (simples)
├── wf_m_poc_xml_hr.XML           # Workflow Informatica (hierárquico)
├── employees.xml                 # Dados de entrada (XML simples)
├── hr.xml                        # Dados de entrada (XML hierárquico)
├── run-informatica-poc.ps1       # Script PowerShell (executor principal)
├── run-informatica-poc.bat       # Wrapper CMD/BAT
├── output/                       # [GERADO] CSVs de saída
│   ├── emp_poc.csv              # Output do workflow simples
│   └── hr.csv                   # Output do workflow hierárquico
└── logs/                         # [GERADO] Logs de execução
    └── wf_execution_*.log       # Log detalhado
```

---

## 🚀 Como Executar

### **Opção 1: PowerShell (Recomendado)**

```powershell
# Executar todos os workflows
.\run-informatica-poc.ps1 -WorkflowType all

# Executar apenas workflow simples
.\run-informatica-poc.ps1 -WorkflowType emp

# Executar apenas workflow hierárquico
.\run-informatica-poc.ps1 -WorkflowType hr
```

### **Opção 2: CMD/BAT (Windows)**

```cmd
# Executar todos
run-informatica-poc.bat all

# Apenas empregados
run-informatica-poc.bat emp

# Apenas HR
run-informatica-poc.bat hr

# Sem argumento (default = all)
run-informatica-poc.bat
```

### **Opção 3: Terminal VS Code**

```powershell
# No terminal integrado
pwsh -NoProfile -ExecutionPolicy Bypass -File run-informatica-poc.ps1 -WorkflowType all
```

---

## 📊 Workflows Implementados

### **Workflow 1: Simples (XML Flat)**
- **Nome:** `wf_m_poc_xml_emp`
- **Entrada:** `employees.xml` (8 registros de funcionários)
- **Transformação:** 
  - XPK_employee (auto-increment)
  - FK_employees (constante)
  - Passthrough dos campos
- **Saída:** `output/emp_poc.csv`
- **Campos:**
  ```
  XPK_employee, FK_employees, EMPLOYEE_ID, FIRST_NAME, LAST_NAME, SALARY, DEPARTMENT_ID
  ```

### **Workflow 2: Hierárquico (XML Aninhado)**
- **Nome:** `wf_m_poc_xml_hr`
- **Entrada:** `hr.xml` (3 departamentos, 8 funcionários aninhados)
- **Transformação:**
  - Flattening de estrutura hierárquica
  - XPK_Department (auto-increment)
  - XPK_Employee (auto-increment)
  - FK_Department (referência)
- **Saída:** `output/hr.csv`
- **Campos:**
  ```
  XPK_Department, DEPT_ID, DEPT_NAME, XPK_Employee, FK_Department, EMP_ID, FIRST_NAME, LAST_NAME, SALARY
  ```

---

## 📈 Fluxo de Dados

### **Workflow 1 - Simples**
```
employees.xml
    ↓
[XML Parser]
    ↓
[Expression Transform] (passthrough)
    ↓
[File Writer]
    ↓
emp_poc.csv
```

### **Workflow 2 - Hierárquico**
```
hr.xml (nested structure)
    ↓
[XML Parser]
    ↓
[Hierarchy Flattening]
    ↓
[Expression Transform]
    ↓
[File Writer]
    ↓
hr.csv (flat structure)
```

---

## 🔍 Validação de Saída

### **emp_poc.csv** (Esperado)
```csv
XPK_employee,FK_employees,EMPLOYEE_ID,FIRST_NAME,LAST_NAME,SALARY,DEPARTMENT_ID
1,1,101,John,Smith,85000,1
2,1,102,Jane,Doe,92000,1
3,1,103,Michael,Johnson,78000,2
...
```

### **hr.csv** (Esperado)
```csv
XPK_Department,DEPT_ID,DEPT_NAME,XPK_Employee,FK_Department,EMP_ID,FIRST_NAME,LAST_NAME,SALARY
1,1,Sales,1,1,101,John,Smith,85000
1,1,Sales,2,1,102,Jane,Doe,92000
...
```

---

## 📝 Logs

Cada execução gera um arquivo de log em:
```
logs/wf_execution_YYYYMMDD_HHMMSS.log
```

**Exemplo de log:**
```
[2026-06-16 14:30:45] [INFO] === INICIANDO WORKFLOW: wf_m_poc_xml_emp ===
[2026-06-16 14:30:45] [INFO] Lendo XML de entrada: C:\...\employees.xml
[2026-06-16 14:30:45] [INFO] Total de registros encontrados: 8
[2026-06-16 14:30:45] [INFO] Transformando dados (passthrough)...
[2026-06-16 14:30:45] [INFO] Exportando dados para: C:\...\output\emp_poc.csv
[2026-06-16 14:30:45] [SUCCESS] ✓ SUCESSO: 8 registros processados e salvos
```

---

## 🔧 Troubleshooting

### **Erro: "PowerShell não encontrado"**
- Instalar PowerShell 7+: https://github.com/PowerShell/PowerShell/releases
- Ou usar PowerShell 5 nativo do Windows

### **Erro: "Arquivo não encontrado"**
- Verificar se `employees.xml` e `hr.xml` existem no diretório
- Verificar caminho absoluto vs relativo

### **Erro: "Acesso negado ao escrever em output/"**
- Dar permissões de escrita no diretório
- Usar `Run as Administrator`

### **CSV vazio ou com dados incompletos**
- Verificar formato dos XMLs de entrada
- Validar schema com: `Invoke-WebRequest -Uri "https://www.w3.org/2001/XMLSchema" -OutFile schema.xsd`

---

## 📺 Vídeos de Referência

- **Workflow Simples:** https://www.youtube.com/watch?v=ypGDbtYLQKw
- **Workflow Hierárquico:** https://www.youtube.com/watch?v=0aKBhwFPE-Y

---

## 🎯 Próximos Passos

1. ✅ Executar os workflows
2. ✅ Validar CSVs em `output/`
3. ✅ Revisar logs em `logs/`
4. Integrar com PowerCenter Informatica real (se instalado)
5. Automatizar via scheduler/cron

---

**Created:** 2026-06-16  
**Status:** ✅ Ready for Testing
