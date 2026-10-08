from typing import Any, Dict, Optional

from controllers import formateo
from models.analyzer import CriptoanalizadorVigenere
from models.caso_prueba import CLAVE_CASO_PRUEBA, TEXTO_CASO_PRUEBA
from models.vigenere import (
    cifrar_vigenere, contar_intersecciones, descifrar_vigenere, generar_tabla_vigenere,
    normalizar_texto,
)
from views.main_window import MainWindow, PESTANA_DESCIFRADO, PESTANA_KASISKI

MIN_LETRAS_ANALISIS = 15
MAX_LONGITUD_CLAVE_UI = 25


class AppController:
    def __init__(self, modelo: CriptoanalizadorVigenere, vista: MainWindow):
        self.modelo = modelo
        self.vista = vista
        self._exploracion: Optional[Dict[str, Any]] = None

        self._inicializar_vistas()
        self._conectar_senales()

    def _inicializar_vistas(self) -> None:
        self.vista.tab_friedman.mostrar_referencias(*formateo.textos_referencia_friedman())

    def _conectar_senales(self) -> None:
        cif = self.vista.tab_cifrador
        cif.cargar_caso_solicitado.connect(self.cargar_caso_prueba)
        cif.cifrar_solicitado.connect(self.cifrar)
        cif.descifrar_solicitado.connect(self.descifrar_con_clave)
        cif.analizar_solicitado.connect(self.analizar)
        cif.criptograma_modificado.connect(self.actualizar_contador)

        frec = self.vista.tab_frecuencias
        frec.longitud_cambiada.connect(self.explorar_longitud)
        frec.columna_seleccionada.connect(self.mostrar_columna)
        frec.confirmar_clave_solicitado.connect(self.confirmar_clave)

        desc = self.vista.tab_descifrado
        desc.exportar_traza_solicitado.connect(self.exportar_traza)
        desc.aviso.connect(self.vista.mostrar_info)

    def cargar_caso_prueba(self) -> None:
        cif = self.vista.tab_cifrador
        cif.set_texto_plano(TEXTO_CASO_PRUEBA)
        cif.set_clave(CLAVE_CASO_PRUEBA)
        self.cifrar(TEXTO_CASO_PRUEBA, CLAVE_CASO_PRUEBA, cif.conservar_formato())

    def cifrar(self, texto_plano: str, clave: str, conservar_formato: bool = False) -> None:
        if not texto_plano.strip():
            self.vista.mostrar_advertencia("Atención", "Por favor ingrese un texto plano para cifrar.")
            return
        if not clave:
            self.vista.mostrar_advertencia("Atención", "Por favor ingrese una clave para cifrar.")
            return
        try:
            criptograma = cifrar_vigenere(texto_plano, clave, conservar_formato)
        except ValueError as e:
            self.vista.mostrar_error("Error", f"Error al cifrar: {e}")
            return
        self.vista.tab_cifrador.set_criptograma(criptograma)
        self._mostrar_clave_usada(clave, texto_plano, conservar_formato)

    def descifrar_con_clave(self, criptograma: str, clave: str, conservar_formato: bool = False) -> None:
        if not criptograma.strip():
            self.vista.mostrar_advertencia("Atención", "No hay criptograma para descifrar.")
            return
        if not clave:
            self.vista.mostrar_advertencia("Atención", "Ingrese la clave para descifrar.")
            return
        try:
            texto_plano = descifrar_vigenere(criptograma, clave, conservar_formato)
        except ValueError as e:
            self.vista.mostrar_error("Error", f"Error al descifrar: {e}")
            return
        self.vista.tab_cifrador.set_texto_plano(texto_plano)
        self._mostrar_clave_usada(clave, texto_plano, conservar_formato)

    def _mostrar_clave_usada(self, clave: str, texto_claro: str, conservar_formato: bool) -> None:
        clave_usada = normalizar_texto(clave)
        self.vista.actualizar_badges(len(clave_usada), clave_usada)
        frecuencias = contar_intersecciones(texto_claro, clave, conservar_formato)
        self.vista.tab_cifrador.mostrar_tabla_vigenere(
            generar_tabla_vigenere(), clave_usada, frecuencias
        )

    def actualizar_contador(self, criptograma: str) -> None:
        self.vista.tab_cifrador.set_contador(len(normalizar_texto(criptograma)))

    def analizar(self, criptograma: str) -> None:
        limpio = normalizar_texto(criptograma)
        if len(limpio) < MIN_LETRAS_ANALISIS:
            self.vista.mostrar_advertencia(
                "Texto insuficiente",
                f"El criptograma debe contener al menos {MIN_LETRAS_ANALISIS} letras "
                "para realizar criptoanálisis estadístico."
            )
            return

        try:
            self.vista.mostrar_estado("Ejecutando criptoanálisis estadístico...")
            self.modelo.cargar_criptograma(limpio)
            resultados = self.modelo.ejecutar_analisis_completo()
        except Exception as e:
            self.vista.mostrar_error("Error durante Criptoanálisis", f"Ocurrió un error: {e}")
            self.vista.mostrar_estado("Error durante el análisis.")
            return

        m = resultados['determined_key_length']
        clave = resultados['recovered_key']

        self.vista.actualizar_badges(m, clave)
        self._mostrar_kasiski(resultados['kasiski'])
        self._mostrar_friedman(resultados['friedman'])
        self._iniciar_frecuencias(m)
        self._mostrar_descifrado(clave)

        self.vista.ir_a_pestana(PESTANA_KASISKI)
        self.vista.mostrar_estado(f"Análisis completado exitosamente. Clave deducida: '{clave}' (Longitud m={m}).")
        self.vista.mostrar_info(
            "Criptoanálisis Finalizado",
            "El análisis ha finalizado exitosamente:\n\n"
            f"• Longitud estimada (Kasiski/IC): m = {m}\n"
            f"• Clave recuperada (Chi²): '{clave}'\n\n"
            "Explore las pestañas 2 a 5 para visualizar cada fase paso a paso."
        )

    def _mostrar_kasiski(self, kasiski: Dict[str, Any]) -> None:
        tab = self.vista.tab_kasiski
        tab.mostrar_resumen(*formateo.resumen_kasiski(kasiski))
        tab.mostrar_ngramas(formateo.filas_ngramas(kasiski))
        tab.mostrar_factores(formateo.filas_factores(kasiski))

    def _mostrar_friedman(self, friedman: Dict[str, Any]) -> None:
        tab = self.vista.tab_friedman
        tab.mostrar_metricas(*formateo.metricas_friedman(friedman))
        tab.mostrar_periodos(formateo.titulo_tabla_periodos(friedman), formateo.filas_periodos(friedman))

    def _iniciar_frecuencias(self, longitud_sugerida: int) -> None:
        maximo = min(MAX_LONGITUD_CLAVE_UI, len(self.modelo.clean_ciphertext))
        longitud = min(longitud_sugerida, maximo)
        self.vista.tab_frecuencias.configurar_longitud(maximo, longitud)
        self.explorar_longitud(longitud)

    def explorar_longitud(self, longitud: int) -> None:
        if not self.modelo.clean_ciphertext:
            return
        self._exploracion = self.modelo.explorar_longitud_clave(longitud)
        tab = self.vista.tab_frecuencias
        clave = self._exploracion['recovered_key']
        tab.mostrar_clave(clave)
        tab.mostrar_columnas(formateo.etiquetas_columnas(clave, longitud))
        self.mostrar_columna(0)

    def mostrar_columna(self, indice: int) -> None:
        if not self._exploracion:
            return
        columnas = self._exploracion['columns']
        if not 0 <= indice < len(columnas):
            return
        columna = columnas[indice]
        self.vista.tab_frecuencias.mostrar_detalle_columna(
            formateo.info_columna(columna), formateo.filas_candidatas(columna)
        )

    def confirmar_clave(self) -> None:
        if not self._exploracion:
            return
        clave = self._exploracion['recovered_key']
        try:
            self.modelo.descifrar_mensaje(clave)
        except ValueError as e:
            self.vista.mostrar_error("Error al descifrar", f"Error: {e}")
            return
        self.vista.actualizar_badges(len(clave), clave)
        self._mostrar_descifrado(clave)
        self.vista.ir_a_pestana(PESTANA_DESCIFRADO)
        self.vista.mostrar_estado(f"Mensaje descifrado con clave '{clave}'.")

    def _mostrar_descifrado(self, clave: str) -> None:
        traza = formateo.construir_traza(
            self.modelo.clean_ciphertext, self.modelo.decrypted_text, clave, self.modelo.execution_log
        )
        self.vista.tab_descifrado.mostrar_resultados(
            self.modelo.clean_ciphertext, self.modelo.decrypted_text, clave, traza
        )

    def exportar_traza(self, ruta: str, contenido: str) -> None:
        try:
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
        except OSError as e:
            self.vista.mostrar_error("Error", f"Error al guardar archivo: {e}")
            return
        self.vista.mostrar_info("Éxito", f"Traza guardada exitosamente en:\n{ruta}")
