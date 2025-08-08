from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QScrollArea, QFrame, QDialogButtonBox, QWidget, QGridLayout, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class CategoryConfigDialog(QDialog):
    def __init__(self, all_categories, hidden_categories, disabled_categories, parent=None):
        super().__init__(parent)
        self.all_categories = all_categories
        self.hidden_categories = hidden_categories.copy()
        self.disabled_categories = disabled_categories.copy()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Configurar Categorías")
        self.setModal(True)
        self.resize(800, 600)
        
        # Estilo general del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
                font-size: 9pt;
            }
            QLineEdit:focus {
                border-color: #8B5CF6;
            }
            QScrollArea {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                border-radius: 6px;
            }
            QScrollBar:vertical {
                background-color: #3c3c3c;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #666666;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777777;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)  # Reducido de 12 a 8
        layout.setContentsMargins(20, 15, 20, 20)  # Reducido margen superior
        
        # Instrucciones (sin título grande)
        instructions = QLabel("🔧 Personaliza la visibilidad y estado de las categorías:")
        instructions.setFont(QFont("Segoe UI", 10))  # Ligeramente más grande
        instructions.setStyleSheet("color: #cccccc; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Campo de filtro/búsqueda
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        
        filter_label = QLabel("🔍 Filtrar:")
        filter_label.setFont(QFont("Segoe UI", 9))
        filter_label.setStyleSheet("color: #ffffff;")
        filter_layout.addWidget(filter_label)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Buscar categorías...")
        self.filter_input.textChanged.connect(self.filter_categories)
        filter_layout.addWidget(self.filter_input)
        
        layout.addLayout(filter_layout)
        
        # Área de scroll para checkboxes con diseño en columnas
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        
        # Usar QGridLayout para organizar en columnas
        self.scroll_layout = QGridLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(6)
        self.scroll_layout.setContentsMargins(12, 8, 12, 8)
        
        self.hide_checkboxes = {}
        self.disable_checkboxes = {}
        self.category_widgets = {}  # Para poder filtrar
        
        # Crear todos los widgets de categorías
        self.create_category_widgets()
        
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.setStyleSheet("""
            QDialogButtonBox {
                background-color: transparent;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 9pt;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #777777;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QPushButton:default {
                background-color: #8B5CF6;
                border-color: #8B5CF6;
            }
            QPushButton:default:hover {
                background-color: #7C3AED;
            }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def create_category_widgets(self):
        """Crea todos los widgets de categorías"""
        categories = sorted(self.all_categories)
        columns = 3
        
        for i, category in enumerate(categories):
            row = i // columns
            col = i % columns
            
            category_container = self._create_compact_category_widget(category)
            self.category_widgets[category] = category_container
            self.scroll_layout.addWidget(category_container, row, col)
        
        # Añadir stretch para empujar todo hacia arriba
        self.scroll_layout.setRowStretch(len(categories) // columns + 1, 1)
    
    def filter_categories(self, text):
        """Filtra las categorías basado en el texto de búsqueda"""
        text = text.lower().strip()
        
        for category, widget in self.category_widgets.items():
            # Verificar si la categoría coincide con el filtro
            category_text = category.replace('_', ' ').lower()
            should_show = text == "" or text in category_text
            
            widget.setVisible(should_show)
    
    def _create_compact_category_widget(self, category):
        """Crea un widget compacto para una categoría individual"""
        # Contenedor más compacto para cada categoría
        category_container = QFrame()
        category_container.setFixedSize(240, 65)
        category_container.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 2px;
            }
            QFrame:hover {
                background-color: #404040;
                border-color: #666666;
            }
        """)
        category_layout = QVBoxLayout(category_container)
        category_layout.setSpacing(2)
        category_layout.setContentsMargins(6, 3, 6, 3)
        
        # Nombre de la categoría más compacto
        category_name = QLabel(category.replace('_', ' ').title())
        category_name.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        category_name.setStyleSheet("color: #ffffff; margin: 0px; padding: 0px;")
        category_name.setWordWrap(True)
        category_name.setMaximumHeight(16)
        category_layout.addWidget(category_name)
        
        # Layout horizontal para los checkboxes más compacto
        checkboxes_layout = QHBoxLayout()
        checkboxes_layout.setSpacing(6)
        checkboxes_layout.setContentsMargins(0, 0, 0, 0)
        
        # Contenedor para checkbox de ocultar
        hide_container = QVBoxLayout()
        hide_container.setSpacing(1)
        hide_container.setContentsMargins(0, 0, 0, 0)
        
        # Título pequeño para ocultar
        hide_label = QLabel("Ocultar")
        hide_label.setFont(QFont("Segoe UI", 7))
        hide_label.setStyleSheet("color: #ff6b6b; margin: 0px; padding: 0px;")
        hide_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hide_container.addWidget(hide_label)
        
        # Checkbox para ocultar
        hide_checkbox = QCheckBox("🙈")
        hide_checkbox.setToolTip("Ocultar categoría")
        hide_checkbox.setChecked(category in self.hidden_categories)
        hide_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ff6b6b;
                font-weight: 500;
                font-size: 8pt;
                spacing: 2px;
                margin: 0px;
                padding: 0px;
            }
            QCheckBox::indicator {
                width: 12px;
                height: 12px;
                border-radius: 2px;
                border: 2px solid #ff6b6b;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #ff6b6b;
                border-color: #ff6b6b;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #ff5252;
            }
            QCheckBox::indicator:hover {
                border-color: #ff5252;
            }
        """)
        self.hide_checkboxes[category] = hide_checkbox
        hide_container.addWidget(hide_checkbox)
        
        # Widget contenedor para ocultar
        hide_widget = QWidget()
        hide_widget.setLayout(hide_container)
        checkboxes_layout.addWidget(hide_widget)
        
        # Contenedor para checkbox de deshabilitar
        disable_container = QVBoxLayout()
        disable_container.setSpacing(1)
        disable_container.setContentsMargins(0, 0, 0, 0)
        
        # Título pequeño para deshabilitar
        disable_label = QLabel("Deshabilitar")
        disable_label.setFont(QFont("Segoe UI", 7))
        disable_label.setStyleSheet("color: #ffa726; margin: 0px; padding: 0px;")
        disable_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        disable_container.addWidget(disable_label)
        
        # Checkbox para deshabilitar
        disable_checkbox = QCheckBox("🚫")
        disable_checkbox.setToolTip("Deshabilitar categoría")
        disable_checkbox.setChecked(category in self.disabled_categories)
        disable_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffa726;
                font-weight: 500;
                font-size: 8pt;
                spacing: 2px;
                margin: 0px;
                padding: 0px;
            }
            QCheckBox::indicator {
                width: 12px;
                height: 12px;
                border-radius: 2px;
                border: 2px solid #ffa726;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #ffa726;
                border-color: #ffa726;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #ff9800;
            }
            QCheckBox::indicator:hover {
                border-color: #ff9800;
            }
        """)
        self.disable_checkboxes[category] = disable_checkbox
        disable_container.addWidget(disable_checkbox)
        
        # Widget contenedor para deshabilitar
        disable_widget = QWidget()
        disable_widget.setLayout(disable_container)
        checkboxes_layout.addWidget(disable_widget)
        
        checkboxes_layout.addStretch()
        category_layout.addLayout(checkboxes_layout)
        
        # Lógica: si está oculta, no puede estar deshabilitada
        def on_hide_changed(checked, disable_cb=disable_checkbox, disable_lbl=disable_label):
            if checked:
                disable_cb.setChecked(False)
                disable_cb.setEnabled(False)
                disable_lbl.setStyleSheet("color: #666666; margin: 0px; padding: 0px;")
                disable_cb.setStyleSheet(disable_cb.styleSheet() + """
                    QCheckBox {
                        color: #666666;
                    }
                    QCheckBox::indicator {
                        border-color: #666666;
                    }
                """)
            else:
                disable_cb.setEnabled(True)
                disable_lbl.setStyleSheet("color: #ffa726; margin: 0px; padding: 0px;")
                disable_cb.setStyleSheet("""
                    QCheckBox {
                        color: #ffa726;
                        font-weight: 500;
                        font-size: 8pt;
                        spacing: 2px;
                        margin: 0px;
                        padding: 0px;
                    }
                    QCheckBox::indicator {
                        width: 12px;
                        height: 12px;
                        border-radius: 2px;
                        border: 2px solid #ffa726;
                        background-color: transparent;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #ffa726;
                        border-color: #ffa726;
                    }
                    QCheckBox::indicator:checked:hover {
                        background-color: #ff9800;
                    }
                    QCheckBox::indicator:hover {
                        border-color: #ff9800;
                    }
                """)
        
        hide_checkbox.toggled.connect(on_hide_changed)
        
        # Aplicar estado inicial
        if hide_checkbox.isChecked():
            disable_checkbox.setEnabled(False)
            disable_label.setStyleSheet("color: #666666; margin: 0px; padding: 0px;")
            disable_checkbox.setStyleSheet(disable_checkbox.styleSheet() + """
                QCheckBox {
                    color: #666666;
                }
                QCheckBox::indicator {
                    border-color: #666666;
                }
            """)
        
        return category_container
    
    def get_hidden_categories(self):
        """Retorna el conjunto de categorías marcadas para ocultar"""
        hidden = set()
        for category, checkbox in self.hide_checkboxes.items():
            if checkbox.isChecked():
                hidden.add(category)
        return hidden
    
    def get_disabled_categories(self):
        """Retorna el conjunto de categorías marcadas para deshabilitar"""
        disabled = set()
        for category, checkbox in self.disable_checkboxes.items():
            if checkbox.isChecked():
                disabled.add(category)
        return disabled