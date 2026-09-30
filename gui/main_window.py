"""
gui/main_window.py
Ventana Principal de la Aplicación de Criptoanálisis de Vigenère.
Integra todas las pestañas de análisis y coordina el flujo de datos.
Asignatura: ELC107 Criptografía y Seguridad - UAGRM.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt
from gui.styles import MAIN_STYLESHEET
from gui.tab_cifrador import TabCifrador
from gui.tab_kasiski import TabKasiski
from gui.tab_friedman import TabFriedman
from gui.tab_frecuencias import TabFrecuencias
from gui.tab_descifrado import TabDescifrado
from gui.tab_defensa import TabDefensa
from core.analyzer import VigenereCryptanalyzer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyzer = VigenereCryptanalyzer()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Criptoanalizador de Vigenère — ELC107 Grupo C (UAGRM)")
        self.resize(1100, 780)
        self.setStyleSheet(MAIN_STYLESHEET)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Encabezado Superior (Header)
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_lbl = QLabel("CRIPTOANALIZADOR DE VIGENÈRE")
        title_lbl.setObjectName("titleLabel")
        subtitle_lbl = QLabel("ELC107 Criptografía y Seguridad • Grupo C • Test de Kasiski + Friedman (IC) + Chi-Cuadrado (χ²)")
        subtitle_lbl.setObjectName("subtitleLabel")
        title_box.addWidget(title_lbl)
        title_box.addWidget(subtitle_lbl)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Badges informativos de estado
        self.badge_m = QLabel("Longitud m: --")
        self.badge_m.setObjectName("badgeLabel")
        self.badge_key = QLabel("Clave: ---")
        self.badge_key.setObjectName("badgeLabel")

        header_layout.addWidget(self.badge_m)
        header_layout.addWidget(self.badge_key)
        main_layout.addLayout(header_layout)

        # Contenedor de Pestañas
        self.tabs = QTabWidget()
        
        self.tab_cifrador = TabCifrador()
        self.tab_kasiski = TabKasiski()
        self.tab_friedman = TabFriedman()
        self.tab_frecuencias = TabFrecuencias()
        self.tab_descifrado = TabDescifrado()
        self.tab_defensa = TabDefensa()

        self.tabs.addTab(self.tab_cifrador, "1. 📥 Interceptor / Cifrador")
        self.tabs.addTab(self.tab_kasiski, "2. 🔍 Test de Kasiski")
        self.tabs.addTab(self.tab_friedman, "3. 📊 Índice de Coincidencia")
        self.tabs.addTab(self.tab_frecuencias, "4. 🔑 Análisis de Frecuencias (χ²)")
        self.tabs.addTab(self.tab_descifrado, "5. 📜 Descifrado y Trazabilidad")
        self.tabs.addTab(self.tab_defensa, "6. 🎓 Guía Defensa Oral (Anti-IA)")

        main_layout.addWidget(self.tabs)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo para iniciar. Puede cargar el caso de prueba docente en la pestaña 1.")

        # Conectar señales
        self.tab_cifrador.criptograma_listo.connect(self.procesar_criptograma)
        self.tab_frecuencias.clave_confirmada.connect(self.aplicar_clave_manual)

    def procesar_criptograma(self, ciphertext: str):
        """Ejecuta el pipeline completo de criptoanálisis sobre el texto cifrado."""
        try:
            self.status_bar.showMessage("Ejecutando criptoanálisis estadístico...")
            self.analyzer.set_ciphertext(ciphertext)
            results = self.analyzer.run_full_analysis()

            m = results['determined_key_length']
            key = results['recovered_key']
            decrypted = results['decrypted_text']

            # Actualizar badges del header
            self.badge_m.setText(f"Longitud m: {m}")
            self.badge_key.setText(f"Clave: '{key}'")

            # Actualizar Pestaña Kasiski
            self.tab_kasiski.display_results(results['kasiski'])

            # Actualizar Pestaña Friedman
            self.tab_friedman.display_results(results['friedman'])

            # Actualizar Pestaña Frecuencias
            self.tab_frecuencias.set_ciphertext(ciphertext, suggested_length=m)

            # Actualizar Pestaña Descifrado
            self.tab_descifrado.display_results(
                ciphertext=results['kasiski']['clean_ciphertext'],
                plaintext=decrypted,
                key=key,
                log=results['execution_log']
            )

            # Cambiar a la pestaña de Kasiski para comenzar la visualización paso a paso
            self.tabs.setCurrentIndex(1)
            self.status_bar.showMessage(f"Análisis completado exitosamente. Clave deducida: '{key}' (Longitud m={m}).")

            QMessageBox.information(
                self,
                "Criptoanálisis Finalizado",
                f"El análisis ha finalizado exitosamente:\n\n"
                f"• Longitud estimada (Kasiski/IC): m = {m}\n"
                f"• Clave recuperada (Chi²): '{key}'\n\n"
                f"Explore las pestañas 2 a 5 para visualizar cada fase paso a paso."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error durante Criptoanálisis", f"Ocurrió un error: {str(e)}")
            self.status_bar.showMessage("Error durante el análisis.")

    def aplicar_clave_manual(self, custom_key: str):
        """Descifra el criptograma con una clave confirmada o editada por el usuario."""
        try:
            decrypted = self.analyzer.decrypt_message(custom_key)
            self.badge_key.setText(f"Clave: '{custom_key}'")
            self.badge_m.setText(f"Longitud m: {len(custom_key)}")

            self.tab_descifrado.display_results(
                ciphertext=self.analyzer.clean_ciphertext,
                plaintext=decrypted,
                key=custom_key,
                log=self.analyzer.execution_log
            )
            # Ir a pestaña descifrado
            self.tabs.setCurrentIndex(4)
            self.status_bar.showMessage(f"Mensaje descifrado con clave '{custom_key}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error al descifrar", f"Error: {str(e)}")
