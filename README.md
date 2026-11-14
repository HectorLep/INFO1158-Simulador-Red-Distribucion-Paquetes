# Simulador de una red de distribución de paquetes

Proyecto 2 · Teoría de Grafos (INFO1158) · Proyecto práctico final.

Aplicación que modela una red logística como un **grafo dirigido con capacidades** y
calcula, con algoritmos escritos por el equipo y sin bibliotecas de grafos:

- el **flujo máximo** de paquetes por hora entre un origen y un destino (algoritmo de
  **Edmonds–Karp**: el método de Ford–Fulkerson con búsqueda en anchura);
- un **corte mínimo** (la partición S/T y las rutas de S a T que limitan el flujo);
- la **verificación** de capacidad, conservación y flujo máximo = capacidad del corte.

La interfaz (Streamlit) permite desactivar y reactivar rutas, modificar capacidades,
agregar conexiones, cambiar el origen y el destino, recalcular y restaurar la red inicial.

## Requisitos

- Windows con PowerShell.
- **Python 3.11 o posterior** (probado con Python 3.13.5). Para comprobarlo:
  `python --version`.
- Conexión a internet la primera vez, para instalar las dependencias.

## Instalación y ejecución en Windows (PowerShell)

Todos los comandos se ejecutan **desde la carpeta raíz del repositorio**, la que contiene
este archivo.

```powershell
# 1. Clonar el repositorio (pide iniciar sesión en GitHub, porque es privado)
git clone https://github.com/HectorLep/INFO1158-Simulador-Red-Distribucion-Paquetes.git
cd INFO1158-Simulador-Red-Distribucion-Paquetes

# 2. Crear un entorno virtual e instalar las dependencias
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r proyecto2/requirements.txt

# 3. Abrir la aplicación (se abre en http://localhost:8501; Ctrl + C para detenerla)
.\.venv\Scripts\python.exe -m streamlit run proyecto2/app.py
```

Si el repositorio se descarga como ZIP (botón «Code → Download ZIP»), descomprimirlo y
empezar en el paso 2 desde la carpeta descomprimida.

Si en el paso 2 `pip` termina con `OSError: [Errno 2] No such file or directory` y una ruta
muy larga, Windows alcanzó su límite de 260 caracteres por ruta: clonar el repositorio en
una carpeta de ruta corta (por ejemplo `C:\Proyectos`) y repetir el paso 2.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s proyecto2/tests -v
```

Resultado esperado: `Ran 81 tests` y `OK`. Las 11 pruebas de `test_interfaz.py` accionan
los controles de la aplicación sin abrir un navegador.

Informe de consola con las tres configuraciones analizadas y el caso manual:

```powershell
.\.venv\Scripts\python.exe proyecto2/verificacion.py
```

## Contenido del repositorio

| Ruta | Contenido |
|---|---|
| `proyecto2/` | Aplicación, algoritmos, datos, pruebas y documentación. Detalle en [`proyecto2/README.md`](proyecto2/README.md) |
| `proyecto2/INFORME_BORRADOR.pdf` | Informe técnico en PDF (fuente: `INFORME_BORRADOR.md`) |
| `proyecto2/GUIA_DE_ESTUDIO.md` | Explicación del modelo, del algoritmo y del código |
| `proyecto2/CUMPLIMIENTO.md` | Matriz requisito → código → prueba → evidencia |
| `proyecto2/GUION_PRESENTACION.md` | Guion de la presentación de 12 minutos |
| `datos_referencia/` | Datos de referencia que una de las pruebas compara con los de `proyecto2/datos/` |
| `herramientas/generar_informe_pdf.py` | Genera el PDF del informe a partir del Markdown (no forma parte de la aplicación) |
| `.streamlit/config.toml` | Apariencia de la aplicación |

## Regenerar el informe en PDF (opcional)

Requiere Microsoft Edge o Google Chrome y el paquete `markdown`:

```powershell
.\.venv\Scripts\python.exe -m pip install markdown
.\.venv\Scripts\python.exe herramientas/generar_informe_pdf.py
```

## Tecnología

Python, Streamlit (interfaz) y Plotly (dibujo de nodos, flechas y etiquetas). Los
algoritmos usan solo estructuras básicas de Python y `collections.deque`; las pruebas usan
`unittest` de la biblioteca estándar.
