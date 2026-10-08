# Criptoanalizador de Vigenère — ELC107 (Grupo C)

**Universidad Autónoma Gabriel René Moreno (UAGRM)**
**Facultad de Ciencias de la Computación y Telecomunicaciones**
**Materia:** ELC107 Criptografía y Seguridad
**Proyecto 1:** Criptoanalizador de Vigenère (Test de Kasiski + Índice de Coincidencia de Friedman + Chi-Cuadrado $\chi^2$)

---

## Descripción del Proyecto

Aplicación académica y profesional desarrollada en **Python** con interfaz gráfica en **PyQt5** para interceptar, analizar y quebrar criptogramas generados mediante el cifrado polialfabético de Vigenère.

El sistema implementa de forma nativa, mediante código propio y sin librerías externas de criptografía, los tres pilares del criptoanálisis clásico:

1. **Test de Kasiski (1863):** detección de $n$-gramas repetidos (principalmente trigramas), cálculo de distancias $\Delta$ entre apariciones y descomposición en factores para deducir la longitud de clave $m$.

2. **Índice de Coincidencia de Friedman (1922):** partición en $k$ subtextos o *cosets* ($C_0, C_1, \dots, C_{k-1}$) y cálculo del $IC$ promedio frente al valor de referencia del español ($IC \approx 0.0740$) y al valor esperado para texto aleatorio ($IC \approx 0.0385$).

3. **Análisis de Frecuencias por Chi-Cuadrado ($\chi^2$):** reducción a $m$ problemas de sustitución monoalfabética tipo César y resolución letra por letra de la palabra clave, minimizando la discrepancia cuadrática respecto al perfil de frecuencias del idioma español.

---

## Requisitos y Ejecución

### Requisitos

* **Python 3.10+** (probado en Python 3.12)
* **PyQt5**
* Dependencias instalables mediante:

```bash
pip install PyQt5
```

### Ejecución de la Aplicación Gráfica

```bash
python3 main.py
```

### Ejecución de las Pruebas Automatizadas

```bash
python3 -m unittest discover -s tests -t . -v
```

---

## Validación del Caso de Prueba Oficial (Grupo C)

### Caso utilizado

* **Texto Claro:** `"SOLA O SER PROFUNDO EN EL SILENCIO DE LA NOCHE..."`
* **Clave de Prueba:** `"MAR"`
* **Longitud de la clave:** $m = 3$

### Resultados Obtenidos

* **Test de Kasiski:** identificación de 56 trigramas repetidos, con el factor **3** como divisor dominante y más de 70 votos.

* **Índice de Coincidencia:**

  * Periodo $k = 1$: $IC \approx 0.0476$.
  * Periodo $k = 3$: $IC \approx 0.0729$, mostrando un pico próximo al valor esperado para el español natural.

* **Recuperación de Clave mediante $\chi^2$:** identificación exacta de la palabra clave `M - A - R`.

* **Descifrado:** reconstrucción íntegra del texto plano original.

---

## Estructura del Proyecto

La aplicación sigue una arquitectura basada en el patrón **MVC (Model-View-Controller)**.

```text
criptoanalizador/
├── models/                              # MODELO: lógica matemática pura (sin PyQt)
│   ├── vigenere.py                      # Cifrado/descifrado Vigenère y normalización
│   ├── kasiski.py                       # Detección de n-gramas, distancias y factores
│   ├── friedman.py                      # Cálculo del IC global y por partición de cosets
│   ├── frequency.py                     # Análisis de frecuencias por columnas
│   ├── analyzer.py                      # Fachada del modelo y flujo de criptoanálisis
│   ├── spanish_freq.py                   # Frecuencias de monogramas en español e IC
│   └── caso_prueba.py                   # Texto y clave del caso de prueba oficial
│
├── views/                               # VISTA: widgets PyQt5 pasivos
│   ├── styles.py                        # Hoja de estilos y tema visual Dark/Slate
│   ├── widgets.py                       # Componentes reutilizables y tablas
│   ├── main_window.py                   # Ventana principal con las 5 pestañas
│   ├── tab_cifrador.py                  # 1. Cifrado, descifrado y carga de prueba
│   ├── tab_kasiski.py                   # 2. Tablas de n-gramas y factores
│   ├── tab_friedman.py                  # 3. Tabla de periodos frente al IC
│   ├── tab_frecuencias.py              # 4. Deducción interactiva de la clave
│   └── tab_descifrado.py               # 5. Descifrado final y exportación
│
├── controllers/                         # CONTROLADOR: conecta vista y modelo
│   ├── app_controller.py                # Casos de uso: cifrar, analizar y exportar
│   └── formateo.py                      # Conversión de resultados a filas y textos
│
├── tests/
│   ├── test_caso_docente.py             # Validación del caso oficial de extremo a extremo
│   └── test_formateo_y_regresiones.py   # Pruebas de formateo y regresiones corregidas
│
│
├── main.py                              # Punto de entrada de la aplicación
└── README.md                            # Documentación técnica del proyecto
```

### Flujo MVC

El flujo general de la aplicación es:

```text
Usuario
   │
   ▼
Vista PyQt5
   │
   │ señal: analizar_solicitado
   ▼
AppController
   │
   ▼
CriptoanalizadorVigenere
   │
   ├── Kasiski
   ├── Friedman
   └── Chi-Cuadrado
   │
   ▼
formateo.py
   │
   ▼
Vista PyQt5
   │
   ▼
Resultados al usuario
```

En términos de responsabilidades:

* **Model:** contiene la lógica matemática y criptográfica.
* **View:** contiene exclusivamente la interfaz gráfica y los componentes visuales.
* **Controller:** coordina las acciones del usuario, ejecuta los casos de uso y transforma los resultados para mostrarlos en la interfaz.

---

## Fundamentos Matemáticos

### 1. Test de Kasiski

El Test de Kasiski busca secuencias repetidas dentro del criptograma, normalmente trigramas.

Si una misma secuencia aparece en dos posiciones diferentes, la distancia entre ellas puede estar relacionada con la longitud de la clave:

$$
\Delta = pos_2 - pos_1
$$

y, cuando la repetición coincide con la misma posición relativa de la clave:

$$
\Delta = k \cdot m
$$

por lo tanto:

$$
m \mid \Delta
$$

donde:

* $\Delta$ es la distancia entre dos apariciones.
* $m$ es la longitud de la clave.
* $k$ es un número entero.

La factorización de las distancias permite obtener candidatos para la longitud de la clave.

---

### 2. Índice de Coincidencia de Friedman

El Índice de Coincidencia permite medir qué tan cercano es un texto al comportamiento estadístico de un idioma.

La fórmula utilizada es:

$$
IC = \frac{\sum_{i=A}^{Z} f_i(f_i-1)}
{N(N-1)}
$$

donde:

* $f_i$ es la frecuencia de la letra $i$.
* $N$ es la cantidad total de letras analizadas.

Valores de referencia:

* **Español:** $IC \approx 0.0740$
* **Texto uniforme/aleatorio:** $IC \approx 0.0385$

Para analizar Vigenère, el criptograma se divide en diferentes cantidades de columnas o *cosets*.

Por ejemplo, para una clave de longitud $3$:

$$
C_0,\ C_1,\ C_2
$$

Se calcula el índice de coincidencia de cada subtexto y posteriormente su promedio.

Cuando el periodo analizado coincide con la longitud real de la clave, los subtextos tienden a comportarse como textos monoalfabéticos y su $IC$ se aproxima al valor característico del idioma.

---

### 3. Prueba de Chi-Cuadrado ($\chi^2$)

Una vez estimada la longitud de la clave, el problema se reduce a encontrar el desplazamiento de cada columna del criptograma.

Para cada posible desplazamiento $s$ se calcula:

$$
\chi^2(s)
=
\sum_{i=A}^{Z}
\frac{(O_i-E_i)^2}{E_i}
$$

donde:

* $O_i$ es la frecuencia observada de la letra $i$.
* $E_i$ es la frecuencia esperada de la letra $i$ en español.
* $N$ es el tamaño del subtexto.
* $P_{esp}(i)$ es la probabilidad esperada de la letra $i$ en español.

La frecuencia esperada se obtiene mediante:

$$
E_i = N \cdot P_{esp}(i)
$$

El desplazamiento que produzca el menor valor de $\chi^2$ se considera el candidato más probable para la letra correspondiente de la clave.

Repitiendo este proceso para cada columna se reconstruye la palabra clave completa.

---

## Flujo General del Criptoanálisis

El proceso completo implementado por la aplicación es:

```text
1. Ingreso del criptograma
          │
          ▼
2. Test de Kasiski
          │
          ├── Buscar n-gramas repetidos
          ├── Calcular distancias
          ├── Factorizar distancias
          └── Proponer longitudes de clave
          │
          ▼
3. Índice de Coincidencia de Friedman
          │
          ├── Probar diferentes periodos
          ├── Dividir el texto en cosets
          ├── Calcular IC de cada coset
          └── Seleccionar periodo candidato
          │
          ▼
4. Análisis Chi-Cuadrado
          │
          ├── Separar columnas
          ├── Probar desplazamientos César
          ├── Calcular χ²
          └── Seleccionar cada letra de la clave
          │
          ▼
5. Reconstrucción de la clave
          │
          ▼
6. Descifrado Vigenère
          │
          ▼
7. Recuperación del texto plano
```

---

## Tecnologías Utilizadas

| Tecnología       | Uso                                    |
| ---------------- | -------------------------------------- |
| **Python 3.10+** | Lenguaje principal                     |
| **PyQt5**        | Interfaz gráfica                       |
| **unittest**     | Pruebas automatizadas                  |
| **Vigenère**     | Algoritmo criptográfico analizado      |
| **Kasiski**      | Estimación de longitud de clave        |
| **Friedman**     | Análisis del Índice de Coincidencia    |
| **Chi-Cuadrado** | Recuperación de las letras de la clave |

---

## Características Principales

### Cifrador de Vigenère

Permite:

* Cifrar texto utilizando una clave.
* Descifrar criptogramas.
* Normalizar texto.
* Ejecutar rápidamente el caso de prueba oficial.

### Analizador de Kasiski

Permite:

* Detectar trigramas repetidos.
* Mostrar posiciones de aparición.
* Calcular distancias.
* Obtener factores.
* Identificar posibles longitudes de clave.

### Analizador de Friedman

Permite:

* Calcular el $IC$ global.
* Evaluar diferentes periodos.
* Dividir el criptograma en *cosets*.
* Comparar los resultados con los valores de referencia.

### Análisis por Chi-Cuadrado

Permite:

* Analizar cada columna de forma independiente.
* Evaluar los 26 desplazamientos posibles.
* Mostrar las puntuaciones $\chi^2$.
* Identificar la letra más probable para cada posición de la clave.

### Descifrado Final

Permite:

* Reconstruir automáticamente la clave.
* Descifrar el criptograma.
* Visualizar el texto recuperado.
* Exportar las trazas y resultados del análisis.

---

## Pruebas Automatizadas

El proyecto incluye pruebas automatizadas para validar tanto el algoritmo como la integración de sus componentes.

Para ejecutar todas las pruebas:

```bash
python3 -m unittest discover -s tests -t . -v
```

Las pruebas principales verifican:

* Cifrado y descifrado Vigenère.
* Detección de patrones mediante Kasiski.
* Cálculo del Índice de Coincidencia.
* Estimación de la longitud de clave.
* Recuperación de la clave mediante $\chi^2$.
* Descifrado correcto del caso docente.
* Formateo de resultados.
* Regresiones de errores corregidos.

---

## Caso Docente

El sistema fue validado utilizando el caso de prueba oficial del **Grupo C**:

```text
Texto claro:
SOLA O SER PROFUNDO EN EL SILENCIO DE LA NOCHE...

Clave:
MAR

Longitud de clave:
3
```

El flujo esperado es:

```text
Texto claro
    ↓
Cifrado Vigenère
    ↓
Criptograma
    ↓
Kasiski → longitud candidata = 3
    ↓
Friedman → pico de IC en k = 3
    ↓
Chi-Cuadrado → M A R
    ↓
Descifrado
    ↓
Texto claro original
```

---

## Objetivo Académico

El propósito del proyecto es demostrar de manera práctica los fundamentos del **criptoanálisis clásico**, mostrando cómo un cifrado polialfabético como Vigenère puede ser analizado estadísticamente sin conocer previamente la clave.

La implementación busca integrar:

* fundamentos matemáticos;
* análisis estadístico de frecuencias;
* programación en Python;
* diseño de interfaces gráficas;
* arquitectura MVC;
* pruebas automatizadas;
* trazabilidad de los resultados del proceso de criptoanálisis.

---

## Integrantes

**Grupo C — ELC107 Criptografía y Seguridad**

> Agregar aquí los nombres de los integrantes del grupo.

---

## Universidad

**Universidad Autónoma Gabriel René Moreno (UAGRM)**
**Facultad de Ciencias de la Computación y Telecomunicaciones**
**ELC107 — Criptografía y Seguridad**
