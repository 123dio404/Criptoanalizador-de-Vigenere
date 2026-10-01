"""
data/spanish_freq.py
Frecuencias estadísticas de letras en el idioma español (monogramas)
basadas en análisis de corpus de la Real Academia Española (RAE) y literatura clásica.
Índice de Coincidencia teórico esperado en español: ~0.074.
Texto aleatorio (equiprobable): 1 / 26 ≈ 0.03846.
"""

# Frecuencias porcentuales típicas del español (suman ~100%)
# Fuente: RAE / Frecuencias estándar para criptoanálisis
FRECUENCIAS_PORCENTUALES_ESP = {
    'A': 12.53,
    'B': 1.42,
    'C': 4.68,
    'D': 5.86,
    'E': 13.68,
    'F': 0.69,
    'G': 1.01,
    'H': 0.70,
    'I': 6.25,
    'J': 0.44,
    'K': 0.02,
    'L': 4.97,
    'M': 3.15,
    'N': 6.71,
    'O': 8.68,
    'P': 2.51,
    'Q': 0.88,
    'R': 6.87,
    'S': 7.98,
    'T': 4.63,
    'U': 3.93,
    'V': 0.90,
    'W': 0.01,
    'X': 0.22,
    'Y': 0.90,
    'Z': 0.52
}

# Alfabeto estándar de 26 letras (A-Z)
ALFABETO_ESP_26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Frecuencias relativas normalizadas (0.0 a 1.0)
PROBABILIDADES_ESP = {
    letra: FRECUENCIAS_PORCENTUALES_ESP[letra] / 100.0
    for letra in ALFABETO_ESP_26
}

# Índice de coincidencia teórico esperado para español, inglés y aleatorio
IC_TEORICO_ESP = 0.0740
IC_TEORICO_INGLES = 0.0667
IC_TEORICO_ALEATORIO = 1.0 / 26.0  # ~0.03846

# --- Alias para mantener compatibilidad ---
ALPHABET_26 = ALFABETO_ESP_26
SPANISH_FREQUENCIES_26 = FRECUENCIAS_PORCENTUALES_ESP
SPANISH_PROBABILITIES_26 = PROBABILIDADES_ESP
IC_THEORETICAL_SPANISH = IC_TEORICO_ESP
IC_THEORETICAL_ENGLISH = IC_TEORICO_INGLES
IC_THEORETICAL_RANDOM = IC_TEORICO_ALEATORIO

