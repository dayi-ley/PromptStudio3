from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

class SuggestionPanel(QWidget):
    suggestion_applied = pyqtSignal(str, str)  # category, value
    
    def __init__(self, prompt_generator):
        super().__init__()
        self.prompt_generator = prompt_generator
        self.category_relationships = self._init_category_relationships()
        self.contextual_suggestions = self._init_contextual_suggestions()
        self.init_ui()
        
    def _init_category_relationships(self):
        """Define qué categorías se relacionan con cada valor"""
        return {
            'sitting': ['pose_brazos', 'pose_piernas', 'expresion'],
            'standing': ['pose_brazos', 'accion', 'expresion'],
            'lying down': ['pose_brazos', 'expresion', 'accion'],
            'walking': ['pose_brazos', 'pose_piernas', 'accion'],
            'anime style': ['expresion', 'cabello', 'ojos'],
            'realistic': ['iluminacion', 'calidad', 'fondo'],
            'outdoor': ['iluminacion', 'accion'],
            'indoor': ['iluminacion', 'fondo'],
            'smiling': ['ojos', 'accion'],
            'serious': ['pose_global', 'iluminacion']
        }
        
    def _init_contextual_suggestions(self):
        """Define sugerencias contextuales basadas en selecciones previas"""
        return {
            'sitting': {
                'pose_brazos': ['hands on lap', 'arms crossed', 'hands on table', 'relaxed arms'],
                'pose_piernas': ['legs crossed', 'legs together', 'feet on ground', 'ankles crossed'],
                'expresion': ['relaxed', 'focused', 'comfortable', 'contemplative']
            },
            'standing': {
                'pose_brazos': ['arms at sides', 'hands on hips', 'crossed arms', 'hands behind back'],
                'accion': ['looking ahead', 'posing', 'waiting', 'observing'],
                'expresion': ['confident', 'alert', 'ready', 'determined']
            },
            'anime style': {
                'expresion': ['kawaii', 'tsundere', 'cheerful', 'determined', 'shy'],
                'cabello': ['twin tails', 'long flowing hair', 'spiky hair', 'colorful hair'],
                'ojos': ['large eyes', 'sparkling eyes', 'colorful eyes', 'expressive eyes']
            },
            'outdoor': {
                'iluminacion': ['natural sunlight', 'golden hour', 'bright daylight', 'soft shadows'],
                'accion': ['walking', 'exploring', 'enjoying nature', 'breathing fresh air']
            },
            'realistic': {
                'iluminacion': ['studio lighting', 'natural lighting', 'dramatic shadows'],
                'calidad': ['photorealistic', 'high detail', 'professional photography'],
                'fondo': ['detailed background', 'realistic environment']
            }
        }
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 4, 8, 6)
        
        # Título de la sección
        title = QLabel("Sugerencias Inteligentes")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #cccccc; margin-bottom: 4px;")
        layout.addWidget(title)
        
        # Árbol de sugerencias
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setRootIsDecorated(True)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 6px;
                color: #ffffff;
                font-size: 9pt;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #4a4a4a;
            }
            QTreeWidget::item:hover {
                background-color: #4a4a4a;
            }
            QTreeWidget::item:selected {
                background-color: #00cc88;
                color: #ffffff;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
        """)
        
        # Conectar doble click para aplicar sugerencia
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.tree_widget)
        
        # Mensaje inicial
        self.show_initial_message()
        
    def show_initial_message(self):
        """Muestra mensaje inicial cuando no hay sugerencias"""
        self.tree_widget.clear()
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, "💡 Selecciona un valor del autocompletado para ver sugerencias")
        root_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
        root_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.Mid))
        self.tree_widget.expandAll()
        
    def update_suggestions_tree(self, selected_category, selected_value):
        """Actualiza el árbol de sugerencias basado en la selección"""
        self.tree_widget.clear()
        
        # Crear nodo raíz con el valor seleccionado
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, f"🎯 {selected_value} ({selected_category.replace('_', ' ').title()})")
        root_item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
        root_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.BrightText))
        
        # Verificar si hay categorías relacionadas
        if selected_value in self.category_relationships:
            related_categories = self.category_relationships[selected_value]
            
            for related_category in related_categories:
                # Crear nodo de categoría
                category_item = QTreeWidgetItem(root_item)
                category_item.setText(0, f"📁 {related_category.replace('_', ' ').title()}")
                category_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
                category_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.Link))
                
                # Obtener sugerencias para esta categoría
                suggestions = []
                
                # Sugerencias contextuales específicas
                if (selected_value in self.contextual_suggestions and 
                    related_category in self.contextual_suggestions[selected_value]):
                    suggestions.extend(self.contextual_suggestions[selected_value][related_category])
                
                # Sugerencias base de la categoría
                base_suggestions = self.prompt_generator.get_category_options(related_category)
                suggestions.extend(base_suggestions)
                
                # Remover duplicados manteniendo orden
                seen = set()
                unique_suggestions = []
                for suggestion in suggestions:
                    if suggestion not in seen:
                        seen.add(suggestion)
                        unique_suggestions.append(suggestion)
                
                # Crear nodos de sugerencias
                for suggestion in unique_suggestions[:8]:  # Limitar a 8 sugerencias por categoría
                    suggestion_item = QTreeWidgetItem(category_item)
                    suggestion_item.setText(0, f"✨ {suggestion}")
                    suggestion_item.setData(0, Qt.ItemDataRole.UserRole, (related_category, suggestion))
                    suggestion_item.setFont(0, QFont("Segoe UI", 8))
                    
                    # Color diferente para sugerencias contextuales vs base
                    if (selected_value in self.contextual_suggestions and 
                        related_category in self.contextual_suggestions[selected_value] and
                        suggestion in self.contextual_suggestions[selected_value][related_category]):
                        # Verde para sugerencias contextuales
                        suggestion_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.LinkVisited))
                    else:
                        # Color normal para sugerencias base
                        suggestion_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.Text))
        else:
            # No hay categorías relacionadas
            no_suggestions_item = QTreeWidgetItem(root_item)
            no_suggestions_item.setText(0, "ℹ️ No hay categorías relacionadas para este valor")
            no_suggestions_item.setFont(0, QFont("Segoe UI", 8))
            no_suggestions_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.Mid))
        
        # Expandir todo el árbol
        self.tree_widget.expandAll()
        
    def on_item_double_clicked(self, item, column):
        """Maneja el doble click en un item del árbol"""
        # Solo procesar items que tienen datos de sugerencia
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            category, value = data
            # Emitir señal para aplicar la sugerencia
            self.suggestion_applied.emit(category, value)
            
    def clear_suggestions(self):
        """Limpia todas las sugerencias y muestra mensaje inicial"""
        self.show_initial_message()