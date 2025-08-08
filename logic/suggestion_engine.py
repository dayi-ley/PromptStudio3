class SuggestionEngine:
    def __init__(self):
        self.suggestion_rules = self._init_suggestion_rules()
        
    def _init_suggestion_rules(self):
        """Inicializa las reglas de sugerencias basadas en relaciones"""
        return {
            'pose_global': {
                'sitting': {
                    'pose_brazos': ['hands on lap', 'hands on knees', 'arms crossed'],
                    'pose_piernas': ['legs crossed', 'legs together', 'feet flat on floor'],
                    'expresion': ['relaxed', 'comfortable', 'casual'],
                    'vestuario_inferior': ['skirt', 'dress', 'comfortable pants']
                },
                'standing': {
                    'pose_brazos': ['arms at sides', 'hands on hips', 'one hand on hip'],
                    'pose_piernas': ['legs slightly apart', 'weight on one leg', 'legs together'],
                    'expresion': ['confident', 'alert', 'ready'],
                    'accion': ['posing', 'waiting', 'looking ahead']
                },
                'lying down': {
                    'pose_brazos': ['arms above head', 'arms at sides', 'one arm under head'],
                    'pose_piernas': ['legs straight', 'legs bent', 'legs crossed'],
                    'expresion': ['relaxed', 'sleepy', 'peaceful'],
                    'accion': ['resting', 'sleeping', 'reading']
                },
                'walking': {
                    'pose_brazos': ['arms swinging', 'hands in pockets', 'carrying bag'],
                    'pose_piernas': ['one foot forward', 'mid-stride', 'dynamic pose'],
                    'expresion': ['focused', 'happy', 'determined'],
                    'accion': ['moving forward', 'going somewhere', 'in motion']
                }
            },
            'vestuario_superior': {
                'school uniform': {
                    'vestuario_inferior': ['pleated skirt', 'school skirt', 'uniform pants'],
                    'accesorios': ['school bag', 'hair ribbon', 'school badge'],
                    'fondo': ['classroom', 'school hallway', 'school yard'],
                    'accion': ['studying', 'walking to class', 'talking with friends']
                },
                'casual shirt': {
                    'vestuario_inferior': ['jeans', 'casual skirt', 'shorts'],
                    'accesorios': ['casual bag', 'simple jewelry', 'sneakers'],
                    'expresion': ['relaxed', 'casual', 'friendly']
                },
                'formal dress': {
                    'accesorios': ['elegant jewelry', 'formal shoes', 'clutch bag'],
                    'expresion': ['elegant', 'sophisticated', 'confident'],
                    'fondo': ['formal setting', 'elegant room', 'event venue']
                }
            },
            'expresion': {
                'smiling': {
                    'ojos': ['bright eyes', 'sparkling eyes', 'happy eyes'],
                    'accion': ['laughing', 'enjoying', 'having fun'],
                    'pose_global': ['relaxed pose', 'open posture']
                },
                'serious': {
                    'ojos': ['focused eyes', 'intense gaze', 'determined eyes'],
                    'pose_brazos': ['crossed arms', 'hands clasped'],
                    'accion': ['concentrating', 'thinking', 'working']
                },
                'surprised': {
                    'ojos': ['wide eyes', 'shocked expression'],
                    'pose_brazos': ['hands to face', 'hands up'],
                    'accion': ['reacting', 'discovering', 'amazed']
                }
            },
            'accion': {
                'reading': {
                    'pose_global': ['sitting', 'lying down'],
                    'pose_brazos': ['holding book', 'hands on book'],
                    'expresion': ['concentrated', 'peaceful', 'absorbed'],
                    'accesorios': ['glasses', 'bookmark']
                },
                'studying': {
                    'pose_global': ['sitting'],
                    'pose_brazos': ['writing', 'holding pen'],
                    'expresion': ['focused', 'concentrated'],
                    'fondo': ['desk', 'library', 'study room'],
                    'accesorios': ['books', 'notebooks', 'pen']
                },
                'dancing': {
                    'pose_global': ['dynamic pose', 'mid-movement'],
                    'pose_brazos': ['arms raised', 'graceful arms'],
                    'expresion': ['joyful', 'energetic', 'passionate'],
                    'vestuario_superior': ['flowing top', 'dance outfit']
                }
            }
        }
        
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
                        
        # Remover duplicados
        for category in suggestions:
            suggestions[category] = list(set(suggestions[category]))
            
        return suggestions