# Guía de estudio · Proyecto 2: red de distribución de paquetes

Esta guía está escrita para que los tres integrantes puedan **explicar cada parte del
proyecto sin leer**. Léela con el código abierto al lado. Todos los números que aparecen
aquí salieron de ejecutar el programa (`python proyecto2/verificacion.py` y las pruebas);
ninguno está inventado.

Índice

1. Qué problema resuelve el programa
2. Qué es un grafo dirigido con capacidades
3. Qué representan los vértices, los arcos, la capacidad y el flujo
4. Estructuras de datos que usamos
5. Algoritmo elegido y por qué
6. El algoritmo paso a paso
7. Ejemplo pequeño resuelto a mano
8. Explicación de cada función principal
9. Variables importantes
10. Cómo se conectan la interfaz y los algoritmos
11. Cómo leer los resultados
12. Errores comunes que debemos evitar
13. Preguntas que puede hacer el profesor (con respuestas)
14. Ejercicios para comprobar que entendimos
15. Cuestionario autocorregible (15 preguntas)
16. Explicación de 5 minutos (para ensayar)

---

## 1. Qué problema resuelve el programa

Una empresa mueve paquetes entre centros logísticos. Cada ruta tiene un sentido y admite
un máximo de paquetes por hora. La empresa quiere saber:

| Pregunta de la empresa | Nombre matemático | Respuesta en la red inicial |
|---|---|---|
| ¿Cuántos paquetes por hora pueden llegar como máximo del origen al destino? | Flujo máximo | 18 paquetes por hora |
| ¿Cuántos paquetes debe llevar cada ruta para lograrlo? | Flujo x(u, v) de cada arco | Por ejemplo O → A: 8/8, A → E: 2/3 … |
| ¿Qué rutas son el cuello de botella? | Corte mínimo | {C → G (3), F → T (2), H → T (8), I → T (5)}, capacidad 18 |
| ¿Qué pasa si se cae una ruta o se amplía otra? | Comparación de configuraciones | Sin H → T: 10. Con I → T en 10: 20 |

## 2. Qué es un grafo dirigido con capacidades

- Un **grafo dirigido** es una pareja G = (V, E): V es un conjunto de **vértices** y E un
  conjunto de **arcos**, que son pares ordenados (u, v) dibujados como una flecha u → v.
- Una **función de capacidad** c asigna a cada arco un número: c(u, v).
  En este proyecto c : E → {1, 2, …, 12}.
- Se eligen dos vértices distintos: el **origen** s y el **destino** t.

A esto se le llama **red de flujo**.

Un **flujo** es otra función, x, que dice cuánto se envía por cada arco. Debe cumplir:

1. **Capacidad:** 0 ≤ x(u, v) ≤ c(u, v) en todo arco.
2. **Conservación:** en cada vértice que no es s ni t, lo que entra es igual a lo que sale
   (los centros intermedios no crean ni guardan paquetes).

El **valor** del flujo es lo que sale de s menos lo que entra a s:
|x| = Σ x(s, v) − Σ x(u, s). Un **flujo máximo** es uno de valor máximo.

## 3. Qué representan los vértices, los arcos, la capacidad y el flujo

| Elemento del modelo | Significado logístico |
|---|---|
| Vértice | Un centro logístico (origen, centros regionales, de distribución, de reparto, destino) |
| Arco u → v | Una ruta de transporte que solo circula de u hacia v |
| c(u, v) | Máximo de paquetes por hora que admite la ruta (entero de 1 a 12) |
| x(u, v) | Paquetes por hora que el plan envía por la ruta |
| Arco con `"activo": false` | Ruta desactivada: existe, pero no transporta nada |
| Etiqueta `6/6` en el grafo | flujo/capacidad: la ruta lleva 6 de los 6 que admite (saturada) |

Red inicial (`datos/red_inicial.json`): V = {O, A, B, C, D, E, F, G, H, I, T}, |V| = 11;
|E| = 18; s = O, t = T. Capacidades:

| Arco | c | Arco | c | Arco | c |
|---|---:|---|---:|---|---:|
| O → A | 8 | B → F | 4 | E → I | 4 |
| O → B | 7 | C → F | 5 | F → I | 6 |
| O → C | 5 | C → G | 3 | F → T | 2 |
| A → D | 6 | D → H | 6 | G → T | 3 |
| A → E | 3 | D → I | 2 | H → T | 8 |
| B → E | 6 | E → H | 5 | I → T | 5 |

Restricciones del enunciado (las comprueba el código en la pestaña *Modelo matemático* y en
las pruebas):

- 10 ≤ |V| ≤ 12 y 15 ≤ |E| ≤ 20 → 11 y 18. **Solo se exigen a la red inicial.**
- Capacidades enteras entre 1 y 12 → la menor es 2 y la mayor 8.
- Sin **lazos** (u → u), sin arcos **repetidos**, sin arcos **recíprocos** (u → v junto con v → u).
- Ningún vértice **aislado**.
- Al menos **dos caminos dirigidos distintos** de s a t → el programa cuenta 11.

## 4. Estructuras de datos que usamos

Solo estructuras básicas de Python. Ninguna biblioteca de grafos.

| Estructura | Ejemplo | Para qué |
|---|---|---|
| Diccionario `red` | `{"vertices": [...], "arcos": [...], "origen": "O", ...}` | Guarda la red tal como está en el JSON |
| Diccionario `capacidades` | `{("O","A"): 8, ("O","B"): 7, ...}` | Solo las rutas **activas** y su capacidad |
| Diccionario `flujo` | `{("O","A"): 8, ("A","E"): 2, ...}` | Paquetes por hora de cada ruta activa |
| Diccionario de diccionarios `residual` | `{"O": {"A": 3, "B": 4}, "A": {"O": 3, "C": 3}, ...}` | Cuánto más se puede mover de un vértice a otro |
| `deque` (cola) | — | BFS atiende los vértices en orden de llegada |
| Diccionario `padre` | `{"O": None, "A": "O", "T": "A"}` | De dónde se llegó a cada vértice (para reconstruir el camino) |
| Lista `pasos` | `[{"camino": [...], "cuello_de_botella": 3, ...}]` | Historial de caminos aumentantes |

**Punto clave del diseño:** todos los cálculos empiezan por `capacidades_activas(red)`. Como
una ruta desactivada no está en ese diccionario, es imposible que lleve flujo o aparezca en
un corte.

## 5. Algoritmo elegido y por qué

### 5.1 El método de Ford–Fulkerson

Idea: empezar con flujo 0 y mejorarlo poco a poco. Mientras exista un **camino aumentante**
(un camino de s a t por el que todavía se puede enviar algo), se envía por él todo lo que
cabe. Cuando no queda ninguno, el flujo es máximo.

Ford–Fulkerson es un **método**, no un algoritmo completo: no dice *cómo* buscar el camino
aumentante. Según cómo se busque, salen variantes distintas.

### 5.2 Las dos estrategias que comparamos

| | Ford–Fulkerson con DFS | Edmonds–Karp (Ford–Fulkerson con BFS) |
|---|---|---|
| Cómo elige el camino aumentante | Búsqueda en profundidad: el primero que encuentra | Búsqueda en anchura: el que tiene **menos arcos** |
| ¿Da el flujo máximo? | Sí (con capacidades enteras) | Sí |
| Cantidad de caminos aumentantes | Hasta \|x\*\| (el valor del flujo máximo): depende de las capacidades | Como mucho del orden de \|V\|·\|E\|: **no depende de las capacidades** |
| Tiempo en el peor caso | O(\|E\| · \|x\*\|) | O(\|V\| · \|E\|²) |
| Caminos que produce | Pueden ser largos y enrevesados | Los más cortos posibles: fáciles de seguir a mano |
| Dificultad de programarlo | Baja | Baja (solo cambia la búsqueda) |

Edmonds–Karp **es** Ford–Fulkerson: lo único que fija es que el camino se busca con BFS.

### 5.3 Por qué elegimos Edmonds–Karp

1. **Garantía de terminación y de rapidez** que no depende de los valores de las
   capacidades, sino solo del tamaño de la red.
2. **Es sistemático y reproducible:** BFS siempre encuentra el camino con menos arcos, así
   que cualquiera puede repetir los pasos a mano y obtener lo mismo que el programa.
3. **Reutiliza una sola búsqueda:** el mismo BFS sirve para hallar caminos aumentantes y,
   al final, para obtener el corte mínimo.

### 5.4 Comparación real en nuestra red

El programa incluye DFS **solo para comparar** (pestaña *Algoritmo paso a paso*). Resultado
de ejecutar ambos:

| Escenario | Valor con BFS | Valor con DFS | Caminos con BFS | Caminos con DFS |
|---|---:|---:|---:|---:|
| Red inicial | 18 | 18 | 6 | 6 |
| Desactivar H → T | 10 | 10 | 4 | 4 |
| I → T con capacidad 10 | 20 | 20 | 7 | 7 |

Honestamente: en una red tan pequeña las dos estrategias usan la misma cantidad de caminos
y llegan al mismo valor (como debe ser). La diferencia se ve en **cómo son** los caminos:

- Con BFS, en la red inicial el camino más largo tiene 4 arcos y **ninguno usa arcos inversos**.
- Con DFS, el segundo camino es **O → A → E → H → D → I → T** (6 arcos) y usa el arco
  inverso H → D: DFS había llenado D → H con 6 y después tuvo que devolver 2.

La ventaja decisiva de BFS es la garantía teórica: con DFS, en redes con capacidades grandes
el número de pasos puede crecer con esas capacidades; con BFS, no.

## 6. El algoritmo paso a paso

### 6.1 La red residual (`construir_red_residual`)

La red residual responde a la pregunta: **"con el flujo que ya tengo, ¿qué cambios puedo
hacer todavía?"**. Por cada ruta original u → v con capacidad c y flujo x:

| Situación | Arco residual | Significado |
|---|---|---|
| c − x > 0 | u → v con capacidad c − x | "Todavía caben c − x paquetes más" (arco **directo**) |
| x > 0 | v → u con capacidad x | "Puedo retirar hasta x paquetes de esta ruta" (arco **inverso**) |

Ejemplo: A → T tiene capacidad 3 y flujo 3. No hay arco directo (está llena) y sí hay un
arco inverso T → A de capacidad 3.

**Un arco inverso no es una ruta.** Ningún camión circula de T a A. Significa que una
decisión anterior puede deshacerse parcialmente para redirigir paquetes.

Como el enunciado prohíbe arcos recíprocos, nunca hay confusión: si en la red residual
aparece v → u y la ruta original es u → v, ese arco solo puede ser el inverso. El programa
lo comprueba al empezar (`comprobar_red_admisible`).

### 6.2 El ciclo principal (`calcular_flujo_maximo`)

```
flujo = 0 en todas las rutas
repetir:
    residual = construir_red_residual(flujo)
    camino   = BFS en la residual, de origen a destino
    si no hay camino: terminar                      ← el flujo ya es máximo
    cuello   = menor capacidad residual del camino  ← cuello de botella
    para cada arco u → v del camino:
        si u → v es ruta original:  flujo[u → v] += cuello
        si no (arco inverso):       flujo[v → u] −= cuello
```

- **Camino aumentante:** camino de s a t en la red residual.
- **Cuello de botella:** lo máximo que se puede enviar por ese camino sin pasarse en
  ninguno de sus arcos; es el mínimo de sus capacidades residuales.
- **Terminación:** las capacidades son enteras, así que cada paso sube el flujo al menos en
  1, y el flujo no puede superar lo que sale del origen. Con BFS, además, hay una cota que
  no depende de las capacidades.

### 6.3 Traza completa en el caso de 5 vértices

Red: O→A (6), O→B (4), A→C (3), A→T (3), B→C (4), C→T (5).

**Paso 1.** Flujo 0. Red residual = la red original.
BFS desde O: descubre A y B; desde A descubre C y **T**. Camino **O → A → T**.
Cuello = mín(6, 3) = 3. Flujo: O→A = 3, A→T = 3. Valor acumulado: 3.

**Paso 2.** Red residual (salida real del programa):
`O: {A: 3, B: 4}`, `A: {O: 3, C: 3}`, `B: {C: 4}`, `C: {T: 5}`, `T: {A: 3}`.
Observa: A → T desapareció (está llena) y aparecieron los inversos A → O y T → A.
BFS: O descubre A y B; A descubre C (T ya no es vecino de A); B nada nuevo; C descubre T.
Camino **O → A → C → T**. Cuello = mín(3, 3, 5) = 3. Flujo: O→A = 6, A→C = 3, C→T = 3.
Valor acumulado: 6.

**Paso 3.** Red residual:
`O: {B: 4}`, `A: {O: 6}`, `B: {C: 4}`, `C: {A: 3, T: 2}`, `T: {A: 3, C: 3}`.
BFS: O descubre B; B descubre C; C descubre A y **T**. Camino **O → B → C → T**.
Cuello = mín(4, 4, 2) = 2. Flujo: O→B = 2, B→C = 2, C→T = 5. Valor acumulado: 8.

**Paso 4.** Red residual final:
`O: {B: 2}`, `A: {O: 6}`, `B: {O: 2, C: 2}`, `C: {A: 3, B: 2}`, `T: {A: 3, C: 5}`.
BFS: O descubre B; B descubre C; C descubre A; A solo lleva de vuelta a O. **T no es
alcanzable → fin.** Flujo máximo = 8.

Flujo final: O→A 6/6, O→B 2/4, A→C 3/3, A→T 3/3, B→C 2/4, C→T 5/5.

### 6.4 Un ejemplo donde el arco inverso es imprescindible

Red de 8 vértices (está en `tests/test_algoritmos.py` como `CAPACIDADES_INVERSO`):

```
O → A (5), A → B (5), B → T (5)        camino corto
A → C (3), C → D (3), D → T (3)        salida alternativa desde A
O → E (4), E → F (4), F → B (4)        entrada alternativa hacia B
```

- **Paso 1.** El camino con menos arcos es O → A → B → T. Cuello 5. Ahora A → B y B → T
  están llenas, y también O → A.
- Si no existieran arcos inversos, el algoritmo se detendría aquí con valor 5: por O → E → F
  se llega a B, pero B → T está llena.
- **Paso 2.** En la red residual existe el arco inverso **B → A** (capacidad 5). BFS
  encuentra **O → E → F → B → A → C → D → T**, con cuello mín(4, 4, 4, 5, 3, 3, 3) = 3.
  Al recorrer B → A, el flujo de A → B **baja de 5 a 2**.
- **Resultado:** valor 8. Flujo final: O→A 5, A→B 2, A→C 3, C→D 3, D→T 3, O→E 3, E→F 3,
  F→B 3, B→T 5.

Interpretación logística: 3 de los 5 paquetes que A enviaba a B se desvían hacia C, y su
lugar en la ruta B → T lo ocupan 3 paquetes que llegan desde F. Nadie viajó "hacia atrás".

El camino aumentante del paso 2 **no es una ruta de transporte** (pasa por B → A, que no
existe). Por eso el resultado que se muestra es siempre el **flujo final sobre las rutas
originales**, no la lista de caminos aumentantes.

### 6.5 El corte mínimo (`encontrar_corte_minimo`)

Un **corte** es una partición de los vértices en dos conjuntos, S y T, con s en S y t en T.
Su **capacidad** es la suma de las capacidades de los arcos que van **de S a T** (los que
van de T a S no cuentan):

c(S, T) = Σ c(u, v), con u en S y v en T.

Cómo lo obtiene el programa:

1. Construir la red residual del flujo **final**.
2. Con BFS, marcar todo lo alcanzable desde s. Eso es **S**. El resto es **T**.
3. El corte son las rutas originales activas con origen en S y destino en T.

En el caso de 5 vértices: alcanzables desde O = {O, B, C, A} → S = {O, A, B, C}, T = {T}.
Rutas de S a T: A → T (3) y C → T (5). Capacidad 8 = flujo máximo.

### 6.6 Por qué flujo máximo = corte mínimo

**Parte 1 — ningún flujo supera a ningún corte.** Todo paquete que sale de s y llega a t
tiene que cruzar alguna vez de S a T. Por las rutas de S a T no pueden pasar más paquetes
que la suma de sus capacidades. Entonces: valor de cualquier flujo ≤ capacidad de cualquier
corte.

**Parte 2 — al terminar el algoritmo se alcanza la igualdad.** Con el S que construimos:

- Toda ruta de S a T está **saturada**. Si le sobrara capacidad, tendría un arco residual
  directo y su extremo final sería alcanzable: estaría en S, no en T.
- Ninguna ruta de T a S lleva flujo. Si llevara, tendría un arco inverso de S a T y su
  origen sería alcanzable.
- Luego todo lo que cruza de S a T es exactamente la capacidad del corte, y nada vuelve:
  valor del flujo = c(S, T).

Juntando las dos partes: no puede existir un flujo mayor (superaría a este corte) ni un
corte menor (sería superado por este flujo). El flujo es **máximo** y el corte es **mínimo**.

El programa comprueba estas tres condiciones en cada cálculo (comprobación "Corte: sus
rutas van de S a T y están saturadas; de T a S no vuelve flujo").

## 7. Ejemplo pequeño resuelto a mano (caso de verificación)

Archivo `datos/caso_manual.json`: O→A (6), O→B (4), A→C (3), A→T (3), B→C (4), C→T (5).

**a) Un flujo factible, pensando en trayectos.**
- 3 paquetes por O → A → T (llena A → T).
- 2 paquetes por O → A → C → T.
- 3 paquetes por O → B → C → T.

Sumando por ruta: O→A = 5, O→B = 3, A→C = 2, A→T = 3, B→C = 3, C→T = 5.

**b) Comprobación de capacidad.** 5 ≤ 6, 3 ≤ 4, 2 ≤ 3, 3 ≤ 3, 3 ≤ 4, 5 ≤ 5. ✔

**c) Comprobación de conservación.**

| Centro | Entra | Sale |
|---|---|---|
| A | 5 (de O) | 2 + 3 = 5 |
| B | 3 (de O) | 3 |
| C | 2 + 3 = 5 | 5 |

**d) Valor.** Sale de O: 5 + 3 = 8. Llega a T: 3 + 5 = 8.

**e) Un corte.** S = {O, A, B, C}, T = {T}. Rutas de S a T: A → T (3) y C → T (5).
Capacidad: 3 + 5 = **8**.

**f) Optimalidad.** Ningún flujo puede superar la capacidad de un corte (sección 6.6). Hay
un flujo de valor 8 y un corte de capacidad 8, así que 8 es el flujo máximo y ese corte es
mínimo. Otra forma de verlo: a T solo llegan A → T y C → T, que suman 8.

**g) Contraste con el código.**

| Ruta | Capacidad | Flujo a mano | Flujo del código |
|---|---:|---:|---:|
| O → A | 6 | 5 | 6 |
| O → B | 4 | 3 | 2 |
| A → C | 3 | 2 | 3 |
| A → T | 3 | 3 | 3 |
| B → C | 4 | 3 | 2 |
| C → T | 5 | 5 | 5 |
| **Valor** | | **8** | **8** |
| **Corte** | | {A → T, C → T} = 8 | {A → T, C → T} = 8 |

**h) Explicación de la diferencia.** El valor y el corte coinciden; el reparto por ruta, no.
El código elige primero los caminos más cortos (O → A → T y luego O → A → C → T), por lo que
llena O → A con 6 y solo necesita 2 por O → B. A mano repartimos 5 y 3. Los dos flujos
cumplen capacidad y conservación y valen 8. **El valor del flujo máximo es único; la
distribución puede no serlo.** La prueba `test_el_flujo_manual_del_kit_es_factible_y_tambien_vale_8`
comprueba ambas cosas.

## 8. Explicación de cada función principal

### `grafo.py` — la red y sus cambios

| Función | Qué hace | Detalle para explicar |
|---|---|---|
| `cargar_red(ruta)` | Lee el JSON y devuelve el diccionario | |
| `copiar_red(red)` | Copia independiente (`deepcopy`) | Sin esto, los escenarios se pisarían entre sí |
| `capacidades_activas(red)` | Diccionario (u, v) → capacidad de las rutas activas | **Puerta de entrada de todos los cálculos** |
| `arcos_desactivados(red)` | Lista de rutas desactivadas | Alimenta el selector "Reactivar" |
| `validar_capacidad(c)` | Lanza `ValueError` si c no es un entero entre 1 y 12 | Rechaza también 2.5, "5" y `True` |
| `validar_arco_nuevo(red, u, v, c)` | Rechaza lazos, repetidos, recíprocos, vértices inexistentes y capacidades inválidas | Las rutas desactivadas también cuentan |
| `validar_estructura(red)` | Lista de problemas que nunca deben existir | Se usa en pruebas y en la pestaña *Modelo* |
| `validar_tamano_inicial(red)` | 10–12 vértices, 15–20 arcos, sin aislados | Solo para la red inicial |
| `desactivar_arco`, `reactivar_arco` | Cambian `"activo"` a `False` / `True` | La ruta nunca se borra |
| `cambiar_capacidad(red, u, v, c)` | Cambia la capacidad de una ruta | Si c no es válida, la red queda igual |
| `agregar_arco(red, u, v, c)` | Valida y añade la ruta | |
| `cambiar_extremos(red, s, t)` | Cambia origen y destino | Rechaza s = t |

### `algoritmos.py` — las matemáticas

| Función | Entrada | Salida |
|---|---|---|
| `comprobar_red_admisible(...)` | Red y extremos | Error si s = t, hay lazos, recíprocos o capacidades no enteras positivas |
| `construir_red_residual(vertices, capacidades, flujo)` | Flujo actual | `residual[u][v]` = capacidad residual (solo valores > 0) |
| `recorrer_en_anchura(residual, inicio)` | Red residual | Diccionario `padre`; sus claves son los vértices alcanzables |
| `reconstruir_camino(padre, destino)` | `padre` | Lista de vértices del camino |
| `buscar_camino_en_anchura(residual, s, t)` | Red residual | Camino aumentante con menos arcos, o `None` |
| `buscar_camino_en_profundidad(...)` | Red residual | Un camino aumentante cualquiera (solo comparación) |
| `calcular_cuello_de_botella(residual, camino)` | Camino | Menor capacidad residual del camino |
| `aumentar_flujo(flujo, camino, cantidad)` | Camino y cantidad | Modifica `flujo`: suma en arcos directos, resta en inversos |
| `calcular_valor_del_flujo(flujo, s)` | Flujo | Sale de s − entra a s |
| `calcular_flujo_maximo(vertices, capacidades, s, t)` | Red | `(flujo, pasos)` |
| `encontrar_corte_minimo(vertices, capacidades, flujo, s)` | Flujo máximo | `(S, T, arcos del corte, capacidad)` |
| `analizar_red_logistica(...)` / `analizar_red(red)` | Red | Diccionario con todos los resultados |

### `verificacion.py` — desconfiar del propio resultado

| Función | Qué comprueba |
|---|---|
| `buscar_violaciones_de_capacidad(capacidades, flujo)` | Rutas con flujo negativo, mayor que la capacidad o no entero |
| `calcular_balances(vertices, flujo)` | Cuánto entra y cuánto sale de cada centro |
| `buscar_violaciones_de_conservacion(...)` | Centros intermedios donde entra ≠ sale |
| `contar_caminos_simples(...)` | Cuántos caminos distintos hay de s a t (condición inicial) |
| `verificar_resultado(red, resultado)` | Las 7 comprobaciones que muestra la aplicación |
| `comprobar_condiciones_iniciales(red)` | Las 4 condiciones de la red inicial |
| `construir_escenarios(red)` / `comparar_escenarios(red)` | Los tres escenarios, cada uno sobre su propia copia |

Las 7 comprobaciones de `verificar_resultado`:

1. Capacidad: 0 ≤ flujo ≤ capacidad en cada ruta activa.
2. Conservación en cada centro intermedio.
3. Valor del flujo = flujo neto que sale del origen.
4. El mismo valor llega, neto, al destino.
5. Partición válida: origen en S, destino en T, cada centro en un solo lado.
6. Las rutas del corte van de S a T y están saturadas; de T a S no vuelve flujo.
7. Flujo máximo = capacidad del corte mínimo.

### `dibujo.py` y `app.py`

- `dibujo.crear_figura(red, resultado, modo)` dibuja la red en uno de tres modos:
  *Capacidades*, *Flujo máximo* o *Corte mínimo*. No calcula nada.
- `app.py` muestra controles y resultados. Sus funciones `accion_...` se ejecutan al pulsar
  un botón y llaman a las funciones de `grafo.py`.

## 9. Variables importantes

| Variable | Tipo | Significado |
|---|---|---|
| `red` | diccionario | La red completa (vértices, arcos, origen, destino, posiciones) |
| `capacidades` | dict (u, v) → entero | c(u, v) de las rutas activas |
| `flujo` | dict (u, v) → entero | x(u, v): paquetes por hora en cada ruta activa |
| `residual` | dict → dict | Capacidad residual entre pares de vértices |
| `padre` | dict | Árbol de BFS: de dónde se llegó a cada vértice |
| `camino` | lista | Camino aumentante, como lista de vértices |
| `cuello` | entero | Cuello de botella del camino |
| `pasos` | lista de dict | Un registro por camino aumentante |
| `flujo_acumulado` | entero | Valor del flujo tras cada paso |
| `alcanzables` | dict | Vértices alcanzables desde s en la residual final (son S) |
| `lado_origen`, `lado_destino` | listas | Conjuntos S y T |
| `arcos_del_corte`, `capacidad_del_corte` | lista, entero | Rutas de S a T y su suma |
| `resultado` | diccionario | Todo lo anterior, reunido por `analizar_red` |

## 10. Cómo se conectan la interfaz y los algoritmos

```
  Usuario pulsa un botón
        │
        ▼
  app.py: accion_desactivar() / accion_cambiar_capacidad() / accion_agregar() ...
        │  llama a
        ▼
  grafo.py: desactivar_arco(red, u, v)   ← valida; si no se puede, ValueError → mensaje rojo
        │
        ▼
  la red cambió → app.py oculta los resultados viejos y pide «Calcular»
        │
        ▼
  app.py: accion_calcular() → algoritmos.analizar_red(red)
        │
        ▼
  verificacion.verificar_resultado(red, resultado)   ← 7 comprobaciones
        │
        ▼
  dibujo.crear_figura(red, resultado, modo)  +  tablas y textos
```

Streamlit vuelve a ejecutar `app.py` completo cada vez que se toca un control. Lo que debe
conservarse vive en `st.session_state`:

- `red`: la red que se está modificando;
- `resultado`: el último análisis;
- `red_calculada`: copia de la red sobre la que se calculó `resultado`.

Si `red` ≠ `red_calculada`, hay cambios sin calcular: los indicadores muestran "—" y el
grafo se dibuja solo con capacidades. Así **nunca se ven resultados que no corresponden a
la red en pantalla**.

La pestaña *Escenarios* no usa `st.session_state.red`: carga siempre el archivo original,
por eso la comparación no se contamina con lo que se haya hecho en el panel lateral.

## 11. Cómo leer los resultados

**Indicadores.** "18 paq./h" es el flujo máximo. "Capacidad del corte mínimo 18 paq./h"
debe coincidir siempre. "Caminos aumentantes 6" es cuántas veces mejoró el flujo.
"✔ 7 de 7" indica que todas las verificaciones pasaron.

**Grafo, modo Flujo máximo.** Etiqueta `flujo/capacidad`. Azul oscuro y etiqueta en negrita
= ruta saturada. Azul claro = lleva flujo y le sobra capacidad. Gris = sin flujo. El grosor
crece con el flujo.

**Grafo, modo Corte mínimo.** Rojo discontinuo = rutas del corte. Celeste = conjunto S.
Naranja claro = conjunto T.

**Flujo de la red inicial (salida real):**

O→A 8/8, O→B 7/7, O→C 3/5, A→D 6/6, A→E 2/3, B→E 4/6, B→F 3/4, C→F 0/5, C→G 3/3,
D→H 6/6, D→I 0/2, E→H 2/5, E→I 4/4, F→I 1/6, F→T 2/2, G→T 3/3, H→T 8/8, I→T 5/5.

Caminos aumentantes (Edmonds–Karp), en orden:

| Paso | Camino | Cuello de botella | Acumulado |
|---|---|---:|---:|
| 1 | O → B → F → T | 2 | 2 |
| 2 | O → C → G → T | 3 | 5 |
| 3 | O → A → D → H → T | 6 | 11 |
| 4 | O → A → E → H → T | 2 | 13 |
| 5 | O → B → E → I → T | 4 | 17 |
| 6 | O → B → F → I → T | 1 | 18 |

Corte: S = {O, A, B, C, D, E, F, H, I}, T = {G, T};
rutas C → G (3), F → T (2), H → T (8), I → T (5); 3 + 2 + 8 + 5 = 18.

**Comparación de escenarios (salida real):**

| Escenario | Flujo máximo | Corte mínimo | Capacidad |
|---|---:|---|---:|
| Red inicial | 18 | {C→G (3), F→T (2), H→T (8), I→T (5)} | 18 |
| Desactivar H → T | 10 | {C→G (3), F→T (2), I→T (5)} | 10 |
| I → T: 5 → 10 | 20 | {O→A (8), O→B (7), O→C (5)} | 20 |

Interpretación:

- **Red inicial.** Del origen podrían salir 8 + 7 + 5 = 20, pero solo llegan 18. El límite
  está cerca del destino.
- **Desactivar H → T.** Se pierden exactamente los 8 paquetes por hora de esa ruta
  (18 → 10), porque pertenecía al corte mínimo y las demás entradas a T ya estaban llenas.
  H queda sin salida: D → H y E → H pasan a llevar 0.
- **Ampliar I → T a 10.** El flujo sube solo 2 (18 → 20), no 5. El cuello de botella se
  traslada a las rutas que salen del origen (8 + 7 + 5 = 20) e I → T queda con 7/10.
  Moraleja: ampliar una ruta ayuda solo hasta que aparece otro cuello de botella.

**El corte mínimo no es único.** En la red inicial, {F→T, G→T, H→T, I→T} (las cuatro rutas
que entran a T) también tiene capacidad 2 + 3 + 8 + 5 = 18. El programa muestra el que
resulta de los vértices alcanzables desde el origen. Por eso ampliar G → T a 12 **no** mejora
el flujo (sigue en 18): C → G (3) sigue limitando. Lo comprobamos con el código.

## 12. Errores comunes que debemos evitar

1. **Confundir capacidad con flujo.** La capacidad es lo que la ruta admite; el flujo, lo
   que el plan envía. Siempre flujo ≤ capacidad.
2. **Creer que un arco inverso es una ruta.** Es un permiso para retirar flujo ya asignado.
3. **Mostrar los caminos aumentantes como "las rutas que siguen los paquetes".** Pueden
   contener arcos inversos. Lo que se entrega es el flujo final por ruta original.
4. **Sumar al corte los arcos que van de T a S.** Solo cuentan los de S hacia T.
5. **Decir que el flujo máximo es único.** Es único su **valor**; el reparto puede variar.
6. **Decir que el corte mínimo es único.** Puede haber varios con la misma capacidad.
7. **Pensar que ampliar una ruta del corte siempre aumenta el flujo.** Puede haber otro
   corte de igual capacidad (ejemplo: G → T).
8. **Decir que Edmonds–Karp y Ford–Fulkerson son algoritmos distintos sin relación.**
   Edmonds–Karp es Ford–Fulkerson con BFS.
9. **Olvidar la conservación al inventar un flujo a mano.** Revisar cada centro intermedio.
10. **Acumular modificaciones entre escenarios.** Cada uno parte de una copia del original.
11. **Aplicar los límites 10–12 y 15–20 a la red modificada.** Solo valen para la inicial.
    El rango 1–12 de las capacidades sí vale siempre.
12. **Aceptar un arco recíproco de una ruta desactivada.** La ruta desactivada sigue existiendo.

## 13. Preguntas que puede hacer el profesor

**1. ¿Qué diferencia hay entre Ford–Fulkerson y Edmonds–Karp?**
Ford–Fulkerson es el método general: aumentar el flujo por caminos aumentantes hasta que no
queden. Edmonds–Karp es ese mismo método con una regla concreta: el camino se busca con BFS,
es decir, se toma el de menos arcos. Eso da una cota de O(|V|·|E|²) que no depende de las
capacidades.

**2. ¿Por qué eligieron Edmonds–Karp?**
Porque garantiza terminar en un número de pasos acotado por el tamaño de la red, porque es
determinista y se puede seguir a mano, y porque el mismo BFS nos sirve para el corte mínimo.

**3. ¿Qué es la red residual?**
Es el grafo de los cambios que todavía se pueden hacer al flujo actual: arcos directos con
la capacidad que sobra y arcos inversos con el flujo que se podría retirar.

**4. ¿Para qué sirve el arco inverso? Den un ejemplo.**
Para corregir decisiones anteriores. En el ejemplo de la sección 6.4 el primer camino llena
A → B con 5; después, el camino O → E → F → B → A → C → D → T usa el inverso B → A y deja
A → B en 2. Sin eso el algoritmo se quedaría en 5 en lugar de 8.

**5. ¿Qué es el cuello de botella de un camino?**
La menor capacidad residual de sus arcos: lo máximo que se puede añadir por ese camino.

**6. ¿Cómo saben que el algoritmo termina?**
Las capacidades son enteras: cada paso aumenta el valor al menos en 1 y el valor está
acotado por la capacidad que sale del origen. Con BFS, además, la cantidad de pasos es como
mucho del orden de |V|·|E|.

**7. ¿Cómo obtienen el corte mínimo?**
Con la red residual final: BFS desde el origen; lo alcanzable es S, el resto T; el corte son
las rutas activas de S a T.

**8. ¿Por qué su capacidad es igual al flujo máximo?**
Porque las rutas de S a T están saturadas y de T a S no vuelve flujo, así que todo el flujo
cruza por el corte llenándolo. Y ningún flujo puede superar a ningún corte. (Sección 6.6.)

**9. ¿Cómo verifican que el flujo es correcto?**
El programa comprueba capacidad, conservación, valor neto en el origen y en el destino,
validez de la partición, saturación del corte e igualdad flujo = corte. Además, las pruebas
calculan el corte mínimo por fuerza bruta (las 512 particiones posibles) y coincide.

**10. ¿El flujo que muestran es el único posible?**
No. El valor máximo es único, pero puede haber varios repartos. En el caso manual, el
nuestro a mano (5 y 3 desde O) y el del código (6 y 2) valen 8 los dos.

**11. ¿Qué pasa si no hay camino del origen al destino?**
Flujo máximo 0, ningún camino aumentante, corte vacío de capacidad 0, y las 7
comprobaciones se siguen cumpliendo.

**12. ¿Qué pasa si intento agregar una ruta A → O?**
Se rechaza por recíproca (ya existe O → A). También se rechazan lazos, repetidas y
capacidades fuera de 1–12. La red queda intacta.

**13. ¿Por qué al ampliar I → T de 5 a 10 el flujo no sube 5?**
Porque aparece otro cuello de botella: del origen solo pueden salir 8 + 7 + 5 = 20.

**14. ¿Usaron alguna biblioteca para los algoritmos?**
No. Solo `deque` de la biblioteca estándar. Streamlit es la interfaz y Plotly dibuja.

**15. ¿Cuál es la complejidad?**
Cada BFS cuesta O(|V| + |E|). Edmonds–Karp hace como mucho O(|V|·|E|) aumentos: total
O(|V|·|E|²). En nuestra red (11 vértices, 18 arcos) hace 6 aumentos.

**16. ¿Por qué prohíben arcos recíprocos?**
Lo exige el enunciado. Además, simplifica el código: un arco residual v → u solo puede ser
el inverso de u → v, sin ambigüedad.

## 14. Ejercicios para comprobar que entendimos

1. En la red inicial, toma A como origen y T como destino. ¿Cuál es el flujo máximo y el corte?
2. Reduce la capacidad de H → T a 3. Sin ejecutar: ¿cuánto vale el flujo máximo?
3. Agrega una ruta directa O → T con capacidad 4. ¿Cuánto vale el flujo máximo?
4. En el caso manual, sube la capacidad de C → T a 12. ¿Cuál es el nuevo flujo máximo y el nuevo corte?
5. En el caso manual, desactiva A → T. ¿Flujo máximo?
6. Escribe la red residual del caso manual después del primer camino aumentante (O → A → T con 3).
7. Con DFS, el segundo camino en la red inicial fue O → A → E → H → D → I → T. ¿Por qué no es un trayecto real?
8. En la red inicial, ¿mejora el flujo si se amplía G → T a 12? ¿Y si se amplía H → T a 12?

**Soluciones (todas comprobadas con el código)**

1. 9 paquetes por hora; corte {A → D (6), A → E (3)}.
2. 13: H → T está en el corte; al bajar de 8 a 3 se pierden 5.
3. 22: la ruta nueva se suma al corte (18 + 4).
4. 10; el corte pasa a ser {O → A (6), O → B (4)}: el límite se traslada al origen.
5. 5; el corte es {C → T (5)}.
6. `O: {A: 3, B: 4}`, `A: {O: 3, C: 3}`, `B: {C: 4}`, `C: {T: 5}`, `T: {A: 3}`.
7. Porque H → D no es una ruta: es el arco inverso de D → H. Ese paso devuelve 2 paquetes de
   D → H para enviarlos por D → I.
8. Con G → T en 12 sigue en 18 (C → G limita). Con H → T en 12 sube a 20 y el corte pasa a
   ser {O → A, O → B, O → C}.

## 15. Cuestionario autocorregible (15 preguntas)

1. La etiqueta `2/5` significa: a) capacidad 2, flujo 5 b) flujo 2, capacidad 5 c) 2 rutas de 5
2. La conservación del flujo se exige en: a) todos los vértices b) los intermedios c) solo el origen
3. El valor del flujo es: a) la suma de todos los flujos b) lo que sale del origen menos lo que entra c) la mayor capacidad
4. Edmonds–Karp busca caminos aumentantes con: a) DFS b) BFS c) al azar
5. El cuello de botella de un camino es: a) su número de arcos b) la mayor capacidad residual c) la menor capacidad residual
6. Un arco inverso representa: a) una ruta de vuelta b) la posibilidad de retirar flujo c) una ruta desactivada
7. Si una ruta tiene c = 6 y x = 4, sus arcos residuales son: a) directo 2 e inverso 4 b) directo 4 e inverso 2 c) solo directo 6
8. El conjunto S del corte mínimo es: a) los vecinos del origen b) los alcanzables desde el origen en la residual final c) los vértices saturados
9. La capacidad de un corte suma: a) arcos de S a T b) arcos de T a S c) ambos
10. Flujo máximo de la red inicial: a) 20 b) 18 c) 10
11. Al desactivar H → T el flujo máximo es: a) 10 b) 13 c) 18
12. Al subir I → T a 10 el flujo máximo es: a) 23 b) 20 c) 18
13. ¿Se puede agregar T → I? a) sí b) no, es recíproco de I → T c) no, es un lazo
14. Las capacidades permitidas son: a) reales positivos b) enteros de 1 a 12 c) enteros de 0 a 20
15. El valor del flujo máximo es único, pero: a) el reparto por ruta puede variar b) el corte cambia de capacidad c) depende de DFS o BFS

**Respuestas:** 1-b, 2-b, 3-b, 4-b, 5-c, 6-b, 7-a, 8-b, 9-a, 10-b, 11-a, 12-b, 13-b, 14-b, 15-a.

## 16. Explicación de 5 minutos (para ensayar)

> Modelamos la red logística como un grafo dirigido con capacidades: 11 centros son los
> vértices, 18 rutas son los arcos y cada ruta tiene una capacidad entera de 1 a 12
> paquetes por hora. O es el origen y T el destino.
>
> Un flujo asigna a cada ruta cuántos paquetes lleva. Debe respetar la capacidad de cada
> ruta y conservarse en los centros intermedios: lo que entra, sale. Buscamos el flujo de
> mayor valor.
>
> Usamos Edmonds–Karp, que es el método de Ford–Fulkerson eligiendo los caminos con
> búsqueda en anchura. Empezamos con flujo cero. En cada paso construimos la red residual,
> que indica cuánto cabe todavía en cada ruta y, con arcos inversos, cuánto flujo ya
> asignado podríamos retirar. Con BFS buscamos el camino aumentante más corto, calculamos
> su cuello de botella y enviamos esa cantidad. Cuando no queda ningún camino, el flujo es
> máximo. En nuestra red son 6 pasos y el resultado es 18 paquetes por hora.
>
> Elegimos BFS y no DFS porque garantiza un número de pasos que no depende de las
> capacidades y porque produce caminos cortos que se pueden seguir a mano.
>
> Para el corte mínimo tomamos la última red residual: los centros todavía alcanzables
> desde el origen forman S y el resto T. Las rutas de S a T son el corte: C→G, F→T, H→T e
> I→T, que suman 3 + 2 + 8 + 5 = 18. Coincide con el flujo, como dice el teorema de flujo
> máximo y corte mínimo: esas rutas están saturadas y son el cuello de botella.
>
> El programa verifica cada resultado: capacidades, conservación, valor e igualdad con el
> corte. Y comparamos tres configuraciones: sin la ruta H→T el flujo baja a 10; ampliando
> I→T de 5 a 10 sube solo a 20, porque el cuello de botella se traslada a la salida del origen.
