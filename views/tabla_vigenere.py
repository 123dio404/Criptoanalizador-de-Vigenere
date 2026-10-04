"""
views/tabla_vigenere.py
Panel lateral plegable con la tabla (tabula recta) de Vigenère.
Las filas correspondientes a las letras de la clave se resaltan con otro color.
"""

from typing import Dict, Sequence, Tuple

from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QSize, Qt
from PyQt5.QtGui import QColor, QFont, QPainter
from PyQt5.QtWidgets import (
    QAbstractButton, QGroupBox, QHBoxLayout, QHeaderView, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

TAM_CELDA_MIN = 12
ANCHO_RESPALDO = 640

# Tono base de los cruces usados; se oscurece hacia COLOR_FRECUENCIA_OSCURO según la frecuencia.
COLOR_FRECUENCIA = (0xF1, 0x8B, 0x6F)
COLOR_FRECUENCIA_OSCURO = (0x7A, 0x34, 0x18)
COLOR_TEXTO_CLARO = QColor("#1e293b")
COLOR_TEXTO_OSCURO = QColor("#fff7f4")


def _color_frecuencia(tono: float) -> QColor:
    """tono 0 es #F18B6F; tono 1 es el mismo color mucho más oscuro."""
    tono = max(0.0, min(1.0, tono))
    canales = (
        int(base + (oscuro - base) * tono)
        for base, oscuro in zip(COLOR_FRECUENCIA, COLOR_FRECUENCIA_OSCURO)
    )
    return QColor(*canales)


class BotonLateral(QAbstractButton):
    """Botón angosto con texto vertical para plegar/desplegar el panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedWidth(28)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setToolTip("Mostrar / ocultar la tabla de Vigenère")

    def sizeHint(self) -> QSize:
        return QSize(28, 220)

    def paintEvent(self, _evento) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        fondo = QColor("#1e40af") if self.underMouse() else QColor("#1e293b")
        p.setBrush(fondo)
        p.setPen(QColor("#38bdf8"))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)

        flecha = "▶" if self.isChecked() else "◀"
        p.translate(self.width() / 2, self.height() / 2)
        p.rotate(90)
        fuente = QFont(self.font())
        fuente.setBold(True)
        p.setFont(fuente)
        p.setPen(QColor("#38bdf8"))
        texto = f"{flecha}   Tabla de Vigenère   {flecha}"
        ancho = p.fontMetrics().horizontalAdvance(texto)
        p.drawText(int(-ancho / 2), int(p.fontMetrics().ascent() / 2) - 1, texto)

    def enterEvent(self, evento) -> None:
        self.update()
        super().enterEvent(evento)

    def leaveEvent(self, evento) -> None:
        self.update()
        super().leaveEvent(evento)


class PanelTablaVigenere(QWidget):
    """Panel que se pliega hacia la derecha dejando visible solo el botón lateral."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.btn_alternar = BotonLateral()
        self.btn_alternar.toggled.connect(self._animar)
        layout.addWidget(self.btn_alternar)

        self.contenido = QGroupBox("Tabla de Vigenère (fila = letra clave, columna = letra clara)")
        cont_layout = QVBoxLayout(self.contenido)
        cont_layout.setContentsMargins(6, 10, 6, 6)

        self.tabla = QTableWidget(26, 26)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionMode(QTableWidget.NoSelection)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        self.tabla.setObjectName("tablaVigenere")
        self.tabla.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabla.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabla.setWordWrap(False)
        # Las 26x26 celdas se reparten el espacio disponible: la tabla entra completa, sin scroll.
        for cabecera in (self.tabla.horizontalHeader(), self.tabla.verticalHeader()):
            cabecera.setMinimumSectionSize(TAM_CELDA_MIN)
            cabecera.setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tabla.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        cont_layout.addWidget(self.tabla, 1)

        self.contenido.setVisible(False)
        layout.addWidget(self.contenido, 1)

        # El ancho lo fija el propio panel: plegado cabe solo el botón y el Generador
        # ocupa el resto; desplegado toma la mitad de la pestaña.
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(self.btn_alternar.width())

        self._animacion = QPropertyAnimation(self, b"minimumWidth", self)
        self._animacion.setDuration(250)
        self._animacion.setEasingCurve(QEasingCurve.OutCubic)
        self._animacion.valueChanged.connect(self._igualar_ancho)
        self._animacion.finished.connect(self._fin_animacion)

    # --- API pública ---
    def mostrar_tabla(self, filas: Sequence[str], letras_clave: str,
                      frecuencias: Dict[Tuple[str, str], int]) -> None:
        """Rellena la tabla y pinta solo los cruces (fila clave, columna clara) que se usaron."""
        alfabeto = filas[0] if filas else ""
        self.tabla.setHorizontalHeaderLabels(list(alfabeto))
        self.tabla.setVerticalHeaderLabels([fila[0] for fila in filas])

        posiciones = {}
        for i, letra in enumerate(letras_clave):
            posiciones.setdefault(letra, []).append(i + 1)
        max_frecuencia = max(frecuencias.values(), default=1)

        for r, fila in enumerate(filas):
            letra_clave = fila[0]
            for c, cifrada in enumerate(fila):
                letra_clara = alfabeto[c]
                item = QTableWidgetItem(cifrada)
                item.setTextAlignment(Qt.AlignCenter)
                veces = frecuencias.get((letra_clave, letra_clara), 0)
                if veces:
                    tono = (veces - 1) / (max_frecuencia - 1) if max_frecuencia > 1 else 0.0
                    item.setBackground(_color_frecuencia(tono))
                    item.setForeground(COLOR_TEXTO_OSCURO if tono > 0.55 else COLOR_TEXTO_CLARO)
                    lugar = ", ".join(map(str, posiciones.get(letra_clave, [])))
                    item.setToolTip(
                        f"Fila clave '{letra_clave}' (posición {lugar}): "
                        f"{letra_clara} + {letra_clave} = {cifrada}, f={veces}"
                    )
                self.tabla.setItem(r, c, item)

    def desplegar(self) -> None:
        self.btn_alternar.setChecked(True)

    def plegar(self) -> None:
        self.btn_alternar.setChecked(False)

    def esta_desplegado(self) -> bool:
        return self.btn_alternar.isChecked()

    # --- Animación ---
    def _ancho_desplegado(self) -> int:
        """La mitad de la pestaña, para que la tabla quepa completa al abrirse."""
        contenedor = self.parentWidget()
        total = contenedor.width() if contenedor else ANCHO_RESPALDO * 2
        return max(ANCHO_RESPALDO // 2, total // 2)

    def _ancho_plegado(self) -> int:
        return self.btn_alternar.width()

    def ajustar_si_desplegado(self) -> None:
        """Mantiene la mitad de la pestaña si la ventana cambia de tamaño con la tabla abierta."""
        if self.esta_desplegado() and self._animacion.state() != QPropertyAnimation.Running:
            ancho = self._ancho_desplegado()
            if self.width() != ancho:
                self.setFixedWidth(ancho)

    def _animar(self, desplegar: bool) -> None:
        self._animacion.stop()
        if desplegar:
            self.contenido.setVisible(True)
        inicio = self.width()
        fin = self._ancho_desplegado() if desplegar else self._ancho_plegado()
        self.setMinimumWidth(min(inicio, fin))
        self.setMaximumWidth(max(inicio, fin))
        self._animacion.setStartValue(inicio)
        self._animacion.setEndValue(fin)
        self._animacion.start()
        self.btn_alternar.update()

    def _igualar_ancho(self, valor: int) -> None:
        self.setMaximumWidth(valor)

    def _fin_animacion(self) -> None:
        self.setFixedWidth(self._ancho_desplegado() if self.btn_alternar.isChecked() else self._ancho_plegado())
        if not self.btn_alternar.isChecked():
            self.contenido.setVisible(False)
