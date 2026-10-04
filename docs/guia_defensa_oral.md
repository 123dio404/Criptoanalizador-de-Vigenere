# GUÍA DE DEFENSA ORAL Y CONTROL ANTI-IA (15 PUNTOS)
## Criptoanalizador de Vigenère — ELC107 (Grupo C)

Este documento te prepara para defender tu proyecto con total solvencia ante el docente, demostrando dominio matemático y técnico del código fuente.

---

## 1. Preguntas Frecuentes del Docente y Cómo Responderlas

### P1: ¿Por qué funciona el Test de Kasiski? ¿Cuál es el principio matemático?
> **Respuesta:**  
> "El cifrado de Vigenère reutiliza periódicamente una clave de longitud $m$. Si en el texto en claro una palabra o secuencia de letras (como 'QUE', 'DEL' o 'PROFUNDO') aparece dos veces en posiciones separadas por una distancia $\Delta$, y por azar o estructura del texto esa distancia es un múltiplo exacto de la longitud de la clave ($\Delta = k \cdot m$), entonces ambas apariciones del texto claro se cifran con exactamente los mismos caracteres de la clave.  
> Esto genera secuencias idénticas en el criptograma. Por tanto, la distancia entre apariciones debe ser divisible por la longitud de la clave. Al factorizar todas las distancias halladas, el factor común con mayor frecuencia de repetición revela la longitud más probable de la clave."

---

### P2: ¿Por qué en la tabla del Índice de Coincidencia (IC) también da un valor alto en $k = 6$ si la clave es de longitud 3 ("MAR")?
> **Respuesta:**  
> "Porque 6 es un múltiplo de 3 ($6 = 2 \times 3$). Al particionar el texto en 6 columnas, los caracteres de la columna 0 y de la columna 3 siguen correspondiendo a la misma letra de la clave ('M'). Cada una de las 6 columnas sigue siendo un cifrado monoalfabético César puro, por lo que su IC individual sigue siendo alto (~0.074).  
> Sin embargo, la longitud fundamental es $k = 3$, porque es el menor periodo que dispara el IC y coincide con el divisor dominante del Test de Kasiski (donde el factor 3 obtuvo más de 70 votos vs 20 del factor 6)."

---

### P3: ¿Por qué el IC del español natural es ~0.074 mientras que el texto aleatorio es ~0.038?
> **Respuesta:**  
> "El Índice de Coincidencia representa la probabilidad de que dos letras elegidas al azar sean iguales:
> $$IC = \frac{\sum f_i (f_i - 1)}{N(N - 1)}$$  
> En una distribución uniforme (aleatoria de 26 letras), todas las letras tienen probabilidad $1/26 \approx 0.0385$.  
> En cambio, en el idioma español la distribución es fuertemente no uniforme: letras como la 'E' (13.6%), 'A' (12.5%) y 'O' (8.6%) concentran gran parte del texto. La suma de las probabilidades al cuadrado $\sum p_i^2$ en español asciende a aproximadamente $0.0740$."

---

### P4: ¿Por qué una traslación monoalfabética (César) no altera el Índice de Coincidencia?
> **Respuesta:**  
> "Porque el cifrado César solo traslada las posiciones de las frecuencias cíclicamente, pero el conjunto de conteos $\{f_A, f_B, \dots, f_Z\}$ sigue siendo idéntico, solo que reordenado. Como la fórmula del IC suma sobre todos los caracteres posibles independientemente del orden, el resultado es estrictamente invariante ante desplazamientos monoalfabéticos."

---

### P5: ¿Cómo recupera tu código cada letra de la clave en `models/frequency.py`?
> **Respuesta:**  
> "Una vez conocida la longitud $m=3$, dividimos el criptograma en 3 columnas o cosets. Cada columna es un cifrado César independiente.  
> Para cada columna, probamos los 26 desplazamientos posibles $s \in \{0, \dots, 25\}$. Desplazamos las letras de la columna hacia atrás y calculamos el estadístico de bondad de ajuste Chi-Cuadrado ($\chi^2$):
> $$\chi^2 = \sum_{i=A}^{Z} \frac{(O_i - E_i)^2}{E_i}$$  
> Donde $O_i$ es la frecuencia observada en el texto descifrado tentativo y $E_i = N \cdot P_{esp}(i)$ es la frecuencia teórica esperada en español. El desplazamiento que obtiene el menor valor de $\chi^2$ minimiza el error y corresponde a la letra correcta de la clave."

---

## 2. Mapa Rápido del Código Fuente (Para Mostrar en Vivo)

| Módulo | Archivo | Función Principal que debes abrir y explicar |
| :--- | :--- | :--- |
| **Cifrador/Descifrador** | [vigenere.py](file:///home/ovando/Projects/criptoanalizador/models/vigenere.py) | `cifrar_vigenere()` y `descifrar_vigenere()`: muestran la suma y resta modular mod 26. |
| **Kasiski** | [kasiski.py](file:///home/ovando/Projects/criptoanalizador/models/kasiski.py) | `buscar_secuencias_repetidas()` y `ejecutar_examen_kasiski()`: recorre trigramas, mide distancias y factoriza divisores. |
| **Friedman (IC)** | [friedman.py](file:///home/ovando/Projects/criptoanalizador/models/friedman.py) | `calcular_indice_coincidencia()` y `particionar_en_subtextos()`: calcula el numerador $\sum f_i(f_i-1)$ y promedia por cosets. |
| **Frecuencias / Chi²** | [frequency.py](file:///home/ovando/Projects/criptoanalizador/models/frequency.py) | `calcular_discrepancia_chi_cuadrado()` y `deducir_clave_por_frecuencias()`: prueba los 26 desplazamientos evaluando $\sum (O-E)^2/E$. |
| **Orquestador** | [analyzer.py](file:///home/ovando/Projects/criptoanalizador/models/analyzer.py) | `ejecutar_analisis_completo()` de `CriptoanalizadorVigenere`: conecta el pipeline completo y genera la bitácora. |


---

## 3. Consejos para la Demostración en Vivo
1. Ejecuta la aplicación:
   ```bash
   python3 main.py
   ```
2. En la pestaña 1, haz clic en **"Cargar Caso de Prueba"**.
3. Haz clic en **"Enviar Criptograma a Análisis Completo"**.
4. La ventana saltará automáticamente a la **Pestaña 2 (Kasiski)**:
   - Señala al docente la tabla de trigramas repetidos (`NUA`, `GDO`, `DOW`, etc.) y muéstrale que las distancias (27, 57, 105, 132) son todas múltiplos de 3.
   - Señala el histograma de factores donde el factor 3 tiene **72 votos**.
5. Pasa a la **Pestaña 3 (Índice de Coincidencia)**:
   - Muestra que en $k=1$ el IC es bajo (0.0476), y en $k=3$ salta a **0.0729** (resaltado en verde).
6. Pasa a la **Pestaña 4 (Análisis de Frecuencias)**:
   - Muestra las letras recuperadas `[ M ] [ A ] [ R ]`.
   - Selecciona la Columna 1 para mostrarle cómo el desplazamiento 12 minimiza $\chi^2$ (valor mínimo absoluto).
7. Pasa a la **Pestaña 5 (Descifrado y Trazabilidad)**:
   - Muestra el texto plano completamente recuperado que inicia con *"SOLA O SER PROFUNDO..."*.
   - Muestra la traza paso a paso lista para auditar.
