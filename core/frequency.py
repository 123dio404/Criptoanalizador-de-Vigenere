"""
core/frequency.py
Análisis de frecuencias y recuperación de la clave mediante Chi-cuadrado (χ²) y Correlación.
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.

Fundamento Matemático:
Dado un criptograma particionado en 'm' subtextos o cosets C_0, C_1, ..., C_{m-1}:
Cada subtexto C_j es un cifrado monoalfabético César con desplazamiento k_j.

Para descubrir k_j:
Se prueban los 26 posibles desplazamientos s ∈ {0, 1, ..., 25} (correspondientes a A-Z).
Al aplicar el desplazamiento inverso a C_j, se obtienen las frecuencias observadas O_i.
Se comparan con las frecuencias esperadas del español E_i = N * P_esp(i) mediante:

1. Estadístico Chi-Cuadrado (χ²):
        χ²(s) = sum_{i=A}^Z  (O_i - E_i)² / E_i
   El desplazamiento 's' que MINIMIZA χ² es el más probable.

2. Coeficiente de Correlación / Producto Escalar:
        Corr(s) = sum_{i=A}^Z (O_i / N) * P_esp(i)
   El desplazamiento 's' que MAXIMIZA Corr es el más probable.
"""

from collections import Counter
from typing import Dict, List, Tuple, Any
from data.spanish_freq import ALPHABET_26, SPANISH_PROBABILITIES_26
from core.friedman import split_into_cosets
from core.vigenere import CHAR_TO_INDEX, INDEX_TO_CHAR


def score_shift_chi_squared(coset: str, shift: int) -> Tuple[float, float]:
    """
    Calcula el puntaje Chi-cuadrado y la correlación al descifrar 'coset' con el desplazamiento 'shift' (0 a 25).
    
    Retorna:
        (chi_squared, correlation)
    """
    n = len(coset)
    if n == 0:
        return float('inf'), 0.0
    
    # Descifrar coset con el desplazamiento candidato shift
    # p = (c - shift) mod 26
    decrypted_counts = Counter()
    for ch in coset:
        c_val = CHAR_TO_INDEX[ch]
        p_val = (c_val - shift) % 26
        decrypted_counts[INDEX_TO_CHAR[p_val]] += 1
        
    chi2 = 0.0
    correlation = 0.0
    
    for letter in ALPHABET_26:
        observed = decrypted_counts.get(letter, 0)
        expected_prob = SPANISH_PROBABILITIES_26[letter]
        expected = n * expected_prob
        
        # Chi-cuadrado
        if expected > 0:
            diff = observed - expected
            chi2 += (diff * diff) / expected
            
        # Correlación
        correlation += (observed / n) * expected_prob
        
    return chi2, correlation


def solve_key_for_column(coset: str) -> List[Dict[str, Any]]:
    """
    Prueba las 26 posibles letras de clave para una columna y retorna una lista ordenada
    desde la más probable (menor chi2 y mayor correlación) hasta la menos probable.
    """
    results = []
    
    for shift in range(26):
        letter = INDEX_TO_CHAR[shift]
        chi2, corr = score_shift_chi_squared(coset, shift)
        results.append({
            'shift': shift,
            'letter': letter,
            'chi2': round(chi2, 2),
            'correlation': round(corr, 4)
        })
        
    # Ordenar principalmente por menor Chi-cuadrado y secundariamente por mayor correlación
    results.sort(key=lambda x: (x['chi2'], -x['correlation']))
    return results


def recover_vigenere_key(ciphertext: str, key_length: int) -> Dict[str, Any]:
    """
    Recupera la clave más probable para una longitud dada 'key_length' dividiendo el criptograma
    en columnas y aplicando análisis de frecuencias a cada una.
    
    Retorna:
    - 'key': Palabra clave más probable
    - 'columns_analysis': Detalle del ranking de letras candidatas por cada posición
    """
    clean_c = "".join([ch for ch in ciphertext.upper() if ch in ALPHABET_26])
    cosets = split_into_cosets(clean_c, key_length)
    
    best_key_chars = []
    columns_detail = []
    
    for col_idx, coset in enumerate(cosets):
        candidates = solve_key_for_column(coset)
        best_candidate = candidates[0]
        best_key_chars.append(best_candidate['letter'])
        
        columns_detail.append({
            'column_index': col_idx,
            'coset_length': len(coset),
            'coset_sample': coset[:30] + ("..." if len(coset) > 30 else ""),
            'best_letter': best_candidate['letter'],
            'best_chi2': best_candidate['chi2'],
            'candidates_ranking': candidates[:5]  # Top 5 candidatos
        })
        
    reconstructed_key = "".join(best_key_chars)
    
    return {
        'key_length': key_length,
        'recovered_key': reconstructed_key,
        'columns': columns_detail
    }
