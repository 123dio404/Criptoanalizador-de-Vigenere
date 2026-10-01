"""
gui/tab_descifrado.py
Pestaña de Descifrado, Trazabilidad y Exportación de Evidencia para el Informe.
Cumple con el requisito: "Evidencia de ejecución (capturas, trazas, resultados)".
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QGroupBox, QSplitter, QApplication, QMessageBox,
    QFileDialog
)
from PyQt5.QtCore import Qt


class TabDescifrado(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Barra superior con clave y estado
        top_box = QGroupBox("Estado del Descifrado")
        top_layout = QHBoxLayout(top_box)

        self.lbl_clave_usada = QLabel("Clave Aplicada: ---")
        self.lbl_clave_usada.setObjectName("badgeLabel")
        self.lbl_longitud = QLabel("Longitud: --")
        self.lbl_longitud.setObjectName("badgeLabel")
        self.lbl_caracteres = QLabel("Total Caracteres: --")
        self.lbl_caracteres.setObjectName("badgeLabel")

        top_layout.addWidget(self.lbl_clave_usada)
        top_layout.addWidget(self.lbl_longitud)
        top_layout.addWidget(self.lbl_caracteres)
        top_layout.addStretch()
        layout.addWidget(top_box)

        # Splitter con Textos y Traza de Depuración
        splitter = QSplitter(Qt.Vertical)

        # Panel de Textos
        text_panel = QWidget()
        text_layout = QHBoxLayout(text_panel)
        text_layout.setContentsMargins(0, 0, 0, 0)

        box_cipher = QGroupBox("Criptograma Interceptado")
        layout_c = QVBoxLayout(box_cipher)
        self.txt_ciphertext = QTextEdit()
        self.txt_ciphertext.setReadOnly(True)
        layout_c.addWidget(self.txt_ciphertext)
        text_layout.addWidget(box_cipher)

        box_plain = QGroupBox("Texto Plano Descifrado")
        layout_p = QVBoxLayout(box_plain)
        self.txt_plaintext = QTextEdit()
        self.txt_plaintext.setReadOnly(True)
        layout_p.addWidget(self.txt_plaintext)
        text_layout.addWidget(box_plain)

        splitter.addWidget(text_panel)

        # Panel de Traza de Depuración
        trace_box = QGroupBox("Traza de Depuración y Evidencia Criptoanalítica Paso a Paso")
        trace_layout = QVBoxLayout(trace_box)

        self.txt_trace = QTextEdit()
        self.txt_trace.setReadOnly(True)
        trace_layout.addWidget(self.txt_trace)

        btn_bar = QHBoxLayout()
        self.btn_copiar_traza = QPushButton("Copiar Traza al Portapapeles")
        self.btn_copiar_traza.setObjectName("secondaryButton")
        self.btn_copiar_traza.clicked.connect(self.copiar_traza)

        self.btn_exportar_traza = QPushButton("Guardar Traza en Archivo (.txt / .md)")
        self.btn_exportar_traza.setObjectName("secondaryButton")
        self.btn_exportar_traza.clicked.connect(self.exportar_traza)

        btn_bar.addWidget(self.btn_copiar_traza)
        btn_bar.addWidget(self.btn_exportar_traza)
        btn_bar.addStretch()
        trace_layout.addLayout(btn_bar)

        splitter.addWidget(trace_box)

        layout.addWidget(splitter)

    def display_results(self, ciphertext: str, plaintext: str, key: str, log: list):
        self.txt_ciphertext.setText(ciphertext)
        self.txt_plaintext.setText(plaintext)
        self.lbl_clave_usada.setText(f"Clave Aplicada: '{key}'")
        self.lbl_longitud.setText(f"Longitud: {len(key)}")
        self.lbl_caracteres.setText(f"Total Caracteres: {len(ciphertext)}")

        # Formatear traza enriquecida
        traza_completa = [
            "==================================================================",
            "   EVIDENCIA Y TRAZA DE CRIPTOANÁLISIS DE VIGENÈRE (ELC107)",
            "==================================================================",
            f"Longitud del Criptograma Interceptado: {len(ciphertext)} caracteres",
            f"Clave Recuperada Final: {key} (m = {len(key)})",
            "",
            "--- REGISTRO DE EVENTOS Y PASOS DE EJECUCIÓN ---"
        ]
        traza_completa.extend(log)
        traza_completa.extend([
            "",
            "--- MUESTRA DEL TEXTO DESCIFRADO ---",
            plaintext[:200] + ("..." if len(plaintext) > 200 else ""),
            "=================================================================="
        ])
        
        self.txt_trace.setText("\n".join(traza_completa))

    def copiar_traza(self):
        content = self.txt_trace.toPlainText()
        if not content:
            QMessageBox.information(self, "Aviso", "No hay traza disponible para copiar.")
            return
        QApplication.clipboard().setText(content)
        QMessageBox.information(self, "Copiado", "La traza completa ha sido copiada al portapapeles.")

    def exportar_traza(self):
        content = self.txt_trace.toPlainText()
        if not content:
            QMessageBox.information(self, "Aviso", "No hay traza para guardar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Traza de Depuración", "traza_criptoanalisis.txt", "Archivos de Texto (*.txt *.md)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                QMessageBox.information(self, "Éxito", f"Traza guardada exitosamente en:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar archivo: {str(e)}")
