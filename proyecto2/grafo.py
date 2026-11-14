"""
Modelo de la red de distribución (Proyecto 2).

La red es un grafo dirigido G = (V, E) con una función de capacidad c:
  - cada vértice de V es un centro logístico;
  - cada arco (u, v) de E es una ruta de transporte que va de u a v;
  - c(u, v) es el máximo de paquetes por hora que admite esa ruta
    (un entero entre 1 y 12).

Toda la red se guarda en un diccionario sencillo, igual al de los archivos JSON:

    red = {
        "nombre":   "Red inicial de distribución",
        "vertices": ["O", "A", ...],
        "origen":   "O",
        "destino":  "T",
        "arcos":    [{"origen": "O", "destino": "A", "capacidad": 8, "activo": True}, ...],
    }

Una ruta desactivada NO se borra: solo se marca con "activo": False. Así se
puede reactivar después y la red original nunca se pierde.

Este archivo solo administra la red (cargar, validar y modificar).
Los algoritmos de flujo están en algoritmos.py.
"""

import copy
import json

# Límites que el enunciado exige ÚNICAMENTE a la configuración inicial.
MINIMO_VERTICES = 10
MAXIMO_VERTICES = 12
MINIMO_ARCOS = 15
MAXIMO_ARCOS = 20

# Límites de capacidad: valen siempre, también después de modificar la red.
CAPACIDAD_MINIMA = 1
CAPACIDAD_MAXIMA = 12


def cargar_red(ruta_archivo):
    """Lee una red desde un archivo JSON y la devuelve como diccionario."""
    with open(ruta_archivo, encoding="utf-8") as archivo:
        return json.load(archivo)


def copiar_red(red):
    """
    Devuelve una copia totalmente independiente de la red.

    Se usa para que cada escenario modificado parta de la red original sin
    alterarla (si solo se copiara la referencia, los cambios se mezclarían).
    """
    return copy.deepcopy(red)


def texto_arco(origen, destino):
    """Devuelve la ruta escrita para personas, por ejemplo 'H → T'."""
    return f"{origen} → {destino}"


def buscar_arco(red, origen, destino):
    """
    Busca la ruta origen → destino entre TODAS las rutas (activas o no).

    Devuelve el diccionario del arco o None si no existe.
    """
    for arco in red["arcos"]:
        if arco["origen"] == origen and arco["destino"] == destino:
            return arco
    return None


def capacidades_activas(red):
    """
    Devuelve las rutas utilizables como diccionario (origen, destino) -> capacidad.

    TODOS los cálculos parten de esta función; por eso una ruta desactivada
    nunca transporta flujo ni aparece en un corte.
    """
    capacidades = {}
    for arco in red["arcos"]:
        if arco["activo"]:
            capacidades[(arco["origen"], arco["destino"])] = arco["capacidad"]
    return capacidades


def arcos_desactivados(red):
    """Devuelve la lista de rutas desactivadas como pares (origen, destino)."""
    desactivados = []
    for arco in red["arcos"]:
        if not arco["activo"]:
            desactivados.append((arco["origen"], arco["destino"]))
    return desactivados


# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

def validar_capacidad(capacidad):
    """
    Lanza ValueError si la capacidad no es un entero entre 1 y 12.

    Se descarta `bool` a propósito: en Python True cuenta como el entero 1, y
    no queremos aceptar por accidente un valor que no es un número.
    """
    es_entero = isinstance(capacidad, int) and not isinstance(capacidad, bool)
    if not es_entero or not CAPACIDAD_MINIMA <= capacidad <= CAPACIDAD_MAXIMA:
        raise ValueError(
            f"La capacidad debe ser un número entero entre {CAPACIDAD_MINIMA} y "
            f"{CAPACIDAD_MAXIMA} paquetes por hora."
        )


def validar_arco_nuevo(red, origen, destino, capacidad):
    """
    Comprueba que la ruta origen → destino se puede agregar a la red.

    Lanza ValueError con un mensaje claro si la conexión está prohibida:
      - algún extremo no es un centro de la red;
      - es un lazo (origen = destino);
      - ya existe esa misma ruta (repetida);
      - ya existe la ruta contraria destino → origen (recíproca);
      - la capacidad no es un entero entre 1 y 12.

    Las rutas desactivadas también cuentan: siguen perteneciendo a la red y
    se pueden reactivar, así que aceptar una repetida o una recíproca de una
    ruta desactivada produciría una red prohibida en cuanto se reactivara.
    """
    if origen not in red["vertices"] or destino not in red["vertices"]:
        raise ValueError("Los dos extremos de la ruta deben ser centros de la red.")
    if origen == destino:
        raise ValueError(
            f"No se admite el lazo {texto_arco(origen, destino)}: "
            "una ruta debe unir dos centros distintos."
        )
    if buscar_arco(red, origen, destino) is not None:
        raise ValueError(
            f"La ruta {texto_arco(origen, destino)} ya existe: no se admiten arcos repetidos."
        )
    if buscar_arco(red, destino, origen) is not None:
        raise ValueError(
            f"Ya existe la ruta contraria {texto_arco(destino, origen)}: "
            "no se admiten arcos recíprocos."
        )
    validar_capacidad(capacidad)


def validar_estructura(red):
    """
    Revisa las reglas que la red debe cumplir SIEMPRE (también tras modificarla).

    Devuelve una lista de problemas en texto; la lista vacía significa que la
    red es válida.
    """
    problemas = []
    vertices = red["vertices"]

    if len(set(vertices)) != len(vertices):
        problemas.append("Hay vértices con el nombre repetido.")
    if red["origen"] not in vertices or red["destino"] not in vertices:
        problemas.append("El origen y el destino deben ser vértices de la red.")
    if red["origen"] == red["destino"]:
        problemas.append("El origen y el destino deben ser vértices distintos.")

    arcos_vistos = set()
    for arco in red["arcos"]:
        origen = arco["origen"]
        destino = arco["destino"]
        if origen not in vertices or destino not in vertices:
            problemas.append(f"El arco {texto_arco(origen, destino)} usa un vértice inexistente.")
        if origen == destino:
            problemas.append(f"El arco {texto_arco(origen, destino)} es un lazo.")
        if (origen, destino) in arcos_vistos:
            problemas.append(f"El arco {texto_arco(origen, destino)} está repetido.")
        if (destino, origen) in arcos_vistos:
            problemas.append(
                f"Los arcos {texto_arco(origen, destino)} y {texto_arco(destino, origen)} son recíprocos."
            )
        try:
            validar_capacidad(arco["capacidad"])
        except ValueError:
            problemas.append(
                f"El arco {texto_arco(origen, destino)} tiene una capacidad no permitida: "
                f"{arco['capacidad']}."
            )
        arcos_vistos.add((origen, destino))
    return problemas


def buscar_vertices_aislados(red):
    """Devuelve los vértices a los que no llega ni de los que sale ningún arco."""
    conectados = set()
    for arco in red["arcos"]:
        conectados.add(arco["origen"])
        conectados.add(arco["destino"])
    aislados = []
    for vertice in red["vertices"]:
        if vertice not in conectados:
            aislados.append(vertice)
    return aislados


def validar_tamano_inicial(red):
    """
    Revisa las condiciones que el enunciado exige SOLO a la configuración inicial:
    10 ≤ |V| ≤ 12, 15 ≤ |E| ≤ 20 y ningún vértice aislado.

    Devuelve una lista de problemas (vacía si todo se cumple). No debe usarse
    para rechazar redes ya modificadas por el usuario.
    """
    problemas = []
    cantidad_vertices = len(red["vertices"])
    cantidad_arcos = len(red["arcos"])

    if not MINIMO_VERTICES <= cantidad_vertices <= MAXIMO_VERTICES:
        problemas.append(
            f"La red inicial debe tener entre {MINIMO_VERTICES} y {MAXIMO_VERTICES} "
            f"vértices y tiene {cantidad_vertices}."
        )
    if not MINIMO_ARCOS <= cantidad_arcos <= MAXIMO_ARCOS:
        problemas.append(
            f"La red inicial debe tener entre {MINIMO_ARCOS} y {MAXIMO_ARCOS} "
            f"arcos y tiene {cantidad_arcos}."
        )
    aislados = buscar_vertices_aislados(red)
    if aislados:
        problemas.append("Hay vértices aislados: " + ", ".join(aislados) + ".")
    return problemas


# ---------------------------------------------------------------------------
# Modificaciones (todas actúan sobre la red recibida)
# ---------------------------------------------------------------------------

def desactivar_arco(red, origen, destino):
    """Marca la ruta origen → destino como desactivada (deja de transportar)."""
    arco = buscar_arco(red, origen, destino)
    if arco is None:
        raise ValueError(f"La ruta {texto_arco(origen, destino)} no existe.")
    if not arco["activo"]:
        raise ValueError(f"La ruta {texto_arco(origen, destino)} ya está desactivada.")
    arco["activo"] = False


def reactivar_arco(red, origen, destino):
    """Vuelve a habilitar una ruta que estaba desactivada."""
    arco = buscar_arco(red, origen, destino)
    if arco is None:
        raise ValueError(f"La ruta {texto_arco(origen, destino)} no existe.")
    if arco["activo"]:
        raise ValueError(f"La ruta {texto_arco(origen, destino)} no está desactivada.")
    arco["activo"] = True


def cambiar_capacidad(red, origen, destino, capacidad):
    """
    Cambia la capacidad de una ruta existente por otro entero entre 1 y 12.

    Si el valor no es válido lanza ValueError y la red queda como estaba.
    """
    arco = buscar_arco(red, origen, destino)
    if arco is None:
        raise ValueError(f"La ruta {texto_arco(origen, destino)} no existe.")
    validar_capacidad(capacidad)
    arco["capacidad"] = capacidad


def agregar_arco(red, origen, destino, capacidad):
    """
    Agrega la ruta dirigida origen → destino con la capacidad indicada, ya activa.

    Antes la valida con validar_arco_nuevo; si está prohibida lanza ValueError
    y la red queda exactamente como estaba.
    """
    validar_arco_nuevo(red, origen, destino, capacidad)
    red["arcos"].append(
        {"origen": origen, "destino": destino, "capacidad": capacidad, "activo": True}
    )


def cambiar_extremos(red, origen, destino):
    """
    Cambia los vértices elegidos como origen (s) y destino (t).

    Lanza ValueError si no pertenecen a la red o si coinciden (con s = t no
    hay nada que transportar: los paquetes ya estarían en su destino).
    """
    if origen not in red["vertices"] or destino not in red["vertices"]:
        raise ValueError("El origen y el destino deben ser centros de la red.")
    if origen == destino:
        raise ValueError("El origen y el destino deben ser centros distintos.")
    red["origen"] = origen
    red["destino"] = destino
