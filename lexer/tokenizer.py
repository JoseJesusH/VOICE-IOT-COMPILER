# ============================================================================
# lexer/tokenizer.py - Versión mejorada
# ============================================================================

import re
import json
import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class TokenizerIoT:
    def __init__(self):
        # Definir categorías de tokens
        self.ACCIONES = {
            "encender": "ENCENDER",
            "enciende": "ENCENDER", 
            "prende": "ENCENDER",
            "prender": "ENCENDER",
            "apagar": "APAGAR",
            "apaga": "APAGAR",
            "subir": "SUBIR",
            "sube": "SUBIR",
            "aumentar": "SUBIR",
            "bajar": "BAJAR",
            "baja": "BAJAR",
            "disminuir": "BAJAR",
            "ajustar": "AJUSTAR",
            "ajusta": "AJUSTAR",
            "poner": "AJUSTAR",
            "silenciar": "SILENCIAR",
            "silencia": "SILENCIAR",
            "mutear": "SILENCIAR",
            "activar": "ACTIVAR",
            "activa": "ACTIVAR",
            "ver": "VER",
            "mostrar": "VER",
            "dime": "VER",
            "decir": "VER"
        }
        
        self.DISPOSITIVOS = {
            "luz": "LUZ",
            "luces": "LUZ",
            "lampara": "LUZ",
            "lamparas": "LUZ",
            "ventilador": "VENTILADOR",
            "abanico": "VENTILADOR",
            "televisor": "TELEVISOR",
            "television": "TELEVISOR",
            "tv": "TELEVISOR",
            "tele": "TELEVISOR",
            "calefactor": "CALEFACTOR",
            "calefaccion": "CALEFACTOR",
            "calentador": "CALEFACTOR",
            "volumen": "VOLUMEN",
            "audio": "VOLUMEN",
            "sonido": "VOLUMEN",
            "brillo": "BRILLO",
            "luminosidad": "BRILLO"
        }
        
        self.HABITACIONES = {
            "cocina": "COCINA",
            "dormitorio": "DORMITORIO",
            "cuarto": "DORMITORIO",
            "habitacion": "DORMITORIO",
            "recamara": "DORMITORIO",
            "sala": "SALA",
            "living": "SALA",
            "salon": "SALA",
            "baño": "BAÑO",
            "bano": "BAÑO",
            "lavabo": "BAÑO",
            "oficina": "OFICINA",
            "estudio": "OFICINA",
            "despacho": "OFICINA"
        }
        
        self.CONSULTAS = {
            "bateria": "BATERIA",
            "batería": "BATERIA",
            "pila": "BATERIA",
            "energia": "BATERIA",
            "hora": "HORA",
            "tiempo": "HORA",
            "reloj": "HORA"
        }
        
        self.PREPOSICIONES = {
            "en": "EN",
            "a": "A",
            "de": "DE",
            "del": "DEL",
            "la": "LA",
            "el": "EL"
        }
        
        # Compilar expresión regular para números
        self.numero_pattern = re.compile(r'\b\d+\b')
        
        # Estadísticas
        self.stats = {
            'tokens_procesados': 0,
            'tokens_desconocidos': 0,
            'comandos_tokenizados': 0
        }
    
    def normalizar_texto(self, texto: str) -> str:
        """Normalizar texto eliminando acentos y caracteres especiales"""
        # Mapeo de caracteres con acento a sin acento
        acentos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
        
        texto_normalizado = texto.lower().strip()
        for con_acento, sin_acento in acentos.items():
            texto_normalizado = texto_normalizado.replace(con_acento, sin_acento)
        
        return texto_normalizado
    
    def extraer_numeros(self, texto: str) -> List[Tuple[int, str]]:
        """Extraer números del texto con sus posiciones"""
        numeros = []
        for match in self.numero_pattern.finditer(texto):
            numeros.append((match.start(), match.group()))
        return numeros
    
    def tokenizar_palabra(self, palabra: str) -> Tuple[str, str]:
        """Tokenizar una palabra individual"""
        palabra_norm = self.normalizar_texto(palabra)
        
        # Verificar en orden de prioridad
        if palabra_norm in self.ACCIONES:
            return (self.ACCIONES[palabra_norm], palabra_norm)
        elif palabra_norm in self.DISPOSITIVOS:
            return (self.DISPOSITIVOS[palabra_norm], palabra_norm)
        elif palabra_norm in self.HABITACIONES:
            return (self.HABITACIONES[palabra_norm], palabra_norm)
        elif palabra_norm in self.CONSULTAS:
            return (self.CONSULTAS[palabra_norm], palabra_norm)
        elif palabra_norm in self.PREPOSICIONES:
            return (self.PREPOSICIONES[palabra_norm], palabra_norm)
        elif palabra_norm.isdigit():
            return ("NUMERO", int(palabra_norm))
        else:
            self.stats['tokens_desconocidos'] += 1
            return ("DESCONOCIDO", palabra_norm)
    
    def tokenizar(self, comando: str) -> List[Tuple[str, Any]]:
        """Tokenizar comando completo"""
        if not comando or not comando.strip():
            return []
        
        self.stats['comandos_tokenizados'] += 1
        tokens = []
        
        # Normalizar y dividir en palabras
        comando_normalizado = self.normalizar_texto(comando)
        palabras = comando_normalizado.split()
        
        logger.info(f"Tokenizando: '{comando}' -> '{comando_normalizado}'")
        
        for palabra in palabras:
            if palabra:  # Evitar palabras vacías
                tipo_token, valor_token = self.tokenizar_palabra(palabra)
                tokens.append((tipo_token, valor_token))
                self.stats['tokens_procesados'] += 1
                logger.debug(f"Token: {tipo_token} = {valor_token}")
        
        # Filtrar tokens irrelevantes para el análisis
        tokens_filtrados = [
            (tipo, valor) for tipo, valor in tokens 
            if tipo not in ["DESCONOCIDO", "LA", "EL"]
        ]
        
        logger.info(f"Tokens generados: {len(tokens_filtrados)}")
        return tokens_filtrados
    
    def get_stats(self) -> Dict[str, int]:
        """Obtener estadísticas del tokenizador"""
        return self.stats.copy()

# Instancia global del tokenizador
_tokenizer_instance = None

def tokenizar(comando: str) -> List[Tuple[str, Any]]:
    """Función principal de tokenización"""
    global _tokenizer_instance
    if _tokenizer_instance is None:
        _tokenizer_instance = TokenizerIoT()
    
    return _tokenizer_instance.tokenizar(comando)