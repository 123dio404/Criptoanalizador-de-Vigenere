"""
models/kasiski.py
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
from typing import Any, Dict, List, Sequence

LONGITUDES_NGRAMA_POR_DEFECTO = (3, 4, 5)


def obtener_divisores_distancia(numero: int, min_val: int = 2, max_val: int = 25) -> List[int]:
    """
    Obtiene todos los divisores enteros de una distancia dentro del rango [min_val, max_val].
    Cada divisor representa una longitud de clave potencial 'm' tal que m | Δ.
    """
    divisores = []
    for d in range(min_val, min(numero + 1, max_val + 1)):
        if numero % d == 0:
            divisores.append(d)
    return divisores


def buscar_secuencias_repetidas(criptograma: str, n: int = 3) -> Dict[str, List[int]]:
    """
    Encuentra todas las secuencias (n-gramas o trigramas) que se repiten en el criptograma.

    Retorna:
        Diccionario {secuencia: [posiciones_donde_aparece]} para aquellas con repeticiones >= 2.
    """
    posiciones = defaultdict(list)
    longitud = len(criptograma)

    for i in range(longitud - n + 1):
        ngram = criptograma[i:i + n]
        posiciones[ngram].append(i)

    # Filtrar únicamente los n-gramas que se repiten al menos 2 veces
    return {ngram: pos_list for ngram, pos_list in posiciones.items() if len(pos_list) >= 2}


def calcular_mcd(valores: Sequence[int]) -> int:
    """MCD de una lista de enteros (0 si la lista está vacía)."""
    mcd = 0
    for v in valores:
        mcd = math.gcd(mcd, v)
    return mcd


def ejecutar_examen_kasiski(
    criptograma: str,
    longitudes_ngram: Sequence[int] = LONGITUDES_NGRAMA_POR_DEFECTO,
    min_long_clave: int = 2,
    max_long_clave: int = 25
) -> Dict[str, Any]:
    """
    Ejecuta el examen de Kasiski completo sobre el texto cifrado.

    Retorna un diccionario detallado con:
    - 'repeated_ngrams': Detalle de cada n-grama repetido, posiciones, distancias y factores:
        * 'factors': unión de los divisores de todas sus distancias.
        * 'common_factors': divisores comunes a TODAS sus distancias (divisores de su MCD).
    - 'all_distances': Lista completa de todas las distancias Δ halladas.
    - 'factor_counts': Conteo de votos de cada divisor candidato a longitud de clave.
    - 'top_key_lengths': Lista ordenada [(longitud_candidata, votos), ...]
    - 'gcd_overall': Máximo común divisor global de las distancias.
    """
    c_limpio = "".join([ch for ch in criptograma.upper() if ch.isalpha()])

    datos_repetidos = []
    todas_las_distancias = []
    histograma_factores = defaultdict(int)

    # Procesar n-gramas (por defecto trigramas 3, 4, 5)
    for n in longitudes_ngram:
        repetidos = buscar_secuencias_repetidas(c_limpio, n=n)
        for ngram, lista_pos in sorted(repetidos.items(), key=lambda item: len(item[1]), reverse=True):
            # Calcular distancias entre apariciones consecutivas
            distancias_consecutivas = []
            factores_ngram = set()
            for i in range(len(lista_pos) - 1):
                d = lista_pos[i + 1] - lista_pos[i]
                distancias_consecutivas.append(d)
                todas_las_distancias.append(d)

                # Descomponer distancia en factores divisores y votar
                divisores = obtener_divisores_distancia(d, min_long_clave, max_long_clave)
                factores_ngram.update(divisores)
                for f in divisores:
                    histograma_factores[f] += 1

            # Factores realmente comunes a todas las distancias: divisores de su MCD
            mcd_ngram = calcular_mcd(distancias_consecutivas)
            factores_comunes = obtener_divisores_distancia(mcd_ngram, min_long_clave, max_long_clave)

            datos_repetidos.append({
                'ngram': ngram,
                'length': n,
                'count': len(lista_pos),
                'positions': lista_pos,
                'distances': distancias_consecutivas,
                'gcd': mcd_ngram,
                'factors': sorted(factores_ngram),
                'common_factors': factores_comunes
            })

    # Ordenar candidatos a longitud de clave por mayor frecuencia acumulada (votos);
    # a igualdad de votos, el menor periodo primero (resultado determinista).
    candidatos_ordenados = sorted(
        [(k, v) for k, v in histograma_factores.items() if min_long_clave <= k <= max_long_clave],
        key=lambda x: (-x[1], x[0])
    )

    return {
        'clean_ciphertext': c_limpio,
        'total_length': len(c_limpio),
        'repeated_ngrams': datos_repetidos,
        'all_distances': todas_las_distancias,
        'factor_counts': dict(sorted(histograma_factores.items())),
        'top_key_lengths': candidatos_ordenados,
        'gcd_overall': calcular_mcd(todas_las_distancias)
    }
