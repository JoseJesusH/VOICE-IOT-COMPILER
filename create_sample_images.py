# ============================================================================
# create_sample_images.py - Script para crear imágenes de ejemplo
# ============================================================================

from PIL import Image, ImageDraw, ImageFont
import os

def create_device_image(device_name, emoji, color, size=(320, 260)):
    """Crear imagen simple para un dispositivo"""
    # Crear imagen con fondo
    img = Image.new('RGB', size, color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Dibujar fondo con color del dispositivo
    draw.rectangle([20, 20, size[0]-20, size[1]-20], fill=color, outline='#333333', width=3)
    
    # Intentar usar una fuente más grande
    try:
        # Para macOS
        font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)
        font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        try:
            # Para otros sistemas
            font_large = ImageFont.truetype("arial.ttf", 60)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            # Fuente por defecto
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Dibujar emoji y texto
    text_emoji = emoji
    text_name = device_name.upper()
    
    # Calcular posición centrada para emoji
    bbox_emoji = draw.textbbox((0, 0), text_emoji, font=font_large)
    emoji_width = bbox_emoji[2] - bbox_emoji[0]
    emoji_height = bbox_emoji[3] - bbox_emoji[1]
    emoji_x = (size[0] - emoji_width) // 2
    emoji_y = (size[1] - emoji_height) // 2 - 20
    
    # Dibujar emoji
    draw.text((emoji_x, emoji_y), text_emoji, fill='white', font=font_large)
    
    # Calcular posición centrada para nombre
    bbox_name = draw.textbbox((0, 0), text_name, font=font_small)
    name_width = bbox_name[2] - bbox_name[0]
    name_x = (size[0] - name_width) // 2
    name_y = emoji_y + emoji_height + 10
    
    # Dibujar nombre
    draw.text((name_x, name_y), text_name, fill='#333333', font=font_small)
    
    return img

def create_all_images():
    """Crear todas las imágenes necesarias"""
    
    # Crear directorio img si no existe
    os.makedirs('img', exist_ok=True)
    
    # Definir dispositivos con emojis y colores
    devices = {
        'luz': ('💡', '#FFC107'),           # Amarillo
        'ventilador': ('🌀', '#2196F3'),    # Azul
        'televisor': ('📺', '#9C27B0'),     # Púrpura
        'calefactor': ('🔥', '#FF5722'),    # Rojo
        'volumen': ('🔊', '#4CAF50'),       # Verde
        'brillo': ('☀️', '#FF9800'),        # Naranja
        'cocina': ('🍳', '#795548'),        # Marrón
        'dormitorio': ('🛏️', '#E91E63'),    # Rosa
        'sala': ('🛋️', '#607D8B'),          # Azul gris
        'baño': ('🚿', '#00BCD4'),          # Cian
        'oficina': ('💻', '#9E9E9E'),       # Gris
        'bateria': ('🔋', '#8BC34A'),       # Verde claro
        'hora': ('⏰', '#673AB7')           # Violeta
    }
    
    print("🎨 Creando imágenes de pictogramas...")
    
    for device, (emoji, color) in devices.items():
        try:
            img = create_device_image(device, emoji, color)
            filename = f'img/{device}.png'
            img.save(filename)
            print(f"   ✅ {filename}")
        except Exception as e:
            print(f"   ❌ Error creando {device}.png: {e}")
    
    print("✅ Imágenes creadas exitosamente!")

def create_simple_placeholder():
    """Crear una imagen placeholder simple si hay problemas con fuentes"""
    try:
        # Imagen simple sin texto
        img = Image.new('RGB', (320, 260), color='#e0e0e0')
        draw = ImageDraw.Draw(img)
        
        # Dibujar un círculo simple
        draw.ellipse([80, 65, 240, 195], fill='#42a5f5', outline='#1976d2', width=5)
        
        # Guardar como ejemplo
        img.save('img/placeholder.png')
        print("✅ Imagen placeholder creada")
        
    except Exception as e:
        print(f"❌ Error creando placeholder: {e}")

if __name__ == "__main__":
    create_all_images()
    create_simple_placeholder()
