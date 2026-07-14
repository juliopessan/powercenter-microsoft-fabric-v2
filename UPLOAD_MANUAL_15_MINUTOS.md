# 🎯 GUIA RÁPIDO — Upload Manual no Fabric (15 minutos)

## ✅ Status Atual

- ✅ Workspace criado: PowerCenter Migration
- ✅ Lakehouse criado: powercenter_lakehouse
- ✅ 1 Pipeline criado: Pipeline_EMP_Workflow
- ⏳ Faltam: 6 notebooks + 8 XMLs + 1 pipeline + execução

---

## 📋 Próximos Passos (Simples e Rápido)

### 1️⃣ Abra o Fabric Portal
```
https://app.fabric.microsoft.com
```
Login: `marcus@mrios.com.br` / `Para@161`

---

### 2️⃣ Navegue até seu Workspace

1. Clique em **"Workspaces"** (menu esquerdo)
2. Procure por **"PowerCenter Migration"**
3. Clique para entrar

---

### 3️⃣ Upload dos 6 Notebooks (3 minutos)

No seu workspace:
1. Clique em **"+ New"** → **"Import notebook"**
2. Selecione os 6 arquivos de uma vez:
   ```
   notebooks/01_PowerCenter_to_PySpark_Translation.ipynb
   notebooks/02_Workflow_Execution_EMP_and_HR.ipynb
   notebooks/03_Map_EMP_Source_to_Target.ipynb
   notebooks/04_PySpark_Large_Scale_Data_Generation.ipynb
   notebooks/05_Map_HR_Source_to_Target.ipynb
   notebooks/06_Pipeline_Import_Guide.ipynb
   ```
3. Clique em **"Import"** e aguarde

✅ **Pronto! Notebooks estarão visíveis em seu workspace**

---

### 4️⃣ Upload dos 8 XMLs para Lakehouse (3 minutos)

1. No workspace, clique em **"powercenter_lakehouse"** (Lakehouse que já existe)
2. Na barra lateral, clique em **"Files"**
3. Clique em **"Upload Files"** e selecione:
   ```
   data/employees.xml
   data/hr.xml
   data/wf_m_poc_xml_emp.XML
   data/wf_m_poc_xml_hr.XML
   (+ 4 outros XMLs se houver em data/)
   ```
4. Clique em **"Upload"** e aguarde

✅ **Pronto! XMLs estarão no lakehouse**

---

### 5️⃣ Upload do Segundo Pipeline (2 minutos)

1. Volte ao workspace
2. Clique em **"+ New"** → **"Pipeline"**
3. Nome: `Pipeline_HR_Workflow`
4. Adicione atividade:
   - Clique em **"Add activity"**
   - Escolha **"Notebook"**
   - Selecione: `05_Map_HR_Source_to_Target`
5. Clique em **"Save"**

✅ **Pipeline criado!**

---

### 6️⃣ Executar os Pipelines (2 minutos)

1. No workspace, clique em `Pipeline_EMP_Workflow`
2. Clique em **"Run"** (botão verde no topo)
3. Aguarde até aparecer ✓ "Succeeded"

Repita para `Pipeline_HR_Workflow`

✅ **Pronto! Pipelines executados!**

---

## 🎉 Resultado Final

Após 15 minutos você terá:
- ✅ 6 Notebooks no workspace
- ✅ 8 XMLs no lakehouse
- ✅ 2 Pipelines criados
- ✅ 2 Pipelines executados
- ✅ Dados transformados prontos para análise

---

## 📸 Se Tiver Dúvidas

Abra o portal e:
1. Workspace deve mostrar seus notebooks
2. Clique em lakehouse → "Files" → 8 XMLs lá
3. Volte ao workspace → 2 pipelines visíveis
4. Execute ambos e confirme sucesso

---

## 🔄 Depois do Upload

Uma vez que tudo estiver no Fabric:
1. Execute os notebooks um por um para validar
2. Analise os dados transformados no lakehouse
3. Use os pipelines para automação contínua

---

**Tempo total: ~15 minutos**  
**Dificuldade: ⭐ Fácil (interface gráfica)**

🚀 **Comece agora em:** https://app.fabric.microsoft.com
