"""
core/kasiski.py
Implementación del Test de Kasiski (Friedrich Kasiski, 1863).
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.

Fundamento Matemático:
Si una secuencia idéntica de texto claro de longitud >= 3 se repite a una distancia que
es múltiplo de la longitud de la clave 'm', y coincide con la misma fase de la clave,
producirá exactamente el mismo criptograma en ambas posiciones.

Por lo tanto:
    Distancia Δ = pos_2 - pos_1 = k * m
Donde 'm' (longitud de la clave) divide a la distancia Δ.
Al factorizar todas las distancias entre secuencias repetidas, el factor común
más recurrente es un fuerte candidato a ser la longitud de la clave 'm'.
"""

import math
from collections import defaultdict
from typing import Dict, List, Tuple, Any


def get_factors(number: int, min_val: int = 2, max_val: int = 25) -> List[int]:
    """
    Obtiene todos los divisores enteros de un número dentro del rango [min_val, max_val].
    """
    factors = []
    for d in range(min_val, min(number + 1, max_val + 1)):
        if number % d == 0:
            factors.append(d)
    return factors


def find_repeated_ngrams(ciphertext: str, n: int = 3) -> Dict[str, List[int]]:
    """
    Encuentra todas las secuencias de longitud 'n' que se repiten en el criptograma.
    
    Retorna:
        Diccionario {secuencia: [posiciones_donde_aparece]} para aquellas con len(pos) >= 2.
    """
    positions = defaultdict(list)
    length = len(ciphertext)
    
    for i in range(length - n + 1):
        ngram = ciphertext[i:i + n]
        positions[ngram].append(i)
        
    # Filtrar únicamente los n-gramas que se repiten al menos 2 veces
    repeated = {ngram: pos_list for ngram, pos_list in positions.items() if len(pos_list) >= 2}
    return repeated


def kasiski_examination(
    ciphertext: str,
    ngram_lengths: List[int] = [3, 4, 5],
    min_key_len: int = 2,
    max_key_len: int = 25
) -> Dict[str, Any]:
    """
    Ejecuta el examen de Kasiski completo sobre el texto cifrado.
    
    Retorna un diccionario detallado con:
    - 'repeated_ngrams': Lista de tuplas con el detalle de cada n-grama repetido:
        (ngram, posiciones, distancias_consecutivas, todas_las_distancias, factores)
    - 'distances': Lista completa de todas las distancias halladas
    - 'factor_counts': Conteo de frecuencia de cada divisor (candidatos a longitud de clave)
    - 'top_key_lengths': Lista ordenada [(longitud_candidata, votos/frecuencia), ...]
    - 'gcd_overall': Máximo común divisor global de las distancias
    """
    clean_c = "".join([ch for ch in ciphertext.upper() if ch.isalpha()])
    
    all_repeated_data = []
    all_distances = []
    factor_histogram = defaultdict(int)
    
    # Procesar n-gramas (por defecto trigramas 3, y superiores)
    for n in ngram_lengths:
        repeated = find_repeated_ngrams(clean_c, n=n)
        for ngram, pos_list in sorted(repeated.items(), key=lambda item: len(item[1]), reverse=True):
            # Calcular distancias entre apariciones consecutivas y entre pares
            consecutive_distances = []
            for i in range(len(pos_list) - 1):
                d = pos_list[i + 1] - pos_list[i]
                consecutive_distances.append(d)
                all_distances.append(d)
                
                # Descomponer distancia en factores
                factors = get_factors(d, min_key_len, max_key_len)
                for f in factors:
                    factor_histogram[f] += 1
            
            # Factores de las distancias consecutivas
            ngram_factors = set()
            for d in consecutive_distances:
                ngram_factors.update(get_factors(d, min_key_len, max_key_len))
                
            all_repeated_data.append({
                'ngram': ngram,
                'length': n,
                'count': len(pos_list),
                'positions': pos_list,
                'distances': consecutive_distances,
                'factors': sorted(list(ngram_factors))
            })
            
    # Ordenar candidatos a longitud por mayor frecuencia acumulada
    sorted_candidates = sorted(
        [(k, v) for k, v in factor_histogram.items() if min_key_len <= k <= max_key_len],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Calcular MCD global si hay distancias
    overall_gcd = 0
    if all_distances:
        overall_gcd = all_distances[0]
        for d in all_distances[1:]:
            overall_gcd = math.gcd(overall_gcd, d)
            
    return {
        'clean_ciphertext': clean_c,
        'total_length': len(clean_c),
        'repeated_ngrams': all_repeated_data,
        'all_distances': all_distances,
        'factor_counts': dict(sorted(factor_histogram.items())),
        'top_key_lengths': sorted_candidates,
        'gcd_overall': overall_gcd
    }
