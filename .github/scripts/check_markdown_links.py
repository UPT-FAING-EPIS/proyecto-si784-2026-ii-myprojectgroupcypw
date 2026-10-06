"""Verifica que los enlaces locales de los Markdown versionados apunten a rutas existentes.

Uso: python .github/scripts/check_markdown_links.py
Sale con código 1 y lista archivo:línea -> destino por cada enlace roto.
Los enlaces externos (http, mailto) y las anclas internas no se comprueban.
La fuente histórica con Git propio se omite porque CI no la descarga.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
HISTORICO = "documentacion/proyecto-si784-2026-ii-myprojectgroupcypw"
ENLACE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
EXTERNO = ("http://", "https://", "mailto:", "tel:", "#")


def markdown_versionados() -> list[Path]:
    salida = subprocess.run(
        ["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [ROOT / linea for linea in salida.splitlines() if not linea.startswith(HISTORICO)]


def enlaces_rotos(archivo: Path) -> list[tuple[int, str]]:
    rotos = []
    en_bloque = False
    for numero, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), start=1):
        if linea.lstrip().startswith("```"):
            en_bloque = not en_bloque
            continue
        if en_bloque:
            continue
        for destino in ENLACE.findall(linea):
            if destino.startswith(EXTERNO):
                continue
            ruta = unquote(destino.split("#", 1)[0])
            if not ruta:
                continue
            objetivo = (ROOT / ruta.lstrip("/")) if ruta.startswith("/") else (archivo.parent / ruta)
            objetivo = objetivo.resolve()
            if objetivo.is_relative_to(ROOT / HISTORICO):
                continue
            if not objetivo.exists():
                rotos.append((numero, destino))
    return rotos


def main() -> int:
    archivos = markdown_versionados()
    total = 0
    for archivo in archivos:
        for numero, destino in enlaces_rotos(archivo):
            print(f"{archivo.relative_to(ROOT).as_posix()}:{numero} -> {destino}")
            total += 1
    print(f"{len(archivos)} archivos Markdown revisados; {total} enlaces locales rotos.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
