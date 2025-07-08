# voz/historial.py

_historial = []

def guardar_historial(comando):
    _historial.append(comando)

def obtener_ultimo_comando():
    if _historial:
        return _historial[-1]
    return None
