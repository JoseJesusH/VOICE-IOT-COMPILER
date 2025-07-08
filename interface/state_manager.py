# ============================================================================
# interface/state_manager.py - Versión corregida y completa
# ============================================================================

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class GestorEstadoIoT:
    def __init__(self, archivo_estado: str = "estado_dispositivos.json"):
        self.archivo_estado = Path(archivo_estado)
        self.estado_dispositivos = {}
        self.historial_comandos = []
        self.cargar_estado()
    
    def cargar_estado(self):
        """Cargar estado de dispositivos desde archivo"""
        try:
            if self.archivo_estado.exists():
                with open(self.archivo_estado, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.estado_dispositivos = data.get('dispositivos', {})
                    self.historial_comandos = data.get('historial', [])
                logger.info("Estado de dispositivos cargado exitosamente")
            else:
                self.inicializar_estado_por_defecto()
        except Exception as e:
            logger.error(f"Error cargando estado: {e}")
            self.inicializar_estado_por_defecto()
    
    def inicializar_estado_por_defecto(self):
        """Inicializar estado por defecto de dispositivos"""
        self.estado_dispositivos = {
            "luz": {
                "encendido": False,
                "ubicaciones": {},
                "ultima_accion": None,
                "accion": "apagado",  # Para compatibilidad
                "timestamp": datetime.now().isoformat()
            },
            "ventilador": {
                "encendido": False,
                "ubicaciones": {},
                "velocidad": 1,
                "ultima_accion": None,
                "accion": "apagado",
                "timestamp": datetime.now().isoformat()
            },
            "televisor": {
                "encendido": False,
                "ubicaciones": {},
                "canal": 1,
                "volumen": 50,
                "ultima_accion": None,
                "accion": "apagado",
                "timestamp": datetime.now().isoformat()
            },
            "calefactor": {
                "encendido": False,
                "ubicaciones": {},
                "temperatura": 20,
                "ultima_accion": None,
                "accion": "apagado",
                "timestamp": datetime.now().isoformat()
            },
            "volumen": {
                "nivel": 50,
                "silenciado": False,
                "ultima_accion": None,
                "accion": "normal",
                "timestamp": datetime.now().isoformat()
            },
            "brillo": {
                "nivel": 70,
                "ultima_accion": None,
                "accion": "normal",
                "timestamp": datetime.now().isoformat()
            }
        }
        logger.info("Estado por defecto inicializado")
    
    def guardar_estado(self):
        """Guardar estado actual en archivo"""
        try:
            data = {
                'dispositivos': self.estado_dispositivos,
                'historial': self.historial_comandos[-100:],  # Mantener últimos 100
                'ultima_actualizacion': datetime.now().isoformat()
            }
            
            with open(self.archivo_estado, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("Estado guardado exitosamente")
        except Exception as e:
            logger.error(f"Error guardando estado: {e}")
    
    def actualizar_dispositivo(self, dispositivo: str, ubicacion: Optional[str], 
                              accion: str, valor: Optional[Any] = None):
        """Actualizar estado de dispositivo"""
        try:
            if dispositivo not in self.estado_dispositivos:
                self.estado_dispositivos[dispositivo] = {}
            
            estado = self.estado_dispositivos[dispositivo]
            estado['ultima_accion'] = accion
            estado['accion'] = accion  # Para compatibilidad con main.py original
            estado['timestamp'] = datetime.now().isoformat()
            
            # Actualizar estado específico según dispositivo y acción
            if dispositivo in ["luz", "ventilador", "televisor", "calefactor"]:
                if accion == "encender":
                    estado['encendido'] = True
                    estado['accion'] = "encendido"
                    if ubicacion:
                        if 'ubicaciones' not in estado:
                            estado['ubicaciones'] = {}
                        estado['ubicaciones'][ubicacion] = True
                elif accion == "apagar":
                    estado['encendido'] = False
                    estado['accion'] = "apagado"
                    if ubicacion and 'ubicaciones' in estado:
                        estado['ubicaciones'][ubicacion] = False
            
            elif dispositivo == "volumen":
                if accion == "ajustar" and valor is not None:
                    estado['nivel'] = valor
                    estado['silenciado'] = False
                    estado['accion'] = f"ajustado_a_{valor}"
                elif accion == "subir":
                    estado['nivel'] = min(100, estado.get('nivel', 50) + 10)
                    estado['accion'] = "subido"
                elif accion == "bajar":
                    estado['nivel'] = max(0, estado.get('nivel', 50) - 10)
                    estado['accion'] = "bajado"
                elif accion == "silenciar":
                    estado['silenciado'] = True
                    estado['accion'] = "silenciado"
                elif accion == "activar":
                    estado['silenciado'] = False
                    estado['accion'] = "activado"
            
            elif dispositivo == "brillo":
                if accion == "ajustar" and valor is not None:
                    estado['nivel'] = valor
                    estado['accion'] = f"ajustado_a_{valor}"
                elif accion == "subir":
                    estado['nivel'] = min(100, estado.get('nivel', 70) + 10)
                    estado['accion'] = "subido"
                elif accion == "bajar":
                    estado['nivel'] = max(10, estado.get('nivel', 70) - 10)
                    estado['accion'] = "bajado"
            
            # Agregar al historial
            self.agregar_al_historial(dispositivo, ubicacion, accion, valor)
            
            # Guardar estado
            self.guardar_estado()
            
            logger.info(f"Estado actualizado: {dispositivo} - {accion}")
            
        except Exception as e:
            logger.error(f"Error actualizando dispositivo: {e}")
    
    def agregar_al_historial(self, dispositivo: str, ubicacion: Optional[str], 
                            accion: str, valor: Optional[Any]):
        """Agregar comando al historial"""
        comando = {
            'timestamp': datetime.now().isoformat(),
            'dispositivo': dispositivo,
            'ubicacion': ubicacion,
            'accion': accion,
            'valor': valor
        }
        
        self.historial_comandos.append(comando)
        
        # Mantener solo los últimos 100 comandos
        if len(self.historial_comandos) > 100:
            self.historial_comandos = self.historial_comandos[-100:]
    
    def obtener_estado(self, dispositivo: str, ubicacion: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estado actual de un dispositivo"""
        try:
            if dispositivo in self.estado_dispositivos:
                estado = self.estado_dispositivos[dispositivo].copy()
                estado['dispositivo'] = dispositivo
                estado['ubicacion'] = ubicacion
                
                # Información específica por ubicación si aplica
                if ubicacion and 'ubicaciones' in estado:
                    estado['estado_ubicacion'] = estado['ubicaciones'].get(ubicacion, False)
                
                return estado
            else:
                return {
                    'dispositivo': dispositivo,
                    'ubicacion': ubicacion,
                    'accion': 'no_configurado',
                    'estado': 'no_configurado',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            return {
                'dispositivo': dispositivo,
                'ubicacion': ubicacion,
                'accion': 'error',
                'error': str(e)
            }

# Instancia global del gestor de estado
_state_manager_instance = None

def obtener_estado(dispositivo: str, ubicacion: Optional[str] = None) -> Dict[str, Any]:
    """Función principal para obtener estado de dispositivo"""
    global _state_manager_instance
    if _state_manager_instance is None:
        _state_manager_instance = GestorEstadoIoT()
    
    return _state_manager_instance.obtener_estado(dispositivo, ubicacion)

def actualizar_estado(dispositivo: str, ubicacion: Optional[str], 
                     accion: str, valor: Optional[Any] = None):
    """Función principal para actualizar estado de dispositivo"""
    global _state_manager_instance
    if _state_manager_instance is None:
        _state_manager_instance = GestorEstadoIoT()
    
    _state_manager_instance.actualizar_dispositivo(dispositivo, ubicacion, accion, valor)