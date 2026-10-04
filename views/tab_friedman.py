"""
views/tab_friedman.py
Vista de la pestaña 3: Índice de Coincidencia (Test de Friedman).
Vista pasiva: recibe valores ya formateados por el controlador y los dibuja.
"""

from typing import Dict, Sequence

from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from views.widgets import PanelInformativo, celda, crear_tabla

COLOR_PICO = "#4ade80"

TEXTO_FUNDAMENTO = (
    "<b>Fórmula de William F. Friedman (1922):</b> IC = Σ [f<sub>i</sub> · (f<sub>i</sub> − 1)] / [N · (N − 1)].<br><br>"
    "Un cifrado polialfabético como Vigenère aplana la distribución estadística (IC global ≈ 0.038 – 0.048). "
    "Sin embargo, al dividir el criptograma en 'k' subtextos (cosets), si 'k' coincide con la longitud de clave 'm' "
    "(o un múltiplo), cada columna se convierte en un cifrado monoalfabético César puro, "
    "disparando el IC promedio a ~0.074 (perfil del idioma español)."
)


class TabFriedman(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Panel de Métricas de Referencia
        ref_box = QGroupBox("Métricas Teóricas de Referencia vs Observadas")
        box_layout = QVBoxLayout(ref_box)
        ref_layout = QHBoxLayout()
        box_layout.addLayout(ref_layout)

        self.lbl_global_ic = QLabel("IC Global del Criptograma: --")
        self.lbl_esp = QLabel("IC Teórico Español: --")
        self.lbl_rand = QLabel("IC Aleatorio (1/26): --")
        self.lbl_friedman_est = QLabel("Estimación directa Friedman: m ≈ --")
        for lbl in (self.lbl_global_ic, self.lbl_esp, self.lbl_rand, self.lbl_friedman_est):
            lbl.setObjectName("badgeLabel")
            ref_layout.addWidget(lbl)
        ref_layout.addStretch()

        # Fundamento teórico: oculto, se despliega con el icono "i"
        box_layout.addWidget(PanelInformativo("Fundamento Teórico: Índice de Coincidencia", TEXTO_FUNDAMENTO))
        layout.addWidget(ref_box)

        # Tabla de Evaluación de Periodos Candidatos
        self.table_box = QGroupBox("Evaluación del Índice de Coincidencia por Periodo Candidato")
        t_layout = QVBoxLayout(self.table_box)

        self.table_periods = crear_tabla(
            ["#", "Periodo (k)", "IC Promedio de Cosets", "Distancia a Español (|IC - 0.074|)",
             "Nivel Relativo", "Diagnóstico Criptoanalítico"],
            columnas_ajustadas=(0, 1, 2, 3),
            columna_elastica=5,
        )
        self.table_periods.setColumnWidth(4, 190)
        t_layout.addWidget(self.table_periods)
        layout.addWidget(self.table_box, 1)

    # --- API pública para el controlador ---
    def mostrar_referencias(self, ic_espanol: str, ic_aleatorio: str) -> None:
        self.lbl_esp.setText(ic_espanol)
        self.lbl_rand.setText(ic_aleatorio)

    def mostrar_metricas(self, ic_global: str, estimacion_friedman: str) -> None:
        self.lbl_global_ic.setText(ic_global)
        self.lbl_friedman_est.setText(estimacion_friedman)

    def mostrar_periodos(self, titulo: str, filas: Sequence[Dict]) -> None:
        """Cada fila: dict con claves indice, periodo, ic, delta, barra, diagnostico, pico (bool)."""
        self.table_box.setTitle(titulo)
        tabla = self.table_periods
        tabla.setRowCount(len(filas))
        for r, f in enumerate(filas):
            color = COLOR_PICO if f['pico'] else None
            tabla.setItem(r, 0, celda(f['indice'], centrado=True))
            tabla.setItem(r, 1, celda(f['periodo'], centrado=True, color=color))
            tabla.setItem(r, 2, celda(f['ic'], centrado=True, color=color))
            tabla.setItem(r, 3, celda(f['delta'], centrado=True))
            tabla.setItem(r, 4, celda(f['barra']))
            tabla.setItem(r, 5, celda(f['diagnostico'], color=color))
