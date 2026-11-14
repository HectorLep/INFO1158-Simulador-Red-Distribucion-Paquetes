"""
Dibujo de la red de distribución con Plotly (Proyecto 2).

Plotly se usa ÚNICAMENTE para representar: círculos (centros), flechas (rutas)
y etiquetas (capacidad o flujo/capacidad). Aquí no se calcula ningún flujo;
los resultados llegan ya calculados desde algoritmos.py.

Las posiciones de los centros vienen del archivo de datos, por lo que el
dibujo no se mueve cuando se desactiva, se modifica o se agrega una ruta.
"""

import math

import plotly.graph_objects as go

from grafo import texto_arco

# Modos de visualización: cada uno muestra UNA cosa para que el grafo sea legible.
MODO_CAPACIDADES = "Capacidades"
MODO_FLUJO = "Flujo máximo"
MODO_CORTE = "Corte mínimo"
MODOS = [MODO_CAPACIDADES, MODO_FLUJO, MODO_CORTE]

RADIO_VERTICE = 0.42            # en las mismas unidades que las posiciones
HOLGURA_MINIMA = 0.6            # distancia mínima entre un trazo y otro centro
POSICION_ETIQUETA = 0.4         # fracción del trazo donde se escribe la etiqueta

COLOR_TEXTO = "#0b0b0b"
COLOR_TEXTO_TENUE = "#898781"
COLOR_ARCO = "#52514e"          # ruta activa sin resaltar
COLOR_ARCO_TENUE = "#c3c2b7"    # ruta sin flujo, o fuera del corte
COLOR_DESACTIVADO = "#b3b2aa"   # ruta desactivada (además va punteada)
COLOR_FLUJO = "#2a78d6"         # ruta con flujo y capacidad libre
COLOR_SATURADO = "#104281"      # ruta con flujo = capacidad
COLOR_CORTE = "#d03b3b"         # rutas del corte mínimo
COLOR_EXTREMO = "#26251f"       # relleno del origen y del destino
COLOR_LADO_ORIGEN = "#cde2fb"   # centros del conjunto S
COLOR_LADO_DESTINO = "#fbe0d2"  # centros del conjunto T
COLOR_FONDO = "#ffffff"


def elegir_estilo_de_arco(arco, resultado, modo):
    """
    Decide cómo se dibuja una ruta según el modo de visualización.

    Entradas: el diccionario del arco, el resultado (o None) y el modo.
    Salida: {"color", "ancho", "linea", "etiqueta", "negrita", "descripcion"}.
    """
    par = (arco["origen"], arco["destino"])
    capacidad = arco["capacidad"]
    nombre = texto_arco(arco["origen"], arco["destino"])

    if not arco["activo"]:
        return {"color": COLOR_DESACTIVADO, "ancho": 1.5, "linea": "dot",
                "etiqueta": f"({capacidad})", "negrita": False,
                "descripcion": f"Ruta {nombre}: desactivada (capacidad {capacidad})"}

    if resultado is None or modo == MODO_CAPACIDADES:
        return {"color": COLOR_ARCO, "ancho": 1.8, "linea": "solid",
                "etiqueta": str(capacidad), "negrita": False,
                "descripcion": f"Ruta {nombre}: capacidad {capacidad} paquetes/h"}

    flujo = resultado["flujo"][par]
    saturada = flujo == capacidad
    estilo = {
        "etiqueta": f"{flujo}/{capacidad}", "negrita": saturada, "linea": "solid",
        "descripcion": f"Ruta {nombre}: flujo {flujo} de {capacidad} paquetes/h"
                       + (" (saturada)" if saturada else ""),
    }
    if modo == MODO_CORTE:
        if par in resultado["corte"]:
            estilo.update({"color": COLOR_CORTE, "ancho": 4, "linea": "dash", "negrita": True})
        else:
            estilo.update({"color": COLOR_ARCO_TENUE, "ancho": 1.5, "negrita": False})
    elif flujo == 0:
        estilo.update({"color": COLOR_ARCO_TENUE, "ancho": 1.5})
    else:
        # El grosor crece con el flujo: a simple vista se ve por dónde pasan más paquetes.
        estilo.update({"color": COLOR_SATURADO if saturada else COLOR_FLUJO,
                       "ancho": 1.5 + 0.45 * flujo})
    return estilo


def punto_de_curva(inicio, control, fin, t):
    """
    Punto de la curva que va de `inicio` a `fin` "atraída" por `control`
    (curva cuadrática de Bézier); t = 0 es el inicio y t = 1 el final.
    Si el control está en la mitad del segmento, la curva es una línea recta.
    """
    x = (1 - t) ** 2 * inicio[0] + 2 * (1 - t) * t * control[0] + t ** 2 * fin[0]
    y = (1 - t) ** 2 * inicio[1] + 2 * (1 - t) * t * control[1] + t ** 2 * fin[1]
    return (x, y)


def calcular_holgura(posiciones, origen, destino, control):
    """Menor distancia entre el trazo origen → destino y los demás centros."""
    holgura = float("inf")
    for paso in range(1, 20):
        punto = punto_de_curva(posiciones[origen], control, posiciones[destino], paso / 20)
        for vertice, posicion in posiciones.items():
            if vertice not in (origen, destino):
                holgura = min(holgura, math.dist(punto, posicion))
    return holgura


def elegir_punto_de_control(posiciones, origen, destino):
    """
    Decide si la ruta se dibuja recta o curvada.

    Lo normal es una línea recta. Solo si la recta pasara por encima de otro
    centro (puede ocurrir con rutas agregadas por el usuario) se prueba a
    curvarla hacia un lado y hacia el otro, y se elige el primer trazo que
    queda despejado. Es una decisión puramente visual: no cambia el grafo.
    """
    x0, y0 = posiciones[origen]
    x1, y1 = posiciones[destino]
    medio = ((x0 + x1) / 2, (y0 + y1) / 2)
    mejor_control = medio
    mejor_holgura = -1.0
    for desvio in (0, 0.25, -0.25, 0.5, -0.5):          # 0 = línea recta
        # Se desplaza el control en dirección perpendicular al segmento.
        control = (medio[0] - (y1 - y0) * desvio, medio[1] + (x1 - x0) * desvio)
        holgura = calcular_holgura(posiciones, origen, destino, control)
        if holgura >= HOLGURA_MINIMA:
            return control
        if holgura > mejor_holgura:
            mejor_control, mejor_holgura = control, holgura
    return mejor_control


def acercar(punto, hacia, distancia):
    """Devuelve el punto desplazado `distancia` unidades en dirección a `hacia`."""
    largo = math.dist(punto, hacia)
    return (
        punto[0] + (hacia[0] - punto[0]) * distancia / largo,
        punto[1] + (hacia[1] - punto[1]) * distancia / largo,
    )


def dibujar_arco(figura, posiciones, origen, destino, estilo):
    """
    Dibuja una ruta: el trazo, la punta de flecha y su etiqueta.

    Devuelve el punto donde quedó la etiqueta (sirve para el texto emergente).
    """
    control = elegir_punto_de_control(posiciones, origen, destino)
    # El trazo empieza y termina en el borde de los círculos, no en su centro.
    inicio = acercar(posiciones[origen], control, RADIO_VERTICE)
    fin = acercar(posiciones[destino], control, RADIO_VERTICE)
    figura.add_shape(
        type="path",
        path=f"M {inicio[0]},{inicio[1]} Q {control[0]},{control[1]} {fin[0]},{fin[1]}",
        line={"color": estilo["color"], "width": estilo["ancho"], "dash": estilo["linea"]},
        layer="below",
    )
    # La punta es una anotación muy corta que termina exactamente en `fin`.
    cola = acercar(fin, control, 0.3)
    figura.add_annotation(
        x=fin[0], y=fin[1], ax=cola[0], ay=cola[1],
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.0,
        arrowwidth=min(max(estilo["ancho"], 2), 4), arrowcolor=estilo["color"], text="",
    )
    # Etiqueta sobre el trazo, con fondo blanco para que se lea encima de las líneas.
    lugar = punto_de_curva(inicio, control, fin, POSICION_ETIQUETA)
    texto = f"<b>{estilo['etiqueta']}</b>" if estilo["negrita"] else estilo["etiqueta"]
    color_etiqueta = COLOR_TEXTO_TENUE if estilo["linea"] == "dot" else COLOR_TEXTO
    figura.add_annotation(
        x=lugar[0], y=lugar[1], text=texto, showarrow=False,
        font={"size": 13, "color": color_etiqueta},
        bgcolor=COLOR_FONDO, bordercolor=estilo["color"], borderwidth=1, borderpad=2,
    )
    return lugar


def dibujar_vertice(figura, nombre, posicion, relleno, color_letra):
    """Dibuja un centro: un círculo con su nombre en el medio."""
    x, y = posicion
    figura.add_shape(
        type="circle",
        x0=x - RADIO_VERTICE, y0=y - RADIO_VERTICE,
        x1=x + RADIO_VERTICE, y1=y + RADIO_VERTICE,
        line={"color": COLOR_EXTREMO, "width": 2}, fillcolor=relleno, layer="above",
    )
    figura.add_annotation(
        x=x, y=y, text=f"<b>{nombre}</b>", showarrow=False,
        font={"size": 17, "color": color_letra},
    )


def agregar_rotulo(figura, posicion, texto):
    """Escribe un rótulo pequeño debajo de un centro (por ejemplo «Origen»)."""
    figura.add_annotation(
        x=posicion[0], y=posicion[1] - RADIO_VERTICE - 0.3, text=texto,
        showarrow=False, font={"size": 13, "color": COLOR_TEXTO},
    )


def agregar_linea_de_leyenda(figura, texto, color, linea="solid", ancho=4):
    """Agrega una línea de muestra a la leyenda (no dibuja nada en el grafo)."""
    figura.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines", name=texto,
        line={"color": color, "width": ancho, "dash": linea},
    ))


def agregar_punto_de_leyenda(figura, texto, color):
    """Agrega un círculo de muestra a la leyenda (color de relleno de un centro)."""
    figura.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers", name=texto,
        marker={"size": 14, "color": color, "line": {"color": COLOR_EXTREMO, "width": 1.5}},
    ))


def agregar_leyenda(figura, red, resultado, modo):
    """Explica en la leyenda los colores y etiquetas del modo elegido."""
    if resultado is None or modo == MODO_CAPACIDADES:
        agregar_linea_de_leyenda(figura, "Ruta activa (etiqueta: capacidad)", COLOR_ARCO, ancho=2)
    elif modo == MODO_FLUJO:
        agregar_linea_de_leyenda(figura, "Ruta con flujo (etiqueta: flujo/capacidad)", COLOR_FLUJO)
        agregar_linea_de_leyenda(figura, "Ruta saturada (flujo = capacidad)", COLOR_SATURADO, ancho=5)
        agregar_linea_de_leyenda(figura, "Ruta sin flujo", COLOR_ARCO_TENUE, ancho=2)
    else:
        agregar_linea_de_leyenda(figura, "Ruta del corte mínimo (de S a T)", COLOR_CORTE, "dash")
        agregar_punto_de_leyenda(figura, "Conjunto S (lado del origen)", COLOR_LADO_ORIGEN)
        agregar_punto_de_leyenda(figura, "Conjunto T (lado del destino)", COLOR_LADO_DESTINO)
        agregar_linea_de_leyenda(figura, "Otras rutas", COLOR_ARCO_TENUE, ancho=2)
    if any(not arco["activo"] for arco in red["arcos"]):
        agregar_linea_de_leyenda(figura, "Ruta desactivada", COLOR_DESACTIVADO, "dot", 2)


def agregar_textos_emergentes(figura, red, puntos_de_arcos, descripciones_de_arcos):
    """Puntos invisibles que muestran información al pasar el cursor."""
    posiciones = red["posiciones"]
    centros = red.get("centros", {})
    figura.add_trace(go.Scatter(
        x=[posiciones[vertice][0] for vertice in red["vertices"]],
        y=[posiciones[vertice][1] for vertice in red["vertices"]],
        mode="markers", marker={"size": 40, "opacity": 0},
        hovertext=[f"{vertice}: {centros.get(vertice, 'Centro logístico')}"
                   for vertice in red["vertices"]],
        hoverinfo="text", showlegend=False,
    ))
    figura.add_trace(go.Scatter(
        x=[punto[0] for punto in puntos_de_arcos],
        y=[punto[1] for punto in puntos_de_arcos],
        mode="markers", marker={"size": 26, "opacity": 0},
        hovertext=descripciones_de_arcos, hoverinfo="text", showlegend=False,
    ))


def elegir_relleno_de_vertice(red, resultado, modo, vertice):
    """Devuelve (color de relleno, color de la letra) de un centro."""
    if vertice in (red["origen"], red["destino"]):
        return COLOR_EXTREMO, "#ffffff"
    if resultado is not None and modo == MODO_CORTE:
        if vertice in resultado["lado_origen"]:
            return COLOR_LADO_ORIGEN, COLOR_TEXTO
        return COLOR_LADO_DESTINO, COLOR_TEXTO
    return COLOR_FONDO, COLOR_TEXTO


def crear_figura(red, resultado, modo, alto=580):
    """
    Construye la figura completa de la red.

    Entradas:
      - red: diccionario de la red (incluye "posiciones").
      - resultado: salida de analizar_red, o None para dibujar solo capacidades.
      - modo: uno de MODOS; indica qué se muestra sobre las rutas.
    Salida: figura de Plotly lista para mostrar.
    """
    posiciones = red["posiciones"]
    figura = go.Figure()

    puntos_de_arcos = []
    descripciones_de_arcos = []
    for arco in red["arcos"]:
        estilo = elegir_estilo_de_arco(arco, resultado, modo)
        lugar = dibujar_arco(figura, posiciones, arco["origen"], arco["destino"], estilo)
        puntos_de_arcos.append(lugar)
        descripciones_de_arcos.append(estilo["descripcion"])

    for vertice in red["vertices"]:
        relleno, color_letra = elegir_relleno_de_vertice(red, resultado, modo, vertice)
        dibujar_vertice(figura, vertice, posiciones[vertice], relleno, color_letra)
    agregar_rotulo(figura, posiciones[red["origen"]], "Origen")
    agregar_rotulo(figura, posiciones[red["destino"]], "Destino")

    agregar_textos_emergentes(figura, red, puntos_de_arcos, descripciones_de_arcos)
    agregar_leyenda(figura, red, resultado, modo)

    equis = [posicion[0] for posicion in posiciones.values()]
    yes = [posicion[1] for posicion in posiciones.values()]
    figura.update_layout(
        height=alto, margin={"l": 10, "r": 10, "t": 10, "b": 10},
        plot_bgcolor=COLOR_FONDO, paper_bgcolor=COLOR_FONDO,
        font={"family": "system-ui, 'Segoe UI', sans-serif", "color": COLOR_TEXTO},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.0, "x": 0,
                "font": {"size": 13}, "itemclick": False, "itemdoubleclick": False},
        hoverlabel={"font": {"size": 13}},
    )
    figura.update_xaxes(
        visible=False, fixedrange=True, range=[min(equis) - 0.9, max(equis) + 0.9],
    )
    figura.update_yaxes(
        visible=False, fixedrange=True, range=[min(yes) - 1.1, max(yes) + 0.8],
        scaleanchor="x", scaleratio=1,     # misma escala: los círculos no se deforman
    )
    return figura
