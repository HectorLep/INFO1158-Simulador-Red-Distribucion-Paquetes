"""Pruebas de los algoritmos: red residual, flujo máximo y corte mínimo (Proyecto 2)."""

import sys
import unittest
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import algoritmos  # noqa: E402
import verificacion  # noqa: E402

# Caso manual de 5 vértices.
VERTICES_MANUAL = ["O", "A", "B", "C", "T"]
CAPACIDADES_MANUAL = {
    ("O", "A"): 6, ("O", "B"): 4, ("A", "C"): 3, ("A", "T"): 3, ("B", "C"): 4, ("C", "T"): 5,
}

# Red donde Edmonds–Karp NECESITA un arco inverso: el primer camino (el más
# corto) envía 5 por A → B, y después conviene devolver 3 de esos paquetes
# para aprovechar las rutas A → C → D → T y O → E → F → B.
VERTICES_INVERSO = ["O", "A", "B", "C", "D", "E", "F", "T"]
CAPACIDADES_INVERSO = {
    ("O", "A"): 5, ("A", "B"): 5, ("B", "T"): 5,
    ("A", "C"): 3, ("C", "D"): 3, ("D", "T"): 3,
    ("O", "E"): 4, ("E", "F"): 4, ("F", "B"): 4,
}


def corte_minimo_por_fuerza_bruta(vertices, capacidades, origen, destino):
    """
    Prueba TODAS las particiones (S, T) con el origen en S y el destino en T y
    devuelve la menor capacidad. No usa el algoritmo de flujo: sirve como
    comprobación independiente del teorema flujo máximo = corte mínimo.
    """
    intermedios = [v for v in vertices if v not in (origen, destino)]
    mejor = None
    for cantidad in range(len(intermedios) + 1):
        for elegidos in combinations(intermedios, cantidad):
            lado_origen = {origen} | set(elegidos)
            capacidad = 0
            for (u, v), valor in capacidades.items():
                if u in lado_origen and v not in lado_origen:
                    capacidad += valor
            if mejor is None or capacidad < mejor:
                mejor = capacidad
    return mejor


def comprobar_flujo_factible(prueba, vertices, capacidades, flujo, origen, destino):
    """Afirma capacidad y conservación sobre un flujo cualquiera."""
    prueba.assertEqual(verificacion.buscar_violaciones_de_capacidad(capacidades, flujo), [])
    prueba.assertEqual(
        verificacion.buscar_violaciones_de_conservacion(vertices, flujo, origen, destino), []
    )


class PruebasRedResidual(unittest.TestCase):
    def test_sin_flujo_solo_hay_arcos_directos(self):
        capacidades = {("O", "A"): 6, ("A", "T"): 3}
        flujo = {("O", "A"): 0, ("A", "T"): 0}
        residual = algoritmos.construir_red_residual(["O", "A", "T"], capacidades, flujo)
        self.assertEqual(residual, {"O": {"A": 6}, "A": {"T": 3}, "T": {}})

    def test_con_flujo_parcial_hay_arco_directo_e_inverso(self):
        capacidades = {("O", "A"): 6, ("A", "T"): 3}
        flujo = {("O", "A"): 2, ("A", "T"): 2}
        residual = algoritmos.construir_red_residual(["O", "A", "T"], capacidades, flujo)
        self.assertEqual(residual["O"], {"A": 4})            # caben 6 − 2 = 4 más
        self.assertEqual(residual["A"], {"O": 2, "T": 1})    # inverso: se pueden retirar 2
        self.assertEqual(residual["T"], {"A": 2})

    def test_ruta_saturada_solo_deja_el_arco_inverso(self):
        capacidades = {("O", "A"): 6, ("A", "T"): 3}
        flujo = {("O", "A"): 3, ("A", "T"): 3}
        residual = algoritmos.construir_red_residual(["O", "A", "T"], capacidades, flujo)
        self.assertNotIn("T", residual["A"])                 # A → T lleno: sin arco directo
        self.assertEqual(residual["T"], {"A": 3})

    def test_cuello_de_botella_es_la_menor_capacidad_residual(self):
        residual = {"O": {"A": 6}, "A": {"C": 3}, "C": {"T": 5}, "T": {}}
        self.assertEqual(algoritmos.calcular_cuello_de_botella(residual, ["O", "A", "C", "T"]), 3)

    def test_aumentar_flujo_por_arcos_directos_e_inversos(self):
        flujo = {("O", "A"): 5, ("A", "B"): 5, ("B", "T"): 5, ("O", "B"): 0, ("A", "T"): 0}
        # El camino O → B → A → T usa el arco inverso B → A.
        algoritmos.aumentar_flujo(flujo, ["O", "B", "A", "T"], 2)
        self.assertEqual(flujo[("O", "B")], 2)               # directo: aumenta
        self.assertEqual(flujo[("A", "B")], 3)               # inverso: disminuye 5 → 3
        self.assertEqual(flujo[("A", "T")], 2)
        self.assertEqual(flujo[("B", "T")], 5)               # no estaba en el camino


class PruebasBusquedaDeCaminos(unittest.TestCase):
    def test_bfs_encuentra_el_camino_con_menos_arcos(self):
        residual = {"O": {"A": 1, "C": 1}, "A": {"B": 1}, "B": {"T": 1}, "C": {"T": 1}, "T": {}}
        self.assertEqual(algoritmos.buscar_camino_en_anchura(residual, "O", "T"), ["O", "C", "T"])
        # DFS encuentra un camino válido, pero más largo.
        self.assertEqual(
            algoritmos.buscar_camino_en_profundidad(residual, "O", "T"), ["O", "A", "B", "T"]
        )

    def test_sin_camino_devuelve_none(self):
        residual = {"O": {"A": 1}, "A": {}, "T": {}}
        self.assertIsNone(algoritmos.buscar_camino_en_anchura(residual, "O", "T"))
        self.assertIsNone(algoritmos.buscar_camino_en_profundidad(residual, "O", "T"))

    def test_recorrido_devuelve_los_alcanzables_y_sus_padres(self):
        residual = {"O": {"A": 1}, "A": {"B": 2}, "B": {}, "T": {"B": 1}}
        padre = algoritmos.recorrer_en_anchura(residual, "O")
        self.assertEqual(padre, {"O": None, "A": "O", "B": "A"})
        self.assertEqual(algoritmos.reconstruir_camino(padre, "B"), ["O", "A", "B"])


class PruebasFlujoMaximo(unittest.TestCase):
    def test_caso_manual_vale_8(self):
        flujo, pasos = algoritmos.calcular_flujo_maximo(
            VERTICES_MANUAL, CAPACIDADES_MANUAL, "O", "T"
        )
        self.assertEqual(algoritmos.calcular_valor_del_flujo(flujo, "O"), 8)
        self.assertEqual(flujo, {
            ("O", "A"): 6, ("O", "B"): 2, ("A", "C"): 3, ("A", "T"): 3, ("B", "C"): 2, ("C", "T"): 5,
        })
        self.assertEqual([paso["camino"] for paso in pasos],
                         [["O", "A", "T"], ["O", "A", "C", "T"], ["O", "B", "C", "T"]])
        self.assertEqual([paso["cuello_de_botella"] for paso in pasos], [3, 3, 2])
        self.assertEqual([paso["flujo_acumulado"] for paso in pasos], [3, 6, 8])
        comprobar_flujo_factible(self, VERTICES_MANUAL, CAPACIDADES_MANUAL, flujo, "O", "T")

    def test_el_arco_inverso_redirige_flujo_ya_enviado(self):
        flujo, pasos = algoritmos.calcular_flujo_maximo(
            VERTICES_INVERSO, CAPACIDADES_INVERSO, "O", "T"
        )
        self.assertEqual(algoritmos.calcular_valor_del_flujo(flujo, "O"), 8)
        # Paso 1: el camino más corto llena A → B con 5.
        self.assertEqual(pasos[0]["camino"], ["O", "A", "B", "T"])
        self.assertEqual(pasos[0]["cuello_de_botella"], 5)
        self.assertEqual(pasos[0]["arcos_inversos"], [])
        # Paso 2: se usa el arco inverso B → A (no es una ruta original).
        self.assertEqual(pasos[1]["camino"], ["O", "E", "F", "B", "A", "C", "D", "T"])
        self.assertEqual(pasos[1]["arcos_inversos"], [("B", "A")])
        self.assertNotIn(("B", "A"), CAPACIDADES_INVERSO)
        self.assertEqual(pasos[1]["cuello_de_botella"], 3)
        # Resultado: A → B bajó de 5 a 2; el flujo final solo usa rutas originales.
        self.assertEqual(flujo[("A", "B")], 2)
        self.assertEqual(set(flujo), set(CAPACIDADES_INVERSO))
        comprobar_flujo_factible(self, VERTICES_INVERSO, CAPACIDADES_INVERSO, flujo, "O", "T")

    def test_flujos_enteros_no_negativos_y_dentro_de_la_capacidad(self):
        for vertices, capacidades in [
            (VERTICES_MANUAL, CAPACIDADES_MANUAL), (VERTICES_INVERSO, CAPACIDADES_INVERSO),
        ]:
            flujo, _ = algoritmos.calcular_flujo_maximo(vertices, capacidades, "O", "T")
            for arco, unidades in flujo.items():
                self.assertIsInstance(unidades, int)
                self.assertGreaterEqual(unidades, 0)
                self.assertLessEqual(unidades, capacidades[arco])

    def test_cada_paso_aumenta_el_flujo_y_el_algoritmo_termina(self):
        _, pasos = algoritmos.calcular_flujo_maximo(
            VERTICES_INVERSO, CAPACIDADES_INVERSO, "O", "T"
        )
        acumulado = 0
        for paso in pasos:
            self.assertGreaterEqual(paso["cuello_de_botella"], 1)
            acumulado += paso["cuello_de_botella"]
            self.assertEqual(paso["flujo_acumulado"], acumulado)
        # No puede haber más pasos que paquetes salen del origen (5 + 4).
        self.assertLessEqual(len(pasos), 9)

    def test_bfs_y_dfs_obtienen_el_mismo_valor_maximo(self):
        for vertices, capacidades in [
            (VERTICES_MANUAL, CAPACIDADES_MANUAL), (VERTICES_INVERSO, CAPACIDADES_INVERSO),
        ]:
            con_bfs, _ = algoritmos.calcular_flujo_maximo(vertices, capacidades, "O", "T")
            con_dfs, _ = algoritmos.calcular_flujo_maximo(
                vertices, capacidades, "O", "T", algoritmos.ESTRATEGIA_PROFUNDIDAD
            )
            self.assertEqual(algoritmos.calcular_valor_del_flujo(con_bfs, "O"),
                             algoritmos.calcular_valor_del_flujo(con_dfs, "O"))
            comprobar_flujo_factible(self, vertices, capacidades, con_dfs, "O", "T")

    def test_el_valor_es_el_flujo_neto_que_sale_del_origen(self):
        # Al origen también le llega una ruta (C → O): lo que entra se resta.
        flujo = {("O", "A"): 5, ("A", "C"): 2, ("C", "O"): 2, ("A", "T"): 3}
        self.assertEqual(algoritmos.calcular_valor_del_flujo(flujo, "O"), 3)

    def test_origen_con_ruta_entrante_y_destino_con_ruta_saliente(self):
        vertices = ["O", "A", "B", "T"]
        capacidades = {("O", "A"): 4, ("A", "T"): 3, ("B", "O"): 6, ("T", "B"): 2}
        resultado = algoritmos.analizar_red_logistica(vertices, capacidades, "O", "T")
        self.assertEqual(resultado["flujo_maximo"], 3)
        self.assertEqual(resultado["capacidad_corte"], 3)
        self.assertEqual(resultado["flujo"][("B", "O")], 0)

    def test_sin_camino_el_flujo_es_cero_y_el_corte_vacio(self):
        capacidades = {("A", "T"): 3, ("B", "C"): 4, ("C", "T"): 5}      # nada sale de O
        resultado = algoritmos.analizar_red_logistica(VERTICES_MANUAL, capacidades, "O", "T")
        self.assertEqual(resultado["flujo_maximo"], 0)
        self.assertEqual(resultado["pasos"], [])
        self.assertEqual(resultado["corte"], [])
        self.assertEqual(resultado["capacidad_corte"], 0)
        self.assertEqual(resultado["lado_origen"], ["O"])

    def test_rechaza_redes_que_el_enunciado_prohibe(self):
        casos = [
            (["O", "T"], {("O", "T"): 3}, "O", "O"),                     # origen = destino
            (["O", "T"], {("O", "T"): 3}, "O", "Z"),                     # destino inexistente
            (["O", "T"], {("O", "T"): 3, ("T", "O"): 2}, "O", "T"),      # recíprocos
            (["O", "T"], {("O", "O"): 3, ("O", "T"): 2}, "O", "T"),      # lazo
            (["O", "T"], {("O", "T"): 0}, "O", "T"),                     # capacidad 0
            (["O", "T"], {("O", "T"): 2.5}, "O", "T"),                   # capacidad no entera
        ]
        for vertices, capacidades, origen, destino in casos:
            with self.assertRaises(ValueError):
                algoritmos.calcular_flujo_maximo(vertices, capacidades, origen, destino)


class PruebasCorteMinimo(unittest.TestCase):
    def test_corte_del_caso_manual(self):
        resultado = algoritmos.analizar_red_logistica(
            VERTICES_MANUAL, CAPACIDADES_MANUAL, "O", "T"
        )
        self.assertEqual(resultado["lado_origen"], ["O", "A", "B", "C"])
        self.assertEqual(resultado["lado_destino"], ["T"])
        self.assertEqual(resultado["corte"], [("A", "T"), ("C", "T")])
        self.assertEqual(resultado["capacidad_corte"], 3 + 5)

    def test_corte_de_la_red_con_arco_inverso(self):
        resultado = algoritmos.analizar_red_logistica(
            VERTICES_INVERSO, CAPACIDADES_INVERSO, "O", "T"
        )
        self.assertEqual(resultado["flujo_maximo"], 8)
        self.assertEqual(resultado["capacidad_corte"], 8)
        self.assertEqual(resultado["corte"], [("B", "T"), ("A", "C")])

    def test_solo_cuentan_las_rutas_de_s_hacia_t(self):
        # B → A va de T a S: no pertenece al corte ni suma capacidad.
        vertices = ["O", "A", "B", "T"]
        capacidades = {("O", "A"): 9, ("A", "T"): 2, ("O", "B"): 3, ("B", "A"): 7, ("B", "T"): 9}
        resultado = algoritmos.analizar_red_logistica(vertices, capacidades, "O", "T")
        self.assertEqual(resultado["flujo_maximo"], 5)
        self.assertEqual(resultado["lado_origen"], ["O", "A"])
        self.assertEqual(resultado["corte"], [("A", "T"), ("O", "B")])
        self.assertEqual(resultado["capacidad_corte"], 5)

    def test_flujo_maximo_igual_al_corte_minimo_por_fuerza_bruta(self):
        for vertices, capacidades in [
            (VERTICES_MANUAL, CAPACIDADES_MANUAL), (VERTICES_INVERSO, CAPACIDADES_INVERSO),
        ]:
            resultado = algoritmos.analizar_red_logistica(vertices, capacidades, "O", "T")
            minimo = corte_minimo_por_fuerza_bruta(vertices, capacidades, "O", "T")
            self.assertEqual(resultado["flujo_maximo"], minimo)
            self.assertEqual(resultado["capacidad_corte"], minimo)


class PruebasDeLasComprobaciones(unittest.TestCase):
    """Las funciones de verificación deben detectar flujos incorrectos."""

    def test_detecta_flujo_mayor_que_la_capacidad(self):
        flujo = {("O", "A"): 7, ("O", "B"): 0, ("A", "C"): 3, ("A", "T"): 3,
                 ("B", "C"): 0, ("C", "T"): 3}
        self.assertEqual(
            verificacion.buscar_violaciones_de_capacidad(CAPACIDADES_MANUAL, flujo), [("O", "A")]
        )

    def test_detecta_flujo_negativo_o_no_entero(self):
        flujo = {("O", "A"): -1, ("O", "B"): 1.5, ("A", "C"): 0, ("A", "T"): 0,
                 ("B", "C"): 0, ("C", "T"): 0}
        self.assertEqual(
            verificacion.buscar_violaciones_de_capacidad(CAPACIDADES_MANUAL, flujo),
            [("O", "A"), ("O", "B")],
        )

    def test_detecta_falta_de_conservacion(self):
        flujo = {("O", "A"): 6, ("O", "B"): 0, ("A", "C"): 1, ("A", "T"): 3,
                 ("B", "C"): 0, ("C", "T"): 1}
        self.assertEqual(
            verificacion.buscar_violaciones_de_conservacion(
                VERTICES_MANUAL, flujo, "O", "T"),
            ["A"],                                           # entran 6 y salen 4
        )

    def test_balances_de_entrada_y_salida(self):
        flujo, _ = algoritmos.calcular_flujo_maximo(VERTICES_MANUAL, CAPACIDADES_MANUAL, "O", "T")
        balances = verificacion.calcular_balances(VERTICES_MANUAL, flujo)
        self.assertEqual(balances["O"], {"entra": 0, "sale": 8})
        self.assertEqual(balances["C"], {"entra": 5, "sale": 5})
        self.assertEqual(balances["T"], {"entra": 8, "sale": 0})

    def test_contar_caminos_simples(self):
        adyacencia = verificacion.construir_adyacencia(VERTICES_MANUAL, CAPACIDADES_MANUAL)
        # O→A→T, O→A→C→T, O→B→C→T
        self.assertEqual(verificacion.contar_caminos_simples(adyacencia, "O", "T", {"O"}), 3)


if __name__ == "__main__":
    unittest.main()
