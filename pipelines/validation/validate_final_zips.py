#!/usr/bin/env python3
"""
Validador de ZIPs com pipeline.json no formato ARM template
"""

import zipfile
import json
import os
import sys

def validate_zip(zip_path):
    """Valida ZIP com pipeline.json ARM template"""
    
    print(f"\n📦 {os.path.basename(zip_path)}")
    print("-" * 70)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            entries = z.namelist()
            
            # Show structure
            print("✓ Estrutura do ZIP:")
            for entry in sorted(entries):
                indent = "  └─ " if "/" in entry else "  ├─ "
                print(f"{indent}{entry}")
            
            # Validate manifest
            pipeline_name = entries[0].split('/')[0] if entries else None
            if not pipeline_name:
                print("❌ ZIP vazio ou inválido")
                return False
            
            manifest_path = f"{pipeline_name}/manifest.json"
            pipeline_path = f"{pipeline_name}/pipeline.json"
            
            # Check manifest
            if manifest_path not in entries:
                print(f"❌ {manifest_path} não encontrado")
                return False
            
            manifest = json.loads(z.read(manifest_path).decode())
            print(f"\n✓ manifest.json válido:")
            print(f"  name: {manifest.get('name')}")
            print(f"  displayName: {manifest.get('displayName')}")
            print(f"  type: {manifest.get('type')}")
            print(f"  version: {manifest.get('version')}")
            
            # Check pipeline
            if pipeline_path not in entries:
                print(f"❌ {pipeline_path} não encontrado")
                return False
            
            pipeline = json.loads(z.read(pipeline_path).decode())
            print(f"\n✓ pipeline.json válido (ARM Template):")
            
            # Check ARM template structure
            if not pipeline.get('$schema'):
                print("  ⚠️  Aviso: $schema não definido")
            else:
                print(f"  schema: {pipeline.get('$schema')[:50]}...")
            
            if 'resources' not in pipeline:
                print("❌ 'resources' não encontrado no ARM template")
                return False
            
            resources = pipeline['resources']
            print(f"  resources: {len(resources)} encontrado(s)")
            
            for resource in resources:
                print(f"\n  Resource: {resource.get('name')}")
                print(f"    type: {resource.get('type')}")
                print(f"    apiVersion: {resource.get('apiVersion')}")
                
                activities = resource.get('properties', {}).get('activities', [])
                print(f"    activities: {len(activities)}")
                
                for activity in activities:
                    activity_type = activity.get('type')
                    activity_name = activity.get('name')
                    print(f"      - {activity_name} ({activity_type})")
            
            print(f"\n✅ {os.path.basename(zip_path)} VÁLIDO E PRONTO PARA FABRIC")
            return True
    
    except json.JSONDecodeError as e:
        print(f"❌ Erro JSON: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def main():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "deliverables")
    base_dir = os.path.normpath(base_dir)

    print("🔍 Validação Final dos ZIPs com pipeline.json CORRETO (ARM Template Format)")
    print("=" * 70)

    zip_files = [
        "pl_m_poc_xml_emp.zip",
        "pl_m_poc_xml_hr.zip"
    ]

    results = {}
    for zip_file in zip_files:
        zip_path = os.path.join(base_dir, zip_file)
        if os.path.exists(zip_path):
            results[zip_file] = validate_zip(zip_path)
        else:
            print(f"\n❌ {zip_file} não encontrado")
            results[zip_file] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    
    for zip_file, is_valid in results.items():
        status = "✅ VÁLIDO" if is_valid else "❌ INVÁLIDO"
        print(f"{zip_file:.<50} {status}")
    
    all_valid = all(results.values())
    
    if all_valid:
        print("\n✨ TODOS OS ZIPs ESTÃO PRONTOS PARA MICROSOFT FABRIC!")
        print("\n📋 Próximos Passos:")
        print("1. Upload dos ZIPs para workspace Fabric")
        print("2. Fabric reconhecerá automaticamente o ARM template")
        print("3. Pipeline será criado com todas as atividades")
        sys.exit(0)
    else:
        print("\n❌ Alguns ZIPs precisam de correção")
        sys.exit(1)

if __name__ == "__main__":
    main()
