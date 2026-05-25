"""
exportar_chat.py
Convierte los archivos JSON de sesiones del agente a TXT legible.
Uso: python exportar_chat.py
"""

import json
import os
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path(r"C:\Users\gabom\ecommerce-agent\sessions")
OUTPUT_DIR   = Path(r"C:\Users\gabom\ecommerce-agent\chats_exportados")

def exportar_sesion(json_path: Path, output_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages = data if isinstance(data, list) else data.get("messages", [])

    lines = []
    lines.append("=" * 60)
    lines.append(f"  CHAT EXPORTADO — {json_path.stem}")
    lines.append(f"  Exportado el {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)
    lines.append("")

    for msg in messages:
        role = msg.get("role", "?").upper()
        content = msg.get("content", "")

        # El contenido puede ser string o lista de bloques
        if isinstance(content, list):
            texto = ""
            for bloque in content:
                if isinstance(bloque, dict) and bloque.get("type") == "text":
                    texto += bloque.get("text", "")
        else:
            texto = str(content)

        if role == "USER":
            lines.append(f"👤 TÚ:")
        else:
            lines.append(f"🤖 AGENTE:")

        for linea in texto.strip().splitlines():
            lines.append(f"   {linea}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Exportado: {output_path.name}")


def main():
    if not SESSIONS_DIR.exists():
        print(f"❌ No se encontró la carpeta de sesiones: {SESSIONS_DIR}")
        return

    archivos = sorted(SESSIONS_DIR.glob("session_*.json"))
    if not archivos:
        print("❌ No hay sesiones guardadas todavía.")
        return

    print(f"📂 Encontradas {len(archivos)} sesión(es)\n")

    for json_path in archivos:
        txt_name = json_path.stem + ".txt"
        output_path = OUTPUT_DIR / txt_name
        exportar_sesion(json_path, output_path)

    print(f"\n📁 Todos los chats exportados en:\n   {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
