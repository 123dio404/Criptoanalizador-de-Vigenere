"""
views/tab_descifrado.py
Vista de la pestaña 5: Descifrado, Trazabilidad y Exportación de Evidencia para el Informe.
Cumple con el requisito: "Evidencia de ejecución (capturas, trazas, resultados)".
Vista pasiva: la escritura a disco la realiza el controlador.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QTextEdit, QVBoxLayout, QWidget,
)


class TabDescifrado(QWidget):
    # (ruta_elegida, contenido_de_la_traza)
    exportar_traza_solicitado = pyqtSignal(str, str)
    # Mensajes informativos para la ventana principal: (titulo, mensaje)
    aviso = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Barra superior con clave y estado
        top_box = QGroupBox("Estado del Descifrado")
        top_layout = QHBoxLayout(top_box)

        self.lbl_clave_usada = QLabel("Clave Aplicada: ---")
        self.lbl_longitud = QLabel("Longitud: --")
        self.lbl_caracteres = QLabel("Total Caracteres: --")
        for lbl in (self.lbl_clave_usada, self.lbl_longitud, self.lbl_caracteres):
            lbl.setObjectName("badgeLabel")
            top_layout.addWidget(lbl)
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
        self.btn_copiar_traza = QPushButton("Copiar")
        self.btn_copiar_traza.setObjectName("secondaryButton")
        self.btn_copiar_traza.clicked.connect(self._copiar_traza)

        self.btn_exportar_traza = QPushButton("Guardar")
        self.btn_exportar_traza.setObjectName("secondaryButton")
        self.btn_exportar_traza.clicked.connect(self._exportar_traza)

        btn_bar.addWidget(self.btn_copiar_traza)
        btn_bar.addWidget(self.btn_exportar_traza)
        btn_bar.addStretch()
        trace_layout.addLayout(btn_bar)

        splitter.addWidget(trace_box)
        layout.addWidget(splitter, 1)

    # --- API pública para el controlador ---
    def mostrar_resultados(self, criptograma: str, texto_plano: str, clave: str, traza: str) -> None:
        self.txt_ciphertext.setPlainText(criptograma)
        self.txt_plaintext.setPlainText(texto_plano)
        self.lbl_clave_usada.setText(f"Clave Aplicada: '{clave}'")
        self.lbl_longitud.setText(f"Longitud: {len(clave)}")
        self.lbl_caracteres.setText(f"Total Caracteres: {len(criptograma)}")
        self.txt_trace.setPlainText(traza)

    # --- Acciones puramente de interfaz ---
    def _copiar_traza(self) -> None:
        contenido = self.txt_trace.toPlainText()
        if not contenido:
            self.aviso.emit("Aviso", "No hay traza disponible para copiar.")
            return
        QApplication.clipboard().setText(contenido)
        self.aviso.emit("Copiado", "La traza completa ha sido copiada al portapapeles.")

    def _exportar_traza(self) -> None:
        contenido = self.txt_trace.toPlainText()
        if not contenido:
            self.aviso.emit("Aviso", "No hay traza para guardar.")
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Traza de Depuración", "traza_criptoanalisis.txt",
            "Archivos de Texto (*.txt *.md)"
        )
        if ruta:
            self.exportar_traza_solicitado.emit(ruta, contenido)
