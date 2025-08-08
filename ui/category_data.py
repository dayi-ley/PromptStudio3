import json
import os

class CategoryData:
    """Clase para manejar los datos de categorías (ocultas, deshabilitadas, relaciones)"""
    
    def __init__(self):
        self.hidden_categories = set()
        self.disabled_categories = set()
        self.category_relationships = self._init_category_relationships()
        self.contextual_suggestions = self._init_contextual_suggestions()
        self.load_categories()
    
    def load_categories(self):
        """Carga las categorías ocultas y deshabilitadas desde el archivo de configuración"""
        try:
            config_path = os.path.join('data', 'ui_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.hidden_categories = set(config.get('hidden_categories', []))
                    self.disabled_categories = set(config.get('disabled_categories', []))
        except Exception as e:
            print(f"Error cargando categorías: {e}")
            self.hidden_categories = set()
            self.disabled_categories = set()
    
    def save_categories(self, hidden_categories, disabled_categories):
        """Guarda las categorías ocultas y deshabilitadas en el archivo de configuración"""
        try:
            config_path = os.path.join('data', 'ui_config.json')
            os.makedirs('data', exist_ok=True)
            
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['hidden_categories'] = list(hidden_categories)
            config['disabled_categories'] = list(disabled_categories)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            # Actualizar los sets locales
            self.hidden_categories = hidden_categories.copy()
            self.disabled_categories = disabled_categories.copy()
        except Exception as e:
            print(f"Error guardando categorías: {e}")
    
    def _init_category_relationships(self):
        """Define las relaciones entre categorías"""
        return {
            'creative_writing': ['character_development', 'world_building', 'narrative_structure'],
            'business': ['marketing', 'strategy', 'communication'],
            'technical': ['programming', 'data_analysis', 'system_design'],
            'educational': ['lesson_planning', 'assessment', 'curriculum_design']
        }
    
    def _init_contextual_suggestions(self):
        """Define sugerencias contextuales para combinaciones de categorías"""
        return {
            ('creative_writing', 'character_development'): {
                'suggestions': [
                    'Desarrollar trasfondo del personaje',
                    'Crear arcos de desarrollo',
                    'Definir motivaciones internas'
                ]
            },
            ('business', 'marketing'): {
                'suggestions': [
                    'Estrategia de contenido',
                    'Análisis de audiencia',
                    'Campañas publicitarias'
                ]
            }
        }