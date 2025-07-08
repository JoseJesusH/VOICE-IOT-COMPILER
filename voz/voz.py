# voz/voz.py

import pyttsx3
import platform

def hablar(texto):
    motor = pyttsx3.init()
    motor.setProperty('rate', 175)
    motor.setProperty('volume', 1.0)

    sistema = platform.system()
    voces = motor.getProperty('voices')

    if sistema == "Darwin":  # macOS
        for voz in voces:
            if "es" in voz.id.lower() or "spanish" in voz.name.lower():
                motor.setProperty('voice', voz.id)
                break
    elif sistema == "Windows":
        try:
            import pythoncom
            pythoncom.CoInitialize()
            for voz in voces:
                if "spanish" in voz.name.lower() or "español" in voz.name.lower():
                    motor.setProperty('voice', voz.id)
                    break
        except ImportError:
            print("❌ pythoncom no disponible en este sistema.")
        except Exception as e:
            print(f"❌ Error inicializando voz en Windows: {e}")
    else:
        # En Linux puedes definir voz por defecto si deseas
        pass

    motor.say(texto)
    motor.runAndWait()

    if sistema == "Windows":
        try:
            pythoncom.CoUninitialize()
        except:
            pass
