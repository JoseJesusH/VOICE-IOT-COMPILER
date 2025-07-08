# ============================================================================
# semantic/validator.py - Versión corregida completa
# ============================================================================

import logging
from typing import List, Tuple, Any, Dict, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ExcepcionSemantica(Exception):
    """Excepción personalizada para errores semánticos"""
    def __init__(self, mensaje: str, contexto: str = ""):
        self.mensaje = mensaje
        self.contexto = contexto
        super().__init__(self.mensaje)

class ValidadorSemanticoIoT:
    def __init__(self):
        # Contexto del dominio IoT
        self.dispositivos_validos = {
            "LUZ", "VENTILADOR", "TELEVISOR", "CALEFACTOR", 
            "VOLUMEN", "BRILLO", "BATERIA", "HORA"
        }
        
        self.habitaciones_validas = {
            "COCINA", "DORMITORIO", "SALA", "BAÑO", "OFICINA"
        }
        
        # Compatibilidad acción-dispositivo
        self.compatibilidad = {
            "ENCENDER": {"LUZ", "VENTILADOR", "TELEVISOR", "CALEFACTOR"},
            "APAGAR": {"LUZ", "VENTILADOR", "TELEVISOR", "CALEFACTOR"},
            "SUBIR": {"VOLUMEN", "BRILLO"},
            "BAJAR": {"VOLUMEN", "BRILLO"},
            "AJUSTAR": {"VOLUMEN", "BRILLO"},
            "SILENCIAR": {"VOLUMEN"},
            "ACTIVAR": {"VOLUMEN"},
            "VER": {"BATERIA", "HORA"}
        }
        
        # Rangos válidos para valores numéricos
        self.rangos_validos = {
            "VOLUMEN": (0, 100),
            "BRILLO": (0, 100)
        }
        
        # Estado simulado de dispositivos
        self.estado_dispositivos = {
            "LUZ": {"encendido": False, "ubicaciones": set()},
            "VENTILADOR": {"encendido": False, "ubicaciones": set()},
            "TELEVISOR": {"encendido": False, "ubicaciones": set()},
            "CALEFACTOR": {"encendido": False, "ubicaciones": set()},
            "VOLUMEN": {"nivel": 50, "silenciado": False},
            "BRILLO": {"nivel": 70}
        }
        
        self.stats = {
            'comandos_validados': 0,
            'errores_semanticos': 0,
            'validaciones_exitosas': 0
        }
    
    def extraer_elementos(self, tokens: List[Tuple[str, Any]]) -> Tuple[str, str, Optional[str], Optional[int]]:
        """Extraer elementos semánticos del comando"""
        accion = None
        dispositivo = None
        habitacion = None
        valor = None
        
        i = 0
        while i < len(tokens):
            tipo, val = tokens[i]
            
            if tipo in self.compatibilidad.keys():
                accion = tipo
            elif tipo in self.dispositivos_validos:
                dispositivo = tipo
            elif tipo in self.habitaciones_validas:
                habitacion = tipo
            elif tipo == "NUMERO":
                valor = val
            
            i += 1
        
        return accion, dispositivo, habitacion, valor
    
    def validar_existencia(self, dispositivo: str) -> None:
        """Validar que el dispositivo existe en el contexto"""
        if dispositivo not in self.dispositivos_validos:
            raise ExcepcionSemantica(
                f"Dispositivo desconocido: {dispositivo}",
                "dispositivos_disponibles"
            )
    
    def validar_compatibilidad(self, accion: str, dispositivo: str) -> None:
        """Validar compatibilidad acción-dispositivo"""
        if accion not in self.compatibilidad:
            raise ExcepcionSemantica(
                f"Acción desconocida: {accion}",
                "acciones_disponibles"
            )
        
        if dispositivo not in self.compatibilidad[accion]:
            dispositivos_compatibles = ", ".join(self.compatibilidad[accion])
            raise ExcepcionSemantica(
                f"La acción '{accion}' no es compatible con '{dispositivo}'. "
                f"Dispositivos compatibles: {dispositivos_compatibles}",
                "compatibilidad_accion_dispositivo"
            )
    
    def validar_habitacion(self, habitacion: Optional[str]) -> None:
        """Validar que la habitación existe"""
        if habitacion and habitacion not in self.habitaciones_validas:
            habitaciones_disponibles = ", ".join(self.habitaciones_validas)
            raise ExcepcionSemantica(
                f"Habitación no reconocida: {habitacion}. "
                f"Habitaciones disponibles: {habitaciones_disponibles}",
                "habitaciones_disponibles"
            )
    
    def validar_rango_valor(self, dispositivo: str, valor: Optional[int]) -> None:
        """Validar que el valor está en rango válido"""
        if valor is not None and dispositivo in self.rangos_validos:
            min_val, max_val = self.rangos_validos[dispositivo]
            if not (min_val <= valor <= max_val):
                raise ExcepcionSemantica(
                    f"Valor {valor} fuera de rango para {dispositivo}. "
                    f"Rango válido: {min_val}-{max_val}",
                    "rango_valores"
                )
    
    def validar_transicion_estado(self, dispositivo: str, accion: str) -> None:
        """Validar que la transición de estado es válida"""
        if dispositivo in self.estado_dispositivos:
            estado_actual = self.estado_dispositivos[dispositivo]
            
            # Validaciones específicas por tipo de dispositivo
            if dispositivo in ["LUZ", "VENTILADOR", "TELEVISOR", "CALEFACTOR"]:
                if accion == "ENCENDER" and estado_actual.get("encendido", False):
                    logger.warning(f"{dispositivo} ya está encendido")
                elif accion == "APAGAR" and not estado_actual.get("encendido", False):
                    logger.warning(f"{dispositivo} ya está apagado")
            
            elif dispositivo == "VOLUMEN":
                if accion == "SILENCIAR" and estado_actual.get("silenciado", False):
                    logger.warning("El volumen ya está silenciado")
                elif accion == "ACTIVAR" and not estado_actual.get("silenciado", False):
                    logger.warning("El volumen ya está activo")
    
    def validar(self, tokens: List[Tuple[str, Any]]) -> Tuple[str, str, Optional[str], Optional[int]]:
        """Validación semántica principal"""
        self.stats['comandos_validados'] += 1
        
        try:
            logger.info("Iniciando validación semántica")
            
            # Extraer elementos del comando
            accion, dispositivo, habitacion, valor = self.extraer_elementos(tokens)
            
            logger.info(f"Elementos extraídos - Acción: {accion}, Dispositivo: {dispositivo}, "
                       f"Habitación: {habitacion}, Valor: {valor}")
            
            # Validaciones obligatorias
            if not dispositivo:
                raise ExcepcionSemantica("No se especificó dispositivo válido")
            
            if not accion:
                raise ExcepcionSemantica("No se especificó acción válida")
            
            # Validaciones específicas
            self.validar_existencia(dispositivo)
            self.validar_compatibilidad(accion, dispositivo)
            self.validar_habitacion(habitacion)
            self.validar_rango_valor(dispositivo, valor)
            self.validar_transicion_estado(dispositivo, accion)
            
            self.stats['validaciones_exitosas'] += 1
            logger.info("Validación semántica exitosa")
            
            return accion, dispositivo, habitacion, valor
            
        except ExcepcionSemantica as e:
            self.stats['errores_semanticos'] += 1
            logger.error(f"Error semántico: {e.mensaje}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """Obtener estadísticas del validador"""
        return self.stats.copy()

# Instancia global del validador
_validator_instance = None

def validar(tokens: List[Tuple[str, Any]]) -> Tuple[str, str, Optional[str], Optional[int]]:
    """Función principal de validación semántica"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ValidadorSemanticoIoT()
    
    return _validator_instance.validar(tokens)