# ============================================================================
# generator/generator.py - Versión mejorada
# ============================================================================

import logging
from typing import List, Tuple, Any, Dict, Optional
import json
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class GeneradorCodigoDSL:
    def __init__(self):
        self.stats = {
            'codigos_generados': 0,
            'comandos_procesados': 0,
            'errores_generacion': 0
        }
        
        # Plantillas para diferentes tipos de comandos
        self.plantillas = {
            'accion_simple': "{accion}_{dispositivo}",
            'accion_con_ubicacion': "{accion}_{dispositivo}_en_{habitacion}",
            'accion_con_valor': "{accion}_{dispositivo}_{valor}",
            'accion_completa': "{accion}_{dispositivo}_{valor}_en_{habitacion}",
            'consulta': "ver_{dispositivo}"
        }
    
    def normalizar_ubicacion(self, habitacion: str) -> str:
        """Normalizar nombre de habitación para DSL"""
        return habitacion.lower().replace(" ", "_").replace("ñ", "n")
    
    def generar_metadatos(self, accion: str, dispositivo: str, 
                         habitacion: Optional[str], valor: Optional[int]) -> Dict[str, Any]:
        """Generar metadatos para el comando DSL"""
        return {
            'timestamp': datetime.now().isoformat(),
            'id_comando': str(uuid.uuid4())[:8],
            'accion': accion,
            'dispositivo': dispositivo,
            'habitacion': habitacion,
            'valor': valor,
            'version_dsl': '1.0'
        }
    
    def seleccionar_plantilla(self, accion: str, dispositivo: str, 
                             habitacion: Optional[str], valor: Optional[int]) -> str:
        """Seleccionar plantilla apropiada según el comando"""
        if accion == "VER":
            return self.plantillas['consulta']
        elif valor is not None and habitacion is not None:
            return self.plantillas['accion_completa']
        elif valor is not None:
            return self.plantillas['accion_con_valor']
        elif habitacion is not None:
            return self.plantillas['accion_con_ubicacion']
        else:
            return self.plantillas['accion_simple']
    
    def generate_code(self, elementos_validados: Tuple[str, str, Optional[str], Optional[int]]) -> Dict[str, Any]:
        """Generar código DSL a partir de elementos validados"""
        self.stats['comandos_procesados'] += 1
        
        try:
            accion, dispositivo, habitacion, valor = elementos_validados
            
            logger.info(f"Generando código DSL para: {accion} {dispositivo}")
            
            # Seleccionar plantilla apropiada
            plantilla = self.seleccionar_plantilla(accion, dispositivo, habitacion, valor)
            
            # Preparar parámetros para la plantilla
            parametros = {
                'accion': accion.lower(),
                'dispositivo': dispositivo.lower()
            }
            
            if habitacion:
                parametros['habitacion'] = self.normalizar_ubicacion(habitacion)
            
            if valor is not None:
                parametros['valor'] = str(valor)
            
            # Generar código DSL
            codigo_dsl = plantilla.format(**parametros)
            
            # Generar metadatos
            metadatos = self.generar_metadatos(accion, dispositivo, habitacion, valor)
            
            # Estructura completa del comando DSL
            comando_completo = {
                'dsl': codigo_dsl,
                'metadatos': metadatos,
                'parametros': {
                    'accion': accion,
                    'dispositivo': dispositivo,
                    'habitacion': habitacion,
                    'valor': valor
                }
            }
            
            self.stats['codigos_generados'] += 1
            logger.info(f"Código DSL generado: {codigo_dsl}")
            
            return comando_completo
            
        except Exception as e:
            self.stats['errores_generacion'] += 1
            logger.error(f"Error generando código DSL: {e}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """Obtener estadísticas del generador"""
        return self.stats.copy()

# Instancia global del generador
_generator_instance = None

def generate_code(elementos_validados: Tuple[str, str, Optional[str], Optional[int]]) -> str:
    """Función principal de generación de código DSL"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = GeneradorCodigoDSL()
    
    comando_completo = _generator_instance.generate_code(elementos_validados)
    return comando_completo['dsl']