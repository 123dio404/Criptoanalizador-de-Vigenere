"""
gui/tab_defensa.py
Pestaña de Apoyo Teórico y Preparación para la Defensa Oral (Control Anti-IA).
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.
Incluye glosario técnico, fórmulas matemáticas explicadas y respuestas a preguntas de examen.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextBrowser, QGroupBox
)

DEFENSA_ORAL_HTML = """
<style>
    body { font-family: sans-serif; color: #e2e8f0; line-height: 1.6; }
    h2 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 6px; }
    h3 { color: #7dd3fc; margin-top: 18px; }
    .card { background-color: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 14px; margin-bottom: 14px; }
    .tag { background-color: #2563eb; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }
    .formula { font-family: monospace; background-color: #1e293b; padding: 6px 10px; border-radius: 4px; color: #facc15; font-size: 13px; display: inline-block; }
    b { color: #f8fafc; }
</style>

<h2>Guía de Fundamentos Teóricos — Criptoanálisis de Vigenère</h2>

<div class="card">
    <span class="tag">CRITERIO DE DEFENSA 15 PTS</span>
    <h3>1. ¿Por qué el Cifrado de Vigenère es vulnerable y cómo lo demuestra Kasiski?</h3>
    <p>
        El cifrado de Vigenère es un <b>cifrado polialfabético periódico</b>. Al reutilizar una clave <i>K</i> de longitud fija <i>m</i>, 
        la periodicidad destruye la seguridad perfecta. Si un mismo fragmento de texto en claro (por ejemplo, el trigrama "QUE" o "DEL") 
        aparece en dos posiciones separadas por una distancia Δ que es múltiplo exacto de <i>m</i>, ambas instancias coincidirán con 
        las mismas letras de la clave y generarán <b>criptogramas idénticos</b>.<br>
        Por tanto, al factorizar las distancias entre n-gramas repetidos, la longitud de la clave <i>m</i> divide a dichas distancias.
    </p>
</div>

<div class="card">
    <span class="tag">MATEMÁTICA Y FÓRMULAS 25 PTS</span>
    <h3>2. ¿Cómo funciona el Índice de Coincidencia (IC) de William Friedman?</h3>
    <p>
        El IC mide la probabilidad de que dos caracteres extraídos al azar sin reemplazo sean idénticos:
        <br><br>
        <span class="formula">IC = Σ [ f_i * (f_i - 1) ] / [ N * (N - 1) ]</span>
        <br><br>
        <b>Comportamiento estadístico:</b>
        <ul>
            <li><b>Idioma Español Natural:</b> IC ≈ 0.0740 (la distribución de letras es no uniforme: A, E, O tienen alta probabilidad).</li>
            <li><b>Texto Aleatorio / Distribución Uniforme (1/26):</b> IC ≈ 0.0385.</li>
            <li><b>Criptograma Vigenère completo:</b> Presenta un IC bajo (0.040 - 0.048) debido a la mezcla polialfabética.</li>
            <li><b>Subtextos o Cosets (longitud m):</b> Al separar las letras en <i>m</i> columnas, cada columna fue cifrada con un solo desplazamiento César. Una traslación monoalfabética <b>conserva intactas las frecuencias relativas</b>, por lo que el IC de cada subtexto vuelve a ser ≈ 0.074.</li>
        </ul>
    </p>
</div>

<div class="card">
    <span class="tag">PREGUNTA FRECUENTE DE EXAMEN</span>
    <h3>3. ¿Por qué en la gráfica o tabla de IC también se ven picos en múltiplos de la clave (ej. k=6 si m=3)?</h3>
    <p>
        Si la clave tiene longitud 3 ("MAR"), agrupar cada 6 posiciones también conserva letras cifradas con el mismo desplazamiento César 
        (la posición 0 y la 6 fueron cifradas con la letra 'M'). Por ello, <b>los múltiplos de la clave también presentarán un IC elevado</b>. 
        Sin embargo, la verdadera longitud fundamental es el <b>mínimo común periodo</b> (k = 3), respaldado por la mayor concentración de votos en el Test de Kasiski.
    </p>
</div>

<div class="card">
    <span class="tag">RECUPERACIÓN DE CLAVE 25 PTS</span>
    <h3>4. ¿Cómo deduce el software cada letra de la clave usando Chi-Cuadrado (χ²)?</h3>
    <p>
        Conocida la longitud <i>m</i>, el problema se divide en <i>m</i> problemas monoalfabéticos de César independientes.
        Para cada columna, se prueban los 26 desplazamientos posibles <i>s ∈ {0..25}</i>. Al descifrar la columna con el desplazamiento <i>s</i>,
        se compara la distribución observada <i>O_i</i> con la frecuencia esperada del español <i>E_i = N * P_esp(i)</i>:
        <br><br>
        <span class="formula">χ²(s) = Σ [ (O_i - E_i)² / E_i ]</span>
        <br><br>
        El valor de <i>s</i> que <b>minimiza χ²</b> indica la letra de la clave para esa columna (por ejemplo: s=12 corresponde a 'M', s=0 a 'A', s=17 a 'R').
    </p>
</div>

<div class="card">
    <span class="tag">LIMITACIONES Y MEJORAS</span>
    <h3>5. ¿Cuáles son las limitaciones del ataque de Kasiski y Friedman?</h3>
    <p>
        <ul>
            <li><b>Criptogramas muy cortos:</b> En textos breves (menos de 50 letras), la probabilidad de que se repitan trigramas por puro azar o por coincidencia periódica es muy baja, y la varianza estadística del IC es alta.</li>
            <li><b>Claves no periódicas o One-Time Pad:</b> Si la clave es tan larga como el texto y nunca se repite (m = N), no existe periodicidad, el IC se mantiene en ~0.0385 y el cifrado es matemáticamente incondicionalmente seguro (teorema de Shannon).</li>
        </ul>
    </p>
</div>
"""


class TabDefensa(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        box = QGroupBox("Material Didáctico y Justificación Teórica (Control Anti-IA)")
        b_layout = QVBoxLayout(box)

        self.browser = QTextBrowser()
        self.browser.setHtml(DEFENSA_ORAL_HTML)
        self.browser.setOpenExternalLinks(True)
        b_layout.addWidget(self.browser)

        layout.addWidget(box)
