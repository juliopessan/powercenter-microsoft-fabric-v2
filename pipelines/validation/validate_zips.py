#!/usr/bin/env python3
"""
Validador de ZIPs Fabric - Verifica se ZIPs estão no formato correto
"""

import zipfile
import json
import sys
from pathlib import Path

def validate_fabric_zip(zip_path):
    """Valida se um ZIP segue o padrão Fabric"""
    
    print(f"\n{'='*70}")
    print(f"📦 Validando: {Path(zip_path).name}")
    print(f"{'='*70}")
    
    if not Path(zip_path).exists():
        print(f"❌ Arquivo não encontrado: {zip_path}")
        return False
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            entries = z.namelist()
            
            print(f"\n📋 Estrutura do ZIP:")
            for entry in entries:
                indent = "  └─ " if "/" in entry else "  ├─ "
                print(f"{indent}{entry}")
            
            # Validação 1: Verificar se há pasta raiz
            folders = set([e.split('/')[0] for e in entries if '/' in e])
            
            if not folders:
                print(f"\n❌ ERRO: Nenhuma pasta encontrada (arquivos na raiz)")
                return False
            
            if len(folders) > 1:
                print(f"\n❌ ERRO: Múltiplas pastas raiz encontradas: {folders}")
                return False
            
            pipeline_name = list(folders)[0]
            print(f"\n✓ Pasta raiz detectada: {pipeline_name}")
            
            # Validação 2: Verificar manifest.json
            manifest_path = f"{pipeline_name}/manifest.json"
            if manifest_path not in entries:
                print(f"❌ ERRO: {manifest_path} não encontrado")
                return False
            
            print(f"✓ {manifest_path} encontrado")
            
            # Validação 3: Verificar pipeline.json
            pipeline_path = f"{pipeline_name}/pipeline.json"
            if pipeline_path not in entries:
                print(f"❌ ERRO: {pipeline_path} não encontrado")
                return False
            
            print(f"✓ {pipeline_path} encontrado")
            
            # Validação 4: Analisar manifest
            try:
                with z.open(manifest_path) as mf:
                    manifest = json.load(mf)
                
                print(f"\n📋 Manifest.json:")
                required_fields = ["name", "displayName", "description", "version", "author", "environment", "type"]
                
                for field in required_fields:
                    if field in manifest:
                        print(f"  ✓ {field}: {manifest[field]}")
                    else:
                        print(f"  ❌ {field}: FALTANDO")
                        return False
                
                # Validação 5: Comparar nome da pasta com manifest
                if manifest["name"] != pipeline_name:
                    print(f"\n⚠️  AVISO: Nome da pasta ({pipeline_name}) ≠ manifest.name ({manifest['name']})")
                else:
                    print(f"\n✓ Nome da pasta corresponde ao manifest")
                
            except json.JSONDecodeError:
                print(f"❌ ERRO: {manifest_path} não é JSON válido")
                return False
            
            # Validação 6: Verificar se há arquivos soltos na raiz
            root_files = [e for e in entries if '/' not in e]
            if root_files:
                print(f"\n❌ ERRO: Arquivos encontrados na raiz do ZIP: {root_files}")
                return False
            
            print(f"\n✅ ZIP VÁLIDO - Pronto para Fabric!")
            return True
            
    except zipfile.BadZipFile:
        print(f"❌ ERRO: {zip_path} não é um arquivo ZIP válido")
        return False
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

def main():
    """Script principal"""
    
    pipeline_dir = Path(__file__).parent
    zip_files = list(pipeline_dir.glob("pl_*.zip"))
    
    if not zip_files:
        print("❌ Nenhum arquivo ZIP encontrado em pipelines/")
        sys.exit(1)
    
    print(f"\n🔍 Encontrados {len(zip_files)} arquivo(s) ZIP")
    
    results = {}
    for zip_path in zip_files:
        results[zip_path.name] = validate_fabric_zip(str(zip_path))
    
    # Resumo final
    print(f"\n{'='*70}")
    print("📊 RESUMO DA VALIDAÇÃO")
    print(f"{'='*70}")
    
    for filename, is_valid in results.items():
        status = "✅ VÁLIDO" if is_valid else "❌ INVÁLIDO"
        print(f"{filename:.<50} {status}")
    
    all_valid = all(results.values())
    
    print(f"\n{'='*70}")
    if all_valid:
        print("✅ Todos os ZIPs estão no formato correto para Fabric!")
        sys.exit(0)
    else:
        print("❌ Alguns ZIPs precisam de correção")
        sys.exit(1)

if __name__ == "__main__":
    main()
