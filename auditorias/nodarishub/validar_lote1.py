from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate(manifest_path: Path, override: dict[int, str] | None = None) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for page in manifest["pages"]:
        page_id = int(page["id"])
        backup = json.loads(Path(page["source_backup"]).read_text(encoding="utf-8"))
        before = (backup.get("content") or {}).get("raw", "")
        after = (override or {}).get(page_id)
        if after is None:
            after = Path(page["output"]).read_text(encoding="utf-8")

        if sha(before) != page["before_sha256"]:
            errors.append(f"{page_id}: checksum del respaldo no coincide")
        if sha(after) != page["after_sha256"] and override is None:
            errors.append(f"{page_id}: checksum del archivo preparado no coincide")

        rebuilt = before
        for change in page["changes"]:
            old, new = change["old"], change["new"]
            if rebuilt.count(old) != 1:
                errors.append(f"{page_id}/{change['label']}: marcador anterior no es único")
                continue
            rebuilt = rebuilt.replace(old, new, 1)
            if after.count(old) != 0:
                errors.append(f"{page_id}/{change['label']}: marcador anterior persiste")
            if after.count(new) != 1:
                errors.append(f"{page_id}/{change['label']}: marcador nuevo no aparece exactamente una vez")
        if rebuilt != after:
            errors.append(f"{page_id}: existen cambios fuera de los reemplazos aprobados")

        before_styles = re.findall(r"(?is)<style\b[^>]*>.*?</style>", before)
        after_styles = re.findall(r"(?is)<style\b[^>]*>.*?</style>", after)
        if before_styles != after_styles:
            errors.append(f"{page_id}: cambió CSS embebido")
        if len(re.findall(r"(?is)<h1\b", before)) != len(re.findall(r"(?is)<h1\b", after)):
            errors.append(f"{page_id}: cambió el número de H1")
        if len(re.findall(r"(?is)<!--\s*wp:", before)) != len(re.findall(r"(?is)<!--\s*wp:", after)):
            errors.append(f"{page_id}: cambió el número de aperturas de bloques WordPress")
        if len(re.findall(r"(?is)<!--\s*/wp:", before)) != len(re.findall(r"(?is)<!--\s*/wp:", after)):
            errors.append(f"{page_id}: cambió el número de cierres de bloques WordPress")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    errors = validate(args.manifest)
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
        return 1

    if args.self_test:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        first = manifest["pages"][0]
        text = Path(first["output"]).read_text(encoding="utf-8")
        marker = first["changes"][0]["new"]
        broken = text.replace(marker, marker + " CONTROL_NEGATIVO", 1)
        negative_errors = validate(args.manifest, {int(first["id"]): broken})
        if not negative_errors:
            print(json.dumps({"status": "FAIL", "errors": ["el control negativo no fue detectado"]}, ensure_ascii=False, indent=2))
            return 1
        print(json.dumps({"status": "PASS", "pages": len(manifest["pages"]), "negative_control": "PASS", "negative_failures_detected": len(negative_errors)}, ensure_ascii=False, indent=2))
        return 0

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    print(json.dumps({"status": "PASS", "pages": len(manifest["pages"]), "checks": "reemplazos exactos, CSS, H1, bloques y checksums"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
