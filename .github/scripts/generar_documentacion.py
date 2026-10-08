"""Genera la sección automática del README.md a partir del código.

Uso: python .github/scripts/generar_documentacion.py [--check]

Produce, entre los marcadores AUTODOC del README: diccionario de datos,
diagrama entidad-relación, diagrama de clases, diagrama de componentes y
diagrama de despliegue (Mermaid). Los modelos se leen de SQLAlchemy y las
clases/componentes mediante análisis estático (ast), sin ejecutar servicios.
Con --check sale con código 1 si el README no está actualizado.
"""

from __future__ import annotations

import ast
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
README = ROOT / "README.md"
INICIO = "<!-- AUTODOC:INICIO -->"
FIN = "<!-- AUTODOC:FIN -->"

# Importar los modelos no debe crear datos runtime dentro del repositorio.
os.environ.setdefault("NOTARYVERIFY_DATA_DIR", tempfile.mkdtemp(prefix="notaryverify-doc-"))
sys.path.insert(0, str(BACKEND))

from app.core.database import Base  # noqa: E402
from app.models import db_models  # noqa: E402,F401


def _tipo(columna) -> str:
    try:
        return str(columna.type)
    except Exception:  # tipos sin representación SQL genérica
        return type(columna.type).__name__


def diccionario_datos() -> str:
    partes = []
    for tabla in sorted(Base.metadata.tables.values(), key=lambda t: t.name):
        clase = next((m.class_.__name__ for m in Base.registry.mappers if m.local_table is tabla), tabla.name)
        partes.append(f"#### `{tabla.name}` ({clase})\n")
        partes.append("| Columna | Tipo | PK | FK | Nulo | Único | Índice |")
        partes.append("| --- | --- | --- | --- | --- | --- | --- |")
        for col in tabla.columns:
            fk = ", ".join(f"`{f.target_fullname}`" for f in col.foreign_keys) or ""
            partes.append(
                f"| `{col.name}` | {_tipo(col)} | {'Sí' if col.primary_key else ''} | {fk} | "
                f"{'Sí' if col.nullable and not col.primary_key else 'No'} | {'Sí' if col.unique else ''} | "
                f"{'Sí' if col.index else ''} |"
            )
        partes.append("")
    return "\n".join(partes)


def _tipo_mermaid(columna) -> str:
    return _tipo(columna).split("(")[0].replace(" ", "_")


def diagrama_er() -> str:
    lineas = ["```mermaid", "erDiagram"]
    relaciones = set()
    for tabla in sorted(Base.metadata.tables.values(), key=lambda t: t.name):
        lineas.append(f"    {tabla.name} {{")
        for col in tabla.columns:
            marca = " PK" if col.primary_key else (" FK" if col.foreign_keys else (" UK" if col.unique else ""))
            lineas.append(f"        {_tipo_mermaid(col)} {col.name}{marca}")
        lineas.append("    }")
        for col in tabla.columns:
            for fk in col.foreign_keys:
                destino = fk.column.table.name
                cardinalidad = "||--o|" if col.unique else "||--o{"
                relaciones.add(f"    {destino} {cardinalidad} {tabla.name} : \"{col.name}\"")
    lineas.extend(sorted(relaciones))
    lineas.append("```")
    return "\n".join(lineas)


def _clases_python(carpeta: Path) -> dict[str, dict]:
    """Clases públicas por módulo: métodos públicos e importaciones de app.*."""
    resultado = {}
    for archivo in sorted(carpeta.glob("*.py")):
        if archivo.name == "__init__.py":
            continue
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        importados = set()
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.module.startswith("app."):
                importados.update(alias.name for alias in nodo.names)
                importados.add(nodo.module.rsplit(".", 1)[-1])
        clases = []
        for nodo in arbol.body:
            if isinstance(nodo, ast.ClassDef) and not nodo.name.startswith("_"):
                metodos = [
                    f.name for f in nodo.body
                    if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and not f.name.startswith("_")
                ]
                bases = [b.id for b in nodo.bases if isinstance(b, ast.Name)]
                clases.append({"nombre": nodo.name, "metodos": metodos, "bases": bases})
        resultado[archivo.stem] = {"clases": clases, "importa": importados}
    return resultado


def diagrama_clases() -> str:
    lineas = ["```mermaid", "classDiagram", "    direction LR"]
    modelos = {m.class_.__name__: m for m in Base.registry.mappers}
    for nombre in sorted(modelos):
        tabla = modelos[nombre].local_table
        lineas.append(f"    class {nombre} {{")
        lineas.append("        <<entity>>")
        for col in tabla.columns:
            lineas.append(f"        +{_tipo_mermaid(col)} {col.name}")
        lineas.append("    }")
    relaciones = set()
    for nombre, mapper in modelos.items():
        for rel in mapper.relationships:
            if rel.direction.name == "ONETOMANY":
                relaciones.add(f"    {nombre} \"1\" --> \"*\" {rel.mapper.class_.__name__}")
        for col in mapper.local_table.columns:
            for fk in col.foreign_keys:
                destino = next((m.class_.__name__ for m in Base.registry.mappers if m.local_table is fk.column.table), None)
                if destino and not any(f"{destino} \"1\" --> \"*\" {nombre}" in r for r in relaciones):
                    relaciones.add(f"    {destino} \"1\" -- \"*\" {nombre} : {col.name}")

    servicios = _clases_python(BACKEND / "app" / "services")
    for modulo, info in servicios.items():
        for clase in info["clases"]:
            if "Exception" in clase["bases"] or clase["nombre"].endswith("Error"):
                continue
            lineas.append(f"    class {clase['nombre']} {{")
            lineas.append("        <<service>>")
            for metodo in clase["metodos"]:
                lineas.append(f"        +{metodo}()")
            lineas.append("    }")
            for usado in sorted(info["importa"] & set(modelos)):
                relaciones.add(f"    {clase['nombre']} ..> {usado} : usa")
    lineas.extend(sorted(relaciones))
    lineas.append("```")
    return "\n".join(lineas)


def diagrama_componentes() -> str:
    rutas = _clases_python(BACKEND / "app" / "api")
    servicios = _clases_python(BACKEND / "app" / "services")
    lineas = [
        "```mermaid",
        "flowchart LR",
        "    subgraph Cliente[\"Frontend estático\"]",
        "        estacion[\"Estación y administración<br/>index.html\"]",
        "        dashboard[\"Dashboard de uso<br/>dashboard.html\"]",
        "    end",
        "    subgraph API[\"backend/app/api\"]",
    ]
    for modulo in sorted(rutas):
        lineas.append(f"        {modulo}[\"{modulo}\"]")
    lineas.append("    end")
    lineas.append("    subgraph Servicios[\"backend/app/services\"]")
    for modulo in sorted(servicios):
        lineas.append(f"        {modulo}[\"{modulo}\"]")
    lineas.extend([
        "    end",
        "    subgraph Core[\"backend/app/core\"]",
        "        database[(\"SQLite<br/>notaryverify.db\")]",
        "        seguridad[\"seguridad / observabilidad\"]",
        "    end",
        "    estacion -->|HTTP JSON| API",
        "    dashboard -->|HTTP JSON| API",
    ])
    for modulo, info in sorted(rutas.items()):
        for servicio in sorted(info["importa"] & set(servicios)):
            lineas.append(f"    {modulo} --> {servicio}")
    lineas.append("    Servicios --> database")
    lineas.append("```")
    return "\n".join(lineas)


def diagrama_despliegue() -> str:
    return "\n".join([
        "```mermaid",
        "flowchart TB",
        "    usuario([\"Operador / Administrador / Auditor<br/>navegador\"])",
        "    subgraph GitHub[\"GitHub\"]",
        "        actions[\"GitHub Actions<br/>CI · Sonar · Semgrep · Snyk · Release\"]",
        "        ghcr[(\"GitHub Container Registry<br/>imágenes backend y frontend\")]",
        "        pages[\"GitHub Pages<br/>documentación técnica\"]",
        "    end",
        "    subgraph Azure[\"Azure (Terraform: infra/terraform)\"]",
        "        rg[\"Resource Group\"]",
        "        plan[\"App Service Plan Linux\"]",
        "        front[\"Web App frontend<br/>python http.server :5500\"]",
        "        back[\"Web App backend<br/>FastAPI/uvicorn :8000\"]",
        "        datos[(\"/home/data<br/>SQLite + archivos runtime\")]",
        "    end",
        "    subgraph Local[\"Desarrollo local (docker-compose.yml)\"]",
        "        cfront[\"contenedor frontend :5500\"]",
        "        cback[\"contenedor backend :8000\"]",
        "        vol[(\"volumen notaryverify-data\")]",
        "    end",
        "    actions -->|docker push| ghcr",
        "    actions -->|terraform apply| rg",
        "    actions -->|pdoc| pages",
        "    rg --> plan --> front & back",
        "    ghcr -->|imagen| front & back",
        "    back --> datos",
        "    usuario -->|HTTPS| front",
        "    usuario -->|HTTPS API| back",
        "    cfront --> cback --> vol",
        "```",
    ])


def generar() -> str:
    return "\n\n".join([
        INICIO,
        "## Documentación generada automáticamente",
        "> Sección regenerada por `.github/workflows/documentacion-readme.yml` con "
        "`python .github/scripts/generar_documentacion.py`. No editar a mano.",
        "### Diccionario de datos",
        diccionario_datos().rstrip(),
        "### Diagrama entidad-relación",
        diagrama_er(),
        "### Diagrama de clases",
        diagrama_clases(),
        "### Diagrama de componentes",
        diagrama_componentes(),
        "### Diagrama de despliegue",
        diagrama_despliegue(),
        FIN,
    ]) + "\n"


def main() -> int:
    contenido = README.read_text(encoding="utf-8").replace("\r\n", "\n")
    seccion = generar()
    if INICIO in contenido and FIN in contenido:
        antes = contenido.split(INICIO, 1)[0]
        despues = contenido.split(FIN, 1)[1].lstrip("\n")
        nuevo = antes + seccion + (("\n" + despues) if despues else "")
    else:
        nuevo = contenido.rstrip("\n") + "\n\n" + seccion
    if "--check" in sys.argv:
        if nuevo != contenido:
            print("README.md desactualizado: ejecute python .github/scripts/generar_documentacion.py")
            return 1
        print("README.md actualizado.")
        return 0
    README.write_text(nuevo, encoding="utf-8", newline="\n")
    print("Sección automática del README regenerada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
