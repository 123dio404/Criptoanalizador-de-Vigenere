"""
main.py
Punto de entrada del Criptoanalizador de Vigenère (arquitectura MVC).
Análisis estadístico mediante Test de Kasiski, Test de Friedman y Chi-Cuadrado (χ²).

    Modelo      -> models/       (lógica criptográfica pura)
    Vista       -> views/        (widgets PyQt5 pasivos)
    Controlador -> controllers/  (une señales de la vista con el modelo)
"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from controllers.app_controller import AppController
from models.analyzer import CriptoanalizadorVigenere
from views.main_window import MainWindow
from views.styles import MAIN_STYLESHEET


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

    modelo = CriptoanalizadorVigenere()
    vista = MainWindow()
    controlador = AppController(modelo, vista)  # noqa: F841 (se mantiene vivo mientras corre la app)
    vista.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
