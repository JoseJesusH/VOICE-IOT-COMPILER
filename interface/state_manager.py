# interface/state_manager.py

_state = {}

def update_state(tokens):
    action = tokens[0][0].lower()
    device = next((val for typ, val in tokens if typ == "DISPOSITIVO"), None)
    room = next((val for typ, val in tokens if typ == "HABITACION"), "global")
    number = next((val for typ, val in tokens if typ == "NUMERO"), None)

    if number is not None:
        try:
            number = int(number)
        except ValueError:
            number = None

    key = f"{device}@{room}"
    _state[key] = {"accion": action, "valor": number if number is not None else "N/A"}

def obtener_estado(device, room="global"):
    key = f"{device}@{room}"
    return _state.get(key, {"accion": "ninguna", "valor": "N/A"})

def display_state():
    if not _state:
        print("🕸️ No hay estado registrado aún.")
        return
    for k, v in _state.items():
        print(f"🔹 {k}: acción = {v['accion']}, valor = {v['valor']}")
