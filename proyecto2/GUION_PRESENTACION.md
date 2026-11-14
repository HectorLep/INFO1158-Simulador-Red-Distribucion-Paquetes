# Guion de presentación · Proyecto 2 (12 minutos, tres integrantes)

Presentación presencial del jueves 26 de noviembre de 2026. Duración máxima: **12 minutos**.
La rúbrica exige: exponer el problema y el modelo, justificar el algoritmo, demostrar la
aplicación (red, flujo máximo, corte mínimo), hacer una **modificación interactiva** que
permita comparar resultados, y que participen los tres.

Los nombres «Integrante 1, 2 y 3» deben sustituirse por los reales. El reparto está pensado
para que cada uno hable de teoría **y** toque la aplicación.

## Reparto y tiempos

| Tiempo | Quién | Bloque | En pantalla |
|---|---|---|---|
| 0:00 – 1:15 | Integrante 1 | Problema | App abierta, modo «Capacidades» |
| 1:15 – 3:15 | Integrante 1 | Modelo matemático | Pestaña «Modelo matemático» |
| 3:15 – 5:45 | Integrante 2 | Algoritmos y justificación | Pestaña «Algoritmo paso a paso» |
| 5:45 – 7:45 | Integrante 2 | Demostración: flujo máximo y corte mínimo | Modos «Flujo máximo» y «Corte mínimo» |
| 7:45 – 10:15 | Integrante 3 | Modificaciones interactivas y comparación | Panel lateral + pestaña «Escenarios» |
| 10:15 – 11:15 | Integrante 3 | Verificación (caso manual y comprobaciones) | Pestañas «Caso manual» y «Verificación» |
| 11:15 – 12:00 | Los tres | Conclusiones | Pestaña «Escenarios» |

Margen de seguridad: ensayar para terminar en **11:30**.

## Antes de empezar (checklist de 5 minutos)

1. Abrir PowerShell en la carpeta raíz y ejecutar:
   `.\.venv\Scripts\python.exe -m streamlit run proyecto2/app.py`
2. Esperar a que el navegador muestre el grafo con «18 paq./h» y «✔ 7 de 7».
3. Poner el navegador en pantalla completa (F11) y el zoom en 90 % si el proyector es pequeño.
4. Dejar seleccionado el modo **Capacidades**.
5. Tener abierta una segunda pestaña del navegador con la misma dirección, como respaldo.
6. Si algo queda en un estado raro durante la demo: botón **↺ Restaurar red inicial**.

## Bloque 1 — Problema (Integrante 1, 1:15)

**Qué decir:**

> «Una empresa reparte paquetes por una red de centros logísticos. Cada ruta tiene un
> sentido y una capacidad máxima en paquetes por hora. La pregunta es: ¿cuántos paquetes
> por hora pueden llegar, como máximo, del centro de origen al de destino? No basta mirar
> lo que sale del origen: una ruta ancha no sirve si las siguientes son estrechas.
> Nuestra aplicación calcula ese máximo, muestra cuánto lleva cada ruta, señala las rutas
> que limitan la red y permite ver qué ocurre si la red cambia.»

**Qué mostrar:** el grafo en modo «Capacidades». Señalar O (origen), T (destino) y una
etiqueta de capacidad.

## Bloque 2 — Modelo matemático (Integrante 1, 2:00)

**Qué hacer:** clic en la pestaña **Modelo matemático**.

**Qué decir:**

> «Lo modelamos como un grafo dirigido G = (V, E) con una función de capacidad c. Los 11
> vértices son centros logísticos; los 18 arcos son rutas; c da a cada ruta un entero de 1
> a 12 paquetes por hora. Un flujo x dice cuántos paquetes lleva cada ruta y debe cumplir
> dos condiciones: no superar la capacidad, y conservarse en los centros intermedios, es
> decir, lo que entra a un centro es lo que sale. El valor del flujo es lo que sale, neto,
> del origen.
>
> La red cumple las restricciones del enunciado: entre 10 y 12 vértices, entre 15 y 20
> arcos, capacidades de 1 a 12, sin lazos, sin arcos repetidos ni recíprocos, ningún
> vértice aislado y al menos dos caminos del origen al destino; de hecho hay 11. Esto no lo
> afirmamos nosotros: lo comprueba el programa, en esta tabla.»

**Qué mostrar:** la tabla «Condiciones de la configuración inicial» con los cuatro ✔.

## Bloque 3 — Algoritmos y justificación (Integrante 2, 2:30)

**Qué hacer:** clic en la pestaña **Algoritmo paso a paso**.

**Qué decir:**

> «Investigamos dos estrategias. Las dos pertenecen al método de Ford–Fulkerson: se empieza
> con flujo cero y, mientras exista un camino aumentante, se envía por él todo lo que cabe.
> La diferencia está en cómo se busca ese camino. Con búsqueda en profundidad se toma el
> primero que aparece, y el número de pasos puede depender de las capacidades. Edmonds–Karp
> usa búsqueda en anchura y toma siempre el camino con menos arcos; así el número de pasos
> queda acotado por el tamaño de la red, sin depender de las capacidades. Edmonds–Karp no
> es otro método: es Ford–Fulkerson con BFS.
>
> Elegimos Edmonds–Karp por esa garantía, porque es sistemático y se puede repetir a mano,
> y porque el mismo BFS nos sirve después para el corte mínimo.
>
> El algoritmo trabaja sobre la red residual. Por cada ruta con capacidad c y flujo x hay
> un arco directo con lo que todavía cabe, c menos x, y un arco inverso con lo que se podría
> retirar, x. El arco inverso no es una ruta: es la posibilidad de deshacer parte de una
> decisión anterior. En cada paso se busca un camino con BFS, se calcula su cuello de
> botella, que es la menor capacidad residual del camino, y se envía esa cantidad.
>
> Aquí están los seis pasos en nuestra red: el primero, O–B–F–T, envía 2; el tercero,
> O–A–D–H–T, envía 6; al final se acumulan 18.»

**Qué mostrar:** la tabla de pasos. Abrir el desplegable **Comparación con Ford–Fulkerson
usando DFS** y señalar el paso 2 de DFS:

> «Con DFS se llega al mismo valor, 18, pero el segundo camino tiene seis arcos y usa el
> arco inverso H → D: había llenado D → H y tuvo que devolver 2. Es un ejemplo real de para
> qué sirven los arcos inversos.»

## Bloque 4 — Demostración: flujo máximo y corte mínimo (Integrante 2, 2:00)

**Qué hacer:**

1. Pulsar **▶ Calcular / Recalcular** (para mostrar la ejecución del algoritmo).
2. Elegir el modo **Flujo máximo**.

**Qué decir:**

> «Al pulsar Calcular se ejecuta nuestro algoritmo. El flujo máximo es 18 paquetes por
> hora. Cada etiqueta es flujo sobre capacidad: O → A lleva 8 de 8, A → E lleva 2 de 3. El
> azul oscuro marca las rutas saturadas y el grosor crece con el flujo.»

3. Elegir el modo **Corte mínimo**.

> «Para el corte mínimo usamos la última red residual: los centros todavía alcanzables
> desde el origen forman el conjunto S, en celeste; el resto es T, en naranja. Las rutas
> que van de S a T, en rojo, son el corte: C → G, F → T, H → T e I → T. Sus capacidades
> suman 3 + 2 + 8 + 5 = 18, exactamente el flujo máximo. Es el teorema de flujo máximo y
> corte mínimo: esas rutas están llenas y son el cuello de botella de la red.»

**Qué mostrar:** el indicador «Capacidad del corte mínimo 18 paq./h» junto a «Flujo máximo
18 paq./h».

## Bloque 5 — Modificaciones interactivas (Integrante 3, 2:30)

**Modificación A: desactivar una ruta.**

1. En el panel lateral, «Desactivar o reactivar una ruta» → elegir **H → T** → **Desactivar ruta**.

> «Desactivo H → T. La aplicación oculta los resultados anteriores y pide recalcular: nunca
> muestra números que no correspondan a la red en pantalla.»

2. Pulsar **▶ Calcular ahora**. Elegir el modo **Flujo máximo**.

> «El flujo baja de 18 a 10. Se pierden exactamente 8, la capacidad de la ruta, porque
> estaba en el corte mínimo y las demás entradas al destino ya estaban llenas. H se queda
> sin salida y deja de recibir paquetes.»

3. Pulsar **Reactivar ruta** y **▶ Calcular ahora** → vuelve a 18.

**Modificación B: cambiar una capacidad.**

4. En «Modificar una capacidad» → ruta **I → T** → nueva capacidad **10** → **Cambiar capacidad** → **▶ Calcular ahora**. Elegir el modo **Corte mínimo**.

> «Amplío I → T de 5 a 10. Podría pensarse que el flujo sube 5, pero sube solo 2, a 20. El
> cuello de botella se trasladó: ahora el corte son las tres rutas que salen del origen,
> 8 + 7 + 5 = 20. Ampliar una ruta ayuda solo hasta que aparece otro límite.»

**Modificación C (10 segundos): una conexión prohibida.**

5. En «Agregar una conexión» → Desde **A**, Hacia **O** → **Agregar conexión**.

> «Si intento agregar A → O, se rechaza: sería recíproca de O → A. Tampoco se admiten
> lazos, rutas repetidas ni capacidades fuera de 1 a 12.»

6. Pulsar **↺ Restaurar red inicial**.

**Comparación.** Clic en la pestaña **Escenarios**.

> «Esta tabla compara las tres configuraciones partiendo siempre de la red original:
> inicial 18, sin H → T 10, con I → T ampliada 20. En las tres, el flujo máximo coincide
> con la capacidad del corte.»

## Bloque 6 — Verificación (Integrante 3, 1:00)

**Qué hacer:** clic en **Caso manual**; después, en **Verificación**.

**Qué decir:**

> «Resolvimos a mano un caso de cinco vértices. Encontramos un flujo de valor 8 y un corte
> de capacidad 8; como ningún flujo puede superar a un corte, los dos son óptimos. El
> código también obtiene 8 y el mismo corte. El reparto por ruta es distinto, y eso es
> correcto: el valor máximo es único, la distribución no.
>
> Además, el programa verifica cada resultado: capacidades, conservación en cada centro,
> valor neto y la igualdad con el corte. Y tenemos 81 pruebas automáticas, que incluyen
> calcular el corte mínimo por fuerza bruta en todas las particiones posibles.»

## Bloque 7 — Conclusiones (los tres, 0:45)

- **Integrante 1:** «El problema logístico se traduce directamente a un flujo máximo en un
  grafo dirigido con capacidades.»
- **Integrante 2:** «Edmonds–Karp lo resuelve con un código corto y con una garantía que no
  depende de las capacidades; los arcos inversos son la clave para corregir decisiones.»
- **Integrante 3:** «El corte mínimo certifica que el flujo es óptimo y dice dónde está el
  cuello de botella; por eso desactivar H → T cuesta 8 y ampliar I → T solo aporta 2.»

---

## Guía de demostración (para no improvisar)

| Paso | Acción exacta | Resultado que debe verse |
|---|---|---|
| 1 | Abrir la app | Flujo máximo 18 paq./h; corte 18 paq./h; 6 caminos; ✔ 7 de 7 |
| 2 | Pestaña «Modelo matemático» | \|V\| = 11, 18 arcos, cuatro condiciones con ✔ |
| 3 | Pestaña «Algoritmo paso a paso» | 6 pasos; acumulado 2, 5, 11, 13, 17, 18 |
| 4 | Abrir el desplegable de DFS | 6 pasos; el 2.º usa H → D |
| 5 | «Calcular / Recalcular» y modo «Flujo máximo» | Etiquetas x/c; H → T 8/8 |
| 6 | Modo «Corte mínimo» | A, B, C, D, E, F, H, I en celeste (S, junto con O); G en naranja claro (T, junto con el destino); 4 rutas rojas; 3 + 2 + 8 + 5 = 18 |
| 7 | Desactivar H → T | Aviso amarillo; indicadores en «—» |
| 8 | «Calcular ahora» | 10 paq./h; 4 caminos; H → T punteada |
| 9 | Reactivar H → T y calcular | 18 paq./h |
| 10 | Capacidad de I → T a 10 y calcular | 20 paq./h; corte {O→A, O→B, O→C} |
| 11 | Agregar A → O | Mensaje rojo: arcos recíprocos |
| 12 | «Restaurar red inicial» | 18 paq./h |
| 13 | Pestaña «Escenarios» | Tabla 18 / 10 / 20 |
| 14 | Pestaña «Caso manual» | Manual 8, código 8; corte {A → T (3), C → T (5)} |
| 15 | Pestaña «Verificación» | 7 comprobaciones con ✔ |

Todos estos resultados se comprobaron en la aplicación real (capturas en `capturas/` y
pruebas `tests/test_interfaz.py`).

**Plan B.** Si el navegador falla: cerrar la pestaña y abrir `http://localhost:8501` de
nuevo. Si falla Streamlit: ejecutar `python proyecto2/verificacion.py`, que imprime en
consola los mismos resultados, y apoyarse en las capturas del informe.

## Diapositivas sugeridas (opcionales, 5 como máximo)

La demostración en vivo es el centro de la exposición; las diapositivas solo acompañan.

1. Título, integrantes y la pregunta: «¿cuántos paquetes por hora llegan como máximo?»
2. Modelo: G = (V, E), c, capacidad y conservación, valor del flujo.
3. Ford–Fulkerson con DFS frente a Edmonds–Karp con BFS (tabla comparativa del informe).
4. Red residual y arco inverso (ejemplo de la sección 6.4 de la guía).
5. Tabla de las tres configuraciones y conclusiones.

## Preguntas probables del profesor y respuestas

**¿Por qué Edmonds–Karp y no Ford–Fulkerson con DFS?**
Porque BFS acota el número de aumentos por O(|V|·|E|) sin depender de las capacidades, da
caminos cortos reproducibles a mano y el mismo recorrido sirve para el corte. En nuestra
red ambas dan 18 con 6 caminos, pero DFS genera un camino de 6 arcos con un arco inverso.

**¿Qué es exactamente un arco inverso?**
Un arco de la red residual, v → u, con capacidad igual al flujo actual de la ruta u → v.
Usarlo significa restar flujo a esa ruta. No es una ruta de transporte.

**¿En su red se usa algún arco inverso?**
Con BFS, no en la red inicial. Con DFS sí (H → D). Y en las pruebas tenemos una red de 8
vértices donde BFS lo necesita: sin él se quedaría en 5 y con él llega a 8.

**¿Cómo termina el algoritmo?**
Cuando BFS no encuentra camino del origen al destino en la red residual. Las capacidades
enteras garantizan que cada paso suma al menos 1.

**¿Cómo se obtiene el corte y por qué es mínimo?**
S son los alcanzables desde el origen en la residual final. Las rutas de S a T están
saturadas y de T a S no vuelve flujo, así que la capacidad del corte es igual al valor del
flujo. Como ningún flujo supera a ningún corte, ese corte es mínimo y el flujo máximo.

**¿El corte mínimo es único?**
No. En la red inicial, las cuatro rutas que entran a T también suman 18. El programa
muestra el que resulta de los vértices alcanzables desde el origen.

**¿Por qué el flujo del caso manual no coincide ruta por ruta con el del programa?**
Porque el flujo máximo no es único en su distribución: 5 y 3 desde O, o 6 y 2, valen 8.

**¿Qué pasa si elijo el mismo vértice como origen y destino?**
Se rechaza con un mensaje y los selectores vuelven a los valores vigentes.

**¿Y si no hay camino entre origen y destino?**
Flujo 0, corte vacío de capacidad 0; las comprobaciones se cumplen igualmente.

**¿Dónde se respeta que una ruta está desactivada?**
En `capacidades_activas`, que es de donde parten todos los cálculos: una ruta desactivada
no entra en el diccionario.

**¿Qué bibliotecas usaron?**
Streamlit para la interfaz y Plotly para dibujar. Los algoritmos usan solo diccionarios,
listas y `deque`.

**Muéstrenme en el código dónde se actualiza el flujo.**
`algoritmos.py`, función `aumentar_flujo`: si el arco del camino es una ruta original se
suma; si no, es inverso y se resta a la ruta contraria.

**¿Cuál es la complejidad?**
O(|V|·|E|²): como mucho O(|V|·|E|) aumentos y cada BFS cuesta O(|V| + |E|).
