# main.py - DEFINITIVA: Mantiene GUI abierta garantizado

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
import sys

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables globales
gui = None
processing_active = True

def procesar_comando(comando):
    """Procesar comando con manejo de errores mejorado"""
    try:
        print("\n═══════════════════════════════════════")
        print("🎙️ Comando recibido:", comando)
        print("═══════════════════════════════════════\n")

        comando = comando.lower().strip()
        print("📥 Entrada normalizada:")
        print("  ", comando, "\n")

        print("═══════════════════════════════════════")
        print("🔠 Análisis léxico (tokenización):")
        tokens = tokenizar(comando)
        if not tokens:
            print("❌ Error léxico: No se pudieron generar tokens.\n")
            return
        for i, token in enumerate(tokens):
            print(f"  Token {i+1}: {token}")
        print("═══════════════════════════════════════\n")

        print("═══════════════════════════════════════")
        print("🧠 Análisis sintáctico (estructura):")
        try:
            analizar(tokens)
            print("✅ Sintaxis válida")
        except Exception as e:
            print(f"❌ Error de sintaxis: {str(e)}")
            print("═══════════════════════════════════════\n")
            return
        print("═══════════════════════════════════════\n")

        print("═══════════════════════════════════════")
        print("🎯 Análisis semántico (verificando significado):")
        try:
            accion, dispositivo, ubicacion, valor = validar(tokens)
            print(f"✅ Acción: {accion}")
            print(f"✅ Dispositivo: {dispositivo}")
            print(f"✅ Ubicación: {ubicacion or 'No especificada'}")
            print(f"✅ Valor: {valor if valor is not None else 'No especificado'}")
        except Exception as e:
            print(f"❌ Error semántico: {str(e)}")
            print("═══════════════════════════════════════\n")
            return
        print("═══════════════════════════════════════\n")

        print("═══════════════════════════════════════")
        print("🧾 Generación de código:")
        try:
            codigo = generate_code((accion, dispositivo, ubicacion, valor))
            print(f"  Código generado: {codigo}")
        except Exception as e:
            print(f"❌ Error generando código: {str(e)}")
            return
        print("═══════════════════════════════════════\n")

        print("═══════════════════════════════════════")
        print("⚙️ Ejecución de acción:")
        try:
            execute(accion, dispositivo, ubicacion, valor)
            print(f"🔧 Acción ejecutada: {accion} {dispositivo} en {ubicacion or 'global'}")
        except Exception as e:
            print(f"❌ Error ejecutando acción: {str(e)}")
        print("═══════════════════════════════════════\n")

        # Actualizar GUI de forma thread-safe
        if gui:
            try:
                # CRÍTICO: Usar after() para thread-safety
                gui.root.after(0, lambda: safe_update_gui(dispositivo, accion))
            except Exception as e:
                print(f"❌ Error actualizando GUI: {str(e)}")

        print("═══════════════════════════════════════")
        print("📊 Estado actualizado:")
        try:
            actualizar_estado(dispositivo, ubicacion, accion, valor)
            estado = obtener_estado(dispositivo, ubicacion)
            print(f"🔹 {dispositivo}@{ubicacion or 'global'} → acción: {estado.get('accion', 'desconocida')}")
        except Exception as e:
            print(f"❌ Error actualizando estado: {str(e)}")
        print("═══════════════════════════════════════\n")
        
        # IMPORTANTE: Mensaje que confirma que la GUI sigue activa
        print("🎉 Comando procesado exitosamente.")
        print("✅ GUI permanece activa para más comandos.")
        print("🎤 Presiona el botón de micrófono o barra espaciadora para más comandos.\n")
        
    except Exception as e:
        print(f"❌ Error crítico procesando comando: {str(e)}")
        logger.error(f"Error crítico: {e}", exc_info=True)

def safe_update_gui(dispositivo, accion):
    """Actualizar GUI de forma segura desde cualquier hilo"""
    try:
        if gui:
            gui.mostrar_pictograma(dispositivo)
            gui.update_status(f"✅ {accion} {dispositivo} completado")
    except Exception as e:
        print(f"❌ Error en safe_update_gui: {e}")

class VoiceCommandHandler:
    """Manejador de comandos de voz integrado con GUI"""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.listening = False
    
    def handle_voice_command(self):
        """Manejar comando de voz desde GUI"""
        if self.listening:
            return  # Evitar comandos múltiples
            
        try:
            self.listening = True
            print("🎤 Iniciando captura de comando desde GUI...")
            
            # Ejecutar reconocimiento en hilo separado
            def voice_thread():
                try:
                    comando = reconocer_comando_voz()
                    if comando and comando.strip():
                        print(f"✅ Comando capturado: {comando}")
                        # Procesar comando
                        procesar_comando(comando)
                    else:
                        print("⚠️ No se capturó comando válido")
                finally:
                    self.listening = False
            
            threading.Thread(target=voice_thread, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Error en handle_voice_command: {e}")
            self.listening = False

def main():
    """Función principal SIMPLIFICADA que garantiza GUI activa"""
    global gui, processing_active
    
    try:
        print("🚀 INICIANDO VOICE-IOT-COMPILER")
        print("=" * 50)
        print("🎙️ Sistema de reconocimiento de voz en español")
        print("🏠 Control de dispositivos IoT por comandos de voz")
        print("=" * 50)
        
        # Crear GUI PRIMERO
        print("🖥️ Creando interfaz gráfica...")
        gui = InterfazPictogramas()
        
        # Crear manejador de comandos
        voice_handler = VoiceCommandHandler(gui)
        
        # Configurar callback que NO cierra la ventana
        def gui_command_callback(comando):
            """Callback que procesa comandos sin cerrar GUI"""
            try:
                print(f"📞 Callback GUI recibió: {comando}")
                # Procesar en hilo separado para no bloquear GUI
                threading.Thread(
                    target=procesar_comando, 
                    args=(comando,), 
                    daemon=True
                ).start()
            except Exception as e:
                print(f"❌ Error en callback: {e}")
        
        # Configurar callback
        gui.set_callback(gui_command_callback)
        
        # CRÍTICO: Sobrescribir el método de cierre para preguntar
        original_on_closing = gui.on_closing
        def safe_on_closing():
            """Cerrar solo si el usuario confirma"""
            try:
                from tkinter import messagebox
                result = messagebox.askyesno(
                    "Cerrar Aplicación", 
                    "¿Estás seguro de que quieres cerrar el asistente de voz?"
                )
                if result:
                    processing_active = False
                    original_on_closing()
                else:
                    print("✅ Aplicación continúa activa por decisión del usuario")
            except Exception as e:
                print(f"Error en cierre: {e}")
                original_on_closing()
        
        gui.on_closing = safe_on_closing
        
        print("✅ Interfaz configurada correctamente")
        print("🎯 IMPORTANTE: La ventana permanecerá abierta después de procesar comandos")
        print("💡 Usa el botón de micrófono o la barra espaciadora para comandos")
        print("❌ Para cerrar, usa el botón 'Salir' en la ventana")
        print("=" * 50)
        
        # INICIAR GUI MAIN LOOP - esto mantiene la aplicación viva
        print("🎬 Iniciando GUI... (mantendrá la aplicación activa)")
        gui.iniciar()  # Esto es BLOQUEANTE y mantiene la app viva
        
        # Este código solo se ejecuta cuando se cierra la GUI
        print("🔄 GUI cerrada, finalizando aplicación...")
        processing_active = False
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicación cerrada por Ctrl+C")
        processing_active = False
    except Exception as e:
        print(f"❌ Error en main: {str(e)}")
        logger.error(f"Error en main: {e}", exc_info=True)
        
        # Si hay error, mantener ventana básica
        try:
            import tkinter as tk
            root = tk.Tk()
            root.title("Voice IoT Compiler - Error")
            root.geometry("400x200")
            
            tk.Label(root, text=f"Error en aplicación:\n{str(e)}\n\nLa ventana permanece abierta", 
                    font=("Arial", 12), wraplength=380).pack(pady=20)
            
            tk.Button(root, text="Cerrar", command=root.destroy, 
                     font=("Arial", 12)).pack(pady=10)
            
            print("🆘 Ventana de error mostrada - NO se cerrará automáticamente")
            root.mainloop()  # Mantener ventana de error abierta
            
        except:
            print("❌ Error crítico - aplicación terminada")

if __name__ == "__main__":
    main()