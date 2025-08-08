from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QDialog
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
        self.category_inputs = {}
        
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
            self.category_changed.emit(category, 'selected')
        else:
            self.selected_categories.discard(category)
            self.category_changed.emit(category, 'deselected')
    
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