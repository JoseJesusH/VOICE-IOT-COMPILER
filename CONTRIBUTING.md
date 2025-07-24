# Contribuir a Voice IoT Compiler

¡Gracias por tu interés en contribuir al proyecto! 

## 🚀 Cómo contribuir

### 1. Setup del entorno de desarrollo

```bash
git clone https://github.com/JoseJesusH/VOICE-IOT-COMPILER.git
cd VOICE-IOT-COMPILER
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Estructura para nuevas funcionalidades

- **Comandos nuevos**: Agregar en `lexer/tokenizer.py`
- **Dispositivos nuevos**: Extender `semantic/validator.py` 
- **Control hardware**: Implementar en `executor/executor.py`
- **UI mejoras**: Modificar `interface/gui.py`

### 3. Estándares de código

- **PEP 8** para formato Python
- **Docstrings** en español para funciones principales
- **Logging** para operaciones importantes
- **Tests** para nuevas funcionalidades

### 4. Pull Request Process

1. Fork del repositorio
2. Crear branch descriptivo (`feature/nueva-funcionalidad`)
3. Implementar cambios con tests
4. Documentar en README si es necesario
5. Abrir Pull Request con descripción detallada

## 🐛 Reportar bugs

Usar [GitHub Issues](https://github.com/JoseJesusH/VOICE-IOT-COMPILER/issues) con:
- Descripción del problema
- Pasos para reproducir  
- Versión de Python/macOS
- Logs relevantes

## 💡 Ideas para contribuir

- [ ] Soporte para más idiomas
- [ ] Integración con HomeKit
- [ ] Mejoras de accesibilidad
- [ ] Control de más dispositivos
- [ ] Tests automatizados
- [ ] Documentación adicional

¡Toda contribución es bienvenida!
