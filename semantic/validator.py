# semantic/validator.py

def validar(tokens):
    dispositivos_validos = ["luz", "ventilador", "televisor", "calefactor", "volumen", "brillo", "bateria", "hora"]
    habitaciones_validas = ["cocina", "dormitorio", "sala", "baño", "oficina"]

    dispositivo = None
    habitacion = None
    accion = None
    numero = None

    for tipo, valor in tokens:
        if tipo == "DISPOSITIVO" or tipo in {"BATERIA", "HORA"}:
            if valor not in dispositivos_validos:
                raise ValueError(f"❌ Dispositivo desconocido: '{valor}'")
            dispositivo = valor
        elif tipo == "HABITACION":
            if valor not in habitaciones_validas:
                raise ValueError(f"❌ Habitación no reconocida: '{valor}'")
            habitacion = valor
        elif tipo in {"ENCENDER", "APAGAR", "SUBIR", "BAJAR", "AJUSTAR", "SILENCIAR", "ACTIVAR", "VER"}:
            accion = tipo.lower()
        elif tipo == "NUMERO":
            numero = valor

    if not dispositivo:
        raise ValueError("❌ No se especificó un dispositivo válido.")
    if not accion:
        raise ValueError("❌ No se especificó una acción válida.")

    return accion, dispositivo, habitacion, numero
