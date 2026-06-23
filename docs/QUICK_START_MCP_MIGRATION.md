# ⚡ Quick Start: Migração via MCP

**Automação completa PowerCenter → Fabric em 3 comandos**

---

## 🎯 O que isso faz

Executa todo o fluxo de migração automaticamente via MCP:

```
1. Criar workspace + lakehouse
2. Upload XMLs (employees.xml, hr.xml)
3. Criar 6 notebooks PySpark
4. Criar 2 pipelines (EMP, HR)
5. Executar workflows
6. Validar outputs (8 registros cada)
7. Gerar relatório final
```

**Tempo:** ~10-15 minutos  
**Output:** Workspace completo + relatório JSON

---

## 🚀 Uso Básico

### 1. Instalar dependências

```bash
pip install requests azure-identity
```

### 2. Configurar autenticação Azure

```bash
# Login via Azure CLI (recomendado)
az login

# OU via variáveis de ambiente
export AZURE_TENANT_ID="seu-tenant-id"
export AZURE_CLIENT_ID="seu-client-id"
export AZURE_CLIENT_SECRET="seu-secret"
```

### 3. Executar migração

```bash
python scripts/fabric_mcp_migration.py --workspace-name "PowerCenter Migration"
```

**Saída esperada:**

```
🚀 Iniciando migração PowerCenter → Fabric via MCP
⏱️  2026-06-23T14:30:00

==============================================================
📦 FASE 1: Setup do Workspace e Lakehouse
==============================================================
Criando workspace 'PowerCenter Migration'...
✓ Workspace criado: 12345678-1234-1234-1234-123456789abc
Criando lakehouse 'PowerCenterData'...
✓ Lakehouse criado: 87654321-4321-4321-4321-cba987654321
Criando estrutura de pastas...
  ✓ Pasta: Notebooks
  ✓ Pasta: Pipelines
  ✓ Pasta: Documentation
✅ Fase 1 concluída

==============================================================
📁 FASE 2: Upload de Arquivos XML
==============================================================
Uploading employees.xml...
  ✓ employees.xml (450 bytes)
Uploading hr.xml...
  ✓ hr.xml (578 bytes)
...
✅ Fase 2 concluída

==============================================================
📓 FASE 3: Upload de Notebooks PySpark
==============================================================
Criando notebook '01_PowerCenter_to_PySpark_Translation'...
  ✓ 01_PowerCenter_to_PySpark_Translation (abcd-1234)
...
✅ Fase 3 concluída (6 notebooks)

==============================================================
🔄 FASE 4: Criação de Pipelines
==============================================================
Criando pipeline 'pipeline_emp_xml_to_csv'...
  ✓ pipeline_emp_xml_to_csv (efgh-5678)
Criando pipeline 'pipeline_hr_xml_to_csv'...
  ✓ pipeline_hr_xml_to_csv (ijkl-9012)
✅ Fase 4 concluída (2 pipelines)

==============================================================
▶️  FASE 5: Execução de Pipelines
==============================================================
Executando pipeline_emp_xml_to_csv...
  ⏳ Aguardando conclusão...
  ✓ pipeline_emp_xml_to_csv concluído
Executando pipeline_hr_xml_to_csv...
  ⏳ Aguardando conclusão...
  ✓ pipeline_hr_xml_to_csv concluído
✅ Fase 5 concluída

==============================================================
✅ FASE 6: Validação de Outputs
==============================================================
Validando emp_poc.csv...
  ✓ emp_poc.csv: 8 registros
Validando hr_poc.csv...
  ✓ hr_poc.csv: 8 registros
✅ Fase 6 concluída

==============================================================
📊 FASE 7: Gerando Relatório Final
==============================================================
✓ Relatório salvo: migration_report.json
✓ Log salvo: logs/migration_20260623_143000.log

==============================================================
🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!
==============================================================
Workspace ID: 12345678-1234-1234-1234-123456789abc
Lakehouse ID: 87654321-4321-4321-4321-cba987654321
Duração total: 847.3s
Relatório: migration_report.json
==============================================================
```

---

## 📊 Resultados

### 1. Workspace no Fabric

Acesse: https://app.powerbi.com/

- Workspace: **PowerCenter Migration**
- Lakehouse: **PowerCenterData**
- 6 notebooks prontos para execução
- 2 pipelines configurados

### 2. Relatório JSON

**Arquivo:** `migration_report.json`

```json
{
  "migration_summary": {
    "start_time": "2026-06-23T14:30:00",
    "end_time": "2026-06-23T14:44:07",
    "duration_seconds": 847.3,
    "status": "success"
  },
  "workspace": {
    "id": "12345678-1234-1234-1234-123456789abc",
    "name": "PowerCenter Migration"
  },
  "lakehouse": {
    "id": "87654321-4321-4321-4321-cba987654321",
    "name": "PowerCenterData"
  },
  "notebooks": {
    "count": 6,
    "items": {
      "01_PowerCenter_to_PySpark_Translation": "abcd-1234",
      "02_Workflow_Execution_EMP_and_HR": "efgh-5678",
      ...
    }
  },
  "pipelines": {
    "count": 2,
    "items": {
      "pipeline_emp_xml_to_csv": "ijkl-9012",
      "pipeline_hr_xml_to_csv": "mnop-3456"
    }
  },
  "outputs": [
    {"name": "emp_poc.csv", "rows": 8},
    {"name": "hr_poc.csv", "rows": 8}
  ]
}
```

### 3. Logs Detalhados

**Arquivo:** `logs/migration_<timestamp>.log`

Contém log completo de todas as operações com timestamps.

---

## 🔧 Opções Avançadas

### Usar capacidade específica

```bash
python scripts/fabric_mcp_migration.py \
  --workspace-name "PCMigration" \
  --capacity-id "abc123-def456-ghi789"
```

### Workspace existente

Se já tiver um workspace, edite o script para usar `workspace_id` diretamente:

```python
# Em PowerCenterMigration.__init__
self.workspace_id = "seu-workspace-id-existente"
```

---

## 🐛 Troubleshooting

### Erro: "AuthenticationError"

**Causa:** Credenciais Azure não configuradas

**Solução:**
```bash
az login
# OU
az login --tenant <seu-tenant-id>
```

### Erro: "CapacityNotFound"

**Causa:** Sem capacidade Fabric trial ou premium

**Solução:**
1. Ativar trial: https://app.fabric.microsoft.com/ → "Start trial"
2. OU especificar capacity ID válido

### Erro: "WorkspaceAlreadyExists"

**Causa:** Workspace com mesmo nome já existe

**Solução:**
```bash
python scripts/fabric_mcp_migration.py --workspace-name "PCMigration2"
```

### Erro: "FileNotFound: notebooks/..."

**Causa:** Executando de diretório errado

**Solução:**
```bash
cd powercenter-microsoft-fabric
python scripts/fabric_mcp_migration.py
```

---

## 📚 Próximos Passos

### 1. Explorar no Fabric

- Abra o workspace no portal Fabric
- Execute notebooks manualmente
- Trigger pipelines via UI
- Analise dados no Lakehouse

### 2. Personalizar Workflows

- Edite notebooks para adicionar transformações
- Ajuste pipelines para incluir validações
- Configure schedules para execução automática

### 3. Produtizar

- Configure alertas no Azure Monitor
- Implemente CI/CD com GitHub Actions
- Adicione testes end-to-end

### 4. Documentação Completa

Veja: [`docs/FABRIC_MCP_MIGRATION_FLOW.md`](../docs/FABRIC_MCP_MIGRATION_FLOW.md)

---

## 🔗 Links Relacionados

- [Documentação completa do fluxo](../docs/FABRIC_MCP_MIGRATION_FLOW.md)
- [Guia de importação manual](../docs/FABRIC_IMPORT_GUIDE.md)
- [Execução de notebooks](../docs/NOTEBOOK_EXECUTION_GUIDE.md)
- [START_HERE.md](../START_HERE.md) (fluxo manual)

---

## 💡 Dicas

- **Tempo de execução:** ~10-15 minutos
- **Custo:** Usa trial gratuito do Fabric (sem cobrança)
- **Rollback:** Se falhar, delete o workspace e reexecute
- **Logs:** Sempre consulte `logs/migration_*.log` em caso de erro

---

**Última atualização:** 2026-06-23  
**Versão:** 1.0  
**Status:** ✅ Pronto para uso
