def analizar(tokens):
    if not tokens:
        raise ValueError("No se encontraron tokens.")

    if tokens[0][0] in {"SILENCIAR", "ACTIVAR"}:
        return True

    if len(tokens) == 4 and tokens[0][0] == "AJUSTAR" and tokens[1][0] == "DISPOSITIVO" and tokens[2][0] == "A" and tokens[3][0] == "NUMERO":
        return True

    if len(tokens) == 2 and tokens[0][0] in {"SUBIR", "BAJAR", "ENCENDER", "APAGAR"} and tokens[1][0] == "DISPOSITIVO":
        return True

    # 🔥 Add support for: ENCENDER luz cocina
    if len(tokens) == 3 and tokens[0][0] in {"ENCENDER", "APAGAR", "SUBIR", "BAJAR"} and tokens[1][0] == "DISPOSITIVO" and tokens[2][0] == "HABITACION":
        return True

    # 🔥 Add support for: AJUSTAR brillo a 70 cocina
    if len(tokens) == 5 and tokens[0][0] == "AJUSTAR" and tokens[1][0] == "DISPOSITIVO" and tokens[2][0] == "A" and tokens[3][0] == "NUMERO" and tokens[4][0] == "HABITACION":
        return True

    # 🔥 Add support for: VER batería / hora
    if len(tokens) == 2 and tokens[0][0] == "VER" and tokens[1][0] in {"BATERIA", "HORA"}:
        return True

    raise SyntaxError("Comando no reconocido.")
