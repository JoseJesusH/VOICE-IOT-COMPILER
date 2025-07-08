# ✅ tokenizer.py
import re

DISPOSITIVOS_VALIDOS = {
    "luz", "ventilador", "televisor", "calefactor", "volumen", "brillo"
}

HABITACIONES_VALIDAS = {
    "cocina", "dormitorio", "sala", "baño", "oficina"
}

ACCIONES = {
    "ENCENDER": {"enciende", "prende", "activa", "encender"},
    "APAGAR": {"apaga", "desactiva", "apagar"},
    "SUBIR": {"sube", "súbele", "aumenta", "incrementa", "subir"},
    "BAJAR": {"baja", "bájale", "reduce", "disminuye", "bajar"},
    "AJUSTAR": {"ajusta", "pon", "configura", "coloca"},
    "SILENCIAR": {"silencia", "mutea", "calla"},
    "ACTIVAR": {"desmutea", "activa sonido", "vuelve el sonido", "activa"},
    "VER": {"ver", "dime", "muestra", "estado", "cuánto", "cuanta", "cómo"},
}

CONSULTAS = {
    "BATERIA": {"batería", "bateria", "estado de batería", "cuánta batería tengo", "nivel de batería"},
    "HORA": {"hora", "qué hora es", "dime la hora", "hora actual"},
}

def normalizar(palabra):
    return palabra.strip().lower()

def tokenizar(comando):
    tokens = []
    comando = comando.lower()
    palabras = re.findall(r'\w+', comando)

    for palabra in palabras:
        palabra_norm = normalizar(palabra)

        for tipo, conjunto in ACCIONES.items():
            if palabra_norm in conjunto:
                tokens.append((tipo, palabra_norm))
                break
        else:
            for tipo, conjunto in CONSULTAS.items():
                if palabra_norm in conjunto:
                    tokens.append((tipo, palabra_norm))
                    break
            else:
                if re.fullmatch(r"\d+", palabra_norm):
                    tokens.append(("NUMERO", palabra_norm))
                elif palabra_norm in DISPOSITIVOS_VALIDOS:
                    tokens.append(("DISPOSITIVO", palabra_norm))
                elif palabra_norm in HABITACIONES_VALIDAS:
                    tokens.append(("HABITACION", palabra_norm))
                elif palabra_norm in {"a", "al"}:
                    tokens.append(("A", palabra_norm))
    return tokens
