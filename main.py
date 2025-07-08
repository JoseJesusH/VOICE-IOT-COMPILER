# main.py - Versión con correcciones mínimas

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
            # Corregir la llamada al generador
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

        if gui:
            try:
                gui.mostrar_pictograma(dispositivo)
            except Exception as e:
                print(f"❌ Error mostrando pictograma: {str(e)}")

        print("═══════════════════════════════════════")
        print("📊 Estado actualizado:")
        try:
            # Actualizar estado primero
            actualizar_estado(dispositivo, ubicacion, accion, valor)
            
            # Luego obtener el estado actualizado
            estado = obtener_estado(dispositivo, ubicacion)
            print(f"🔹 {dispositivo}@{ubicacion or 'global'} → acción: {estado.get('accion', 'desconocida')}")
        except Exception as e:
            print(f"❌ Error actualizando estado: {str(e)}")
        print("═══════════════════════════════════════\n")
        
    except Exception as e:
        print(f"❌ Error crítico procesando comando: {str(e)}")
        logger.error(f"Error crítico: {e}", exc_info=True)

def escuchar():
    """Función de escucha con manejo de errores"""
    while True:
        try:
            comando = reconocer_comando_voz()
            if comando:
                threading.Thread(target=procesar_comando, args=(comando,), daemon=True).start()
        except Exception as e:
            print(f"❌ Error en escucha: {str(e)}")
            logger.error(f"Error en escucha: {e}")
            # Pausa breve antes de reintentar
            threading.Event().wait(2)

def iniciar_interfaz():
    """Iniciar interfaz con manejo de errores"""
    global gui
    try:
        gui = InterfazPictogramas()
        gui.set_callback(procesar_comando)
        gui.iniciar()
    except Exception as e:
        print(f"❌ Error iniciando interfaz: {str(e)}")
        logger.error(f"Error en interfaz: {e}", exc_info=True)

def main():
    """Función principal con manejo de errores"""
    try:
        print("🎙️ Esperando comando de voz en español...")
        threading.Thread(target=escuchar, daemon=True).start()
        iniciar_interfaz()
    except KeyboardInterrupt:
        print("\n🛑 Cerrando sistema...")
    except Exception as e:
        print(f"❌ Error en main: {str(e)}")
        logger.error(f"Error en main: {e}", exc_info=True)

if __name__ == "__main__":
    main()