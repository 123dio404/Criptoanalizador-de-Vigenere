"""
main.py
Punto de entrada del Criptoanalizador de Vigenère.
Análisis estadístico mediante Test de Kasiski, Test de Friedman y Chi-Cuadrado (χ²).
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow
from gui.styles import MAIN_STYLESHEET


def main():
    # Habilitar soporte High DPI para pantallas modernas
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Criptoanalizador de Vigenère")
    app.setOrganizationName("UAGRM")
    app.setStyleSheet(MAIN_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
