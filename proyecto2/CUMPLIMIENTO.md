# Cumplimiento del enunciado · Proyecto 2

Matriz `requisito → archivo/función → prueba → evidencia → estado`, contrastada con
`enunciados/proyecto_2.pdf` (enunciado y rúbricas).

**Auditoría del 14/11/2026.** Qué se hizo y qué no:

- Se ejecutó `.\.venv\Scripts\python.exe -m unittest discover -s proyecto2/tests`:
  **81 pruebas, todas superadas, ninguna omitida** (70 del modelo y los algoritmos, 11 de interfaz).
- Se ejecutó `python proyecto2/verificacion.py` y se comparó su salida, número por número,
  con el informe, la guía de estudio y el guion: coinciden.
- Se volvió a ejecutar la comparación BFS/DFS de la sección 4.4 del informe: coincide.
- Se leyó el PDF del informe página por página (22 páginas) después de regenerarlo.
- La interfaz se comprobó con las pruebas automáticas (`tests/test_interfaz.py`, que
  accionan los controles sin navegador) y con las capturas existentes en `capturas/`.
  **En esta auditoría no se volvió a abrir la aplicación en un navegador**: queda como
  comprobación manual del equipo (ver «Pendientes»).

Estados: **CUMPLE** = hay código, prueba y evidencia. **PENDIENTE** = depende de una acción
manual del equipo.

## 1. Modelación matemática de la red

| Requisito del enunciado | Archivo / función | Prueba | Evidencia | Estado |
|---|---|---|---|---|
| Grafo dirigido G = (V, E) con función de capacidad c | `datos/red_inicial.json`; `grafo.cargar_red`, `grafo.capacidades_activas` | `test_red_inicial_coincide_con_la_referencia_del_kit` | Informe §3.1–3.2; captura `01_capacidades.png` | CUMPLE |
| 10 ≤ \|V\| ≤ 12 y 15 ≤ \|E\| ≤ 20 | `grafo.validar_tamano_inicial`; `verificacion.comprobar_condiciones_iniciales` | `test_red_inicial_cumple_tamanos_del_enunciado`, `test_condiciones_iniciales` | \|V\| = 11, \|E\| = 18 (salida de `verificacion.py`) | CUMPLE |
| c : E → {1, …, 12} | `grafo.validar_capacidad`, `grafo.validar_estructura` | `test_capacidades_iniciales_enteras_entre_1_y_12` | mínima 2, máxima 8 | CUMPLE |
| Sin lazos, arcos repetidos ni recíprocos | `grafo.validar_estructura`; `algoritmos.comprobar_red_admisible` | `test_red_inicial_sin_lazos_repetidos_reciprocos_ni_aislados`, `test_validaciones_detectan_redes_incorrectas`, `test_rechaza_redes_que_el_enunciado_prohibe` | Informe §3.3 | CUMPLE |
| Ningún vértice aislado | `grafo.buscar_vertices_aislados` | `test_red_inicial_sin_lazos_repetidos_reciprocos_ni_aislados` | Informe §3.3 | CUMPLE |
| s ≠ t y al menos dos caminos dirigidos distintos de s a t | `verificacion.contar_caminos_simples` | `test_condiciones_iniciales`, `test_contar_caminos_simples` | s = O, t = T; 11 caminos | CUMPLE |
| Identificar V, E, c y el significado de los elementos | campo `centros` del JSON; `app.mostrar_modelo` | `test_todos_los_vertices_tienen_posicion_y_significado` | Informe §3; captura `13_modelo.png` | CUMPLE |
| Los intervalos solo se exigen a la configuración inicial | `grafo.agregar_arco` no limita el número de arcos | `test_el_limite_de_20_arcos_no_se_impone_a_las_modificaciones` | Informe §3.3 | CUMPLE |

## 2. Investigación, selección e implementación del algoritmo

| Requisito del enunciado | Archivo / función | Prueba | Evidencia | Estado |
|---|---|---|---|---|
| Investigar al menos dos estrategias y compararlas | Informe §4; `algoritmos.buscar_camino_en_profundidad` (solo comparación) | `test_bfs_y_dfs_obtienen_el_mismo_valor_maximo`, `test_bfs_y_dfs_coinciden_en_los_tres_escenarios` | Tabla de §4.4 (18/10/20; 6/4/7 aumentos); captura `11_algoritmo.png` | CUMPLE |
| Edmonds–Karp como variante de Ford–Fulkerson | Informe §4.3 | — | Informe §4.3; guía §5 | CUMPLE |
| Justificar la selección con fuentes identificables | Informe §5 y §13 | — | Fuentes [1]–[5] | CUMPLE (ver pendiente 5) |
| Implementar el algoritmo con código propio | `algoritmos.py`: `construir_red_residual`, `recorrer_en_anchura`, `buscar_camino_en_anchura`, `calcular_cuello_de_botella`, `aumentar_flujo`, `calcular_flujo_maximo` | Clases `PruebasRedResidual`, `PruebasBusquedaDeCaminos`, `PruebasFlujoMaximo` | Informe §6.3 (incluye el código del núcleo) | CUMPLE |
| Red residual con arcos inversos | `construir_red_residual`, `aumentar_flujo` | `test_el_arco_inverso_redirige_flujo_ya_enviado`, `test_aumentar_flujo_por_arcos_directos_e_inversos` | Guía §6.4 | CUMPLE |
| 0 ≤ x(u, v) ≤ c(u, v) | `verificacion.buscar_violaciones_de_capacidad` | `test_flujos_enteros_no_negativos_y_dentro_de_la_capacidad`, `test_detecta_flujo_mayor_que_la_capacidad`, `test_detecta_flujo_negativo_o_no_entero` | Informe §9.4 | CUMPLE |
| Conservación en cada vértice intermedio | `verificacion.buscar_violaciones_de_conservacion`, `calcular_balances` | `test_detecta_falta_de_conservacion`, `test_capacidad_y_conservacion_en_las_tres_configuraciones` | Informe §9.4; captura `10_verificacion.png` | CUMPLE |
| Valor = flujo neto que sale del origen | `algoritmos.calcular_valor_del_flujo` | `test_el_valor_es_el_flujo_neto_que_sale_del_origen`, `test_origen_con_ruta_entrante_y_destino_con_ruta_saliente` | 18 − 0 = 18 | CUMPLE |
| Mostrar el valor máximo y el flujo de cada arco con su capacidad | `app.mostrar_indicadores`, `app.tabla_de_flujos`; `dibujo.crear_figura` (modo «Flujo máximo») | `test_inicia_con_los_resultados_de_la_red_inicial`, `test_los_tres_modos_de_visualizacion_funcionan` | Capturas `02_flujo_maximo.png`, `09_resultados.png` | CUMPLE |

## 3. Corte mínimo y visualización interactiva

| Requisito del enunciado | Archivo / función | Prueba | Evidencia | Estado |
|---|---|---|---|---|
| Investigar el teorema de flujo máximo–corte mínimo | Informe §4.1, §6.3 y §10.4 | — | Guía §6.6 | CUMPLE |
| Identificar un corte mínimo a partir del flujo máximo: S, T y arcos de S a T | `algoritmos.encontrar_corte_minimo` | `test_corte_del_caso_manual`, `test_corte_de_la_red_con_arco_inverso`, `test_solo_cuentan_las_rutas_de_s_hacia_t`, `test_cortes_minimos_concretos` | S = {O, A, B, C, D, E, F, H, I}, T = {G, T}; captura `03_corte_minimo.png` | CUMPLE |
| Comprobar que la capacidad del corte coincide con el flujo | `verificacion.verificar_resultado` (comprobaciones 6 y 7) | `test_flujo_maximo_igual_al_corte_minimo_por_fuerza_bruta` (512 particiones), `test_todas_las_parejas_de_extremos_cumplen_y_coinciden_con_fuerza_bruta` (110 parejas) | 18 = 3 + 2 + 8 + 5 | CUMPLE |
| Representar centros, rutas, direcciones y capacidades | `dibujo.crear_figura` (modo «Capacidades») | `test_los_tres_modos_de_visualizacion_funcionan` | Captura `01_capacidades.png` | CUMPLE |
| Seleccionar origen y destino | `app.accion_cambiar_extremos`; `grafo.cambiar_extremos` | `test_cambiar_origen_y_destino` (modelo e interfaz), `test_rechaza_origen_igual_a_destino`, `test_sin_conexion_el_flujo_es_cero` | — | CUMPLE |
| Ejecutar el algoritmo desde la interfaz | `app.accion_calcular` | `test_desactivar_exige_recalcular_y_luego_se_puede_reactivar` | Captura `05_desactivar_calculado.png` | CUMPLE |
| Visualizar valor, flujo/capacidad y partición del corte | `app.mostrar_resultados`; `dibujo.crear_figura` (modos «Flujo máximo» y «Corte mínimo») | `test_los_tres_modos_de_visualizacion_funcionan` | Capturas `02`, `03`, `09` | CUMPLE |

## 4. Simulación y análisis de modificaciones

| Requisito del enunciado | Archivo / función | Prueba | Evidencia | Estado |
|---|---|---|---|---|
| Desactivar una ruta desde la interfaz | `grafo.desactivar_arco`, `grafo.reactivar_arco`; `app.accion_desactivar`, `app.accion_reactivar` | `test_desactivar_quita_la_ruta_de_los_calculos_sin_borrarla`, `test_desactivar_exige_recalcular_y_luego_se_puede_reactivar` | Capturas `04`, `05` | CUMPLE |
| Modificar la capacidad de una ruta | `grafo.cambiar_capacidad`; `app.accion_cambiar_capacidad` | `test_cambiar_capacidad_valida`, `test_cambiar_capacidad_rechaza_valores_no_permitidos`, `test_modificar_capacidad`, `test_la_capacidad_solo_admite_valores_de_1_a_12` | Captura `06_capacidad_modificada.png` | CUMPLE |
| Agregar una nueva conexión | `grafo.agregar_arco`, `grafo.validar_arco_nuevo`; `app.accion_agregar` | `test_agrega_conexion_valida_en_los_limites_de_capacidad`, `test_agregar_conexion_valida` | Captura `08_conexion_agregada.png` | CUMPLE |
| No admitir lazos, repetidos ni recíprocos | `grafo.validar_arco_nuevo` | `test_rechaza_lazo`, `test_rechaza_arco_repetido`, `test_rechaza_arco_reciproco`, `test_rechaza_repetida_y_reciproca_de_una_ruta_desactivada`, `test_rechaza_conexiones_prohibidas_sin_cambiar_la_red` | Captura `07_rechazo_reciproco.png` | CUMPLE |
| Capacidad entera de 1 a 12 en cada ruta activa | `grafo.validar_capacidad` | `test_rechaza_capacidades_fuera_de_rango_o_no_enteras` | — | CUMPLE |
| La ruta desactivada se respeta en todos los cálculos | `grafo.capacidades_activas` (única entrada de los cálculos) | `test_la_ruta_desactivada_no_lleva_flujo_ni_esta_en_el_corte` | Informe §6.2 | CUMPLE |
| Comparar la red inicial y dos modificaciones: flujo, corte e interpretación | `verificacion.construir_escenarios`, `comparar_escenarios`; `app.mostrar_escenarios` | Clase `PruebasEscenariosDeReferencia` (11 pruebas) | Informe §8 y §9; capturas `12`, `15`, `16`, `17` | CUMPLE |
| Recalcular mediante una acción; poder restablecer | `app.accion_calcular`, `app.accion_restaurar` | `test_restaurar_vuelve_a_la_red_inicial` | Captura `04_desactivar_pendiente.png` | CUMPLE |

Resultados de las tres configuraciones (salida de `verificacion.py` del 14/11/2026):

| Configuración | Flujo máximo | Corte mínimo | Capacidad | Comprobaciones |
|---|---:|---|---:|---|
| Red inicial | 18 | {C→G (3), F→T (2), H→T (8), I→T (5)} | 18 | 7 de 7 |
| Desactivar H → T | 10 | {C→G (3), F→T (2), I→T (5)} | 10 | 7 de 7 |
| I → T: 5 → 10 | 20 | {O→A (8), O→B (7), O→C (5)} | 20 | 7 de 7 |

## 5. Verificación de resultados

| Requisito del enunciado | Archivo / función | Prueba | Evidencia | Estado |
|---|---|---|---|---|
| Caso de 4 a 6 vértices con capacidades enteras | `datos/caso_manual.json` (5 vértices, 6 arcos) | `test_tamano_del_caso_manual` | Informe §10.1 | CUMPLE |
| Flujo factible y corte de igual capacidad; optimalidad | Informe §10.2–10.4 | `test_el_flujo_manual_del_kit_es_factible_y_tambien_vale_8` | Flujo 8, corte {A→T (3), C→T (5)} = 8 | CUMPLE |
| Comparar el cálculo manual con el código y explicar diferencias | `app.mostrar_caso_manual`; Informe §10.5 y §11 | `test_caso_manual_vale_8`, `test_el_codigo_obtiene_el_valor_de_la_solucion_manual` | Captura `14_caso_manual.png` | CUMPLE |
| En las tres configuraciones: capacidades, conservación y máximo = corte | `verificacion.verificar_resultado` | `test_todas_las_comprobaciones_se_cumplen`, `test_capacidad_y_conservacion_en_las_tres_configuraciones` | Informe §9.4; captura `10_verificacion.png` | CUMPLE |

## 6. Condiciones de implementación y documentación

| Condición | Evidencia | Estado |
|---|---|---|
| Algoritmo y procedimientos auxiliares con código propio | `algoritmos.py` solo importa `collections.deque` y `grafo` | CUMPLE |
| Sin bibliotecas que hagan los cálculos | Importaciones revisadas: `streamlit`, `plotly` y `pandas` solo en `app.py` y `dibujo.py`; las pruebas usan `unittest` e `itertools` (y el simulador de Streamlit solo para accionar la interfaz) | CUMPLE |
| Comentarios en las funciones principales (finalidad, entradas, resultados) | Todas las funciones de `grafo.py`, `algoritmos.py` y `dibujo.py` tienen comentario de documentación; en `verificacion.py`, todas menos dos auxiliares de impresión | CUMPLE |
| Fuentes académicas y técnicas identificadas | Informe §13 | CUMPLE |

Observación: en `app.py`, las funciones `accion_...` y `mostrar_...` se explican con
comentarios de bloque y no con un comentario propio cada una. No son funciones del
algoritmo; no se modificaron.

## 7. Informe técnico (rúbrica, 20 puntos)

| Criterio de la rúbrica | Dónde está en el informe | Estado |
|---|---|---|
| 1. Formulación matemática | §3 | CUMPLE |
| 2. Investigación y selección | §4 y §5 | CUMPLE |
| 3. Implementación propia, funciones documentadas y enlace al código | §6 y §15 (repositorio privado en GitHub) | CUMPLE (falta dar acceso al docente) |
| 4. Resultados y análisis de las tres configuraciones | §8 y §9 | CUMPLE |
| 5. Verificación manual y contraste con el código | §10 y §11 | CUMPLE |
| Formato PDF | `INFORME_BORRADOR.pdf` (22 páginas, numeradas) | **PENDIENTE**: regenerar tras completar los datos |
| Dependencias e instrucciones de ejecución | §14; `README.md`; `requirements.txt` | CUMPLE |

Correcciones hechas al informe en esta auditoría:

1. Se quitó de §13 una nota interna dirigida al equipo, que no debía aparecer en la entrega.
2. Se añadió en §3.1 una nota de notación: la letra T nombra el vértice de destino y también
   el conjunto del corte («T = {G, T}»).
3. En §6.3 se sustituyó el esquema en pseudocódigo por el código real del núcleo del
   algoritmo, porque la rúbrica pide «código del algoritmo».
4. PDF: números de página, título del documento correcto y las frases que presentan una
   tabla ya no quedan separadas de ella (`herramientas/generar_informe_pdf.py`).

## 8. Presentación (rúbrica, 20 puntos)

| Criterio de la rúbrica | Material preparado | Estado |
|---|---|---|
| 1. Problema y representación matemática | Guion, bloques 1 y 2 | **PENDIENTE**: ensayo |
| 2. Fundamento de la elección del algoritmo | Guion, bloque 3; guía §5 | **PENDIENTE**: ensayo |
| 3. Demostración funcional | Guion, bloque 4 y guía de demostración | **PENDIENTE**: ensayo |
| 4. Simulación interactiva y comparación | Guion, bloque 5 | **PENDIENTE**: ensayo |
| 5. Participación de los tres y respuestas | Guion (reparto) y preguntas probables; guía §13–15 | **PENDIENTE**: asignar nombres y ensayar |

## 9. Interpretaciones adoptadas ante ambigüedades

Se eligió siempre la lectura más estricta.

- **Arcos recíprocos y repetidos frente a rutas desactivadas.** Una ruta desactivada sigue
  existiendo: no se puede agregar otra igual ni su recíproca.
- **Capacidad de 1 a 12.** Se exige a toda ruta, también a las agregadas o modificadas.
- **Vértices aislados.** Se exige a la configuración inicial. Tras desactivar rutas, un
  centro puede quedar sin rutas activas; el cálculo sigue siendo válido.
- **«Dos caminos dirigidos distintos».** Se cuentan los caminos sin vértices repetidos: hay 11.
- **Origen y destino elegidos en la interfaz.** Se admite cualquier pareja de centros
  distintos; si no hay camino, el flujo es 0 y el corte es vacío.
- **Corte mínimo no único.** Se muestra el que definen los vértices alcanzables desde el
  origen en la red residual final.

## 10. Pendientes antes de la entrega (acciones manuales del equipo)

1. **Datos de la portada** en `INFORME_BORRADOR.md`: nombres de los tres integrantes y del
   docente.
2. **Enlace al código:** hecho. Repositorio privado
   https://github.com/HectorLep/INFO1158-Simulador-Red-Distribucion-Paquetes, ya citado en
   la portada y en §15. Falta **invitar al docente como colaborador** (Settings →
   Collaborators → Add people). El repositorio es privado: sin esa invitación, el enlace
   no le abrirá.
3. **Regenerar el PDF** después del punto 1, desde la carpeta raíz:
   `.\.venv\Scripts\python.exe herramientas/generar_informe_pdf.py`
   (requiere `python -m pip install markdown`). Revisar que no quede el texto «PENDIENTE» y
   renombrar el archivo para la entrega (el nombre actual dice «BORRADOR»).
4. **Comprobar el acceso del docente** una vez aceptada la invitación.
5. **Bibliografía.** Confirmar que el equipo consultó realmente las fuentes [1] a [5]. La
   fuente [1] se cita por título de capítulo y sin número, porque la numeración de la 4.ª
   edición no se pudo confirmar; si se tiene el libro, añadir los números.
6. **Abrir la aplicación en el navegador** y recorrer la «Guía de demostración» del guion
   (15 pasos).
7. **Guion:** sustituir «Integrante 1, 2 y 3» por los nombres y ensayar con cronómetro
   (objetivo 11:30; máximo 12:00).
8. **Subir el PDF a Educa** antes del jueves 26/11/2026 a las 23:00.
