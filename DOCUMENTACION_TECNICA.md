# 🏠 VOICE IOT COMPILER - Documentación Técnica Completa

## 📋 Índice
1. [Introducción y Arquitectura](#introducción-y-arquitectura)
2. [Pipeline de Procesamiento](#pipeline-de-procesamiento)
3. [Análisis Léxico (Tokenización)](#análisis-léxico-tokenización)
4. [Análisis Sintáctico (Parser)](#análisis-sintáctico-parser)
5. [Análisis Semántico (Validación)](#análisis-semántico-validación)
6. [Generación de Código DSL](#generación-de-código-dsl)
7. [Ejecutor de Acciones](#ejecutor-de-acciones)
8. [Interfaz Gráfica y Accesibilidad](#interfaz-gráfica-y-accesibilidad)
9. [Flujo de Trabajo Completo](#flujo-de-trabajo-completo)
10. [Tipos de Comandos Soportados](#tipos-de-comandos-soportados)
11. [Arquitectura del Software](#arquitectura-del-software)
12. [Conclusiones](#conclusiones)

---

## 🚀 **COMANDOS QUE CONTROLAN HARDWARE REAL DE MACOS**

### ✅ **Control Real de Volumen**
```bash
🗣️ "sube volumen"          → 🔊 Volumen REAL +10%
🗣️ "baja volumen"          → 🔊 Volumen REAL -10%
🗣️ "ajusta volumen a 50"   → 🔊 Volumen REAL al 50%
🗣️ "silencia volumen"      → 🔇 Mac se silencia completamente
🗣️ "activa volumen"        → 🔊 Reactiva audio silenciado
```

### ✅ **Control Real de Brillo (via comandos de "luz")**
```bash
🗣️ "enciende luz en cocina" → 🔆 Brillo REAL al 80%
🗣️ "apaga luz en sala"      → 🔅 Brillo REAL al 20%
🗣️ "sube luz"               → 🔆 Brillo REAL +10%
🗣️ "baja luz"               → 🔅 Brillo REAL -10%
```

### ✅ **Control Real de Aplicaciones**
```bash
🗣️ "enciende televisor"     → 📺 Abre QuickTime Player
🗣️ "apaga televisor"        → 📺 Cierra QuickTime Player
```

### 🎭 **Comandos Solo Simulados (GUI únicamente)**
```bash
🗣️ "enciende ventilador"    → 🌀 Solo actualiza GUI
🗣️ "enciende calefactor"    → 🔥 Solo actualiza GUI
🗣️ "dime la hora"           → 🕐 Muestra hora real del sistema
🗣️ "ver batería"            → 🔋 Muestra batería real del sistema
```

---

## � Extensiones y Mejoras Implementadas

### Control Real de macOS

El sistema ahora incluye **control real** del MacBook Air M2 mediante:

#### 1. **Control de Volumen**
```bash
# Comandos macOS implementados
osascript -e "set volume output volume 70"        # Ajustar volumen
osascript -e "set volume with output muted"       # Silenciar
osascript -e "set volume without output muted"    # Activar
```

#### 2. **Control de Brillo**
```bash
# Control real de brillo de pantalla
osascript -e "tell application \"System Events\" to set brightness of displays to 0.8"
```

#### 3. **Mapeo Inteligente IoT → macOS**
| Comando IoT | Control Real macOS |
|-------------|-------------------|
| `"enciende luz en cocina"` | Brillo pantalla → 80% |
| `"apaga luz en dormitorio"` | Brillo pantalla → 20% |
| `"sube luz en sala"` | Incrementa brillo +10% |
| `"enciende ventilador"` | Efectos del sistema |
| `"enciende televisor"` | Abre QuickTime Player |

### Retroalimentación de Voz Mejorada

#### Mensajes Específicos por Acción
```python
def obtener_mensaje_retroalimentacion(self, accion, dispositivo, ubicacion, valor):
    if dispositivo == "luz" and ubicacion:
        if accion == "encender":
            return f"Encendiendo luz en {ubicacion} - aumentando brillo de pantalla"
        elif accion == "apagar":
            return f"Apagando luz en {ubicacion} - disminuyendo brillo de pantalla"
    
    elif dispositivo == "volumen":
        if accion == "subir":
            return "Subiendo volumen del sistema"
        elif accion == "silenciar":
            return "Silenciando audio del sistema"
```

### Simulaciones Creativas

#### 1. **Ventilador Virtual**
- **Encender**: Modifica configuración de energía del CPU
- **Apagar**: Restaura configuración de ahorro de energía

#### 2. **Televisor Virtual**
- **Encender**: Abre QuickTime Player como "pantalla"
- **Apagar**: Cierra la aplicación

#### 3. **Calefactor Virtual**
- **Encender**: Abre Activity Monitor (simula "calor" del CPU)
- **Apagar**: Cierra Activity Monitor

---

## �🎯 Introducción y Arquitectura

### Descripción General
VOICE IOT COMPILER es un **compilador de dominio específico (DSL)** para comandos de voz en español que controla dispositivos IoT (Internet de las Cosas). El sistema implementa un pipeline completo de procesamiento de lenguaje natural siguiendo los principios clásicos de la teoría de compiladores.

### Objetivo Académico
Este proyecto demuestra la aplicación práctica de:
- **Teoría de Compiladores**: Análisis léxico, sintáctico y semántico
- **Procesamiento de Lenguaje Natural**: Reconocimiento de voz y tokenización
- **Arquitectura de Software**: Patrón de pipeline y separación de responsabilidades
- **Accesibilidad**: Interfaz inclusiva con pictogramas y retroalimentación de voz

### Arquitectura del Sistema
```
┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐
│  Entrada de Voz │ -> │   Tokenización   │ -> │  Análisis Parser  │
│  (Audio Input)  │    │    (Lexer)       │    │   (Sintáctico)    │
└─────────────────┘    └──────────────────┘    └───────────────────┘
                                                          │
┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐
│   Ejecución     │ <- │  Generación DSL  │ <- │   Validación      │
│   (Executor)    │    │   (Generator)    │    │   (Semántico)     │
└─────────────────┘    └──────────────────┘    └───────────────────┘
```

---

## 🔄 Pipeline de Procesamiento

### Fases del Compilador

El sistema procesa comandos de voz siguiendo **6 fases principales**:

1. **Reconocimiento de Voz** → Convierte audio a texto
2. **Análisis Léxico** → Tokeniza el texto en elementos semánticos
3. **Análisis Sintáctico** → Valida la estructura gramatical
4. **Análisis Semántico** → Verifica compatibilidad y contexto
5. **Generación de Código** → Produce un DSL estructurado
6. **Ejecución** → Realiza la acción en el dispositivo

### Ejemplo de Procesamiento Completo

**Entrada de Usuario**: *"Enciende la luz en la cocina"*

```
FASE 1 - RECONOCIMIENTO DE VOZ:
Audio → "enciende la luz en la cocina"

FASE 2 - ANÁLISIS LÉXICO:
Texto → [("ENCENDER", "enciende"), ("LUZ", "luz"), ("EN", "en"), ("COCINA", "cocina")]

FASE 3 - ANÁLISIS SINTÁCTICO:
Estructura → ACCION + DISPOSITIVO + PREPOSICION + HABITACION ✅

FASE 4 - ANÁLISIS SEMÁNTICO:
Validación → (ENCENDER, LUZ, COCINA, None) ✅

FASE 5 - GENERACIÓN DSL:
Código → "encender_luz_en_cocina"

FASE 6 - EJECUCIÓN:
Acción → Simular encendido de luz en cocina + Actualizar estado
```

---

## 🔤 Análisis Léxico (Tokenización)

### Archivo: `lexer/tokenizer.py`

### Función Principal
El **TokenizerIoT** convierte texto en español a tokens categorizados que el compilador puede procesar.

### Categorías de Tokens

#### 1. **ACCIONES**
```python
ACCIONES = {
    "encender": "ENCENDER", "enciende": "ENCENDER", "prende": "ENCENDER",
    "apagar": "APAGAR", "apaga": "APAGAR",
    "subir": "SUBIR", "sube": "SUBIR", "aumentar": "SUBIR",
    "bajar": "BAJAR", "baja": "BAJAR", "disminuir": "BAJAR",
    "ajustar": "AJUSTAR", "ajusta": "AJUSTAR", "poner": "AJUSTAR",
    "silenciar": "SILENCIAR", "silencia": "SILENCIAR", "mutear": "SILENCIAR",
    "activar": "ACTIVAR", "activa": "ACTIVAR",
    "ver": "VER", "mostrar": "VER", "dime": "VER", "decir": "VER"
}
```

#### 2. **DISPOSITIVOS**
```python
DISPOSITIVOS = {
    "luz": "LUZ", "luces": "LUZ", "lampara": "LUZ",
    "ventilador": "VENTILADOR", "abanico": "VENTILADOR",
    "televisor": "TELEVISOR", "television": "TELEVISOR", "tv": "TELEVISOR",
    "calefactor": "CALEFACTOR", "calefaccion": "CALEFACTOR",
    "volumen": "VOLUMEN", "audio": "VOLUMEN", "sonido": "VOLUMEN",
    "brillo": "BRILLO", "luminosidad": "BRILLO"
}
```

#### 3. **HABITACIONES**
```python
HABITACIONES = {
    "cocina": "COCINA", "dormitorio": "DORMITORIO", "cuarto": "DORMITORIO",
    "sala": "SALA", "living": "SALA", "salon": "SALA",
    "baño": "BAÑO", "bano": "BAÑO", "lavabo": "BAÑO",
    "oficina": "OFICINA", "estudio": "OFICINA", "despacho": "OFICINA"
}
```

#### 4. **CONSULTAS ESPECIALES**
```python
CONSULTAS = {
    "bateria": "BATERIA", "batería": "BATERIA", "pila": "BATERIA",
    "hora": "HORA", "tiempo": "HORA", "reloj": "HORA"
}
```

### Proceso de Tokenización

```python
def tokenizar(comando: str) -> List[Tuple[str, Any]]:
    # 1. Normalización (quitar acentos, convertir a minúsculas)
    comando_normalizado = normalizar_texto(comando)
    
    # 2. División en palabras
    palabras = comando_normalizado.split()
    
    # 3. Clasificación de cada palabra
    tokens = []
    for palabra in palabras:
        tipo_token, valor_token = tokenizar_palabra(palabra)
        tokens.append((tipo_token, valor_token))
    
    # 4. Filtrado de tokens irrelevantes
    tokens_filtrados = [
        (tipo, valor) for tipo, valor in tokens 
        if tipo not in ["DESCONOCIDO", "LA", "EL"]
    ]
    
    return tokens_filtrados
```

### Normalización de Texto
```python
def normalizar_texto(self, texto: str) -> str:
    acentos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n'  # Manejo especial del español
    }
    
    texto_normalizado = texto.lower().strip()
    for con_acento, sin_acento in acentos.items():
        texto_normalizado = texto_normalizado.replace(con_acento, sin_acento)
    
    return texto_normalizado
```

---

## 🧠 Análisis Sintáctico (Parser)

### Archivo: `parser/parser.py`

### Gramática del Lenguaje IoT

El parser implementa una **gramática libre de contexto** para comandos IoT:

```
COMANDO ::= CONSULTA | ACCION_SIMPLE | ACCION_CON_VALOR

CONSULTA ::= "VER" ("BATERIA" | "HORA")

ACCION_SIMPLE ::= ACCION DISPOSITIVO [UBICACION]
    where ACCION ∈ {ENCENDER, APAGAR, SUBIR, BAJAR, SILENCIAR, ACTIVAR}
    and DISPOSITIVO ∈ {LUZ, VENTILADOR, TELEVISOR, CALEFACTOR, VOLUMEN, BRILLO}

ACCION_CON_VALOR ::= "AJUSTAR" DISPOSITIVO ["A" NUMERO] [UBICACION]

UBICACION ::= "EN" HABITACION
    where HABITACION ∈ {COCINA, DORMITORIO, SALA, BAÑO, OFICINA}
```

### Implementación del Parser

#### 1. **Parser de Consultas**
```python
def analizar_consulta(self) -> bool:
    # VER (BATERIA|HORA)
    self.consumir("VER")
    token_siguiente = self.token_actual()
    
    if token_siguiente[0] in ["BATERIA", "HORA"]:
        self.avanzar()
        return True
    else:
        raise ExcepcionSintactica(
            f"Después de VER se esperaba BATERIA o HORA, se encontró {token_siguiente[0]}"
        )
```

#### 2. **Parser de Acciones Simples**
```python
def analizar_accion_simple(self) -> bool:
    # ACCION DISPOSITIVO [EN HABITACION]
    
    # Consumir acción
    token_accion = self.token_actual()
    if token_accion[0] in ["ENCENDER", "APAGAR", "SUBIR", "BAJAR", "SILENCIAR", "ACTIVAR"]:
        self.avanzar()
    else:
        raise ExcepcionSintactica(f"Acción no válida: {token_accion[0]}")
    
    # Consumir dispositivo
    token_dispositivo = self.token_actual()
    if token_dispositivo[0] in ["LUZ", "VENTILADOR", "TELEVISOR", "CALEFACTOR", "VOLUMEN", "BRILLO"]:
        self.avanzar()
    else:
        raise ExcepcionSintactica(f"Dispositivo no válido: {token_dispositivo[0]}")
    
    # Opcional: EN HABITACION
    if self.token_actual()[0] == "EN":
        self.avanzar()
        # Validar habitación...
    
    return True
```

#### 3. **Parser de Acciones con Valor**
```python
def analizar_accion_con_valor(self) -> bool:
    # AJUSTAR DISPOSITIVO [A NUMERO] [EN HABITACION]
    
    self.consumir("AJUSTAR")
    
    # Dispositivo compatible con ajuste
    token_dispositivo = self.token_actual()
    if token_dispositivo[0] in ["VOLUMEN", "BRILLO"]:
        self.avanzar()
    else:
        raise ExcepcionSintactica(f"Dispositivo no compatible con AJUSTAR: {token_dispositivo[0]}")
    
    # Opcional: A NUMERO
    if self.token_actual()[0] == "A":
        self.avanzar()
        if self.token_actual()[0] == "NUMERO":
            self.avanzar()
    
    return True
```

### Manejo de Errores Sintácticos

```python
class ExcepcionSintactica(Exception):
    def __init__(self, mensaje: str, posicion: int = -1):
        self.mensaje = mensaje
        self.posicion = posicion
        super().__init__(self.mensaje)
```

---

## 🎯 Análisis Semántico (Validación)

### Archivo: `semantic/validator.py`

### Validaciones Implementadas

El validador semántico verifica que los comandos tengan **sentido en el dominio IoT**:

#### 1. **Compatibilidad Acción-Dispositivo**
```python
compatibilidad = {
    "ENCENDER": {"LUZ", "VENTILADOR", "TELEVISOR", "CALEFACTOR"},
    "APAGAR": {"LUZ", "VENTILADOR", "TELEVISOR", "CALEFACTOR"},
    "SUBIR": {"VOLUMEN", "BRILLO"},
    "BAJAR": {"VOLUMEN", "BRILLO"},
    "AJUSTAR": {"VOLUMEN", "BRILLO"},
    "SILENCIAR": {"VOLUMEN"},
    "ACTIVAR": {"VOLUMEN"},
    "VER": {"BATERIA", "HORA"}
}
```

#### 2. **Validación de Rangos**
```python
rangos_validos = {
    "VOLUMEN": (0, 100),  # Porcentaje de volumen
    "BRILLO": (0, 100)    # Porcentaje de brillo
}

def validar_rango_valor(self, dispositivo: str, valor: Optional[int]) -> None:
    if valor is not None and dispositivo in self.rangos_validos:
        min_val, max_val = self.rangos_validos[dispositivo]
        if not (min_val <= valor <= max_val):
            raise ExcepcionSemantica(
                f"Valor {valor} fuera de rango para {dispositivo}. "
                f"Rango válido: {min_val}-{max_val}"
            )
```

#### 3. **Validación de Contexto**
```python
def validar_transicion_estado(self, dispositivo: str, accion: str) -> None:
    if dispositivo in self.estado_dispositivos:
        estado_actual = self.estado_dispositivos[dispositivo]
        
        # Validar transiciones lógicas
        if dispositivo in ["LUZ", "VENTILADOR", "TELEVISOR", "CALEFACTOR"]:
            if accion == "ENCENDER" and estado_actual.get("encendido", False):
                logger.warning(f"{dispositivo} ya está encendido")
            elif accion == "APAGAR" and not estado_actual.get("encendido", False):
                logger.warning(f"{dispositivo} ya está apagado")
```

### Proceso de Validación Completo

```python
def validar(self, tokens: List[Tuple[str, Any]]) -> Tuple[str, str, Optional[str], Optional[int]]:
    # 1. Extraer elementos semánticos
    accion, dispositivo, habitacion, valor = self.extraer_elementos(tokens)
    
    # 2. Validaciones obligatorias
    if not dispositivo:
        raise ExcepcionSemantica("No se especificó dispositivo válido")
    if not accion:
        raise ExcepcionSemantica("No se especificó acción válida")
    
    # 3. Validaciones específicas
    self.validar_existencia(dispositivo)
    self.validar_compatibilidad(accion, dispositivo)
    self.validar_habitacion(habitacion)
    self.validar_rango_valor(dispositivo, valor)
    self.validar_transicion_estado(dispositivo, accion)
    
    return accion, dispositivo, habitacion, valor
```

---

## 🧾 Generación de Código DSL

### Archivo: `generator/generator.py`

### Lenguaje de Dominio Específico (DSL)

El generador produce un **DSL estructurado** que representa el comando validado:

#### Plantillas de Código DSL
```python
plantillas = {
    'accion_simple': "{accion}_{dispositivo}",
    'accion_con_ubicacion': "{accion}_{dispositivo}_en_{habitacion}",
    'accion_con_valor': "{accion}_{dispositivo}_{valor}",
    'accion_completa': "{accion}_{dispositivo}_{valor}_en_{habitacion}",
    'consulta': "ver_{dispositivo}"
}
```

#### Ejemplos de Código DSL Generado

| Comando de Voz | Código DSL Generado |
|----------------|---------------------|
| "Enciende la luz" | `encender_luz` |
| "Apaga el ventilador en cocina" | `apagar_ventilador_en_cocina` |
| "Sube el volumen" | `subir_volumen` |
| "Ajusta brillo a 70" | `ajustar_brillo_70` |
| "Ajusta volumen a 50 en sala" | `ajustar_volumen_50_en_sala` |
| "Dime la hora" | `ver_hora` |

### Estructura Completa del DSL

```python
def generate_code(self, elementos_validados) -> Dict[str, Any]:
    accion, dispositivo, habitacion, valor = elementos_validados
    
    # Generar código DSL
    codigo_dsl = plantilla.format(**parametros)
    
    # Estructura completa con metadatos
    comando_completo = {
        'dsl': codigo_dsl,
        'metadatos': {
            'timestamp': datetime.now().isoformat(),
            'id_comando': str(uuid.uuid4())[:8],
            'accion': accion,
            'dispositivo': dispositivo,
            'habitacion': habitacion,
            'valor': valor,
            'version_dsl': '1.0'
        },
        'parametros': {
            'accion': accion,
            'dispositivo': dispositivo,
            'habitacion': habitacion,
            'valor': valor
        }
    }
    
    return comando_completo
```

---

## ⚙️ Ejecutor de Acciones

### Archivo: `executor/executor.py`

### Funcionalidades del Ejecutor

#### 1. **Control Real del Sistema**
- **Volumen**: Integración con PulseAudio (Linux) para control real
- **Brillo**: Control de brillo de pantalla con xrandr
- **Batería**: Lectura real usando psutil
- **Hora**: Obtención de hora del sistema

#### 2. **Simulación de Dispositivos IoT**
```python
estado_dispositivos = {
    "luz": {"encendido": False, "ubicaciones": set()},
    "ventilador": {"encendido": False, "ubicaciones": set()},
    "televisor": {"encendido": False, "ubicaciones": set()},
    "calefactor": {"encendido": False, "ubicaciones": set()},
    "volumen": {"nivel": 50, "silenciado": False},
    "brillo": {"nivel": 70}
}
```

#### 3. **Control de Volumen Real (Linux)**
```python
def controlar_volumen_sistema(self, accion: str, valor: Optional[int] = None) -> bool:
    if self.platform == "Linux" and self.pulseaudio_available:
        if accion == "ajustar" and valor is not None:
            cmd = f"pactl set-sink-volume @DEFAULT_SINK@ {valor}%"
            subprocess.run(cmd, shell=True, check=True)
        elif accion == "subir":
            subprocess.run("pactl set-sink-volume @DEFAULT_SINK@ +10%", shell=True)
        elif accion == "silenciar":
            subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ 1", shell=True)
```

#### 4. **Retroalimentación de Voz**
```python
def speak(self, text: str):
    # Síntesis de voz thread-safe
    def _speak():
        print(f"🔊 TTS: {text}")
        logger.info(f"TTS: {text}")
    
    threading.Thread(target=_speak, daemon=True).start()
```

### Tipos de Ejecución

1. **Consultas de Sistema**: Hora, batería
2. **Control Real**: Volumen, brillo (en sistemas compatibles)
3. **Simulación IoT**: Dispositivos del hogar
4. **Actualización de Estado**: Persistencia del estado de dispositivos

---

## 🖥️ Interfaz Gráfica y Accesibilidad

### Archivo: `interface/gui.py`

### Características de Accesibilidad

#### 1. **Diseño Inclusivo**
- **Alto contraste**: Cumple WCAG 2.1 AA
- **Fuentes accesibles**: Comic Sans MS y Arial para mejor legibilidad
- **Pictogramas descriptivos**: Representación visual de dispositivos
- **Retroalimentación multimodal**: Visual, auditiva y textual

#### 2. **Controles de Accesibilidad**
```python
# Configuración de accesibilidad
self.fonts = {
    'title': ('Comic Sans MS', 22, 'bold'),
    'button': ('Arial', 14, 'bold'),
    'label': ('Arial', 12)
}

self.colors = {
    'primary_bg': '#fce4ec',      # Rosa muy claro
    'secondary_bg': '#e1f5fe',    # Azul muy claro
    'accent_blue': '#42a5f5',     # Azul accesible
    'text_primary': '#880e4f',    # Alto contraste
}
```

#### 3. **Atajos de Teclado**
- **Barra espaciadora**: Activar reconocimiento de voz
- **F1**: Mostrar ayuda
- **Esc**: Cerrar aplicación

#### 4. **Pictogramas con Texto Alternativo**
```python
# Carga de imágenes con descripción accesible
devices_info = {
    "luz": "Bombilla encendida representando control de iluminación",
    "ventilador": "Ventilador girando para control de ventilación",
    "televisor": "Pantalla de televisor para control de entretenimiento",
    # ...
}
```

### Componentes de la Interfaz

1. **Área de Control Principal**: Botón de micrófono grande y accesible
2. **Zona de Pictogramas**: Retroalimentación visual del dispositivo activo
3. **Panel de Estado**: Información en tiempo real del sistema
4. **Área de Estadísticas**: Monitoreo de uso y rendimiento

---

## 🔄 Flujo de Trabajo Completo

### Diagrama de Secuencia

```
Usuario -> GUI: Presiona botón micrófono
GUI -> Speech: reconocer_comando_voz()
Speech -> GUI: "enciende la luz en cocina"
GUI -> Main: procesar_comando()
Main -> Lexer: tokenizar()
Lexer -> Main: [("ENCENDER", "enciende"), ("LUZ", "luz"), ("EN", "en"), ("COCINA", "cocina")]
Main -> Parser: analizar()
Parser -> Main: True (sintaxis válida)
Main -> Semantic: validar()
Semantic -> Main: ("ENCENDER", "LUZ", "COCINA", None)
Main -> Generator: generate_code()
Generator -> Main: "encender_luz_en_cocina"
Main -> Executor: execute()
Executor -> Sistema: Simular acción
Executor -> Main: Éxito
Main -> GUI: Actualizar pictograma
GUI -> Usuario: Mostrar luz encendida
```

### Manejo de Errores

Cada fase puede generar errores específicos que se propagan hacia arriba:

```python
try:
    # Análisis léxico
    tokens = tokenizar(comando)
    
    # Análisis sintáctico
    analizar(tokens)
    
    # Análisis semántico
    accion, dispositivo, ubicacion, valor = validar(tokens)
    
    # Generación y ejecución
    codigo = generate_code((accion, dispositivo, ubicacion, valor))
    execute(accion, dispositivo, ubicacion, valor)
    
except ExcepcionSintactica as e:
    print(f"❌ Error de sintaxis: {e}")
except ExcepcionSemantica as e:
    print(f"❌ Error semántico: {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
```

---

## 📝 Tipos de Comandos Soportados

### 1. **Comandos de Control de Dispositivos**

#### Encender/Apagar
- `"enciende la luz"`
- `"apaga el ventilador"`
- `"prende el televisor en sala"`
- `"apaga el calefactor en dormitorio"`

#### Dispositivos compatibles:
- **Luz**: `luz`, `luces`, `lampara`
- **Ventilador**: `ventilador`, `abanico`
- **Televisor**: `televisor`, `television`, `tv`, `tele`
- **Calefactor**: `calefactor`, `calefaccion`, `calentador`

### 2. **Comandos de Ajuste de Parámetros**

#### Volumen
- `"sube volumen"` (aumenta 10%)
- `"baja volumen"` (disminuye 10%)
- `"ajusta volumen a 70"` (nivel específico)
- `"silencia volumen"`
- `"activa volumen"`

#### Brillo
- `"sube brillo"`
- `"baja brillo"`
- `"ajusta brillo a 40"`

### 3. **Comandos de Consulta**

#### Información del Sistema
- `"dime la hora"`
- `"ver batería"`
- `"mostrar hora"`
- `"ver bateria"`

### 4. **Especificación de Ubicación**

Todos los dispositivos pueden especificar habitación:
- `"enciende la luz en cocina"`
- `"apaga ventilador en dormitorio"`
- `"prende televisor en sala"`

#### Habitaciones soportadas:
- **Cocina**: `cocina`
- **Dormitorio**: `dormitorio`, `cuarto`, `habitacion`, `recamara`
- **Sala**: `sala`, `living`, `salon`
- **Baño**: `baño`, `bano`, `lavabo`
- **Oficina**: `oficina`, `estudio`, `despacho`

### 5. **Variaciones de Lenguaje Natural**

El sistema reconoce múltiples formas de expresar el mismo comando:
- **Encender**: `enciende`, `prende`, `encender`, `prender`
- **Apagar**: `apaga`, `apagar`
- **Ver**: `ver`, `mostrar`, `dime`, `decir`
- **Ajustar**: `ajusta`, `poner`, `configura`

---

## 🏗️ Arquitectura del Software

### Patrón de Diseño: Pipeline

```
Input -> Stage1 -> Stage2 -> Stage3 -> Stage4 -> Stage5 -> Output
Audio    Lexer    Parser   Semantic  Generator  Executor   Action
```

### Principios Aplicados

1. **Separación de Responsabilidades**: Cada módulo tiene una función específica
2. **Manejo de Errores**: Propagación controlada de excepciones
3. **Extensibilidad**: Fácil agregar nuevos dispositivos o comandos
4. **Reutilización**: Componentes modulares independientes
5. **Thread Safety**: Manejo seguro de concurrencia en GUI

### Estructura de Archivos

```
VOICE_IOT_COMPILER_/
├── main.py                     # Punto de entrada y orquestación
├── lexer/
│   ├── tokenizer.py           # Análisis léxico
├── parser/
│   ├── parser.py              # Análisis sintáctico
├── semantic/
│   ├── validator.py           # Análisis semántico
├── generator/
│   ├── generator.py           # Generación DSL
├── executor/
│   ├── executor.py            # Ejecución de acciones
├── speech/
│   ├── recognizer.py          # Reconocimiento de voz
├── interface/
│   ├── gui.py                 # Interfaz gráfica
│   ├── state_manager.py       # Gestión de estado
├── img/                       # Pictogramas accesibles
└── logs/                      # Archivos de log
```

### Dependencias Tecnológicas

```python
# Reconocimiento de voz
import speech_recognition as sr

# Síntesis de voz
import pyttsx3

# Interfaz gráfica
import tkinter as tk
from PIL import Image, ImageTk

# Control del sistema
import psutil
import subprocess

# Procesamiento
import re
import json
import logging
from typing import List, Tuple, Dict, Any, Optional
```

---

## 📊 Métricas y Estadísticas

### Sistema de Monitoreo

El sistema incluye métricas detalladas de rendimiento:

```python
# Estadísticas por módulo
stats = {
    'tokenizer': {
        'tokens_procesados': 0,
        'tokens_desconocidos': 0,
        'comandos_tokenizados': 0
    },
    'parser': {
        'comandos_analizados': 0,
        'errores_sintacticos': 0,
        'comandos_validos': 0
    },
    'validator': {
        'comandos_validados': 0,
        'errores_semanticos': 0,
        'validaciones_exitosas': 0
    },
    'executor': {
        'acciones_ejecutadas': 0,
        'comandos_reales': 0,
        'comandos_simulados': 0,
        'errores_ejecucion': 0
    }
}
```

---

## 🎓 Conclusiones

### Logros Académicos

1. **Implementación Completa de Compilador**: El proyecto demuestra todos los componentes de un compilador moderno aplicado a un dominio específico.

2. **Aplicación Práctica de Teoría**: Conexión directa entre conceptos teóricos de compiladores y una aplicación real funcionando.

3. **Accesibilidad e Inclusión**: Diseño que considera usuarios con diferentes capacidades, cumpliendo estándares internacionales.

4. **Integración de Tecnologías**: Combinación exitosa de NLP, síntesis de voz, interfaces gráficas y control de sistema.

### Fortalezas Técnicas

- **Robustez**: Manejo comprehensivo de errores en todas las fases
- **Extensibilidad**: Arquitectura modular permite agregar fácilmente nuevos dispositivos
- **Usabilidad**: Interfaz intuitiva con retroalimentación multimodal
- **Rendimiento**: Procesamiento eficiente de comandos en tiempo real

### Innovaciones Implementadas

1. **DSL para IoT**: Lenguaje específico optimizado para comandos de domótica
2. **Pipeline Semántico**: Validación contextual avanzada para IoT
3. **Interfaz Accesible**: Cumplimiento de estándares WCAG 2.1
4. **Control Real**: Integración efectiva con APIs del sistema operativo

### Impacto y Aplicaciones

El proyecto tiene aplicaciones directas en:
- **Domótica accesible**: Control de hogares inteligentes para personas con discapacidades
- **Educación**: Herramienta didáctica para enseñar compiladores
- **Investigación**: Base para desarrollos avanzados en NLP e IoT
- **Industria**: Prototipo para sistemas de control por voz empresariales

### Trabajo Futuro

- **Machine Learning**: Integración de modelos de NLP más avanzados
- **IoT Real**: Conectividad con dispositivos físicos (Zigbee, WiFi, Bluetooth)
- **Múltiples Idiomas**: Soporte para otros idiomas además del español
- **Análisis Predictivo**: Aprendizaje de patrones de uso del usuario

---

## 📚 Referencias Técnicas

- **Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D.** (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley.
- **Bird, S., Klein, E., & Loper, E.** (2009). *Natural Language Processing with Python*. O'Reilly Media.
- **W3C Web Accessibility Initiative.** (2018). *Web Content Accessibility Guidelines (WCAG) 2.1*. https://www.w3.org/WAI/WCAG21/

---

*Desarrollado como proyecto académico para la Universidad Nacional de San Agustín de Arequipa*  
*Curso: Compiladores - Facultad de Ingeniería de Sistemas*  
*Año: 2025*
