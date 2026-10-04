"""
tests/test_formateo_y_regresiones.py
Pruebas de la capa Controlador (formateo, sin PyQt) y regresiones de los bugs corregidos.
"""

import unittest

from controllers import formateo
from models.analyzer import CriptoanalizadorVigenere
from models.caso_prueba import CLAVE_CASO_PRUEBA, TEXTO_CASO_PRUEBA
from models.friedman import analizar_periodos_friedman
from models.kasiski import ejecutar_examen_kasiski
from models.vigenere import cifrar_vigenere, contar_intersecciones, descifrar_vigenere, generar_tabla_vigenere


class TestCifradoConFormato(unittest.TestCase):

    def test_conserva_espacios_signos_y_mayusculas(self):
        cifrado = cifrar_vigenere("Hola, Mundo!", "MAR", conservar_formato=True)
        self.assertEqual(cifrado, "Tocm, Mlzdf!")

    def test_es_reversible_con_caracteres_especiales(self):
        texto = "¿Canción de año 2026? ¡Sí, señor!\nLínea 2."
        cifrado = cifrar_vigenere(texto, "clave", conservar_formato=True)
        self.assertEqual(descifrar_vigenere(cifrado, "clave", conservar_formato=True), texto)

    def test_sin_formato_todo_seguido_en_mayusculas(self):
        self.assertEqual(cifrar_vigenere("Hola, Mundo!", "MAR"), "TOCMMLZDF")

    def test_intersecciones_cuentan_repeticiones(self):
        """AAA con clave M usa tres veces el cruce (M, A); HOLA reparte un cruce por letra."""
        self.assertEqual(contar_intersecciones("AAA", "M"), {("M", "A"): 3})
        self.assertEqual(
            contar_intersecciones("HOLA", "MAR"),
            {("M", "H"): 1, ("A", "O"): 1, ("R", "L"): 1, ("M", "A"): 1},
        )

    def test_intersecciones_ignoran_lo_que_no_se_cifra(self):
        self.assertEqual(
            contar_intersecciones("A, A!", "M", conservar_formato=True),
            {("M", "A"): 2},
        )

    def test_tabla_vigenere(self):
        tabla = generar_tabla_vigenere()
        self.assertEqual(len(tabla), 26)
        self.assertEqual(tabla[0], "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual(tabla[12][7], "T")  # H + M = T


class TestRegresiones(unittest.TestCase):

    def setUp(self):
        self.cripto = cifrar_vigenere(TEXTO_CASO_PRUEBA, CLAVE_CASO_PRUEBA)

    def test_factores_comunes_son_la_interseccion_de_las_distancias(self):
        """Antes se mostraba la UNIÓN de divisores: [27, 105, 57] daba [3, 5, 7, 9, 15, 19, ...]."""
        kasiski = ejecutar_examen_kasiski(self.cripto)
        item = next(i for i in kasiski['repeated_ngrams'] if i['ngram'] == "NUA")
        self.assertEqual(item['distances'], [27, 105, 57])
        self.assertEqual(item['common_factors'], [3])
        self.assertIn(5, item['factors'])  # la unión se conserva como dato aparte

    def test_friedman_prefiere_el_periodo_fundamental_y_no_un_multiplo(self):
        """Con la clave MAR el IC en k=12 (0.0749) supera al de k=3, pero el periodo correcto es 3."""
        friedman = analizar_periodos_friedman(self.cripto, max_periodo=15)
        ics = {p['period']: p['average_ic'] for p in friedman['periods_data']}
        self.assertGreater(ics[12], ics[3])
        self.assertEqual(friedman['best_period_by_ic'], 3)

    def test_cargar_criptograma_reinicia_todo_el_estado(self):
        analizador = CriptoanalizadorVigenere(self.cripto)
        analizador.ejecutar_analisis_completo()
        analizador.cargar_criptograma("ABCDEFGHIJKLMNOP")
        self.assertEqual(analizador.recovered_key, "")
        self.assertEqual(analizador.decrypted_text, "")
        self.assertEqual(analizador.determined_key_length, 1)
        self.assertEqual(analizador.execution_log, [])

    def test_clave_de_longitud_invalida(self):
        analizador = CriptoanalizadorVigenere(self.cripto)
        with self.assertRaises(ValueError):
            analizador.explorar_longitud_clave(0)


class TestFormateo(unittest.TestCase):

    def setUp(self):
        analizador = CriptoanalizadorVigenere(cifrar_vigenere(TEXTO_CASO_PRUEBA, CLAVE_CASO_PRUEBA))
        self.res = analizador.ejecutar_analisis_completo()

    def test_resumen_kasiski(self):
        ngramas, distancias, dominante = formateo.resumen_kasiski(self.res['kasiski'])
        self.assertEqual(ngramas, "N-Gramas Repetidos: 56")
        self.assertEqual(distancias, "Distancias Calculadas: 76")
        self.assertTrue(dominante.startswith("Divisor Dominante: m = 3"))

    def test_filas_ngramas_numeradas_y_con_factores_comunes(self):
        filas = formateo.filas_ngramas(self.res['kasiski'])
        self.assertEqual(filas[0]['indice'], "1")
        self.assertEqual(len(filas), 56)
        self.assertTrue(all(f['factores'] for f in filas))

    def test_filas_factores_marcan_un_unico_principal(self):
        filas = formateo.filas_factores(self.res['kasiski'])
        self.assertEqual([f['principal'] for f in filas].count(True), 1)
        self.assertEqual(filas[0]['candidata'], "m = 3")
        self.assertEqual(filas[0]['evaluacion'], "CANDIDATO PRINCIPAL")

    def test_filas_periodos_resaltan_k3_y_multiplos(self):
        filas = {f['periodo']: f for f in formateo.filas_periodos(self.res['friedman'])}
        self.assertTrue(filas['k = 3']['diagnostico'].startswith("PICO MÁXIMO"))
        self.assertIn("Múltiplo", filas['k = 6']['diagnostico'])
        self.assertFalse(filas['k = 4']['pico'])

    def test_filas_candidatas_ordenadas_con_optimo_en_primer_lugar(self):
        columna = self.res['key_recovery']['columns'][0]
        filas = formateo.filas_candidatas(columna)
        self.assertEqual(len(filas), 26)
        self.assertEqual(filas[0]['letra'], "M")
        self.assertTrue(filas[0]['optimo'])
        self.assertIn("ÓPTIMO", filas[0]['ranking'])

    def test_traza_incluye_eventos_y_clave(self):
        traza = formateo.construir_traza("ABC", "XYZ", "MAR", ["[TEST] evento"])
        self.assertIn("[TEST] evento", traza)
        self.assertIn("Clave Recuperada Final: MAR (m = 3)", traza)


if __name__ == "__main__":
    unittest.main(verbosity=2)
