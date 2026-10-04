"""
controllers/formateo.py
Convierte los resultados del modelo en filas/textos listos para que las vistas los dibujen.
Son funciones puras (sin PyQt) para poder probarlas sin interfaz gráfica.
"""

from typing import Any, Dict, List, Sequence, Tuple

from models.spanish_freq import IC_TEORICO_ALEATORIO, IC_TEORICO_ESP

UMBRAL_PICO_IC = 0.065
LARGO_BARRA_KASISKI = 10
LARGO_BARRA_FRIEDMAN = 20


# --------------------------------------------------------------------------- Kasiski
def resumen_kasiski(kasiski: Dict[str, Any]) -> Tuple[str, str, str]:
    candidatos = kasiski.get('top_key_lengths', [])
    if candidatos:
        m, votos = candidatos[0]
        dominante = f"Divisor Dominante: m = {m} ({votos} votos)"
    else:
        dominante = "Divisor Dominante: No concluyente"
    return (
        f"N-Gramas Repetidos: {len(kasiski.get('repeated_ngrams', []))}",
        f"Distancias Calculadas: {len(kasiski.get('all_distances', []))}",
        dominante,
    )


def filas_ngramas(kasiski: Dict[str, Any]) -> List[Dict[str, str]]:
    filas = []
    for i, item in enumerate(kasiski.get('repeated_ngrams', []), start=1):
        comunes = item['common_factors']
        filas.append({
            'indice': str(i),
            'ngrama': item['ngram'],
            'longitud': str(item['length']),
            'apariciones': str(item['count']),
            'posiciones': str(item['positions']),
            'distancias': str(item['distances']),
            'factores': str(comunes) if comunes else "—",
            'factores_tooltip': (
                f"Divisores comunes a todas las distancias (MCD = {item['gcd']}): {comunes}\n"
                f"Todos los divisores individuales: {item['factors']}"
                if comunes else
                f"Sin factor común (MCD = {item['gcd']}): posible coincidencia fortuita.\n"
                f"Divisores individuales: {item['factors']}"
            ),
        })
    return filas


def _evaluar_candidato(fila: int, m: int, principal: int) -> str:
    if fila == 0:
        return "CANDIDATO PRINCIPAL"
    if m % principal == 0:
        return "Múltiplo del principal"
    if principal % m == 0:
        return "Divisor del principal"
    return "Candidato secundario" if fila < 3 else "Baja probabilidad"


def filas_factores(kasiski: Dict[str, Any]) -> List[Dict[str, Any]]:
    ranking: Sequence[Tuple[int, int]] = kasiski.get('top_key_lengths', [])
    if not ranking:
        return []
    principal, max_votos = ranking[0]
    filas = []
    for i, (m, votos) in enumerate(ranking):
        barra = "█" * max(1, round(votos / max_votos * LARGO_BARRA_KASISKI)) + f" ({votos})"
        filas.append({
            'indice': str(i + 1),
            'candidata': f"m = {m}",
            'votos': str(votos),
            'barra': barra,
            'evaluacion': _evaluar_candidato(i, m, principal),
            'principal': i == 0,
        })
    return filas


# --------------------------------------------------------------------------- Friedman
def textos_referencia_friedman() -> Tuple[str, str]:
    return (
        f"IC Teórico Español: {IC_TEORICO_ESP:.4f}",
        f"IC Aleatorio (1/26): {IC_TEORICO_ALEATORIO:.4f}",
    )


def metricas_friedman(friedman: Dict[str, Any]) -> Tuple[str, str]:
    estimacion = friedman.get('friedman_formula_estimate')
    return (
        f"IC Global del Criptograma: {friedman.get('global_ic', 0.0):.4f}",
        f"Estimación directa Friedman: m ≈ {estimacion}" if estimacion
        else "Estimación directa Friedman: N/A",
    )


def titulo_tabla_periodos(friedman: Dict[str, Any]) -> str:
    periodos = friedman.get('periods_data', [])
    if not periodos:
        return "Evaluación del Índice de Coincidencia por Periodo Candidato"
    return (
        "Evaluación del Índice de Coincidencia por Periodo Candidato "
        f"(k = {periodos[0]['period']} .. {periodos[-1]['period']})"
    )


def filas_periodos(friedman: Dict[str, Any]) -> List[Dict[str, Any]]:
    mejor = friedman.get('best_period_by_ic', 1)
    filas = []
    for i, p in enumerate(friedman.get('periods_data', []), start=1):
        k, ic = p['period'], p['average_ic']
        ratio = max(0.0, min(1.0, (ic - IC_TEORICO_ALEATORIO) / (IC_TEORICO_ESP - IC_TEORICO_ALEATORIO)))
        barra = "█" * int(ratio * LARGO_BARRA_FRIEDMAN) + f" {int(ratio * 100)}%"

        if k == mejor:
            diagnostico, pico = "PICO MÁXIMO (Longitud de Clave Recomendada)", True
        elif ic >= UMBRAL_PICO_IC and k % mejor == 0:
            diagnostico, pico = "Pico Secundario (Múltiplo de la Clave)", True
        elif ic >= UMBRAL_PICO_IC:
            diagnostico, pico = "IC elevado (no múltiplo del periodo recomendado)", True
        else:
            diagnostico, pico = "Polialfabético (Subtextos mezclados)", False

        filas.append({
            'indice': str(i),
            'periodo': f"k = {k}",
            'ic': f"{ic:.4f}",
            'delta': f"{p['delta_to_spanish']:.4f}",
            'barra': barra,
            'diagnostico': diagnostico,
            'pico': pico,
        })
    return filas


# --------------------------------------------------------------------------- Frecuencias χ²
def texto_clave_columna(letra: str, indice: int) -> str:
    return f"Columna #{indice + 1} (Posición {indice}) -> Letra sugerida: '{letra}'"


def etiquetas_columnas(clave: str, longitud: int) -> List[str]:
    return [texto_clave_columna(clave[i] if i < len(clave) else "?", i) for i in range(longitud)]


def info_columna(columna: Dict[str, Any]) -> str:
    coset = columna['coset']
    muestra = coset[:18] + ("..." if len(coset) > 18 else "")
    return f"Subtexto: {len(coset)} letras | Muestra: {muestra}"


def filas_candidatas(columna: Dict[str, Any]) -> List[Dict[str, Any]]:
    filas = []
    for i, c in enumerate(columna['full_ranking']):
        filas.append({
            'letra': c['letter'],
            'desplazamiento': f"{c['shift']} ('{c['letter']}')",
            'chi2': f"{c['chi2']:.2f}",
            'correlacion': f"{c['correlation']:.4f}",
            'ranking': f"#{i + 1}" + (" (ÓPTIMO)" if i == 0 else ""),
            'optimo': i == 0,
        })
    return filas


# --------------------------------------------------------------------------- Traza
def construir_traza(criptograma: str, texto_plano: str, clave: str, eventos: Sequence[str]) -> str:
    lineas = [
        "==================================================================",
        "   EVIDENCIA Y TRAZA DE CRIPTOANÁLISIS DE VIGENÈRE (ELC107)",
        "==================================================================",
        f"Longitud del Criptograma Interceptado: {len(criptograma)} caracteres",
        f"Clave Recuperada Final: {clave} (m = {len(clave)})",
        "",
        "--- REGISTRO DE EVENTOS Y PASOS DE EJECUCIÓN ---",
        *eventos,
        "",
        "--- MUESTRA DEL TEXTO DESCIFRADO ---",
        texto_plano[:200] + ("..." if len(texto_plano) > 200 else ""),
        "==================================================================",
    ]
    return "\n".join(lineas)
