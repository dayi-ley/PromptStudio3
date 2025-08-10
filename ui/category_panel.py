from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QDialog, QLineEdit, QCompleter, QGridLayout,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from .category_config_dialog import CategoryConfigDialog
from .category_data import CategoryData

class CategoryPanel(QWidget):
    category_changed = pyqtSignal(str, str)
    suggestion_requested = pyqtSignal(str, str)
    
    def __init__(self, prompt_generator):
        super().__init__()
        self.prompt_generator = prompt_generator
        self.category_buttons = {}
        self.category_states = {}
        self.selected_categories = set()
        self.category_inputs = {}  # Diccionario para almacenar los inputs
        
        # Usar la clase CategoryData para manejar datos
        self.category_data = CategoryData()
        self.hidden_categories = self.category_data.hidden_categories
        self.disabled_categories = self.category_data.disabled_categories
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 4, 8, 6)
        
        # Sección de categorías
        category_section = QFrame()
        category_section.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 6px;
            }
        """)
        category_layout = QVBoxLayout(category_section)
        category_layout.setSpacing(4)
        category_layout.setContentsMargins(10, 6, 10, 8)
        
        # Header con título y botón de configuración
        header_layout = QHBoxLayout()
        
        title = QLabel("Categorías")
        title.setFont(QFont("Segoe UI", 9))
        title.setStyleSheet("color: #cccccc; margin-bottom: 2px;")
        header_layout.addWidget(title)
        
        config_button = QPushButton("⚙️ Configurar")
        config_button.setMaximumSize(80, 24)
        config_button.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #cccccc;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 8pt;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        config_button.clicked.connect(self.show_category_config)
        header_layout.addWidget(config_button)
        
        category_layout.addLayout(header_layout)
        
        # Contenedor para botones
        self.categories_container = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_container)
        self.categories_layout.setSpacing(8)
        self.categories_layout.setContentsMargins(5, 5, 5, 5)
        
        self.recreate_category_buttons()
        
        # Scroll para las categorías
        categories_scroll = QScrollArea()
        categories_scroll.setWidget(self.categories_container)
        categories_scroll.setWidgetResizable(True)
        categories_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        categories_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        categories_scroll.setMaximumHeight(120)
        
        category_layout.addWidget(categories_scroll)
        layout.addWidget(category_section)
        
        # Sección de input inteligente
        self.input_section = QFrame()
        self.input_section.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 6px;
            }
        """)
        self.input_layout = QVBoxLayout(self.input_section)
        self.input_layout.setSpacing(4)
        self.input_layout.setContentsMargins(10, 6, 10, 8)
        
        # Título del input
        self.input_title = QLabel("Selecciona una categoría para comenzar")
        self.input_title.setFont(QFont("Segoe UI", 9))
        self.input_title.setStyleSheet("color: #cccccc; margin-bottom: 2px;")
        self.input_layout.addWidget(self.input_title)
        
        # Contenedor para inputs dinámicos con QGridLayout desde el inicio
        self.inputs_container = QWidget()
        self.inputs_container_layout = QGridLayout(self.inputs_container)
        self.inputs_container_layout.setSpacing(8)
        self.inputs_container_layout.setContentsMargins(5, 5, 5, 5)
        
        # Scroll para los inputs
        inputs_scroll = QScrollArea()
        inputs_scroll.setWidget(self.inputs_container)
        inputs_scroll.setWidgetResizable(True)
        inputs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inputs_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        inputs_scroll.setMaximumHeight(150)
        
        self.input_layout.addWidget(inputs_scroll)
        layout.addWidget(self.input_section)
        
        # Inicialmente ocultar la sección de input
        self.input_section.hide()

    def recreate_category_buttons(self):
        """Recrea todos los botones de categoría con layout tipo ladrillos"""
        # Limpiar botones existentes
        for i in reversed(range(self.categories_layout.count())):
            child = self.categories_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        self.category_buttons.clear()
        
        # Obtener categorías visibles
        visible_categories = [
            cat for cat in self.prompt_generator.categories.keys() 
            if cat not in self.hidden_categories
        ]
        
        if not visible_categories:
            return
        
        # Crear layout tipo ladrillos
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        current_row_layout = QHBoxLayout()
        current_row_layout.setSpacing(6)
        current_row_layout.setContentsMargins(0, 0, 0, 0)
        
        current_row_widget = QWidget()
        current_row_widget.setLayout(current_row_layout)
        
        container_width = 1200
        current_width = 0
        
        for category in visible_categories:
            button = QPushButton(category.replace('_', ' ').title())
            
            is_disabled = category in self.disabled_categories
            
            if is_disabled:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #6B7280;
                        color: #9CA3AF;
                        border: none;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 10px;
                        font-weight: 500;
                        margin: 0px;
                    }
                """)
                button.setEnabled(False)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #8B5CF6;
                        color: white;
                        border: none;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 10px;
                        font-weight: 500;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #7C3AED;
                    }
                    QPushButton:pressed {
                        background-color: #6D28D9;
                    }
                    QPushButton:checked {
                        background-color: #059669;
                    }
                """)
                button.setCheckable(True)
            
            button.adjustSize()
            button_width = button.sizeHint().width() + 6
            
            if current_width + button_width > container_width and current_row_layout.count() > 0:
                current_row_layout.addStretch()
                main_layout.addWidget(current_row_widget)
                
                current_row_layout = QHBoxLayout()
                current_row_layout.setSpacing(6)
                current_row_layout.setContentsMargins(0, 0, 0, 0)
                
                current_row_widget = QWidget()
                current_row_widget.setLayout(current_row_layout)
                current_width = 0
            
            current_row_layout.addWidget(button)
            current_width += button_width
            
            if not is_disabled:
                button.clicked.connect(lambda checked, cat=category: self.on_category_selected(cat))
            
            self.category_buttons[category] = button
        
        if current_row_layout.count() > 0:
            current_row_layout.addStretch()
            main_layout.addWidget(current_row_widget)
        
        main_layout.addStretch()
        self.categories_layout.addWidget(main_container)

    def on_category_selected(self, category):
        """Maneja la selección de una categoría"""
        if category in self.disabled_categories:
            return
            
        button = self.category_buttons.get(category)
        if not button:
            return
            
        if button.isChecked():
            self.selected_categories.add(category)
            self.create_category_input(category)
            self.category_changed.emit(category, 'selected')
            # Emitir señal para sugerencias
            self.suggestion_requested.emit(category, '')
        else:
            self.selected_categories.discard(category)
            self.remove_category_input(category)
            self.category_changed.emit(category, 'deselected')
            
        # Mostrar/ocultar sección de input según si hay categorías seleccionadas
        if self.selected_categories:
            self.input_section.show()
            self.input_title.setText(f"Configurar categorías seleccionadas ({len(self.selected_categories)})")
        else:
            self.input_section.hide()
    
    def create_category_input(self, category):
        """Crea un input inteligente para una categoría"""
        if category in self.category_inputs:
            return  # Ya existe
            
        # Contenedor para esta categoría (más compacto)
        category_container = QFrame()
        category_container.setFixedSize(280, 70)  # Tamaño fijo más compacto
        category_container.setStyleSheet("""
            QFrame {
                background-color: #505050;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        
        container_layout = QVBoxLayout(category_container)
        container_layout.setSpacing(2)
        container_layout.setContentsMargins(4, 3, 4, 3)
        
        # Etiqueta de la categoría (más compacta)
        category_label = QLabel(category.replace('_', ' ').title())
        category_label.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        category_label.setStyleSheet("color: #00cc88; margin: 0px; padding: 0px;")
        category_label.setMaximumHeight(12)
        container_layout.addWidget(category_label)
        
        # Layout horizontal para input y botón
        input_layout = QHBoxLayout()
        input_layout.setSpacing(2)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        # Input con autocompletado (más compacto)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"Valor para {category.replace('_', ' ')[:15]}...")
        line_edit.setMaximumHeight(25)
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #606060;
                border: 1px solid #777777;
                border-radius: 3px;
                padding: 3px 4px;
                color: #ffffff;
                font-size: 8pt;
            }
            QLineEdit:focus {
                border-color: #00cc88;
            }
        """)
        
        # Botón pequeño para mostrar opciones
        options_btn = QPushButton("📋")
        options_btn.setFixedSize(25, 25)
        options_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 3px;
                color: #ffffff;
                font-size: 10pt;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #00cc88;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        options_btn.setToolTip(f"Ver todas las opciones para {category.replace('_', ' ')}")
        options_btn.clicked.connect(lambda: self.show_category_options(category))
        
        # Añadir al layout horizontal
        input_layout.addWidget(line_edit)
        input_layout.addWidget(options_btn)
        
        # Configurar autocompletado
        options = self.prompt_generator.get_category_options(category)
        if options:
            completer = QCompleter(options)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            line_edit.setCompleter(completer)
        
        # Conectar eventos
        line_edit.textChanged.connect(lambda text, cat=category: self.on_input_changed(cat, text))
        
        container_layout.addLayout(input_layout)
        
        # Guardar referencia
        self.category_inputs[category] = {
            'container': category_container,
            'line_edit': line_edit,
            'label': category_label,
            'options_btn': options_btn
        }
        
        # Agregar directamente al grid
        self.add_input_to_grid(category_container)
        
    def show_category_options(self, category):
        """Muestra una ventana con todas las opciones de la categoría"""
        options = self.prompt_generator.get_category_options(category)
        if not options:
            return
            
        # Crear y mostrar el diálogo
        dialog = CategoryOptionsDialog(category, options, self)
        
        # Posicionar cerca del botón que se presionó
        if category in self.category_inputs:
            btn = self.category_inputs[category]['options_btn']
            btn_pos = btn.mapToGlobal(btn.rect().bottomLeft())
            dialog.move(btn_pos.x() - 150, btn_pos.y() + 5)
        
        dialog.exec()

    def add_input_to_grid(self, container):
        """Agrega un input al grid en la siguiente posición disponible"""
        # Calcular posición en el grid (3 columnas)
        total_inputs = len(self.category_inputs)
        row = (total_inputs - 1) // 3
        col = (total_inputs - 1) % 3
        
        # Agregar al grid
        self.inputs_container_layout.addWidget(container, row, col)
    
    def remove_category_input(self, category):
        """Elimina el input de una categoría"""
        if category in self.category_inputs:
            input_data = self.category_inputs[category]
            
            # Remover del layout
            self.inputs_container_layout.removeWidget(input_data['container'])
            input_data['container'].deleteLater()
            del self.category_inputs[category]
            
            # Reorganizar todos los inputs restantes
            self.reorganize_grid()
            
            # Limpiar valor en el generador
            self.prompt_generator.set_category_value(category, "")
    
    def reorganize_grid(self):
        """Reorganiza todos los inputs en el grid después de eliminar uno"""
        # Remover todos los widgets del grid
        for category, input_data in self.category_inputs.items():
            self.inputs_container_layout.removeWidget(input_data['container'])
        
        # Volver a agregar en orden
        row = 0
        col = 0
        for category, input_data in self.category_inputs.items():
            self.inputs_container_layout.addWidget(input_data['container'], row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def on_input_changed(self, category, text):
        """Maneja cambios en los inputs"""
        # Actualizar el generador de prompts
        self.prompt_generator.set_category_value(category, text)
        
        # Emitir señal de cambio
        self.category_changed.emit(category, text)
        
        # Si hay texto, emitir señal para sugerencias
        if text.strip():
            self.suggestion_requested.emit(category, text)
    
    def on_category_click(self, category):
        """Método para compatibilidad con main_window"""
        if category in self.category_buttons:
            button = self.category_buttons[category]
            button.setChecked(True)
            self.on_category_selected(category)
    
    def refresh_all(self):
        """Limpia todas las selecciones y inputs"""
        # Desmarcar todos los botones
        for button in self.category_buttons.values():
            button.setChecked(False)
        
        # Limpiar categorías seleccionadas
        self.selected_categories.clear()
        
        # Eliminar todos los inputs
        for category in list(self.category_inputs.keys()):
            self.remove_category_input(category)
        
        # Ocultar sección de input
        self.input_section.hide()

    def show_category_config(self):
        """Muestra el diálogo de configuración de categorías"""
        dialog = CategoryConfigDialog(
            list(self.prompt_generator.categories.keys()),
            self.hidden_categories,
            self.disabled_categories,
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.hidden_categories = dialog.get_hidden_categories()
            self.disabled_categories = dialog.get_disabled_categories()
            self.category_data.save_categories(self.hidden_categories, self.disabled_categories)
            self.recreate_category_buttons()

class CategoryOptionsDialog(QDialog):
    """Ventana simple para mostrar opciones de categoría"""
    def __init__(self, category, options, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)  # Hacer la ventana modal
        self.init_ui(category, options)
        
    def init_ui(self, category, options):
        # Calcular dimensiones dinámicas basadas en cantidad de opciones
        num_options = len(options)
        if num_options <= 10:
            columns = 1
            width = 250
            height = min(300, num_options * 25 + 80)
        elif num_options <= 30:
            columns = 2
            width = 400
            height = min(400, (num_options // 2 + 1) * 25 + 80)
        else:
            columns = 3
            width = 550
            height = min(500, (num_options // 3 + 1) * 25 + 80)
            
        self.setFixedSize(width, height)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Contenedor principal con estilo
        main_container = QFrame()
        main_container.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 8px;
            }
        """)
        container_layout = QVBoxLayout(main_container)
        container_layout.setSpacing(4)
        container_layout.setContentsMargins(8, 8, 8, 8)
        
        # Título pequeño
        title = QLabel(f"Opciones para: {category.replace('_', ' ').title()} ({num_options})")
        title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title.setStyleSheet("color: #00cc88; margin-bottom: 4px;")
        container_layout.addWidget(title)
        
        # Contenedor con scroll para las opciones
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #505050;
                border: 1px solid #666666;
                border-radius: 4px;
            }
        """)
        
        # Widget contenedor para las opciones en grid
        options_widget = QWidget()
        options_layout = QGridLayout(options_widget)
        options_layout.setSpacing(2)
        options_layout.setContentsMargins(4, 4, 4, 4)
        
        # Añadir opciones al grid en múltiples columnas
        for i, option in enumerate(options):
            row = i // columns
            col = i % columns
            
            option_label = QLabel(option)
            option_label.setStyleSheet("""
                QLabel {
                    background-color: #606060;
                    color: #ffffff;
                    padding: 3px 6px;
                    border-radius: 3px;
                    font-size: 8pt;
                    border: 1px solid #777777;
                }
                QLabel:hover {
                    background-color: #707070;
                    border-color: #00cc88;
                }
            """)
            option_label.setWordWrap(True)
            option_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            option_label.setMinimumHeight(20)
            option_label.setMaximumHeight(40)
            
            # Hacer clickeable
            option_label.mousePressEvent = lambda event, opt=option: self.option_clicked(opt)
            option_label.setCursor(Qt.CursorShape.PointingHandCursor)
            
            options_layout.addWidget(option_label, row, col)
        
        # Ajustar columnas para que tengan el mismo ancho
        for col in range(columns):
            options_layout.setColumnStretch(col, 1)
            
        scroll_area.setWidget(options_widget)
        container_layout.addWidget(scroll_area)
        
        # Nota informativa
        info_label = QLabel("💡 Click en una opción para copiarla")
        info_label.setFont(QFont("Segoe UI", 7))
        info_label.setStyleSheet("color: #999999; margin-top: 2px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(info_label)
        
        layout.addWidget(main_container)
        
    def option_clicked(self, option):
        """Copia la opción al portapapeles y cierra el diálogo"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(option)
        self.close()
        
    def mousePressEvent(self, event):
        """Cerrar solo si el click es fuera del contenido principal"""
        # Obtener la posición del click relativa a este widget
        click_pos = event.pos()
        
        # Verificar si el click está dentro del área del contenido principal
        main_container = self.findChild(QFrame)
        if main_container:
            container_rect = main_container.geometry()
            if not container_rect.contains(click_pos):
                self.close()
        else:
            # Si no se encuentra el contenedor, cerrar
            self.close()
        
    def keyPressEvent(self, event):
        """Cerrar con Escape"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)
        
    def focusOutEvent(self, event):
        """Cerrar cuando la ventana pierde el foco"""
        self.close()
        super().focusOutEvent(event)