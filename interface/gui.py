import os
import sys
import tkinter as tk
from tkinter import Label, Entry, Button, Frame
from PIL import Image, ImageTk

class InterfazPictogramas:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Asistente Inclusivo IoT")
        self.root.geometry("650x650")
        self.root.configure(bg="#fce4ec")

        self.callback = None
        self.imagenes = {}

        Label(self.root, text="🧠 Asistente Infantil Inclusivo IoT",
              font=("Comic Sans MS", 18, "bold"), bg="#fce4ec", fg="#880e4f").pack(pady=10)

        self.entrada = Entry(self.root, font=("Arial", 14), width=30)
        self.entrada.pack(pady=5)

        self.boton_enviar = Button(self.root, text="📤 Enviar comando", font=("Arial", 12),
                                   bg="#66bb6a", fg="white", command=self.enviar_texto)
        self.boton_enviar.pack(pady=5)

        self.boton_voz = Button(self.root, text="🎤 Hablar", font=("Arial", 12),
                                bg="#42a5f5", fg="white", command=self.escuchar_comando)
        self.boton_voz.pack(pady=5)

        # 🔴 Botón salir justo debajo del botón de hablar
        self.boton_salir = Button(self.root, text="❌ Salir", font=("Arial", 12, "bold"),
                                  bg="#e53935", fg="white", command=self.salir)
        self.boton_salir.pack(pady=5)

        # 🖼️ Cuadro central para pictograma (ajustable según contenido)
        self.frame_central = Frame(self.root, bg="#fce4ec")
        self.frame_central.pack(pady=20)

        self.lbl_central = Label(self.frame_central, bg="#fce4ec")
        self.lbl_central.pack()

        self.cargar_imagenes()

    def cargar_imagenes(self):
        dispositivos = [
            "luz", "ventilador", "televisor", "volumen", "brillo",
            "cocina", "dormitorio", "sala", "bano", "oficina", "calefactor",
            "bateria", "hora"
        ]
        ruta_img = "img"

        for nombre in dispositivos:
            try:
                ruta = os.path.join(ruta_img, f"{nombre}.png")
                img_grande = Image.open(ruta).resize((300, 240), Image.Resampling.LANCZOS)
                self.imagenes[nombre] = ImageTk.PhotoImage(img_grande)
            except Exception as e:
                print(f"⚠️ Error cargando {nombre}.png:", e)

    def mostrar_pictograma(self, dispositivo):
        if dispositivo in self.imagenes:
            self.lbl_central.configure(image=self.imagenes[dispositivo], text="")
            self.lbl_central.image = self.imagenes[dispositivo]
        else:
            self.lbl_central.configure(image='', text="(Sin imagen)", font=("Arial", 12), fg="#9e9e9e")

    def enviar_texto(self):
        comando = self.entrada.get()
        if comando and self.callback:
            self.callback(comando)

    def escuchar_comando(self):
        import threading
        from speech.recognizer import reconocer_comando_voz

        def proceso():
            comando = reconocer_comando_voz()
            if comando and self.callback:
                self.callback(comando)

        threading.Thread(target=proceso).start()


    def set_callback(self, callback):
        self.callback = callback

    def iniciar(self):
        self.root.mainloop()

    def salir(self):
        print("🚪 Cerrando asistente completamente...")
        self.root.destroy()
        sys.exit(0)
