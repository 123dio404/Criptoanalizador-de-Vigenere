from collections import Counter
from typing import Dict, List, Tuple, Any
from models.spanish_freq import ALFABETO_ESP_26, IC_TEORICO_ESP, IC_TEORICO_ALEATORIO

TOLERANCIA_PICO_IC = 0.92


def calcular_indice_coincidencia(texto: str) -> float:
    limpio = [ch for ch in texto.upper() if ch in ALFABETO_ESP_26]
    n = len(limpio)
    if n <= 1:
        return 0.0

    conteos = Counter(limpio)
    numerador = sum(c * (c - 1) for c in conteos.values())
    denominador = n * (n - 1)

    return numerador / denominador


def particionar_en_subtextos(texto: str, k: int) -> List[str]:
    limpio = "".join([ch for ch in texto.upper() if ch in ALFABETO_ESP_26])
    subtextos = [[] for _ in range(k)]
    for idx, ch in enumerate(limpio):
        subtextos[idx % k].append(ch)
    return ["".join(c) for c in subtextos]


def analizar_periodos_friedman(
    criptograma: str,
    max_periodo: int = 15,
    min_periodo: int = 1
) -> Dict[str, Any]:
    c_limpio = "".join([ch for ch in criptograma.upper() if ch in ALFABETO_ESP_26])
    n = len(c_limpio)
    ic_global = calcular_indice_coincidencia(c_limpio)

    datos_periodos = []

    for k in range(min_periodo, min(max_periodo + 1, n + 1)):
        subtextos = particionar_en_subtextos(c_limpio, k)
        ics_subtextos = [calcular_indice_coincidencia(s) for s in subtextos if len(s) > 1]

        if ics_subtextos:
            ic_promedio = sum(ics_subtextos) / len(ics_subtextos)
        else:
            ic_promedio = 0.0

        delta_espanol = abs(ic_promedio - IC_TEORICO_ESP)

        datos_periodos.append({
            'period': k,
            'average_ic': ic_promedio,
            'coset_ics': ics_subtextos,
            'delta_to_spanish': delta_espanol,
            'is_probable': ic_promedio >= 0.060
        })

    # los multiplos de m tambien pican, se toma el menor periodo cercano al maximo
    mejor_periodo = min_periodo
    mejor_ic_promedio = 0.0
    if datos_periodos:
        ic_maximo = max(d['average_ic'] for d in datos_periodos)
        for d in datos_periodos:
            if d['average_ic'] >= ic_maximo * TOLERANCIA_PICO_IC:
                mejor_periodo = d['period']
                mejor_ic_promedio = d['average_ic']
                break

    estimacion_friedman_m = None
    kp = IC_TEORICO_ESP
    kr = IC_TEORICO_ALEATORIO
    if n > 1 and (ic_global - kr) > 0:
        denom = (ic_global - kr) + ((kp - ic_global) / n)
        if denom > 0:
            estimacion_friedman_m = round((kp - kr) / denom, 2)

    return {
        'ciphertext_length': n,
        'global_ic': ic_global,
        'periods_data': datos_periodos,
        'best_period_by_ic': mejor_periodo,
        'best_avg_ic': mejor_ic_promedio,
        'friedman_formula_estimate': estimacion_friedman_m
    }
