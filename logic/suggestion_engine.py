import json
import os

class SuggestionEngine:
    def __init__(self):
        self.suggestion_rules = self._load_suggestion_rules()
        self.translations = self._load_translations()  # NUEVO
    
    def _load_translations(self):
        """Carga las traducciones desde el archivo JSON"""
        try:
            translations_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'translations.json')
            with open(translations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Archivo de traducciones no encontrado")
            return {}
        except json.JSONDecodeError:
            print("Error al decodificar el archivo de traducciones")
            return {}
    
    def get_translation(self, category, item_key, language='es'):
        """Obtiene la traducción de un elemento específico"""
        try:
            return self.translations[language][category][item_key]
        except KeyError:
            return None  # Si no hay traducción, devolver None
    
    def get_translations_for_category(self, category, language='es'):
        """Obtiene todas las traducciones para una categoría"""
        try:
            return self.translations[language].get(category, {})
        except KeyError:
            return {}
    
    def _load_suggestion_rules(self):
        """Carga las reglas de sugerencias desde el archivo JSON"""
        try:
            # Obtener la ruta del archivo JSON
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path = os.path.join(current_dir, 'data', 'suggestion_rules.json')
            
            # Cargar el archivo JSON
            with open(json_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Archivo de reglas de sugerencias no encontrado: {json_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            return {}
        except Exception as e:
            print(f"Error al cargar reglas de sugerencias: {e}")
            return {}
        
    def get_suggestions(self, trigger_category, trigger_value):
        """Obtiene sugerencias basadas en una categoría y valor específicos"""
        suggestions = {}
        
        # Buscar en las reglas de sugerencias
        if trigger_category in self.suggestion_rules:
            category_rules = self.suggestion_rules[trigger_category]
            
            # Buscar coincidencias exactas o parciales
            for rule_value, related_suggestions in category_rules.items():
                if rule_value.lower() in trigger_value.lower() or trigger_value.lower() in rule_value.lower():
                    for related_category, values in related_suggestions.items():
                        if related_category not in suggestions:
                            suggestions[related_category] = []
                        suggestions[related_category].extend(values)
        
        # NUEVA LÓGICA: Relaciones especiales para subcategorías de vestuario
        if trigger_category.startswith('vestuario_'):
            # Si seleccionamos algo de vestuario_general, sugerir para todas las subcategorías
            if trigger_category == 'vestuario_general':
                self._add_vestuario_suggestions(suggestions, 'vestuario_superior', trigger_value)
                self._add_vestuario_suggestions(suggestions, 'vestuario_inferior', trigger_value)
                self._add_vestuario_suggestions(suggestions, 'vestuario_accesorios', trigger_value)
                self._add_vestuario_suggestions(suggestions, 'ropa_interior_superior', trigger_value)
                self._add_vestuario_suggestions(suggestions, 'ropa_interior_inferior', trigger_value)
            
            # Si seleccionamos algo de vestuario_superior, sugerir para vestuario_inferior
            elif trigger_category == 'vestuario_superior':
                self._add_vestuario_suggestions(suggestions, 'vestuario_inferior', trigger_value)
                self._add_vestuario_suggestions(suggestions, 'vestuario_accesorios', trigger_value)
            
            # Si seleccionamos algo de vestuario_inferior, sugerir para vestuario_superior
            elif trigger_category == 'vestuario_inferior':
                self._add_vestuario_suggestions(suggestions, 'vestuario_superior', trigger_value)
                self._add_vestuario_suggestions(suggestions, 'vestuario_accesorios', trigger_value)
                        
        # Remover duplicados
        for category in suggestions:
            suggestions[category] = list(set(suggestions[category]))
            
        return suggestions
    
    def _add_vestuario_suggestions(self, suggestions, target_category, trigger_value):
        """Añade sugerencias específicas de vestuario basadas en estilo y coherencia"""
        # Mapeo de estilos
        style_mapping = {
            'casual': ['t-shirt', 'jeans', 'sneakers', 'casual'],
            'formal': ['blouse', 'dress pants', 'heels', 'elegant'],
            'edgy': ['leather', 'boots', 'dark', 'rock'],
            'summer': ['light', 'sandals', 'fresh', 'outdoor']
        }
        
        # Detectar estilo del trigger_value
        detected_style = None
        for style, keywords in style_mapping.items():
            if any(keyword in trigger_value.lower() for keyword in keywords):
                detected_style = style
                break
        
        # Añadir sugerencias basadas en el estilo detectado
        if detected_style and detected_style in self.suggestion_rules.get('estilo_coordinado', {}):
            style_suggestions = self.suggestion_rules['estilo_coordinado'][detected_style + '_style']
            if target_category in style_suggestions:
                if target_category not in suggestions:
                    suggestions[target_category] = []
                suggestions[target_category].extend(style_suggestions[target_category])
        
        # Remover duplicados
        for category in suggestions:
            suggestions[category] = list(set(suggestions[category]))
            
        return suggestions

    def get_combinations(self, category, value):
        """Obtiene combinaciones específicas para una prenda"""
        combinations = {}
        
        print(f"Buscando combinaciones para: {category} - {value}")  # Debug
        
        # Buscar en las reglas de combinaciones
        if 'combinaciones_vestuario' in self.suggestion_rules:
            # Normalizar el valor para buscar
            # Línea 193 - Cambiar de:
            search_key = value.lower().replace(' ', '_')
            
            # A:
            search_key = value.lower().replace(' ', '_').replace('-', '_')
            combo_rules = self.suggestion_rules['combinaciones_vestuario']
            
            print(f"Buscando clave: {search_key}")  # Debug
            print(f"Claves disponibles: {list(combo_rules.keys())}")  # Debug
            
            if search_key in combo_rules:
                combo_data = combo_rules[search_key]
                
                print(f"Datos de combinación encontrados: {combo_data}")  # Debug
                
                # Obtener combinaciones compatibles
                for combo_type, items in combo_data.items():
                    if combo_type.startswith('compatible_') and isinstance(items, list):
                        # Mapear los tipos de combinación a categorías
                        if combo_type == 'compatible_superior':
                            combinations['vestuario_superior'] = items
                        elif combo_type == 'compatible_inferior':
                            combinations['vestuario_inferior'] = items
                        elif combo_type == 'compatible_accessories':
                            combinations['vestuario_accesorios'] = items
                        elif combo_type == 'compatible_accesorios':
                            combinations['vestuario_accesorios'] = items
                        
        print(f"Combinaciones finales: {combinations}")  # Debug
        return combinations
    
    def get_combinations_only(self, category, value):
        """Obtiene SOLO combinaciones (vestuario) sin accesorios"""
        combinations = {}
        
        if 'combinaciones_vestuario' in self.suggestion_rules:
            search_key = value.lower().replace(' ', '_')
            combo_rules = self.suggestion_rules['combinaciones_vestuario']
            
            if search_key in combo_rules:
                combo_data = combo_rules[search_key]
                
                # Solo obtener combinaciones de vestuario, NO accesorios
                for combo_type, items in combo_data.items():
                    if combo_type.startswith('compatible_') and isinstance(items, list):
                        if combo_type == 'compatible_superior':
                            combinations['vestuario_superior'] = items
                        elif combo_type == 'compatible_inferior':
                            combinations['vestuario_inferior'] = items
                        # NO incluir compatible_accessories aquí
                        
        return combinations
    
    def get_accessories_only(self, category, value):
        """Obtiene SOLO accesorios para una prenda específica"""
        accessories = {}
        
        if 'combinaciones_vestuario' in self.suggestion_rules:
            search_key = value.lower().replace(' ', '_')
            combo_rules = self.suggestion_rules['combinaciones_vestuario']
            
            if search_key in combo_rules:
                combo_data = combo_rules[search_key]
                
                # Solo obtener accesorios
                for combo_type, items in combo_data.items():
                    if combo_type in ['compatible_accessories', 'compatible_accesorios'] and isinstance(items, list):
                        accessories['vestuario_accesorios'] = items
                        
        return accessories
    
    def get_translations(self, category, value):
        """Obtiene las traducciones para una prenda específica"""
        translations = {}
        
        if 'combinaciones_vestuario' in self.suggestion_rules:
            search_key = value.lower().replace(' ', '_')
            combo_rules = self.suggestion_rules['combinaciones_vestuario']
            
            if search_key in combo_rules:
                combo_data = combo_rules[search_key]
                
                # Obtener traducciones si existen
                if 'translations' in combo_data and isinstance(combo_data['translations'], dict):
                    translations = combo_data['translations']
                        
        return translations
        