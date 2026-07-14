# ✅ CHECKLIST DE UPLOAD — Siga Passo-a-Passo

**Portal Status:** Aberto em https://app.fabric.microsoft.com  
**Tempo Estimado:** 15-20 minutos  
**Próximo Passo:** Autenticar com suas credenciais

---

## 🔐 PASSO 1: Autenticar (1 minuto)

Você verá a tela de login do Microsoft Fabric.

**Digite:**
- Email: `marcus@mrios.com.br`
- Senha: `Para@161`

Clique em **"Sign in"**

✓ Você será redirecionado para seu workspace

---

## 🏢 PASSO 2: Acessar Workspace (30 segundos)

Na sidebar esquerda, clique em **"Workspaces"**

Procure por: **"PowerCenter Migration"**

Clique para entrar

✓ Você verá o workspace com o lakehouse existente

---

## 📓 PASSO 3: Upload de 6 Notebooks (3 minutos)

No workspace PowerCenter Migration:

1. Clique em **"+ New"** (botão verde no topo)
2. Selecione **"Import notebook"**
3. Clique em **"Upload"** e procure por:
   ```
   notebooks/
   ├── 01_PowerCenter_to_PySpark_Translation.ipynb
   ├── 02_Workflow_Execution_EMP_and_HR.ipynb
   ├── 03_Map_EMP_Source_to_Target.ipynb
   ├── 04_PySpark_Large_Scale_Data_Generation.ipynb
   ├── 05_Map_HR_Source_to_Target.ipynb
   └── 06_Pipeline_Import_Guide.ipynb
   ```
4. Selecione **TODOS 6 de uma vez** (Ctrl+A após ir até pasta)
5. Clique em **"Import"**
6. Aguarde 2-3 minutos

✓ Você verá 6 notebooks listados no workspace

---

## 📁 PASSO 4: Upload de 8 XMLs no Lakehouse (3 minutos)

1. No workspace, clique em **"powercenter_lakehouse"** (o lakehouse que já existe)
2. Na barra lateral, clique em **"Files"**
3. Clique em **"Upload files"**
4. Procure pela pasta `data/` e selecione:
   ```
   data/
   ├── employees.xml
   ├── hr.xml
   ├── wf_m_poc_xml_emp.XML
   ├── wf_m_poc_xml_hr.XML
   └── (+ 4 mais se houver)
   ```
5. Selecione **TODOS 8** (ou quantos houver)
6. Clique em **"Upload"**
7. Aguarde 1-2 minutos

✓ Você verá os XMLs listados em "Files"

---

## 🔗 PASSO 5: Criar Segundo Pipeline (2 minutos)

1. Volte ao workspace PowerCenter Migration (clique em breadcrumb)
2. Clique em **"+ New"** → **"Pipeline"**
3. Digite o nome: **`Pipeline_HR_Workflow`**
4. Clique em **"Create"**
5. Na tela do pipeline:
   - Clique em **"Activity"** ou **"Add activity"**
   - Escolha **"Notebook"** da lista
   - Selecione: **`05_Map_HR_Source_to_Target`**
   - Clique em **"OK"**
6. Clique em **"Save"** (botão no topo)

✓ Segundo pipeline criado

---

## ▶️ PASSO 6: Executar Ambos Pipelines (2 minutos)

### Pipeline 1: EMP

1. No workspace, clique em **"Pipeline_EMP_Workflow"**
2. Clique em **"Run"** (botão verde no topo com ▶)
3. Aguarde até ver status ✓ **"Succeeded"**
4. Volte ao workspace

### Pipeline 2: HR

1. Clique em **"Pipeline_HR_Workflow"**
2. Clique em **"Run"**
3. Aguarde até ver status ✓ **"Succeeded"**

✓ Ambos pipelines executados com sucesso

---

## 🎉 PASSO 7: Validar Resultado (1 minuto)

1. Volte ao workspace
2. Você deve ver:
   - ✅ 6 notebooks listados
   - ✅ 1 lakehouse com 8 XMLs
   - ✅ 2 pipelines (ambos com ✓ "Succeeded")

3. Clique em **"powercenter_lakehouse"**
4. Você verá:
   - **Files:** 8 arquivos XML
   - **Tables:** Tabelas Delta criadas pelos pipelines

✓ **TUDO PRONTO!**

---

## ⏱️ Tempo Total: ~15-20 minutos

| Etapa | Tempo |
|-------|-------|
| Autenticação | 1 min |
| Workspace | 0.5 min |
| Upload Notebooks | 3 min |
| Upload XMLs | 3 min |
| Criar Pipeline 2 | 2 min |
| Executar Pipelines | 2 min |
| Validar | 1 min |
| **TOTAL** | **~13 min** |

---

## 📞 Se Tiver Problemas

| Problema | Solução |
|----------|---------|
| Login falha | Confirme email/senha (`marcus@mrios.com.br` / `Para@161`) |
| Workspace não aparece | Clique em "Workspaces" → procure "PowerCenter Migration" |
| Upload falha | Verifique conexão internet; tente 1-2 arquivos por vez |
| Pipeline não encontra notebook | Confirme que upload de notebooks foi bem-sucedido |
| Execução falha | Clique "View run history" para ver detalhes do erro |

---

## 🎯 Após Completar Tudo

1. Os dados estão no Fabric
2. Os pipelines transformaram os dados
3. Está pronto para:
   - Análise nos notebooks
   - Criação de dashboards Power BI
   - Integração com outros serviços

---

**Comece em:** https://app.fabric.microsoft.com  
**Login:** marcus@mrios.com.br / Para@161

👉 **Clique em "Sign in" na tela que já abriu no navegador!**
