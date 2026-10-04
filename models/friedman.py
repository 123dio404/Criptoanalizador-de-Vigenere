"""
models/friedman.py
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
from models.spanish_freq import ALFABETO_ESP_26, IC_TEORICO_ESP, IC_TEORICO_ALEATORIO

# Un periodo se considera "pico" si su IC alcanza al menos esta fracción del IC máximo observado.
TOLERANCIA_PICO_IC = 0.92


def calcular_indice_coincidencia(texto: str) -> float:
    """
    Calcula el Índice de Coincidencia (IC) de una cadena de texto.
    Solo considera caracteres alfabéticos A-Z.
    
    Fórmula:
        IC = sum(f_i * (f_i - 1)) / (N * (N - 1))
        
    Retorna 0.0 si la longitud del texto es menor a 2.
    """
    limpio = [ch for ch in texto.upper() if ch in ALFABETO_ESP_26]
    n = len(limpio)
    if n <= 1:
        return 0.0
    
    conteos = Counter(limpio)
    numerador = sum(c * (c - 1) for c in conteos.values())
    denominador = n * (n - 1)
    
    return numerador / denominador


def particionar_en_subtextos(texto: str, k: int) -> List[str]:
    """
    Divide el texto en 'k' subcadenas periódicas (cosets o columnas):
    C_j contiene los caracteres en posiciones i donde i % k == j.
    """
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
    """
    Evalúa el Índice de Coincidencia promedio para periodos candidatos desde min_periodo hasta max_periodo.
    
    Retorna:
    - 'global_ic': IC del criptograma completo sin particionar.
    - 'periods_data': Lista de diccionarios con {period, average_ic, coset_ics, delta_to_spanish}.
    - 'best_period_by_ic': El menor periodo 'k' cuyo IC promedio está en el pico (ver TOLERANCIA_PICO_IC).
    - 'estimated_key_length_friedman': Estimación directa según fórmula de Friedman.
    """
    c_limpio = "".join([ch for ch in criptograma.upper() if ch in ALFABETO_ESP_26])
    n = len(c_limpio)
    ic_global = calcular_indice_coincidencia(c_limpio)
    
    datos_periodos = []

    for k in range(min_periodo, min(max_periodo + 1, n + 1)):
        subtextos = particionar_en_subtextos(c_limpio, k)
        # Calcular IC de cada coset/subtexto
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
            'is_probable': ic_promedio >= 0.060  # Umbral cercano al lenguaje natural
        })

    # Selección del mejor periodo: los múltiplos de 'm' también presentan IC alto (y, al tener
    # cosets más cortos, un IC más ruidoso que puede superar al del periodo verdadero).
    # Por ello se elige el MENOR periodo cuyo IC esté dentro de la tolerancia del IC máximo.
    mejor_periodo = min_periodo
    mejor_ic_promedio = 0.0
    if datos_periodos:
        ic_maximo = max(d['average_ic'] for d in datos_periodos)
        for d in datos_periodos:
            if d['average_ic'] >= ic_maximo * TOLERANCIA_PICO_IC:
                mejor_periodo = d['period']
                mejor_ic_promedio = d['average_ic']
                break

    # Estimación analítica directa por fórmula de Friedman:
    # m ≈ (k_p - k_r) / (IC_obs - k_r + (k_p - IC_obs) / N)
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
