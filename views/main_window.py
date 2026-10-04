"""
views/main_window.py
Vista principal: contenedor de pestañas, encabezado y barra de estado.
No conoce el modelo; el AppController es quien la conecta con él.
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QMessageBox, QStatusBar,
    QTabWidget, QVBoxLayout, QWidget,
)

from views.styles import MAIN_STYLESHEET
from views.widgets import BarraPestanas
from views.tab_cifrador import TabCifrador
from views.tab_descifrado import TabDescifrado
from views.tab_frecuencias import TabFrecuencias
from views.tab_friedman import TabFriedman
from views.tab_kasiski import TabKasiski

PESTANA_KASISKI = 1
PESTANA_DESCIFRADO = 4


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._construir_ui()

    def _construir_ui(self):
        self.setWindowTitle("Criptoanalizador de Vigenère — ELC107 Grupo C")
        self.resize(1280, 800)
        self.setStyleSheet(MAIN_STYLESHEET)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Encabezado superior
        header_layout = QHBoxLayout()
        title_lbl = QLabel("CRIPTOANALIZADOR DE VIGENÈRE")
        title_lbl.setObjectName("titleLabel")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        self.badge_m = QLabel("Longitud m: --")
        self.badge_m.setObjectName("badgeLabel")
        self.badge_key = QLabel("Clave: ---")
        self.badge_key.setObjectName("badgeLabel")
        header_layout.addWidget(self.badge_m)
        header_layout.addWidget(self.badge_key)
        main_layout.addLayout(header_layout)

        # Pestañas
        self.tabs = QTabWidget()
        barra = BarraPestanas()
        barra.setElideMode(Qt.ElideNone)
        barra.setExpanding(False)
        barra.setUsesScrollButtons(False)
        barra.setDrawBase(False)
        self.tabs.setTabBar(barra)
        self.tab_cifrador = TabCifrador()
        self.tab_kasiski = TabKasiski()
        self.tab_friedman = TabFriedman()
        self.tab_frecuencias = TabFrecuencias()
        self.tab_descifrado = TabDescifrado()

        self.tabs.addTab(self.tab_cifrador, "1. Interceptor / Cifrador")
        self.tabs.addTab(self.tab_kasiski, "2. Test de Kasiski")
        self.tabs.addTab(self.tab_friedman, "3. Índice de Coincidencia")
        self.tabs.addTab(self.tab_frecuencias, "4. Análisis de Frecuencias (χ²)")
        self.tabs.addTab(self.tab_descifrado, "5. Descifrado y Trazabilidad")
        main_layout.addWidget(self.tabs)

        # El ancho mínimo es el de los títulos: si la barra queda más corta, la última
        # pestaña se corta y el borde recortado se ve como una línea.
        ancho_pestanas = self.tabs.tabBar().sizeHint().width()
        self.tabs.setMinimumWidth(ancho_pestanas)
        self.resize(max(1280, ancho_pestanas + 40), 800)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.mostrar_estado(
            "Listo para iniciar. Puede ingresar un criptograma o cargar el caso de prueba en la pestaña 1."
        )

    # --- API pública para el controlador ---
    def mostrar_estado(self, mensaje: str) -> None:
        self.status_bar.showMessage(mensaje)

    def actualizar_badges(self, longitud: int, clave: str) -> None:
        self.badge_m.setText(f"Longitud m: {longitud}")
        self.badge_key.setText(f"Clave: '{clave}'")

    def ir_a_pestana(self, indice: int) -> None:
        self.tabs.setCurrentIndex(indice)

    def mostrar_info(self, titulo: str, mensaje: str) -> None:
        QMessageBox.information(self, titulo, mensaje)

    def mostrar_advertencia(self, titulo: str, mensaje: str) -> None:
        QMessageBox.warning(self, titulo, mensaje)

    def mostrar_error(self, titulo: str, mensaje: str) -> None:
        QMessageBox.critical(self, titulo, mensaje)
