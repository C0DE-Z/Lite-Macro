from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QMenu, QAction, QGraphicsOpacityEffect, QFileDialog, QMessageBox, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, Qt, QPointF
from PyQt5.QtGui import QColor, QCursor, QPen, QBrush, QWheelEvent, QPainter  # Import QPainter
import os
import json
import time

class DraggableEllipseItem(QGraphicsEllipseItem):
    def __init__(self, ui, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setBrush(QBrush(QColor("blue")))
        self.setPen(QPen(QColor("white"), 2))
        self.old_x, self.old_y = 0, 0

    def mousePressEvent(self, event):
        self.old_x, self.old_y = self.pos().x(), self.pos().y()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.update_position()

    def update_position(self):
        x, y = self.pos().x(), self.pos().y()
        for action in self.ui.macro_recorder.macro:
            if action[0] == 'mouse' and (action[1], action[2]) == [self.old_x, self.old_y]:
                action[1], action[2] = int(x), int(y)
                break
        self.old_x, self.old_y = int(x), int(y)
        self.ui.render_macro()

class Ui(QMainWindow):
    def __init__(self, macro_recorder):
        super().__init__()
        self.macro_recorder = macro_recorder
        self.cache_file = "macro_cache.json"
        self.init_ui()
        self.setWindowTitle("Macro Recorder")
        self.load_cache()
        self.drag_data = None  # Initialize drag_data
        self.connecting_line = None  # Initialize connecting line

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QPushButton {
                background-color: #3B3B3B;
                color: white;
                border: 1px solid #3B3B3B;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #505050;
            }
            QPushButton:pressed {
                background-color: #2B2B2B;
                border: 1px solid #2B2B2B;
            }
            QTextEdit {
                background-color: #2B2B2B;
                color: white;
                font-family: Courier;
                border: 1px solid #3B3B3B;
                border-radius: 5px;
            }
            QMenu {
                background-color: #2B2B2B;
                color: white;
                border: 1px solid #3B3B3B;
            }
            QMenu::item:selected {
                background-color: #505050;
            }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.toggle_record)
        self.layout.addWidget(self.record_button)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_macro)
        self.layout.addWidget(self.play_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_macro)
        self.layout.addWidget(self.save_button)

        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_macro)
        self.layout.addWidget(self.load_button)

        self.macro_display = QTextEdit()
        self.macro_display.setReadOnly(True)
        self.layout.addWidget(self.macro_display)

        self.visual_editor_scene = QGraphicsScene()
        self.visual_editor_view = QGraphicsView(self.visual_editor_scene)
        self.visual_editor_view.setStyleSheet("background-color: #2B2B2B;")
        self.visual_editor_view.setRenderHint(QPainter.Antialiasing)
        self.visual_editor_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.visual_editor_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.layout.addWidget(self.visual_editor_view)

        self.context_menu = QMenu(self)
        self.add_keystroke_action = QAction("Add Keystroke", self)
        self.add_keystroke_action.triggered.connect(self.add_keystroke_action_triggered)
        self.context_menu.addAction(self.add_keystroke_action)

        self.add_mouse_action = QAction("Add Mouse Action", self)
        self.add_mouse_action.triggered.connect(self.add_mouse_action_triggered)
        self.context_menu.addAction(self.add_mouse_action)

        self.remove_node_action = QAction("Remove Node", self)
        self.remove_node_action.triggered.connect(self.remove_node)
        self.context_menu.addAction(self.remove_node_action)

        self.visual_editor_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.visual_editor_view.customContextMenuRequested.connect(self.show_context_menu)

        self.visual_editor_view.setInteractive(True)
        self.visual_editor_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.visual_editor_view.setMouseTracking(True)
        self.visual_editor_view.setRenderHint(QPainter.Antialiasing)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.ControlModifier:
            factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
            self.visual_editor_view.scale(factor, factor)
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.visual_editor_scene.selectedItems():
                if isinstance(item, DraggableEllipseItem):
                    self.visual_editor_scene.removeItem(item)
                    self.macro_recorder.macro = [action for action in self.macro_recorder.macro if not (action[1] == item.old_x and action[2] == item.old_y)]
            self.render_macro()

    def toggle_record(self):
        if self.macro_recorder:
            self.macro_recorder.toggle_record()
            self.render_macro()  # Ensure the visual editor updates when recording stops
            self.save_cache()

    def play_macro(self):
        if self.macro_recorder:
            self.macro_recorder.play_macro()

    def save_macro(self):
        if self.macro_recorder:
            self.macro_recorder.save_macro()
            self.save_cache()

    def load_macro(self):
        if self.macro_recorder:
            self.macro_recorder.load_macro()
            self.save_cache()

    def add_keystroke_action_triggered(self):
        # Add a keystroke action at the current mouse position
        x, y = self.visual_editor_view.mapFromGlobal(QCursor.pos()).x(), self.visual_editor_view.mapFromGlobal(QCursor.pos()).y()
        action = ["key", "a", "down", time.time()]  # Example keystroke action
        self.macro_recorder.macro.append(action)
        self.render_macro()
        self.update_macro_display(self.macro_recorder.macro)
        self.save_cache()

    def add_mouse_action_triggered(self):
        # Add a mouse action at the current mouse position
        x, y = self.visual_editor_view.mapFromGlobal(QCursor.pos()).x(), self.visual_editor_view.mapFromGlobal(QCursor.pos()).y()
        action = ["mouse", int(x), int(y), time.time()]  # Ensure coordinates are integers
        self.macro_recorder.macro.append(action)
        self.render_macro()
        self.update_macro_display(self.macro_recorder.macro)
        self.save_cache()

    def remove_node(self):
        if self.drag_data:
            item = self.drag_data["item"]
            x, y = item.pos().x(), item.pos().y()
            self.macro_recorder.macro = [action for action in self.macro_recorder.macro if not (action[1] == int(x) and action[2] == int(y))]
            self.render_macro()
            self.update_macro_display(self.macro_recorder.macro)
            self.save_cache()
            self.drag_data = None

    def show_context_menu(self, pos):
        self.context_menu.exec_(self.visual_editor_view.mapToGlobal(pos))

    def render_macro(self):
        if not self.macro_recorder:
            return  # Prevent AttributeError if macro_recorder is None
        self.visual_editor_scene.clear()
        last_pos = None
        for i, action in enumerate(self.macro_recorder.macro):
            if action[0] == 'mouse':
                if last_pos:
                    line = QGraphicsLineItem(last_pos[0], last_pos[1], action[1], action[2])
                    line.setPen(QPen(QColor("blue"), 2))
                    self.visual_editor_scene.addItem(line)
                oval = DraggableEllipseItem(self, action[1] - 5, action[2] - 5, 10, 10)  # Pass the Ui instance
                oval.old_x, oval.old_y = action[1], action[2]
                self.visual_editor_scene.addItem(oval)
                last_pos = (action[1], action[2])
                # Display action order and delay
                if i > 0:
                    delay = action[3] - self.macro_recorder.macro[i-1][3]
                    text = QGraphicsTextItem(f"{i+1} ({delay:.2f}s)")
                    text.setDefaultTextColor(QColor("white"))
                    text.setPos(action[1], action[2] - 15)
                    self.visual_editor_scene.addItem(text)
            elif action[0] == 'key':
                rect = QGraphicsEllipseItem(50, 50, 100, 50)
                rect.setBrush(QBrush(QColor("green")))
                rect.setPen(QPen(QColor("white"), 2))
                self.visual_editor_scene.addItem(rect)
                text = QGraphicsTextItem(f"Key: {action[1]}")
                text.setDefaultTextColor(QColor("white"))
                text.setPos(75, 65)
                self.visual_editor_scene.addItem(text)
                # Display action order and delay
                if i > 0:
                    delay = action[3] - self.macro_recorder.macro[i-1][3]
                    text = QGraphicsTextItem(f"{i+1} ({delay:.2f}s)")
                    text.setDefaultTextColor(QColor("white"))
                    text.setPos(75, 40)
                    self.visual_editor_scene.addItem(text)
        self.update_macro_display(self.macro_recorder.macro)  # Update text output
        with open(self.cache_file, "w") as f:
            json.dump(self.macro_recorder.macro, f)

    def load_cache(self):
        if os.path.exists(self.cache_file) and self.macro_recorder:
            with open(self.cache_file, "r") as f:
                self.macro_recorder.macro = json.load(f)
            self.update_macro_display(self.macro_recorder.macro)

    def update_macro_display(self, macro):
        if not self.macro_recorder:
            return  # Prevent AttributeError if macro_recorder is None
        self.macro_display.setPlainText("")
        for action in macro:
            if action[0] == 'mouse':
                self.macro_display.append(f"Mouse: Move to ({action[1]}, {action[2]}) at {action[3]:.2f}")
            elif action[0] == 'key':
                self.macro_display.append(f"Key: {action[1]} {action[2]} at {action[3]:.2f}")

    def ask_open_file(self):
        return QFileDialog.getOpenFileName(self, "Open Macro Script", ".", "Macro Script (*.MacroScript)")[0]

    def ask_save_file(self):
        return QFileDialog.getSaveFileName(self, "Save Macro Script", ".", "Macro Script (*.MacroScript)")[0]

    def show_info(self, message):
        QMessageBox.information(self, "Info", message)

    def show_warning(self, message):
        QMessageBox.warning(self, "Warning", message)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.macro_recorder.macro, f)
