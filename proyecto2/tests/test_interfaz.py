"""
Pruebas de la interfaz: se ejecuta app.py sin navegador y se accionan sus controles.

Usan la herramienta de pruebas que trae Streamlit (AppTest). Si Streamlit no
está instalado, estas pruebas se omiten y el resto sigue funcionando.
"""

import sys
import unittest
from pathlib import Path

CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CARPETA_PROYECTO))

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@unittest.skipIf(AppTest is None, "Streamlit no está instalado")
class PruebasInterfaz(unittest.TestCase):
    """Comprueba la interacción principal de la aplicación Streamlit."""

    def setUp(self):
        self.app = AppTest.from_file(str(CARPETA_PROYECTO / "app.py"), default_timeout=60)
        self.app.run()

    def indicadores(self):
        """Devuelve los valores de los cuatro indicadores, en orden."""
        self.assertFalse(self.app.exception, "La aplicación lanzó una excepción")
        return [indicador.value for indicador in self.app.metric]

    def pulsar(self, clave):
        self.app.button(key=clave).click().run()

    def elegir(self, clave, valor):
        self.app.selectbox(key=clave).set_value(valor)

    def calcular(self):
        self.pulsar("boton_calcular")

    def errores(self):
        return [error.value for error in self.app.error]

    def red(self):
        return self.app.session_state.red

    def test_inicia_con_los_resultados_de_la_red_inicial(self):
        self.assertEqual(self.indicadores(), ["18 paq./h", "18 paq./h", "6", "✔ 7 de 7"])
        self.assertEqual(len(self.app.warning), 0)

    def test_desactivar_exige_recalcular_y_luego_se_puede_reactivar(self):
        self.elegir("selector_desactivar", ("H", "T"))
        self.pulsar("boton_desactivar")
        self.assertEqual(self.indicadores(), ["—", "—", "—", "—"])
        self.assertEqual(len(self.app.warning), 1)
        self.calcular()
        self.assertEqual(self.indicadores(), ["10 paq./h", "10 paq./h", "4", "✔ 7 de 7"])

        self.elegir("selector_reactivar", ("H", "T"))
        self.pulsar("boton_reactivar")
        self.calcular()
        self.assertEqual(self.indicadores()[0], "18 paq./h")

    def test_modificar_capacidad(self):
        self.elegir("selector_capacidad", ("I", "T"))
        self.app.number_input(key="entrada_capacidad").set_value(10)
        self.pulsar("boton_capacidad")
        self.assertEqual(self.indicadores(), ["—", "—", "—", "—"])
        self.calcular()
        self.assertEqual(self.indicadores(), ["20 paq./h", "20 paq./h", "7", "✔ 7 de 7"])

    def test_la_capacidad_solo_admite_valores_de_1_a_12(self):
        entrada = self.app.number_input(key="entrada_capacidad")
        self.assertEqual((entrada.min, entrada.max), (1, 12))
        nueva = self.app.number_input(key="entrada_nueva_capacidad")
        self.assertEqual((nueva.min, nueva.max), (1, 12))

    def test_agregar_conexion_valida(self):
        self.elegir("selector_nuevo_origen", "O")
        self.elegir("selector_nuevo_destino", "T")
        self.app.number_input(key="entrada_nueva_capacidad").set_value(4)
        self.pulsar("boton_agregar")
        self.calcular()
        self.assertEqual(self.indicadores()[:2], ["22 paq./h", "22 paq./h"])
        self.assertEqual(len(self.red()["arcos"]), 19)

    def test_rechaza_conexiones_prohibidas_sin_cambiar_la_red(self):
        casos = [("A", "A", "lazo"), ("O", "A", "repetidos"), ("A", "O", "recíprocos")]
        for origen, destino, palabra in casos:
            self.elegir("selector_nuevo_origen", origen)
            self.elegir("selector_nuevo_destino", destino)
            self.pulsar("boton_agregar")
            self.assertEqual(len(self.errores()), 1, f"{origen} → {destino}")
            self.assertIn(palabra, self.errores()[0])
            self.assertEqual(self.indicadores()[0], "18 paq./h")
            self.assertEqual(len(self.red()["arcos"]), 18)

    def test_cambiar_origen_y_destino(self):
        self.elegir("selector_origen", "A")
        self.pulsar("boton_extremos")
        self.calcular()
        self.assertEqual(self.indicadores()[:2], ["9 paq./h", "9 paq./h"])

    def test_rechaza_origen_igual_a_destino(self):
        self.elegir("selector_origen", "T")
        self.pulsar("boton_extremos")
        self.assertEqual(len(self.errores()), 1)
        self.assertIn("distintos", self.errores()[0])
        self.assertEqual(self.red()["origen"], "O")
        self.assertEqual(self.app.selectbox(key="selector_origen").value, "O")

    def test_sin_conexion_el_flujo_es_cero(self):
        self.elegir("selector_origen", "T")
        self.elegir("selector_destino", "O")
        self.pulsar("boton_extremos")
        self.calcular()
        self.assertEqual(self.indicadores(), ["0 paq./h", "0 paq./h", "0", "✔ 7 de 7"])

    def test_restaurar_vuelve_a_la_red_inicial(self):
        self.elegir("selector_desactivar", ("O", "A"))
        self.pulsar("boton_desactivar")
        self.elegir("selector_capacidad", ("I", "T"))
        self.app.number_input(key="entrada_capacidad").set_value(12)
        self.pulsar("boton_capacidad")
        self.elegir("selector_nuevo_origen", "O")
        self.elegir("selector_nuevo_destino", "H")
        self.pulsar("boton_agregar")
        self.elegir("selector_origen", "B")
        self.pulsar("boton_extremos")
        self.pulsar("boton_restaurar")
        self.assertEqual(self.indicadores(), ["18 paq./h", "18 paq./h", "6", "✔ 7 de 7"])
        red = self.red()
        self.assertEqual((red["origen"], red["destino"], len(red["arcos"])), ("O", "T", 18))
        self.assertTrue(all(arco["activo"] for arco in red["arcos"]))
        capacidad_i_t = [
            a["capacidad"] for a in red["arcos"] if (a["origen"], a["destino"]) == ("I", "T")
        ]
        self.assertEqual(capacidad_i_t, [5])

    def test_los_tres_modos_de_visualizacion_funcionan(self):
        for modo in ["Capacidades", "Corte mínimo", "Flujo máximo"]:
            self.app.radio(key="modo").set_value(modo).run()
            self.assertFalse(self.app.exception, modo)


if __name__ == "__main__":
    unittest.main()
