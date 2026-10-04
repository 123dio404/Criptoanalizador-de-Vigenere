"""
views/tab_frecuencias.py
Vista de la pestaña 4: Análisis de Frecuencias y recuperación de la clave por Chi-cuadrado (χ²).
Vista pasiva: no calcula nada; emite señales y dibuja lo que le entrega el controlador.
"""

from typing import Dict, Sequence

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from views.widgets import celda, crear_tabla

COLOR_OPTIMO = "#22d3ee"


class TabFrecuencias(QWidget):
    # Señales hacia el controlador
    longitud_cambiada = pyqtSignal(int)
    columna_seleccionada = pyqtSignal(int)
    confirmar_clave_solicitado = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Panel Superior de Control de Longitud de Clave
        top_box = QGroupBox("Parámetros de Reconstrucción de Clave")
        top_layout = QHBoxLayout(top_box)

        lbl_len = QLabel("Longitud de Clave (m):")
        self.spin_key_len = QSpinBox()
        self.spin_key_len.setRange(1, 25)
        self.spin_key_len.setValue(3)
        self.spin_key_len.valueChanged.connect(self.longitud_cambiada)

        btn_recalc = QPushButton("Recalcular Clave para esta Longitud")
        btn_recalc.setObjectName("secondaryButton")
        btn_recalc.clicked.connect(lambda: self.longitud_cambiada.emit(self.spin_key_len.value()))

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

        self.btn_usar_clave = QPushButton("Confirmar y Descifrar Texto Completo")
        self.btn_usar_clave.setObjectName("accentButton")
        self.btn_usar_clave.clicked.connect(self.confirmar_clave_solicitado)

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
        self.combo_columns.currentIndexChanged.connect(self.columna_seleccionada)

        self.lbl_col_info = QLabel("Subtexto: -- caracteres")
        self.lbl_col_info.setObjectName("badgeLabel")

        selector_layout.addWidget(lbl_col)
        selector_layout.addWidget(self.combo_columns)
        selector_layout.addWidget(self.lbl_col_info)
        selector_layout.addStretch()
        col_layout.addLayout(selector_layout)

        # Tabla de los 26 desplazamientos evaluados para la columna seleccionada
        self.table_candidates = crear_tabla(
            ["Letra Candidata", "Desplazamiento (s)", "Chi-Cuadrado (χ²)",
             "Correlación con Español", "Ranking"],
            columnas_ajustadas=(0, 1, 3, 4),
            columna_elastica=2,
        )
        col_layout.addWidget(self.table_candidates)
        layout.addWidget(col_box, 1)

    # --- API pública para el controlador ---
    def configurar_longitud(self, maximo: int, valor: int) -> None:
        """Ajusta el rango del selector y el valor sin disparar la señal de cambio."""
        self.spin_key_len.blockSignals(True)
        self.spin_key_len.setRange(1, max(1, maximo))
        self.spin_key_len.setValue(valor)
        self.spin_key_len.blockSignals(False)

    def longitud(self) -> int:
        return self.spin_key_len.value()

    def mostrar_clave(self, clave: str) -> None:
        self.lbl_recovered_key.setText(f"CLAVE:  [ {'  '.join(clave)} ]")

    def mostrar_columnas(self, etiquetas: Sequence[str]) -> None:
        """Rellena el selector de columnas y selecciona la primera sin emitir señal."""
        self.combo_columns.blockSignals(True)
        self.combo_columns.clear()
        self.combo_columns.addItems(list(etiquetas))
        self.combo_columns.blockSignals(False)

    def mostrar_detalle_columna(self, info: str, filas: Sequence[Dict[str, str]]) -> None:
        """Cada fila: dict con claves letra, desplazamiento, chi2, correlacion, ranking, optimo (bool)."""
        self.lbl_col_info.setText(info)
        tabla = self.table_candidates
        tabla.setRowCount(len(filas))
        for r, f in enumerate(filas):
            color = COLOR_OPTIMO if f['optimo'] else None
            tabla.setItem(r, 0, celda(f['letra'], centrado=True, color=color))
            tabla.setItem(r, 1, celda(f['desplazamiento'], centrado=True))
            tabla.setItem(r, 2, celda(f['chi2'], centrado=True, color=color))
            tabla.setItem(r, 3, celda(f['correlacion'], centrado=True))
            tabla.setItem(r, 4, celda(f['ranking'], centrado=True, color=color))
