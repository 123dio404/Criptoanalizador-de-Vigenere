"""
views/widgets.py
Widgets reutilizables de la capa Vista.
"""

from typing import Optional, Sequence

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QTabBar, QTableWidget,
    QTableWidgetItem, QToolButton, QVBoxLayout, QWidget,
)


class BarraPestanas(QTabBar):
    """
    La barra estándar calcula el ancho de cada pestaña justo y, con el borde de la
    hoja de estilos, recorta el último carácter (el ')' de 'Frecuencias (χ²)').
    """

    def tabSizeHint(self, index: int):
        hint = super().tabSizeHint(index)
        # El glifo χ² se mide más angosto de lo que se pinta y el borde se come el ')'.
        if "χ" in self.tabText(index):
            hint.setWidth(hint.width() + 20)
        return hint


class PanelInformativo(QWidget):
    """
    Panel de ayuda teórica oculto por defecto. Muestra un título junto a un icono "i";
    al pulsar el icono se despliega (o se oculta) el texto explicativo.
    """

    def __init__(self, titulo: str, texto: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        cabecera = QHBoxLayout()
        cabecera.setContentsMargins(0, 0, 0, 0)

        self.btn_info = QToolButton()
        self.btn_info.setObjectName("infoButton")
        self.btn_info.setText("i")
        self.btn_info.setCheckable(True)
        self.btn_info.setCursor(Qt.PointingHandCursor)
        self.btn_info.setToolTip("Mostrar / ocultar el fundamento teórico")
        self.btn_info.toggled.connect(self._alternar)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("infoTitle")

        cabecera.addWidget(self.btn_info)
        cabecera.addWidget(lbl_titulo)
        cabecera.addStretch()
        layout.addLayout(cabecera)

        self.lbl_detalle = QLabel(texto)
        self.lbl_detalle.setObjectName("infoBody")
        self.lbl_detalle.setWordWrap(True)
        self.lbl_detalle.setTextFormat(Qt.RichText)
        self.lbl_detalle.setVisible(False)
        layout.addWidget(self.lbl_detalle)

    def _alternar(self, visible: bool) -> None:
        self.lbl_detalle.setVisible(visible)


def crear_tabla(encabezados: Sequence[str], columnas_ajustadas: Sequence[int] = (),
                columna_elastica: Optional[int] = None) -> QTableWidget:
    """
    Crea una tabla de solo lectura con el estilo de la aplicación.
    - columnas_ajustadas: columnas que se dimensionan según su contenido.
    - columna_elastica: columna que absorbe el espacio sobrante (por defecto la última).
    Las columnas restantes son redimensionables manualmente y la tabla desplaza horizontalmente si no caben.
    """
    tabla = QTableWidget()
    tabla.setColumnCount(len(encabezados))
    tabla.setHorizontalHeaderLabels(list(encabezados))
    tabla.setEditTriggers(QTableWidget.NoEditTriggers)
    tabla.setSelectionBehavior(QTableWidget.SelectRows)
    tabla.setAlternatingRowColors(False)
    tabla.verticalHeader().setVisible(False)
    tabla.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
    tabla.setVerticalScrollMode(QTableWidget.ScrollPerPixel)

    cabecera = tabla.horizontalHeader()
    cabecera.setStretchLastSection(False)
    elastica = len(encabezados) - 1 if columna_elastica is None else columna_elastica
    metricas = cabecera.fontMetrics()
    for col, titulo in enumerate(encabezados):
        if col == elastica and col not in columnas_ajustadas:
            # Absorbe el ancho sobrante: si no, Qt deja un hueco vacío a la derecha
            # que se pinta con el color por defecto (blanco).
            cabecera.setSectionResizeMode(col, QHeaderView.Stretch)
        elif col in columnas_ajustadas:
            cabecera.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        else:
            cabecera.setSectionResizeMode(col, QHeaderView.Interactive)
            tabla.setColumnWidth(col, max(150, metricas.width(titulo) + 40))
    return tabla


def celda(texto: str, centrado: bool = False, color: Optional[str] = None,
          tooltip: Optional[str] = None) -> QTableWidgetItem:
    """Crea una celda de tabla con alineación, color y tooltip opcionales."""
    item = QTableWidgetItem(texto)
    if centrado:
        item.setTextAlignment(Qt.AlignCenter)
    if color:
        item.setForeground(QColor(color))
    item.setToolTip(tooltip if tooltip is not None else texto)
    return item
