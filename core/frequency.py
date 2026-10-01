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
from data.spanish_freq import ALFABETO_ESP_26, PROBABILIDADES_ESP
from core.friedman import particionar_en_subtextos
from core.vigenere import LETRA_A_INDICE, INDICE_A_LETRA


def calcular_discrepancia_chi_cuadrado(subtexto: str, desplazamiento: int) -> Tuple[float, float]:
    """
    Calcula el estadístico Chi-cuadrado (χ²) y la correlación fonética al descifrar
    'subtexto' con un desplazamiento propuesto (0 a 25 correspondiente a A-Z).
    
    Fórmulas:
        χ²(s) = sum((O_i - E_i)² / E_i)
        Corr(s) = sum((O_i / N) * P_esp(i))
        
    Retorna:
        (chi_cuadrado, correlacion)
    """
    n = len(subtexto)
    if n == 0:
        return float('inf'), 0.0
    
    # Descifrar subtexto César con el desplazamiento candidato
    # p = (c - desplazamiento) mod 26
    conteos_descifrado = Counter()
    for ch in subtexto:
        c_val = LETRA_A_INDICE[ch]
        p_val = (c_val - desplazamiento) % 26
        conteos_descifrado[INDICE_A_LETRA[p_val]] += 1
        
    chi2 = 0.0
    correlacion = 0.0
    
    for letra in ALFABETO_ESP_26:
        observado = conteos_descifrado.get(letra, 0)
        prob_esperada = PROBABILIDADES_ESP[letra]
        esperado = n * prob_esperada
        
        # Estadístico Chi-cuadrado
        if esperado > 0:
            diff = observado - esperado
            chi2 += (diff * diff) / esperado
            
        # Coeficiente de correlación
        correlacion += (observado / n) * prob_esperada
        
    return chi2, correlacion


def resolver_clave_para_columna(subtexto: str) -> List[Dict[str, Any]]:
    """
    Prueba las 26 posibles letras del alfabeto para una columna (subtexto monoalfabético César)
    y retorna la lista ordenada desde la más probable (menor χ² y mayor correlación)
    hasta la menos probable.
    """
    resultados = []
    
    for desplazamiento in range(26):
        letra = INDICE_A_LETRA[desplazamiento]
        chi2, corr = calcular_discrepancia_chi_cuadrado(subtexto, desplazamiento)
        resultados.append({
            'shift': desplazamiento,
            'letter': letra,
            'chi2': round(chi2, 2),
            'correlation': round(corr, 4)
        })
        
    # Ordenar principalmente por menor Chi-cuadrado y secundariamente por mayor correlación
    resultados.sort(key=lambda x: (x['chi2'], -x['correlation']))
    return resultados


def deducir_clave_por_frecuencias(criptograma: str, longitud_clave: int) -> Dict[str, Any]:
    """
    Recupera la clave más probable para una longitud dada 'longitud_clave'
    dividiendo el criptograma en columnas y aplicando el análisis Chi-cuadrado a cada una.
    
    Retorna:
    - 'recovered_key': Palabra clave más probable
    - 'columns': Detalle del ranking de letras candidatas por cada posición
    """
    c_limpio = "".join([ch for ch in criptograma.upper() if ch in ALFABETO_ESP_26])
    subtextos = particionar_en_subtextos(c_limpio, longitud_clave)
    
    mejores_letras_clave = []
    detalle_columnas = []
    
    for idx_col, subtexto in enumerate(subtextos):
        candidatos = resolver_clave_para_columna(subtexto)
        mejor_candidato = candidatos[0]
        mejores_letras_clave.append(mejor_candidato['letter'])
        
        detalle_columnas.append({
            'column_index': idx_col,
            'coset_length': len(subtexto),
            'coset_sample': subtexto[:30] + ("..." if len(subtexto) > 30 else ""),
            'best_letter': mejor_candidato['letter'],
            'best_chi2': mejor_candidato['chi2'],
            'candidates_ranking': candidatos[:5]  # Top 5 candidatos
        })
        
    clave_reconstruida = "".join(mejores_letras_clave)
    
    return {
        'key_length': longitud_clave,
        'recovered_key': clave_reconstruida,
        'columns': detalle_columnas
    }


# --- Alias para compatibilidad hacia atrás ---
score_shift_chi_squared = calcular_discrepancia_chi_cuadrado
solve_key_for_column = resolver_clave_para_columna
recover_vigenere_key = deducir_clave_por_frecuencias

