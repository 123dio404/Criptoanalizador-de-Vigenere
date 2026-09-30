"""
main.py
Punto de Entrada del Criptoanalizador de Vigenère.
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.
Grupo C: Criptoanálisis de Vigenère con Kasiski, Friedman y Chi-cuadrado.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow


def main():
    # Habilitar soporte High DPI para pantallas modernas
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Criptoanalizador de Vigenere - ELC107 Grupo C")
    app.setOrganizationName("UAGRM")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
