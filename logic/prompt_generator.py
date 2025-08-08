import json

class PromptGenerator:
    def __init__(self):
        # CATEGORÍAS EXPANDIDAS - SISTEMA COMPLETO
        self.categories = {
            # Personaje
            'edad_aparente': [],
            'etnia': [],
            'complexion': [],
            'altura_relativa': [],
            'piel_detalles': [],
            
            # Cabello y Rostro
            'cabello_forma': [],
            'cabello_color': [],
            'cabello_accesorios': [],
            'rostro_accesorios': [],
            'ojos': [],
            
            # Vestuario
            'vestuario_general': [],
            'vestuario_superior': [],
            'vestuario_inferior': [],
            'vestuario_accesorios': [],
            'ropa_interior_superior': [],
            'ropa_interior_inferior': [],
            'ropa_interior_accesorios': [],
            
            # Poses
            'pose_actitud_global': [],
            'pose_brazos': [],
            'pose_piernas': [],
            'postura_cabeza': [],
            'direccion_mirada_personaje': [],
            
            # Fondo y Atmósfera
            'fondo': [],
            'atmosfera_vibe': [],
            
            # Contenido NSFW
            'nsfw': [],
            
            # Objetos y Accesorios
            'objetos_interaccion': [],
            'objetos_escenario': [],
            'mirada_espectador': [],
            
            # Expresión emocional
            'expresion_facial_ojos': [],
            'expresion_facial_boca': [],
            'expresion_facial_mejillas': [],
            'actitud_emocion': [],
            
            # Estilo y composición
            'angulo': [],
            'composicion': [],
            'calidad_tecnica': [],
            'estilo_artistico': [],
            
            # Loras y AI
            'loras_estilos_artistico': [],
            'loras_detalles_mejoras': [],
            'loras_modelos_especificos': [],
            'loras_personaje': [],
            
            # Interacción y Acción
            'accion_actual': [],
            'uso_de_objeto': [],
            'relacion_con_entorno': [],
            
            # Iluminación y Ambiente
            'tipo_iluminacion': [],
            'color_luz': [],
            'sombras': []
        }
        
        self.category_values = {}
        self.blocked_categories = set()
        self.category_options = self._init_category_options()
        self.categorias_bloqueadas = set()  # Categorías bloqueadas permanentemente
        self.categorias_temporalmente_bloqueadas = set()  # Para conflictos dinámicos
        
        # CORRECCIÓN: Cargar reglas e inicializar atributos
        self.reglas = self._cargar_reglas()
        self.prioridades = self.reglas.get('prioridades', {})
        self.conflictos = self.reglas.get('conflictos', [])
    
    def _init_category_options(self):
        """Inicializa las opciones predefinidas para cada categoría"""
        return {
            # Personaje
            'edad_aparente': ['teen', 'young adult', 'adult', 'mature', 'elderly'],
            'etnia': ['caucasian', 'asian', 'african', 'hispanic', 'middle eastern', 'mixed'],
            'complexion': ['slim', 'athletic', 'curvy', 'muscular', 'petite', 'voluptuous'],
            'altura_relativa': ['short', 'average height', 'tall', 'very tall'],
            'piel_detalles': ['smooth skin', 'freckles', 'tan', 'pale', 'dark skin', 'scars'],
            
            # Cabello y Rostro
            'cabello_forma': ['straight hair', 'wavy hair', 'curly hair', 'braided hair', 'ponytail', 'bun', 'short hair', 'long hair'],
            'cabello_color': ['blonde hair', 'brown hair', 'black hair', 'red hair', 'white hair', 'blue hair', 'pink hair'],
            'cabello_accesorios': ['hair ribbon', 'headband', 'hair clips', 'hair ornament', 'tiara'],
            'rostro_accesorios': ['glasses', 'sunglasses', 'eyepatch', 'face mask', 'earrings'],
            'ojos': ['blue eyes', 'brown eyes', 'green eyes', 'hazel eyes', 'gray eyes', 'purple eyes', 'red eyes'],
            
            # Vestuario
            'vestuario_general': ['casual wear', 'formal wear', 'school uniform', 'swimwear', 'sportswear', 'traditional clothing'],
            'vestuario_superior': ['blouse', 'sweater', 'tank top', 'jacket', 'dress shirt', 'crop top', 't-shirt'],
            'vestuario_inferior': ['skirt', 'pants', 'shorts', 'leggings', 'dress', 'jeans', 'mini skirt'],
            'vestuario_accesorios': ['belt', 'tie', 'scarf', 'gloves', 'socks', 'stockings'],
            'ropa_interior_superior': ['bra', 'sports bra', 'bandeau', 'camisole'],
            'ropa_interior_inferior': ['panties', 'thong', 'boyshorts', 'briefs'],
            'ropa_interior_accesorios': ['garter belt', 'stockings', 'thigh highs'],
            
            # Poses
            'pose_actitud_global': ['standing', 'sitting', 'lying down', 'kneeling', 'crouching', 'walking', 'running'],
            'pose_brazos': ['arms at sides', 'hands on hips', 'crossed arms', 'hands behind back', 'reaching up', 'arms crossed'],
            'pose_piernas': ['legs together', 'legs apart', 'crossed legs', 'one leg raised', 'bent knees'],
            'postura_cabeza': ['head straight', 'head tilted', 'looking up', 'looking down', 'head turned'],
            'direccion_mirada_personaje': ['looking at viewer', 'looking away', 'looking to the side', 'eyes closed'],
            
            # Fondo y Atmósfera
            'fondo': ['simple background', 'outdoor', 'indoor', 'classroom', 'bedroom', 'garden', 'beach', 'city'],
            'atmosfera_vibe': ['peaceful', 'energetic', 'romantic', 'mysterious', 'cheerful', 'melancholic'],
            
            # Contenido NSFW
            'nsfw': ['sfw', 'suggestive', 'nsfw', 'explicit'],
            
            # Objetos y Accesorios
            'objetos_interaccion': ['holding book', 'holding phone', 'holding cup', 'holding flower', 'holding weapon'],
            'objetos_escenario': ['chair', 'table', 'bed', 'tree', 'building', 'car'],
            'mirada_espectador': ['looking at viewer', 'eye contact', 'winking', 'seductive look'],
            
            # Expresión emocional
            'expresion_facial_ojos': ['happy eyes', 'sad eyes', 'angry eyes', 'surprised eyes', 'sleepy eyes'],
            'expresion_facial_boca': ['smiling', 'frowning', 'open mouth', 'closed mouth', 'laughing'],
            'expresion_facial_mejillas': ['blushing', 'normal cheeks', 'puffed cheeks'],
            'actitud_emocion': ['happy', 'sad', 'angry', 'surprised', 'excited', 'calm', 'nervous'],
            
            # Estilo y composición
            'angulo': ['front view', 'side view', 'back view', 'three-quarter view', 'close-up', 'full body'],
            'composicion': ['centered', 'rule of thirds', 'dynamic pose', 'symmetrical'],
            'calidad_tecnica': ['masterpiece', 'best quality', 'high resolution', 'detailed', 'ultra detailed'],
            'estilo_artistico': ['anime style', 'realistic', 'cartoon', 'manga style', 'chibi', 'oil painting'],
            
            # Loras y AI
            'loras_estilos_artistico': ['anime lora', 'realistic lora', 'painting lora'],
            'loras_detalles_mejoras': ['detail lora', 'face lora', 'hand lora'],
            'loras_modelos_especificos': ['character lora', 'celebrity lora'],
            'loras_personaje': ['specific character', 'original character'],
            
            # Interacción y Acción
            'accion_actual': ['reading', 'writing', 'eating', 'drinking', 'sleeping', 'dancing', 'exercising'],
            'uso_de_objeto': ['using phone', 'reading book', 'drinking coffee', 'playing instrument'],
            'relacion_con_entorno': ['interacting with environment', 'isolated', 'part of scene'],
            
            # Iluminación y Ambiente
            'tipo_iluminacion': ['soft lighting', 'dramatic lighting', 'natural lighting', 'studio lighting', 'backlighting'],
            'color_luz': ['warm light', 'cool light', 'golden hour', 'blue hour', 'neon lighting'],
            'sombras': ['soft shadows', 'hard shadows', 'no shadows', 'dramatic shadows']
        }
        
    def get_all_categories(self):
        """Retorna todas las categorías disponibles"""
        return list(self.categories.keys())
        
    def get_category_options(self, category):
        """Retorna las opciones predefinidas para una categoría"""
        return self.category_options.get(category, [])
        
    def set_category_blocked(self, category, blocked):
        """Bloquea o desbloquea una categoría"""
        if blocked:
            self.blocked_categories.add(category)
            # Remover valor si está bloqueada
            if category in self.category_values:
                del self.category_values[category]
        else:
            self.blocked_categories.discard(category)
            
    def set_category_value(self, category, value):
        """Establece el valor de una categoría"""
        if category not in self.blocked_categories:
            self.category_values[category] = value
            
    def get_category_value(self, category):
        """Obtiene el valor de una categoría"""
        return self.category_values.get(category, "")
        
    def _cargar_reglas(self):
        try:
            with open('data/category_rules.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Si no existe el archivo, devolver estructura vacía pero válida
            return {
                'reglas_inferencia': {}, 
                'conflictos': [], 
                'prioridades': {}
            }
    
    def aplicar_inferencias(self, categoria, valor):
        """Aplica reglas cuando se selecciona un valor"""
        reglas_categoria = self.reglas['reglas_inferencia'].get(categoria, {})
        reglas_valor = reglas_categoria.get(valor, {})
        
        sugerencias = {}
        categorias_a_bloquear = reglas_valor.get('_bloquear', [])
        
        # Bloquear categorías conflictivas
        for cat_bloquear in categorias_a_bloquear:
            self.categorias_temporalmente_bloqueadas.add(cat_bloquear)
            if cat_bloquear in self.category_values:
                del self.category_values[cat_bloquear]
        
        # Generar sugerencias para otras categorías
        for cat_relacionada, valores_sugeridos in reglas_valor.items():
            if not cat_relacionada.startswith('_'):  # Ignorar claves especiales
                sugerencias[cat_relacionada] = valores_sugeridos
        
        return sugerencias
    
    def resolver_conflictos(self):
        """Resuelve conflictos basado en prioridades"""
        for conflicto in self.conflictos:
            cat1, cat2 = conflicto
            if cat1 in self.category_values and cat2 in self.category_values:
                prioridad1 = self.prioridades.get(cat1, 0)
                prioridad2 = self.prioridades.get(cat2, 0)
                
                if prioridad1 > prioridad2:
                    del self.category_values[cat2]
                    self.categorias_temporalmente_bloqueadas.add(cat2)
                elif prioridad2 > prioridad1:
                    del self.category_values[cat1]
                    self.categorias_temporalmente_bloqueadas.add(cat1)
    
    def generate_prompt(self):
        """Genera prompt ordenado por prioridades"""
        # Solo resolver conflictos si hay reglas cargadas
        if self.conflictos:
            self.resolver_conflictos()
        
        # Ordenar por prioridad (mayor a menor)
        categorias_ordenadas = sorted(
            self.category_values.keys(),
            key=lambda x: self.prioridades.get(x, 0),
            reverse=True
        )
        
        valores_activos = []
        for categoria in categorias_ordenadas:
            if categoria in self.category_values and self.category_values[categoria]:
                valores_activos.append(self.category_values[categoria])
        
        return ", ".join(valores_activos)
        
    def clear_all(self):
        """Limpia todos los valores"""
        self.category_values.clear()
    
    def bloquear_categoria_permanente(self, categoria):
        """Bloqueo manual del usuario (clic derecho)"""
        self.categorias_bloqueadas.add(categoria)
        if categoria in self.category_values:
            del self.category_values[categoria]
    
    def es_categoria_disponible(self, categoria):
        return categoria not in self.categorias_bloqueadas and categoria not in self.categorias_temporalmente_bloqueadas