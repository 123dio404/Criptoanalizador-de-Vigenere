"""
core/friedman.py
Cálculo del Índice de Coincidencia (IC) y Test de Friedman (William F. Friedman, 1922).
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.

Fundamento Matemático:
El Índice de Coincidencia (IC) mide la probabilidad de que dos letras seleccionadas al azar
del texto sean idénticas:

         sum_{i=A}^Z f_i * (f_i - 1)
    IC = ---------------------------
                 N * (N - 1)

Valores de Referencia:
- Idioma Español (monogramas naturales): IC ≈ 0.0740
- Idioma Inglés: IC ≈ 0.0667
- Texto Aleatorio (distribución uniforme 1/26): IC ≈ 0.0385

Partición en Cosets (Subtextos por periodo k):
Si la longitud de la clave es 'm', al dividir el texto en 'm' subtextos:
    C_j = c_j, c_{j+m}, c_{j+2m}, ...  (para j = 0, ..., m-1)
Cada subtexto C_j fue cifrado con un único desplazamiento César monoalfabético.
Como una traslación monoalfabética preserva las frecuencias internas, el IC de cada subtexto
vuelve al valor del idioma original: IC(C_j) ≈ 0.074.
El promedio de los IC de los subtextos para el periodo correcto 'm' mostrará un pico distintivo.
"""

from collections import Counter
from typing import Dict, List, Tuple, Any
from data.spanish_freq import ALPHABET_26, IC_THEORETICAL_SPANISH, IC_THEORETICAL_RANDOM


def calculate_ic(text: str) -> float:
    """
    Calcula el Índice de Coincidencia (IC) de una cadena de texto.
    Solo considera caracteres alfabéticos A-Z.
    
    Retorna 0.0 si la longitud del texto es menor a 2.
    """
    clean = [ch for ch in text.upper() if ch in ALPHABET_26]
    n = len(clean)
    if n <= 1:
        return 0.0
    
    counts = Counter(clean)
    numerator = sum(count * (count - 1) for count in counts.values())
    denominator = n * (n - 1)
    
    return numerator / denominator


def split_into_cosets(text: str, k: int) -> List[str]:
    """
    Divide el texto en 'k' subcadenas periódicas (cosets):
    C_j contiene los caracteres en posiciones i donde i % k == j.
    """
    clean = "".join([ch for ch in text.upper() if ch in ALPHABET_26])
    cosets = [[] for _ in range(k)]
    for idx, ch in enumerate(clean):
        cosets[idx % k].append(ch)
    return ["".join(c) for c in cosets]


def friedman_period_analysis(
    ciphertext: str,
    max_period: int = 15,
    min_period: int = 1
) -> Dict[str, Any]:
    """
    Evalúa el Índice de Coincidencia promedio para periodos candidatos desde min_period hasta max_period.
    
    Retorna:
    - 'global_ic': IC del criptograma completo sin particionar
    - 'periods_data': Lista de diccionarios con {period, average_ic, coset_ics, delta_to_spanish}
    - 'best_period_by_ic': El periodo 'k' con mayor IC promedio
    - 'estimated_key_length_friedman': Estimación directa según fórmula de Friedman
    """
    clean_c = "".join([ch for ch in ciphertext.upper() if ch in ALPHABET_26])
    n = len(clean_c)
    global_ic = calculate_ic(clean_c)
    
    periods_data = []
    best_period = 1
    best_avg_ic = 0.0
    
    for k in range(min_period, min(max_period + 1, n + 1)):
        cosets = split_into_cosets(clean_c, k)
        # Calcular IC de cada coset
        coset_ics = [calculate_ic(coset) for coset in cosets if len(coset) > 1]
        
        if coset_ics:
            avg_ic = sum(coset_ics) / len(coset_ics)
        else:
            avg_ic = 0.0
            
        delta_spanish = abs(avg_ic - IC_THEORETICAL_SPANISH)
        
        periods_data.append({
            'period': k,
            'average_ic': avg_ic,
            'coset_ics': coset_ics,
            'delta_to_spanish': delta_spanish,
            'is_probable': avg_ic >= 0.060  # Umbral cercano a lenguaje natural
        })
        
        # Considerar el mejor periodo (que tenga mayor IC)
        if avg_ic > best_avg_ic:
            best_avg_ic = avg_ic
            best_period = k
            
    # Estimación directa por fórmula de Friedman:
    # m ≈ (k_p - k_r) / (IC_obs - k_r + (k_p - IC_obs) / N)
    friedman_m_estimate = None
    kp = IC_THEORETICAL_SPANISH
    kr = IC_THEORETICAL_RANDOM
    if n > 1 and (global_ic - kr) > 0:
        denom = (global_ic - kr) + ((kp - global_ic) / n)
        if denom > 0:
            friedman_m_estimate = round((kp - kr) / denom, 2)
            
    return {
        'ciphertext_length': n,
        'global_ic': global_ic,
        'periods_data': periods_data,
        'best_period_by_ic': best_period,
        'best_avg_ic': best_avg_ic,
        'friedman_formula_estimate': friedman_m_estimate
    }
