# ============================================================================
# speech/recognizer.py - Versión con debug mejorado
# ============================================================================

import speech_recognition as sr
import pyttsx3
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
            self.tts_engine = None
            self.setup_tts()
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
        """Configurar síntesis de voz en español"""
        try:
            logger.info("Configurando TTS...")
            self.tts_engine = pyttsx3.init()
            
            voices = self.tts_engine.getProperty('voices')
            spanish_voice_found = False
            
            logger.info(f"Voces disponibles: {len(voices)}")
            
            for i, voice in enumerate(voices):
                logger.debug(f"Voz {i}: {voice.name} - {voice.id}")
                if any(indicator in voice.name.lower() for indicator in ['spanish', 'es', 'español', 'diego', 'mónica', 'albert']):
                    self.tts_engine.setProperty('voice', voice.id)
                    spanish_voice_found = True
                    logger.info(f"Voz en español configurada: {voice.name}")
                    break
            
            if not spanish_voice_found:
                logger.warning("No se encontró voz en español, usando voz por defecto")
            
            # Configurar parámetros de voz
            self.tts_engine.setProperty('rate', 150)  # Velocidad
            self.tts_engine.setProperty('volume', 0.9)  # Volumen
            
            logger.info("TTS configurado correctamente")
        except Exception as e:
            logger.error(f"Error configurando TTS: {e}", exc_info=True)
            self.tts_engine = None
    
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
        """Retroalimentación auditiva thread-safe"""
        def _speak():
            try:
                if self.tts_engine:
                    logger.debug(f"Hablando: {text}")
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                else:
                    logger.warning("TTS no disponible")
            except Exception as e:
                logger.error(f"Error en síntesis de voz: {e}", exc_info=True)
        
        threading.Thread(target=_speak, daemon=True).start()
    
    def get_stats(self):
        """Obtener estadísticas de uso"""
        return self.stats.copy()

def reconocer_comando_voz():
    """Función principal para reconocimiento de voz con manejo robusto de errores"""
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
            recognizer.speak("Comando recibido")
            
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
                recognizer.speak("Comando recibido usando reconocimiento local")
                return command.lower().strip()
            except Exception as offline_error:
                logger.error(f"Error en reconocimiento offline: {offline_error}")
                recognizer.speak("Error de conexión y reconocimiento local no disponible")
                recognizer.stats['failed_recognitions'] += 1
                return None
        
        except sr.UnknownValueError:
            print("❌ No se pudo entender el audio")
            logger.warning("Audio no reconocido")
            recognizer.speak("No entendí el comando, intenta de nuevo")
            recognizer.stats['failed_recognitions'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error inesperado en reconocimiento: {e}", exc_info=True)
            print(f"❌ Error inesperado en reconocimiento: {str(e)}")
            recognizer.speak("Ocurrió un error inesperado")
            return None
    
    except Exception as e:
        logger.error(f"Error crítico en reconocer_comando_voz: {e}", exc_info=True)
        print(f"❌ Error crítico: {str(e)}")
        print("Stacktrace:")
        traceback.print_exc()
        return None