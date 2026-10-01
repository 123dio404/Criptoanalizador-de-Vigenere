# Criptoanalizador de Vigenère — ELC107 (Grupo C)
**Universidad Autónoma Gabriel René Moreno (UAGRM)**  
**Facultad de Ciencias de la Computación y Telecomunicaciones**  
**Materia:** ELC107 Criptografía y Seguridad  
**Proyecto 1:** Criptoanalizador de Vigenère (Test de Kasiski + Índice de Coincidencia de Friedman + Chi-Cuadrado $\chi^2$)

---

## Descripción del Proyecto

Aplicación académica y profesional desarrollada en **Python** con interfaz gráfica en **PyQt5** para interceptar, analizar y quebrar criptogramas generados mediante el cifrado polialfabético de Vigenère.

El sistema implementa de forma nativa (en código propio y sin librerías externas de criptografía) los tres pilares del criptoanálisis clásico:
1. **Test de Kasiski (1863):** Detección de $n$-gramas repetidos (trigramas), cálculo de distancias $\Delta$ entre apariciones y descomposición en factores para deducir la longitud de clave $m$.
2. **Índice de Coincidencia de Friedman (1922):** Partición en $k$ subtextos o cosets ($C_0, C_1, \dots, C_{k-1}$) y cálculo del $IC$ promedio frente al valor de referencia del español ($IC \approx 0.0740$) vs aleatorio ($IC \approx 0.0385$).
3. **Análisis de Frecuencias por Chi-Cuadrado ($\chi^2$):** Reducción a $m$ problemas de sustitución monoalfabética César y resolución letra por letra de la palabra clave minimizando la discrepancia cuadrática respecto al perfil fonético del idioma español.

---

## Requisitos y Ejecución

### Requisitos:
- **Python 3.10+** (Probado en Python 3.12)
- **PyQt5** (`pip install PyQt5` o ya instalado en el sistema)

### Ejecución de la Aplicación Gráfica:
```bash
python3 main.py
```

### Ejecución de las Pruebas Automatizadas (Validación Caso Docente):
```bash
python3 -m unittest tests/test_caso_docente.py -v
```

---

## Validación del Caso de Prueba Oficial (Grupo C)

* **Texto Claro:** `"SOLA O SER PROFUNDO EN EL SILENCIO DE LA NOCHE..."`
* **Clave de Prueba:** `"MAR"` (longitud $m = 3$)
* **Resultados Obtenidos:**
  * **Test de Kasiski:** Identificación de 56 trigramas repetidos con el factor 3 como divisor dominante con más de 70 votos.
  * **Índice de Coincidencia:** 
    * Periodo $k=1$: $IC \approx 0.0476$ (comportamiento polialfabético aplanado).
    * Periodo $k=3$: $IC \approx 0.0729$ (**pico que coincide con el español natural**).
  * **Recuperación de Clave ($\chi^2$):** Identificación exacta de la palabra clave `M - A - R`.
  * **Descifrado:** Reconstrucción 100% íntegra del texto plano original.

---

## Estructura del Proyecto

```
criptoanalizador/
├── core/                     # LÓGICA MATEMÁTICA PURA (Sin librerías externas)
│   ├── __init__.py
│   ├── vigenere.py          # Cifrado/Descifrado Vigenère y normalización
│   ├── kasiski.py           # Detección de trigramas, cálculo de distancias y divisores
│   ├── friedman.py          # Cálculo de IC global y por partición de cosets
│   ├── frequency.py         # Análisis de frecuencias por columnas (Chi-cuadrado)
│   └── analyzer.py          # Orquestador del flujo de criptoanálisis
├── data/
│   ├── __init__.py
│   └── spanish_freq.py      # Frecuencias oficiales de monogramas en español (RAE)
├── gui/                      # INTERFAZ GRÁFICA MODERNA (PyQt5)
│   ├── __init__.py
│   ├── styles.py            # Hoja de estilos (Tema Slate / Dark)
│   ├── tab_cifrador.py      # Cifrado, descifrado y carga rápida de prueba
│   ├── tab_kasiski.py       # Visualización de trigramas, distancias y factores
│   ├── tab_friedman.py      # Gráficas y tablas de periodos vs IC
│   ├── tab_frecuencias.py   # Deducción interactiva de cada letra de la clave
│   ├── tab_descifrado.py    # Descifrado final y exportador de trazas
│   └── main_window.py       # Ventana principal integradora
├── tests/
│   ├── __init__.py
│   └── test_caso_docente.py # Tests unitarios que validan el caso obligatorio
├── docs/
│   ├── plantilla_informe.md # Borrador completo del informe académico en PDF
│   └── guia_defensa_oral.md # Preguntas frecuentes y justificación matemática
├── main.py                   # Script de inicio
└── README.md                 # Documentación técnica
```

---

## Fundamentos Matemáticos

### 1. Test de Kasiski
$$\Delta = pos_2 - pos_1 = k \cdot m \implies m \mid \Delta$$
Si un trigrama claro se repite a una distancia que es múltiplo de la longitud de la clave $m$, coincidirá con las mismas letras de la clave y generará el mismo criptograma.

### 2. Índice de Coincidencia (Friedman)
$$IC = \frac{\sum_{i=A}^{Z} f_i (f_i - 1)}{N (N - 1)}$$
* Español: $IC \approx 0.0740$
* Uniforme / Aleatorio: $IC \approx 1/26 \approx 0.0385$

### 3. Prueba de Chi-Cuadrado ($\chi^2$)
$$\chi^2(s) = \sum_{i=A}^{Z} \frac{(O_i - E_i)^2}{E_i}$$
Donde $O_i$ son las frecuencias observadas al desplazar el subtexto por $s$, y $E_i = N \cdot P_{esp}(i)$ son las frecuencias esperadas en español. El valor $s$ que minimiza $\chi^2$ es la letra de la clave.
