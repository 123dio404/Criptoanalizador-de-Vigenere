from collections import Counter
from typing import Dict, List, Tuple, Any
from models.spanish_freq import ALFABETO_ESP_26, PROBABILIDADES_ESP
from models.friedman import particionar_en_subtextos
from models.vigenere import LETRA_A_INDICE, INDICE_A_LETRA


def calcular_discrepancia_chi_cuadrado(subtexto: str, desplazamiento: int) -> Tuple[float, float]:
    n = len(subtexto)
    if n == 0:
        return float('inf'), 0.0

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

        if esperado > 0:
            diff = observado - esperado
            chi2 += (diff * diff) / esperado

        correlacion += (observado / n) * prob_esperada

    return chi2, correlacion


def resolver_clave_para_columna(subtexto: str) -> List[Dict[str, Any]]:
    resultados = []

    for desplazamiento in range(26):
        letra = INDICE_A_LETRA[desplazamiento]
        chi2, corr = calcular_discrepancia_chi_cuadrado(subtexto, desplazamiento)
        resultados.append({
            'shift': desplazamiento,
            'letter': letra,
            'chi2': chi2,
            'correlation': corr
        })

    resultados.sort(key=lambda x: (x['chi2'], -x['correlation']))
    for r in resultados:
        r['chi2'] = round(r['chi2'], 2)
        r['correlation'] = round(r['correlation'], 4)
    return resultados


def deducir_clave_por_frecuencias(criptograma: str, longitud_clave: int) -> Dict[str, Any]:
    if longitud_clave < 1:
        raise ValueError("La longitud de la clave debe ser al menos 1.")
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
            'coset': subtexto,
            'coset_length': len(subtexto),
            'coset_sample': subtexto[:30] + ("..." if len(subtexto) > 30 else ""),
            'best_letter': mejor_candidato['letter'],
            'best_chi2': mejor_candidato['chi2'],
            'candidates_ranking': candidatos[:5],
            'full_ranking': candidatos
        })

    clave_reconstruida = "".join(mejores_letras_clave)

    return {
        'key_length': longitud_clave,
        'recovered_key': clave_reconstruida,
        'columns': detalle_columnas
    }
