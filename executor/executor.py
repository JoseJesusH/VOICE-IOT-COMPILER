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
            accion_lower = accion.lower()  # Normalizar case
            
            if self.platform == "Darwin":  # macOS
                return self._controlar_volumen_macos(accion_lower, valor)
                
            elif self.platform == "Linux" and self.pulseaudio_available:
                if accion_lower == "ajustar" and valor is not None:
                    cmd = f"pactl set-sink-volume @DEFAULT_SINK@ {valor}%"
                    subprocess.run(cmd, shell=True, check=True)
                    self.estado_dispositivos["volumen"]["nivel"] = valor
                    self.estado_dispositivos["volumen"]["silenciado"] = False
                    
                elif accion_lower == "subir":
                    subprocess.run("pactl set-sink-volume @DEFAULT_SINK@ +10%", 
                                 shell=True, check=True)
                    self.estado_dispositivos["volumen"]["nivel"] = min(100, 
                        self.estado_dispositivos["volumen"]["nivel"] + 10)
                    
                elif accion_lower == "bajar":
                    subprocess.run("pactl set-sink-volume @DEFAULT_SINK@ -10%", 
                                 shell=True, check=True)
                    self.estado_dispositivos["volumen"]["nivel"] = max(0, 
                        self.estado_dispositivos["volumen"]["nivel"] - 10)
                    
                elif accion_lower == "silenciar":
                    subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ 1", 
                                 shell=True, check=True)
                    self.estado_dispositivos["volumen"]["silenciado"] = True
                    
                elif accion_lower == "activar":
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
    
    def _controlar_volumen_macos(self, accion: str, valor: Optional[int] = None) -> bool:
        """Control de volumen específico para macOS"""
        try:
            print(f"🔍 DEBUG: Ejecutando control de volumen macOS - acción: {accion}, valor: {valor}")
            
            # Sincronizar con volumen REAL del sistema
            try:
                result_real = subprocess.run(['osascript', '-e', 'output volume of (get volume settings)'], 
                                           capture_output=True, text=True)
                if result_real.returncode == 0:
                    volumen_real = int(result_real.stdout.strip())
                    print(f"🔍 DEBUG: Volumen REAL del sistema: {volumen_real}%")
                    self.estado_dispositivos["volumen"]["nivel"] = volumen_real
            except Exception as e:
                print(f"⚠️ Error sincronizando volumen: {e}")
            
            if accion == "ajustar" and valor is not None:
                cmd = f'osascript -e "set volume output volume {valor}"'
                print(f"🔍 DEBUG: Ejecutando comando: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Volumen ajustado a {valor}%")
                    self.estado_dispositivos["volumen"]["nivel"] = valor
                    self.estado_dispositivos["volumen"]["silenciado"] = False
                else:
                    print(f"❌ Error ajustando volumen: {result.stderr}")
                    return False
                
            elif accion == "subir":
                nivel_actual = self.estado_dispositivos["volumen"]["nivel"]
                nuevo_nivel = min(100, nivel_actual + 10)
                print(f"🔍 DEBUG: Subiendo volumen de {nivel_actual}% a {nuevo_nivel}%")
                return self._controlar_volumen_macos("ajustar", nuevo_nivel)
                
            elif accion == "bajar":
                nivel_actual = self.estado_dispositivos["volumen"]["nivel"]
                nuevo_nivel = max(0, nivel_actual - 10)
                print(f"🔍 DEBUG: Bajando volumen de {nivel_actual}% a {nuevo_nivel}%")
                return self._controlar_volumen_macos("ajustar", nuevo_nivel)
                
            elif accion == "silenciar":
                cmd = 'osascript -e "set volume with output muted"'
                print(f"🔍 DEBUG: Ejecutando comando: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Volumen silenciado")
                    self.estado_dispositivos["volumen"]["silenciado"] = True
                else:
                    print(f"❌ Error silenciando volumen: {result.stderr}")
                    return False
                
            elif accion == "activar":
                cmd = 'osascript -e "set volume without output muted"'
                print(f"🔍 DEBUG: Ejecutando comando: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Volumen activado")
                    self.estado_dispositivos["volumen"]["silenciado"] = False
                else:
                    print(f"❌ Error activando volumen: {result.stderr}")
                    return False
            
            self.stats['comandos_reales'] += 1
            logger.info(f"Control de volumen macOS ejecutado: {accion} {valor}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error ejecutando comando de volumen en macOS: {e}")
            print(f"❌ Error en comando de volumen: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado en control de volumen: {e}")
            print(f"❌ Error inesperado: {e}")
            return False
    
    def controlar_brillo_sistema(self, accion: str, valor: Optional[int] = None) -> bool:
        """Controlar brillo de la pantalla"""
        try:
            accion_lower = accion.lower()  # Normalizar case
            
            if self.platform == "Darwin":  # macOS
                return self._controlar_brillo_macos(accion_lower, valor)
                
            elif self.platform == "Linux" and self.xrandr_available:
                if accion_lower == "ajustar" and valor is not None:
                    # Convertir porcentaje a factor de brillo (0.1 a 1.0)
                    factor = max(0.1, min(1.0, valor / 100.0))
                    cmd = f"xrandr --output $(xrandr | grep ' connected' | head -1 | cut -d' ' -f1) --brightness {factor}"
                    subprocess.run(cmd, shell=True, check=True)
                    self.estado_dispositivos["brillo"]["nivel"] = valor
                    
                elif accion_lower == "subir":
                    nuevo_nivel = min(100, self.estado_dispositivos["brillo"]["nivel"] + 10)
                    factor = max(0.1, min(1.0, nuevo_nivel / 100.0))
                    cmd = f"xrandr --output $(xrandr | grep ' connected' | head -1 | cut -d' ' -f1) --brightness {factor}"
                    subprocess.run(cmd, shell=True, check=True)
                    self.estado_dispositivos["brillo"]["nivel"] = nuevo_nivel
                    
                elif accion_lower == "bajar":
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
    
    def _controlar_brillo_macos(self, accion: str, valor: Optional[int] = None) -> bool:
        """Control de brillo específico para macOS"""
        try:
            print(f"🔍 DEBUG: Ejecutando control de brillo macOS - acción: {accion}, valor: {valor}")
            
            if accion == "ajustar" and valor is not None:
                # Convertir porcentaje a decimal (0.1 a 1.0)
                factor = max(0.1, min(1.0, valor / 100.0))
                print(f"🔍 DEBUG: Convirtiendo {valor}% a {factor}")
                
                # Método 1: brightness CLI
                print("🔍 DEBUG: Intentando brightness CLI...")
                try:
                    cmd = f"brightness {factor}"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    print(f"🔍 DEBUG: brightness resultado - código: {result.returncode}")
                    print(f"🔍 DEBUG: brightness stdout: '{result.stdout.strip()}'")
                    print(f"🔍 DEBUG: brightness stderr: '{result.stderr.strip()}'")
                    
                    if result.returncode == 0 and "failed" not in result.stderr.lower():
                        print("✅ Brillo ajustado con brightness CLI")
                        self.estado_dispositivos["brillo"]["nivel"] = valor
                        return True
                    else:
                        print("❌ brightness CLI falló o no tiene permisos")
                except Exception as e:
                    print(f"❌ Error ejecutando brightness: {e}")
                
                # Método 2: AppleScript usando System Events con keys
                print("🔍 DEBUG: Intentando AppleScript con teclas de función...")
                try:
                    # Obtener brillo actual aproximado
                    current_level = self.estado_dispositivos["brillo"]["nivel"]
                    target_level = valor
                    
                    if target_level > current_level:
                        # Subir brillo - INTERCAMBIADO: usar F1 (144) para subir
                        steps = min(10, (target_level - current_level) // 10)
                        for _ in range(steps):
                            cmd = 'osascript -e "tell application \\"System Events\\" to key code 144"'  # F1 
                            subprocess.run(cmd, shell=True, capture_output=True)
                        print(f"✅ Brillo aumentado usando teclas F1 ({steps} pasos)")
                    elif target_level < current_level:
                        # Bajar brillo - INTERCAMBIADO: usar F2 (145) para bajar
                        steps = min(10, (current_level - target_level) // 10)
                        for _ in range(steps):
                            cmd = 'osascript -e "tell application \\"System Events\\" to key code 145"'  # F2
                            subprocess.run(cmd, shell=True, capture_output=True)
                        print(f"✅ Brillo reducido usando teclas F2 ({steps} pasos)")
                    
                    self.estado_dispositivos["brillo"]["nivel"] = valor
                    return True
                    
                except Exception as e:
                    print(f"❌ Error con AppleScript: {e}")
                
                # Método 3: Instrucciones al usuario
                print("⚠️ Control automático de brillo no disponible")
                print("💡 SUGERENCIA: Para habilitar control de brillo:")
                print("   1. Ir a Configuración del Sistema > Privacidad y Seguridad > Accesibilidad")
                print("   2. Agregar Terminal o tu aplicación de Python")
                print("   3. Reiniciar la aplicación")
                print(f"🎭 Simulando cambio de brillo a {valor}%")
                
                self.estado_dispositivos["brillo"]["nivel"] = valor
                return True
                self.estado_dispositivos["brillo"]["nivel"] = valor
                return True
                
            elif accion == "subir":
                nivel_actual = self.estado_dispositivos["brillo"]["nivel"]
                nuevo_nivel = min(100, nivel_actual + 10)
                print(f"🔍 DEBUG: Subiendo brillo de {nivel_actual}% a {nuevo_nivel}%")
                return self._controlar_brillo_macos("ajustar", nuevo_nivel)
                
            elif accion == "bajar":
                nivel_actual = self.estado_dispositivos["brillo"]["nivel"]
                nuevo_nivel = max(10, nivel_actual - 10)
                print(f"🔍 DEBUG: Bajando brillo de {nivel_actual}% a {nuevo_nivel}%")
                return self._controlar_brillo_macos("ajustar", nuevo_nivel)
            
            # Si no es ajustar/subir/bajar, simular
            print(f"⚠️ Acción de brillo no reconocida: {accion}")
            return False
            
        except Exception as e:
            logger.error(f"Error en control de brillo macOS: {e}")
            print(f"❌ Error inesperado en brillo: {e}")
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
    
    def controlar_televisor_macos(self, accion: str, ubicacion: Optional[str] = None) -> bool:
        """Control del televisor a través de aplicaciones macOS"""
        try:
            accion_lower = accion.lower()
            print(f"🔍 DEBUG: Ejecutando control de televisor macOS - acción: {accion_lower}, ubicación: {ubicacion}")
            
            if accion_lower == "encender":
                # Encender televisor = abrir aplicación de video (QuickTime Player)
                print("🔍 DEBUG: Abriendo QuickTime Player como simulación de televisor")
                cmd = 'open -a "QuickTime Player"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ QuickTime Player abierto correctamente")
                    self.estado_dispositivos["televisor"]["encendido"] = True
                    if ubicacion:
                        self.estado_dispositivos["televisor"]["ubicaciones"].add(ubicacion)
                    self.stats['comandos_reales'] += 1
                    return True
                else:
                    print(f"❌ Error abriendo QuickTime Player: {result.stderr}")
                    return False
                    
            elif accion_lower == "apagar":
                # Apagar televisor = cerrar aplicaciones de video
                print("🔍 DEBUG: Cerrando aplicaciones de video")
                apps_to_close = ["QuickTime Player", "VLC", "Netflix", "YouTube"]
                
                success = False
                for app in apps_to_close:
                    try:
                        cmd = f'osascript -e "tell application \\"{app}\\" to quit"'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"✅ {app} cerrado correctamente")
                            success = True
                    except Exception as e:
                        print(f"⚠️ No se pudo cerrar {app}: {e}")
                
                self.estado_dispositivos["televisor"]["encendido"] = False
                if ubicacion:
                    self.estado_dispositivos["televisor"]["ubicaciones"].discard(ubicacion)
                
                if success:
                    self.stats['comandos_reales'] += 1
                    return True
                else:
                    print("⚠️ No se encontraron aplicaciones de video para cerrar")
                    # Aún consideramos esto como éxito
                    self.stats['comandos_reales'] += 1
                    return True
            
            else:
                print(f"⚠️ Acción de televisor no reconocida: {accion_lower}")
                return False
                
        except Exception as e:
            logger.error(f"Error en control de televisor macOS: {e}")
            print(f"❌ Error inesperado en televisor: {e}")
            return False
    
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
            
            elif dispositivo.lower() == "volumen":
                exito = self.controlar_volumen_sistema(accion, valor)
                if exito:
                    if accion.lower() == "ajustar":
                        mensaje = f"Volumen ajustado a {valor}"
                    elif accion.lower() == "silenciar":
                        mensaje = "Volumen silenciado"
                    elif accion.lower() == "activar":
                        mensaje = "Volumen activado"
                    else:
                        mensaje = f"Volumen {accion}"
                    
                    print(f"🔊 {mensaje}")
                    if accion != "silenciar":  # No hablar si estamos silenciando
                        self.speak(mensaje)
                else:
                    self.stats['errores_ejecucion'] += 1
            
            elif dispositivo.lower() == "brillo":
                exito = self.controlar_brillo_sistema(accion, valor)
                if exito:
                    if accion.lower() == "ajustar":
                        mensaje = f"Brillo ajustado a {valor}"
                    else:
                        mensaje = f"Brillo {accion}"
                    
                    print(f"💡 {mensaje}")
                    self.speak(mensaje)
                else:
                    self.stats['errores_ejecucion'] += 1
                    
            elif dispositivo.lower() == "luz":
                # Mapeo inteligente: luz -> control real de brillo
                print(f"🔍 DEBUG: Comando luz detectado - {accion} luz en {ubicacion}")
                exito = self.ejecutar_accion_inteligente_luz(accion, ubicacion)
                if exito:
                    if accion.lower() == "encender":
                        mensaje = f"Encendiendo luz{' en ' + ubicacion if ubicacion else ''} - aumentando brillo"
                    elif accion.lower() == "apagar":
                        mensaje = f"Apagando luz{' en ' + ubicacion if ubicacion else ''} - disminuyendo brillo"
                    elif accion.lower() == "subir":
                        mensaje = "Subiendo intensidad de luz - aumentando brillo"
                    elif accion.lower() == "bajar":
                        mensaje = "Bajando intensidad de luz - disminuyendo brillo"
                    else:
                        mensaje = f"Control de luz {accion} completado"
                    
                    print(f"💡 {mensaje}")
                    self.speak(mensaje)
                    
                    # Actualizar estado simulado de luz también
                    if accion.lower() in ["encender", "apagar"]:
                        self.estado_dispositivos["luz"]["encendido"] = (accion.lower() == "encender")
                        if ubicacion:
                            if accion.lower() == "encender":
                                self.estado_dispositivos["luz"]["ubicaciones"].add(ubicacion)
                            else:
                                self.estado_dispositivos["luz"]["ubicaciones"].discard(ubicacion)
                else:
                    self.stats['errores_ejecucion'] += 1
                    
            elif dispositivo.lower() == "televisor":
                # Control real del televisor vía aplicaciones macOS
                print(f"🔍 DEBUG: Comando televisor detectado - {accion} televisor en {ubicacion}")
                exito = self.controlar_televisor_macos(accion, ubicacion)
                if exito:
                    if accion.lower() == "encender":
                        mensaje = f"Encendiendo televisor{' en ' + ubicacion if ubicacion else ''} - abriendo QuickTime Player"
                    elif accion.lower() == "apagar":
                        mensaje = f"Apagando televisor{' en ' + ubicacion if ubicacion else ''} - cerrando aplicaciones de video"
                    else:
                        mensaje = f"Control de televisor {accion} completado"
                    
                    print(f"📺 {mensaje}")
                    self.speak(mensaje)
                    
                    # Actualizar estado del televisor
                    if accion.lower() in ["encender", "apagar"]:
                        self.estado_dispositivos["televisor"]["encendido"] = (accion.lower() == "encender")
                        if ubicacion:
                            if accion.lower() == "encender":
                                self.estado_dispositivos["televisor"]["ubicaciones"].add(ubicacion)
                            else:
                                self.estado_dispositivos["televisor"]["ubicaciones"].discard(ubicacion)
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
    
    def ejecutar_accion_inteligente_luz(self, accion: str, ubicacion: Optional[str]) -> bool:
        """Ejecutar control inteligente de luz mapeado a brillo real"""
        accion_lower = accion.lower()
        
        print(f"🔍 DEBUG: Mapeando luz -> brillo para acción '{accion_lower}'")
        
        if accion_lower == "encender":
            # Encender luz = subir brillo a 80%
            print("🔍 DEBUG: Ejecutando encender luz -> ajustar brillo a 80%")
            return self.controlar_brillo_sistema("ajustar", 80)
        elif accion_lower == "apagar":
            # Apagar luz = bajar brillo a 20%
            print("🔍 DEBUG: Ejecutando apagar luz -> ajustar brillo a 20%")
            return self.controlar_brillo_sistema("ajustar", 20)
        elif accion_lower == "subir":
            # Subir intensidad de luz = subir brillo
            print("🔍 DEBUG: Ejecutando subir luz -> subir brillo")
            return self.controlar_brillo_sistema("subir", None)
        elif accion_lower == "bajar":
            # Bajar intensidad de luz = bajar brillo
            print("🔍 DEBUG: Ejecutando bajar luz -> bajar brillo")
            return self.controlar_brillo_sistema("bajar", None)
        else:
            print(f"🔍 DEBUG: Acción de luz no reconocida: {accion_lower}")
            return False
    
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