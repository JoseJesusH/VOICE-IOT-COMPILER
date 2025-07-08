# main.py

from speech.recognizer import reconocer_comando_voz
from lexer.tokenizer import tokenizar
from parser.parser import analizar
from semantic.validator import validar
from generator.generator import generate_code
from executor.executor import execute
from interface.state_manager import obtener_estado
from interface.gui import InterfazPictogramas
import threading


# Variable global para la GUI
gui = None

def procesar_comando(comando):
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
    codigo = generate_code(tokens)
    print(f"  Código generado: {codigo}")
    print("═══════════════════════════════════════\n")

    print("═══════════════════════════════════════")
    print("⚙️ Ejecución de acción:")
    execute(accion, dispositivo, ubicacion, valor)
    print(f"🔧 Acción ejecutada: {accion} {dispositivo} en {ubicacion or 'global'}")
    print("═══════════════════════════════════════\n")

    if gui:
        gui.mostrar_pictograma(dispositivo)

    print("═══════════════════════════════════════")
    print("📊 Estado actualizado:")
    estado = obtener_estado(dispositivo, ubicacion)
    print(f"🔹 {dispositivo}@{ubicacion or 'global'} → acción: {estado['accion']}")
    print("═══════════════════════════════════════\n")

def escuchar():
    while True:
        comando = reconocer_comando_voz()
        if comando:
            threading.Thread(target=procesar_comando, args=(comando,)).start()

def iniciar_interfaz():
    global gui
    gui = InterfazPictogramas()
    gui.set_callback(procesar_comando)
    gui.iniciar()

def main():
    print("🎙️ Esperando comando de voz en español...")
    threading.Thread(target=escuchar, daemon=True).start()
    iniciar_interfaz()

if __name__ == "__main__":
    main()
