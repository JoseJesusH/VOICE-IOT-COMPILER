# speech/recognizer.py

import speech_recognition as sr

def reconocer_comando_voz():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Esperando comando de voz en español...")
        audio = recognizer.listen(source)
        try:
            texto = recognizer.recognize_google(audio, language="es-ES")
            print(f"✅ Comando reconocido: {texto}")
            return texto.lower()
        except sr.UnknownValueError:
            print("❌ No se entendio el audio.")
        except sr.RequestError:
            print("❌ Error de conexión con el servicio de reconocimiento.")
    return None
