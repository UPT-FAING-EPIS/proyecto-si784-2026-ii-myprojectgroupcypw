"""Reporte de Bugs, Vulnerabilities y Security Hotspots desde la API de SonarQube.

Uso: python .github/scripts/reporte_sonar.py <salida.md>
Variables: SONAR_HOST_URL, SONAR_TOKEN, SONAR_PROJECT_KEY y, opcional, SONAR_PULL_REQUEST.
Escribe el reporte en Markdown (y en GITHUB_STEP_SUMMARY si existe). Sale con
código 1 si el Quality Gate está en ERROR.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.parse
import urllib.request

HOST = os.environ.get("SONAR_HOST_URL", "https://sonarcloud.io").rstrip("/")
TOKEN = os.environ["SONAR_TOKEN"]
PROYECTO = os.environ["SONAR_PROJECT_KEY"]
PR = os.environ.get("SONAR_PULL_REQUEST", "")


def consultar(ruta: str, **parametros) -> dict:
    if PR:
        parametros["pullRequest"] = PR
    url = f"{HOST}{ruta}?{urllib.parse.urlencode(parametros)}"
    credencial = base64.b64encode(f"{TOKEN}:".encode()).decode()
    peticion = urllib.request.Request(url, headers={"Authorization": f"Basic {credencial}"})
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        return json.load(respuesta)


def total_issues(tipo: str) -> int:
    return consultar("/api/issues/search", componentKeys=PROYECTO, types=tipo, resolved="false", ps=1)["total"]


def total_hotspots() -> int:
    datos = consultar("/api/hotspots/search", projectKey=PROYECTO, status="TO_REVIEW", ps=1)
    return datos["paging"]["total"]


def main() -> int:
    salida = sys.argv[1] if len(sys.argv) > 1 else "sonar-reporte.md"
    gate = consultar("/api/qualitygates/project_status", projectKey=PROYECTO)["projectStatus"]
    medidas = consultar(
        "/api/measures/component", component=PROYECTO,
        metricKeys="ncloc,coverage,duplicated_lines_density,code_smells,reliability_rating,security_rating",
    )["component"]["measures"]
    medidas = {m["metric"]: m.get("value", m.get("period", {}).get("value", "—")) for m in medidas}

    filas = [
        ("Bugs", total_issues("BUG")),
        ("Vulnerabilities", total_issues("VULNERABILITY")),
        ("Security Hotspots por revisar", total_hotspots()),
        ("Code Smells", total_issues("CODE_SMELL")),
    ]
    estado = gate["status"]
    lineas = [
        "# Reporte SonarQube — NotaryVerify",
        "",
        f"- Proyecto: `{PROYECTO}`" + (f" · Pull request #{PR}" if PR else ""),
        f"- Quality Gate: **{'✅ APROBADO' if estado == 'OK' else '❌ ' + estado}**",
        f"- Panel: {HOST}/dashboard?id={urllib.parse.quote(PROYECTO)}",
        "",
        "| Categoría | Abiertos | Resultado |",
        "| --- | --- | --- |",
        *[f"| {nombre} | {total} | {'✅ superado' if total == 0 else '⚠️ revisar'} |" for nombre, total in filas],
        "",
        "| Métrica | Valor |",
        "| --- | --- |",
        *[f"| {clave} | {valor} |" for clave, valor in sorted(medidas.items())],
        "",
        "| Condición del Quality Gate | Valor | Umbral | Estado |",
        "| --- | --- | --- | --- |",
        *[
            f"| {c['metricKey']} | {c.get('actualValue', '—')} | {c.get('errorThreshold', '—')} | {c['status']} |"
            for c in gate.get("conditions", [])
        ],
    ]
    texto = "\n".join(lineas) + "\n"
    with open(salida, "w", encoding="utf-8") as archivo:
        archivo.write(texto)
    if resumen := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(resumen, "a", encoding="utf-8") as archivo:
            archivo.write(texto)
    print(texto)
    return 1 if estado == "ERROR" else 0


if __name__ == "__main__":
    sys.exit(main())
