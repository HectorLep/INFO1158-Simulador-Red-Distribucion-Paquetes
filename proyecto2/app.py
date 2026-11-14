"""
Interfaz del Proyecto 2: simulador de una red de distribución de paquetes.

Ejecutar desde la carpeta raíz:   python -m streamlit run proyecto2/app.py

Este archivo solo se ocupa de la pantalla. Los cálculos están en:
  - grafo.py ........ la red y sus modificaciones válidas;
  - algoritmos.py ... flujo máximo (Edmonds–Karp) y corte mínimo;
  - verificacion.py . comprobaciones matemáticas y escenarios de comparación;
  - dibujo.py ....... la figura del grafo.

Cómo funciona Streamlit: cada vez que el usuario toca un control, este archivo
se ejecuta de nuevo de arriba abajo. Lo que debe sobrevivir entre ejecuciones
se guarda en st.session_state:
  - red ............ la red que el usuario está modificando;
  - resultado ...... el último análisis calculado;
  - red_calculada .. copia de la red sobre la que se hizo ese análisis.
Si red y red_calculada son distintas, hay cambios sin calcular y los
resultados anteriores se ocultan hasta pulsar «Calcular».
"""

# Streamlit y Plotly usan pandas por dentro (tablas y figuras), pero lo cargan
# "a medias" la primera vez que lo necesitan. Importarlo aquí garantiza que
# esté completamente cargado antes de dibujar; sin esta línea, pulsar un
# control mientras la aplicación arranca podía producir un error de carga.
import pandas  # noqa: F401
import streamlit as st

import dibujo
from algoritmos import (
    ESTRATEGIA_PROFUNDIDAD,
    analizar_red,
    calcular_flujo_maximo,
    calcular_valor_del_flujo,
)
from grafo import (
    CAPACIDAD_MAXIMA,
    CAPACIDAD_MINIMA,
    agregar_arco,
    arcos_desactivados,
    cambiar_capacidad,
    cambiar_extremos,
    capacidades_activas,
    cargar_red,
    copiar_red,
    desactivar_arco,
    reactivar_arco,
    texto_arco,
)
from verificacion import (
    ARCHIVO_CASO_MANUAL,
    ARCHIVO_RED_INICIAL,
    buscar_violaciones_de_capacidad,
    buscar_violaciones_de_conservacion,
    calcular_balances,
    comparar_escenarios,
    comprobar_condiciones_iniciales,
    texto_camino,
    todo_cumple,
    verificar_resultado,
)

st.set_page_config(
    page_title="Red de distribución de paquetes", page_icon="📦", layout="wide"
)
st.markdown(
    "<style>.block-container {padding-top: 2.4rem; padding-bottom: 3rem;}</style>",
    unsafe_allow_html=True,
)

UNIDAD = "paq./h"


# ---------------------------------------------------------------------------
# Estado de la aplicación
# ---------------------------------------------------------------------------

def calcular_resultados():
    """Ejecuta los algoritmos sobre la red actual y recuerda sobre qué red se calculó."""
    st.session_state.resultado = analizar_red(st.session_state.red)
    st.session_state.red_calculada = copiar_red(st.session_state.red)


def cargar_estado_inicial():
    """Carga la red inicial del archivo de datos y calcula sus resultados."""
    red = cargar_red(ARCHIVO_RED_INICIAL)
    st.session_state.red = red
    st.session_state.selector_origen = red["origen"]
    st.session_state.selector_destino = red["destino"]
    calcular_resultados()


def avisar(tipo, texto):
    """Guarda un mensaje ("exito" o "error") para mostrarlo en la próxima pantalla."""
    st.session_state.aviso = (tipo, texto)


# ---------------------------------------------------------------------------
# Acciones de los botones. Streamlit las ejecuta ANTES de redibujar la página.
# Si grafo.py rechaza la operación (ValueError), la red no cambia y se muestra
# el motivo.
# ---------------------------------------------------------------------------

RECORDATORIO = " Pulsa «Calcular» para actualizar los resultados."


def accion_calcular():
    calcular_resultados()
    avisar("exito", "Flujo máximo y corte mínimo calculados para la red que se muestra.")


def accion_restaurar():
    cargar_estado_inicial()
    avisar("exito", "Se restauró la red inicial y se recalcularon sus resultados.")


def accion_cambiar_extremos():
    red = st.session_state.red
    origen = st.session_state.selector_origen
    destino = st.session_state.selector_destino
    try:
        cambiar_extremos(red, origen, destino)
        avisar("exito", f"Origen: {origen}. Destino: {destino}." + RECORDATORIO)
    except ValueError as error:
        # Los selectores vuelven a mostrar los extremos que siguen vigentes.
        st.session_state.selector_origen = red["origen"]
        st.session_state.selector_destino = red["destino"]
        avisar("error", str(error))


def accion_desactivar():
    origen, destino = st.session_state.selector_desactivar
    try:
        desactivar_arco(st.session_state.red, origen, destino)
        avisar("exito", f"Ruta {texto_arco(origen, destino)} desactivada." + RECORDATORIO)
    except ValueError as error:
        avisar("error", str(error))


def accion_reactivar():
    origen, destino = st.session_state.selector_reactivar
    try:
        reactivar_arco(st.session_state.red, origen, destino)
        avisar("exito", f"Ruta {texto_arco(origen, destino)} reactivada." + RECORDATORIO)
    except ValueError as error:
        avisar("error", str(error))


def accion_cambiar_capacidad():
    origen, destino = st.session_state.selector_capacidad
    capacidad = st.session_state.entrada_capacidad
    try:
        cambiar_capacidad(st.session_state.red, origen, destino, capacidad)
        avisar("exito", f"La ruta {texto_arco(origen, destino)} ahora admite {capacidad} "
                        f"{UNIDAD}." + RECORDATORIO)
    except ValueError as error:
        avisar("error", "No se cambió la capacidad. " + str(error))


def accion_agregar():
    origen = st.session_state.selector_nuevo_origen
    destino = st.session_state.selector_nuevo_destino
    capacidad = st.session_state.entrada_nueva_capacidad
    try:
        agregar_arco(st.session_state.red, origen, destino, capacidad)
        avisar("exito", f"Ruta {texto_arco(origen, destino)} agregada con capacidad "
                        f"{capacidad} {UNIDAD}." + RECORDATORIO)
    except ValueError as error:
        avisar("error", "No se agregó la conexión. " + str(error))


def mostrar_tabla(filas):
    """
    Muestra una lista de diccionarios como tabla, con la altura justa para que
    se vean TODAS las filas sin barra de desplazamiento (35 px por fila).
    """
    st.dataframe(filas, hide_index=True, height=35 * (len(filas) + 1) + 3)


def texto_de_par(arco):
    """Convierte el par (origen, destino) en 'origen → destino' para los selectores."""
    return texto_arco(arco[0], arco[1])


# ---------------------------------------------------------------------------
# Panel lateral: controles
# ---------------------------------------------------------------------------

def mostrar_panel_lateral(red):
    capacidades = capacidades_activas(red)
    activas = list(capacidades)

    def texto_con_capacidad(arco):
        return f"{texto_de_par(arco)}   (capacidad {capacidades[arco]})"

    with st.sidebar:
        st.header("Controles")
        st.button(
            "▶ Calcular / Recalcular", type="primary", width="stretch",
            on_click=accion_calcular, key="boton_calcular",
            help="Ejecuta Edmonds–Karp y halla el corte mínimo sobre la red actual.",
        )
        st.button(
            "↺ Restaurar red inicial", width="stretch",
            on_click=accion_restaurar, key="boton_restaurar",
            help="Descarta todos los cambios y vuelve a la configuración inicial.",
        )
        st.caption("Después de cada cambio, pulsa «Calcular / Recalcular».")

        with st.expander("Origen y destino", expanded=True):
            columna_origen, columna_destino = st.columns(2)
            columna_origen.selectbox("Origen (s)", red["vertices"], key="selector_origen")
            columna_destino.selectbox("Destino (t)", red["vertices"], key="selector_destino")
            st.button("Aplicar origen y destino", width="stretch",
                      on_click=accion_cambiar_extremos, key="boton_extremos")
            st.caption("Deben ser dos centros distintos.")

        with st.expander("Desactivar o reactivar una ruta", expanded=True):
            if activas:
                st.selectbox("Ruta activa", activas, format_func=texto_con_capacidad,
                             key="selector_desactivar")
                st.button("Desactivar ruta", width="stretch",
                          on_click=accion_desactivar, key="boton_desactivar")
            desactivadas = arcos_desactivados(red)
            if desactivadas:
                st.selectbox("Ruta desactivada", desactivadas, format_func=texto_de_par,
                             key="selector_reactivar")
                st.button("Reactivar ruta", width="stretch",
                          on_click=accion_reactivar, key="boton_reactivar")
            else:
                st.caption("No hay rutas desactivadas. Una ruta desactivada no transporta "
                           "paquetes, pero no se borra.")

        with st.expander("Modificar una capacidad", expanded=True):
            if activas:
                st.selectbox("Ruta", activas, format_func=texto_con_capacidad,
                             key="selector_capacidad")
                st.number_input(f"Nueva capacidad ({UNIDAD})", min_value=CAPACIDAD_MINIMA,
                                max_value=CAPACIDAD_MAXIMA, value=10, step=1,
                                key="entrada_capacidad")
                st.button("Cambiar capacidad", width="stretch",
                          on_click=accion_cambiar_capacidad, key="boton_capacidad")
            st.caption("Entero entre 1 y 12 paquetes por hora.")

        with st.expander("Agregar una conexión", expanded=True):
            columna_desde, columna_hacia = st.columns(2)
            columna_desde.selectbox("Desde", red["vertices"], key="selector_nuevo_origen")
            columna_hacia.selectbox("Hacia", red["vertices"], index=1,
                                    key="selector_nuevo_destino")
            st.number_input(f"Capacidad ({UNIDAD})", min_value=CAPACIDAD_MINIMA,
                            max_value=CAPACIDAD_MAXIMA, value=5, step=1,
                            key="entrada_nueva_capacidad")
            st.button("Agregar conexión", width="stretch",
                      on_click=accion_agregar, key="boton_agregar")
            st.caption("No se admiten lazos, rutas repetidas ni recíprocas.")


# ---------------------------------------------------------------------------
# Zona superior: título, avisos e indicadores
# ---------------------------------------------------------------------------

def mostrar_encabezado():
    st.title("Simulador de una red de distribución de paquetes")
    st.caption(
        "Proyecto 2 · Teoría de Grafos (INFO1158). La red es un grafo dirigido: cada "
        "vértice es un centro logístico y cada flecha, una ruta con una capacidad máxima "
        "en paquetes por hora. Se calcula cuántos paquetes por hora pueden llegar como "
        "máximo del origen al destino (flujo máximo) y qué rutas limitan ese valor "
        "(corte mínimo)."
    )


def mostrar_aviso():
    """Muestra una sola vez el mensaje dejado por la última acción."""
    if "aviso" in st.session_state:
        tipo, texto = st.session_state.aviso
        if tipo == "exito":
            st.success(texto)
        else:
            st.error(texto)
        del st.session_state.aviso


def mostrar_indicadores(red, resultado):
    """Cuatro indicadores; `resultado` es None cuando hay cambios sin calcular."""
    columnas = st.columns(4)
    titulos = [
        f"Flujo máximo {red['origen']} → {red['destino']}", "Capacidad del corte mínimo",
        "Caminos aumentantes", "Comprobaciones",
    ]
    if resultado is None:
        for columna, titulo in zip(columnas, titulos):
            columna.metric(titulo, "—", border=True)
        return

    comprobaciones = verificar_resultado(red, resultado)
    cumplidas = sum(1 for comprobacion in comprobaciones if comprobacion["cumple"])
    marca = "✔" if todo_cumple(comprobaciones) else "✖"
    columnas[0].metric(titulos[0], f"{resultado['flujo_maximo']} {UNIDAD}", border=True)
    columnas[1].metric(titulos[1], f"{resultado['capacidad_corte']} {UNIDAD}", border=True)
    columnas[2].metric(titulos[2], len(resultado["pasos"]), border=True)
    columnas[3].metric(titulos[3], f"{marca} {cumplidas} de {len(comprobaciones)}", border=True)


# ---------------------------------------------------------------------------
# Zona principal: el grafo
# ---------------------------------------------------------------------------

def texto_conjunto(elementos):
    """Escribe una lista como conjunto matemático: {a, b, c} o ∅."""
    if not elementos:
        return "∅"
    return "{" + ", ".join(elementos) + "}"


def texto_corte(resultado):
    """Escribe las rutas del corte con su capacidad: {F → T (2), H → T (8)}."""
    capacidades = resultado["capacidades"]
    return texto_conjunto(
        [f"{texto_arco(u, v)} ({capacidades[(u, v)]})" for u, v in resultado["corte"]]
    )


def texto_suma_del_corte(resultado):
    """Escribe la suma de capacidades del corte: '3 + 2 + 8 + 5 = 18'."""
    if not resultado["corte"]:
        return "0"
    capacidades = resultado["capacidades"]
    sumandos = " + ".join(str(capacidades[arco]) for arco in resultado["corte"])
    return f"{sumandos} = {resultado['capacidad_corte']}"


def describir_modo(resultado, modo):
    """Frase corta que explica lo que se ve en el grafo."""
    if modo == dibujo.MODO_FLUJO:
        return (f"Cada etiqueta es **flujo/capacidad**. El flujo máximo es "
                f"**{resultado['flujo_maximo']} paquetes por hora**; el grosor de la flecha "
                "crece con el flujo y el azul oscuro marca las rutas saturadas.")
    if modo == dibujo.MODO_CORTE:
        if not resultado["corte"]:
            return ("No hay ninguna ruta de S a T: el destino no es alcanzable y el corte "
                    "mínimo es vacío (capacidad 0).")
        return (f"En rojo discontinuo, las rutas del corte mínimo: van del conjunto **S** "
                f"(celeste) al conjunto **T** (naranja claro). Su capacidad total es "
                f"**{texto_suma_del_corte(resultado)} paquetes por hora**.")
    return "Cada etiqueta es la **capacidad** de la ruta, en paquetes por hora."


def mostrar_grafo(red, resultado):
    if resultado is None:
        st.warning(
            "La red cambió y los resultados anteriores ya no corresponden. "
            "Pulsa **Calcular / Recalcular** para ejecutar el algoritmo sobre esta red."
        )
        st.button("▶ Calcular ahora", type="primary", on_click=accion_calcular,
                  key="boton_calcular_aviso")
        with st.container(border=True):
            st.plotly_chart(dibujo.crear_figura(red, None, dibujo.MODO_CAPACIDADES),
                            theme=None, config={"displayModeBar": False},
                            key="grafo_principal")
        return

    modo = st.radio("Mostrar en el grafo", dibujo.MODOS, index=1, horizontal=True, key="modo")
    with st.container(border=True):
        st.plotly_chart(dibujo.crear_figura(red, resultado, modo),
                        theme=None, config={"displayModeBar": False}, key="grafo_principal")
    st.markdown(describir_modo(resultado, modo))


# ---------------------------------------------------------------------------
# Zona inferior: pestañas de detalle
# ---------------------------------------------------------------------------

def tabla_de_flujos(red, resultado):
    """Una fila por ruta: flujo, capacidad, capacidad libre y estado."""
    filas = []
    for arco in red["arcos"]:
        par = (arco["origen"], arco["destino"])
        if not arco["activo"]:
            filas.append({"Ruta": texto_de_par(par), "Flujo / capacidad": "—",
                          "Flujo": None, "Capacidad": arco["capacidad"],
                          "Capacidad libre": None, "Estado": "Desactivada"})
            continue
        flujo = resultado["flujo"][par]
        if flujo == arco["capacidad"]:
            estado = "Saturada"
        elif flujo == 0:
            estado = "Sin uso"
        else:
            estado = "Con capacidad libre"
        if par in resultado["corte"]:
            estado += " · en el corte mínimo"
        filas.append({"Ruta": texto_de_par(par),
                      "Flujo / capacidad": f"{flujo}/{arco['capacidad']}",
                      "Flujo": flujo, "Capacidad": arco["capacidad"],
                      "Capacidad libre": arco["capacidad"] - flujo, "Estado": estado})
    return filas


def mostrar_resultados(red, resultado):
    columna_flujo, columna_corte = st.columns([3, 2])

    with columna_flujo:
        st.subheader("Flujo por ruta")
        st.markdown(f"Flujo máximo: **{resultado['flujo_maximo']} paquetes por hora** de "
                    f"{red['origen']} a {red['destino']}.")
        mostrar_tabla(tabla_de_flujos(red, resultado))
        st.caption("x(u, v)/c(u, v): paquetes por hora que se envían por la ruta, sobre los "
                   "que admite. La distribución del flujo puede no ser única; el valor "
                   "máximo sí lo es.")

    with columna_corte:
        st.subheader("Corte mínimo")
        st.markdown(f"- **S** = {texto_conjunto(resultado['lado_origen'])}\n"
                    f"- **T** = {texto_conjunto(resultado['lado_destino'])}\n"
                    f"- Rutas de S a T: {texto_corte(resultado)}\n"
                    f"- Capacidad del corte: c(S, T) = **{texto_suma_del_corte(resultado)}**")
        st.success(f"Flujo máximo = {resultado['flujo_maximo']} = "
                   f"{resultado['capacidad_corte']} = capacidad del corte mínimo")
        st.caption(
            "S son los centros alcanzables desde el origen en la red residual final. Las "
            "rutas del corte están saturadas: son el cuello de botella. Para transportar "
            "más hay que ampliar la capacidad a través del corte; puede no bastar si existe "
            "otro corte con la misma capacidad."
        )


def tabla_de_comprobaciones(comprobaciones):
    filas = []
    for comprobacion in comprobaciones:
        filas.append({
            "Comprobación": comprobacion["comprobacion"],
            "Resultado": "✔ Cumple" if comprobacion["cumple"] else "✖ No cumple",
            "Detalle": comprobacion["detalle"],
        })
    return filas


def tabla_de_balances(red, resultado):
    """Una fila por centro: cuánto flujo entra, cuánto sale y si se conserva."""
    balances = calcular_balances(red["vertices"], resultado["flujo"])
    filas = []
    for vertice in red["vertices"]:
        entra = balances[vertice]["entra"]
        sale = balances[vertice]["sale"]
        if vertice == red["origen"]:
            papel, observacion = "Origen", f"emite {sale - entra}"
        elif vertice == red["destino"]:
            papel, observacion = "Destino", f"recibe {entra - sale}"
        else:
            papel = "Intermedio"
            observacion = "✔ se conserva" if entra == sale else "✖ no se conserva"
        filas.append({"Centro": vertice, "Papel": papel, "Entra": entra, "Sale": sale,
                      "Observación": observacion})
    return filas


def mostrar_verificacion(red, resultado):
    st.markdown("Comprobaciones hechas por código sobre el flujo que se muestra "
                "(archivo `verificacion.py`).")
    comprobaciones = verificar_resultado(red, resultado)
    mostrar_tabla(tabla_de_comprobaciones(comprobaciones))
    if todo_cumple(comprobaciones):
        st.success("Todas las comprobaciones se cumplen.")
    else:
        st.error("Alguna comprobación no se cumple: el resultado no es confiable.")
    st.markdown("**Conservación del flujo, centro por centro** (paquetes por hora)")
    mostrar_tabla(tabla_de_balances(red, resultado))


def tabla_de_pasos(pasos):
    filas = []
    for numero, paso in enumerate(pasos, start=1):
        inversos = ", ".join(
            f"{texto_arco(u, v)} (devuelve flujo de {texto_arco(v, u)})"
            for u, v in paso["arcos_inversos"]
        )
        filas.append({
            "Paso": numero,
            "Camino aumentante": texto_camino(paso["camino"]),
            "Cuello de botella": paso["cuello_de_botella"],
            "Flujo acumulado": paso["flujo_acumulado"],
            "Arcos inversos usados": inversos or "—",
        })
    return filas


def mostrar_algoritmo(red, resultado):
    st.markdown(
        "**Edmonds–Karp** (Ford–Fulkerson con búsqueda en anchura). En cada paso se "
        "construye la **red residual**, se busca con BFS el camino aumentante con menos "
        "arcos, se calcula su **cuello de botella** (la menor capacidad residual del camino) "
        "y se envía esa cantidad. Cuando no queda ningún camino, el flujo es máximo."
    )
    mostrar_tabla(tabla_de_pasos(resultado["pasos"]))
    if not resultado["pasos"]:
        st.info("No existe ningún camino del origen al destino: el flujo máximo es 0.")
    st.caption(
        "Un arco inverso no es una ruta: significa retirar paquetes ya asignados a una "
        "ruta para redirigirlos. Si esta red no usa ninguno, mira el ejemplo de la guía de "
        "estudio, donde sí hace falta."
    )
    with st.expander("Comparación con Ford–Fulkerson usando búsqueda en profundidad (DFS)"):
        flujo_dfs, pasos_dfs = calcular_flujo_maximo(
            red["vertices"], capacidades_activas(red), red["origen"], red["destino"],
            ESTRATEGIA_PROFUNDIDAD,
        )
        st.markdown(
            f"Con DFS se obtiene el mismo valor máximo, "
            f"**{calcular_valor_del_flujo(flujo_dfs, red['origen'])} paquetes por hora**, "
            f"usando **{len(pasos_dfs)}** caminos aumentantes (BFS usó "
            f"**{len(resultado['pasos'])}**). Los caminos de DFS suelen ser más largos; la "
            "ventaja de BFS es que su número de pasos está acotado sin depender de las "
            "capacidades."
        )
        mostrar_tabla(tabla_de_pasos(pasos_dfs))


def texto_cambio(antes, despues):
    """Describe cómo cambia una cantidad respecto de la red inicial."""
    if antes == despues:
        return f"se mantiene en {antes}"
    return f"pasa de {antes} a {despues}"


def mostrar_escenarios():
    st.markdown(
        "Tres configuraciones con el mismo origen **O** y destino **T**. Cada modificación "
        "se aplica sobre una copia de la red inicial (no se acumulan) y no depende de los "
        "cambios hechos en el panel lateral."
    )
    red_original = cargar_red(ARCHIVO_RED_INICIAL)
    comparacion = comparar_escenarios(red_original)
    filas = []
    for escenario in comparacion:
        resultado = escenario["resultado"]
        filas.append({
            "Escenario": escenario["nombre"],
            "Modificación": escenario["cambio"],
            "Flujo máximo": resultado["flujo_maximo"],
            "Capacidad del corte": resultado["capacidad_corte"],
            "Verificado": "✔" if todo_cumple(escenario["comprobaciones"]) else "✖",
            "Corte mínimo": texto_corte(resultado),
            "S": texto_conjunto(resultado["lado_origen"]),
            "T": texto_conjunto(resultado["lado_destino"]),
        })
    mostrar_tabla(filas)

    inicial, sin_ruta, con_capacidad = [e["resultado"] for e in comparacion]
    capacidades = capacidades_activas(red_original)
    salida_del_origen = sum(c for (u, v), c in capacidades.items() if u == "O")
    st.markdown(
        "**Interpretación**\n\n"
        f"- **Red inicial.** Del origen pueden salir hasta {salida_del_origen} paquetes por "
        f"hora, pero solo llegan **{inicial['flujo_maximo']}**: el límite lo impone el "
        f"corte {texto_corte(inicial)}, cuyas rutas quedan saturadas.\n"
        f"- **Desactivar H → T.** El flujo máximo "
        f"{texto_cambio(inicial['flujo_maximo'], sin_ruta['flujo_maximo'])}. Se pierden "
        f"exactamente los {capacidades[('H', 'T')]} paquetes por hora de esa ruta porque "
        "pertenecía al corte mínimo y las demás rutas hacia T ya estaban llenas. El centro "
        "H queda sin salida y deja de recibir paquetes (D → H y E → H llevan "
        f"{sin_ruta['flujo'][('D', 'H')]} y {sin_ruta['flujo'][('E', 'H')]}).\n"
        f"- **Aumentar I → T de 5 a 10.** El flujo máximo "
        f"{texto_cambio(inicial['flujo_maximo'], con_capacidad['flujo_maximo'])}: sube "
        f"{con_capacidad['flujo_maximo'] - inicial['flujo_maximo']}, no 5. El cuello de "
        f"botella se traslada al corte {texto_corte(con_capacidad)} (las rutas que salen "
        f"del origen), y a I → T le sobra capacidad: lleva "
        f"{con_capacidad['flujo'][('I', 'T')]}/10."
    )

    st.markdown("**Ver un escenario**")
    columna_escenario, columna_modo = st.columns([1, 2])
    nombres = [f"{e['nombre']} ({e['cambio']})" for e in comparacion]
    elegido = columna_escenario.selectbox("Escenario", nombres, key="escenario_elegido")
    modo = columna_modo.radio("Mostrar", dibujo.MODOS, index=1, horizontal=True,
                              key="modo_escenario")
    escenario = comparacion[nombres.index(elegido)]
    with st.container(border=True):
        st.plotly_chart(
            dibujo.crear_figura(escenario["red"], escenario["resultado"], modo, alto=500),
            theme=None, config={"displayModeBar": False}, key="grafo_escenario",
        )
    mostrar_tabla(tabla_de_comprobaciones(escenario["comprobaciones"]))


def mostrar_modelo(red):
    vertices = red["vertices"]
    st.markdown(
        "La red se modela como un **grafo dirigido G = (V, E)** con una **función de "
        "capacidad c : E → {1, 2, …, 12}**.\n\n"
        "- Cada **vértice** de V es un centro logístico.\n"
        "- Cada **arco** (u, v) de E es una ruta de transporte de u hacia v.\n"
        "- **c(u, v)** es el máximo de paquetes por hora que admite la ruta.\n"
        "- Un **flujo** x asigna a cada ruta cuántos paquetes por hora transporta, con "
        "0 ≤ x(u, v) ≤ c(u, v) y conservación en los centros intermedios.\n"
        f"- Origen s = **{red['origen']}**, destino t = **{red['destino']}**."
    )
    st.markdown(f"**V** = {texto_conjunto(vertices)}, |V| = {len(vertices)}")
    st.markdown(f"**E** tiene {len(red['arcos'])} arcos "
                f"({len(capacidades_activas(red))} activos). Valores de c:")

    columna_arcos, columna_derecha = st.columns(2)
    with columna_arcos:
        st.markdown("**Arcos y capacidades**")
        filas_de_arcos = []
        for arco in red["arcos"]:
            filas_de_arcos.append({
                "Arco (u, v)": texto_arco(arco["origen"], arco["destino"]),
                "c(u, v)": arco["capacidad"],
                "Estado": "Activo" if arco["activo"] else "Desactivado",
            })
        mostrar_tabla(filas_de_arcos)
    with columna_derecha:
        st.markdown("**Significado de los vértices**")
        centros = red.get("centros", {})
        filas_de_vertices = []
        for vertice in vertices:
            filas_de_vertices.append(
                {"Vértice": vertice, "Centro que representa": centros.get(vertice, "")}
            )
        mostrar_tabla(filas_de_vertices)
    st.markdown("**Condiciones de la configuración inicial**")
    condiciones = comprobar_condiciones_iniciales(cargar_red(ARCHIVO_RED_INICIAL))
    mostrar_tabla(tabla_de_comprobaciones(condiciones))
    st.caption("Los intervalos de vértices y arcos se exigen solo a la red inicial; las "
               "modificaciones pueden cambiar la cantidad de arcos. Los lazos, los arcos "
               "repetidos, los recíprocos y las capacidades fuera de 1–12 se rechazan siempre.")


# Flujo factible encontrado A MANO para el caso de 5 vértices (ver GUIA_DE_ESTUDIO.md).
FLUJO_MANUAL = {
    ("O", "A"): 5, ("O", "B"): 3, ("A", "C"): 2, ("A", "T"): 3, ("B", "C"): 3, ("C", "T"): 5,
}
CORTE_MANUAL = [("A", "T"), ("C", "T")]


def mostrar_caso_manual():
    red = cargar_red(ARCHIVO_CASO_MANUAL)
    resultado = analizar_red(red)
    capacidades = resultado["capacidades"]
    st.markdown("Caso independiente de 5 vértices que se resuelve a mano y se contrasta "
                "con el código.")
    columna_figura, columna_texto = st.columns([3, 2])
    with columna_figura:
        modo = st.radio("Mostrar", dibujo.MODOS, index=1, horizontal=True, key="modo_manual")
        with st.container(border=True):
            st.plotly_chart(dibujo.crear_figura(red, resultado, modo, alto=400),
                            theme=None, config={"displayModeBar": False}, key="grafo_manual")
    with columna_texto:
        st.markdown(
            "**Resolución manual**\n\n"
            "1. *Un flujo factible.* Enviar 3 por O → A → T, 2 por O → A → C → T y 3 por "
            "O → B → C → T. Resulta O→A = 5, O→B = 3, A→C = 2, A→T = 3, B→C = 3, C→T = 5. "
            "Ninguna ruta supera su capacidad y en A, B y C entra lo mismo que sale. "
            "Valor: 5 + 3 = **8**.\n"
            "2. *Un corte.* S = {O, A, B, C}, T = {T}. Las rutas de S a T son A → T (3) y "
            "C → T (5): capacidad 3 + 5 = **8**.\n"
            "3. *Optimalidad.* Todo paquete que llega a T cruza de S a T, así que ningún "
            "flujo puede valer más que la capacidad de un corte. Hay un flujo de valor 8 y "
            "un corte de capacidad 8: el flujo es máximo y el corte es mínimo."
        )

    st.markdown("**Contraste con el código, ruta por ruta**")
    filas = []
    for arco, capacidad in capacidades.items():
        filas.append({
            "Ruta": texto_de_par(arco), "Capacidad": capacidad,
            "Flujo manual": FLUJO_MANUAL[arco], "Flujo del código": resultado["flujo"][arco],
            "¿Igual?": "Sí" if FLUJO_MANUAL[arco] == resultado["flujo"][arco] else "No",
        })
    mostrar_tabla(filas)

    manual_factible = (
        buscar_violaciones_de_capacidad(capacidades, FLUJO_MANUAL) == []
        and buscar_violaciones_de_conservacion(
            red["vertices"], FLUJO_MANUAL, red["origen"], red["destino"]) == []
    )
    valor_manual = calcular_valor_del_flujo(FLUJO_MANUAL, red["origen"])
    capacidad_corte_manual = sum(capacidades[arco] for arco in CORTE_MANUAL)
    mostrar_tabla([
        {"Concepto": "Flujo factible (capacidad y conservación)",
         "Manual": "✔" if manual_factible else "✖", "Código": "✔"
            if todo_cumple(verificar_resultado(red, resultado)) else "✖"},
        {"Concepto": "Valor del flujo (paquetes por hora)",
         "Manual": str(valor_manual), "Código": str(resultado["flujo_maximo"])},
        {"Concepto": "Corte hallado",
         "Manual": "{A → T (3), C → T (5)}", "Código": texto_corte(resultado)},
        {"Concepto": "Capacidad del corte",
         "Manual": str(capacidad_corte_manual), "Código": str(resultado["capacidad_corte"])},
    ])
    st.info(
        "El valor máximo (8) y el corte coinciden. La distribución por ruta es distinta: a "
        "mano se envían 5 por O → A y 3 por O → B; el código, que elige primero los caminos "
        "más cortos, envía 6 y 2. Ambas son correctas: el valor del flujo máximo es único, "
        "pero puede alcanzarse con repartos diferentes."
    )


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

if "red" not in st.session_state:
    cargar_estado_inicial()

red = st.session_state.red
mostrar_panel_lateral(red)
mostrar_encabezado()
mostrar_aviso()

# Los resultados solo se muestran si corresponden exactamente a la red actual.
if red == st.session_state.red_calculada:
    resultado = st.session_state.resultado
else:
    resultado = None

mostrar_indicadores(red, resultado)
mostrar_grafo(red, resultado)

(pestana_resultados, pestana_verificacion, pestana_algoritmo, pestana_escenarios,
 pestana_modelo, pestana_manual) = st.tabs([
    "Resultados", "Verificación", "Algoritmo paso a paso", "Escenarios",
    "Modelo matemático", "Caso manual",
])
with pestana_resultados:
    if resultado is None:
        st.info("Resultados pendientes: pulsa «Calcular / Recalcular».")
    else:
        mostrar_resultados(red, resultado)
with pestana_verificacion:
    if resultado is None:
        st.info("Verificación pendiente: pulsa «Calcular / Recalcular».")
    else:
        mostrar_verificacion(red, resultado)
with pestana_algoritmo:
    if resultado is None:
        st.info("Pasos pendientes: pulsa «Calcular / Recalcular».")
    else:
        mostrar_algoritmo(red, resultado)
with pestana_escenarios:
    mostrar_escenarios()
with pestana_modelo:
    mostrar_modelo(red)
with pestana_manual:
    mostrar_caso_manual()
