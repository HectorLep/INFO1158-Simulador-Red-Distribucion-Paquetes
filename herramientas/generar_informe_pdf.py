"""
Convierte el informe en Markdown a PDF.

Uso, desde la carpeta raíz:

    .venv/Scripts/python.exe herramientas/generar_informe_pdf.py
    .venv/Scripts/python.exe herramientas/generar_informe_pdf.py proyecto2/INFORME_BORRADOR.md

Pasos: 1) Markdown -> HTML con el paquete `markdown`;
       2) HTML -> PDF con Microsoft Edge (o Chrome) en modo sin ventana.
El PDF queda junto al archivo .md, con el mismo nombre.

Requisito: el paquete `markdown`  (python -m pip install markdown).
No forma parte de la aplicación: solo sirve para preparar la entrega.
"""

import subprocess
import sys
from pathlib import Path

import markdown

NAVEGADORES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

ESTILO = """
@page { size: A4; margin: 2cm 2cm 2.2cm 2cm;
        @bottom-center { content: counter(page); font-family: 'Segoe UI', Arial, sans-serif;
                         font-size: 9pt; color: #444; } }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; line-height: 1.45;
       color: #111; }
h1 { font-size: 21pt; margin: 0 0 4pt 0; }
h2 { font-size: 14pt; margin-top: 20pt; border-bottom: 1px solid #bbb; padding-bottom: 3pt;
     break-after: avoid; }
h3 { font-size: 11.5pt; margin-top: 14pt; break-after: avoid; }
p, li { text-align: justify; }
/* La frase que presenta una tabla o un bloque de código no se separa de él. */
p:has(+ table), p:has(+ pre) { break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9.5pt;
        break-inside: avoid; }
th, td { border: 1px solid #999; padding: 3pt 6pt; vertical-align: top; text-align: left; }
th { background: #eef1f5; }
img { display: block; max-width: 100%; max-height: 17cm; margin: 10pt auto 4pt auto;
      border: 1px solid #ccc; }
p:has(> img) { break-inside: avoid; text-align: center; }
p:has(> img) + p { text-align: center; font-size: 9pt; color: #444; break-before: avoid; }
pre { background: #f4f4f1; padding: 8pt; font-size: 9pt; border: 1px solid #ddd;
      white-space: pre-wrap; break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 9.5pt; }
hr { border: 0; border-top: 1px solid #bbb; margin: 14pt 0; }
"""


def buscar_navegador():
    """Devuelve la ruta de Edge o Chrome, o None si no se encuentra ninguno."""
    for ruta in NAVEGADORES:
        if Path(ruta).exists():
            return ruta
    return None


def convertir(archivo_md):
    """Genera el PDF de `archivo_md` en su misma carpeta y devuelve su ruta."""
    archivo_md = Path(archivo_md).resolve()
    texto = archivo_md.read_text(encoding="utf-8")
    cuerpo = markdown.markdown(texto, extensions=["tables", "fenced_code"])
    # El título del PDF es el del informe (primera línea "# ..."), no el nombre del archivo.
    titulo = archivo_md.stem
    for linea in texto.splitlines():
        if linea.startswith("# "):
            titulo = linea[2:].strip()
            break
    html = (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        f"<title>{titulo}</title><style>{ESTILO}</style></head>"
        f"<body>{cuerpo}</body></html>"
    )
    # El HTML se guarda junto al .md para que las imágenes relativas (capturas/...) se encuentren.
    archivo_html = archivo_md.with_suffix(".html")
    archivo_pdf = archivo_md.with_suffix(".pdf")
    archivo_html.write_text(html, encoding="utf-8")

    navegador = buscar_navegador()
    if navegador is None:
        print("No se encontró Edge ni Chrome. Abre este archivo en un navegador y usa "
              f"Imprimir > Guardar como PDF:\n  {archivo_html}")
        return None
    subprocess.run(
        [navegador, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={archivo_pdf}", archivo_html.as_uri()],
        check=True, capture_output=True, timeout=120,
    )
    archivo_html.unlink()                     # el HTML intermedio ya no hace falta
    return archivo_pdf


if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else "proyecto2/INFORME_BORRADOR.md"
    resultado = convertir(entrada)
    if resultado is not None:
        print(f"PDF generado: {resultado}")
