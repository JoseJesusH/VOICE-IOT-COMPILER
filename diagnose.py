# ============================================================================
# diagnose.py - Script de diagnóstico completo
# ============================================================================

import sys
import os
import importlib
from pathlib import Path
import subprocess

def check_python_version():
    """Verificar versión de Python"""
    print("🐍 Verificando Python...")
    if sys.version_info >= (3, 8):
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
    else:
        print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} (se requiere 3.8+)")
        return False

def check_dependencies():
    """Verificar dependencias"""
    print("📦 Verificando dependencias...")
    
    dependencies = {
        'speech_recognition': 'Reconocimiento de voz',
        'pyttsx3': 'Síntesis de voz',
        'PIL': 'Procesamiento de imágenes (Pillow)',
        'psutil': 'Información del sistema',
        'tkinter': 'Interfaz gráfica'
    }
    
    missing = []
    
    for module, description in dependencies.items():
        try:
            importlib.import_module(module)
            print(f"   ✅ {description}")
        except ImportError:
            print(f"   ❌ {description} ({module})")
            missing.append(module)
    
    return missing

def check_project_structure():
    """Verificar estructura del proyecto"""
    print("📁 Verificando estructura del proyecto...")
    
    required_files = [
        'main.py',
        'speech/__init__.py',
        'speech/recognizer.py',
        'lexer/__init__.py', 
        'lexer/tokenizer.py',
        'parser/__init__.py',
        'parser/parser.py',
        'semantic/__init__.py',
        'semantic/validator.py',
        'generator/__init__.py',
        'generator/generator.py',
        'executor/executor.py',
        'interface/__init__.py',
        'interface/gui.py',
        'interface/state_manager.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            missing_files.append(file_path)
    
    return missing_files

def check_directories():
    """Verificar directorios necesarios"""
    print("📂 Verificando directorios...")
    
    required_dirs = ['img', 'logs', 'config']
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ (creando...)")
            Path(dir_name).mkdir(exist_ok=True)
            print(f"   ✅ {dir_name}/ creado")

def check_imports():
    """Verificar importaciones del proyecto"""
    print("🔄 Verificando importaciones del proyecto...")
    
    modules_to_test = [
        ('speech.recognizer', 'reconocer_comando_voz'),
        ('lexer.tokenizer', 'tokenizar'),
        ('parser.parser', 'analizar'),
        ('semantic.validator', 'validar'),
        ('generator.generator', 'generate_code'),
        ('executor.executor', 'execute'),
        ('interface.gui', 'InterfazPictogramasAccesible')
    ]
    
    import_errors = []
    
    for module_name, function_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, function_name):
                print(f"   ✅ {module_name}.{function_name}")
            else:
                print(f"   ❌ {module_name}.{function_name} (función no encontrada)")
                import_errors.append(f"{module_name}.{function_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}: {e}")
            import_errors.append(module_name)
        except Exception as e:
            print(f"   ❌ {module_name}: Error inesperado - {e}")
            import_errors.append(module_name)
    
    return import_errors

def test_basic_functionality():
    """Probar funcionalidad básica"""
    print("🧪 Probando funcionalidad básica...")
    
    try:
        # Probar tokenizador
        from lexer.tokenizer import tokenizar
        tokens = tokenizar("enciende la luz")
        if tokens:
            print("   ✅ Tokenizador funciona")
        else:
            print("   ❌ Tokenizador no genera tokens")
            return False
        
        # Probar parser
        from parser.parser import analizar
        analizar(tokens)
        print("   ✅ Parser funciona")
        
        # Probar validador
        from semantic.validator import validar
        validar(tokens)
        print("   ✅ Validador semántico funciona")
        
        # Probar generador
        from generator.generator import generate_code
        code = generate_code(("ENCENDER", "LUZ", None, None))
        if code:
            print("   ✅ Generador de código funciona")
        else:
            print("   ❌ Generador no produce código")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en funcionalidad básica: {e}")
        return False

def check_audio_system():
    """Verificar sistema de audio"""
    print("🔊 Verificando sistema de audio...")
    
    try:
        import speech_recognition as sr
        import pyttsx3
        
        # Probar reconocedor
        recognizer = sr.Recognizer()
        print("   ✅ Reconocedor de voz inicializado")
        
        # Probar TTS
        tts = pyttsx3.init()
        voices = tts.getProperty('voices')
        print(f"   ✅ TTS inicializado ({len(voices)} voces disponibles)")
        
        # Buscar voz en español
        spanish_voice = None
        for voice in voices:
            if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                spanish_voice = voice
                break
        
        if spanish_voice:
            print(f"   ✅ Voz en español encontrada: {spanish_voice.name}")
        else:
            print("   ⚠️ No se encontró voz en español específica")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en sistema de audio: {e}")
        return False

def install_missing_dependencies(missing_deps):
    """Instalar dependencias faltantes"""
    if not missing_deps:
        return True
    
    print(f"�� Instalando {len(missing_deps)} dependencias faltantes...")
    
    # Mapear nombres de módulos a nombres de paquetes
    package_mapping = {
        'speech_recognition': 'SpeechRecognition',
        'PIL': 'Pillow',
        'pyttsx3': 'pyttsx3',
        'psutil': 'psutil'
    }
    
    for dep in missing_deps:
        if dep == 'tkinter':
            print(f"   ⚠️ tkinter debería estar incluido con Python")
            continue
            
        package_name = package_mapping.get(dep, dep)
        
        try:
            print(f"   📥 Instalando {package_name}...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   ✅ {package_name} instalado")
        except subprocess.CalledProcessError:
            print(f"   ❌ Error instalando {package_name}")
            return False
    
    return True

def create_missing_files():
    """Crear archivos __init__.py faltantes"""
    print("📄 Creando archivos faltantes...")
    
    modules = ['speech', 'lexer', 'parser', 'semantic', 'generator', 'interface']
    
    for module in modules:
        os.makedirs(module, exist_ok=True)
        init_file = Path(module) / '__init__.py'
        if not init_file.exists():
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(f'"""Módulo {module} del compilador IoT"""\n')
            print(f"   ✅ {init_file} creado")

def main():
    """Función principal de diagnóstico"""
    print("🏥 DIAGNÓSTICO DEL COMPILADOR DE COMANDOS DE VOZ IoT")
    print("=" * 60)
    
    all_good = True
    
    # Verificar Python
    if not check_python_version():
        print("\n❌ Versión de Python insuficiente")
        return False
    
    # Verificar dependencias
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"\n⚠️ Faltan {len(missing_deps)} dependencias")
        if input("¿Deseas instalarlas automáticamente? (s/n): ").lower() == 's':
            if not install_missing_dependencies(missing_deps):
                all_good = False
        else:
            all_good = False
    
    # Verificar estructura
    check_directories()
    missing_files = check_project_structure()
    if missing_files:
        print(f"\n⚠️ Faltan {len(missing_files)} archivos del proyecto")
        all_good = False
        
        if 'speech/__init__.py' in missing_files or 'lexer/__init__.py' in missing_files:
            create_missing_files()
    
    # Verificar importaciones
    import_errors = check_imports()
    if import_errors:
        print(f"\n⚠️ {len(import_errors)} errores de importación")
        all_good = False
    
    # Probar funcionalidad
    if all_good:
        if not test_basic_functionality():
            all_good = False
    
    # Verificar audio
    if not check_audio_system():
        print("\n⚠️ Problemas con el sistema de audio")
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_good:
        print("✅ DIAGNÓSTICO COMPLETADO: Sistema listo para funcionar")
        print("\nPara ejecutar el proyecto:")
        print("   python main.py")
        print("\nPara crear imágenes de ejemplo:")
        print("   python create_sample_images.py")
    else:
        print("❌ DIAGNÓSTICO COMPLETADO: Se encontraron problemas")
        print("\nProblemas encontrados:")
        if missing_deps:
            print(f"   • {len(missing_deps)} dependencias faltantes")
        if missing_files:
            print(f"   • {len(missing_files)} archivos faltantes")
        if import_errors:
            print(f"   • {len(import_errors)} errores de importación")
        
        print("\nSoluciones sugeridas:")
        print("   1. Instalar dependencias: pip install SpeechRecognition pyttsx3 Pillow psutil")
        print("   2. Verificar que todos los archivos .py estén en su lugar")
        print("   3. Ejecutar este diagnóstico nuevamente")
    
    return all_good

if __name__ == "__main__":
    main()
