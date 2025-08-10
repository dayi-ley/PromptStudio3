from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor
from logic.suggestion_engine import SuggestionEngine

class SuggestionPanel(QWidget):
    suggestion_applied = pyqtSignal(str, str)
    combination_requested = pyqtSignal(str, str)
    prompt_updated = pyqtSignal()  # NUEVA SEÑAL
    
    def __init__(self, prompt_generator, main_window=None):
        super().__init__()
        self.prompt_generator = prompt_generator
        self.main_window = main_window
        self.suggestion_engine = SuggestionEngine()
        
        # Rastrear sugerencias seleccionadas
        self.selected_suggestions = set()
        # Rastrear combinaciones mostradas
        self.current_combinations = {}
        # NUEVO: Sistema de columnas dinámicas
        self.dynamic_columns = []  # Lista de columnas creadas dinámicamente
        self.column_data = []      # Datos de cada columna (para navegación)
        self.max_columns = 4       # Reducido de 5 a 4 (sin estilos)
        
        # NUEVO: Control de estado de columnas (FALTABA ESTA LÍNEA)
        self.column_states = {}  # {column_index: {'collapsed': bool, 'created': bool}}
        
        # NUEVO: Sistema de construcción de prompt contextual
        self.selection_history = []  # Historial de selecciones: [(tipo, categoría, valor, columna_index)]
        self.garment_selections = {}  # {prenda_id: {tipo, categoría, valor, atributos}}
        self.current_garment_id = None  # ID de la prenda actual siendo modificada
        
        self.category_relationships = self._init_category_relationships()
        self.contextual_suggestions = self._init_contextual_suggestions()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(8, 4, 8, 6)
        
        # Título
        title = QLabel("💡 Sugerencias Inteligentes")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #cccccc; margin-bottom: 4px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Layout horizontal para múltiples columnas dinámicas
        self.columns_layout = QHBoxLayout()
        
        # Columna principal de sugerencias (siempre visible)
        self.main_column = self._create_suggestion_column("Sugerencias Principales", 0)
        self.columns_layout.addWidget(self.main_column)
        self.dynamic_columns.append(self.main_column)
        
        layout.addLayout(self.columns_layout)
        
        # Guardar referencia al tree_widget principal para compatibilidad
        self.tree_widget = self.main_column.findChild(QTreeWidget)
        
        self.setLayout(layout)
        
        # Mensaje inicial
        self.show_initial_message()
        
    def _create_suggestion_column(self, title, column_index):
        """Crea una columna de sugerencias con su propio QTreeWidget y botón Siguiente"""
        column_widget = QWidget()
        column_layout = QVBoxLayout(column_widget)
        column_layout.setContentsMargins(4, 0, 4, 0)
        
        # Header con título y botón skip
        header_layout = QHBoxLayout()
        
        # Título de la columna
        column_title = QLabel(title)
        column_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        column_title.setStyleSheet("color: #cccccc; margin-bottom: 4px;")
        header_layout.addWidget(column_title)
        
        # Botón "Skip" pequeño y discreto (solo para columnas que no sean la principal ni la de colores)
        if column_index > 0 and column_index < 3:  # Combinaciones y Accesorios
            skip_button = QPushButton("⏭")
            skip_button.setFixedSize(20, 20)  # Botón muy pequeño
            skip_button.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #cccccc;
                    border: 1px solid #888888;
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #4a90e2;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: #357abd;
                }
            """)
            skip_button.setToolTip("Saltar al siguiente paso")
            skip_button.clicked.connect(lambda: self._toggle_skip_column(column_index))
            header_layout.addWidget(skip_button)
        
        header_layout.addStretch()  # Empujar el botón hacia la derecha
        column_layout.addLayout(header_layout)
        
        # Árbol de sugerencias
        tree_widget = QTreeWidget()
        tree_widget.setHeaderHidden(True)
        tree_widget.setRootIsDecorated(True)
        tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 6px;
                color: #ffffff;
                font-size: 9pt;
                min-width: 200px;
                max-width: 250px;
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
        """)
        
        # Conectar doble click con el índice de columna
        tree_widget.itemDoubleClicked.connect(
            lambda item, col: self.on_item_double_clicked(item, col, column_index)
        )
        
        column_layout.addWidget(tree_widget)
        return column_widget
        
    def _is_same_selection(self, category, value, column_index):
        """Verifica si la selección actual es la misma que la última en esta columna"""
        # Usar un diccionario para rastrear la última selección por columna
        if not hasattr(self, 'last_selections_by_column'):
            self.last_selections_by_column = {}
        
        last_selection = self.last_selections_by_column.get(column_index)
        return (last_selection is not None and 
                last_selection['category'] == category and 
                last_selection['value'] == value)
    
    def on_item_double_clicked(self, item, column, column_index):
        """Maneja el doble clic en un elemento"""
        print(f"DEBUG: on_item_double_clicked llamado con column_index={column_index}")
        print(f"DEBUG: item.parent() = {item.parent()}")
        
        if item.parent():  # Es un elemento hijo
            category = item.parent().text(0)
            value = item.text(0)
            
            # LIMPIAR LOS EMOJIS Y ESPACIOS EXTRA DEL VALOR
            clean_value = value.replace('✨ ', '').replace('🎨 ', '').strip()
            clean_category = category.replace('📁 ', '').replace('👔 ', '').replace('🎯 ', '').strip()
            
            print(f"Selección en columna {column_index}: {clean_category} - {clean_value}")
            
            # Verificar si hay columnas siguientes para alternar expandir/colapsar
            has_next_columns = len(self.dynamic_columns) > column_index + 1

            if self._is_same_selection(clean_category, clean_value, column_index):
                if has_next_columns:
                    print(f"Misma selección detectada en columna {column_index}, colapsando columnas siguientes...")
                    # Colapsar columnas siguientes
                    self._clear_columns_from(column_index + 1)
                    # Limpiar selecciones de columnas posteriores
                    if hasattr(self, 'last_selections_by_column'):
                        keys_to_remove = [k for k in self.last_selections_by_column.keys() if k > column_index]
                        for k in keys_to_remove:
                            del self.last_selections_by_column[k]
                    self._update_prompt()
                    return
                else:
                    print(f"Misma selección detectada en columna {column_index}, expandiendo columna siguiente...")
                    # No hay columnas siguientes, así que expandir (continuar con la lógica normal)
                    pass

            # Guardar esta selección como la última para esta columna
            if not hasattr(self, 'last_selections_by_column'):
                self.last_selections_by_column = {}
            self.last_selections_by_column[column_index] = {
                'category': clean_category,
                'value': clean_value
            }
            
            # Limpiar prompt anterior si es una nueva prenda principal
            if column_index == 0:
                print("Limpiando prompt contextual anterior...")
                self._clear_contextual_prompt()
                self._clear_dynamic_columns()
                print("Prompt contextual limpiado completamente")
            else:
                # Para otras columnas, solo limpiar las columnas posteriores
                self._clear_columns_from(column_index + 1)
            
            # Determinar el tipo de selección
            if column_index == 0:  # Prenda principal
                selection_type = "garment"
            elif column_index == 1:  # Combinación (también es prenda)
                selection_type = "garment"
            elif column_index == 2:  # Accesorio
                selection_type = "accessory"
            else:
                selection_type = "garment"
            
            print(f"DEBUG: Registrando selección tipo {selection_type}")
            # Registrar la selección con valores limpios SOLO si NO es columna de colores
            if column_index != 3:  # No llamar _track_selection para colores
                self._track_selection(column_index, clean_category, clean_value, selection_type)
            
            print(f"DEBUG: Verificando column_index para mostrar siguiente columna: {column_index}")
            # Mostrar siguiente columna si es necesario
            if column_index == 0:  # Columna principal
                print("DEBUG: Mostrando columna de Combinaciones")
                self._show_next_column(column_index + 1, "Combinaciones")
            elif column_index == 1:  # Columna de combinaciones
                print("DEBUG: Mostrando columna de Accesorios")
                self._show_next_column(column_index + 1, "Accesorios")
            elif column_index == 2:  # Columna de accesorios - MOSTRAR COLORES AUTOMÁTICAMENTE
                print(f"DEBUG: ¡DEBERÍA CREAR COLUMNA DE COLORES! Accesorio seleccionado: {clean_value}")
                print(f"Creando columna de colores después de seleccionar accesorio: {clean_value}")
                self._create_color_column_for_all_garments(column_index + 1)
                print("DEBUG: Columna de colores creada")
            elif column_index == 3:  # Columna de colores
                print("DEBUG: Procesando selección de color")
                # Obtener datos del elemento seleccionado
                item_data = item.data(0, Qt.ItemDataRole.UserRole)
                if item_data and len(item_data) > 2:
                    selection_type, color_value, garment_id = item_data
                    # EXTRAER SOLO EL COLOR SIN LA PRENDA
                    if '_' in color_value:
                        clean_color_value = color_value.split('_')[-1]  # Solo el color
                    else:
                        clean_color_value = color_value.replace('🎨 ', '').strip()
                    
                    # CREAR NUEVA ENTRADA EN LUGAR DE MODIFICAR LA EXISTENTE
                    if garment_id in self.garment_selections:
                        original_garment = self.garment_selections[garment_id]
                        
                        # Crear nuevo ID para la prenda con color
                        colored_garment_id = f"{garment_id}_colored_{len(self.garment_selections)}"
                        
                        # Crear nueva entrada con color PERO SIN ATRIBUTO COLOR
                        self.garment_selections[colored_garment_id] = {
                            'base_item': f"{clean_color_value} {original_garment['base_item']}",
                            'category': original_garment['category'],
                            'attributes': {}  # NO agregar el atributo color aquí
                        }
                        
                        print(f"Nueva prenda creada: {colored_garment_id} = {clean_color_value} {original_garment['base_item']}")
                        self._update_prompt()
                    
                    print(f"Color seleccionado: {clean_color_value} para prenda {garment_id}")

            else:
                print(f"DEBUG: column_index {column_index} no manejado")
        else:
            print(f"DEBUG: item.parent() es None, no es un elemento hijo")
            
        print(f"Prompt actual: {self._build_contextual_prompt()}")
    
    def _show_color_column_for_all_garments(self, column_index):
        """Crea columna de colores con opciones para todas las prendas"""
        color_column = self._create_suggestion_column("Colores", column_index)
        tree_widget = color_column.findChild(QTreeWidget)
        
        # Limpiar y crear estructura
        tree_widget.clear()
        
        # Crear nodo raíz
        root_item = QTreeWidgetItem(tree_widget)
        root_item.setText(0, "🎨 Seleccionar Colores")
        root_item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
        root_item.setForeground(0, QColor(70, 130, 180))
        
        # Crear sección para cada prenda seleccionada
        for garment_id, garment_data in self.garment_selections.items():
            garment_item = QTreeWidgetItem(root_item)
            garment_item.setText(0, f"👔 {garment_data['base_item']}")
            garment_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
            garment_item.setForeground(0, QColor(100, 149, 237))
            
            # Agregar opciones de color
            colors = ["black", "white", "blue", "red", "green", "gray", "brown","orange","yellow","pink","gold","silver","purple","jade","violet"]



            for color in colors:
                color_item = QTreeWidgetItem(garment_item)
                color_item.setText(0, f"🎨 {color}")
                color_item.setFont(0, QFont("Segoe UI", 8))
                color_item.setForeground(0, QColor(255, 255, 255))
                color_item.setData(0, Qt.ItemDataRole.UserRole, ("color", color, garment_id))
        
        tree_widget.expandAll()
        
        # AGREGAR ESTAS LÍNEAS QUE FALTABAN:
        # Agregar al layout
        self.columns_layout.addWidget(color_column)
        self.dynamic_columns.append(color_column)
        
        # Marcar como creada
        if column_index not in self.column_states:
            self.column_states[column_index] = {}
        self.column_states[column_index]['created'] = True
        
        # Hacer visible la columna
        color_column.setVisible(True)
        
        print("DEBUG: Columna de colores agregada al layout y hecha visible")
        
        return color_column
    
    def _show_next_column(self, column_index, column_title):
        """Muestra la siguiente columna con combinaciones - LÓGICA ORIGINAL"""
        print(f"Mostrando columna {column_index}: {column_title}")
        
        # Verificar si la columna ya existe
        if self._column_exists(column_index):
            print(f"Columna {column_index} ya existe, no se crea duplicada")
            return
        
        # Obtener datos para la siguiente columna basado en las selecciones actuales
        next_data = self._get_next_column_data_simple(column_title)
        
        if next_data:
            # Crear nueva columna
            new_column = self._create_suggestion_column(column_title, column_index)
            
            # Agregar al layout
            self.columns_layout.addWidget(new_column)
            self.dynamic_columns.append(new_column)
            
            # Marcar como creada
            if column_index not in self.column_states:
                self.column_states[column_index] = {}
            self.column_states[column_index]['created'] = True
            
            # Llenar con datos
            tree_widget = new_column.findChild(QTreeWidget)
            self._populate_column(tree_widget, next_data, column_title)
            
            # Mostrar la columna
            new_column.setVisible(True)
        else:
            # No hay datos, mostrar mensaje de fin
            self._show_end_message(column_index)
    
    def _get_next_column_data_simple(self, column_title):
        """Obtiene datos de manera simple basado en el título de la columna"""
        if column_title == "Combinaciones":
            # Obtener la última selección de prenda principal
            for selection in reversed(self.selection_history):
                if selection['column_index'] == 0:
                    return self.suggestion_engine.get_combinations(selection['category'], selection['value'])
        elif column_title == "Accesorios":
            return self.suggestion_engine.get_accessories("", "")
        
        return None
    
    def _show_skip_indicator_in_column(self, column_widget, column_title):
        """Muestra indicador de salto en una columna específica"""
        tree_widget = column_widget.findChild(QTreeWidget)
        if tree_widget:
            tree_widget.clear()
            skip_item = QTreeWidgetItem(tree_widget)
            skip_item.setText(0, f"⏭️ {column_title} - SALTADO")
            skip_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
            skip_item.setForeground(0, QColor(255, 165, 0))  # Color naranja
            tree_widget.expandAll()
    
    def _get_next_column_data(self, category, value, column_type):
        """Obtiene los datos para la siguiente columna"""
        if column_type == "Combinaciones":
            # Obtener combinaciones del motor de sugerencias
            return self.suggestion_engine.get_combinations(category, value)
        elif column_type == "Estilos":
            # Obtener estilos (implementar en suggestion_engine)
            return self.suggestion_engine.get_styles(category, value)
        elif column_type == "Colores":
            # Obtener colores (implementar en suggestion_engine)
            return self.suggestion_engine.get_colors(category, value)
        elif column_type == "Accesorios":
            # Obtener accesorios (implementar en suggestion_engine)
            return self.suggestion_engine.get_accessories(category, value)
        
        return None
    
    def _get_next_column_type(self, current_column_index, category, value):
        """Determina el tipo de la siguiente columna - SIN ESTILOS"""
        if current_column_index == 1:  # Después de combinaciones
            return "Accesorios"
        elif current_column_index == 2:  # Después de accesorios
            return "Colores"
        else:
            return None  # No más columnas
    
    def _populate_column(self, tree_widget, data, title):
        """Llena una columna con datos - CON TRADUCCIONES"""
        tree_widget.clear()
        
        # Crear nodo raíz
        root_item = QTreeWidgetItem(tree_widget)
        root_item.setText(0, f"🎯 {title}")
        root_item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
        root_item.setForeground(0, QColor(70, 130, 180))
        
        # Procesar datos por categoría
        for category, suggestions in data.items():
            if suggestions:
                # Crear nodo de categoría
                category_item = QTreeWidgetItem(root_item)
                category_display = category.replace('_', ' ').title()
                category_item.setText(0, f"📁 {category_display}")
                category_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
                category_item.setForeground(0, QColor(100, 149, 237))
                
                # Agregar sugerencias con traducciones
                for suggestion in suggestions[:6]:  # Limitar a 6
                    self._create_item_with_translation(
                        tree_widget, suggestion, category, category_item
                    )
        
        # Expandir todo
        tree_widget.expandAll()
    
    def _show_end_message(self, column_index):
        """Muestra mensaje cuando no hay más combinaciones"""
        end_column = self._create_suggestion_column("Fin de combinaciones", column_index)
        
        # Agregar al layout
        self.columns_layout.addWidget(end_column)
        self.dynamic_columns.append(end_column)
        
        # Mostrar mensaje
        tree_widget = end_column.findChild(QTreeWidget)
        tree_widget.clear()
        
        root_item = QTreeWidgetItem(tree_widget)
        root_item.setText(0, "ℹ️ No hay más combinaciones disponibles")
        root_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
        root_item.setForeground(0, QColor(255, 165, 0))  # Naranja
        
        end_column.setVisible(True)
    
    def _clear_dynamic_columns(self):
        """Limpia todas las columnas dinámicas excepto la principal"""
        print("Limpiando columnas dinámicas...")
        
        # Remover todas las columnas excepto la principal (índice 0)
        columns_to_remove = []
        
        for i in range(1, len(self.dynamic_columns)):
            column_widget = self.dynamic_columns[i]
            columns_to_remove.append(column_widget)
            self.columns_layout.removeWidget(column_widget)
            column_widget.setParent(None)
            column_widget.deleteLater()
        
        # Mantener solo la columna principal
        self.dynamic_columns = self.dynamic_columns[:1]
        
        # Limpiar estados de columnas dinámicas
        keys_to_remove = [k for k in self.column_states.keys() if k > 0]
        for key in keys_to_remove:
            del self.column_states[key]
        
        print(f"Columnas dinámicas limpiadas. Columnas restantes: {len(self.dynamic_columns)}")
        
    def _clear_columns_from(self, start_index):
        """Limpia las columnas dinámicas desde un índice específico hacia adelante"""
        if start_index >= len(self.dynamic_columns):
            return # No hay columnas que limpiar
        print(f"Limpiando columnas desde índice {start_index}...")
        
        # NUEVO: Limpiar selecciones correspondientes según el índice
        if start_index <= 1:  # Si limpiamos desde combinaciones (índice 1)
            # Limpiar todas las selecciones excepto la prenda principal
            garments_to_keep = {}
            for garment_id, garment_data in self.garment_selections.items():
                # Solo mantener la primera prenda principal
                if garment_id.startswith('garment_') and len(garments_to_keep) == 0:
                    garments_to_keep[garment_id] = {
                        'base_item': garment_data['base_item'],
                        'category': garment_data['category'],
                        'attributes': {}  # Limpiar atributos como colores
                    }
            self.garment_selections = garments_to_keep
            
        elif start_index <= 2:  # Si limpiamos desde accesorios (índice 2)
            # Limpiar accesorios y colores, mantener prendas principales y combinaciones
            garments_to_keep = {}
            for garment_id, garment_data in self.garment_selections.items():
                if garment_id.startswith('garment_'):  # Mantener solo prendas principales
                    garments_to_keep[garment_id] = {
                        'base_item': garment_data['base_item'],
                        'category': garment_data['category'],
                        'attributes': {}  # Limpiar colores
                    }
            self.garment_selections = garments_to_keep
            
        elif start_index <= 3:  # Si limpiamos desde colores (índice 3)
            # Solo limpiar colores, mantener todo lo demás
            for garment_id in self.garment_selections:
                self.garment_selections[garment_id]['attributes'] = {}
        
        # Remover columnas del layout desde el final hacia atrás
        columns_to_remove = []
        for i in range(start_index, len(self.dynamic_columns)):
            column = self.dynamic_columns[i]
            columns_to_remove.append(column)
            self.columns_layout.removeWidget(column)
            column.setParent(None)
            column.deleteLater()
            
        # Actualizar la lista de columnas
        self.dynamic_columns = self.dynamic_columns[:start_index]
            
        # Limpiar estados específicos según el índice
        if start_index <= 2:  # Si limpiamos desde accesorios o antes
            self.color_column_created = False

        # NUEVO: Actualizar el prompt después de limpiar las selecciones
        self._update_prompt()
        
        print(f"Columnas limpiadas. Columnas restantes: {len(self.dynamic_columns)}")
        print(f"Selecciones restantes: {list(self.garment_selections.keys())}")
    
    def _is_clothing_item(self, category, value):
        """Determina si un elemento es una prenda de vestir"""
        clothing_categories = ['vestuario_superior', 'vestuario_inferior', 'vestuario_general']
        return category in clothing_categories
    
    def _show_combinations(self, category, value):
        """Muestra combinaciones para una prenda específica"""
        print(f"Buscando combinaciones para: {category} - {value}")
        
        # Obtener combinaciones del motor de sugerencias
        combinations = self.suggestion_engine.get_combinations(category, value)
        
        if combinations:
            print(f"Combinaciones finales: {combinaciones}")
            
            # Mostrar la columna de combinaciones
            self.combinations_column.setVisible(True)
            
            # Obtener el tree widget de la columna de combinaciones
            combinations_tree = self.combinations_column.findChild(QTreeWidget)
            combinations_tree.clear()
            
            # Crear nodo raíz
            root_item = QTreeWidgetItem(combinations_tree)
            root_item.setText(0, f"🔗 Combinaciones para: {value}")
            root_item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
            root_item.setForeground(0, QColor(70, 130, 180))
            
            # Agregar combinaciones por categoría
            for combo_category, combo_suggestions in combinations.items():
                if combo_suggestions:
                    # Crear nodo de categoría
                    category_item = QTreeWidgetItem(root_item)
                    category_item.setText(0, f"📁 {combo_category.replace('_', ' ').title()}")
                    category_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
                    category_item.setForeground(0, QColor(100, 149, 237))
                    
                    # Agregar sugerencias individuales
                    for suggestion in combo_suggestions[:6]:  # Limitar a 6
                        suggestion_item = QTreeWidgetItem(category_item)
                        suggestion_item.setText(0, f"✨ {suggestion}")
                        suggestion_item.setFont(0, QFont("Segoe UI", 8))
                        suggestion_item.setForeground(0, QColor(255, 255, 255))
                        suggestion_item.setData(0, Qt.ItemDataRole.UserRole, (combo_category, suggestion))
            
            # Expandir todo
            combinations_tree.expandAll()
        else:
            print("No se encontraron combinaciones")
            # Ocultar la columna si no hay combinaciones
            self.combinations_column.setVisible(False)
    
    def _init_category_relationships(self):
        """Inicializa las relaciones entre categorías"""
        return {
            'pose_global': ['expresion', 'accion', 'vestuario_general'],
            'vestuario_general': ['vestuario_superior', 'vestuario_inferior', 'vestuario_accesorios'],
            'vestuario_superior': ['vestuario_inferior', 'vestuario_accesorios', 'ropa_interior_superior'],
            'vestuario_inferior': ['vestuario_superior', 'vestuario_accesorios', 'ropa_interior_inferior'],
            'expresion': ['pose_global', 'accion'],
            'accion': ['pose_global', 'expresion', 'fondo'],
            'fondo': ['accion', 'pose_global'],
            'vestuario_accesorios': ['vestuario_superior', 'vestuario_inferior'],
            'ropa_interior_superior': ['vestuario_superior'],
            'ropa_interior_inferior': ['vestuario_inferior'],
            'estilo_coordinado': ['vestuario_general', 'vestuario_superior', 'vestuario_inferior', 'vestuario_accesorios']
        }

    def _init_contextual_suggestions(self):
        """Inicializa sugerencias contextuales"""
        return {
            'pose_global': {
                'sitting': {
                    'expresion': ['focused', 'relaxed', 'contemplative'],
                    'accion': ['reading', 'studying', 'thinking'],
                    'vestuario_general': ['school uniform', 'casual outfit']
                },
                'standing': {
                    'expresion': ['confident', 'determined', 'friendly'],
                    'accion': ['presenting', 'greeting', 'posing'],
                    'vestuario_general': ['formal outfit', 'casual outfit']
                }
            }
        }
    
    def show_initial_message(self):
        """Muestra mensaje inicial cuando no hay sugerencias"""
        if hasattr(self, 'tree_widget'):
            self.tree_widget.clear()
            root_item = QTreeWidgetItem(self.tree_widget)
            root_item.setText(0, "💡 Selecciona un valor del autocompletado para ver sugerencias")
            root_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
            root_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.Mid))
            self.tree_widget.expandAll()
        
    def update_suggestions_tree(self, selected_category, selected_value):
        """Actualiza el árbol de sugerencias basado en la categoría y valor seleccionados"""
        # Limpiar el árbol principal
        self.tree_widget.clear()
        
        # Crear nodo raíz
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, f"🎯 Sugerencias para: {selected_value}")
        root_item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
        root_item.setForeground(0, QColor(70, 130, 180))
        
        has_suggestions = False
        
        # Obtener sugerencias del motor
        engine_suggestions = self.suggestion_engine.get_suggestions(selected_category, selected_value)
        
        # Procesar sugerencias del SuggestionEngine
        if engine_suggestions:
            has_suggestions = True
            for related_category, suggestions in engine_suggestions.items():
                if suggestions:
                    # Crear nodo de categoría
                    category_item = QTreeWidgetItem(root_item)
                    category_item.setText(0, f"📁 {related_category.replace('_', ' ').title()}")
                    category_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
                    category_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.Link))
                    
                    # Crear nodos de sugerencias (limitar a 8)
                    for suggestion in suggestions[:8]:
                        suggestion_item = QTreeWidgetItem(category_item)
                        
                        # Verificar si esta sugerencia ya fue seleccionada
                        suggestion_key = (related_category, suggestion)
                        is_selected = suggestion_key in self.selected_suggestions
                        
                        if is_selected:
                            suggestion_item.setText(0, f"✅ {suggestion}")
                            suggestion_item.setForeground(0, QColor(34, 139, 34))
                            suggestion_item.setFont(0, QFont("Segoe UI", 8, QFont.Weight.Bold))
                        else:
                            suggestion_item.setText(0, f"✨ {suggestion}")
                            suggestion_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.LinkVisited))
                            suggestion_item.setFont(0, QFont("Segoe UI", 8))
                        
                        suggestion_item.setData(0, Qt.ItemDataRole.UserRole, (related_category, suggestion))
        
        # Si no hay sugerencias, mostrar mensaje
        if not has_suggestions:
            no_suggestions_item = QTreeWidgetItem(root_item)
            no_suggestions_item.setText(0, "ℹ️ No hay categorías relacionadas para este valor")
            no_suggestions_item.setFont(0, QFont("Segoe UI", 8))
            no_suggestions_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.Mid))
        
        # Expandir todo el árbol
        self.tree_widget.expandAll()
        
    def clear_suggestions(self):
        """Limpia todas las sugerencias y muestra mensaje inicial"""
        self.selected_suggestions.clear()
        if hasattr(self, 'combinations_column'):
            self.combinations_column.setVisible(False)
        self.show_initial_message()
        
    def clear_selected_suggestions(self):
        """Limpia solo las sugerencias seleccionadas"""
        self.selected_suggestions.clear()
        # Refrescar la vista actual si hay sugerencias mostradas
        if self.tree_widget.topLevelItemCount() > 0:
            # Obtener la categoría y valor actual del nodo raíz
            root_item = self.tree_widget.topLevelItem(0)
            if root_item:
                text = root_item.text(0)
                # Extraer información y refrescar
                # (esto requeriría almacenar la categoría/valor actual)
    
    def _update_category_visual_state(self, category):
        """Actualiza el estado visual de todos los elementos de una categoría"""
        # Recorrer todos los elementos del árbol principal
        for i in range(self.tree_widget.topLevelItemCount()):
            root_item = self.tree_widget.topLevelItem(i)
            
            # Recorrer categorías
            for j in range(root_item.childCount()):
                category_item = root_item.child(j)
                
                # Recorrer elementos de la categoría
                for k in range(category_item.childCount()):
                    suggestion_item = category_item.child(k)
                    item_data = suggestion_item.data(0, Qt.ItemDataRole.UserRole)
                    
                    if item_data and item_data[0] == category:
                        # Verificar si este elemento está seleccionado
                        suggestion_key = (item_data[0], item_data[1])
                        is_selected = suggestion_key in self.selected_suggestions
                        
                        if is_selected:
                            suggestion_item.setText(0, f"✅ {item_data[1]}")
                            suggestion_item.setForeground(0, QColor(34, 139, 34))
                            suggestion_item.setFont(0, QFont("Segoe UI", 8, QFont.Weight.Bold))
                        else:
                            suggestion_item.setText(0, f"✨ {item_data[1]}")
                            suggestion_item.setForeground(0, self.tree_widget.palette().color(self.tree_widget.palette().ColorRole.LinkVisited))
                            suggestion_item.setFont(0, QFont("Segoe UI", 8))
    
    def _track_selection(self, column_index, category, value, selection_type):
        """Registra una selección y actualiza el estado"""
        selection_data = {
            'type': selection_type,
            'category': category,
            'value': value,
            'column_index': column_index,
            'timestamp': len(self.selection_history),
            'skipped': value == "(saltado)"  # Marcar si fue saltado
        }
        
        if selection_type == "garment" and not selection_data['skipped']:
            # Nueva prenda principal (solo si no fue saltado)
            garment_id = f"garment_{len(self.garment_selections)}"
            self.garment_selections[garment_id] = {
                'base_item': value,
                'category': category,
                'attributes': {}
            }
            self.current_garment_id = garment_id
            
        elif selection_type == "accessory" and not selection_data['skipped']:
            # Accesorios como prendas independientes
            garment_id = f"accessory_{len(self.garment_selections)}"
            self.garment_selections[garment_id] = {
                'base_item': value,
                'category': category,
                'attributes': {}
            }
            
        elif selection_type == "color":
            # Color puede aplicarse a múltiples prendas
            target_garment = self._determine_color_target(value)
            if target_garment and target_garment in self.garment_selections:
                self.garment_selections[target_garment]['attributes']['color'] = value
        
        self.selection_history.append(selection_data)
        self._update_prompt()
    
    def _determine_color_target(self, color_selection):
        """Determina a qué prenda se aplica un color seleccionado"""
        # Lógica para determinar la prenda objetivo basada en el contexto
        if self.current_garment_id:
            return self.current_garment_id
        return None
    
    def _build_contextual_prompt(self):
        """Construye el prompt contextual basado en las selecciones actuales"""
        prompt_parts = []
        
        # Procesar cada prenda seleccionada
        for garment_id, garment_data in self.garment_selections.items():
            if garment_data['base_item'] != "(saltado)":
                base_item = garment_data['base_item']
                attributes = garment_data['attributes']
                
                # Limpiar y formatear la prenda base (eliminar guiones bajos)
                clean_base_item = self._clear_item_name(base_item)
                
                # Construir descripción de la prenda
                garment_description = []
                
                # Agregar color PRIMERO si existe
                if 'color' in attributes:
                    color_value = attributes['color']
                    # Si el color viene en formato "prenda_color", extraer solo el color
                    if '_' in color_value:
                        # Tomar la última parte después del último guión bajo
                        clean_color = color_value.split('_')[-1]
                    else:
                        clean_color = color_value
                    
                    clean_color = self._clear_item_name(clean_color)
                    garment_description.append(clean_color)
                
                # Agregar prenda base limpia DESPUÉS
                garment_description.append(clean_base_item)
                
                # Unir con espacio (no guión bajo)
                prompt_parts.append(' '.join(garment_description))
        
        # Unir con comas y espacios correctamente
        return ', '.join(prompt_parts)
    
    def _clear_item_name(self, item_name):
        """Limpia nombres de elementos: elimina guiones bajos y formatea correctamente"""
        if not item_name:
            return item_name
        
        # Eliminar guiones bajos y reemplazar con espacios
        cleaned = item_name.replace('_', ' ')
        
        # Convertir a minúsculas para consistencia
        cleaned = cleaned.lower()
        
        return cleaned
    
    def _update_prompt(self):
        """Actualiza el prompt en el generador"""
        contextual_prompt = self._build_contextual_prompt()
        if contextual_prompt and self.prompt_generator:
            # Actualizar el prompt contextual
            self.prompt_generator.set_category_value('vestuario_contextual', contextual_prompt)
            # Emitir señal para actualizar la interfaz
            self.prompt_updated.emit()
            # Cambiar esta línea:
            # self.prompt_generator.add_contextual_suggestions(contextual_prompt)
            # Por esta:
            self.prompt_generator.set_category_value('vestuario_contextual', contextual_prompt)
    
    def _create_color_column_for_all_garments(self, column_index):
        """Crea columna de colores con opciones para todas las prendas"""
        color_column = self._create_suggestion_column("Colores", column_index)
        tree_widget = color_column.findChild(QTreeWidget)
        
        # Limpiar y crear estructura
        tree_widget.clear()
        
        # Crear nodo raíz
        root_item = QTreeWidgetItem(tree_widget)
        root_item.setText(0, "🎨 Seleccionar Colores")
        root_item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
        root_item.setForeground(0, QColor(70, 130, 180))
        
        # Crear sección para cada prenda seleccionada
        for garment_id, garment_data in self.garment_selections.items():
            garment_item = QTreeWidgetItem(root_item)
            garment_item.setText(0, f"👔 {garment_data['base_item']}")
            garment_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
            garment_item.setForeground(0, QColor(100, 149, 237))
            
            # Agregar opciones de color
            colors = ["black", "white", "blue", "red", "green", "gray", "brown","orange","yellow","pink","gold","silver","purple","jade","violet"]
            for color in colors:
                color_item = QTreeWidgetItem(garment_item)
                color_item.setText(0, f"🎨 {color}")
                color_item.setFont(0, QFont("Segoe UI", 8))
                color_item.setForeground(0, QColor(255, 255, 255))
                color_item.setData(0, Qt.ItemDataRole.UserRole, ("color", f"{garment_data['base_item']}_{color}", garment_id))
        
        tree_widget.expandAll()
        
        # AGREGAR ESTAS LÍNEAS QUE FALTABAN:
        # Agregar al layout
        self.columns_layout.addWidget(color_column)
        self.dynamic_columns.append(color_column)
        
        # Marcar como creada
        if column_index not in self.column_states:
            self.column_states[column_index] = {}
        self.column_states[column_index]['created'] = True
        
        # Hacer visible la columna
        color_column.setVisible(True)
        
        print("DEBUG: Columna de colores agregada al layout y hecha visible")
        
        return color_column
    
    def _skip_to_next_column(self, current_column_index):
        """Salta al siguiente paso sin seleccionar nada en la columna actual"""
        print(f"Saltando desde columna {current_column_index} al siguiente paso")
        
        if current_column_index == 1:  # Desde Combinaciones
            # Saltar a Accesorios
            self._show_next_column("", "(saltado)", 2, "Accesorios")
            
        elif current_column_index == 2:  # Desde Accesorios
            # Saltar directamente a Colores
            self._show_color_column_for_all_garments(3)
        
        # Actualizar el prompt para reflejar el salto
        def _show_skip_indicator(self, column_index, column_title):
            """Muestra un indicador visual cuando se salta un paso"""
            # Encontrar la columna correspondiente
            if column_index < len(self.dynamic_columns):
                column_widget = self.dynamic_columns[column_index]
                tree_widget = column_widget.findChild(QTreeWidget)
                
                if tree_widget:
                    tree_widget.clear()
                    skip_item = QTreeWidgetItem(tree_widget)
                    skip_item.setText(0, f"⏭️ {column_title} - SALTADO")
                    skip_item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
                    skip_item.setForeground(0, QColor(255, 165, 0))  # Color naranja
                    tree_widget.expandAll()
        
        # Control de estado de columnas
        self.column_states = {}  # {column_index: {'collapsed': bool, 'created': bool}}
        self.max_columns = 4

    def _toggle_skip_column(self, current_column_index):
        """Toggle para colapsar/expandir columna y evitar duplicación"""
        print(f"Toggle skip para columna {current_column_index}")
        
        # Verificar si la columna ya está colapsada
        if current_column_index in self.column_states:
            is_collapsed = self.column_states[current_column_index].get('collapsed', False)
            
            if is_collapsed:
                # Expandir: mostrar la columna actual y ocultar las siguientes
                self._expand_column(current_column_index)
            else:
                # Colapsar: ocultar la columna actual y mostrar la siguiente
                self._collapse_column(current_column_index)
        else:
            # Primera vez: colapsar
            self._collapse_column(current_column_index)
    
    def _collapse_column(self, column_index):
        """Colapsa la columna actual y muestra la siguiente"""
        # Marcar como colapsada
        if column_index not in self.column_states:
            self.column_states[column_index] = {}
        self.column_states[column_index]['collapsed'] = True
        
        # Ocultar el contenido de la columna actual (pero mantener el header)
        if column_index < len(self.dynamic_columns):
            column_widget = self.dynamic_columns[column_index]
            tree_widget = column_widget.findChild(QTreeWidget)
            if tree_widget:
                tree_widget.setVisible(False)
        
        # Mostrar la siguiente columna (solo si no existe ya)
        next_column_index = column_index + 1
        if not self._column_exists(next_column_index):
            if column_index == 1:  # Desde Combinaciones
                self._show_next_column("", "(saltado)", 2, "Accesorios")
            elif column_index == 2:  # Desde Accesorios
                self._show_color_column_for_all_garments(3)
        
        # Actualizar el prompt
        self._track_selection(column_index, "", "(saltado)", "skip")
    
    def _expand_column(self, column_index):
        """Expande la columna actual y oculta las siguientes"""
        # Marcar como expandida
        self.column_states[column_index]['collapsed'] = False
        
        # Mostrar el contenido de la columna actual
        if column_index < len(self.dynamic_columns):
            column_widget = self.dynamic_columns[column_index]
            tree_widget = column_widget.findChild(QTreeWidget)
            if tree_widget:
                tree_widget.setVisible(True)
        
        # Ocultar/eliminar columnas siguientes
        self._remove_columns_after(column_index)
        
        # Remover el salto del historial
        self._remove_skip_from_history(column_index)
    
    def _column_exists(self, column_index):
        """Verifica si una columna ya existe"""
        return column_index < len(self.dynamic_columns)
    
    def _remove_columns_after(self, column_index):
        """Elimina todas las columnas después del índice especificado"""
        columns_to_remove = []
        
        for i in range(column_index + 1, len(self.dynamic_columns)):
            column_widget = self.dynamic_columns[i]
            columns_to_remove.append(column_widget)
            self.columns_layout.removeWidget(column_widget)
            column_widget.setParent(None)
            column_widget.deleteLater()
        
        # Actualizar la lista de columnas dinámicas
        self.dynamic_columns = self.dynamic_columns[:column_index + 1]
        
        # Limpiar estados de columnas eliminadas
        keys_to_remove = [k for k in self.column_states.keys() if k > column_index]
        for key in keys_to_remove:
            del self.column_states[key]
    
    def _remove_skip_from_history(self, column_index):
        """Remueve el salto del historial de selecciones"""
        # Filtrar el historial para remover saltos de esta columna
        self.selection_history = [
            item for item in self.selection_history 
            if not (item.get('column_index') == column_index and item.get('value') == "(saltado)")
        ]
        
        # Actualizar el prompt
        self._update_prompt()

    def _get_translation_map(self):
        """Mapa de traducciones español -> inglés para tooltips discretos"""
        return {
            # Prendas principales
            'school blazer': 'blazer escolar',
            'white shirt': 'camisa blanca', 
            'uniform blouse': 'blusa de uniforme',
            'polo shirt': 'polo',
            'pleated skirt': 'falda plisada',
            'school skirt': 'falda escolar',
            'knee-length skirt': 'falda hasta la rodilla',
            
            # Accesorios
            'school bag': 'mochila escolar',
            'hair ribbon': 'cinta para el cabello',
            'school badge': 'insignia escolar',
            'knee socks': 'calcetines hasta la rodilla',
            'school shoes': 'zapatos escolares',
            'necktie': 'corbata',
            'bow tie': 'corbatín',
            
            # Colores
            'black': 'negro',
            'white': 'blanco',
            'blue': 'azul',
            'red': 'rojo',
            'green': 'verde',
            'gray': 'gris',
            'navy': 'azul marino',
            'brown': 'marrón',
            'pink': 'rosa',
            'purple': 'morado'
        }
    
    def _create_item_with_translation(self, tree_widget, english_text, category, parent_item=None):
        """Crea un item con texto en inglés y tooltip de traducción"""
        translation_map = self._get_translation_map()
        spanish_translation = translation_map.get(english_text, english_text)
        
        if parent_item:
            item = QTreeWidgetItem(parent_item)
        else:
            item = QTreeWidgetItem(tree_widget)
        
        # Texto principal en inglés
        item.setText(0, f"✨ {english_text}")
        
        # Tooltip discreto con traducción
        item.setToolTip(0, f"🇪🇸 {spanish_translation}")
        
        # Datos para el sistema
        item.setData(0, Qt.ItemDataRole.UserRole, (category, english_text))
        
        # Estilo
        item.setFont(0, QFont("Segoe UI", 8))
        item.setForeground(0, QColor(255, 255, 255))
        
        return item
    
    def _clear_contextual_prompt(self):
        """Limpia completamente el prompt contextual y reinicia el sistema"""
        print("Limpiando prompt contextual anterior...")
        
        # Limpiar todas las estructuras de datos
        self.selection_history.clear()
        self.garment_selections.clear()
        self.current_garment_id = None
        
        # Limpiar estados de columnas
        self.column_states.clear()
        
        # Limpiar el prompt en el generador
        if self.prompt_generator:
            self.prompt_generator.set_category_value('vestuario_contextual', '')
            # Emitir señal para actualizar la interfaz
            self.prompt_updated.emit()
        
        print("Prompt contextual limpiado completamente")

    def _remove_selections_from_column(self, column_index):
        """Remueve las selecciones desde una columna específica hacia adelante"""
        if column_index == 1:  # Desde combinaciones
            self.garment_selections = [s for s in self.garment_selections if s['type'] == 'main']
        elif column_index == 2:  # Desde accesorios
            self.garment_selections = [s for s in self.garment_selections 
                                     if s['type'] in ['main', 'combination']]
        elif column_index == 3:  # Desde colores
            self.garment_selections = [s for s in self.garment_selections 
                                     if s['type'] in ['main', 'combination', 'accessory']]
        
    