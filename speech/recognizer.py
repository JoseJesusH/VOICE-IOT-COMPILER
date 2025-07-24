# ============================================================================
# speech/recognizer.py - Versión SIN TTS para evitar conflictos
# ============================================================================

import speech_recognition as sr
import threading
from datetime import datetime
import json
import logging
import time
import traceback

# Configurar logging
logger = logging.getLogger(__name__)

class VoiceRecognizer:
    def __init__(self):
        try:
            logger.info("Inicializando VoiceRecognizer...")
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            # REMOVED: TTS engine initialization to avoid conflicts
            self.tts_enabled = False  # Disabled to prevent conflicts
            self.calibrate_microphone()
            self.stats = {
                'total_commands': 0,
                'successful_recognitions': 0,
                'failed_recognitions': 0,
                'average_response_time': 0
            }
            logger.info("VoiceRecognizer inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando VoiceRecognizer: {e}", exc_info=True)
            raise
    
    def setup_tts(self):
        """TTS deshabilitado para evitar conflictos con GUI"""
        try:
            logger.info("TTS deshabilitado en recognizer para evitar conflictos")
            self.tts_enabled = False
            # No inicializar pyttsx3 aquí - dejamos que la GUI lo maneje
        except Exception as e:
            logger.error(f"Error en setup_tts: {e}")
            self.tts_enabled = False
    
    def calibrate_microphone(self):
        """Calibrar micrófono para ruido ambiente"""
        try:
            logger.info("Calibrando micrófono...")
            with self.microphone as source:
                logger.info("Ajustando para ruido ambiente...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Configurar valores óptimos
                self.recognizer.energy_threshold = 4000
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                self.recognizer.phrase_threshold = 0.3
            logger.info("Micrófono calibrado exitosamente")
        except Exception as e:
            logger.error(f"Error calibrando micrófono: {e}", exc_info=True)
    
    def speak(self, text):
        """Retroalimentación de voz DESHABILITADA - solo muestra en consola"""
        try:
            # FIXED: No usar TTS aquí para evitar conflictos
            print(f"🎤 Recognizer: {text}")
            logger.info(f"Recognizer feedback: {text}")
            # Let the GUI handle all TTS - no pyttsx3 here
        except Exception as e:
            logger.error(f"Error en speak (disabled): {e}")
    
    def get_stats(self):
        """Obtener estadísticas de uso"""
        return self.stats.copy()

def reconocer_comando_voz():
    """Función principal para reconocimiento de voz SIN conflictos TTS"""
    try:
        logger.info("=== INICIANDO RECONOCIMIENTO DE VOZ ===")
        recognizer = VoiceRecognizer()
        start_time = time.time()
        
        recognizer.stats['total_commands'] += 1
        
        logger.info("Capturando audio del micrófono...")
        with recognizer.microphone as source:
            print("🎤 Escuchando...")
            logger.info("Iniciando captura de audio")
            try:
                audio = recognizer.recognizer.listen(
                    source, 
                    timeout=5, 
                    phrase_time_limit=10
                )
                logger.info("Audio capturado exitosamente")
            except sr.WaitTimeoutError:
                logger.warning("Timeout esperando audio")
                print("⏰ Timeout esperando comando")
                return None
        
        print("🔄 Procesando audio...")
        logger.info("Audio capturado, iniciando reconocimiento")
        
        try:
            # Intentar Google Speech Recognition primero
            logger.info("Intentando reconocimiento con Google Speech API...")
            command = recognizer.recognizer.recognize_google(
                audio, 
                language="es-ES"
            )
            
            # Calcular tiempo de respuesta
            response_time = time.time() - start_time
            recognizer.stats['successful_recognitions'] += 1
            recognizer.stats['average_response_time'] = (
                recognizer.stats['average_response_time'] + response_time
            ) / 2
            
            print(f"📝 Reconocido: {command}")
            logger.info(f"Comando reconocido exitosamente: {command}")
            
            # FIXED: No usar TTS aquí - solo feedback en consola
            print("✅ Comando recibido y procesado")
            
            return command.lower().strip()
        
        except sr.RequestError as e:
            logger.warning(f"Error de API de Google: {e}")
            # Fallback a reconocimiento offline si está disponible
            try:
                logger.info("Intentando reconocimiento offline...")
                command = recognizer.recognizer.recognize_sphinx(
                    audio, 
                    language="es-ES"
                )
                print(f"📝 Reconocido (offline): {command}")
                logger.info(f"Comando reconocido offline: {command}")
                
                # FIXED: No usar TTS - solo mensaje en consola
                print("✅ Comando recibido usando reconocimiento local")
                return command.lower().strip()
                
            except Exception as offline_error:
                logger.error(f"Error en reconocimiento offline: {offline_error}")
                print("❌ Error de conexión y reconocimiento local no disponible")
                recognizer.stats['failed_recognitions'] += 1
                return None
        
        except sr.UnknownValueError:
            print("❌ No se pudo entender el audio")
            logger.warning("Audio no reconocido")
            print("💡 Intenta hablar más claro y cerca del micrófono")
            recognizer.stats['failed_recognitions'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error inesperado en reconocimiento: {e}", exc_info=True)
            print(f"❌ Error inesperado en reconocimiento: {str(e)}")
            print("⚠️ Ocurrió un error inesperado")
            return None
    
    except Exception as e:
        logger.error(f"Error crítico en reconocer_comando_voz: {e}", exc_info=True)
        print(f"❌ Error crítico: {str(e)}")
        print("Stacktrace:")
        traceback.print_exc()
        return None

# Alternative simple function if the class approach has issues
def simple_voice_recognition():
    """Versión ultra-simple de reconocimiento sin TTS"""
    try:
        print("🎤 Iniciando reconocimiento simple...")
        
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("🎤 Escuchando comando...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        print("🔄 Procesando...")
        command = recognizer.recognize_google(audio, language="es-ES")
        
        print(f"✅ Comando: {command}")
        return command.lower().strip()
        
    except sr.WaitTimeoutError:
        print("⏰ Timeout - no se detectó audio")
        return None
    except sr.UnknownValueError:
        print("❌ No se entendió el comando")
        return None
    except sr.RequestError as e:
        print(f"❌ Error de servicio: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# For backward compatibility with your existing code
def reconocer_comando_voz_backup():
    """Función de respaldo si hay problemas con la principal"""
    try:
        return simple_voice_recognition()
    except Exception as e:
        print(f"❌ Error en función de respaldo: {e}")
        return None