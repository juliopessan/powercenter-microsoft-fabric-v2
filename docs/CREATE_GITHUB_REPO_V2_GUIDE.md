# Guia: Criar Repositório V2 no GitHub

Este guia fornece **3 opções** para criar o repositório V2 no GitHub.

---

## 📋 Status Atual

✅ **Projeto preparado localmente**
- Commit V2 criado: `c58e70c`
- README_V2.md pronto
- Todos os arquivos em staging
- `.gitignore` configurado

---

## Opção 1: GitHub CLI (Recomendado) ⚡

### Passo 1: Autenticar no GitHub

```bash
gh auth login
```

Siga as instruções:
1. Selecione **GitHub.com**
2. Escolha **HTTPS**
3. Autentique **via browser** ou **token**

### Passo 2: Criar o repositório

#### Via Script PowerShell (Automatizado):

```powershell
.\scripts\create-github-repo-v2.ps1
```

#### Ou via comando direto:

```bash
gh repo create powercenter-microsoft-fabric-v2 \
    --public \
    --description "V2: Migração automatizada de Informatica PowerCenter para Microsoft Fabric com PySpark, MCP Server e automação completa" \
    --source=. \
    --push
```

✅ **Pronto!** Seu repositório estará em: `https://github.com/juliopessan/powercenter-microsoft-fabric-v2`

---

## Opção 2: Interface Web do GitHub 🌐

### Passo 1: Criar repositório vazio

1. Acesse: https://github.com/new
2. **Repository name:** `powercenter-microsoft-fabric-v2`
3. **Description:** `V2: Migração automatizada de Informatica PowerCenter para Microsoft Fabric com PySpark, MCP Server e automação completa`
4. **Visibility:** Public
5. **NÃO** adicione README, .gitignore ou license (já temos localmente)
6. Clique em **Create repository**

### Passo 2: Conectar o repositório local

Copie os comandos exibidos pelo GitHub em "…or push an existing repository from the command line":

```bash
git remote add origin https://github.com/juliopessan/powercenter-microsoft-fabric-v2.git
git branch -M main
git push -u origin main
```

✅ **Pronto!** Atualize a página do GitHub para ver os arquivos.

---

## Opção 3: Git + Personal Access Token 🔑

### Passo 1: Criar Personal Access Token

1. Acesse: https://github.com/settings/tokens
2. Clique em **Generate new token** → **Generate new token (classic)**
3. **Note:** `PowerCenter V2 Repository`
4. **Expiration:** 90 days (ou conforme sua preferência)
5. **Scopes:** Marque:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
6. Clique em **Generate token**
7. **COPIE O TOKEN** (você não verá novamente)

### Passo 2: Criar repositório via API

```bash
# Substitua YOUR_TOKEN pelo token copiado
$TOKEN = "YOUR_TOKEN"
$REPO_NAME = "powercenter-microsoft-fabric-v2"
$DESCRIPTION = "V2: Migração automatizada de Informatica PowerCenter para Microsoft Fabric"

# Criar repositório
Invoke-RestMethod `
    -Uri "https://api.github.com/user/repos" `
    -Method POST `
    -Headers @{
        "Authorization" = "token $TOKEN"
        "Accept" = "application/vnd.github.v3+json"
    } `
    -Body (@{
        "name" = $REPO_NAME
        "description" = $DESCRIPTION
        "private" = $false
        "auto_init" = $false
    } | ConvertTo-Json)
```

### Passo 3: Push do código

```bash
git remote add origin https://github.com/juliopessan/powercenter-microsoft-fabric-v2.git
git branch -M main
git push -u origin main
```

Quando solicitada a senha, use o **Personal Access Token** (não sua senha do GitHub).

---

## 🎨 Configurações Pós-Criação

Após criar o repositório, configure:

### 1. Topics (Tags)

No GitHub, vá em **Settings** → **About** → **Topics**, adicione:
- `powercenter`
- `microsoft-fabric`
- `pyspark`
- `data-migration`
- `etl`
- `informatica`
- `azure`
- `automation`
- `jupyter`
- `notebooks`

### 2. Social Preview

Em **Settings** → **Social preview**, adicione uma imagem de preview (1280x640px)

### 3. Branch Protection (Opcional)

Para proteger a branch `main`:

1. **Settings** → **Branches** → **Add rule**
2. **Branch name pattern:** `main`
3. Marque:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
4. **Save changes**

### 4. GitHub Pages (Opcional)

Para hospedar documentação:

1. **Settings** → **Pages**
2. **Source:** Deploy from a branch
3. **Branch:** `main` / `docs`
4. **Save**

Sua documentação estará em: `https://juliopessan.github.io/powercenter-microsoft-fabric-v2/`

### 5. README Badge

Adicione badges ao README:

```markdown
[![GitHub stars](https://img.shields.io/github/stars/juliopessan/powercenter-microsoft-fabric-v2?style=social)](https://github.com/juliopessan/powercenter-microsoft-fabric-v2)
[![GitHub forks](https://img.shields.io/github/forks/juliopessan/powercenter-microsoft-fabric-v2?style=social)](https://github.com/juliopessan/powercenter-microsoft-fabric-v2/fork)
[![GitHub issues](https://img.shields.io/github/issues/juliopessan/powercenter-microsoft-fabric-v2)](https://github.com/juliopessan/powercenter-microsoft-fabric-v2/issues)
```

---

## 🔍 Verificar Sucesso

Após o push, verifique:

```bash
# Ver URL do repositório remoto
git remote -v

# Ver histórico de commits
git log --oneline -10

# Ver status
git status
```

Acesse o repositório no navegador:
```
https://github.com/juliopessan/powercenter-microsoft-fabric-v2
```

---

## 🐛 Troubleshooting

### Erro: "remote origin already exists"

```bash
# Remover origin antigo
git remote remove origin

# Adicionar novo origin
git remote add origin https://github.com/juliopessan/powercenter-microsoft-fabric-v2.git
```

### Erro: "Permission denied (publickey)"

Se usando SSH, configure sua chave SSH ou use HTTPS:

```bash
# Mudar para HTTPS
git remote set-url origin https://github.com/juliopessan/powercenter-microsoft-fabric-v2.git
```

### Erro: "Authentication failed"

Para HTTPS, use Personal Access Token como senha (não sua senha do GitHub).

### Erro: "Repository not found"

Verifique se o repositório foi criado corretamente no GitHub.

---

## 📞 Precisa de Ajuda?

Se encontrar problemas:

1. **GitHub CLI docs:** https://cli.github.com/manual/
2. **GitHub API docs:** https://docs.github.com/en/rest
3. **Git docs:** https://git-scm.com/doc

---

## ✅ Checklist

- [ ] Autenticado no GitHub (via CLI, browser ou token)
- [ ] Repositório criado no GitHub
- [ ] Push realizado com sucesso
- [ ] README_V2.md visível no repositório
- [ ] Topics/tags configurados
- [ ] Branch protection configurado (opcional)
- [ ] GitHub Pages configurado (opcional)

---

**🎉 Parabéns! Seu repositório V2 está no ar!**

URL Final: https://github.com/juliopessan/powercenter-microsoft-fabric-v2
