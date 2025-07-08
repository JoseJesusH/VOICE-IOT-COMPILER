# ============================================================================
# debug_images.py - Script para debuggear problema de imágenes
# ============================================================================

import os
from pathlib import Path

def debug_images():
    """Debuggear problema de carga de imágenes"""
    print("🔍 DEBUGGING IMÁGENES")
    print("=" * 50)
    
    # 1. Verificar qué archivos existen realmente
    img_dir = Path("img")
    if img_dir.exists():
        print("📁 Archivos en directorio img/:")
        archivos_reales = []
        for archivo in sorted(img_dir.iterdir()):
            if archivo.is_file():
                archivos_reales.append(archivo.name)
                print(f"   ✅ {archivo.name}")
        print()
    else:
        print("❌ Directorio img/ no existe")
        return
    
    # 2. Verificar qué archivos busca el código
    dispositivos_esperados = [
        "luz", "ventilador", "televisor", "volumen", "brillo", 
        "cocina", "dormitorio", "sala", "baño", "oficina", 
        "calefactor", "bateria", "hora"
    ]
    
    print("🔍 Archivos que busca el código:")
    archivos_faltantes = []
    archivos_encontrados = []
    
    for dispositivo in dispositivos_esperados:
        archivo_esperado = f"{dispositivo}.png"
        ruta_completa = img_dir / archivo_esperado
        
        if ruta_completa.exists():
            print(f"   ✅ {archivo_esperado}")
            archivos_encontrados.append(archivo_esperado)
        else:
            print(f"   ❌ {archivo_esperado}")
            archivos_faltantes.append(archivo_esperado)
    
    print()
    
    # 3. Analizar discrepancias
    print("🔍 ANÁLISIS DE DISCREPANCIAS:")
    print("=" * 30)
    
    if archivos_faltantes:
        print("❌ Archivos faltantes:")
        for archivo in archivos_faltantes:
            print(f"   • {archivo}")
        print()
    
    # 4. Buscar archivos similares
    print("🔍 Buscando archivos similares:")
    for faltante in archivos_faltantes:
        nombre_base = faltante.replace('.png', '')
        print(f"\nPara '{faltante}':")
        
        # Buscar variaciones
        variaciones_encontradas = []
        for real in archivos_reales:
            nombre_real = real.replace('.png', '').lower()
            if nombre_base in nombre_real or nombre_real in nombre_base:
                variaciones_encontradas.append(real)
        
        if variaciones_encontradas:
            print(f"   Encontradas variaciones: {variaciones_encontradas}")
        else:
            print(f"   No se encontraron variaciones")
    
    # 5. Probar la función de carga de imágenes
    print("\n🧪 PROBANDO CARGA DE IMÁGENES:")
    print("=" * 35)
    
    try:
        from interface.gui import InterfazPictogramasAccesible
        
        # Crear instancia temporal para probar carga
        gui_test = InterfazPictogramasAccesible()
        
        print("Imágenes cargadas exitosamente:")
        for dispositivo in dispositivos_esperados:
            if dispositivo in gui_test.images:
                print(f"   ✅ {dispositivo}")
            else:
                print(f"   ❌ {dispositivo}")
        
    except Exception as e:
        print(f"❌ Error probando GUI: {e}")
    
    # 6. Generar comandos de corrección
    print("\n🔧 COMANDOS DE CORRECCIÓN:")
    print("=" * 30)
    
    if 'baño.png' in archivos_reales and 'bano.png' not in archivos_reales:
        print("# Crear enlace para baño:")
        print("cp img/baño.png img/bano.png")
    
    if 'batería.png' in archivos_reales and 'bateria.png' not in archivos_reales:
        print("# Crear enlace para batería:")
        print("cp img/batería.png img/bateria.png")
    
    # Sugerir creación de archivos faltantes
    if archivos_faltantes:
        print("\n# Crear archivos faltantes:")
        for faltante in archivos_faltantes:
            if faltante not in archivos_reales:
                print(f"# Falta: {faltante}")

def fix_images():
    """Corregir nombres de archivos automáticamente"""
    print("🔧 CORRIGIENDO NOMBRES DE ARCHIVOS")
    print("=" * 40)
    
    img_dir = Path("img")
    
    # Mapeo de correcciones
    correcciones = {
        'baño.png': 'bano.png',
        'batería.png': 'bateria.png'
    }
    
    for original, corregido in correcciones.items():
        archivo_original = img_dir / original
        archivo_corregido = img_dir / corregido
        
        if archivo_original.exists() and not archivo_corregido.exists():
            try:
                import shutil
                shutil.copy2(archivo_original, archivo_corregido)
                print(f"✅ Copiado: {original} → {corregido}")
            except Exception as e:
                print(f"❌ Error copiando {original}: {e}")
        elif archivo_corregido.exists():
            print(f"ℹ️  Ya existe: {corregido}")
        else:
            print(f"❌ No encontrado: {original}")

def test_image_loading():
    """Probar carga de una imagen específica"""
    print("🧪 PROBANDO CARGA DE IMAGEN ESPECÍFICA")
    print("=" * 40)
    
    try:
        from PIL import Image
        import os
        
        # Probar con luz
        test_file = "img/luz.png"
        if os.path.exists(test_file):
            img = Image.open(test_file)
            print(f"✅ {test_file} se puede abrir")
            print(f"   Tamaño: {img.size}")
            print(f"   Modo: {img.mode}")
        else:
            print(f"❌ {test_file} no existe")
        
        # Listar todos los PNG en img/
        img_files = [f for f in os.listdir("img") if f.endswith('.png')]
        print(f"\n📁 Archivos PNG encontrados ({len(img_files)}):")
        for f in sorted(img_files):
            print(f"   • {f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_images()
    print()
    fix_images()
    print()
    test_image_loading()
