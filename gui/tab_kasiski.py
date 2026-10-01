"""
gui/tab_kasiski.py
Pestaña de Visualización del Test de Kasiski.
Muestra de forma interactiva y pedagógica las secuencias repetidas, distancias y factores.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QSplitter
)
from PyQt5.QtCore import Qt


class TabKasiski(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Tarjeta de Resumen y Métricas
        metrics_box = QGroupBox("Resumen del Examen de Kasiski")
        metrics_layout = QHBoxLayout(metrics_box)

        self.lbl_ngram_count = QLabel("N-Gramas Repetidos: --")
        self.lbl_ngram_count.setObjectName("badgeLabel")
        self.lbl_dist_count = QLabel("Distancias Analizadas: --")
        self.lbl_dist_count.setObjectName("badgeLabel")
        self.lbl_top_factors = QLabel("Divisor Más Frecuente (Clave Estimada): --")
        self.lbl_top_factors.setObjectName("badgeLabel")

        metrics_layout.addWidget(self.lbl_ngram_count)
        metrics_layout.addWidget(self.lbl_dist_count)
        metrics_layout.addWidget(self.lbl_top_factors)
        metrics_layout.addStretch()
        layout.addWidget(metrics_box)

        # Fundamento teórico
        theory_box = QGroupBox("Fundamento Criptográfico")
        theory_layout = QVBoxLayout(theory_box)
        theory_text = QLabel(
            "Principio de Kasiski: Cuando secuencias idénticas de texto claro se cifran con la misma fase de la clave, "
            "producen secuencias idénticas en el criptograma. Por tanto, la distancia (Δ) entre apariciones es múltiplo "
            "de la longitud de la clave 'm'. El factor común más frecuente revela la longitud de la clave."
        )
        theory_text.setWordWrap(True)
        theory_text.setStyleSheet("color: #94a3b8; font-style: italic;")
        theory_layout.addWidget(theory_text)
        layout.addWidget(theory_box)

        # Tablas divididas con Splitter
        splitter = QSplitter(Qt.Vertical)

        # Tabla 1: Trigramas y secuencias repetidas
        table1_box = QGroupBox("1. Registro Detallado de Secuencias Repetidas (N-Gramas)")
        t1_layout = QVBoxLayout(table1_box)
        
        self.table_ngrams = QTableWidget()
        self.table_ngrams.setColumnCount(6)
        self.table_ngrams.setHorizontalHeaderLabels([
            "N-Grama", "Longitud", "Apariciones", "Posiciones (Índices)", "Distancias (Δ)", "Factores Comunes"
        ])
        self.table_ngrams.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_ngrams.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_ngrams.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_ngrams.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        t1_layout.addWidget(self.table_ngrams)
        splitter.addWidget(table1_box)

        # Tabla 2: Ranking de Factores y Divisores
        table2_box = QGroupBox("2. Histograma de Frecuencia de Factores / Divisores Comunes")
        t2_layout = QVBoxLayout(table2_box)
        
        self.table_factors = QTableWidget()
        self.table_factors.setColumnCount(4)
        self.table_factors.setHorizontalHeaderLabels([
            "Longitud Candidata (m)", "Frecuencia / Votos", "Proporción Visual", "Evaluación Criptoanalítica"
        ])
        self.table_factors.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_factors.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_factors.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        t2_layout.addWidget(self.table_factors)
        splitter.addWidget(table2_box)

        layout.addWidget(splitter)

    def display_results(self, kasiski_data: dict):
        """Puebla las tablas y métricas con los datos calculados por el módulo kasiski.py."""
        repeated = kasiski_data.get('repeated_ngrams', [])
        all_dist = kasiski_data.get('all_distances', [])
        top_candidates = kasiski_data.get('top_key_lengths', [])
        factor_counts = kasiski_data.get('factor_counts', {})

        self.lbl_ngram_count.setText(f"N-Gramas Repetidos: {len(repeated)}")
        self.lbl_dist_count.setText(f"Distancias Calculadas: {len(all_dist)}")
        
        if top_candidates:
            best_len, best_votes = top_candidates[0]
            self.lbl_top_factors.setText(f"Divisor Dominante: m = {best_len} ({best_votes} votos)")
        else:
            self.lbl_top_factors.setText("Divisor Dominante: No concluyente")

        # Llenar Tabla 1: Secuencias repetidas
        self.table_ngrams.setRowCount(len(repeated))
        for row, item in enumerate(repeated):
            self.table_ngrams.setItem(row, 0, QTableWidgetItem(item['ngram']))
            self.table_ngrams.setItem(row, 1, QTableWidgetItem(str(item['length'])))
            self.table_ngrams.setItem(row, 2, QTableWidgetItem(str(item['count'])))
            self.table_ngrams.setItem(row, 3, QTableWidgetItem(str(item['positions'])))
            self.table_ngrams.setItem(row, 4, QTableWidgetItem(str(item['distances'])))
            self.table_ngrams.setItem(row, 5, QTableWidgetItem(str(item['factors'])))
            
            # Alinear al centro columnas numéricas
            for col in range(6):
                it = self.table_ngrams.item(row, col)
                if it and col in (1, 2):
                    it.setTextAlignment(Qt.AlignCenter)

        # Llenar Tabla 2: Ranking de factores
        sorted_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)
        max_votes = sorted_factors[0][1] if sorted_factors else 1
        
        self.table_factors.setRowCount(len(sorted_factors))
        for row, (factor, votes) in enumerate(sorted_factors):
            # Barra visual de caracteres
            bar_len = int((votes / max_votes) * 25)
            bar_visual = "█" * bar_len + f" ({votes})"
            
            eval_text = "CANDIDATO PRINCIPAL" if row == 0 else ("Candidato Secundario / Múltiplo" if row < 3 else "Baja probabilidad")

            it_factor = QTableWidgetItem(f"m = {factor}")
            it_votes = QTableWidgetItem(str(votes))
            it_bar = QTableWidgetItem(bar_visual)
            it_eval = QTableWidgetItem(eval_text)

            it_factor.setTextAlignment(Qt.AlignCenter)
            it_votes.setTextAlignment(Qt.AlignCenter)
            
            # Resaltar en verde o azul el candidato principal
            if row == 0:
                it_factor.setForeground(Qt.cyan)
                it_eval.setForeground(Qt.cyan)

            self.table_factors.setItem(row, 0, it_factor)
            self.table_factors.setItem(row, 1, it_votes)
            self.table_factors.setItem(row, 2, it_bar)
            self.table_factors.setItem(row, 3, it_eval)
