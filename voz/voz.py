"""
Módulo principal de voz - versión simplificada
"""

class GestorVoz:
    """Gestor simple del sistema de voz"""
    
    def __init__(self):
        self.activo = False
    
    def procesar_comando_voz(self, callback=None):
        """Procesar un comando de voz"""
        try:
            from speech.recognizer import reconocer_comando_voz
            comando = reconocer_comando_voz()
            
            if comando and callback:
                callback(comando)
                return comando
            
            return None
                
        except Exception as e:
            print(f"Error procesando comando de voz: {e}")
            return None