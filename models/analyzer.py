"""
models/analyzer.py
Orquestador del Criptoanálisis de Vigenère (fachada del Modelo).
Integra Test de Kasiski, Índice de Coincidencia (Friedman), Análisis por Frecuencias (Chi-cuadrado)
y Descifrado con generación de traza de depuración.
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.
"""

from typing import Any, Dict, List, Optional, Sequence

from models.vigenere import normalizar_texto, descifrar_vigenere
from models.kasiski import ejecutar_examen_kasiski, LONGITUDES_NGRAMA_POR_DEFECTO
from models.friedman import analizar_periodos_friedman
from models.frequency import deducir_clave_por_frecuencias

UMBRAL_IC_CONSISTENTE = 0.058


class CriptoanalizadorVigenere:
    """
    Clase orquestadora para el análisis criptográfico completo de textos cifrados con Vigenère.
    Integra Kasiski, Friedman, Chi-cuadrado y Descifrado con trazabilidad paso a paso.
    """

    def __init__(self, criptograma: str = ""):
        self.execution_log: List[str] = []
        self.cargar_criptograma(criptograma)

    def cargar_criptograma(self, criptograma: str) -> None:
        """Actualiza el texto cifrado a analizar y reinicia TODOS los resultados previos."""
        self.raw_ciphertext = criptograma
        self.clean_ciphertext = normalizar_texto(criptograma, mantener_espacios=False)
        self.kasiski_result: Optional[Dict[str, Any]] = None
        self.friedman_result: Optional[Dict[str, Any]] = None
        self.key_recovery_result: Optional[Dict[str, Any]] = None
        self.determined_key_length: int = 1
        self.recovered_key: str = ""
        self.decrypted_text: str = ""
        self.execution_log.clear()

    def ejecutar_kasiski(
        self,
        longitudes_ngram: Sequence[int] = LONGITUDES_NGRAMA_POR_DEFECTO,
        max_long_clave: int = 20
    ) -> Dict[str, Any]:
        """Ejecuta el examen de Kasiski buscando repeticiones y factores comunes."""
        self.execution_log.append(f"[KASISKI] Iniciando análisis sobre {len(self.clean_ciphertext)} caracteres.")
        self.kasiski_result = ejecutar_examen_kasiski(
            self.clean_ciphertext,
            longitudes_ngram=longitudes_ngram,
            max_long_clave=max_long_clave
        )

        rep_count = len(self.kasiski_result['repeated_ngrams'])
        top_candidates = self.kasiski_result['top_key_lengths'][:3]
        self.execution_log.append(
            f"[KASISKI] Hallados {rep_count} n-gramas repetidos. Candidatos principales: {top_candidates}"
        )
        return self.kasiski_result

    def ejecutar_friedman(self, max_periodo: int = 15) -> Dict[str, Any]:
        """Ejecuta el análisis de Índice de Coincidencia de Friedman para periodos k=1..max_periodo."""
        self.execution_log.append(f"[FRIEDMAN] Calculando IC global y particionado para periodos k=1..{max_periodo}.")
        self.friedman_result = analizar_periodos_friedman(self.clean_ciphertext, max_periodo=max_periodo)

        global_ic = round(self.friedman_result['global_ic'], 4)
        best_period = self.friedman_result['best_period_by_ic']
        best_avg_ic = round(self.friedman_result['best_avg_ic'], 4)

        self.execution_log.append(
            f"[FRIEDMAN] IC global = {global_ic}. Mejor periodo por IC = {best_period} (IC promedio = {best_avg_ic})."
        )
        return self.friedman_result

    def determinar_longitud_clave_probable(self) -> int:
        """
        Determina de forma inteligente la longitud de clave más probable
        cruzando las evidencias del Test de Kasiski y el Test de Friedman.
        """
        if not self.kasiski_result:
            self.ejecutar_kasiski()
        if not self.friedman_result:
            self.ejecutar_friedman()

        kasiski_tops = [k for k, _ in self.kasiski_result['top_key_lengths'][:5]]
        friedman_best = self.friedman_result['best_period_by_ic']

        if friedman_best in kasiski_tops:
            # Coincidencia directa entre el mejor de Friedman y el top de Kasiski
            chosen_length = friedman_best
            self.execution_log.append(
                f"[DECISIÓN] Coincidencia robusta: Longitud {chosen_length} validada por Kasiski e IC."
            )
        elif kasiski_tops:
            # Si no coincide, elegir el primer candidato de Kasiski con IC consistente con el idioma
            ic_por_periodo = {p['period']: p['average_ic'] for p in self.friedman_result['periods_data']}
            chosen_length = next(
                (k for k in kasiski_tops if ic_por_periodo.get(k, 0.0) >= UMBRAL_IC_CONSISTENTE),
                kasiski_tops[0]
            )
            self.execution_log.append(f"[DECISIÓN] Longitud seleccionada por mayor consistencia: {chosen_length}")
        else:
            chosen_length = friedman_best
            self.execution_log.append(f"[DECISIÓN] Selección basada en pico de IC: {chosen_length}")

        self.determined_key_length = chosen_length
        return chosen_length

    def explorar_longitud_clave(self, longitud_clave: int) -> Dict[str, Any]:
        """
        Calcula (sin alterar el estado ni la traza) la clave Chi-cuadrado para una longitud dada,
        incluyendo el ranking completo de letras por columna. Útil para exploración interactiva.
        """
        return deducir_clave_por_frecuencias(self.clean_ciphertext, longitud_clave)

    def deducir_clave(self, longitud_clave: Optional[int] = None) -> str:
        """
        Deduce la clave para la longitud especificada (o la detectada automáticamente)
        mediante Chi-cuadrado sobre cada columna monoalfabética.
        """
        if longitud_clave is None:
            if self.determined_key_length <= 1:
                self.determinar_longitud_clave_probable()
            longitud_clave = self.determined_key_length

        self.execution_log.append(f"[CLAVE] Recuperando caracteres de la clave para m = {longitud_clave}.")
        self.key_recovery_result = deducir_clave_por_frecuencias(self.clean_ciphertext, longitud_clave)
        self.recovered_key = self.key_recovery_result['recovered_key']
        self.execution_log.append(f"[CLAVE] Clave recuperada: '{self.recovered_key}'")
        return self.recovered_key

    def descifrar_mensaje(self, clave: Optional[str] = None) -> str:
        """Descifra el criptograma utilizando la clave indicada o la recuperada."""
        if clave is None:
            if not self.recovered_key:
                self.deducir_clave()
            clave = self.recovered_key

        self.decrypted_text = descifrar_vigenere(self.clean_ciphertext, clave)
        self.execution_log.append(f"[DESCIFRADO] Mensaje descifrado exitosamente con clave '{clave}'.")
        return self.decrypted_text

    def ejecutar_analisis_completo(self) -> Dict[str, Any]:
        """Ejecuta el pipeline completo de criptoanálisis de inicio a fin."""
        self.ejecutar_kasiski()
        self.ejecutar_friedman()
        m = self.determinar_longitud_clave_probable()
        clave = self.deducir_clave(m)
        descifrado = self.descifrar_mensaje(clave)

        return {
            'determined_key_length': m,
            'recovered_key': clave,
            'decrypted_text': descifrado,
            'kasiski': self.kasiski_result,
            'friedman': self.friedman_result,
            'key_recovery': self.key_recovery_result,
            'execution_log': self.execution_log
        }
