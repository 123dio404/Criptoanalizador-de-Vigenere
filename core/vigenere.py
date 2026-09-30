"""
core/vigenere.py
Implementación del Cifrado de Vigenère y utilidades de normalización lingüística.
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.

Fundamento Matemático:
Sea el alfabeto Z_26 = {0, 1, ..., 25} correspondiente a {A, B, ..., Z}.
Dada una clave K = (k_0, k_1, ..., k_{m-1}) de longitud m,
y un texto claro P = (p_0, p_1, ..., p_{n-1}):

Cifrado:
    c_i = (p_i + k_{i mod m}) mod 26

Descifrado:
    p_i = (c_i - k_{i mod m}) mod 26
"""

import unicodedata
from data.spanish_freq import ALPHABET_26

CHAR_TO_INDEX = {char: idx for idx, char in enumerate(ALPHABET_26)}
INDEX_TO_CHAR = {idx: char for idx, char in enumerate(ALPHABET_26)}


def normalize_text(text: str, keep_spaces: bool = False) -> str:
    """
    Normaliza el texto de entrada:
    - Convierte a mayúsculas.
    - Elimina acentos y diéresis (Á->A, É->E, Ñ->N si alfabeto 26).
    - Remueve caracteres no alfabéticos si keep_spaces es False.
    """
    if not text:
        return ""
    
    # Normalización Unicode NFD para separar caracteres de sus tildes/marcas
    text_upper = text.upper()
    
    # Reemplazo explícito común en español antes de desmontar acentos
    text_upper = text_upper.replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
    text_upper = text_upper.replace('Ó', 'O').replace('Ú', 'U').replace('Ü', 'U')
    text_upper = text_upper.replace('Ñ', 'N')  # Para estándar Z_26
    
    # Descomposición canónica
    nfkd_form = unicodedata.normalize('NFKD', text_upper)
    cleaned = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    result = []
    for char in cleaned:
        if char in CHAR_TO_INDEX:
            result.append(char)
        elif keep_spaces and char.isspace():
            result.append(" ")
            
    return "".join(result)


def encrypt(plaintext: str, key: str) -> str:
    """
    Cifra un texto plano usando el cifrado de Vigenère con alfabeto A-Z (Z_26).
    
    Parámetros:
        plaintext: Texto a cifrar (puede contener espacios o minúsculas).
        key: Clave alfabética.
        
    Retorna:
        Texto cifrado (solo letras mayúsculas A-Z).
    """
    clean_p = normalize_text(plaintext, keep_spaces=False)
    clean_k = normalize_text(key, keep_spaces=False)
    
    if not clean_k:
        raise ValueError("La clave no puede estar vacía.")
    if not clean_p:
        return ""
    
    m = len(clean_k)
    key_indices = [CHAR_TO_INDEX[c] for c in clean_k]
    
    ciphertext = []
    for i, p_char in enumerate(clean_p):
        p_val = CHAR_TO_INDEX[p_char]
        k_val = key_indices[i % m]
        c_val = (p_val + k_val) % 26
        ciphertext.append(INDEX_TO_CHAR[c_val])
        
    return "".join(ciphertext)


def decrypt(ciphertext: str, key: str) -> str:
    """
    Descifra un criptograma usando el cifrado de Vigenère con alfabeto A-Z (Z_26).
    
    Parámetros:
        ciphertext: Texto cifrado.
        key: Clave alfabética estimada o confirmada.
        
    Retorna:
        Texto plano descifrado (mayúsculas A-Z).
    """
    clean_c = normalize_text(ciphertext, keep_spaces=False)
    clean_k = normalize_text(key, keep_spaces=False)
    
    if not clean_k:
        raise ValueError("La clave no puede estar vacía.")
    if not clean_c:
        return ""
    
    m = len(clean_k)
    key_indices = [CHAR_TO_INDEX[c] for c in clean_k]
    
    plaintext = []
    for i, c_char in enumerate(clean_c):
        c_val = CHAR_TO_INDEX[c_char]
        k_val = key_indices[i % m]
        p_val = (c_val - k_val) % 26
        plaintext.append(INDEX_TO_CHAR[p_val])
        
    return "".join(plaintext)
