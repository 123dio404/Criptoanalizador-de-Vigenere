"""
data/spanish_freq.py
Frecuencias estadísticas de letras en el idioma español (monogramas)
basadas en análisis de corpus de la Real Academia Española (RAE) y literatura clásica.
Índice de Coincidencia teórico esperado en español: ~0.074.
Texto aleatorio (equiprobable): 1 / 26 ≈ 0.03846.
"""

# Frecuencias porcentuales típicas del español (suman ~100%)
# Fuente: RAE / Frecuencias estándar para criptoanálisis
SPANISH_FREQUENCIES_26 = {
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

# Alfabeto estándar de 26 letras
ALPHABET_26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Frecuencias relativas normalizadas (0.0 a 1.0)
SPANISH_PROBABILITIES_26 = {
    letter: SPANISH_FREQUENCIES_26[letter] / 100.0
    for letter in ALPHABET_26
}

# Índice de coincidencia teórico esperado para español e inglés
IC_THEORETICAL_SPANISH = 0.0740
IC_THEORETICAL_ENGLISH = 0.0667
IC_THEORETICAL_RANDOM = 1.0 / 26.0  # ~0.03846
