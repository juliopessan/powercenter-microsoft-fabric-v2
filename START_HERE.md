# Passo a Passo — PowerCenter to Microsoft Fabric

**Do clone ao pipeline rodando no Fabric em ~30 minutos.**

---

## Visão geral do fluxo

```
Clone → Setup → Harness → Dados locais → Fabric → Pipeline
  1        2       3           4            5         6
```

---

## Passo 1 — Clonar o repositório

```bash
git clone https://github.com/juliopessan/powercenter-microsoft-fabric.git
cd powercenter-microsoft-fabric
```

---

## Passo 2 — Preparar o ambiente (automático)

```bash
python3 scripts/setup_environment.py
```

O script verifica e configura tudo automaticamente:

| Item | Ação |
|---|---|
| Python 3.11+ | Verifica versão |
| pip | Verifica instalação |
| Git | Verifica instalação |
| PowerShell | Verifica (opcional em Mac/Linux) |
| Pacotes Python | Instala `requests`, `pandas`, `openpyxl`, `azure-identity` |
| Pastas do projeto | Cria as que estiverem ausentes |
| `.env` | Gera template se não existir |

**Ao final você verá:**
```
✨ Ambiente pronto! Execute os notebooks no Fabric.
```

Se algum item falhar, o script indica exatamente o que fazer.

---

## Passo 3 — Instalar o pre-commit hook

```bash
python3 scripts/install_hooks.py
```

A partir daí, o harness roda automaticamente antes de cada `git commit` e bloqueia se encontrar erros.

Para rodar o harness manualmente a qualquer momento:

```bash
python3 -m harness.runner
```

Todos os 7 specs devem estar ✅ antes de continuar.

---

## Passo 4 — Preencher o `.env`

Abra o arquivo `.env` gerado pelo setup e preencha com as credenciais do seu tenant Azure:

```env
FABRIC_TENANT_ID=<seu-tenant-id>
FABRIC_CLIENT_ID=<seu-client-id>
FABRIC_CLIENT_SECRET=<seu-client-secret>
FABRIC_WORKSPACE_ID=<seu-workspace-id>
FABRIC_LAKEHOUSE_ID=<seu-lakehouse-id>
```

Onde encontrar esses valores:
- **TENANT_ID / CLIENT_ID / CLIENT_SECRET** → Azure Portal → Entra ID → App Registrations
- **WORKSPACE_ID** → URL do Fabric (`app.fabric.microsoft.com/groups/<id>`)
- **LAKEHOUSE_ID** → Fabric workspace → clique no Lakehouse → copie o ID da URL

---

## Passo 5 — Validar dados localmente (opcional)

```bash
# Gera 10.000 registros sintéticos sem precisar de Spark
python3 scripts/generate_10k_demo.py
```

Saída esperada em `output/hr_poc_10k/hr_poc_10k_data.csv`.

```bash
# Valida os ZIPs de pipeline
python3 pipelines/validation/validate_zips.py
```

Todos os 4 ZIPs devem retornar ✅.

---

## Passo 6 — Preparar o Microsoft Fabric

### 6.1 Criar o Lakehouse

1. Acesse [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. Abra seu workspace
3. **+ New → Lakehouse**
4. Nome sugerido: `informatica_poc`
5. Aguarde a criação (< 1 minuto)

### 6.2 Fazer upload dos XMLs de entrada

No Lakehouse criado:

1. Clique em **Files** (painel esquerdo)
2. Crie a pasta `source/` (botão **...** → **New folder**)
3. Faça upload dos arquivos:
   - `data/employees.xml`
   - `data/hr.xml`

Estrutura esperada no Lakehouse:
```
Files/
└── source/
    ├── employees.xml
    └── hr.xml
```

---

## Passo 7 — Importar os notebooks

1. No workspace, clique em **+ New → Import notebook**
2. Selecione os notebooks na ordem:

| Ordem | Arquivo | Propósito |
|---|---|---|
| 1 | `notebooks/03_Map_EMP_Source_to_Target.ipynb` | Transforma XML EMP → CSV |
| 2 | `notebooks/05_Map_HR_Source_to_Target.ipynb` | Transforma XML HR → CSV |

3. Em cada notebook importado, clique em **Add Lakehouse** e selecione `informatica_poc`

---

## Passo 8 — Importar o pipeline

### Opção A — Pipeline ARM template (recomendado para Fabric Data Factory)

1. No workspace: **+ New → Data pipeline**
2. Clique em **Import** (ou **...** → **Import from file**)
3. Selecione o ZIP:
   - Para EMP: `pipelines/deliverables/pl_m_poc_xml_emp.zip`
   - Para HR:  `pipelines/deliverables/pl_m_poc_xml_hr.zip`
4. O Fabric reconhece automaticamente o ARM template e cria as atividades

### Opção B — Formato Fabric DF nativo

Use os arquivos com sufixo `_FABRIC_DF`:
- `pipelines/deliverables/pl_m_poc_xml_emp_FABRIC_DF.zip`
- `pipelines/deliverables/pl_m_poc_xml_hr_FABRIC_DF.zip`

---

## Passo 9 — Executar e validar

### Executar o pipeline

1. Abra o pipeline importado
2. Clique em **Run** → **Save and run**
3. Monitore em **Run history** (painel inferior)

### Verificar os arquivos de saída

Após execução bem-sucedida, os CSVs estarão em:

```
Files/
├── source/
│   ├── employees.xml  ✓
│   └── hr.xml         ✓
└── output/
    ├── emp_poc.csv    ✓  (8 registros)
    └── hr.csv         ✓  (8 registros)
```

### Criar Delta tables (opcional)

Execute o notebook `scripts/fabric_import_notebook.py` no Fabric para criar Delta tables a partir dos CSVs — isso habilita analytics via Power BI Direct Lake.

---

## Checklist completo

```
Ambiente local
  [ ] python3 scripts/setup_environment.py  → ✨ Ambiente pronto
  [ ] python3 scripts/install_hooks.py      → hook instalado
  [ ] python3 -m harness.runner             → 7/7 specs ✅
  [ ] .env preenchido com credenciais Azure

Dados locais (opcional)
  [ ] python3 scripts/generate_10k_demo.py  → output/hr_poc_10k/
  [ ] python3 pipelines/validation/validate_zips.py → 4/4 ZIPs ✅

Microsoft Fabric
  [ ] Lakehouse criado (informatica_poc)
  [ ] employees.xml e hr.xml em Files/source/
  [ ] Notebooks 03 e 05 importados e Lakehouse vinculado
  [ ] Pipeline importado (ARM ou Fabric DF)
  [ ] Pipeline executado com sucesso
  [ ] CSVs validados em Files/output/
  [ ] Delta tables criadas (opcional)
```

---

## Comandos de referência rápida

```bash
# Setup
python3 scripts/setup_environment.py   # prepara ambiente
python3 scripts/install_hooks.py       # instala pre-commit hook

# Qualidade
python3 -m harness.runner              # roda todos os specs
python3 -m harness.runner --fix        # corrige problemas simples
python3 -m harness.runner --ci         # modo CI (exit 1 em erros)

# Validação
python3 pipelines/validation/validate_zips.py        # valida estrutura dos ZIPs
python3 pipelines/validation/validate_final_zips.py  # valida ZIPs + ARM template

# Dados
python3 scripts/generate_10k_demo.py   # gera dados de teste sem Spark
```

---

## Troubleshooting

**Setup falha em Python** → Instale Python 3.11+ em [python.org/downloads](https://python.org/downloads)

**Harness bloqueia o commit** → Execute `python3 -m harness.runner` para ver os erros detalhados e corrija-os antes de commitar.

**"Invalid ZIP" no Fabric** → Use os ZIPs de `pipelines/deliverables/`. Não tente importar os de `pipelines/schemas/` ou `pipelines/archive/`.

**"Path not found"** → Confirme que os XMLs estão em `Files/source/` (não na raiz do Lakehouse).

**Notebook sem output** → Verifique se o Lakehouse está montado (ícone ⚡ ao lado do nome do Lakehouse no notebook).

**`.env` com chaves vazias** → O harness avisa mas não bloqueia. Preencha antes de executar scripts que conectam no Fabric.

---

## Suporte

- Tutoriais: [EMP](https://www.youtube.com/watch?v=ypGDbtYLQKw) · [HR](https://www.youtube.com/watch?v=0aKBhwFPE-Y)
- Guias detalhados: `docs/`
- Issues: [github.com/juliopessan/powercenter-microsoft-fabric/issues](https://github.com/juliopessan/powercenter-microsoft-fabric/issues)

---

**Última atualização:** 2026-06-19 | **Versão:** 2.0
