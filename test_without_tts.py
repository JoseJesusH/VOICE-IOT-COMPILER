# ============================================================================
# Solución: Crear una versión sin TTS para evitar el conflicto
# ============================================================================

# 1. OPCIÓN RÁPIDA: Crear test_without_tts.py

# test_without_tts.py
from speech.recognizer import reconocer_comando_voz
from lexer.tokenizer import tokenizar
from parser.parser import analizar
from semantic.validator import validar
from generator.generator import generate_code
from executor.executor import execute
from interface.state_manager import obtener_estado, actualizar_estado
from interface.gui import InterfazPictogramas
import threading
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable global para la GUI
gui = None

def procesar_comando(comando):
    """Procesar comando sin TTS"""
    try:
        print("\n" + "="*70)
        print(f"🎙️ COMANDO: {comando}")
        print("="*70)

        comando = comando.lower().strip()
        print(f"📥 Normalizado: {comando}")

        # Análisis léxico
        print("\n🔠 ANÁLISIS LÉXICO:")
        tokens = tokenizar(comando)
        if not tokens:
            print("❌ Sin tokens")
            return
        for i, token in enumerate(tokens):
            print(f"  Token {i+1}: {token}")

        # Análisis sintáctico
        print("\n🧠 ANÁLISIS SINTÁCTICO:")
        try:
            analizar(tokens)
            print("✅ Sintaxis válida")
        except Exception as e:
            print(f"❌ Error sintáctico: {e}")
            return

        # Análisis semántico
        print("\n🎯 ANÁLISIS SEMÁNTICO:")
        try:
            accion, dispositivo, ubicacion, valor = validar(tokens)
            print(f"✅ Acción: {accion}")
            print(f"✅ Dispositivo: {dispositivo}")
            print(f"✅ Ubicación: {ubicacion or 'No especificada'}")
            print(f"✅ Valor: {valor or 'No especificado'}")
        except Exception as e:
            print(f"❌ Error semántico: {e}")
            return

        # Generación de código
        print("\n🧾 GENERACIÓN DSL:")
        try:
            codigo = generate_code((accion, dispositivo, ubicacion, valor))
            print(f"✅ Código: {codigo}")
        except Exception as e:
            print(f"❌ Error generando: {e}")
            return

        # Ejecución (sin TTS)
        print("\n⚙️ EJECUCIÓN:")
        try:
            execute(accion, dispositivo, ubicacion, valor)
            print(f"✅ Ejecutado: {accion} {dispositivo}")
        except Exception as e:
            print(f"❌ Error ejecutando: {e}")

        # Actualizar GUI
        print("\n🖥️ ACTUALIZANDO GUI:")
        if gui:
            try:
                gui.root.after(0, lambda: gui.mostrar_pictograma(dispositivo))
                print("✅ Pictograma actualizado")
            except Exception as e:
                print(f"❌ Error GUI: {e}")

        # Actualizar estado
        print("\n📊 ACTUALIZANDO ESTADO:")
        try:
            actualizar_estado(dispositivo, ubicacion, accion, valor)
            estado = obtener_estado(dispositivo, ubicacion)
            print(f"✅ Estado: {dispositivo} → {estado.get('accion', 'N/A')}")
        except Exception as e:
            print(f"❌ Error estado: {e}")

        print("\n" + "="*70)
        print("✅ COMANDO PROCESADO COMPLETAMENTE")
        print("✅ GUI DEBE MANTENERSE ABIERTA")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        logger.error(f"Error crítico: {e}", exc_info=True)

def escuchar():
    """Escuchar comandos"""
    while True:
        try:
            comando = reconocer_comando_voz()
            if comando:
                print(f"\n🎤 NUEVO COMANDO DETECTADO: {comando}")
                threading.Thread(target=procesar_comando, args=(comando,), daemon=True).start()
        except Exception as e:
            print(f"❌ Error escuchando: {e}")
            threading.Event().wait(2)

class SimpleGUI:
    """GUI simplificada sin TTS para evitar conflictos"""
    def __init__(self):
        import tkinter as tk
        from PIL import Image, ImageTk
        import os
        
        self.root = tk.Tk()
        self.root.title("🏠 Asistente IoT - Sin TTS")
        self.root.geometry("800x600")
        self.root.configure(bg='#fce4ec')
        self.callback = None
        self.images = {}
        
        # Cargar imágenes
        self.load_images()
        
        # Crear interfaz
        self.create_interface()
        
        # Manejar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_images(self):
        """Cargar imágenes sin errores"""
        try:
            from PIL import Image, ImageTk
            import os
            
            devices = ["luz", "ventilador", "televisor", "volumen", "brillo", 
                      "cocina", "dormitorio", "sala", "bano", "baño", "oficina", 
                      "calefactor", "bateria", "hora"]
            
            for device in devices:
                try:
                    img_path = f"img/{device}.png"
                    if os.path.exists(img_path):
                        img = Image.open(img_path).resize((300, 240))
                        self.images[device] = ImageTk.PhotoImage(img)
                        print(f"✅ Imagen cargada: {device}")
                except:
                    pass
        except Exception as e:
            print(f"Error cargando imágenes: {e}")
    
    def create_interface(self):
        """Crear interfaz simple"""
        import tkinter as tk
        
        # Título
        title = tk.Label(self.root, text="🏠 Asistente IoT (Sin TTS)", 
                        font=('Arial', 20, 'bold'), bg='#fce4ec', fg='#880e4f')
        title.pack(pady=20)
        
        # Botón de voz
        self.voice_btn = tk.Button(self.root, text="🎤 HABLAR", 
                                  font=('Arial', 16, 'bold'), bg='#42a5f5', fg='white',
                                  width=20, height=2, command=self.start_listening)
        self.voice_btn.pack(pady=20)
        
        # Área de imagen
        self.img_label = tk.Label(self.root, text="Presiona el micrófono\npara comenzar", 
                                 font=('Arial', 14), bg='#fce4ec')
        self.img_label.pack(expand=True)
        
        # Estado
        self.status_label = tk.Label(self.root, text="✅ Sistema listo", 
                                    font=('Arial', 12), bg='#e1f5fe')
        self.status_label.pack(fill='x', padx=20, pady=10)
        
        # Botón salir
        exit_btn = tk.Button(self.root, text="❌ Salir", font=('Arial', 12),
                           bg='#e53935', fg='white', command=self.on_closing)
        exit_btn.pack(pady=10)
        
        # Atajos de teclado
        self.root.bind('<space>', lambda e: self.start_listening())
        self.root.bind('<Escape>', lambda e: self.on_closing())
        self.root.focus_set()
    
    def start_listening(self):
        """Iniciar escucha sin TTS"""
        self.voice_btn.config(state='disabled', text='🎤 ESCUCHANDO...', bg='#ff9800')
        self.status_label.config(text='🎤 Escuchando comando...')
        
        def listen():
            try:
                from speech.recognizer import reconocer_comando_voz
                comando = reconocer_comando_voz()
                
                self.root.after(100, self.restore_button)
                
                if comando and self.callback:
                    self.root.after(100, lambda: self.safe_callback(comando))
                    self.root.after(200, lambda: self.status_label.config(text=f'✅ Procesado: {comando}'))
                else:
                    self.root.after(100, lambda: self.status_label.config(text='❌ No se reconoció comando'))
            except Exception as e:
                print(f"Error en escucha: {e}")
                self.root.after(100, self.restore_button)
        
        threading.Thread(target=listen, daemon=True).start()
    
    def restore_button(self):
        """Restaurar botón"""
        self.voice_btn.config(state='normal', text='🎤 HABLAR', bg='#42a5f5')
    
    def safe_callback(self, comando):
        """Callback seguro"""
        try:
            if self.callback:
                self.callback(comando)
        except Exception as e:
            print(f"Error en callback: {e}")
            self.status_label.config(text=f'❌ Error: {e}')
    
    def mostrar_pictograma(self, dispositivo):
        """Mostrar pictograma"""
        try:
            device_key = dispositivo.lower()
            if device_key in self.images:
                self.img_label.config(image=self.images[device_key], text='')
                print(f"✅ Mostrando imagen de {dispositivo}")
            else:
                self.img_label.config(image='', text=f'Dispositivo: {dispositivo}')
                print(f"⚠️ Sin imagen para {dispositivo}")
        except Exception as e:
            print(f"Error mostrando pictograma: {e}")
    
    def set_callback(self, callback):
        """Establecer callback"""
        self.callback = callback
    
    def on_closing(self):
        """Cerrar aplicación"""
        print("🛑 Cerrando aplicación...")
        self.root.destroy()
    
    def iniciar(self):
        """Iniciar GUI"""
        print("🖥️ Iniciando GUI simplificada...")
        self.root.mainloop()

def main():
    """Función principal sin TTS"""
    global gui
    
    try:
        print("🚀 INICIANDO SISTEMA SIN TTS")
        print("="*50)
        
        # Usar GUI simplificada
        gui = SimpleGUI()
        gui.set_callback(procesar_comando)
        
        # Iniciar escucha
        threading.Thread(target=escuchar, daemon=True).start()
        print("✅ Escucha iniciada")
        
        # Iniciar GUI
        gui.iniciar()
        
    except Exception as e:
        print(f"❌ Error en main: {e}")

if __name__ == "__main__":
    main()
