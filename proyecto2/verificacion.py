"""Validación de resultados, escenarios e informe de consola.

Este módulo comprueba capacidades, conservación, valor del flujo y corte
mínimo. También prepara los escenarios de comparación de la aplicación.
"""

from pathlib import Path

from algoritmos import analizar_red
from grafo import (
    cambiar_capacidad,
    capacidades_activas,
    cargar_red,
    copiar_red,
    desactivar_arco,
    texto_arco,
    validar_estructura,
    validar_tamano_inicial,
)

CARPETA_DATOS = Path(__file__).resolve().parent / "datos"
ARCHIVO_RED_INICIAL = CARPETA_DATOS / "red_inicial.json"
ARCHIVO_CASO_MANUAL = CARPETA_DATOS / "caso_manual.json"


def texto_camino(camino):
    """Escribe un camino para personas: ['O','A','T'] -> 'O → A → T'."""
    return " → ".join(camino)


def buscar_violaciones_de_capacidad(capacidades, flujo):
    """
    Devuelve las rutas cuyo flujo NO cumple 0 ≤ x ≤ c (o no es un entero).
    La lista vacía significa que todas las rutas respetan su capacidad.
    """
    violaciones = []
    for arco, capacidad in capacidades.items():
        unidades = flujo[arco]
        es_entero = isinstance(unidades, int) and not isinstance(unidades, bool)
        if not es_entero or unidades < 0 or unidades > capacidad:
            violaciones.append(arco)
    return violaciones


def calcular_balances(vertices, flujo):
    """
    Para cada vértice, suma el flujo que entra y el flujo que sale.

    Salida: diccionario vértice -> {"entra": número, "sale": número}.
    """
    balances = {}
    for vertice in vertices:
        balances[vertice] = {"entra": 0, "sale": 0}
    for (u, v), unidades in flujo.items():
        balances[u]["sale"] += unidades
        balances[v]["entra"] += unidades
    return balances


def buscar_violaciones_de_conservacion(vertices, flujo, origen, destino):
    """
    Devuelve los vértices intermedios donde entra una cantidad distinta de la
    que sale. La lista vacía significa que el flujo se conserva.
    """
    balances = calcular_balances(vertices, flujo)
    violaciones = []
    for vertice in vertices:
        if vertice in (origen, destino):
            continue
        if balances[vertice]["entra"] != balances[vertice]["sale"]:
            violaciones.append(vertice)
    return violaciones


def contar_caminos_simples(adyacencia, actual, destino, visitados):
    """
    Cuenta los caminos dirigidos distintos (sin repetir vértices) de `actual`
    a `destino`. Solo se usa para comprobar que la red inicial ofrece al menos
    dos caminos, como pide el enunciado.
    """
    if actual == destino:
        return 1
    cantidad = 0
    for vecino in adyacencia[actual]:
        if vecino not in visitados:
            cantidad += contar_caminos_simples(adyacencia, vecino, destino, visitados | {vecino})
    return cantidad


def construir_adyacencia(vertices, capacidades):
    """Listas de sucesores de cada vértice usando solo las rutas activas."""
    adyacencia = {}
    for vertice in vertices:
        adyacencia[vertice] = []
    for u, v in capacidades:
        adyacencia[u].append(v)
    return adyacencia


def verificar_resultado(red, resultado):
    """Comprueba que el resultado contiene un flujo y un corte válidos."""
    vertices = red["vertices"]
    capacidades = capacidades_activas(red)
    origen = red["origen"]
    destino = red["destino"]
    flujo = resultado["flujo"]
    lado_origen = resultado["lado_origen"]
    lado_destino = resultado["lado_destino"]
    corte = resultado["corte"]
    comprobaciones = []

    def anotar(comprobacion, cumple, detalle):
        """Añade una comprobación con su estado y explicación."""
        comprobaciones.append({"comprobacion": comprobacion, "cumple": cumple, "detalle": detalle})

    fuera_de_rango = buscar_violaciones_de_capacidad(capacidades, flujo)
    if fuera_de_rango:
        detalle = "No cumplen: " + ", ".join(texto_arco(u, v) for u, v in fuera_de_rango)
    else:
        detalle = f"{len(capacidades)} rutas activas revisadas"
    anotar(
        "Capacidad: 0 ≤ flujo ≤ capacidad en cada ruta activa",
        fuera_de_rango == [] and set(flujo) == set(capacidades),
        detalle,
    )

    sin_conservar = buscar_violaciones_de_conservacion(vertices, flujo, origen, destino)
    if sin_conservar:
        detalle = "No se conserva en: " + ", ".join(sin_conservar)
    else:
        detalle = f"{len(vertices) - 2} centros intermedios revisados"
    anotar(
        "Conservación: en cada centro intermedio entra lo mismo que sale",
        sin_conservar == [],
        detalle,
    )

    balances = calcular_balances(vertices, flujo)
    neto_origen = balances[origen]["sale"] - balances[origen]["entra"]
    neto_destino = balances[destino]["entra"] - balances[destino]["sale"]
    anotar(
        "Valor del flujo = flujo neto que sale del origen",
        resultado["flujo_maximo"] == neto_origen,
        f"sale {balances[origen]['sale']} − entra {balances[origen]['entra']} = {neto_origen}",
    )
    anotar(
        "El mismo valor llega, neto, al destino",
        resultado["flujo_maximo"] == neto_destino,
        f"entra {balances[destino]['entra']} − "
        f"sale {balances[destino]['sale']} = {neto_destino}",
    )

    particion_valida = (
        origen in lado_origen
        and destino in lado_destino
        and len(lado_origen) + len(lado_destino) == len(vertices)
        and set(lado_origen) | set(lado_destino) == set(vertices)
    )
    anotar(
        "Partición: origen en S, destino en T, cada centro en un solo lado",
        particion_valida,
        f"|S| = {len(lado_origen)}, |T| = {len(lado_destino)}",
    )

    cruces_correctos = True
    for (u, v), capacidad in capacidades.items():
        va_de_s_a_t = u in lado_origen and v in lado_destino
        va_de_t_a_s = u in lado_destino and v in lado_origen
        if va_de_s_a_t != ((u, v) in corte):
            cruces_correctos = False
        if va_de_s_a_t and flujo[(u, v)] != capacidad:
            cruces_correctos = False
        if va_de_t_a_s and flujo[(u, v)] != 0:
            cruces_correctos = False
    anotar(
        "Corte: sus rutas van de S a T y están saturadas; de T a S no vuelve flujo",
        cruces_correctos,
        f"{len(corte)} ruta(s) en el corte",
    )

    suma = " + ".join(str(capacidades[arco]) for arco in corte) or "0"
    capacidad_corte = sum(capacidades[arco] for arco in corte)
    anotar(
        "Flujo máximo = capacidad del corte mínimo",
        resultado["flujo_maximo"] == capacidad_corte == resultado["capacidad_corte"],
        f"{resultado['flujo_maximo']} = {suma} = {capacidad_corte}",
    )
    return comprobaciones


def todo_cumple(comprobaciones):
    """True si todas las comprobaciones de la lista se cumplen."""
    for comprobacion in comprobaciones:
        if not comprobacion["cumple"]:
            return False
    return True


def comprobar_condiciones_iniciales(red):
    """Comprueba tamaño, estructura, capacidades y caminos de la red inicial."""
    problemas_tamano = validar_tamano_inicial(red)
    problemas_estructura = validar_estructura(red)
    capacidades = capacidades_activas(red)
    adyacencia = construir_adyacencia(red["vertices"], capacidades)
    caminos = contar_caminos_simples(adyacencia, red["origen"], red["destino"], {red["origen"]})
    return [
        {
            "comprobacion": "10 ≤ |V| ≤ 12, 15 ≤ |E| ≤ 20 y ningún vértice aislado",
            "cumple": problemas_tamano == [],
            "detalle": f"|V| = {len(red['vertices'])}, |E| = {len(red['arcos'])}",
        },
        {
            "comprobacion": "Sin lazos, arcos repetidos ni recíprocos; origen ≠ destino",
            "cumple": not any("capacidad" not in problema for problema in problemas_estructura),
            "detalle": (
                "Sin problemas" if not problemas_estructura else "; ".join(problemas_estructura)
            ),
        },
        {
            "comprobacion": "Capacidades enteras entre 1 y 12 paquetes por hora",
            "cumple": not any("capacidad" in problema for problema in problemas_estructura),
            "detalle": f"mínima {min(capacidades.values())}, máxima {max(capacidades.values())}",
        },
        {
            "comprobacion": "Al menos dos caminos dirigidos distintos del origen al destino",
            "cumple": caminos >= 2,
            "detalle": f"Se hallaron {caminos} caminos distintos",
        },
    ]


def construir_escenarios(red_original):
    """Crea la red inicial y dos copias con modificaciones independientes."""
    sin_ruta = copiar_red(red_original)
    desactivar_arco(sin_ruta, "H", "T")

    con_mas_capacidad = copiar_red(red_original)
    cambiar_capacidad(con_mas_capacidad, "I", "T", 10)

    return [
        {"nombre": "Red inicial", "cambio": "Ninguno", "red": copiar_red(red_original)},
        {"nombre": "Modificación 1", "cambio": "Desactivar H → T", "red": sin_ruta},
        {
            "nombre": "Modificación 2",
            "cambio": "Capacidad de I → T: 5 → 10",
            "red": con_mas_capacidad,
        },
    ]


def comparar_escenarios(red_original):
    """Analiza y verifica todos los escenarios generados."""
    comparacion = []
    for escenario in construir_escenarios(red_original):
        resultado = analizar_red(escenario["red"])
        escenario["resultado"] = resultado
        escenario["comprobaciones"] = verificar_resultado(escenario["red"], resultado)
        comparacion.append(escenario)
    return comparacion


def imprimir_comprobaciones(comprobaciones):
    """Imprime una lista de comprobaciones con una marca de estado."""
    for comprobacion in comprobaciones:
        marca = "OK   " if comprobacion["cumple"] else "FALLA"
        print(f"  [{marca}] {comprobacion['comprobacion']} ({comprobacion['detalle']})")


def imprimir_resultado(titulo, red):
    """Imprime el flujo por ruta, los pasos del algoritmo, el corte y las comprobaciones."""
    resultado = analizar_red(red)
    capacidades = resultado["capacidades"]
    print(f"\n=== {titulo} ===")
    print(
        f"Origen: {red['origen']}   Destino: {red['destino']}   "
        f"Rutas activas: {len(capacidades)}"
    )
    print(f"FLUJO MÁXIMO: {resultado['flujo_maximo']} paquetes por hora")
    print("Flujo / capacidad por ruta:")
    for (u, v), capacidad in capacidades.items():
        print(f"  {texto_arco(u, v)}: {resultado['flujo'][(u, v)]}/{capacidad}")
    print("Caminos aumentantes (Edmonds–Karp):")
    for numero, paso in enumerate(resultado["pasos"], start=1):
        inversos = ""
        if paso["arcos_inversos"]:
            inversos = (
                "  [usa arco inverso: "
                + ", ".join(texto_arco(u, v) for u, v in paso["arcos_inversos"])
                + "]"
            )
        print(
            f"  {numero}. {texto_camino(paso['camino'])}  "
            f"cuello de botella {paso['cuello_de_botella']}  "
            f"acumulado {paso['flujo_acumulado']}{inversos}"
        )
    print(f"S = {{{', '.join(resultado['lado_origen'])}}}")
    print(f"T = {{{', '.join(resultado['lado_destino'])}}}")
    if resultado["corte"]:
        rutas = ", ".join(
            f"{texto_arco(u, v)}({capacidades[(u, v)]})" for u, v in resultado["corte"]
        )
        print(f"Corte mínimo: {{{rutas}}}  capacidad = {resultado['capacidad_corte']}")
    else:
        print("Corte mínimo: ∅ (ninguna ruta va de S a T), capacidad = 0")
    imprimir_comprobaciones(verificar_resultado(red, resultado))


def imprimir_informe():
    """Imprime condiciones iniciales, los tres escenarios y el caso manual."""
    red_original = cargar_red(ARCHIVO_RED_INICIAL)
    print("CONDICIONES DE LA CONFIGURACIÓN INICIAL")
    imprimir_comprobaciones(comprobar_condiciones_iniciales(red_original))
    for escenario in construir_escenarios(red_original):
        imprimir_resultado(f"{escenario['nombre']} — {escenario['cambio']}", escenario["red"])
    imprimir_resultado("Caso manual de 5 vértices", cargar_red(ARCHIVO_CASO_MANUAL))


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    imprimir_informe()
