"""
tests/test_caso_docente.py
Prueba y validación rigurosa del caso de prueba docente para ELC107:
Texto que inicia con "SOLAOSERPROFUNDO..." y clave "MAR".
Valida:
1. Detección de trigramas repetidos (Kasiski).
2. Distancias múltiplos de 3 y factor 3 como divisor dominante.
3. Cálculo del Índice de Coincidencia (IC) con pico en periodo k = 3.
4. Recuperación exacta de la clave "MAR" mediante Chi-cuadrado.
5. Descifrado íntegro del texto plano original.
"""

import unittest
from core.vigenere import normalize_text, encrypt, decrypt
from core.kasiski import kasiski_examination
from core.friedman import friedman_period_analysis, calculate_ic
from core.frequency import recover_vigenere_key
from core.analyzer import VigenereCryptanalyzer


class TestCriptoanalizadorDocente(unittest.TestCase):

    def setUp(self):
        # Caso de prueba representativo en español con el inicio requerido por la guía:
        # "SOLAOSERPROFUNDO..."
        self.plain_source = (
            "SOLA O SER PROFUNDO EN EL SILENCIO DE LA NOCHE CUANDO LA LUNA ILUMINA EL CAMINO. "
            "SOLA O SER PROFUNDO EN EL MAR AZUL Y TRANSPARENTE DONDE LOS PECES NADAN EN PAZ. "
            "EL RIO ES CLARO Y PROFUNDO, EL VIENTO SUSURRA HISTORIAS ANTIGUAS EN EL VALLE. "
            "SOLA O SER PROFUNDO EN EL PENSAMIENTO DEL HOMBRE QUE BUSCA LA VERDAD Y LA SABIDURIA."
        )
        self.key = "MAR"
        self.normalized_plain = normalize_text(self.plain_source)
        self.ciphertext = encrypt(self.normalized_plain, self.key)

    def test_01_text_starts_with_required_prefix(self):
        """Verifica que el texto claro comience exactamente con 'SOLAOSERPROFUNDO'."""
        self.assertTrue(self.normalized_plain.startswith("SOLAOSERPROFUNDO"))

    def test_02_encryption_and_decryption_symmetry(self):
        """Verifica que encrypt y decrypt sean operaciones inversas exactas."""
        decrypted = decrypt(self.ciphertext, self.key)
        self.assertEqual(decrypted, self.normalized_plain)

    def test_03_kasiski_detects_trigrams_and_factor_3(self):
        """Verifica el examen de Kasiski: detección de trigramas y prevalencia del factor 3."""
        kasiski_res = kasiski_examination(self.ciphertext, ngram_lengths=[3])
        repeated = kasiski_res['repeated_ngrams']
        
        # Deben existir trigramas repetidos
        self.assertGreater(len(repeated), 0, "No se detectaron trigramas repetidos en el criptograma.")
        
        # El factor 3 debe estar presente en el histograma de factores y tener alta frecuencia
        factor_counts = kasiski_res['factor_counts']
        self.assertIn(3, factor_counts, "El factor 3 no fue encontrado entre los divisores de distancias.")
        
        # El factor 3 debe ser el más votado (o uno de los top candidatos)
        top_candidates = [k for k, _ in kasiski_res['top_key_lengths']]
        self.assertEqual(top_candidates[0], 3, f"Se esperaba que 3 fuera el factor principal, se obtuvo {top_candidates}.")

    def test_04_friedman_ic_peak_at_period_3(self):
        """Verifica que el Índice de Coincidencia promedio tenga un pico cercano al español en k=3."""
        friedman_res = friedman_period_analysis(self.ciphertext, max_period=8)
        periods_dict = {p['period']: p['average_ic'] for p in friedman_res['periods_data']}
        
        ic_period_1 = periods_dict[1]
        ic_period_3 = periods_dict[3]
        
        # Para periodo 1 (cifrado polialfabético sin alinear), IC debe ser bajo (< 0.055)
        self.assertLess(ic_period_1, 0.055, f"IC en k=1 debería tender a aleatorio, fue {ic_period_1}")
        
        # Para periodo 3 (alineado a la clave), IC debe acercarse al español (~0.074, típicamente > 0.065)
        self.assertGreater(ic_period_3, 0.065, f"IC en k=3 debería ser alto, fue {ic_period_3}")
        self.assertGreater(ic_period_3, ic_period_1, "El IC en k=3 debe ser significativamente mayor al IC global.")

    def test_05_chi_squared_recovers_exact_key(self):
        """Verifica la recuperación exacta de la palabra clave 'MAR' mediante frecuencias Chi-cuadrado."""
        recovery = recover_vigenere_key(self.ciphertext, key_length=3)
        self.assertEqual(recovery['recovered_key'], "MAR", f"Se esperaba clave 'MAR', se obtuvo '{recovery['recovered_key']}'.")

    def test_06_full_pipeline_orchestrator(self):
        """Verifica el flujo automatizado completo de extremo a extremo."""
        analyzer = VigenereCryptanalyzer(self.ciphertext)
        result = analyzer.run_full_analysis()
        
        self.assertEqual(result['determined_key_length'], 3)
        self.assertEqual(result['recovered_key'], "MAR")
        self.assertEqual(result['decrypted_text'], self.normalized_plain)
        self.assertTrue(len(result['execution_log']) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
