from typing import Dict, Sequence, Tuple

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout,
    QWidget,
)

from views.tabla_vigenere import PanelTablaVigenere


class TabCifrador(QWidget):
    cargar_caso_solicitado = pyqtSignal()
    cifrar_solicitado = pyqtSignal(str, str, bool)
    descifrar_solicitado = pyqtSignal(str, str, bool)
    analizar_solicitado = pyqtSignal(str)
    criptograma_modificado = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(10)

        cifrador_box = QGroupBox("Generador")
        cifrador_layout = QVBoxLayout(cifrador_box)

        key_layout = QHBoxLayout()
        lbl_key = QLabel("Palabra Clave:")
        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("Ejemplo: MAR, SECRETO, CLAVE...")
        self.input_key.setText("MAR")
        self.input_key.setMaximumWidth(250)

        self.chk_formato = QCheckBox("Mantener espacios y caracteres especiales")
        self.chk_formato.setToolTip(
            "Activado: se respetan espacios, signos y mayúsculas/minúsculas; solo se cifran las letras A-Z.\n"
            "Desactivado: el texto se normaliza a mayúsculas A-Z seguidas, sin espacios ni signos."
        )

        key_layout.addWidget(lbl_key)
        key_layout.addWidget(self.input_key)
        key_layout.addSpacing(16)
        key_layout.addWidget(self.chk_formato)
        key_layout.addStretch()
        cifrador_layout.addLayout(key_layout)

        lbl_plain = QLabel("Mensaje a Cifrar:")
        self.txt_plain = QTextEdit()
        self.txt_plain.setPlaceholderText("Escriba o pegue el texto en claro aquí...")
        self.txt_plain.setMinimumHeight(100)
        cifrador_layout.addWidget(lbl_plain)
        cifrador_layout.addWidget(self.txt_plain)

        btn_layout = QHBoxLayout()
        self.btn_encrypt = QPushButton("Cifrar")
        self.btn_encrypt.clicked.connect(
            lambda: self.cifrar_solicitado.emit(self.texto_plano(), self.clave(), self.conservar_formato())
        )
        self.btn_decrypt = QPushButton("Descifrar")
        self.btn_decrypt.setObjectName("secondaryButton")
        self.btn_decrypt.clicked.connect(
            lambda: self.descifrar_solicitado.emit(self.criptograma(), self.clave(), self.conservar_formato())
        )
        self.btn_clear = QPushButton("Limpiar Campos")
        self.btn_clear.setObjectName("secondaryButton")
        self.btn_clear.clicked.connect(self.limpiar)

        self.btn_prueba = QPushButton("Caso de Prueba")
        self.btn_prueba.setObjectName("accentButton")
        self.btn_prueba.clicked.connect(self.cargar_caso_solicitado)

        btn_layout.addWidget(self.btn_encrypt)
        btn_layout.addWidget(self.btn_decrypt)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_prueba)
        btn_layout.addStretch()
        cifrador_layout.addLayout(btn_layout)

        lbl_cipher = QLabel("Criptograma:")
        self.txt_cipher = QTextEdit()
        self.txt_cipher.setPlaceholderText("Aquí aparecerá el texto cifrado, o puede pegar un criptograma externo...")
        self.txt_cipher.setMinimumHeight(110)
        cifrador_layout.addWidget(lbl_cipher)
        cifrador_layout.addWidget(self.txt_cipher)

        action_layout = QHBoxLayout()
        self.lbl_stats = QLabel("Longitud del criptograma: 0 caracteres.")
        self.lbl_stats.setObjectName("badgeLabel")

        self.btn_analizar = QPushButton("Análisis(Kasiski + IC + Chi²)")
        self.btn_analizar.clicked.connect(lambda: self.analizar_solicitado.emit(self.criptograma()))

        action_layout.addWidget(self.lbl_stats)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_analizar)
        cifrador_layout.addLayout(action_layout)

        layout.addWidget(cifrador_box, 1)

        self.panel_tabla = PanelTablaVigenere()
        layout.addWidget(self.panel_tabla)

    def resizeEvent(self, evento) -> None:
        super().resizeEvent(evento)
        self.panel_tabla.ajustar_si_desplegado()

        self.txt_cipher.textChanged.connect(
            lambda: self.criptograma_modificado.emit(self.criptograma())
        )

    def texto_plano(self) -> str:
        return self.txt_plain.toPlainText()

    def clave(self) -> str:
        return self.input_key.text().strip()

    def criptograma(self) -> str:
        return self.txt_cipher.toPlainText()

    def conservar_formato(self) -> bool:
        return self.chk_formato.isChecked()

    def set_texto_plano(self, texto: str) -> None:
        self.txt_plain.setPlainText(texto)

    def set_clave(self, clave: str) -> None:
        self.input_key.setText(clave)

    def set_criptograma(self, texto: str) -> None:
        self.txt_cipher.setPlainText(texto)

    def set_contador(self, cantidad: int) -> None:
        self.lbl_stats.setText(f"Longitud del criptograma: {cantidad} caracteres alfabéticos.")

    def mostrar_tabla_vigenere(self, filas: Sequence[str], letras_clave: str,
                               frecuencias: Dict[Tuple[str, str], int]) -> None:
        self.panel_tabla.mostrar_tabla(filas, letras_clave, frecuencias)
        self.panel_tabla.desplegar()

    def limpiar(self) -> None:
        self.txt_plain.clear()
        self.txt_cipher.clear()
        self.input_key.clear()
