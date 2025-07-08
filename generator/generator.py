# generator.py

def generate_code(tokens):
    action = tokens[0][0].lower()
    device = next((val for typ, val in tokens if typ == "DEVICE"), "unknown")
    room = next((val for typ, val in tokens if typ == "ROOM"), None)
    number = next((val for typ, val in tokens if typ == "NUMBER"), None)

    command = f"{action}_{device}"
    if number is not None:
        command += f"_{number}"
    if room:
        command += f"_in_{room.replace(' ', '_')}"

    return command
