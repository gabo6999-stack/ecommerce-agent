from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

TRANSFORMS = {
    183: [
        (
            '<p class="nhx-note" style="margin-top:.5rem">¿Quieres el panorama completo del mercado antes de decidir? Consulta nuestra guía sobre los <a href="https://nodarishub.com/precios-paginas-web-ecuador/">precios de páginas web en Ecuador</a>.</p>',
            '<p class="nhx-note" style="margin-top:.5rem">¿Quieres conocer los costos antes de decidir? Consulta <a href="https://nodarishub.com/mx/crear-pagina-web/">cuánto cuesta crear una página web en México</a>.</p>',
            "referencia_y_enlace_mx",
        ),
    ],
    195: [
        (
            '<h1 style="margin-inline:auto">Agencia SEO en México: llevamos tu negocio a la <span class="nhx-accent">primera página de Google</span></h1>',
            '<h1 style="margin-inline:auto">Posicionamiento SEO para PyMEs en México: <span class="nhx-accent">técnica, contenido y medición</span></h1>',
            "h1_seo_mx_no_garantista",
        ),
    ],
    196: [
        (
            '<h1 style="margin-inline:auto">Agencia SEO en Ecuador: llevamos tu negocio a la <span class="nhx-accent">primera página de Google</span></h1>',
            '<h1 style="margin-inline:auto">Agencia SEO en Ecuador para mejorar <span class="nhx-accent">visibilidad, tráfico y medición</span></h1>',
            "h1_seo_ec_no_garantista",
        ),
    ],
}


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backups", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    records = []
    for page_id, transforms in TRANSFORMS.items():
        matches = list(args.backups.glob(f"page-{page_id}-*.json"))
        if len(matches) != 1:
            raise RuntimeError(f"Se esperaba un respaldo para page {page_id}; encontrados {len(matches)}")
        obj = json.loads(matches[0].read_text(encoding="utf-8"))
        original = (obj.get("content") or {}).get("raw", "")
        updated = original
        changes = []
        for old, new, label in transforms:
            count = updated.count(old)
            if count != 1:
                raise RuntimeError(f"{page_id}/{label}: se esperaba 1 coincidencia exacta; encontradas {count}")
            updated = updated.replace(old, new, 1)
            changes.append({"label": label, "old": old, "new": new, "matches": count})
        if updated == original:
            raise RuntimeError(f"{page_id}: la transformación no cambió el contenido")
        out_file = args.out / f"page-{page_id}.html"
        out_file.write_text(updated, encoding="utf-8")
        records.append({
            "id": page_id,
            "url": obj["link"],
            "title_unchanged": (obj.get("title") or {}).get("raw", ""),
            "source_backup": str(matches[0]),
            "output": str(out_file),
            "before_sha256": sha(original),
            "after_sha256": sha(updated),
            "before_chars": len(original),
            "after_chars": len(updated),
            "changes": changes,
        })

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "lote1_seguro_nodarishub",
        "pages": records,
    }
    manifest_path = args.out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "pages": records}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
