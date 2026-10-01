"""
gui/tab_friedman.py
Pestaña de Visualización del Índice de Coincidencia (Test de Friedman).
Permite verificar la hipótesis de la longitud de la clave evaluando el comportamiento
monoalfabético vs polialfabético de los subtextos (cosets).
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox
)
from PyQt5.QtCore import Qt
from data.spanish_freq import IC_TEORICO_ESP, IC_TEORICO_ALEATORIO


class TabFriedman(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Panel de Métricas de Referencia
        ref_box = QGroupBox("Métricas Teóricas de Referencia vs Observadas")
        ref_layout = QHBoxLayout(ref_box)

        self.lbl_global_ic = QLabel("IC Global del Criptograma: --")
        self.lbl_global_ic.setObjectName("badgeLabel")
        
        lbl_esp = QLabel(f"IC Teórico Español: {IC_TEORICO_ESP:.4f}")
        lbl_esp.setObjectName("badgeLabel")
        
        lbl_rand = QLabel(f"IC Aleatorio (1/26): {IC_TEORICO_ALEATORIO:.4f}")
        lbl_rand.setObjectName("badgeLabel")

        self.lbl_friedman_est = QLabel("Estimación directa Friedman: m ≈ --")
        self.lbl_friedman_est.setObjectName("badgeLabel")

        ref_layout.addWidget(self.lbl_global_ic)
        ref_layout.addWidget(lbl_esp)
        ref_layout.addWidget(lbl_rand)
        ref_layout.addWidget(self.lbl_friedman_est)
        ref_layout.addStretch()
        layout.addWidget(ref_box)

        # Explicación teórica
        theory_box = QGroupBox("Fundamento Teórico: Índice de Coincidencia")
        theory_layout = QVBoxLayout(theory_box)
        theory_text = QLabel(
            "Fórmula de William F. Friedman (1922): IC = Σ [f_i * (f_i - 1)] / [N * (N - 1)].\n"
            "Un cifrado polialfabético como Vigenère aplana la distribución estadística (IC global ≈ 0.038 - 0.048). "
            "Sin embargo, al dividir el criptograma en 'k' subtextos (cosets), si 'k' coincide con la longitud de clave 'm' "
            "(o un múltiplo), cada columna se convierte en un cifrado monoalfabético César puro, "
            "disparando el IC promedio a ~0.074 (perfil del idioma español)."
        )
        theory_text.setWordWrap(True)
        theory_text.setStyleSheet("color: #94a3b8; font-style: italic;")
        theory_layout.addWidget(theory_text)
        layout.addWidget(theory_box)

        # Tabla de Evaluación de Periodos Candidatos
        table_box = QGroupBox("Evaluación del Índice de Coincidencia por Periodo Candidato (k = 1 .. 15)")
        t_layout = QVBoxLayout(table_box)

        self.table_periods = QTableWidget()
        self.table_periods.setColumnCount(5)
        self.table_periods.setHorizontalHeaderLabels([
            "Periodo (k)", "IC Promedio de Cosets", "Distancia a Español (|IC - 0.074|)",
            "Nivel Relativo", "Diagnóstico Criptoanalítico"
        ])
        self.table_periods.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_periods.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_periods.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_periods.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        t_layout.addWidget(self.table_periods)

        layout.addWidget(table_box)

    def display_results(self, friedman_data: dict):
        """Puebla la interfaz con los resultados de Friedman."""
        global_ic = friedman_data.get('global_ic', 0.0)
        best_period = friedman_data.get('best_period_by_ic', 1)
        best_avg_ic = friedman_data.get('best_avg_ic', 0.0)
        friedman_est = friedman_data.get('friedman_formula_estimate', None)
        periods_data = friedman_data.get('periods_data', [])

        self.lbl_global_ic.setText(f"IC Global del Criptograma: {global_ic:.4f}")
        
        if friedman_est:
            self.lbl_friedman_est.setText(f"Estimación directa Friedman: m ≈ {friedman_est}")
        else:
            self.lbl_friedman_est.setText("Estimación directa Friedman: N/A")

        self.table_periods.setRowCount(len(periods_data))
        for row, p in enumerate(periods_data):
            k = p['period']
            avg_ic = p['average_ic']
            delta = p['delta_to_spanish']
            
            # Generar barra visual normalizada
            # 0.0385 -> 0%, 0.0740 -> 100%
            ratio = max(0.0, min(1.0, (avg_ic - 0.038) / (0.074 - 0.038)))
            bar_len = int(ratio * 20)
            bar_str = "█" * bar_len + f" {int(ratio*100)}%"

            is_peak = (k == best_period) or (avg_ic >= 0.065)
            if is_peak:
                if k == best_period:
                    diag = "★ PICO MÁXIMO (Longitud de Clave Recomendada)"
                else:
                    diag = "Pico Secundario (Múltiplo de la Clave)"
            else:
                diag = "Polialfabético (Subtextos mezclados)"

            it_k = QTableWidgetItem(f"k = {k}")
            it_ic = QTableWidgetItem(f"{avg_ic:.4f}")
            it_delta = QTableWidgetItem(f"{delta:.4f}")
            it_bar = QTableWidgetItem(bar_str)
            it_diag = QTableWidgetItem(diag)

            it_k.setTextAlignment(Qt.AlignCenter)
            it_ic.setTextAlignment(Qt.AlignCenter)
            it_delta.setTextAlignment(Qt.AlignCenter)

            if is_peak:
                it_k.setForeground(Qt.green)
                it_ic.setForeground(Qt.green)
                it_diag.setForeground(Qt.green)

            self.table_periods.setItem(row, 0, it_k)
            self.table_periods.setItem(row, 1, it_ic)
            self.table_periods.setItem(row, 2, it_delta)
            self.table_periods.setItem(row, 3, it_bar)
            self.table_periods.setItem(row, 4, it_diag)
