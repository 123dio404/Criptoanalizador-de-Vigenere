"""
gui/styles.py
Estilos visuales modernos para la interfaz gráfica PyQt5.
Paleta de colores sobria, elegante y de alta legibilidad (tema Dark Slate / Cyber-Security).
"""

MAIN_STYLESHEET = """
QMainWindow {
    background-color: #0f172a;
}

QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Ubuntu', 'Roboto', sans-serif;
    font-size: 13px;
}

/* Encabezados y Labels */
QLabel {
    color: #cbd5e1;
}

QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #38bdf8;
}

QLabel#subtitleLabel {
    font-size: 13px;
    color: #94a3b8;
}

QLabel#badgeLabel {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
    color: #38bdf8;
}

/* Pestañas (QTabWidget) */
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #1e293b;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    border: 1px solid #334155;
    border-bottom: none;
    padding: 10px 18px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    color: #38bdf8;
    border-color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #1e293b;
    color: #e2e8f0;
}

/* Botones */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton#secondaryButton {
    background-color: #334155;
    color: #f1f5f9;
    border: 1px solid #475569;
}

QPushButton#secondaryButton:hover {
    background-color: #475569;
}

QPushButton#accentButton {
    background-color: #059669;
    color: #ffffff;
    font-weight: bold;
}

QPushButton#accentButton:hover {
    background-color: #047857;
}

/* Campos de Texto y Edición */
QTextEdit, QPlainTextEdit, QLineEdit {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}

QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus {
    border: 1px solid #38bdf8;
}

/* Tablas (QTableWidget) */
QTableWidget {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    gridline-color: #1e293b;
    color: #e2e8f0;
    selection-background-color: #1e40af;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 6px 10px;
    border: 1px solid #334155;
    font-weight: bold;
    font-size: 12px;
}

QTableCornerButton::section {
    background-color: #1e293b;
    border: 1px solid #334155;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #0f172a;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* GroupBox y Paneles */
QGroupBox {
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 14px;
    padding: 14px;
    background-color: #1e293b;
    font-weight: bold;
    color: #38bdf8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
}

/* ComboBox y SpinBox */
QComboBox, QSpinBox {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    color: #f8fafc;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    selection-background-color: #2563eb;
}

/* Diálogos y Cuadros de Mensaje / Alerta (QMessageBox / QDialog) */
QDialog, QMessageBox {
    background-color: #1e293b;
    color: #f8fafc;
}

QMessageBox QLabel, QDialog QLabel {
    color: #f1f5f9;
    background-color: transparent;
    font-size: 13px;
    font-weight: 500;
}

QMessageBox QPushButton, QDialog QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 6px 20px;
    min-width: 80px;
    font-weight: 600;
    font-size: 13px;
}

QMessageBox QPushButton:hover, QDialog QPushButton:hover {
    background-color: #1d4ed8;
}
"""

