"""Pruebas de los escenarios de referencia, el caso manual y los cambios de extremos."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import algoritmos  # noqa: E402
import grafo  # noqa: E402
import verificacion  # noqa: E402
from test_algoritmos import corte_minimo_por_fuerza_bruta  # noqa: E402


def cargar_red_inicial():
    """Carga la red inicial compartida por los escenarios de prueba."""
    return grafo.cargar_red(verificacion.ARCHIVO_RED_INICIAL)


class PruebasEscenariosDeReferencia(unittest.TestCase):
    """Valores de CASOS_COMPROBADOS.md, recalculados con el código propio."""

    def setUp(self):
        self.red_original = cargar_red_inicial()
        self.escenarios = verificacion.comparar_escenarios(self.red_original)

    def test_flujos_maximos_de_referencia(self):
        for escenario, esperado in zip(self.escenarios, [18, 10, 20]):
            resultado = escenario["resultado"]
            self.assertEqual(resultado["flujo_maximo"], esperado, escenario["nombre"])
            self.assertEqual(resultado["capacidad_corte"], esperado, escenario["nombre"])

    def test_todas_las_comprobaciones_se_cumplen(self):
        for escenario in self.escenarios:
            self.assertEqual(len(escenario["comprobaciones"]), 7)
            for comprobacion in escenario["comprobaciones"]:
                self.assertTrue(
                    comprobacion["cumple"],
                    f"{escenario['nombre']}: {comprobacion['comprobacion']}",
                )

    def test_capacidad_y_conservacion_en_las_tres_configuraciones(self):
        for escenario in self.escenarios:
            red = escenario["red"]
            flujo = escenario["resultado"]["flujo"]
            capacidades = grafo.capacidades_activas(red)
            self.assertEqual(set(flujo), set(capacidades))
            for arco, capacidad in capacidades.items():
                self.assertTrue(0 <= flujo[arco] <= capacidad, f"{escenario['nombre']} {arco}")
            balances = verificacion.calcular_balances(red["vertices"], flujo)
            for vertice in red["vertices"]:
                if vertice not in ("O", "T"):
                    self.assertEqual(
                        balances[vertice]["entra"],
                        balances[vertice]["sale"],
                        f"{escenario['nombre']} {vertice}",
                    )

    def test_cortes_minimos_concretos(self):
        inicial, sin_ruta, con_mas_capacidad = [e["resultado"] for e in self.escenarios]
        self.assertEqual(inicial["corte"], [("C", "G"), ("F", "T"), ("H", "T"), ("I", "T")])
        self.assertEqual(inicial["lado_destino"], ["G", "T"])
        self.assertEqual(sin_ruta["corte"], [("C", "G"), ("F", "T"), ("I", "T")])
        self.assertEqual(con_mas_capacidad["corte"], [("O", "A"), ("O", "B"), ("O", "C")])
        self.assertEqual(con_mas_capacidad["lado_origen"], ["O"])

    def test_el_corte_de_referencia_del_kit_tambien_vale_18(self):
        capacidades = grafo.capacidades_activas(self.red_original)
        del_kit = [("F", "T"), ("G", "T"), ("H", "T"), ("I", "T")]
        self.assertEqual(sum(capacidades[arco] for arco in del_kit), 18)

    def test_los_escenarios_usan_el_mismo_origen_y_destino(self):
        for escenario in self.escenarios:
            self.assertEqual(escenario["red"]["origen"], "O")
            self.assertEqual(escenario["red"]["destino"], "T")

    def test_las_modificaciones_parten_de_la_red_original_sin_acumularse(self):
        inicial, sin_ruta, con_mas_capacidad = [e["red"] for e in self.escenarios]
        self.assertEqual(self.red_original, cargar_red_inicial())
        self.assertEqual(inicial, self.red_original)
        self.assertEqual(grafo.arcos_desactivados(sin_ruta), [("H", "T")])
        self.assertEqual(grafo.capacidades_activas(sin_ruta)[("I", "T")], 5)
        self.assertEqual(grafo.arcos_desactivados(con_mas_capacidad), [])
        self.assertEqual(grafo.capacidades_activas(con_mas_capacidad)[("I", "T")], 10)
        self.assertEqual(grafo.capacidades_activas(con_mas_capacidad)[("H", "T")], 8)

    def test_la_ruta_desactivada_no_lleva_flujo_ni_esta_en_el_corte(self):
        resultado = self.escenarios[1]["resultado"]
        self.assertNotIn(("H", "T"), resultado["flujo"])
        self.assertNotIn(("H", "T"), resultado["corte"])
        self.assertNotIn(("H", "T"), resultado["capacidades"])

    def test_flujo_maximo_igual_al_corte_minimo_por_fuerza_bruta(self):
        for escenario in self.escenarios:
            red = escenario["red"]
            minimo = corte_minimo_por_fuerza_bruta(
                red["vertices"], grafo.capacidades_activas(red), "O", "T"
            )
            self.assertEqual(escenario["resultado"]["flujo_maximo"], minimo, escenario["nombre"])

    def test_bfs_y_dfs_coinciden_en_los_tres_escenarios(self):
        for escenario in self.escenarios:
            red = escenario["red"]
            con_dfs, _ = algoritmos.calcular_flujo_maximo(
                red["vertices"],
                grafo.capacidades_activas(red),
                "O",
                "T",
                algoritmos.ESTRATEGIA_PROFUNDIDAD,
            )
            self.assertEqual(
                algoritmos.calcular_valor_del_flujo(con_dfs, "O"),
                escenario["resultado"]["flujo_maximo"],
            )

    def test_condiciones_iniciales(self):
        condiciones = verificacion.comprobar_condiciones_iniciales(self.red_original)
        self.assertEqual(len(condiciones), 4)
        for comprobacion in condiciones:
            self.assertTrue(comprobacion["cumple"], comprobacion["comprobacion"])


class PruebasCasoManual(unittest.TestCase):
    """Comprueba el caso pequeño resuelto manualmente."""

    def setUp(self):
        self.red = grafo.cargar_red(verificacion.ARCHIVO_CASO_MANUAL)

    def test_tamano_del_caso_manual(self):
        self.assertTrue(4 <= len(self.red["vertices"]) <= 6)
        self.assertEqual(grafo.validar_estructura(self.red), [])

    def test_el_codigo_obtiene_el_valor_de_la_solucion_manual(self):
        resultado = algoritmos.analizar_red(self.red)
        self.assertEqual(resultado["flujo_maximo"], 8)
        self.assertEqual(resultado["corte"], [("A", "T"), ("C", "T")])
        self.assertEqual(resultado["capacidad_corte"], 8)
        self.assertTrue(
            verificacion.todo_cumple(verificacion.verificar_resultado(self.red, resultado))
        )

    def test_el_flujo_manual_del_kit_es_factible_y_tambien_vale_8(self):
        flujo_manual = {
            ("O", "A"): 5,
            ("O", "B"): 3,
            ("A", "C"): 2,
            ("A", "T"): 3,
            ("B", "C"): 3,
            ("C", "T"): 5,
        }
        capacidades = grafo.capacidades_activas(self.red)
        self.assertEqual(
            verificacion.buscar_violaciones_de_capacidad(capacidades, flujo_manual), []
        )
        self.assertEqual(
            verificacion.buscar_violaciones_de_conservacion(
                self.red["vertices"], flujo_manual, "O", "T"
            ),
            [],
        )
        self.assertEqual(algoritmos.calcular_valor_del_flujo(flujo_manual, "O"), 8)
        flujo_codigo = algoritmos.analizar_red(self.red)["flujo"]
        self.assertNotEqual(flujo_manual, flujo_codigo)
        self.assertEqual(algoritmos.calcular_valor_del_flujo(flujo_codigo, "O"), 8)


class PruebasModificacionesYExtremos(unittest.TestCase):
    """Comprueba cambios de rutas, capacidades y extremos del flujo."""

    def test_desactivar_y_reactivar_recupera_el_flujo_original(self):
        red = cargar_red_inicial()
        grafo.desactivar_arco(red, "H", "T")
        self.assertEqual(algoritmos.analizar_red(red)["flujo_maximo"], 10)
        grafo.reactivar_arco(red, "H", "T")
        self.assertEqual(algoritmos.analizar_red(red)["flujo_maximo"], 18)

    def test_reducir_una_capacidad_del_corte_reduce_el_flujo(self):
        red = cargar_red_inicial()
        grafo.cambiar_capacidad(red, "H", "T", 3)
        self.assertEqual(algoritmos.analizar_red(red)["flujo_maximo"], 13)

    def test_agregar_una_conexion_directa_aumenta_el_flujo(self):
        red = cargar_red_inicial()
        grafo.agregar_arco(red, "O", "T", 4)
        resultado = algoritmos.analizar_red(red)
        self.assertEqual(resultado["flujo_maximo"], 22)
        self.assertTrue(verificacion.todo_cumple(verificacion.verificar_resultado(red, resultado)))

    def test_otro_origen_y_destino(self):
        red = cargar_red_inicial()
        grafo.cambiar_extremos(red, "A", "T")
        resultado = algoritmos.analizar_red(red)
        self.assertEqual(resultado["origen"], "A")
        self.assertEqual(resultado["flujo_maximo"], 9)
        self.assertEqual(resultado["corte"], [("A", "D"), ("A", "E")])

    def test_extremos_sin_conexion(self):
        red = cargar_red_inicial()
        grafo.cambiar_extremos(red, "T", "O")
        resultado = algoritmos.analizar_red(red)
        self.assertEqual(resultado["flujo_maximo"], 0)
        self.assertEqual(resultado["corte"], [])
        self.assertTrue(verificacion.todo_cumple(verificacion.verificar_resultado(red, resultado)))

    def test_todas_las_parejas_de_extremos_cumplen_y_coinciden_con_fuerza_bruta(self):
        red = cargar_red_inicial()
        capacidades = grafo.capacidades_activas(red)
        for origen in red["vertices"]:
            for destino in red["vertices"]:
                if origen == destino:
                    continue
                grafo.cambiar_extremos(red, origen, destino)
                resultado = algoritmos.analizar_red(red)
                self.assertTrue(
                    verificacion.todo_cumple(verificacion.verificar_resultado(red, resultado)),
                    f"Falla con {origen} → {destino}",
                )
                self.assertEqual(
                    resultado["flujo_maximo"],
                    corte_minimo_por_fuerza_bruta(red["vertices"], capacidades, origen, destino),
                    f"Falla con {origen} → {destino}",
                )


if __name__ == "__main__":
    unittest.main()
