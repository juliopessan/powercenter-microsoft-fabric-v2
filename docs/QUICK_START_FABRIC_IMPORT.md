# QUICK START: Importar Outputs do Informatica para Fabric

## 🎯 Objetivo

Importar os arquivos CSV gerados (`emp_poc.csv` e `hr_poc.csv`) no Microsoft Fabric em 15 minutos.

---

## 📋 Passo 1: Preparar Credenciais Azure (5 minutos)

### 1.1 Criar App Registration

1. Acesse: https://portal.azure.com/
2. Navegue para: **Azure AD** → **App registrations** → **+ New registration**
3. Nome: `informatica-fabric-automation`
4. Clique em **Register**
5. **Copie e salve:**
   - **Application (client) ID** → cole em `ClientId` abaixo
   - **Directory (tenant) ID** → cole em `TenantId` abaixo

### 1.2 Criar Client Secret

1. Na página do app: **Certificates & secrets**
2. Clique em **+ New client secret**
3. Descrição: `FabricImportSecret`
4. Expira em: 24 meses
5. **Copie o valor** → cole em `ClientSecret` abaixo

### 1.3 Adicionar Permissões de API

1. Na página do app: **API permissions**
2. Clique em **+ Add a permission**
3. Selecione **APIs my organization uses** → procure **Power BI Service**
4. Selecione **Application permissions**
5. Marque: `Workspace.ReadWrite.All` e `Item.ReadWrite.All`
6. Clique em **Grant admin consent** (requer admin)

### 1.4 Obter Capacity ID (se tiver Fabric Premium)

1. Acesse: https://app.powerbi.com/
2. Clique em **Settings** (canto superior direito)
3. Vá para: **Admin Portal** → **Capacity settings**
4. Copie o **Capacity ID** da sua capacidade Fabric Premium

**Variáveis salvas:**
```
TenantId: ________________
ClientId: ________________
ClientSecret: ________________
CapacityId: ________________
```

---

## 🚀 Passo 2: Executar Automação (5 minutos)

### 2.1 Executar Script de Automação

```powershell
# Abra PowerShell no diretório Informatica-Scenarios

cd C:\Users\julio.cesar.d.pessan\Informatica-Scenarios

# Execute o script com suas credenciais

.\fabric-mcp-automation.ps1 `
    -TenantId "PASTE_TENANT_ID" `
    -ClientId "PASTE_CLIENT_ID" `
    -ClientSecret "PASTE_CLIENT_SECRET" `
    -CapacityId "PASTE_CAPACITY_ID" `
    -Action Full
```

### 2.2 Aguarde Conclusão

O script executará automaticamente:
```
✓ Step 1: Authenticate with Azure AD
✓ Step 2: Test MCP Connection
✓ Step 3: Create Workspace (informatica-poc-workspace)
✓ Step 4: Create Lakehouse (informatica_poc_data)
✓ Step 5: Upload emp_poc.csv
✓ Step 6: Upload hr_poc.csv
✓ Step 7: Verify Upload
```

**Output esperado:**
```
✅ FABRIC ENVIRONMENT SETUP COMPLETE

📊 Created Resources:
   • Workspace ID: 12345678-1234-1234-1234-123456789012
   • Lakehouse ID: 87654321-4321-4321-4321-210987654321
   • Files Uploaded: 2

🚀 You're ready to query your data in Fabric!
```

---

## ✅ Passo 3: Verificar Dados (3 minutos)

### 3.1 Acessar Fabric

1. Acesse: https://app.powerbi.com/
2. Clique em **Workspaces** (lado esquerdo)
3. Procure por: **informatica-poc-workspace**
4. Clique no workspace

### 3.2 Visualizar Arquivos

1. Clique em **informatica_poc_data** (lakehouse)
2. Clique na aba **Files**
3. Você verá:
   ```
   📄 emp_poc.csv (8 registros)
   📄 hr_poc.csv (8 registros)
   ```

### 3.3 Preview dos Dados

1. Clique em **emp_poc.csv**
2. Selecione **Preview**
3. Verifique:
   ```
   XPK_employee | FK_employees | EMPLOYEE_ID | FIRST_NAME | LAST_NAME | SALARY | DEPARTMENT_ID
   1            | 1            | 101         | John       | Smith     | 85000  | 1
   ...
   ```

---

## 🔧 Passo 4: Criar Tabelas Delta (2 minutos)

### 4.1 Abrir Notebook

1. No workspace, clique em **+ New**
2. Selecione **Notebook**
3. Nome: `Import_And_Transform`
4. Clique em **Create**

### 4.2 Copiar Código

1. Copie o conteúdo de: `fabric_import_notebook.py`
2. Cole no notebook, começando da **Cell 1**

### 4.3 Executar Notebook

1. Clique em **Run all** (ou Ctrl+Alt+F10)
2. Aguarde execução (~30 segundos)
3. Verifique output:
   ```
   ✓ EMP_POC loaded successfully
     Rows: 8
     Columns: 7
   
   ✓ HR_POC loaded successfully
     Rows: 8
     Columns: 9
   ```

---

## 📊 Passo 5: Consultar Dados (Opcional)

### 5.1 Nova Query SQL

1. No workspace, clique em **+ New**
2. Selecione **SQL query**
3. Cole:
   ```sql
   SELECT * FROM emp_poc LIMIT 5
   ```
4. Clique em **Run**

### 5.2 Resultado Esperado

```
XPK_employee | FK_employees | EMPLOYEE_ID | FIRST_NAME | LAST_NAME | SALARY | DEPARTMENT_ID
1            | 1            | 101         | John       | Smith     | 85000  | 1
2            | 1            | 102         | Jane       | Doe       | 90000  | 1
3            | 1            | 103         | Bob        | Johnson   | 75000  | 2
...
```

---

## 🎉 Conclusão

Pronto! Seus dados estão no Fabric:

✅ **Workspace criado:** informatica-poc-workspace  
✅ **Lakehouse criado:** informatica_poc_data  
✅ **Arquivos importados:** emp_poc.csv, hr_poc.csv  
✅ **Tabelas Delta criadas:** emp_poc, hr_poc  
✅ **Dados validados:** 8 + 8 registros  

### Próximos Passos

1. **Análise com Power BI**
   - Criar relatórios visuais
   - Conectar ao Lakehouse
   
2. **Integração com Pipelines**
   - Criar pipeline Fabric
   - Agendar execuções automáticas
   
3. **Migração de Workflows**
   - Traduzir workflows PowerCenter
   - Usar notebooks PySpark
   
4. **Decommissioning**
   - Validar dados migrados
   - Planejar shutdown PowerCenter

---

## 🆘 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Erro: "Invalid token" | Verifique ClientSecret e TenantId |
| Erro: "Unauthorized (401)" | Conceda permissões API (Admin consent) |
| Erro: "File not found" | Verifique se emp_poc.csv existe em `/output/` |
| Arquivo não aparece no Fabric | Aguarde 30 segundos e recarregue |
| Notebook não executa | Selecione Spark compute antes de rodar |

---

## 📚 Documentação Completa

Para detalhes completos, consulte:

- **Guia de Importação:** [FABRIC_IMPORT_GUIDE.md](FABRIC_IMPORT_GUIDE.md)
- **MCP Server Reference:** [FABRIC_MCP_SERVER_GUIDE.md](FABRIC_MCP_SERVER_GUIDE.md)
- **PySpark Translation:** [POWERcenter_TO_PYSPARK_MAPPING.md](POWERcenter_TO_PYSPARK_MAPPING.md)

---

**Tempo Total:** ~15 minutos  
**Status:** ✅ Pronto para Produção  
**Suporte:** data-engineering@company.com
