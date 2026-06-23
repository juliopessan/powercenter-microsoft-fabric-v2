# Script para Criar Repositório V2 no GitHub
# Execute este script após autenticar no GitHub CLI

Write-Host "🚀 Criando repositório PowerCenter-Microsoft-Fabric V2..." -ForegroundColor Cyan

# Verificar autenticação
Write-Host "`n📋 Verificando autenticação GitHub..." -ForegroundColor Yellow
gh auth status

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Não autenticado. Execute: gh auth login" -ForegroundColor Red
    exit 1
}

# Criar repositório
Write-Host "`n📦 Criando repositório no GitHub..." -ForegroundColor Yellow
gh repo create powercenter-microsoft-fabric-v2 `
    --public `
    --description "V2: Migração automatizada de Informatica PowerCenter para Microsoft Fabric com PySpark, MCP Server e automação completa" `
    --source=. `
    --push

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Repositório criado com sucesso!" -ForegroundColor Green
    Write-Host "🌐 URL: https://github.com/juliopessan/powercenter-microsoft-fabric-v2" -ForegroundColor Cyan
    Write-Host "`n📊 Estatísticas do repositório:" -ForegroundColor Yellow
    
    # Mostrar estatísticas
    Write-Host "  - Commits: " -NoNewline
    git rev-list --count HEAD
    
    Write-Host "  - Branches: " -NoNewline
    git branch -a | Measure-Object | Select-Object -ExpandProperty Count
    
    Write-Host "  - Arquivos: " -NoNewline
    git ls-files | Measure-Object | Select-Object -ExpandProperty Count
    
    Write-Host "`n📚 Próximos Passos:" -ForegroundColor Yellow
    Write-Host "  1. Acesse: https://github.com/juliopessan/powercenter-microsoft-fabric-v2"
    Write-Host "  2. Configure descrição e topics no repositório"
    Write-Host "  3. Adicione topics: powercenter, microsoft-fabric, pyspark, migration, automation"
    Write-Host "  4. Configure GitHub Pages para hospedar docs (se desejar)"
    Write-Host "  5. Configure branch protection rules"
    
    Write-Host "`n🎉 Repositório V2 pronto para uso!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Erro ao criar repositório" -ForegroundColor Red
    Write-Host "Execute manualmente: gh repo create --help" -ForegroundColor Yellow
}
