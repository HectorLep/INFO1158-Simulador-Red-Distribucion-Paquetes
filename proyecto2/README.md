# Proyecto 2 · Simulador de una red de distribución de paquetes

Teoría de Grafos (INFO1158). Aplicación que modela una red logística como un **grafo
dirigido con capacidades** y calcula, con algoritmos escritos por el equipo:

1. el **flujo máximo** de paquetes por hora entre un origen y un destino — algoritmo de
   **Edmonds–Karp** (método de Ford–Fulkerson con búsqueda en anchura);
2. un **corte mínimo**: la partición S/T y las rutas de S a T que limitan ese flujo;
3. la **verificación** de que el flujo respeta las capacidades, se conserva en los centros
   intermedios y coincide con la capacidad del corte.

No se usa ninguna biblioteca de grafos. Streamlit dibuja la interfaz y Plotly solo
representa círculos, flechas y etiquetas.

## Requisitos

- Python 3.11 o posterior (probado con Python 3.13.5 de Miniconda).
- Dependencias de `requirements.txt` (probado con Streamlit 1.67.0, Plotly 7.1.0 y pandas 3.1.1).

## Ejecución en Windows (PowerShell)

Abrir PowerShell en la carpeta raíz (la que contiene `proyecto2/`). El comando `py` no es
necesario; se usa `python`.

**Opción A — con un entorno virtual `.venv` ya creado en la carpeta raíz** (si no existe,
por ejemplo en un clon recién descargado, usar la opción C):

```powershell
.\.venv\Scripts\python.exe -m streamlit run proyecto2/app.py
```

**Opción B — con el Python de Conda:**

```powershell
python -m pip install -r proyecto2/requirements.txt
python -m streamlit run proyecto2/app.py
```

**Opción C — en otra computadora, creando un entorno nuevo:**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r proyecto2/requirements.txt
.\.venv\Scripts\python.exe -m streamlit run proyecto2/app.py
```

El navegador se abre en `http://localhost:8501`. Para detener la aplicación: `Ctrl + C` en
PowerShell.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s proyecto2/tests -v
```

- 72 pruebas del modelo, los algoritmos y los escenarios: solo necesitan la biblioteca
  estándar (también funcionan con `python -m unittest discover -s proyecto2/tests -v`).
- 11 pruebas de interfaz (`test_interfaz.py`): accionan los controles de la aplicación sin
  navegador; necesitan Streamlit y se omiten automáticamente si no está instalado.

Para revisar formato e imports desde la raíz:

```powershell
python -m black proyecto2 herramientas
python -m ruff check proyecto2 herramientas
```

Informe de consola con los tres escenarios y el caso manual (evidencia reproducible):

```powershell
python proyecto2/verificacion.py
```

## Archivos

| Archivo | Contenido |
|---|---|
| `grafo.py` | La red como diccionario: cargar, validar, desactivar/reactivar rutas, cambiar capacidades, agregar conexiones, cambiar origen y destino. |
| `algoritmos.py` | Red residual, búsqueda de caminos aumentantes (BFS; DFS solo para comparar), flujo máximo y corte mínimo. |
| `verificacion.py` | Comprobaciones matemáticas (capacidad, conservación, valor, corte) y los tres escenarios. |
| `dibujo.py` | Figura del grafo con Plotly (solo representación). |
| `app.py` | Interfaz Streamlit. |
| `datos/red_inicial.json` | Red inicial: 11 centros y 18 rutas con capacidades. |
| `datos/caso_manual.json` | Caso de verificación manual: 5 centros y 6 rutas. |
| `tests/` | Pruebas `unittest`. |
| `capturas/` | Capturas reales de la aplicación en ejecución. |
| `GUIA_DE_ESTUDIO.md` | Explicación completa para estudiar y defender el proyecto. |
| `INFORME_BORRADOR.md` | Borrador del informe técnico (fuente del PDF). |
| `GUION_PRESENTACION.md` | Guion de 12 minutos y guía de demostración. |
| `CUMPLIMIENTO.md` | Matriz requisito → código → prueba → evidencia. |

## Uso rápido de la interfaz

1. **Panel lateral**: cambiar origen y destino, desactivar o reactivar una ruta, modificar una
   capacidad (1 a 12), agregar una conexión.
2. Tras cualquier cambio, pulsar **Calcular / Recalcular**. Mientras hay cambios sin calcular,
   la aplicación oculta los resultados anteriores para no mostrar datos que ya no corresponden.
3. **Mostrar en el grafo**: capacidades, flujo máximo (etiquetas `flujo/capacidad`) o corte
   mínimo (conjuntos S y T y rutas del corte).
4. **Restaurar red inicial** descarta todos los cambios.
5. Pestañas inferiores: resultados, verificación, algoritmo paso a paso, escenarios, modelo
   matemático y caso manual.

## Resultados de referencia (calculados por el código)

| Escenario | Flujo máximo | Corte mínimo hallado | Capacidad del corte |
|---|---:|---|---:|
| Red inicial | 18 paq./h | {C → G (3), F → T (2), H → T (8), I → T (5)} | 18 |
| Desactivar H → T | 10 paq./h | {C → G (3), F → T (2), I → T (5)} | 10 |
| Capacidad de I → T: 5 → 10 | 20 paq./h | {O → A (8), O → B (7), O → C (5)} | 20 |
| Caso manual (5 vértices) | 8 paq./h | {A → T (3), C → T (5)} | 8 |
