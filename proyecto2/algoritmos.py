"""Cálculo de flujo máximo y corte mínimo sin bibliotecas de grafos.

El flujo máximo se obtiene con Edmonds-Karp y el corte mínimo se extrae de la
red residual final. Las capacidades recibidas corresponden a rutas activas.
"""

from collections import deque

from grafo import capacidades_activas

ESTRATEGIA_ANCHURA = "anchura"
ESTRATEGIA_PROFUNDIDAD = "profundidad"


def arcos_de_camino(camino):
    """Devuelve los pares consecutivos de un camino: [O, A, T] -> [(O, A), (A, T)]."""
    arcos = []
    for posicion in range(len(camino) - 1):
        arcos.append((camino[posicion], camino[posicion + 1]))
    return arcos


def comprobar_red_admisible(vertices, capacidades, origen, destino):
    """
    Lanza ValueError si la red no cumple lo que el algoritmo necesita.

    - Origen y destino distintos y pertenecientes a la red.
    - Sin lazos ni arcos recíprocos. Gracias a esto, un arco residual v → u
      solo puede significar "devolver flujo de la ruta u → v": nunca se
      confunde con una ruta original en ese sentido.
    - Capacidades enteras positivas. Con enteros, cada camino aumentante sube
      el flujo al menos en 1, y por eso el algoritmo termina.
    """
    if origen not in vertices or destino not in vertices:
        raise ValueError("El origen y el destino deben ser vértices de la red.")
    if origen == destino:
        raise ValueError("El origen y el destino deben ser vértices distintos.")
    for (u, v), capacidad in capacidades.items():
        if u == v:
            raise ValueError(f"Lazo no admitido: {u} → {v}.")
        if (v, u) in capacidades:
            raise ValueError(f"Arcos recíprocos no admitidos: {u} ↔ {v}.")
        es_entero = isinstance(capacidad, int) and not isinstance(capacidad, bool)
        if not es_entero or capacidad <= 0:
            raise ValueError(f"La capacidad de {u} → {v} debe ser un entero positivo.")


def construir_red_residual(vertices, capacidades, flujo):
    """Construye la red residual del flujo actual, omitiendo capacidades cero."""
    residual = {}
    for vertice in vertices:
        residual[vertice] = {}
    for (u, v), capacidad in capacidades.items():
        disponible = capacidad - flujo[(u, v)]
        if disponible > 0:
            residual[u][v] = disponible
        if flujo[(u, v)] > 0:
            residual[v][u] = flujo[(u, v)]
    return residual


def recorrer_en_anchura(residual, inicio):
    """
    Recorre la red residual en anchura (BFS) desde el vértice inicio.

    La cola atiende los vértices en el orden en que se descubren: primero los
    que están a 1 arco, luego a 2, etc. Por eso el camino que se reconstruye
    hacia cualquier vértice tiene el menor número de arcos posible.

    Salida: diccionario padre, donde padre[v] es el vértice desde el que se
    descubrió v (padre[inicio] es None). Sus claves son exactamente los
    vértices alcanzables desde inicio.
    """
    padre = {inicio: None}
    cola = deque([inicio])
    while cola:
        actual = cola.popleft()
        for vecino in residual[actual]:
            if vecino not in padre:
                padre[vecino] = actual
                cola.append(vecino)
    return padre


def reconstruir_camino(padre, destino):
    """Reconstruye el camino inicio → destino siguiendo los padres hacia atrás."""
    camino = []
    vertice = destino
    while vertice is not None:
        camino.append(vertice)
        vertice = padre[vertice]
    camino.reverse()
    return camino


def buscar_camino_en_anchura(residual, origen, destino):
    """
    Busca con BFS un camino aumentante: un camino de origen a destino en la
    red residual. Devuelve la lista de vértices o None si no existe.
    """
    padre = recorrer_en_anchura(residual, origen)
    if destino not in padre:
        return None
    return reconstruir_camino(padre, destino)


def buscar_camino_en_profundidad(residual, actual, destino, visitados=None):
    """
    Busca un camino aumentante con DFS (se incluye SOLO para comparar estrategias).

    Avanza por el primer arco residual disponible hasta donde pueda y retrocede
    si se queda sin opciones. Encuentra un camino si existe, pero no
    necesariamente el más corto.
    """
    if visitados is None:
        visitados = set()
    visitados.add(actual)
    if actual == destino:
        return [actual]
    for vecino in residual[actual]:
        if vecino not in visitados:
            resto = buscar_camino_en_profundidad(residual, vecino, destino, visitados)
            if resto is not None:
                return [actual] + resto
    return None


def calcular_cuello_de_botella(residual, camino):
    """
    Devuelve la menor capacidad residual a lo largo del camino.

    Es la cantidad máxima de paquetes por hora que se puede añadir por ese
    camino sin superar la capacidad de ninguno de sus arcos.
    """
    cuello = None
    for u, v in arcos_de_camino(camino):
        if cuello is None or residual[u][v] < cuello:
            cuello = residual[u][v]
    return cuello


def aumentar_flujo(flujo, camino, cantidad):
    """
    Envía `cantidad` paquetes por hora a lo largo de un camino aumentante.

    Para cada arco residual u → v del camino:
      - si u → v es una ruta original, su flujo AUMENTA en `cantidad`;
      - si no lo es, se trata de un arco inverso: el flujo de la ruta
        original v → u DISMINUYE en `cantidad` (esos paquetes se redirigen).

    Modifica el diccionario flujo recibido.
    """
    for u, v in arcos_de_camino(camino):
        if (u, v) in flujo:
            flujo[(u, v)] += cantidad
        else:
            flujo[(v, u)] -= cantidad


def calcular_valor_del_flujo(flujo, origen):
    """
    Valor del flujo |x| = lo que sale del origen menos lo que entra al origen.
    """
    valor = 0
    for (u, v), unidades in flujo.items():
        if u == origen:
            valor += unidades
        if v == origen:
            valor -= unidades
    return valor


def calcular_flujo_maximo(vertices, capacidades, origen, destino, estrategia=ESTRATEGIA_ANCHURA):
    """Calcula el flujo máximo y registra cada camino aumentante utilizado."""
    comprobar_red_admisible(vertices, capacidades, origen, destino)

    flujo = {}
    for arco in capacidades:
        flujo[arco] = 0

    pasos = []
    flujo_acumulado = 0
    while True:
        residual = construir_red_residual(vertices, capacidades, flujo)
        if estrategia == ESTRATEGIA_ANCHURA:
            camino = buscar_camino_en_anchura(residual, origen, destino)
        else:
            camino = buscar_camino_en_profundidad(residual, origen, destino)
        if camino is None:
            break

        cuello = calcular_cuello_de_botella(residual, camino)
        aumentar_flujo(flujo, camino, cuello)
        flujo_acumulado += cuello

        arcos_inversos = []
        for arco in arcos_de_camino(camino):
            if arco not in capacidades:
                arcos_inversos.append(arco)
        pasos.append(
            {
                "camino": camino,
                "cuello_de_botella": cuello,
                "arcos_inversos": arcos_inversos,
                "flujo_acumulado": flujo_acumulado,
            }
        )
    return flujo, pasos


def encontrar_corte_minimo(vertices, capacidades, flujo, origen):
    """Obtiene la partición y los arcos del corte mínimo desde la red residual."""
    residual = construir_red_residual(vertices, capacidades, flujo)
    alcanzables = recorrer_en_anchura(residual, origen)

    lado_origen = []
    lado_destino = []
    for vertice in vertices:
        if vertice in alcanzables:
            lado_origen.append(vertice)
        else:
            lado_destino.append(vertice)

    arcos_del_corte = []
    capacidad_del_corte = 0
    for (u, v), capacidad in capacidades.items():
        if u in alcanzables and v not in alcanzables:
            arcos_del_corte.append((u, v))
            capacidad_del_corte += capacidad
    return lado_origen, lado_destino, arcos_del_corte, capacidad_del_corte


def analizar_red_logistica(vertices, capacidades, origen, destino):
    """
    Calcula el flujo máximo y un corte mínimo, y reúne los resultados.
    Salida: diccionario con
      - "origen", "destino"
      - "capacidades": rutas activas y su capacidad
      - "flujo": flujo final de cada ruta activa
      - "flujo_maximo": valor del flujo (paquetes por hora)
      - "pasos": caminos aumentantes usados (ver calcular_flujo_maximo)
      - "lado_origen", "lado_destino": partición S / T del corte mínimo
      - "corte": rutas que cruzan de S a T
      - "capacidad_corte": suma de sus capacidades
    """
    flujo, pasos = calcular_flujo_maximo(vertices, capacidades, origen, destino)
    lado_origen, lado_destino, corte, capacidad_corte = encontrar_corte_minimo(
        vertices, capacidades, flujo, origen
    )
    return {
        "origen": origen,
        "destino": destino,
        "capacidades": capacidades,
        "flujo": flujo,
        "flujo_maximo": calcular_valor_del_flujo(flujo, origen),
        "pasos": pasos,
        "lado_origen": lado_origen,
        "lado_destino": lado_destino,
        "corte": corte,
        "capacidad_corte": capacidad_corte,
    }


def analizar_red(red):
    """Analiza una red completa (diccionario de grafo.py) usando solo sus rutas activas."""
    return analizar_red_logistica(
        red["vertices"], capacidades_activas(red), red["origen"], red["destino"]
    )
