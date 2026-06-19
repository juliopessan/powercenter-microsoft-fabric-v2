"""
Spec: ZipStructure
Valida ZIPs de pipeline Fabric. Dois formatos são aceitos:

  Formato nested (padrão antigo):
    <nome>/manifest.json
    <nome>/pipeline.json

  Formato flat (fabric-ready — ARM template):
    manifest.json        (na raiz)
    <nome>.json          (na raiz, nome = stem do ZIP)
    pipeline deve conter 'resources' (ARM template)
"""

import json
import zipfile
from pathlib import Path
from .base import Spec, SpecResult, Severity

MANIFEST_REQUIRED_NESTED = ["name", "displayName", "description", "version", "author", "environment", "type"]
MANIFEST_REQUIRED_FLAT   = ["name", "displayName", "description", "version", "author", "environment"]
PIPELINE_ARM_REQUIRED    = ["resources"]

# Pastas ignoradas (referência / arquivo histórico)
_SKIP_DIRS = {"reference", "archive"}


def _validate_nested(result: SpecResult, zip_path: Path, rel: str, entries: list):
    """Formato nested: todos os arquivos dentro de uma pasta raiz."""
    folders = {e.split("/")[0] for e in entries if "/" in e}
    root_files = [e for e in entries if "/" not in e]

    if root_files:
        result.add(Severity.ERROR, rel,
            f"Arquivos soltos na raiz: {root_files}. Use formato nested ou flat/fabric-ready.")
        return

    if not folders:
        result.add(Severity.ERROR, rel, "ZIP sem pasta raiz e sem manifest.json na raiz")
        return

    if len(folders) > 1:
        result.add(Severity.ERROR, rel, f"Múltiplas pastas raiz: {sorted(folders)}")
        return

    folder = next(iter(folders))

    for fname, required in [
        (f"{folder}/manifest.json", MANIFEST_REQUIRED_NESTED),
        (f"{folder}/pipeline.json", None),
    ]:
        if fname not in entries:
            result.add(Severity.ERROR, rel, f"{fname.split('/')[-1]} ausente")
            continue
        if required:
            try:
                with zipfile.ZipFile(zip_path) as z:
                    data = json.loads(z.read(fname))
                for field in required:
                    if not data.get(field):
                        result.add(Severity.ERROR, rel,
                            f"manifest.json: campo obrigatório '{field}' ausente ou vazio")
            except json.JSONDecodeError as e:
                result.add(Severity.ERROR, rel, f"manifest.json JSON inválido: {e}")


def _validate_flat(result: SpecResult, zip_path: Path, rel: str, entries: list):
    """Formato flat (fabric-ready): manifest.json + <nome>.json na raiz."""
    if "manifest.json" not in entries:
        result.add(Severity.ERROR, rel, "manifest.json ausente na raiz do ZIP")
    else:
        try:
            with zipfile.ZipFile(zip_path) as z:
                manifest = json.loads(z.read("manifest.json"))
            for field in MANIFEST_REQUIRED_FLAT:
                if not manifest.get(field):
                    result.add(Severity.ERROR, rel,
                        f"manifest.json: campo '{field}' ausente ou vazio")
        except json.JSONDecodeError as e:
            result.add(Severity.ERROR, rel, f"manifest.json JSON inválido: {e}")

    pipeline_name = zip_path.stem.replace("_FABRIC", "") + ".json"
    if pipeline_name not in entries:
        json_files = [e for e in entries if e.endswith(".json") and e != "manifest.json"]
        if not json_files:
            result.add(Severity.ERROR, rel, f"Nenhum JSON de pipeline encontrado na raiz")
            return
        pipeline_name = json_files[0]

    try:
        with zipfile.ZipFile(zip_path) as z:
            pipeline = json.loads(z.read(pipeline_name))
        for field in PIPELINE_ARM_REQUIRED:
            if field not in pipeline:
                result.add(Severity.ERROR, rel,
                    f"{pipeline_name}: campo ARM obrigatório '{field}' ausente")
        if "resources" in pipeline and not isinstance(pipeline["resources"], list):
            result.add(Severity.ERROR, rel, f"{pipeline_name}: 'resources' deve ser lista")
    except json.JSONDecodeError as e:
        result.add(Severity.ERROR, rel, f"{pipeline_name} JSON inválido: {e}")


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

            is_flat = "manifest.json" in entries and not any("/" in e for e in entries)

            if is_flat:
                _validate_flat(result, zip_path, rel, entries)
            else:
                _validate_nested(result, zip_path, rel, entries)

        return result
