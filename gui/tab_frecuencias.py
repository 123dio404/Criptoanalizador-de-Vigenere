"""
gui/tab_frecuencias.py
Pestaña de Análisis de Frecuencias y Recuperación de la Clave por Chi-cuadrado (χ²).
Permite visualizar la deducción matemática de cada carácter de la clave y ajustarla interactivamente.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QSpinBox,
    QPushButton, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from core.frequency import deducir_clave_por_frecuencias, resolver_clave_para_columna
from core.friedman import particionar_en_subtextos
from data.spanish_freq import ALFABETO_ESP_26


class TabFrecuencias(QWidget):
    clave_confirmada = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ciphertext = ""
        self.current_key_data = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Panel Superior de Control de Longitud de Clave
        top_box = QGroupBox("Parámetros de Reconstrucción de Clave")
        top_layout = QHBoxLayout(top_box)

        lbl_len = QLabel("Longitud de Clave (m):")
        self.spin_key_len = QSpinBox()
        self.spin_key_len.setRange(1, 25)
        self.spin_key_len.setValue(3)
        self.spin_key_len.valueChanged.connect(self.recalcular_clave)

        btn_recalc = QPushButton("🔄 Recalcular Clave para esta Longitud")
        btn_recalc.setObjectName("secondaryButton")
        btn_recalc.clicked.connect(self.recalcular_clave)

        top_layout.addWidget(lbl_len)
        top_layout.addWidget(self.spin_key_len)
        top_layout.addWidget(btn_recalc)
        top_layout.addStretch()
        layout.addWidget(top_box)

        # Banner de Clave Recuperada
        key_box = QGroupBox("Palabra Clave Resuelta mediante Chi-Cuadrado (χ²)")
        key_layout = QHBoxLayout(key_box)

        self.lbl_recovered_key = QLabel("CLAVE: ---")
        self.lbl_recovered_key.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #38bdf8; letter-spacing: 4px; padding: 4px;"
        )
        
        self.btn_usar_clave = QPushButton("🔑 Confirmar y Descifrar Texto Completo")
        self.btn_usar_clave.setObjectName("accentButton")
        self.btn_usar_clave.clicked.connect(self.confirmar_clave)

        key_layout.addWidget(self.lbl_recovered_key)
        key_layout.addStretch()
        key_layout.addWidget(self.btn_usar_clave)
        layout.addWidget(key_box)

        # Selector de Columna
        col_box = QGroupBox("Inspección Detallada por Columna (Subcifrado César)")
        col_layout = QVBoxLayout(col_box)

        selector_layout = QHBoxLayout()
        lbl_col = QLabel("Seleccione la Columna / Posición de la Clave a Examinar:")
        self.combo_columns = QComboBox()
        self.combo_columns.currentIndexChanged.connect(self.mostrar_detalle_columna)
        
        self.lbl_col_info = QLabel("Subtexto: -- caracteres")
        self.lbl_col_info.setObjectName("badgeLabel")

        selector_layout.addWidget(lbl_col)
        selector_layout.addWidget(self.combo_columns)
        selector_layout.addWidget(self.lbl_col_info)
        selector_layout.addStretch()
        col_layout.addLayout(selector_layout)

        # Tabla de los 26 desplazamientos evaluados para la columna seleccionada
        self.table_candidates = QTableWidget()
        self.table_candidates.setColumnCount(5)
        self.table_candidates.setHorizontalHeaderLabels([
            "Letra Candidata", "Desplazamiento (s)", "Chi-Cuadrado (χ²)", "Correlación con Español", "Ranking"
        ])
        self.table_candidates.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for c in range(5):
            self.table_candidates.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self.table_candidates.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        col_layout.addWidget(self.table_candidates)

        layout.addWidget(col_box)

    def set_ciphertext(self, ciphertext: str, suggested_length: int = 3):
        self.ciphertext = "".join([ch for ch in ciphertext.upper() if ch in ALFABETO_ESP_26])
        self.spin_key_len.blockSignals(True)
        self.spin_key_len.setValue(suggested_length)
        self.spin_key_len.blockSignals(False)
        self.recalcular_clave()

    def recalcular_clave(self):
        if not self.ciphertext:
            return
        m = self.spin_key_len.value()
        self.current_key_data = deducir_clave_por_frecuencias(self.ciphertext, m)
        rec_key = self.current_key_data['recovered_key']
        self.lbl_recovered_key.setText(f"CLAVE:  [ { '  '.join(rec_key) } ]")

        # Actualizar combo de columnas
        self.combo_columns.blockSignals(True)
        self.combo_columns.clear()
        for idx in range(m):
            letter = rec_key[idx] if idx < len(rec_key) else "?"
            self.combo_columns.addItem(f"Columna #{idx+1} (Posición {idx}) -> Letra sugerida: '{letter}'")
        self.combo_columns.blockSignals(False)

        self.mostrar_detalle_columna(0)

    def mostrar_detalle_columna(self, col_index: int):
        if not self.ciphertext or not self.current_key_data:
            return
        m = self.spin_key_len.value()
        if col_index < 0 or col_index >= m:
            return

        cosets = particionar_en_subtextos(self.ciphertext, m)
        coset = cosets[col_index] if col_index < len(cosets) else ""
        self.lbl_col_info.setText(f"Subtexto: {len(coset)} letras | Muestra: {coset[:18]}...")

        # Obtener ranking de las 26 letras
        candidates = resolver_clave_para_columna(coset)
        self.table_candidates.setRowCount(len(candidates))

        for row, cand in enumerate(candidates):
            letra = cand['letter']
            shift = cand['shift']
            chi2 = cand['chi2']
            corr = cand['correlation']
            ranking = f"#{row + 1}" + (" (ÓPTIMO)" if row == 0 else "")

            it_letra = QTableWidgetItem(letra)
            it_shift = QTableWidgetItem(f"{shift} ('{letra}')")
            it_chi2 = QTableWidgetItem(f"{chi2:.2f}")
            it_corr = QTableWidgetItem(f"{corr:.4f}")
            it_rank = QTableWidgetItem(ranking)

            it_letra.setTextAlignment(Qt.AlignCenter)
            it_shift.setTextAlignment(Qt.AlignCenter)
            it_chi2.setTextAlignment(Qt.AlignCenter)
            it_corr.setTextAlignment(Qt.AlignCenter)
            it_rank.setTextAlignment(Qt.AlignCenter)

            if row == 0:
                it_letra.setForeground(Qt.cyan)
                it_chi2.setForeground(Qt.cyan)
                it_rank.setForeground(Qt.cyan)

            self.table_candidates.setItem(row, 0, it_letra)
            self.table_candidates.setItem(row, 1, it_shift)
            self.table_candidates.setItem(row, 2, it_chi2)
            self.table_candidates.setItem(row, 3, it_corr)
            self.table_candidates.setItem(row, 4, it_rank)

    def confirmar_clave(self):
        if self.current_key_data:
            self.clave_confirmada.emit(self.current_key_data['recovered_key'])
