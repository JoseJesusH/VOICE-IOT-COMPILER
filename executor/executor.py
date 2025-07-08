# executor/executor.py

import platform
import os
from datetime import datetime
import psutil
from voz.voz import hablar

OS = platform.system()

# --------- VOLUMEN ----------
if OS == "Windows":
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL

    def get_volume_interface():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))

    def set_volume(level):
        volume = get_volume_interface()
        volume.SetMasterVolumeLevelScalar(max(0.0, min(level / 100.0, 1.0)), None)

    def change_volume(direction):
        volume = get_volume_interface()
        current = volume.GetMasterVolumeLevelScalar()
        delta = 0.1
        new_level = current + delta if direction == "up" else current - delta
        volume.SetMasterVolumeLevelScalar(max(0.0, min(new_level, 1.0)), None)

    def mute_volume():
        get_volume_interface().SetMute(1, None)

    def unmute_volume():
        get_volume_interface().SetMute(0, None)

elif OS == "Darwin":  # macOS
    def set_volume(level):
        os.system(f"osascript -e 'set volume output volume {level}'")

    def change_volume(direction):
        delta = 10
        # Obtener volumen actual
        vol = int(os.popen("osascript -e 'output volume of (get volume settings)'").read())
        new_level = vol + delta if direction == "up" else vol - delta
        new_level = max(0, min(new_level, 100))
        os.system(f"osascript -e 'set volume output volume {new_level}'")

    def mute_volume():
        os.system("osascript -e 'set volume output muted true'")

    def unmute_volume():
        os.system("osascript -e 'set volume output muted false'")

else:
    def set_volume(level): pass
    def change_volume(direction): pass
    def mute_volume(): pass
    def unmute_volume(): pass

# --------- BRILLO ----------
try:
    import screen_brightness_control as sbc

    def set_brightness(level):
        sbc.set_brightness(level)

    def change_brightness(direction):
        current = sbc.get_brightness(display=0)[0]
        delta = 10
        new_level = current + delta if direction == "up" else current - delta
        sbc.set_brightness(max(0, min(new_level, 100)))

except ImportError:
    def set_brightness(level): print("Brillo no soportado en este sistema")
    def change_brightness(direction): print("Brillo no soportado en este sistema")

# --------- UTILIDADES ---------

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return battery.percent
    return None

def get_current_time():
    now = datetime.now()
    return now.strftime("%H:%M")

# --------- EJECUTOR GENERAL ---------

def execute(accion, dispositivo, ubicacion=None, valor=None):
    if accion == "ver":
        if dispositivo == "hora":
            hora = get_current_time()
            print(f"🕒 Hora actual: {hora}")
            hablar(f"La hora actual es {hora}")
        elif dispositivo == "bateria":
            porcentaje = get_battery_status()
            if porcentaje is not None:
                print(f"🔋 Nivel de batería: {porcentaje}%")
                hablar(f"La batería está al {porcentaje} por ciento")
            else:
                print("⚠️ No se pudo obtener el nivel de batería.")
                hablar("No pude obtener el nivel de batería")
        else:
            print(f"👀 Comando 'ver' no implementado para: {dispositivo}")
        return

    if accion == "silenciar":
        mute_volume()
    elif accion == "activar":
        unmute_volume()
    elif dispositivo == "volumen":
        if accion == "ajustar" and valor:
            set_volume(int(valor))
        elif accion == "subir":
            change_volume("up")
        elif accion == "bajar":
            change_volume("down")
    elif dispositivo == "brillo":
        if accion == "ajustar" and valor:
            set_brightness(int(valor))
        elif accion == "subir":
            change_brightness("up")
        elif accion == "bajar":
            change_brightness("down")
    else:
        print(f"🔧 Acción simulada: {accion} {dispositivo}")
