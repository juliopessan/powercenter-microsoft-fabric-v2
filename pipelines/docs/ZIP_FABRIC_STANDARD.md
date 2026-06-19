# 📦 Padrão de Formato ZIP para Microsoft Fabric

> **Documento de Padronização**: Define o formato correto para criação de arquivos ZIP de pipeline no Fabric

## ✅ Padrão Correto (Seguindo kb-pl_bronze_driven)

```
pl_m_poc_xml_emp.zip
└── pl_m_poc_xml_emp/                 ← PASTA RAIZ (nome do pipeline)
    ├── manifest.json                 ← Metadados do pipeline
    └── pipeline.json                 ← Configuração do pipeline
```

### Estrutura Interna Obrigatória

```
ZIP (arquivo comprimido)
  │
  └─ [pipeline-name]/                 (PASTA COM NOME DO PIPELINE)
     ├─ manifest.json                 (JSON metadados)
     └─ pipeline.json                 (JSON configuração)
```

---

## 📋 Arquivo: manifest.json

**Localização:** Dentro de `[pipeline-name]/manifest.json`

**Conteúdo Completo (Modelo kb-pl_bronze_driven):**

```json
{
  "name": "pl_m_poc_xml_emp",
  "displayName": "Informatica POC - Employee XML Pipeline",
  "description": "Transforms employee XML data to CSV format using PySpark. Parses flat XML structure, applies type conversions, validates data quality, and outputs to CSV.",
  "version": "1.0.0",
  "author": "Informatica Migration Team",
  "environment": "Microsoft Fabric",
  "type": "Pipeline",
  "icons": [
    "NotebookActivity",
    "DataTransform"
  ],
  "requires": {
    "linkedservices": {
      "fabric_lakehouse": {
        "supportTypes": [
          "Lakehouse"
        ]
      }
    }
  },
  "annotations": [
    "Informatica",
    "Migration",
    "PySpark",
    "XML-to-CSV"
  ],
  "services": [
    "Microsoft Fabric"
  ],
  "categories": [
    "Data Integration",
    "ETL"
  ],
  "scope": [
    "Fabric"
  ]
}
```

**Campos Obrigatórios (Baseline):**
- `name`: Identificador único (sem espaços, lowercase com underscore)
- `displayName`: Nome amigável para UI do Fabric
- `description`: Descrição funcional (detalhado)
- `version`: Versionamento (semver: X.Y.Z)
- `author`: Time/responsável
- `environment`: Sempre "Microsoft Fabric"
- `type`: Sempre "Pipeline"

**Campos Recomendados (Completo - seguindo kb-pl_bronze_driven):**
- `icons`: Array de ícones principais (NotebookActivity, DataTransform)
- `requires.linkedservices`: Dependências de serviços vinculados
- `annotations`: Tags para busca e indexação
- `services`: Serviços principais utilizados
- `categories`: Categorias (Data Integration, ETL, etc)
- `scope`: Escopo (Fabric, OnPrem, etc)

---

## 🚫 Erros Comuns a Evitar

| ❌ ERRADO | ✅ CORRETO | Motivo |
|-----------|-----------|--------|
| `manifest.json` na raiz do ZIP | `pipeline-name/manifest.json` | Fabric não localiza |
| Sem pasta intermediária | Pasta intermediária nomeada | Fabric espera estrutura |
| Nomes com espaços em pasta | Nomes sem espaços/underscore | Compatibilidade |
| Múltiplas pastas na raiz | Uma única pasta | Estrutura não-ambígua |
| Sem manifest.json | manifest.json presente | Fabric valida na importação |

---

## 🔧 Como Criar ZIP Corretamente

### Método 1: PowerShell (Recomendado)

```powershell
# 1. Criar estrutura
mkdir "emp_pipeline\pl_m_poc_xml_emp"

# 2. Adicionar arquivos
Copy-Item "pipeline_wf_m_poc_xml_emp.json" "emp_pipeline\pl_m_poc_xml_emp\pipeline.json"
@"
{
  "name": "pl_m_poc_xml_emp",
  "displayName": "Pipeline Name",
  "description": "Description",
  "version": "1.0.0",
  "author": "Team",
  "environment": "Microsoft Fabric",
  "type": "Pipeline"
}
"@ | Out-File "emp_pipeline\pl_m_poc_xml_emp\manifest.json" -Encoding UTF8

# 3. Comprimir
Compress-Archive -Path "emp_pipeline\*" -DestinationPath "pl_m_poc_xml_emp.zip" -Force

# 4. Limpar
Remove-Item "emp_pipeline" -Recurse
```

### Método 2: Python (Alternativo)

```python
import zipfile
import json
import os

def create_fabric_zip(pipeline_name, manifest_data, pipeline_json_path, output_zip):
    """Cria ZIP com estrutura Fabric correta"""
    
    with zipfile.ZipFile(output_zip, 'w') as z:
        # Adicionar manifest.json
        manifest_json = json.dumps(manifest_data, indent=2)
        z.writestr(f"{pipeline_name}/manifest.json", manifest_json)
        
        # Adicionar pipeline.json
        with open(pipeline_json_path, 'r') as f:
            z.writestr(f"{pipeline_name}/pipeline.json", f.read())

# Uso
manifest = {
    "name": "pl_m_poc_xml_emp",
    "displayName": "Informatica POC - Employee XML Pipeline",
    "description": "Transforms employee XML data",
    "version": "1.0.0",
    "author": "Informatica Migration Team",
    "environment": "Microsoft Fabric",
    "type": "Pipeline"
}

create_fabric_zip("pl_m_poc_xml_emp", manifest, "pipeline_wf_m_poc_xml_emp.json", "pl_m_poc_xml_emp.zip")
```

---

## ✔️ Checklist de Validação

Antes de usar o ZIP no Fabric, verificar:

- [ ] **Nome da pasta** corresponde ao `name` em manifest.json
- [ ] **manifest.json** está DENTRO da pasta, não na raiz
- [ ] **pipeline.json** está DENTRO da pasta, não na raiz
- [ ] **Sem arquivos soltos** na raiz do ZIP
- [ ] **Manifest válido** (JSON bem-formado)
- [ ] **Todos os campos obrigatórios** preenchidos
- [ ] **Encoding UTF-8** para arquivos JSON
- [ ] **Nenhuma pasta vazia** dentro do ZIP

---

## 📊 Comparação: Antes vs Depois

### ❌ ANTES (Incorreto)

```
pl_m_poc_xml_emp.zip
├── manifest.json              ← NA RAIZ (Errado!)
└── pipeline.json              ← NA RAIZ (Errado!)
```

**Resultado em Fabric:** ❌ Erro de importação - Estrutura não reconhecida

### ✅ DEPOIS (Correto)

```
pl_m_poc_xml_emp.zip
└── pl_m_poc_xml_emp/          ← PASTA CONTENDO
    ├── manifest.json
    └── pipeline.json
```

**Resultado em Fabric:** ✅ Importação bem-sucedida - Pipeline criado

---

## 🔄 Pipeline de Criação (Para Automação)

Para garantir consistência, seguir este fluxo:

```
1. Validar manifest.json (JSON válido)
2. Validar pipeline.json (JSON válido)
3. Criar pasta com nome_do_pipeline
4. Copiar manifest.json para pasta
5. Copiar pipeline.json para pasta
6. Comprimir pasta (não adicionar para fora)
7. Remover pasta temporária
8. Validar ZIP (verificar estrutura interna)
```

---

## 📞 Referência

- **Arquivo de Referência:** `kb-pl_bronze_driven (2).zip`
- **Aplicado a:** `pl_m_poc_xml_emp.zip`, `pl_m_poc_xml_hr.zip`
- **Data de Padronização:** 2026-06-19
- **Versão:** 1.0

---

## 🎯 Regra de Ouro

> **"Tudo dentro de UMA pasta, cujo nome é o nome do pipeline"**

Antes de criar qualquer ZIP para Fabric, lembre-se:
1. Existe UMA pasta principal?
2. Seu nome é o `name` do pipeline?
3. Todos os arquivos estão DENTRO dela?
4. Nada está solto na raiz?

Se sim a tudo → ZIP Fabric-ready ✅
