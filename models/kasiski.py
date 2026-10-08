import math
from collections import defaultdict
from typing import Any, Dict, List, Sequence

LONGITUDES_NGRAMA_POR_DEFECTO = (3, 4, 5)


def obtener_divisores_distancia(numero: int, min_val: int = 2, max_val: int = 25) -> List[int]:
    divisores = []
    for d in range(min_val, min(numero + 1, max_val + 1)):
        if numero % d == 0:
            divisores.append(d)
    return divisores


def buscar_secuencias_repetidas(criptograma: str, n: int = 3) -> Dict[str, List[int]]:
    posiciones = defaultdict(list)
    longitud = len(criptograma)

    for i in range(longitud - n + 1):
        ngram = criptograma[i:i + n]
        posiciones[ngram].append(i)

    return {ngram: pos_list for ngram, pos_list in posiciones.items() if len(pos_list) >= 2}


def calcular_mcd(valores: Sequence[int]) -> int:
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
    c_limpio = "".join([ch for ch in criptograma.upper() if ch.isalpha()])

    datos_repetidos = []
    todas_las_distancias = []
    histograma_factores = defaultdict(int)

    for n in longitudes_ngram:
        repetidos = buscar_secuencias_repetidas(c_limpio, n=n)
        for ngram, lista_pos in sorted(repetidos.items(), key=lambda item: len(item[1]), reverse=True):
            distancias_consecutivas = []
            factores_ngram = set()
            for i in range(len(lista_pos) - 1):
                d = lista_pos[i + 1] - lista_pos[i]
                distancias_consecutivas.append(d)
                todas_las_distancias.append(d)

                divisores = obtener_divisores_distancia(d, min_long_clave, max_long_clave)
                factores_ngram.update(divisores)
                for f in divisores:
                    histograma_factores[f] += 1

            # comunes son los divisores del mcd, no la union de todos los divisores
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
