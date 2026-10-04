"""
models/vigenere.py
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
from collections import Counter
from typing import Dict, List, Tuple

from models.spanish_freq import ALFABETO_ESP_26

LETRA_A_INDICE = {char: idx for idx, char in enumerate(ALFABETO_ESP_26)}
INDICE_A_LETRA = {idx: char for idx, char in enumerate(ALFABETO_ESP_26)}


def normalizar_texto(texto: str, mantener_espacios: bool = False) -> str:
    """
    Normaliza el texto de entrada:
    - Convierte a mayúsculas.
    - Elimina acentos y diéresis (Á->A, É->E, Ñ->N para estándar Z_26).
    - Remueve caracteres no alfabéticos si mantener_espacios es False.
    """
    if not texto:
        return ""
    
    # Normalización Unicode NFD para separar caracteres de sus tildes/marcas
    texto_mayus = texto.upper()
    
    # Reemplazo explícito común en español antes de desmontar acentos
    texto_mayus = texto_mayus.replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
    texto_mayus = texto_mayus.replace('Ó', 'O').replace('Ú', 'U').replace('Ü', 'U')
    texto_mayus = texto_mayus.replace('Ñ', 'N')
    
    # Descomposición canónica
    forma_nfkd = unicodedata.normalize('NFKD', texto_mayus)
    limpio = "".join([c for c in forma_nfkd if not unicodedata.combining(c)])
    
    resultado = []
    for char in limpio:
        if char in LETRA_A_INDICE:
            resultado.append(char)
        elif mantener_espacios and char.isspace():
            resultado.append(" ")
            
    return "".join(resultado)


def contar_intersecciones(texto_claro: str, clave: str, conservar_formato: bool = False) -> Dict[Tuple[str, str], int]:
    """
    Cuenta cuántas veces se usa cada cruce (letra_clave, letra_clara) al cifrar el texto.
    La letra clara es la columna de la tabla y la letra clave es la fila.
    """
    k_limpia = normalizar_texto(clave, mantener_espacios=False)
    if not k_limpia or not texto_claro:
        return {}

    if conservar_formato:
        letras = [ch.upper() for ch in texto_claro if ch.isascii() and ch.upper() in LETRA_A_INDICE]
    else:
        letras = list(normalizar_texto(texto_claro, mantener_espacios=False))

    pares = ((k_limpia[i % len(k_limpia)], letra) for i, letra in enumerate(letras))
    return dict(Counter(pares))


def generar_tabla_vigenere() -> List[str]:
    """
    Tabla (tabula recta) de Vigenère: la fila k es el alfabeto desplazado k posiciones.
    tabla[k][p] es la letra cifrada de la letra clara p con la letra clave k.
    """
    return [ALFABETO_ESP_26[k:] + ALFABETO_ESP_26[:k] for k in range(26)]


def _desplazar_conservando_formato(texto: str, clave: str, signo: int) -> str:
    """
    Aplica Vigenère solo a las letras A-Z / a-z, respetando mayúsculas y minúsculas.
    Espacios, signos, dígitos y letras acentuadas o 'ñ' se copian tal cual y no
    consumen posición de la clave (así el descifrado es exactamente reversible).
    """
    k_limpia = normalizar_texto(clave, mantener_espacios=False)
    if not k_limpia:
        raise ValueError("La clave no puede estar vacía.")

    indices_clave = [LETRA_A_INDICE[c] for c in k_limpia]
    m = len(indices_clave)
    resultado = []
    pos_clave = 0
    for ch in texto:
        mayus = ch.upper()
        if ch.isascii() and mayus in LETRA_A_INDICE:
            valor = (LETRA_A_INDICE[mayus] + signo * indices_clave[pos_clave % m]) % 26
            nueva = INDICE_A_LETRA[valor]
            resultado.append(nueva if ch.isupper() else nueva.lower())
            pos_clave += 1
        else:
            resultado.append(ch)
    return "".join(resultado)


def cifrar_vigenere(texto_plano: str, clave: str, conservar_formato: bool = False) -> str:
    """
    Cifra un texto plano usando el cifrado de Vigenère con alfabeto A-Z (Z_26).
    
    Fórmula modular:
        c_i = (p_i + k_{i mod m}) mod 26
        
    Parámetros:
        texto_plano: Texto a cifrar (puede contener espacios o minúsculas).
        clave: Clave alfabética.
        conservar_formato: si es True se respetan espacios, signos y mayúsculas/minúsculas.
        
    Retorna:
        Texto cifrado (solo letras mayúsculas A-Z, salvo con conservar_formato).
    """
    if conservar_formato:
        return _desplazar_conservando_formato(texto_plano, clave, +1)

    p_limpio = normalizar_texto(texto_plano, mantener_espacios=False)
    k_limpia = normalizar_texto(clave, mantener_espacios=False)
    
    if not k_limpia:
        raise ValueError("La clave no puede estar vacía.")
    if not p_limpio:
        return ""
    
    m = len(k_limpia)
    indices_clave = [LETRA_A_INDICE[c] for c in k_limpia]
    
    criptograma = []
    for i, p_char in enumerate(p_limpio):
        p_val = LETRA_A_INDICE[p_char]
        k_val = indices_clave[i % m]
        c_val = (p_val + k_val) % 26
        criptograma.append(INDICE_A_LETRA[c_val])
        
    return "".join(criptograma)


def descifrar_vigenere(criptograma: str, clave: str, conservar_formato: bool = False) -> str:
    """
    Descifra un criptograma usando el cifrado de Vigenère con alfabeto A-Z (Z_26).
    
    Fórmula modular:
        p_i = (c_i - k_{i mod m}) mod 26
        
    Parámetros:
        criptograma: Texto cifrado.
        clave: Clave alfabética estimada o confirmada.
        conservar_formato: si es True se respetan espacios, signos y mayúsculas/minúsculas.
        
    Retorna:
        Texto plano descifrado (mayúsculas A-Z, salvo con conservar_formato).
    """
    if conservar_formato:
        return _desplazar_conservando_formato(criptograma, clave, -1)

    c_limpio = normalizar_texto(criptograma, mantener_espacios=False)
    k_limpia = normalizar_texto(clave, mantener_espacios=False)
    
    if not k_limpia:
        raise ValueError("La clave no puede estar vacía.")
    if not c_limpio:
        return ""
    
    m = len(k_limpia)
    indices_clave = [LETRA_A_INDICE[c] for c in k_limpia]
    
    texto_plano = []
    for i, c_char in enumerate(c_limpio):
        c_val = LETRA_A_INDICE[c_char]
        k_val = indices_clave[i % m]
        p_val = (c_val - k_val) % 26
        texto_plano.append(INDICE_A_LETRA[p_val])
        
    return "".join(texto_plano)
