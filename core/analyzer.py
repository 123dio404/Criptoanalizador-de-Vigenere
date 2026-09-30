"""
core/analyzer.py
Orquestador del Criptoanálisis de Vigenère.
Integra Test de Kasiski, Índice de Coincidencia (Friedman), Análisis por Frecuencias (Chi-cuadrado)
y Descifrado con generación de traza de depuración.
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.
"""

from typing import Dict, Any, Optional, List
from core.vigenere import normalize_text, encrypt, decrypt
from core.kasiski import kasiski_examination
from core.friedman import friedman_period_analysis, calculate_ic
from core.frequency import recover_vigenere_key


class VigenereCryptanalyzer:
    """
    Clase orquestadora para el análisis criptográfico completo de textos cifrados con Vigenère.
    """
    
    def __init__(self, ciphertext: str = ""):
        self.raw_ciphertext = ciphertext
        self.clean_ciphertext = normalize_text(ciphertext, keep_spaces=False)
        self.kasiski_result: Optional[Dict[str, Any]] = None
        self.friedman_result: Optional[Dict[str, Any]] = None
        self.key_recovery_result: Optional[Dict[str, Any]] = None
        self.determined_key_length: int = 1
        self.recovered_key: str = ""
        self.decrypted_text: str = ""
        self.execution_log: List[str] = []

    def set_ciphertext(self, ciphertext: str) -> None:
        """Actualiza el texto cifrado a analizar."""
        self.raw_ciphertext = ciphertext
        self.clean_ciphertext = normalize_text(ciphertext, keep_spaces=False)
        self.kasiski_result = None
        self.friedman_result = None
        self.key_recovery_result = None
        self.execution_log.clear()

    def run_kasiski(self, ngram_lengths: List[int] = [3, 4, 5], max_key_len: int = 20) -> Dict[str, Any]:
        """Ejecuta el examen de Kasiski."""
        self.execution_log.append(f"[KASISKI] Iniciando análisis sobre {len(self.clean_ciphertext)} caracteres.")
        self.kasiski_result = kasiski_examination(
            self.clean_ciphertext,
            ngram_lengths=ngram_lengths,
            max_key_len=max_key_len
        )
        
        rep_count = len(self.kasiski_result['repeated_ngrams'])
        top_candidates = self.kasiski_result['top_key_lengths'][:3]
        self.execution_log.append(
            f"[KASISKI] Hallados {rep_count} n-gramas repetidos. Candidatos principales: {top_candidates}"
        )
        return self.kasiski_result

    def run_friedman(self, max_period: int = 15) -> Dict[str, Any]:
        """Ejecuta el análisis de Índice de Coincidencia de Friedman."""
        self.execution_log.append(f"[FRIEDMAN] Calculando IC global y particionado para periodos k=1..{max_period}.")
        self.friedman_result = friedman_period_analysis(self.clean_ciphertext, max_period=max_period)
        
        global_ic = round(self.friedman_result['global_ic'], 4)
        best_period = self.friedman_result['best_period_by_ic']
        best_avg_ic = round(self.friedman_result['best_avg_ic'], 4)
        
        self.execution_log.append(
            f"[FRIEDMAN] IC global = {global_ic}. Mejor periodo por IC = {best_period} (IC promedio = {best_avg_ic})."
        )
        return self.friedman_result

    def determine_probable_key_length(self) -> int:
        """
        Determina de forma inteligente la longitud de clave más probable
        cruzando las evidencias del Test de Kasiski y el Test de Friedman.
        """
        if not self.kasiski_result:
            self.run_kasiski()
        if not self.friedman_result:
            self.run_friedman()
            
        kasiski_tops = [k for k, _ in self.kasiski_result['top_key_lengths'][:5]]
        friedman_best = self.friedman_result['best_period_by_ic']
        
        # Verificar coincidencia directa entre el mejor de Friedman y el top de Kasiski
        chosen_length = 1
        if friedman_best in kasiski_tops:
            chosen_length = friedman_best
            self.execution_log.append(
                f"[DECISIÓN] Coincidencia robusta: Longitud {chosen_length} validada por Kasiski e IC."
            )
        elif kasiski_tops:
            # Si no coincide exactamente el #1, buscar si algún top de Kasiski tiene un IC alto (> 0.058)
            found = False
            for k_cand in kasiski_tops:
                # Buscar su IC en friedman_result
                for p_info in self.friedman_result['periods_data']:
                    if p_info['period'] == k_cand and p_info['average_ic'] >= 0.058:
                        chosen_length = k_cand
                        found = True
                        break
                if found:
                    break
            if not found:
                chosen_length = kasiski_tops[0]
            self.execution_log.append(f"[DECISIÓN] Longitud seleccionada por mayor consistencia: {chosen_length}")
        else:
            chosen_length = friedman_best
            self.execution_log.append(f"[DECISIÓN] Selección basada en pico de IC: {chosen_length}")
            
        self.determined_key_length = chosen_length
        return chosen_length

    def solve_key(self, key_length: Optional[int] = None) -> str:
        """
        Deduce la clave para la longitud especificada (o la detectada automáticamente)
        mediante Chi-cuadrado sobre cada columna.
        """
        if key_length is None:
            if self.determined_key_length <= 1:
                self.determine_probable_key_length()
            key_length = self.determined_key_length
            
        self.execution_log.append(f"[CLAVE] Recuperando caracteres de la clave para m = {key_length}.")
        self.key_recovery_result = recover_vigenere_key(self.clean_ciphertext, key_length)
        self.recovered_key = self.key_recovery_result['recovered_key']
        self.execution_log.append(f"[CLAVE] Clave recuperada: '{self.recovered_key}'")
        return self.recovered_key

    def decrypt_message(self, key: Optional[str] = None) -> str:
        """Descifra el criptograma utilizando la clave indicada o la recuperada."""
        if key is None:
            if not self.recovered_key:
                self.solve_key()
            key = self.recovered_key
            
        self.decrypted_text = decrypt(self.clean_ciphertext, key)
        self.execution_log.append(f"[DESCIFRADO] Mensaje descifrado exitosamente con clave '{key}'.")
        return self.decrypted_text

    def run_full_analysis(self) -> Dict[str, Any]:
        """Ejecuta el pipeline completo de criptoanálisis de inicio a fin."""
        self.run_kasiski()
        self.run_friedman()
        m = self.determine_probable_key_length()
        key = self.solve_key(m)
        decrypted = self.decrypt_message(key)
        
        return {
            'determined_key_length': m,
            'recovered_key': key,
            'decrypted_text': decrypted,
            'kasiski': self.kasiski_result,
            'friedman': self.friedman_result,
            'key_recovery': self.key_recovery_result,
            'execution_log': self.execution_log
        }
