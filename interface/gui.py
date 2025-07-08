# ============================================================================
# interface/gui.py - Versión corregida para evitar cierre inesperado
# ============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, font
from PIL import Image, ImageTk
import pyttsx3
import threading
import os
import logging
from datetime import datetime
from typing import Optional, Callable, Dict, Any
import traceback

logger = logging.getLogger(__name__)

class InterfazPictogramasAccesible:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_accessibility()
        self.setup_tts()
        self.load_images()
        self.create_widgets()
        self.callback = None
        self.current_device = None
        self.tts_busy = False
        
        # Estadísticas de uso
        self.stats = {
            'comandos_procesados': 0,
            'tiempo_sesion_inicio': datetime.now(),
            'interacciones_voz': 0,
            'interacciones_teclado': 0
        }
        
    def setup_window(self):
        """Configurar ventana principal con accesibilidad"""
        self.root.title("🏠 Asistente Inclusivo IoT - UNSA")
        self.root.geometry("900x800")
        self.root.configure(bg='#fce4ec')
        self.root.resizable(True, True)
        
        # Configurar para cerrar correctamente
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Evitar que la ventana se cierre por errores
        self.root.report_callback_exception = self.handle_exception
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Manejar excepciones sin cerrar la ventana"""
        error_msg = f"Error en GUI: {exc_type.__name__}: {exc_value}"
        logger.error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
        print(f"❌ {error_msg}")
        
        # Mostrar error al usuario pero NO cerrar la ventana
        try:
            messagebox.showerror("Error", f"Se produjo un error:\n{exc_value}\n\nLa aplicación continuará funcionando.")
        except:
            pass  # Si no se puede mostrar el mensaje, continuar
    
    def setup_accessibility(self):
        """Configurar características de accesibilidad"""
        # Configurar fuentes accesibles
        self.fonts = {
            'title': ('Comic Sans MS', 22, 'bold'),
            'button': ('Arial', 14, 'bold'),
            'label': ('Arial', 12),
            'status': ('Arial', 11),
            'small': ('Arial', 10)
        }
        
        # Colores accesibles con alto contraste (WCAG 2.1 AA)
        self.colors = {
            'primary_bg': '#fce4ec',      # Rosa muy claro
            'secondary_bg': '#e1f5fe',    # Azul muy claro
            'accent_blue': '#42a5f5',     # Azul accesible
            'accent_red': '#e53935',      # Rojo accesible
            'text_primary': '#880e4f',    # Texto principal
            'text_secondary': '#0277bd',  # Texto secundario
            'success': '#4caf50',         # Verde éxito
            'warning': '#ff9800'          # Naranja advertencia
        }
    
    def setup_tts(self):
        """Configurar síntesis de voz para macOS de forma segura"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configurar voz en español para macOS
            voices = self.tts_engine.getProperty('voices')
            spanish_voice_set = False
            
            for voice in voices:
                if any(indicator in voice.name.lower() for indicator in ['spanish', 'es', 'español', 'diego', 'mónica', 'bubbles']):
                    self.tts_engine.setProperty('voice', voice.id)
                    spanish_voice_set = True
                    logger.info(f"Voz en español configurada: {voice.name}")
                    break
            
            if not spanish_voice_set:
                logger.warning("No se encontró voz en español, usando voz por defecto")
            
            # Configurar parámetros para macOS
            self.tts_engine.setProperty('rate', 180)
            self.tts_engine.setProperty('volume', 0.9)
            
        except Exception as e:
            logger.error(f"Error configurando TTS: {e}")
            self.tts_engine = None
    
    def load_images(self):
        """Cargar pictogramas accesibles con manejo robusto de errores"""
        self.images = {}
        self.alt_texts = {}
        image_dir = "img"
        default_size = (320, 260)
        
        # Mapeo de dispositivos con textos descriptivos
        devices_info = {
            "luz": "Bombilla encendida representando control de iluminación",
            "ventilador": "Ventilador girando para control de ventilación", 
            "televisor": "Pantalla de televisor para control de entretenimiento",
            "volumen": "Altavoz con ondas sonoras para control de audio",
            "brillo": "Sol brillante para control de luminosidad",
            "cocina": "Utensilios de cocina representando esta habitación",
            "dormitorio": "Cama representando el dormitorio",
            "sala": "Sofá representando la sala de estar",
            "bano": "Ducha representando el cuarto de baño",
            "baño": "Ducha representando el cuarto de baño",
            "oficina": "Escritorio con computadora representando la oficina",
            "calefactor": "Radiador para control de calefacción",
            "bateria": "Batería con indicador de carga",
            "hora": "Reloj mostrando la hora actual"
        }
        
        for device, description in devices_info.items():
            try:
                # Intentar diferentes variaciones del nombre
                possible_names = [
                    f"{device}.png",
                    f"{device.replace('ñ', 'n')}.png",  # baño -> bano
                    f"{device.replace('í', 'i')}.png"   # batería -> bateria
                ]
                
                image_loaded = False
                for name in possible_names:
                    image_path = os.path.join(image_dir, name)
                    if os.path.exists(image_path):
                        try:
                            # Cargar y redimensionar imagen
                            image = Image.open(image_path)
                            image = image.resize(default_size, Image.Resampling.LANCZOS)
                            
                            # Mejorar contraste para accesibilidad
                            from PIL import ImageEnhance
                            enhancer = ImageEnhance.Contrast(image)
                            image = enhancer.enhance(1.2)
                            
                            self.images[device] = ImageTk.PhotoImage(image)
                            self.alt_texts[device] = description
                            logger.info(f"Imagen cargada: {name} para {device}")
                            image_loaded = True
                            break
                        except Exception as e:
                            logger.warning(f"Error cargando {name}: {e}")
                            continue
                
                if not image_loaded:
                    # Crear imagen placeholder si no se puede cargar
                    placeholder = Image.new('RGB', default_size, color='#e0e0e0')
                    self.images[device] = ImageTk.PhotoImage(placeholder)
                    self.alt_texts[device] = f"Imagen no disponible para {device}"
                    logger.warning(f"Usando placeholder para {device}")
                    
            except Exception as e:
                logger.error(f"Error crítico cargando imagen {device}: {e}")
                # Imagen de emergencia
                try:
                    emergency = Image.new('RGB', default_size, color='lightgray')
                    self.images[device] = ImageTk.PhotoImage(emergency)
                    self.alt_texts[device] = f"Error cargando imagen de {device}"
                except:
                    pass  # Si falla todo, continuar sin imagen
    
    def create_widgets(self):
        """Crear widgets con diseño accesible"""
        try:
            # Frame principal
            main_frame = tk.Frame(self.root, bg=self.colors['primary_bg'])
            main_frame.pack(fill='both', expand=True, padx=15, pady=15)
            
            # Título principal
            self.create_title_section(main_frame)
            
            # Sección de controles principales
            self.create_control_section(main_frame)
            
            # Área de pictogramas
            self.create_pictogram_section(main_frame)
            
            # Panel de estado y estadísticas
            self.create_status_section(main_frame)
            
            # Controles de salida
            self.create_exit_section(main_frame)
            
            # Configurar accesos directos de teclado
            self.setup_keyboard_shortcuts()
            
        except Exception as e:
            logger.error(f"Error creando widgets: {e}")
            # Si falla la creación de widgets, crear interfaz mínima
            self.create_minimal_interface()
    
    def create_minimal_interface(self):
        """Crear interfaz mínima si falla la principal"""
        try:
            label = tk.Label(self.root, text="🏠 Asistente IoT\n\nError cargando interfaz completa", 
                           font=('Arial', 16), bg='#fce4ec')
            label.pack(expand=True)
            
            button = tk.Button(self.root, text="🎤 Hablar", font=('Arial', 14),
                             command=self.start_listening, bg='#42a5f5', fg='white')
            button.pack(pady=20)
        except Exception as e:
            logger.error(f"Error creando interfaz mínima: {e}")
    
    def create_title_section(self, parent):
        """Crear sección de título"""
        title_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="🏠 Asistente Inclusivo IoT",
            font=self.fonts['title'],
            fg=self.colors['text_primary'],
            bg=self.colors['primary_bg']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Universidad Nacional de San Agustín de Arequipa",
            font=self.fonts['small'],
            fg=self.colors['text_secondary'],
            bg=self.colors['primary_bg']
        )
        subtitle_label.pack()
    
    def create_control_section(self, parent):
        """Crear sección de controles principales"""
        control_frame = tk.LabelFrame(
            parent,
            text=" Controles de Voz ",
            font=self.fonts['label'],
            fg=self.colors['text_primary'],
            bg=self.colors['primary_bg'],
            relief='raised',
            borderwidth=2
        )
        control_frame.pack(fill='x', pady=(0, 20))
        
        # Botón principal de voz
        self.voice_button = tk.Button(
            control_frame,
            text="🎤 Presiona para Hablar\n(Espacio o Click)",
            font=self.fonts['button'],
            bg=self.colors['accent_blue'],
            fg="white",
            width=30,
            height=3,
            command=self.start_listening,
            relief="raised",
            borderwidth=4,
            cursor="hand2"
        )
        self.voice_button.pack(pady=15)
        
        # Instrucciones
        instruction_text = (
            "Presiona el botón o usa la barra espaciadora para dar comandos de voz.\n"
            "Ejemplos: 'Enciende la luz', 'Sube el brillo', 'Dime la hora'"
        )
        
        instruction_label = tk.Label(
            control_frame,
            text=instruction_text,
            font=self.fonts['small'],
            fg=self.colors['text_secondary'],
            bg=self.colors['primary_bg'],
            wraplength=600,
            justify='center'
        )
        instruction_label.pack(pady=(0, 10))
    
    def create_pictogram_section(self, parent):
        """Crear sección de pictogramas"""
        pictogram_frame = tk.LabelFrame(
            parent,
            text=" Estado Visual del Dispositivo ",
            font=self.fonts['label'],
            fg=self.colors['text_primary'],
            bg=self.colors['primary_bg'],
            relief='raised',
            borderwidth=2
        )
        pictogram_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Área de imagen principal
        self.image_frame = tk.Frame(pictogram_frame, bg=self.colors['primary_bg'])
        self.image_frame.pack(pady=20, expand=True, fill='both')
        
        # Label para imagen
        self.image_label = tk.Label(
            self.image_frame,
            text="Presiona el botón de micrófono para comenzar\n\nEl pictograma del dispositivo aparecerá aquí",
            font=self.fonts['label'],
            bg=self.colors['primary_bg'],
            fg=self.colors['text_primary'],
            wraplength=400,
            justify='center'
        )
        self.image_label.pack(expand=True)
        
        # Label para descripción de imagen
        self.alt_text_label = tk.Label(
            pictogram_frame,
            text="",
            font=self.fonts['small'],
            bg=self.colors['secondary_bg'],
            fg=self.colors['text_secondary'],
            wraplength=500,
            justify='center',
            relief='sunken',
            borderwidth=1
        )
        self.alt_text_label.pack(fill='x', padx=10, pady=(0, 10))
    
    def create_status_section(self, parent):
        """Crear sección de estado"""
        status_frame = tk.LabelFrame(
            parent,
            text=" Estado del Sistema ",
            font=self.fonts['label'],
            fg=self.colors['text_primary'],
            bg=self.colors['secondary_bg'],
            relief='raised',
            borderwidth=2
        )
        status_frame.pack(fill='x', pady=(0, 20))
        
        # Estado principal
        self.status_label = tk.Label(
            status_frame,
            text="✅ Sistema listo - Presiona el micrófono para comenzar",
            font=self.fonts['status'],
            bg=self.colors['secondary_bg'],
            fg=self.colors['text_secondary']
        )
        self.status_label.pack(pady=8)
        
        # Frame para estadísticas
        stats_frame = tk.Frame(status_frame, bg=self.colors['secondary_bg'])
        stats_frame.pack(fill='x', padx=10, pady=(0, 8))
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Comandos procesados: 0 | Tiempo de sesión: 0:00",
            font=self.fonts['small'],
            bg=self.colors['secondary_bg'],
            fg=self.colors['text_secondary']
        )
        self.stats_label.pack()
    
    def create_exit_section(self, parent):
        """Crear sección de controles de salida"""
        exit_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        exit_frame.pack(fill='x')
        
        # Botón de ayuda
        help_button = tk.Button(
            exit_frame,
            text="❓ Ayuda (F1)",
            font=self.fonts['button'],
            bg=self.colors['warning'],
            fg="white",
            width=15,
            height=1,
            command=self.show_help,
            relief="raised",
            borderwidth=2
        )
        help_button.pack(side='left', padx=(0, 10))
        
        # Botón de salida
        exit_button = tk.Button(
            exit_frame,
            text="❌ Salir (Esc)",
            font=self.fonts['button'],
            bg=self.colors['accent_red'],
            fg="white",
            width=15,
            height=1,
            command=self.on_closing,
            relief="raised",
            borderwidth=2
        )
        exit_button.pack(side='right')
    
    def setup_keyboard_shortcuts(self):
        """Configurar accesos directos de teclado"""
        try:
            self.root.bind('<space>', lambda e: self.start_listening())
            self.root.bind('<Return>', lambda e: self.start_listening())
            self.root.bind('<Escape>', lambda e: self.on_closing())
            self.root.bind('<F1>', lambda e: self.show_help())
            
            # Asegurar que la ventana pueda recibir eventos de teclado
            self.root.focus_set()
            if hasattr(self, 'voice_button'):
                self.voice_button.focus_set()
        except Exception as e:
            logger.error(f"Error configurando atajos de teclado: {e}")
    
    def start_listening(self):
        """Iniciar escucha de voz con manejo robusto de errores"""
        try:
            self.stats['interacciones_voz'] += 1
            
            # Actualizar UI
            if hasattr(self, 'voice_button'):
                self.voice_button.config(
                    state="disabled", 
                    text="🎤 Escuchando...\nHabla ahora",
                    bg=self.colors['warning']
                )
            self.update_status("🎤 Escuchando comando de voz...")
            
            # Retroalimentación auditiva segura
            self.speak("Escuchando")
            
            def listen_thread():
                try:
                    from speech.recognizer import reconocer_comando_voz
                    comando = reconocer_comando_voz()
                    
                    # Restaurar botón usando after() para thread safety
                    self.root.after(100, self.restore_voice_button)
                    
                    if comando and self.callback:
                        self.stats['comandos_procesados'] += 1
                        # Usar after() para thread safety
                        self.root.after(100, lambda: self.safe_callback(comando))
                        self.root.after(200, lambda: self.update_status(f"✅ Comando procesado: {comando}"))
                    else:
                        self.root.after(100, lambda: self.update_status("❌ No se reconoció comando válido"))
                        self.root.after(200, lambda: self.speak("No entendí el comando"))
                        
                except Exception as e:
                    logger.error(f"Error en hilo de escucha: {e}", exc_info=True)
                    self.root.after(100, self.restore_voice_button)
                    self.root.after(200, lambda: self.update_status("❌ Error en reconocimiento de voz"))
            
            # Iniciar escucha en hilo separado
            threading.Thread(target=listen_thread, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error iniciando escucha: {e}", exc_info=True)
            self.restore_voice_button()
    
    def safe_callback(self, comando):
        """Callback seguro que no puede cerrar la ventana"""
        try:
            if self.callback:
                self.callback(comando)
        except Exception as e:
            logger.error(f"Error en callback: {e}", exc_info=True)
            self.update_status(f"❌ Error procesando comando: {str(e)}")
    
    def restore_voice_button(self):
        """Restaurar estado normal del botón de voz"""
        try:
            if hasattr(self, 'voice_button'):
                self.voice_button.config(
                    state="normal", 
                    text="🎤 Presiona para Hablar\n(Espacio o Click)",
                    bg=self.colors['accent_blue']
                )
        except Exception as e:
            logger.error(f"Error restaurando botón: {e}")
    
    def mostrar_pictograma(self, dispositivo: str):
        """Mostrar pictograma del dispositivo de forma segura"""
        try:
            # Asegurar que se ejecute en el hilo principal
            if threading.current_thread() != threading.main_thread():
                self.root.after(0, lambda: self.mostrar_pictograma(dispositivo))
                return
                
            self.current_device = dispositivo
            
            # Normalizar nombre del dispositivo
            device_key = dispositivo.lower()
            
            if device_key in self.images:
                self.image_label.config(image=self.images[device_key], text="")
                alt_text = self.alt_texts.get(device_key, f"Dispositivo: {dispositivo}")
                self.alt_text_label.config(text=f"📷 {alt_text}")
                self.speak(f"Controlando {dispositivo}")
                logger.info(f"Pictograma mostrado: {dispositivo}")
            else:
                self.image_label.config(image="", text=f"Dispositivo: {dispositivo.capitalize()}")
                self.alt_text_label.config(text=f"Sin imagen disponible para {dispositivo}")
                logger.warning(f"Imagen no disponible para: {dispositivo}")
                
        except Exception as e:
            logger.error(f"Error mostrando pictograma: {e}", exc_info=True)
            try:
                self.image_label.config(image="", text="Error mostrando imagen")
            except:
                pass
    
    def update_status(self, message: str):
        """Actualizar mensaje de estado de forma segura"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=message)
            
            # Actualizar estadísticas
            if hasattr(self, 'stats_label'):
                tiempo_sesion = datetime.now() - self.stats['tiempo_sesion_inicio']
                minutos = int(tiempo_sesion.total_seconds() // 60)
                segundos = int(tiempo_sesion.total_seconds() % 60)
                
                stats_text = (f"Comandos procesados: {self.stats['comandos_procesados']} | "
                             f"Tiempo de sesión: {minutos}:{segundos:02d}")
                self.stats_label.config(text=stats_text)
                
        except Exception as e:
            logger.error(f"Error actualizando estado: {e}")
    
    def speak(self, text: str):
        """Síntesis de voz thread-safe y sin bloqueos"""
        if self.tts_busy or not self.tts_engine:
            return
            
        def _speak():
            try:
                self.tts_busy = True
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"Error en síntesis de voz: {e}")
            finally:
                self.tts_busy = False
        
        threading.Thread(target=_speak, daemon=True).start()
    
    def show_help(self):
        """Mostrar ventana de ayuda"""
        try:
            help_text = """🏠 ASISTENTE INCLUSIVO IoT - AYUDA

COMANDOS DE VOZ DISPONIBLES:
• "Enciende la luz [en habitación]"
• "Apaga el ventilador [en habitación]"  
• "Sube/baja el volumen"
• "Sube/baja el brillo"
• "Dime la hora"
• "Cuánta batería tengo"

ATAJOS DE TECLADO:
• Espacio/Enter: Activar micrófono
• Escape: Salir de la aplicación
• F1: Mostrar esta ayuda

HABITACIONES DISPONIBLES:
• Cocina, Dormitorio, Sala, Baño, Oficina

DISPOSITIVOS DISPONIBLES:
• Luz, Ventilador, Televisor, Calefactor
• Volumen, Brillo"""
            
            messagebox.showinfo("Ayuda - Asistente IoT", help_text)
            
        except Exception as e:
            logger.error(f"Error mostrando ayuda: {e}")
    
    def set_callback(self, callback: Callable[[str], None]):
        """Establecer callback para comandos procesados"""
        self.callback = callback
    
    def on_closing(self):
        """Manejar cierre de aplicación de forma segura"""
        try:
            self.speak("Cerrando asistente. Hasta luego.")
            # Dar tiempo para que se escuche el mensaje
            self.root.after(1500, self.root.destroy)
        except Exception as e:
            logger.error(f"Error cerrando aplicación: {e}")
            self.root.destroy()
    
    def iniciar(self):
        """Iniciar interfaz con manejo robusto de errores"""
        try:
            # Mensaje de bienvenida
            self.speak("Asistente inclusivo iniciado. Presiona el micrófono para comenzar.")
            
            # Iniciar loop principal con manejo de errores
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Error iniciando interfaz: {e}", exc_info=True)
            try:
                messagebox.showerror("Error", f"Error iniciando interfaz: {e}")
            except:
                print(f"Error crítico en interfaz: {e}")

# Compatibilidad con el nombre original
InterfazPictogramas = InterfazPictogramasAccesible