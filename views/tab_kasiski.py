"""
views/tab_kasiski.py
Vista de la pestaña 2: Test de Kasiski.
Vista pasiva: recibe filas ya formateadas por el controlador y las dibuja.
"""

from typing import Dict, List, Sequence

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QSplitter, QVBoxLayout, QWidget

from views.widgets import PanelInformativo, celda, crear_tabla

COLOR_DESTACADO = "#22d3ee"

TEXTO_FUNDAMENTO = (
    "<b>Principio de Kasiski:</b> cuando secuencias idénticas de texto claro se cifran con la misma fase "
    "de la clave, producen secuencias idénticas en el criptograma. Por tanto, la distancia (Δ) entre "
    "apariciones es múltiplo de la longitud de la clave 'm'. El factor común más frecuente revela la "
    "longitud de la clave."
)


class TabKasiski(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Tarjeta de Resumen y Métricas
        metrics_box = QGroupBox("Resumen del Examen de Kasiski")
        box_layout = QVBoxLayout(metrics_box)
        metrics_layout = QHBoxLayout()
        box_layout.addLayout(metrics_layout)

        self.lbl_ngram_count = QLabel("N-Gramas Repetidos: --")
        self.lbl_dist_count = QLabel("Distancias Calculadas: --")
        self.lbl_top_factors = QLabel("Divisor Dominante: --")
        for lbl in (self.lbl_ngram_count, self.lbl_dist_count, self.lbl_top_factors):
            lbl.setObjectName("badgeLabel")
            metrics_layout.addWidget(lbl)
        metrics_layout.addStretch()

        # Fundamento teórico: oculto, se despliega con el icono "i"
        box_layout.addWidget(PanelInformativo("Fundamento Criptográfico", TEXTO_FUNDAMENTO))
        layout.addWidget(metrics_box)

        # Tablas una al lado de la otra
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Tabla 1: N-gramas y secuencias repetidas
        table1_box = QGroupBox("1. Registro Detallado de Secuencias Repetidas (N-Gramas)")
        t1_layout = QVBoxLayout(table1_box)
        self.table_ngrams = crear_tabla(
            ["#", "N-Grama", "Longitud", "Apariciones", "Posiciones",
             "Distancias (Δ)", "Factores Comunes"],
            columnas_ajustadas=(0, 1, 2, 3),
        )
        self.table_ngrams.setColumnWidth(4, 160)
        self.table_ngrams.setColumnWidth(5, 120)
        t1_layout.addWidget(self.table_ngrams)
        splitter.addWidget(table1_box)

        # Tabla 2: Ranking de factores y divisores
        table2_box = QGroupBox("2. Histograma de Frecuencia de Factores / Divisores Comunes")
        t2_layout = QVBoxLayout(table2_box)
        self.table_factors = crear_tabla(
            ["#", "Candidata (m)", "Votos", "Proporción", "Evaluación"],
            columnas_ajustadas=(0, 1, 2),
            columna_elastica=4,
        )
        self.table_factors.setColumnWidth(3, 110)
        t2_layout.addWidget(self.table_factors)
        splitter.addWidget(table2_box)

        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 4)
        splitter.setSizes([500, 400])
        layout.addWidget(splitter, 1)

    # --- API pública para el controlador ---
    def mostrar_resumen(self, n_ngramas: str, n_distancias: str, divisor_dominante: str) -> None:
        self.lbl_ngram_count.setText(n_ngramas)
        self.lbl_dist_count.setText(n_distancias)
        self.lbl_top_factors.setText(divisor_dominante)

    def mostrar_ngramas(self, filas: Sequence[Dict[str, str]]) -> None:
        """Cada fila: dict con claves indice, ngrama, longitud, apariciones, posiciones, distancias, factores."""
        tabla = self.table_ngrams
        tabla.setRowCount(len(filas))
        for r, f in enumerate(filas):
            tabla.setItem(r, 0, celda(f['indice'], centrado=True))
            tabla.setItem(r, 1, celda(f['ngrama'], centrado=True))
            tabla.setItem(r, 2, celda(f['longitud'], centrado=True))
            tabla.setItem(r, 3, celda(f['apariciones'], centrado=True))
            tabla.setItem(r, 4, celda(f['posiciones']))
            tabla.setItem(r, 5, celda(f['distancias']))
            tabla.setItem(r, 6, celda(f['factores'], tooltip=f['factores_tooltip']))

    def mostrar_factores(self, filas: Sequence[Dict]) -> None:
        """Cada fila: dict con claves indice, candidata, votos, barra, evaluacion, principal (bool)."""
        tabla = self.table_factors
        tabla.setRowCount(len(filas))
        for r, f in enumerate(filas):
            color = COLOR_DESTACADO if f['principal'] else None
            tabla.setItem(r, 0, celda(f['indice'], centrado=True))
            tabla.setItem(r, 1, celda(f['candidata'], centrado=True, color=color))
            tabla.setItem(r, 2, celda(f['votos'], centrado=True))
            tabla.setItem(r, 3, celda(f['barra']))
            tabla.setItem(r, 4, celda(f['evaluacion'], color=color))
