"""Pruebas del modelo de la red: validaciones y modificaciones (Proyecto 2)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import grafo  # noqa: E402

CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"


def cargar_red_inicial():
    """Carga la red de referencia usada por las pruebas del modelo."""
    return grafo.cargar_red(CARPETA_DATOS / "red_inicial.json")


class PruebasConfiguracionInicial(unittest.TestCase):
    """Comprueba la estructura y los datos de la configuración inicial."""

    def test_red_inicial_cumple_tamanos_del_enunciado(self):
        red = cargar_red_inicial()
        self.assertEqual(len(red["vertices"]), 11)
        self.assertEqual(len(red["arcos"]), 18)
        self.assertEqual(grafo.validar_tamano_inicial(red), [])

    def test_red_inicial_sin_lazos_repetidos_reciprocos_ni_aislados(self):
        red = cargar_red_inicial()
        self.assertEqual(grafo.validar_estructura(red), [])
        self.assertEqual(grafo.buscar_vertices_aislados(red), [])
        self.assertNotEqual(red["origen"], red["destino"])

    def test_capacidades_iniciales_enteras_entre_1_y_12(self):
        for arco in cargar_red_inicial()["arcos"]:
            self.assertIsInstance(arco["capacidad"], int)
            self.assertTrue(1 <= arco["capacidad"] <= 12)

    def test_red_inicial_coincide_con_la_referencia_del_kit(self):
        esperadas = {
            ("O", "A"): 8,
            ("O", "B"): 7,
            ("O", "C"): 5,
            ("A", "D"): 6,
            ("A", "E"): 3,
            ("B", "E"): 6,
            ("B", "F"): 4,
            ("C", "F"): 5,
            ("C", "G"): 3,
            ("D", "H"): 6,
            ("D", "I"): 2,
            ("E", "H"): 5,
            ("E", "I"): 4,
            ("F", "I"): 6,
            ("F", "T"): 2,
            ("G", "T"): 3,
            ("H", "T"): 8,
            ("I", "T"): 5,
        }
        self.assertEqual(grafo.capacidades_activas(cargar_red_inicial()), esperadas)

    def test_los_datos_coinciden_con_los_json_de_referencia_del_kit(self):
        carpeta_kit = CARPETA_DATOS.parent.parent / "datos_referencia"
        pares = [
            ("red_inicial.json", "p2_red_inicial.json"),
            ("caso_manual.json", "p2_verificacion_manual.json"),
        ]
        for propio, del_kit in pares:
            if not (carpeta_kit / del_kit).exists():
                self.skipTest("No se encontró la carpeta datos_referencia del kit")
            red = grafo.cargar_red(CARPETA_DATOS / propio)
            referencia = grafo.cargar_red(carpeta_kit / del_kit)
            self.assertEqual(red["vertices"], referencia["vertices"])
            self.assertEqual(red["arcos"], referencia["arcos"])
            self.assertEqual(
                (red["origen"], red["destino"]), (referencia["origen"], referencia["destino"])
            )

    def test_todos_los_vertices_tienen_posicion_y_significado(self):
        red = cargar_red_inicial()
        for vertice in red["vertices"]:
            self.assertIn(vertice, red["posiciones"])
            self.assertIn(vertice, red["centros"])

    def test_validaciones_detectan_redes_incorrectas(self):
        red = cargar_red_inicial()
        red["vertices"].append("Z")
        self.assertEqual(grafo.buscar_vertices_aislados(red), ["Z"])
        self.assertTrue(grafo.validar_tamano_inicial(red))

        pequena = {
            "vertices": ["O", "T"],
            "origen": "O",
            "destino": "O",
            "arcos": [
                {"origen": "O", "destino": "T", "capacidad": 5, "activo": True},
                {"origen": "T", "destino": "O", "capacidad": 5, "activo": True},
                {"origen": "O", "destino": "O", "capacidad": 5, "activo": True},
                {"origen": "O", "destino": "T", "capacidad": 13, "activo": True},
            ],
        }
        problemas = " ".join(grafo.validar_estructura(pequena))
        for palabra in ["distintos", "recíprocos", "lazo", "repetido", "capacidad no permitida"]:
            self.assertIn(palabra, problemas)
        self.assertEqual(len(grafo.validar_tamano_inicial(pequena)), 2)

    def test_cargar_red_rechaza_json_invalido(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "red_invalida.json"
            ruta.write_text("{red incompleta", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON válido"):
                grafo.cargar_red(ruta)

    def test_cargar_red_rechaza_red_sin_claves_obligatorias(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "red_incompleta.json"
            ruta.write_text(json.dumps({"vertices": ["O", "T"]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Faltan claves"):
                grafo.cargar_red(ruta)


class PruebasAgregarConexion(unittest.TestCase):
    """Comprueba las reglas para agregar conexiones a la red."""

    def setUp(self):
        self.red = cargar_red_inicial()

    def assert_rechaza(self, origen, destino, capacidad, palabra_clave):
        """La conexión debe rechazarse con un mensaje claro y sin tocar la red."""
        antes = grafo.copiar_red(self.red)
        with self.assertRaises(ValueError) as error:
            grafo.agregar_arco(self.red, origen, destino, capacidad)
        self.assertIn(palabra_clave, str(error.exception))
        self.assertEqual(self.red, antes)

    def test_rechaza_lazo(self):
        self.assert_rechaza("A", "A", 5, "lazo")

    def test_rechaza_arco_repetido(self):
        self.assert_rechaza("O", "A", 5, "repetidos")

    def test_rechaza_arco_reciproco(self):
        self.assert_rechaza("A", "O", 5, "recíprocos")

    def test_rechaza_vertice_inexistente(self):
        self.assert_rechaza("O", "Z", 5, "centros de la red")

    def test_rechaza_repetida_y_reciproca_de_una_ruta_desactivada(self):
        grafo.desactivar_arco(self.red, "H", "T")
        self.assert_rechaza("H", "T", 5, "repetidos")
        self.assert_rechaza("T", "H", 5, "recíprocos")

    def test_rechaza_capacidades_fuera_de_rango_o_no_enteras(self):
        for capacidad in [0, 13, -3, 2.5, "5", None, True]:
            self.assert_rechaza("O", "H", capacidad, "entero entre 1 y 12")

    def test_agrega_conexion_valida_en_los_limites_de_capacidad(self):
        grafo.agregar_arco(self.red, "O", "H", 1)
        grafo.agregar_arco(self.red, "O", "I", 12)
        capacidades = grafo.capacidades_activas(self.red)
        self.assertEqual(capacidades[("O", "H")], 1)
        self.assertEqual(capacidades[("O", "I")], 12)
        self.assertEqual(grafo.validar_estructura(self.red), [])

    def test_el_limite_de_20_arcos_no_se_impone_a_las_modificaciones(self):
        for origen, destino in [("O", "H"), ("O", "I"), ("A", "H"), ("B", "I")]:
            grafo.agregar_arco(self.red, origen, destino, 4)
        self.assertEqual(len(self.red["arcos"]), 22)
        self.assertEqual(grafo.validar_estructura(self.red), [])


class PruebasDesactivarYCambiarCapacidad(unittest.TestCase):
    """Comprueba la activación, desactivación y capacidad de las rutas."""

    def setUp(self):
        self.red = cargar_red_inicial()

    def test_desactivar_quita_la_ruta_de_los_calculos_sin_borrarla(self):
        grafo.desactivar_arco(self.red, "H", "T")
        self.assertNotIn(("H", "T"), grafo.capacidades_activas(self.red))
        self.assertEqual(grafo.arcos_desactivados(self.red), [("H", "T")])
        self.assertEqual(len(self.red["arcos"]), 18)

    def test_reactivar_devuelve_la_red_al_estado_original(self):
        original = grafo.copiar_red(self.red)
        grafo.desactivar_arco(self.red, "H", "T")
        grafo.reactivar_arco(self.red, "H", "T")
        self.assertEqual(self.red, original)

    def test_errores_de_desactivacion(self):
        with self.assertRaises(ValueError):
            grafo.desactivar_arco(self.red, "O", "T")
        grafo.desactivar_arco(self.red, "H", "T")
        with self.assertRaises(ValueError):
            grafo.desactivar_arco(self.red, "H", "T")
        with self.assertRaises(ValueError):
            grafo.reactivar_arco(self.red, "O", "A")
        with self.assertRaises(ValueError):
            grafo.reactivar_arco(self.red, "O", "T")

    def test_cambiar_capacidad_valida(self):
        grafo.cambiar_capacidad(self.red, "I", "T", 10)
        self.assertEqual(grafo.capacidades_activas(self.red)[("I", "T")], 10)

    def test_cambiar_capacidad_rechaza_valores_no_permitidos(self):
        for capacidad in [0, 13, -1, 4.5, "10", True]:
            with self.assertRaises(ValueError):
                grafo.cambiar_capacidad(self.red, "I", "T", capacidad)
        self.assertEqual(grafo.capacidades_activas(self.red)[("I", "T")], 5)
        with self.assertRaises(ValueError):
            grafo.cambiar_capacidad(self.red, "O", "T", 5)


class PruebasExtremosYCopias(unittest.TestCase):
    """Comprueba los extremos del flujo y la independencia de las copias."""

    def test_cambiar_origen_y_destino(self):
        red = cargar_red_inicial()
        grafo.cambiar_extremos(red, "A", "I")
        self.assertEqual((red["origen"], red["destino"]), ("A", "I"))

    def test_rechaza_origen_igual_a_destino(self):
        red = cargar_red_inicial()
        with self.assertRaises(ValueError):
            grafo.cambiar_extremos(red, "B", "B")
        self.assertEqual((red["origen"], red["destino"]), ("O", "T"))

    def test_rechaza_extremos_inexistentes(self):
        red = cargar_red_inicial()
        with self.assertRaises(ValueError):
            grafo.cambiar_extremos(red, "O", "Z")

    def test_la_copia_es_independiente_del_original(self):
        original = cargar_red_inicial()
        copia = grafo.copiar_red(original)
        grafo.desactivar_arco(copia, "H", "T")
        grafo.cambiar_capacidad(copia, "I", "T", 10)
        grafo.agregar_arco(copia, "O", "H", 3)
        self.assertEqual(original, cargar_red_inicial())


if __name__ == "__main__":
    unittest.main()
