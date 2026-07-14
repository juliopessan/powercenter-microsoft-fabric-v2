# Upload Manual - Portal Fabric

## 🎯 Objetivo
Fazer upload dos 6 notebooks do PowerCenter para o workspace "PowerCenter Migration" via portal web do Fabric.

---

## 📋 Pré-requisitos
- ✅ Workspace "PowerCenter Migration" criado (ID: `999fa43f-32d3-4a10-ad5d-b58a5962e43a`)
- ✅ 6 notebooks prontos na pasta `notebooks/`
- ✅ Credenciais Fabric:
  - Email: marcos@mrios.com.br
  - Senha: Para@161

---

## 🚀 Passo a Passo

### Etapa 1: Login no Portal Fabric (2 min)

1. **Abrir o portal:**
   ```
   https://app.fabric.microsoft.com/home?experience=fabric-developer
   ```

2. **Fazer login:**
   - Email: `marcos@mrios.com.br`
   - Senha: `Para@161`

3. **Aguardar carregamento da home do Fabric**

---

### Etapa 2: Acessar o Workspace (1 min)

1. **No menu lateral esquerdo**, clique em **"Workspaces"** (ícone de pasta)

2. **Procurar workspace:**
   - Na lista, busque: **PowerCenter Migration**
   - Ou use a busca no topo da lista

3. **Clicar no workspace para abrir**

4. **Verificar que o workspace está vazio** (esperado — acabamos de criar)

---

### Etapa 3: Criar Lakehouse (5 min)

> ⚠️ **IMPORTANTE:** Lakehouse é obrigatório antes de fazer upload de notebooks (notebooks precisam de um lakehouse padrão).

1. **No workspace PowerCenter Migration**, clicar em **"+ Novo"** (botão laranja no topo)

2. **Selecionar:** `Lakehouse`

3. **Preencher:**
   - Nome: `powercenter_lakehouse`
   - Descrição (opcional): `Lakehouse para migração PowerCenter - armazenamento de dados ETL`

4. **Clicar em "Criar"**

5. **Aguardar provisionamento** (30-60 segundos)

6. **Quando criado, você verá:**
   - Tela do lakehouse com 3 abas: Tables / Files / Shortcuts
   - Estrutura vazia (normal)

7. **Voltar para o workspace:** clicar em **"PowerCenter Migration"** no breadcrumb (topo da tela)

---

### Etapa 4: Upload dos 6 Notebooks (10 min)

> 📁 **Arquivos locais:** `C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\notebooks\`

#### 4.1 Notebook 01 - PowerCenter to PySpark Translation

1. **No workspace**, clicar em **"+ Novo" → "Notebook" → "Importar"**

2. **Clicar em "Carregar" / "Upload"**

3. **Selecionar arquivo:**
   ```
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\notebooks\01_PowerCenter_to_PySpark_Translation.ipynb
   ```

4. **Aguardar upload** (arquivo tem 47 KB)

5. **Quando abrir o notebook:**
   - **Fechar a tela do notebook** (X no canto superior direito)
   - **Voltar para o workspace**

---

#### 4.2 Notebook 02 - Workflow Execution

1. **"+ Novo" → "Notebook" → "Importar"**

2. **Upload:**
   ```
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\notebooks\02_Workflow_Execution_EMP_and_HR.ipynb
   ```

3. **Aguardar upload** (21 KB)

4. **Fechar e voltar ao workspace**

---

#### 4.3 Notebook 03 - Map EMP Source to Target

1. **"+ Novo" → "Notebook" → "Importar"**

2. **Upload:**
   ```
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\notebooks\03_Map_EMP_Source_to_Target.ipynb
   ```

3. **Aguardar upload** (8.8 KB)

4. **Fechar e voltar**

---

#### 4.4 Notebook 04 - PySpark Large Scale Data Generation

1. **"+ Novo" → "Notebook" → "Importar"**

2. **Upload:**
   ```
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\notebooks\04_PySpark_Large_Scale_Data_Generation.ipynb
   ```

3. **Aguardar upload** (5.8 KB)

4. **Fechar e voltar**

---

#### 4.5 Notebook 05 - Map HR Source to Target

1. **"+ Novo" → "Notebook" → "Importar"**

2. **Upload:**
   ```
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\notebooks\05_Map_HR_Source_to_Target.ipynb
   ```

3. **Aguardar upload** (9.6 KB)

4. **Fechar e voltar**

---

#### 4.6 Notebook 06 - Pipeline Import Guide

1. **"+ Novo" → "Notebook" → "Importar"**

2. **Upload:**
   ```
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\notebooks\06_Pipeline_Import_Guide.ipynb
   ```

3. **Aguardar upload** (27 KB)

4. **Fechar e voltar**

---

### Etapa 5: Upload dos 4 Arquivos XML no Lakehouse (3 min)

> 📁 **Arquivos locais:** `C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\data\`

1. **No workspace**, clicar no lakehouse: **powercenter_lakehouse**

2. **Clicar na aba "Files"** (no topo da tela do lakehouse)

3. **Clicar em "Upload" → "Upload files"**

4. **Selecionar os 4 arquivos XML:**
   ```
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\data\employees.xml          (1.6 KB)
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\data\hr.xml                 (3.1 KB)
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\data\wf_m_poc_xml_emp.XML  (34 KB)
   C:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\data\wf_m_poc_xml_hr.XML   (44 KB)
   ```

5. **Confirmar upload** (total: 84 KB)

6. **Aguardar processamento** (30 segundos)

7. **Verificar que os 4 arquivos aparecem na pasta Files/**

8. **Voltar para o workspace** (breadcrumb)

---

### Etapa 6: Verificação Final (1 min)

No workspace **PowerCenter Migration**, você deve ver:

| Item | Tipo | Status |
|------|------|--------|
| powercenter_lakehouse | Lakehouse | ✅ Criado |
| 01_PowerCenter_to_PySpark_Translation | Notebook | ✅ Importado |
| 02_Workflow_Execution_EMP_and_HR | Notebook | ✅ Importado |
| 03_Map_EMP_Source_to_Target | Notebook | ✅ Importado |
| 04_PySpark_Large_Scale_Data_Generation | Notebook | ✅ Importado |
| 05_Map_HR_Source_to_Target | Notebook | ✅ Importado |
| 06_Pipeline_Import_Guide | Notebook | ✅ Importado |

**Total de itens no workspace:** 7 (1 lakehouse + 6 notebooks)

---

## ✅ Próximos Passos

Depois de completar este upload manual:

1. **Criar 2 pipelines** (via portal Fabric):
   - Pipeline_EMP_Workflow
   - Pipeline_HR_Workflow

2. **Executar os pipelines**

3. **Validar tabelas criadas:**
   - `emp_poc` (8 registros esperados)
   - `hr_poc` (11 registros esperados)

4. **Exportar CSVs para `output/`**

---

## 🆘 Troubleshooting

### ❌ "Lakehouse não aparece como opção"
- **Causa:** Workspace sem capacidade Premium
- **Solução:** Verificar com admin do tenant se a capacidade Premium está ativa

### ❌ "Upload de notebook falha"
- **Causa:** Arquivo .ipynb corrompido ou formato inválido
- **Solução:** Validar arquivo JSON localmente antes do upload

### ❌ "Não consigo fazer login"
- **Causa:** Credenciais incorretas ou MFA habilitado
- **Solução:** Verificar email/senha e completar MFA se necessário

---

## 📊 Tempo Total Estimado
- Login: 2 min
- Acessar workspace: 1 min
- Criar lakehouse: 5 min
- Upload 6 notebooks: 10 min
- Upload 4 XMLs: 3 min
- Verificação: 1 min

**TOTAL: ~22 minutos**

---

## 📝 Notas

- Este processo substitui a automação via API (que estava bloqueada por limitação de capacidade)
- Upload manual via portal é mais confiável e visual
- Depois deste passo, podemos voltar a usar MCP tools para criar pipelines e executar workflows
