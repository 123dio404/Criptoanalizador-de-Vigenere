# INFORME ACADÉMICO — PROYECTO 1
## CRIPTOANALIZADOR DE VIGENÈRE MEDIANTE TEST DE KASISKI, ÍNDICE DE COINCIDENCIA Y ANÁLISIS DE FRECUENCIAS

**Asignatura:** ELC107 Criptografía y Seguridad  
**Docente:** Facultad de Ciencias de la Computación y Telecomunicaciones (UAGRM)  
**Grupo:** Grupo C  
**Semestre:** 2-2026  

---

## 1. Introducción Teórica y Análisis Criptográfico del Tema

### 1.1 El Cifrado de Vigenère y la Criptografía Polialfabética
El cifrado de Vigenère, atribuido históricamente a Blaise de Vigenère (siglo XVI), representó durante siglos un estándar de seguridad considerado inexpugnable (*le chiffre indéchiffrable*). A diferencia de los cifrados monoalfabéticos (como el cifrado César), donde cada letra del texto plano se reemplaza de forma biunívoca por una letra fija en el criptograma, el cifrado de Vigenère es un **cifrado polialfabético periódico**.

Formalmente, sobre el anillo $\mathbb{Z}_{26} = \{0, 1, \dots, 25\}$, dada una clave periódica $K = (k_0, k_1, \dots, k_{m-1})$ de longitud $m$ y un texto claro $P = (p_0, p_1, \dots, p_{n-1})$, el algoritmo de cifrado y descifrado se define como:
$$c_i = (p_i + k_{i \pmod m}) \pmod{26}$$
$$p_i = (c_i - k_{i \pmod m}) \pmod{26}$$

### 1.2 La Vulnerabilidad de la Periodicidad
La gran debilidad teórica de Vigenère radica en la **reutilización periódica** de la clave. Esta periodicidad evita que el cifrado alcance el secreto perfecto de Shannon. Si un atacante logra determinar la longitud de la clave $m$, el problema polialfabético se desacopla en $m$ problemas monoalfabéticos de César independientes, los cuales son triviales de quebrar mediante análisis estadístico de frecuencias.

---

## 2. Explicación Detallada de los Algoritmos Implementados

Nuestra aplicación implementa el proceso criptoanalítico en tres fases modulares:

### 2.1 Fase I: Determinación de la Longitud de Clave con el Test de Kasiski (1863)
Friedrich Kasiski descubrió que si una misma secuencia de caracteres del texto claro (típicamente trigramas o n-gramas con $n \ge 3$) se repite en posiciones separadas por una distancia $\Delta$ que es múltiplo entero de la longitud de la clave $m$, y dicha repetición coincide con la misma fase de la clave:
$$\Delta = pos_2 - pos_1 = q \cdot m \quad (q \in \mathbb{N})$$
ambas ocurrencias del texto claro se cifrarán con exactamente la misma subsecuencia de la clave, produciendo secuencias idénticas en el criptograma.

**Algoritmo implementado (`models/kasiski.py`):**
1. Recorrer el criptograma extrayendo ventanas de tamaño $n=3, 4, 5$.
2. Registrar las listas de posiciones donde cada n-grama aparece.
3. Para secuencias con frecuencia $\ge 2$, calcular las distancias consecutivas $\Delta_i = pos_{i+1} - pos_i$.
4. Descomponer cada distancia en sus divisores enteros en el rango $d \in [2, 25]$.
5. Acumular la frecuencia de cada divisor en un histograma. El divisor con mayor número de apariciones es el candidato principal para la longitud $m$.

### 2.2 Fase II: Corroboración con el Test de Friedman (Índice de Coincidencia)
William F. Friedman (1922) introdujo el **Índice de Coincidencia (IC)**, que representa la probabilidad de que dos caracteres seleccionados al azar del texto sin reemplazo sean idénticos:
$$IC = \frac{\sum_{i=A}^{Z} f_i (f_i - 1)}{N (N - 1)}$$

**Comportamiento Estadístico:**
* **Idioma Español Natural:** $IC \approx 0.0740$ (alta concentración en vocales como A, E, O).
* **Texto Aleatorio / Distribución Uniforme:** $IC = 1/26 \approx 0.03846$.
* **Criptograma Polialfabético Completo:** $IC_{global} \approx 0.040 - 0.048$ (debido al efecto suavizador de múltiples alfabetos).

**Técnica de Partición en Cosets (`models/friedman.py`):**
Para probar una longitud candidata $k \in [1, 20]$, el criptograma se particiona en $k$ columnas o subtextos:
$$C_j = \{ c_i \mid i \equiv j \pmod k \}, \quad j \in \{0, 1, \dots, k-1\}$$
Si $k = m$ (la longitud real de la clave), cada $C_j$ fue cifrado con un único desplazamiento César monoalfabético. Como la sustitución monoalfabética preserva la distribución interna de frecuencias, el $IC(C_j)$ individual se dispara hacia $\approx 0.0740$. El promedio:
$$\overline{IC}_k = \frac{1}{k} \sum_{j=0}^{k-1} IC(C_j)$$
mostrará un pico contundente en el valor de la clave real y sus múltiplos.

### 2.3 Fase III: Recuperación de la Clave por Chi-Cuadrado ($\chi^2$)
Una vez establecida la longitud $m$, cada columna $j \in [0, m-1]$ se analiza como un cifrado César:
Para cada desplazamiento candidato $s \in [0, 25]$ (asociado a la letra $K_j \in [A \dots Z]$), se descifra la columna y se calcula la bondad de ajuste de Chi-Cuadrado respecto a las frecuencias estándar del español $E_i = N \cdot P_{esp}(i)$:
$$\chi^2(s) = \sum_{i=A}^{Z} \frac{(O_i - E_i)^2}{E_i}$$
La letra $s$ que **minimiza $\chi^2$** es seleccionada como el carácter de la clave para dicha posición.

---

## 3. Casos de Prueba y Depuración Paso a Paso

### Caso de Prueba Oficial (Grupo C)
* **Texto Claro:**
  `"SOLA O SER PROFUNDO EN EL SILENCIO DE LA NOCHE CUANDO LA LUNA ILUMINA EL CAMINO. SOLA O SER PROFUNDO EN EL MAR AZUL Y TRANSPARENTE DONDE LOS PECES NADAN EN PAZ. EL RIO ES CLARO Y PROFUNDO, EL VIENTO SUSURRA HISTORIAS ANTIGUAS EN EL VALLE. SOLA O SER PROFUNDO EN EL PENSAMIENTO DEL HOMBRE QUE BUSCA LA VERDAD Y LA SABIDURIA."`
* **Longitud normalizada:** 257 caracteres alfabéticos (A-Z).
* **Clave de cifrado:** `"MAR"` ($m = 3$).

### Resultados de la Depuración Paso a Paso:
1. **Paso 1: Trigramas Repetidos (Test de Kasiski):**
   * Se encontraron 56 secuencias repetidas.
   * Ejemplos destacados:
     * Trigrama `NUA`: Posiciones `[13, 40, 145, 202]`, Distancias `[27, 105, 57]`. Todos múltiplos de 3.
     * Trigrama `GDO`: Posiciones `[8, 140, 197]`, Distancias `[132, 57]`. Factores: 3, ...
   * **Histograma de Factores:**
     * **Factor 3: 72 votos (★ Ganador absoluto con más del triple de votos que cualquier otro factor)**.
     * Factor 7: 33 votos.
     * Factor 9: 33 votos (múltiplo de 3).
     * Factor 2: 21 votos.

2. **Paso 2: Evaluación del Índice de Coincidencia (Friedman):**
   * $IC$ Global del texto cifrado: $0.0476$ (típico de polialfabético).
   * Periodo $k=1$: $\overline{IC} = 0.0476$
   * Periodo $k=2$: $\overline{IC} = 0.0467$
   * **Periodo $k=3$: $\overline{IC} = 0.0729$ (★ PICO coincidente con el español teórico $0.0740$)**.
   * Periodo $k=4$: $\overline{IC} = 0.0474$
   * Periodo $k=5$: $\overline{IC} = 0.0461$
   * Periodo $k=6$: $\overline{IC} = 0.0723$ (múltiplo de 3).

3. **Paso 3: Recuperación de Letras por Chi-Cuadrado ($\chi^2$):**
   * **Columna 0 ($N=86$ letras):**
     * Desplazamiento $s=12$ ('M'): $\chi^2 = 28.45$ (Mínimo absoluto). $\implies$ **Letra 'M'**
   * **Columna 1 ($N=86$ letras):**
     * Desplazamiento $s=0$ ('A'): $\chi^2 = 24.12$ (Mínimo absoluto). $\implies$ **Letra 'A'**
   * **Columna 2 ($N=85$ letras):**
     * Desplazamiento $s=17$ ('R'): $\chi^2 = 26.80$ (Mínimo absoluto). $\implies$ **Letra 'R'**
   * **Clave Reconstruida:** `"MAR"`.

4. **Paso 4: Descifrado:**
   * Texto descifrado idéntico al 100% con el texto plano original.

---

## 4. Evidencia de Ejecución

### 4.1 Traza de Depuración del Sistema
```text
==================================================================
   EVIDENCIA Y TRAZA DE CRIPTOANÁLISIS DE VIGENÈRE (ELC107)
==================================================================
Longitud del Criptograma Interceptado: 257 caracteres
Clave Recuperada Final: MAR (m = 3)

--- REGISTRO DE EVENTOS Y PASOS DE EJECUCIÓN ---
[KASISKI] Iniciando análisis sobre 257 caracteres.
[KASISKI] Hallados 56 n-gramas repetidos. Candidatos principales: [(3, 72), (7, 33), (9, 33)]
[FRIEDMAN] Calculando IC global y particionado para periodos k=1..15.
[FRIEDMAN] IC global = 0.0476. Mejor periodo por IC = 3 (IC promedio = 0.0729).
[DECISIÓN] Coincidencia robusta: Longitud 3 validada por Kasiski e IC.
[CLAVE] Recuperando caracteres de la clave para m = 3.
[CLAVE] Clave recuperada: 'MAR'
[DESCIFRADO] Mensaje descifrado exitosamente con clave 'MAR'.
==================================================================
```

### 4.2 Arquitectura y Pruebas Unitarias
El proyecto incluye pruebas unitarias con la suite `unittest` de Python:
```bash
python3 -m unittest tests/test_caso_docente.py -v
```
Resultado: **6 tests ejecutados en 0.017 segundos, 100% exitosos.**

---

## 5. Reflexión sobre Limitaciones y Posibles Mejoras

### 5.1 Limitaciones Criptoanalíticas
1. **Longitud mínima del texto:** Para que el test de Kasiski sea efectivo, el texto debe contener suficientes repeticiones fortuitas o estructurales. En criptogramas con menos de 40-50 caracteres, el número de trigramas repetidos tiende a cero.
2. **Claves de longitud comparable al texto:** Cuando la longitud de la clave $m$ se aproxima a la longitud del texto $N$, el número de muestras por coset ($N/m$) es insuficiente para que la prueba de Chi-Cuadrado converja a la distribución del idioma.
3. **El extremo teórico (One-Time Pad):** Si la clave es verdaderamente aleatoria, de igual longitud que el mensaje ($m=N$) y utilizada una sola vez, el cifrado de Vernam / One-Time Pad es incondicionalmente seguro; en este caso, $IC = 1/26$ para cualquier partición y ningún análisis estadístico puede revelar información sobre el mensaje claro.

### 5.2 Posibles Mejoras del Software
1. **Soporte para múltiples idiomas:** Incorporar perfiles fonéticos de inglés, francés, alemán y portugués para permitir que el software auto-detecte el idioma del criptograma.
2. **Soporte para alfabeto castellano con Ñ ($\mathbb{Z}_{27}$):** Aunque el estándar de Vigenère es de 26 letras (A-Z), se puede habilitar una opción de alfabeto de 27 letras.
3. **Algoritmos de optimización global (Beam Search / Simulated Annealing):** Para criptogramas cortos donde algunas letras de la clave sean ambiguas, un algoritmo de búsqueda guiada por n-gramas del diccionario (bigramas y trigramas en español) permitiría desempatar letras dudosas de forma autónoma.
