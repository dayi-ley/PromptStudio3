from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QSplitter,
    QScrollArea, QFrame, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QScreen
from .category_panel import CategoryPanel
from .suggestion_panel import SuggestionPanel
from logic.prompt_generator import PromptGenerator
from logic.suggestion_engine import SuggestionEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.prompt_generator = PromptGenerator()
        self.suggestion_engine = SuggestionEngine()
        self.init_ui()
        self.center_window()
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, 30)
        
    def init_ui(self):
        self.setWindowTitle("Generador de Prompts IA")
        self.setFixedSize(1250, 600)
        self.center_window()
        
        # Estilo general de la ventana (tema oscuro)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Panel de categorías (parte superior)
        self.category_panel = CategoryPanel(self.prompt_generator)
        main_layout.addWidget(self.category_panel)
        
        # Splitter para dividir sugerencias y prompt
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel de sugerencias (izquierda)
        self.suggestion_panel = SuggestionPanel(self.prompt_generator)
        splitter.addWidget(self.suggestion_panel)
        
        # Panel de prompt generado (derecha)
        prompt_section = QFrame()
        prompt_section.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 6px;
            }
        """)
        prompt_layout = QVBoxLayout(prompt_section)
        prompt_layout.setSpacing(4)
        prompt_layout.setContentsMargins(10, 6, 10, 8)
        
        # Título del prompt
        prompt_title = QLabel("Prompt Generado")
        prompt_title.setFont(QFont("Segoe UI", 9))
        prompt_title.setStyleSheet("color: #cccccc; margin-bottom: 2px;")
        prompt_layout.addWidget(prompt_title)
        
        # Área de texto del prompt
        self.prompt_display = QTextEdit()
        self.prompt_display.setPlaceholderText("El prompt generado aparecerá aquí...")
        self.prompt_display.setStyleSheet("""
            QTextEdit {
                background-color: #505050;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                line-height: 1.4;
            }
        """)
        prompt_layout.addWidget(self.prompt_display)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        
        # Botón generar
        generate_btn = QPushButton("Generar Prompt")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #00cc88;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 8pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b377;
            }
            QPushButton:pressed {
                background-color: #009966;
            }
        """)
        generate_btn.clicked.connect(self.generate_prompt)
        button_layout.addWidget(generate_btn)
        
        # Botón copiar
        copy_btn = QPushButton("Copiar")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 8pt;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        copy_btn.clicked.connect(self.copy_prompt)
        button_layout.addWidget(copy_btn)
        
        # Botón limpiar
        clear_btn = QPushButton("Limpiar Todo")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 8pt;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_btn)
        
        prompt_layout.addLayout(button_layout)
        splitter.addWidget(prompt_section)
        
        # Configurar proporciones del splitter
        splitter.setSizes([400, 500])
        main_layout.addWidget(splitter)
        
        # Configurar proporciones del layout principal
        main_layout.setStretch(0, 0)  # Categorías fijas
        main_layout.setStretch(1, 1)  # Contenido se expande
        
        # CONEXIONES CORREGIDAS
        self.category_panel.category_changed.connect(self.on_category_changed)
        # Conectar la nueva señal de sugerencias
        self.category_panel.suggestion_requested.connect(self.suggestion_panel.update_suggestions_tree)
        # Conectar aplicación de sugerencias
        self.suggestion_panel.suggestion_applied.connect(self.on_suggestion_applied)
        # NUEVA CONEXIÓN: Actualizar prompt cuando cambie el contexto
        self.suggestion_panel.prompt_updated.connect(self.generate_prompt)
    def on_category_changed(self, category, value):
        """Se ejecuta cuando cambia el valor de una categoría"""
        # Solo generar el prompt, las sugerencias se manejan por separado
        self.generate_prompt()
        
    def generate_prompt(self):
        """Genera y muestra el prompt completo"""
        prompt = self.prompt_generator.generate_prompt()
        self.prompt_display.setPlainText(prompt)
        
    def copy_prompt(self):
        """Copia el prompt al portapapeles"""
        prompt = self.prompt_display.toPlainText()
        if prompt:
            clipboard = QApplication.clipboard()
            clipboard.setText(prompt)
            QMessageBox.information(self, "Éxito", "Prompt copiado al portapapeles")
        else:
            QMessageBox.warning(self, "Advertencia", "No hay prompt para copiar")
            
    def clear_all(self):
        """Limpia todos los valores"""
        self.prompt_generator.clear_all()
        self.category_panel.refresh_all()
        self.suggestion_panel.clear_suggestions()
        self.prompt_display.clear()
        
    def on_suggestion_applied(self, category, value):
        """Maneja cuando se aplica una sugerencia desde el árbol"""
        # Activar la categoría si no está seleccionada
        if category not in self.category_panel.selected_categories:
            # Simular click en la categoría
            self.category_panel.on_category_click(category)
            
        # Establecer el valor en el input
        if category in self.category_panel.category_inputs:
            line_edit = self.category_panel.category_inputs[category]['line_edit']
            line_edit.setText(value)
            
        # Actualizar el generador
        self.prompt_generator.set_category_value(category, value)
        
        # Actualizar el prompt
        self.generate_prompt()
        
        # NUEVA LÍNEA: Mantener las sugerencias visibles
        # Buscar la categoría original que generó las sugerencias
        original_category = None
        original_value = None
        
        # Buscar en vestuario_general primero (ya que es la categoría principal)
        if 'vestuario_general' in self.category_panel.category_inputs:
            vestuario_general_input = self.category_panel.category_inputs['vestuario_general']['line_edit']
            if vestuario_general_input.text().strip():
                original_category = 'vestuario_general'
                original_value = vestuario_general_input.text().strip()
        
        # Si no hay vestuario_general, buscar en otras categorías de vestuario
        if not original_category:
            for cat in ['vestuario_superior', 'vestuario_inferior', 'vestuario_accesorios']:
                if cat in self.category_panel.category_inputs:
                    cat_input = self.category_panel.category_inputs[cat]['line_edit']
                    if cat_input.text().strip() and cat != category:  # No usar la categoría que acabamos de cambiar
                        original_category = cat
                        original_value = cat_input.text().strip()
                        break
        
        # Si encontramos una categoría original, actualizar las sugerencias
        if original_category and original_value:
            self.suggestion_panel.update_suggestions_tree(original_category, original_value)