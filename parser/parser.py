# ============================================================================
# parser/parser.py - Versión corregida completa
# ============================================================================

import logging
from typing import List, Tuple, Any, Dict

logger = logging.getLogger(__name__)

class ExcepcionSintactica(Exception):
    """Excepción personalizada para errores sintácticos"""
    def __init__(self, mensaje: str, posicion: int = -1):
        self.mensaje = mensaje
        self.posicion = posicion
        super().__init__(self.mensaje)

class ParserIoT:
    def __init__(self):
        self.tokens = []
        self.posicion = 0
        self.stats = {
            'comandos_analizados': 0,
            'errores_sintacticos': 0,
            'comandos_validos': 0
        }
    
    def token_actual(self) -> Tuple[str, Any]:
        """Obtener token en posición actual"""
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        return ("EOF", None)
    
    def avanzar(self) -> None:
        """Avanzar a siguiente token"""
        self.posicion += 1
    
    def consumir(self, tipo_esperado: str) -> Tuple[str, Any]:
        """Consumir token del tipo esperado"""
        token = self.token_actual()
        if token[0] != tipo_esperado:
            raise ExcepcionSintactica(
                f"Se esperaba {tipo_esperado}, se encontró {token[0]}",
                self.posicion
            )
        self.avanzar()
        return token
    
    def analizar_consulta(self) -> bool:
        """Analizar comando de consulta: VER (BATERIA|HORA)"""
        try:
            self.consumir("VER")
            token_siguiente = self.token_actual()
            
            if token_siguiente[0] in ["BATERIA", "HORA"]:
                self.avanzar()
                return True
            else:
                raise ExcepcionSintactica(
                    f"Después de VER se esperaba BATERIA o HORA, se encontró {token_siguiente[0]}"
                )
        except ExcepcionSintactica:
            raise
    
    def analizar_accion_simple(self) -> bool:
        """Analizar acción simple: ACCION DISPOSITIVO [EN HABITACION]"""
        try:
            # Consumir acción
            token_accion = self.token_actual()
            if token_accion[0] in ["ENCENDER", "APAGAR", "SUBIR", "BAJAR", "SILENCIAR", "ACTIVAR"]:
                self.avanzar()
            else:
                raise ExcepcionSintactica(f"Acción no válida: {token_accion[0]}")
            
            # Consumir dispositivo
            token_dispositivo = self.token_actual()
            if token_dispositivo[0] in ["LUZ", "VENTILADOR", "TELEVISOR", "CALEFACTOR", "VOLUMEN", "BRILLO"]:
                self.avanzar()
            else:
                raise ExcepcionSintactica(f"Dispositivo no válido: {token_dispositivo[0]}")
            
            # Opcional: EN HABITACION
            if self.token_actual()[0] == "EN":
                self.avanzar()
                token_habitacion = self.token_actual()
                if token_habitacion[0] in ["COCINA", "DORMITORIO", "SALA", "BAÑO", "OFICINA"]:
                    self.avanzar()
                elif token_habitacion[0] == "EOF":
                    # Comando incompleto pero válido hasta aquí
                    logger.warning("Comando incompleto: falta especificar habitación")
                    return True
                else:
                    raise ExcepcionSintactica(f"Habitación no válida: {token_habitacion[0]}")
            
            return True
        except ExcepcionSintactica:
            raise
    
    def analizar_accion_con_valor(self) -> bool:
        """Analizar acción con valor: AJUSTAR DISPOSITIVO [A NUMERO] [EN HABITACION]"""
        try:
            self.consumir("AJUSTAR")
            
            # Dispositivo
            token_dispositivo = self.token_actual()
            if token_dispositivo[0] in ["VOLUMEN", "BRILLO"]:
                self.avanzar()
            else:
                raise ExcepcionSintactica(f"Dispositivo no compatible con AJUSTAR: {token_dispositivo[0]}")
            
            # Opcional: A NUMERO
            if self.token_actual()[0] == "A":
                self.avanzar()
                if self.token_actual()[0] == "NUMERO":
                    self.avanzar()
                elif self.token_actual()[0] == "EOF":
                    raise ExcepcionSintactica("Se esperaba un número después de 'a'")
                else:
                    raise ExcepcionSintactica(f"Se esperaba número, se encontró {self.token_actual()[0]}")
            elif self.token_actual()[0] == "EOF":
                # Comando incompleto pero podemos manejarlo
                logger.warning("Comando 'ajustar' sin valor específico")
                return True
            
            # Opcional: EN HABITACION
            if self.token_actual()[0] == "EN":
                self.avanzar()
                token_habitacion = self.token_actual()
                if token_habitacion[0] in ["COCINA", "DORMITORIO", "SALA", "BAÑO", "OFICINA"]:
                    self.avanzar()
                elif token_habitacion[0] == "EOF":
                    logger.warning("Comando incompleto: falta especificar habitación")
                    return True
                else:
                    raise ExcepcionSintactica(f"Habitación no válida: {token_habitacion[0]}")
            
            return True
        except ExcepcionSintactica:
            raise
    
    def analizar(self, tokens: List[Tuple[str, Any]]) -> bool:
        """Análisis sintáctico principal"""
        self.stats['comandos_analizados'] += 1
        self.tokens = tokens
        self.posicion = 0
        
        if not tokens:
            self.stats['errores_sintacticos'] += 1
            raise ExcepcionSintactica("Comando vacío")
        
        try:
            primer_token = self.token_actual()
            logger.info(f"Analizando comando que inicia con: {primer_token[0]}")
            
            if primer_token[0] == "VER":
                self.analizar_consulta()
            elif primer_token[0] == "AJUSTAR":
                self.analizar_accion_con_valor()
            elif primer_token[0] in ["ENCENDER", "APAGAR", "SUBIR", "BAJAR", "SILENCIAR", "ACTIVAR"]:
                self.analizar_accion_simple()
            else:
                raise ExcepcionSintactica(f"Comando no reconocido: {primer_token[0]}")
            
            # No es necesario verificar tokens adicionales para comandos incompletos válidos
            
            self.stats['comandos_validos'] += 1
            logger.info("Análisis sintáctico exitoso")
            return True
            
        except ExcepcionSintactica as e:
            self.stats['errores_sintacticos'] += 1
            logger.error(f"Error sintáctico: {e.mensaje}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """Obtener estadísticas del parser"""
        return self.stats.copy()

# Instancia global del parser
_parser_instance = None

def analizar(tokens: List[Tuple[str, Any]]) -> bool:
    """Función principal de análisis sintáctico"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = ParserIoT()
    
    return _parser_instance.analizar(tokens)