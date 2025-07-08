# ============================================================================
# executor/executor.py - Versión corregida y completa
# ============================================================================

import logging
import subprocess
import platform
import psutil
import pyttsx3
import threading
from typing import Optional, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EjecutorAccionesIoT:
    def __init__(self):
        self.platform = platform.system()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Estado simulado de dispositivos
        self.estado_dispositivos = {
            "luz": {"encendido": False, "ubicaciones": set()},
            "ventilador": {"encendido": False, "ubicaciones": set()},
            "televisor": {"encendido": False, "ubicaciones": set()},
            "calefactor": {"encendido": False, "ubicaciones": set()},
            "volumen": {"nivel": 50, "silenciado": False},
            "brillo": {"nivel": 70}
        }
        
        self.stats = {
            'acciones_ejecutadas': 0,
            'errores_ejecucion': 0,
            'comandos_simulados': 0,
            'comandos_reales': 0
        }
        
        # Inicializar controladores específicos del sistema
        self._init_system_controllers()
    
    def _init_system_controllers(self):
        """Inicializar controladores específicos del sistema operativo"""
        try:
            if self.platform == "Linux":
                # Verificar si PulseAudio está disponible
                result = subprocess.run(['which', 'pactl'], capture_output=True)
                self.pulseaudio_available = result.returncode == 0
                
                # Verificar si xrandr está disponible para control de brillo
                result = subprocess.run(['which', 'xrandr'], capture_output=True)
                self.xrandr_available = result.returncode == 0
            else:
                self.pulseaudio_available = False
                self.xrandr_available = False
                
            logger.info(f"Sistema: {self.platform}, PulseAudio: {self.pulseaudio_available}, "
                       f"xrandr: {self.xrandr_available}")
        except Exception as e:
            logger.error(f"Error inicializando controladores del sistema: {e}")
    
    def setup_tts(self):
        """Configurar síntesis de voz"""
        try:
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
        except Exception as e:
            logger.error(f"Error configurando TTS: {e}")
    
    def speak(self, text: str):
        """Síntesis de voz thread-safe sin conflictos"""
        def _speak():
            try:
                # No usar TTS en executor si hay conflictos
                print(f"🔊 TTS: {text}")
                logger.info(f"TTS simulado: {text}")
            except Exception as e:
                logger.error(f"Error en síntesis de voz: {e}")
        
        threading.Thread(target=_speak, daemon=True).start()
    
    def controlar_volumen_sistema(self, accion: str, valor: Optional[int] = None) -> bool:
        """Controlar volumen del sistema operativo"""
        try:
            if self.platform == "Linux" and self.pulseaudio_available:
                if accion == "ajustar" and valor is not None:
                    cmd = f"pactl set-sink-volume @DEFAULT_SINK@ {valor}%"
                    subprocess.run(cmd, shell=True, check=True)
                    self.estado_dispositivos["volumen"]["nivel"] = valor
                    self.estado_dispositivos["volumen"]["silenciado"] = False
                    
                elif accion == "subir":
                    subprocess.run("pactl set-sink-volume @DEFAULT_SINK@ +10%", 
                                 shell=True, check=True)
                    self.estado_dispositivos["volumen"]["nivel"] = min(100, 
                        self.estado_dispositivos["volumen"]["nivel"] + 10)
                    
                elif accion == "bajar":
                    subprocess.run("pactl set-sink-volume @DEFAULT_SINK@ -10%", 
                                 shell=True, check=True)
                    self.estado_dispositivos["volumen"]["nivel"] = max(0, 
                        self.estado_dispositivos["volumen"]["nivel"] - 10)
                    
                elif accion == "silenciar":
                    subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ 1", 
                                 shell=True, check=True)
                    self.estado_dispositivos["volumen"]["silenciado"] = True
                    
                elif accion == "activar":
                    subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ 0", 
                                 shell=True, check=True)
                    self.estado_dispositivos["volumen"]["silenciado"] = False
                
                self.stats['comandos_reales'] += 1
                return True
            else:
                # Simulación para otros sistemas
                logger.info(f"Simulando control de volumen: {accion} {valor}")
                if accion == "ajustar" and valor is not None:
                    self.estado_dispositivos["volumen"]["nivel"] = valor
                elif accion == "silenciar":
                    self.estado_dispositivos["volumen"]["silenciado"] = True
                elif accion == "activar":
                    self.estado_dispositivos["volumen"]["silenciado"] = False
                
                self.stats['comandos_simulados'] += 1
                return True
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error ejecutando comando de volumen: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado controlando volumen: {e}")
            return False
    
    def controlar_brillo_sistema(self, accion: str, valor: Optional[int] = None) -> bool:
        """Controlar brillo de la pantalla"""
        try:
            if self.platform == "Linux" and self.xrandr_available:
                if accion == "ajustar" and valor is not None:
                    # Convertir porcentaje a factor de brillo (0.1 a 1.0)
                    factor = max(0.1, min(1.0, valor / 100.0))
                    cmd = f"xrandr --output $(xrandr | grep ' connected' | head -1 | cut -d' ' -f1) --brightness {factor}"
                    subprocess.run(cmd, shell=True, check=True)
                    self.estado_dispositivos["brillo"]["nivel"] = valor
                    
                elif accion == "subir":
                    nuevo_nivel = min(100, self.estado_dispositivos["brillo"]["nivel"] + 10)
                    factor = max(0.1, min(1.0, nuevo_nivel / 100.0))
                    cmd = f"xrandr --output $(xrandr | grep ' connected' | head -1 | cut -d' ' -f1) --brightness {factor}"
                    subprocess.run(cmd, shell=True, check=True)
                    self.estado_dispositivos["brillo"]["nivel"] = nuevo_nivel
                    
                elif accion == "bajar":
                    nuevo_nivel = max(10, self.estado_dispositivos["brillo"]["nivel"] - 10)
                    factor = max(0.1, min(1.0, nuevo_nivel / 100.0))
                    cmd = f"xrandr --output $(xrandr | grep ' connected' | head -1 | cut -d' ' -f1) --brightness {factor}"
                    subprocess.run(cmd, shell=True, check=True)
                    self.estado_dispositivos["brillo"]["nivel"] = nuevo_nivel
                
                self.stats['comandos_reales'] += 1
                return True
            else:
                # Simulación para otros sistemas
                logger.info(f"Simulando control de brillo: {accion} {valor}")
                if accion == "ajustar" and valor is not None:
                    self.estado_dispositivos["brillo"]["nivel"] = valor
                elif accion == "subir":
                    self.estado_dispositivos["brillo"]["nivel"] = min(100, 
                        self.estado_dispositivos["brillo"]["nivel"] + 10)
                elif accion == "bajar":
                    self.estado_dispositivos["brillo"]["nivel"] = max(10, 
                        self.estado_dispositivos["brillo"]["nivel"] - 10)
                
                self.stats['comandos_simulados'] += 1
                return True
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error ejecutando comando de brillo: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado controlando brillo: {e}")
            return False
    
    def obtener_info_bateria(self) -> Optional[int]:
        """Obtener información de la batería"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return int(battery.percent)
            else:
                logger.warning("No se detectó batería en el sistema")
                return None
        except Exception as e:
            logger.error(f"Error obteniendo información de batería: {e}")
            return None
    
    def obtener_hora_actual(self) -> str:
        """Obtener hora actual del sistema"""
        try:
            now = datetime.now()
            return now.strftime("%H:%M")
        except Exception as e:
            logger.error(f"Error obteniendo hora: {e}")
            return "Error"
    
    def execute(self, accion: str, dispositivo: str, 
                ubicacion: Optional[str] = None, valor: Optional[int] = None):
        """Ejecutar acción en dispositivo IoT"""
        self.stats['acciones_ejecutadas'] += 1
        
        try:
            logger.info(f"Ejecutando: {accion} {dispositivo} en {ubicacion or 'global'} valor={valor}")
            
            if accion == "ver":
                if dispositivo == "hora":
                    hora = self.obtener_hora_actual()
                    mensaje = f"La hora actual es {hora}"
                    print(f"🕒 {mensaje}")
                    self.speak(mensaje)
                    
                elif dispositivo == "bateria":
                    porcentaje = self.obtener_info_bateria()
                    if porcentaje is not None:
                        mensaje = f"La batería está al {porcentaje} por ciento"
                        print(f"🔋 {mensaje}")
                        self.speak(mensaje)
                    else:
                        mensaje = "No pude obtener el nivel de batería"
                        print(f"❌ {mensaje}")
                        self.speak(mensaje)
            
            elif dispositivo == "volumen":
                exito = self.controlar_volumen_sistema(accion, valor)
                if exito:
                    if accion == "ajustar":
                        mensaje = f"Volumen ajustado a {valor}"
                    elif accion == "silenciar":
                        mensaje = "Volumen silenciado"
                    elif accion == "activar":
                        mensaje = "Volumen activado"
                    else:
                        mensaje = f"Volumen {accion}"
                    
                    print(f"🔊 {mensaje}")
                    if accion != "silenciar":  # No hablar si estamos silenciando
                        self.speak(mensaje)
                else:
                    self.stats['errores_ejecucion'] += 1
            
            elif dispositivo == "brillo":
                exito = self.controlar_brillo_sistema(accion, valor)
                if exito:
                    if accion == "ajustar":
                        mensaje = f"Brillo ajustado a {valor}"
                    else:
                        mensaje = f"Brillo {accion}"
                    
                    print(f"💡 {mensaje}")
                    self.speak(mensaje)
                else:
                    self.stats['errores_ejecucion'] += 1
            
            else:
                # Simulación para otros dispositivos
                self.simular_accion_dispositivo(accion, dispositivo, ubicacion)
            
            # Actualizar historial de comandos
            self.actualizar_historial(accion, dispositivo, ubicacion, valor)
            
        except Exception as e:
            self.stats['errores_ejecucion'] += 1
            logger.error(f"Error ejecutando acción: {e}")
            self.speak("Error ejecutando la acción")
    
    def simular_accion_dispositivo(self, accion: str, dispositivo: str, ubicacion: Optional[str]):
        """Simular acción en dispositivos que no tienen control real"""
        ubicacion_str = f" en {ubicacion}" if ubicacion else ""
        mensaje = f"{accion.capitalize()} {dispositivo}{ubicacion_str}"
        
        # Actualizar estado simulado
        if dispositivo in self.estado_dispositivos:
            if accion in ["encender", "apagar"]:
                self.estado_dispositivos[dispositivo]["encendido"] = (accion == "encender")
                if ubicacion:
                    if accion == "encender":
                        self.estado_dispositivos[dispositivo]["ubicaciones"].add(ubicacion)
                    else:
                        self.estado_dispositivos[dispositivo]["ubicaciones"].discard(ubicacion)
        
        print(f"🎭 Simulando: {mensaje}")
        self.speak(f"Simulando {mensaje}")
        self.stats['comandos_simulados'] += 1
    
    def actualizar_historial(self, accion: str, dispositivo: str, 
                           ubicacion: Optional[str], valor: Optional[int]):
        """Actualizar historial de comandos ejecutados"""
        try:
            comando_historial = {
                'timestamp': datetime.now().isoformat(),
                'accion': accion,
                'dispositivo': dispositivo,
                'ubicacion': ubicacion,
                'valor': valor,
                'exito': True
            }
            
            # En una implementación real, esto se guardaría en base de datos
            logger.info(f"Historial actualizado: {comando_historial}")
            
        except Exception as e:
            logger.error(f"Error actualizando historial: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """Obtener estadísticas del ejecutor"""
        return self.stats.copy()
    
    def get_device_status(self, dispositivo: str, ubicacion: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estado actual de un dispositivo"""
        if dispositivo in self.estado_dispositivos:
            estado = self.estado_dispositivos[dispositivo].copy()
            estado['dispositivo'] = dispositivo
            estado['ubicacion'] = ubicacion
            return estado
        return {'dispositivo': dispositivo, 'estado': 'desconocido'}

# Instancia global del ejecutor
_executor_instance = None

def execute(accion: str, dispositivo: str, ubicacion: Optional[str] = None, valor: Optional[int] = None):
    """Función principal de ejecución de acciones"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = EjecutorAccionesIoT()
    
    _executor_instance.execute(accion, dispositivo, ubicacion, valor)