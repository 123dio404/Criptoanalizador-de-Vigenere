"""
gui/tab_cifrador.py
Pestaña de Cifrado, Descifrado y Carga de Criptogramas para Pruebas.
Permite cifrar, descifrar y cargar textos de prueba para el análisis.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QLineEdit, QPushButton, QGroupBox, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
from core.vigenere import cifrar_vigenere, descifrar_vigenere, normalizar_texto

TEXTO_CASO_PRUEBA = (
    "SOLA O SER PROFUNDO EN EL SILENCIO DE LA NOCHE CUANDO LA LUNA ILUMINA EL CAMINO. "
    "SOLA O SER PROFUNDO EN EL MAR AZUL Y TRANSPARENTE DONDE LOS PECES NADAN EN PAZ. "
    "EL RIO ES CLARO Y PROFUNDO, EL VIENTO SUSURRA HISTORIAS ANTIGUAS EN EL VALLE. "
    "SOLA O SER PROFUNDO EN EL PENSAMIENTO DEL HOMBRE QUE BUSCA LA VERDAD Y LA SABIDURIA."
)
CLAVE_CASO_PRUEBA = "MAR"

# Alias de compatibilidad
CASO_DOCENTE_TEXTO = TEXTO_CASO_PRUEBA
CASO_DOCENTE_CLAVE = CLAVE_CASO_PRUEBA


class TabCifrador(QWidget):
    # Señal emitida cuando el usuario envía un criptograma a análisis
    criptograma_listo = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Panel de Carga Rápida de Casos de Prueba
        top_box = QGroupBox("Opciones Rápidas de Prueba")
        top_layout = QHBoxLayout(top_box)
        
        lbl_info = QLabel("Carga rápida de texto de prueba:")
        btn_prueba = QPushButton("⚡ Cargar Caso de Prueba ('SOLAOSERPROFUNDO...' + 'MAR')")
        btn_prueba.setObjectName("accentButton")
        btn_prueba.clicked.connect(self.cargar_caso_prueba)
        
        top_layout.addWidget(lbl_info)
        top_layout.addWidget(btn_prueba)
        top_layout.addStretch()
        layout.addWidget(top_box)

        # Panel de Cifrado / Simulación
        cifrador_box = QGroupBox("Generador / Interceptor de Criptogramas Vigenère")
        cifrador_layout = QVBoxLayout(cifrador_box)

        # Fila Clave
        key_layout = QHBoxLayout()
        lbl_key = QLabel("Palabra Clave:")
        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("Ejemplo: MAR, SECTRETO, CLAVE...")
        self.input_key.setText("MAR")
        self.input_key.setMaximumWidth(250)
        key_layout.addWidget(lbl_key)
        key_layout.addWidget(self.input_key)
        key_layout.addStretch()
        cifrador_layout.addLayout(key_layout)

        # Texto Claro
        lbl_plain = QLabel("Texto Plano (Mensaje a Cifrar):")
        self.txt_plain = QTextEdit()
        self.txt_plain.setPlaceholderText("Escriba o pegue el texto en claro aquí...")
        self.txt_plain.setMinimumHeight(100)
        cifrador_layout.addWidget(lbl_plain)
        cifrador_layout.addWidget(self.txt_plain)

        # Botones de Cifrado
        btn_layout = QHBoxLayout()
        self.btn_encrypt = QPushButton("🔒 Cifrar Texto con Clave")
        self.btn_encrypt.clicked.connect(self.cifrar_texto)
        self.btn_decrypt = QPushButton("🔓 Descifrar con Clave Indicada")
        self.btn_decrypt.setObjectName("secondaryButton")
        self.btn_decrypt.clicked.connect(self.descifrar_con_clave)
        self.btn_clear = QPushButton("🗑 Limpiar Campos")
        self.btn_clear.setObjectName("secondaryButton")
        self.btn_clear.clicked.connect(self.limpiar)
        
        btn_layout.addWidget(self.btn_encrypt)
        btn_layout.addWidget(self.btn_decrypt)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        cifrador_layout.addLayout(btn_layout)

        # Criptograma Resultante / Entrada para Criptoanálisis
        lbl_cipher = QLabel("Criptograma (Texto Cifrado a Interceptar y Analizar):")
        self.txt_cipher = QTextEdit()
        self.txt_cipher.setPlaceholderText("Aquí aparecerá el texto cifrado, o puede pegar un criptograma externo...")
        self.txt_cipher.setMinimumHeight(110)
        cifrador_layout.addWidget(lbl_cipher)
        cifrador_layout.addWidget(self.txt_cipher)

        # Barra de Acción para Iniciar Criptoanálisis
        action_layout = QHBoxLayout()
        self.lbl_stats = QLabel("Longitud del criptograma: 0 caracteres.")
        self.lbl_stats.setObjectName("badgeLabel")
        
        self.btn_analizar = QPushButton("🚀 Enviar Criptograma a Análisis Completo (Kasiski + IC + Chi²)")
        self.btn_analizar.clicked.connect(self.enviar_a_analisis)
        
        action_layout.addWidget(self.lbl_stats)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_analizar)
        cifrador_layout.addLayout(action_layout)

        layout.addWidget(cifrador_box)

        # Conectar cambio de texto en criptograma para actualizar contador
        self.txt_cipher.textChanged.connect(self.actualizar_contador)

    def cargar_caso_prueba(self):
        self.txt_plain.setText(TEXTO_CASO_PRUEBA)
        self.input_key.setText(CLAVE_CASO_PRUEBA)
        self.cifrar_texto()

    # Alias de compatibilidad
    cargar_caso_docente = cargar_caso_prueba

    def cifrar_texto(self):
        plain = self.txt_plain.toPlainText().strip()
        key = self.input_key.text().strip()
        if not plain:
            QMessageBox.warning(self, "Atención", "Por favor ingrese un texto plano para cifrar.")
            return
        if not key:
            QMessageBox.warning(self, "Atención", "Por favor ingrese una clave para cifrar.")
            return
        try:
            cipher = cifrar_vigenere(plain, key)
            self.txt_cipher.setText(cipher)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cifrar: {str(e)}")

    def descifrar_con_clave(self):
        cipher = self.txt_cipher.toPlainText().strip()
        key = self.input_key.text().strip()
        if not cipher:
            QMessageBox.warning(self, "Atención", "No hay criptograma para descifrar.")
            return
        if not key:
            QMessageBox.warning(self, "Atención", "Ingrese la clave para descifrar.")
            return
        try:
            plain = descifrar_vigenere(cipher, key)
            self.txt_plain.setText(plain)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al descifrar: {str(e)}")

    def limpiar(self):
        self.txt_plain.clear()
        self.txt_cipher.clear()
        self.input_key.clear()

    def actualizar_contador(self):
        cleaned = normalizar_texto(self.txt_cipher.toPlainText(), mantener_espacios=False)
        self.lbl_stats.setText(f"Longitud del criptograma: {len(cleaned)} caracteres alfabéticos.")

    def enviar_a_analisis(self):
        cipher = self.txt_cipher.toPlainText().strip()
        cleaned = normalizar_texto(cipher, mantener_espacios=False)
        if len(cleaned) < 15:
            QMessageBox.warning(
                self,
                "Texto insuficiente",
                "El criptograma debe contener al menos 15 letras para realizar criptoanálisis estadístico."
            )
            return
        self.criptograma_listo.emit(cleaned)
