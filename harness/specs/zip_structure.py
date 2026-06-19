"""
Spec: ZipStructure
Todo ZIP de pipeline deliverable deve seguir o padrão Fabric:
  <nome>/
    manifest.json   (com campos obrigatórios)
    pipeline.json   (ARM template com $schema+resources OU Fabric DF com name+type+properties)

Erros originais: pl_m_poc_xml_*_FABRIC_DF.zip com pipeline.json na raiz, sem manifest.
"""

import json
import zipfile
from pathlib import Path
from .base import Spec, SpecResult, Severity

MANIFEST_REQUIRED = ["name", "displayName", "description", "version", "author", "environment", "type"]

# ARM template (pl_m_poc_xml_*.zip sem sufixo _FABRIC_DF)
PIPELINE_ARM_REQUIRED = ["$schema", "resources"]

# Fabric DF format (*_FABRIC_DF.zip)
PIPELINE_FABRIC_DF_REQUIRED = ["name", "type", "properties"]

# Pastas ignoradas (referência / arquivo histórico — não são deliverables)
_SKIP_DIRS = {"reference", "archive"}


def _is_fabric_df(zip_path: Path) -> bool:
    return "_FABRIC_DF" in zip_path.stem


class ZipStructureSpec(Spec):
    name = "ZipStructure"

    def run(self, root: Path) -> SpecResult:
        result = SpecResult(spec_name=self.name, passed=True)

        for zip_path in root.rglob("*.zip"):
            if any(part in _SKIP_DIRS for part in zip_path.parts):
                continue

            rel = str(zip_path.relative_to(root))
            result.checked += 1

            try:
                with zipfile.ZipFile(zip_path) as z:
                    entries = z.namelist()
            except zipfile.BadZipFile:
                result.add(Severity.ERROR, rel, "Arquivo ZIP corrompido ou inválido")
                continue

            # Estrutura: todos os arquivos devem estar dentro de uma pasta raiz única
            folders = {e.split("/")[0] for e in entries if "/" in e}
            root_files = [e for e in entries if "/" not in e]

            if root_files:
                result.add(Severity.ERROR, rel,
                    f"Arquivo(s) solto(s) na raiz do ZIP: {root_files}. "
                    "Todos os arquivos devem estar dentro de uma pasta.")

            if not folders:
                result.add(Severity.ERROR, rel, "ZIP sem pasta raiz — estrutura inválida para Fabric")
                continue

            if len(folders) > 1:
                result.add(Severity.ERROR, rel, f"Múltiplas pastas raiz: {sorted(folders)}")
                continue

            folder = next(iter(folders))

            # Valida manifest.json
            manifest_key = f"{folder}/manifest.json"
            if manifest_key not in entries:
                result.add(Severity.ERROR, rel, f"manifest.json ausente (esperado: {manifest_key})")
            else:
                try:
                    with zipfile.ZipFile(zip_path) as z:
                        manifest = json.loads(z.read(manifest_key))
                    for field in MANIFEST_REQUIRED:
                        if not manifest.get(field):
                            result.add(Severity.ERROR, rel,
                                f"manifest.json: campo obrigatório '{field}' ausente ou vazio")
                    if manifest.get("name") and manifest["name"] != folder:
                        result.add(Severity.WARNING, rel,
                            f"manifest.name='{manifest['name']}' ≠ pasta raiz='{folder}'")
                except json.JSONDecodeError as e:
                    result.add(Severity.ERROR, rel, f"manifest.json inválido: {e}")

            # Valida pipeline.json — escolhe o conjunto de campos conforme o tipo
            pipeline_key = f"{folder}/pipeline.json"
            if pipeline_key not in entries:
                result.add(Severity.ERROR, rel, f"pipeline.json ausente (esperado: {pipeline_key})")
            else:
                try:
                    with zipfile.ZipFile(zip_path) as z:
                        pipeline = json.loads(z.read(pipeline_key))

                    if _is_fabric_df(zip_path):
                        required = PIPELINE_FABRIC_DF_REQUIRED
                    else:
                        required = PIPELINE_ARM_REQUIRED

                    for field in required:
                        if field not in pipeline:
                            result.add(Severity.ERROR, rel,
                                f"pipeline.json: campo obrigatório '{field}' ausente "
                                f"({'Fabric DF' if _is_fabric_df(zip_path) else 'ARM template'} format)")

                    if "resources" in pipeline and not isinstance(pipeline["resources"], list):
                        result.add(Severity.ERROR, rel,
                            "pipeline.json (ARM): 'resources' deve ser uma lista")

                except json.JSONDecodeError as e:
                    result.add(Severity.ERROR, rel, f"pipeline.json inválido: {e}")

        return result
