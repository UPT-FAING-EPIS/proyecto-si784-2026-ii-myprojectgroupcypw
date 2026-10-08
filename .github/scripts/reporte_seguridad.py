"""Convierte los resultados JSON de Semgrep o Snyk en un reporte Markdown.

Uso:
  python .github/scripts/reporte_seguridad.py semgrep semgrep.json semgrep-reporte.md
  python .github/scripts/reporte_seguridad.py snyk snyk-deps.json snyk-code.sarif snyk-reporte.md

Escribe también en GITHUB_STEP_SUMMARY si existe. Sale con código 1 cuando
hay hallazgos bloqueantes: severidad ERROR en Semgrep, high/critical en Snyk.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path


def _leer(ruta: str) -> dict | list | None:
    archivo = Path(ruta)
    if not archivo.exists() or not archivo.read_text(encoding="utf-8").strip():
        return None
    return json.loads(archivo.read_text(encoding="utf-8"))


def _tabla_hallazgos(filas: list[tuple[str, str, str, str]]) -> list[str]:
    if not filas:
        return ["Sin hallazgos. ✅", ""]
    salida = ["| Severidad | Regla | Ubicación | Mensaje |", "| --- | --- | --- | --- |"]
    for severidad, regla, ubicacion, mensaje in filas[:200]:
        mensaje = mensaje.replace("|", "\\|").replace("\n", " ")[:200]
        salida.append(f"| {severidad} | `{regla}` | `{ubicacion}` | {mensaje} |")
    if len(filas) > 200:
        salida.append(f"| … | | | {len(filas) - 200} hallazgos adicionales en el JSON |")
    return salida + [""]


def reporte_semgrep(json_path: str) -> tuple[list[str], bool]:
    datos = _leer(json_path) or {"results": [], "errors": []}
    filas = [
        (r["extra"].get("severity", "INFO"), r["check_id"].rsplit(".", 1)[-1],
         f"{r['path']}:{r['start']['line']}", r["extra"].get("message", ""))
        for r in datos.get("results", [])
    ]
    conteo = Counter(f[0] for f in filas)
    bloqueante = conteo.get("ERROR", 0) > 0
    lineas = [
        "# Reporte Semgrep — NotaryVerify",
        "",
        f"- Resultado: **{'❌ hallazgos de severidad ERROR' if bloqueante else '✅ superado (sin severidad ERROR)'}**",
        f"- Hallazgos: {len(filas)} · ERROR {conteo.get('ERROR', 0)} · WARNING {conteo.get('WARNING', 0)} · "
        f"INFO {conteo.get('INFO', 0)}",
        f"- Archivos analizados: {len(datos.get('paths', {}).get('scanned', []))}",
        "",
        *_tabla_hallazgos(sorted(filas, key=lambda f: ["ERROR", "WARNING", "INFO"].index(f[0]) if f[0] in ("ERROR", "WARNING", "INFO") else 3)),
    ]
    return lineas, bloqueante


def _vulnerabilidades_dependencias(datos) -> list[tuple[str, str, str, str]]:
    proyectos = datos if isinstance(datos, list) else [datos]
    filas, vistos = [], set()
    for proyecto in proyectos:
        for v in proyecto.get("vulnerabilities", []):
            clave = (v.get("id"), v.get("packageName"))
            if clave in vistos:
                continue
            vistos.add(clave)
            filas.append((v.get("severity", "low"), v.get("id", ""),
                          f"{v.get('packageName')}@{v.get('version')}", v.get("title", "")))
    return filas


def _hallazgos_codigo(sarif) -> list[tuple[str, str, str, str]]:
    niveles = {"error": "high", "warning": "medium", "note": "low"}
    filas = []
    for corrida in (sarif or {}).get("runs", []):
        for r in corrida.get("results", []):
            ubicacion = r.get("locations", [{}])[0].get("physicalLocation", {})
            ruta = ubicacion.get("artifactLocation", {}).get("uri", "")
            linea = ubicacion.get("region", {}).get("startLine", "")
            filas.append((niveles.get(r.get("level", "note"), "low"), r.get("ruleId", ""),
                          f"{ruta}:{linea}", r.get("message", {}).get("text", "")))
    return filas


def reporte_snyk(deps_path: str, code_path: str) -> tuple[list[str], bool]:
    orden = ["critical", "high", "medium", "low"]
    deps = _vulnerabilidades_dependencias(_leer(deps_path) or {})
    codigo = _hallazgos_codigo(_leer(code_path))
    lineas = ["# Reporte Snyk — NotaryVerify", ""]
    bloqueante = False
    for titulo, filas in (("Dependencias (snyk test)", deps), ("Código (snyk code test)", codigo)):
        conteo = Counter(f[0] for f in filas)
        graves = conteo.get("critical", 0) + conteo.get("high", 0)
        bloqueante = bloqueante or graves > 0
        lineas += [
            f"## {titulo}",
            "",
            f"- Resultado: **{'❌ hallazgos high/critical' if graves else '✅ superado (sin high/critical)'}**",
            "- " + " · ".join(f"{nivel} {conteo.get(nivel, 0)}" for nivel in orden),
            "",
            *_tabla_hallazgos(sorted(filas, key=lambda f: orden.index(f[0]) if f[0] in orden else 4)),
        ]
    return lineas, bloqueante


def main() -> int:
    herramienta, *rutas = sys.argv[1:]
    if herramienta == "semgrep":
        lineas, bloqueante = reporte_semgrep(rutas[0])
    elif herramienta == "snyk":
        lineas, bloqueante = reporte_snyk(rutas[0], rutas[1])
    else:
        raise SystemExit("Herramienta no soportada: use semgrep o snyk")
    texto = "\n".join(lineas) + "\n"
    Path(rutas[-1]).write_text(texto, encoding="utf-8")
    if resumen := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(resumen, "a", encoding="utf-8") as archivo:
            archivo.write(texto)
    print(texto)
    return 1 if bloqueante else 0


if __name__ == "__main__":
    sys.exit(main())
