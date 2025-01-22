import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from Scripts.FileHandler.Files import FileHandler
import os
import json
import time  # Ensure this import is at the top
from tkinter import Canvas, Menu  # Import standard tkinter Canvas and Menu

class Ui:
    def __init__(self, root, macro_recorder):
        self.root = root
        self.macro_recorder = macro_recorder
        self.file_handler = FileHandler()
        self.cache_file = "macro_cache.json"
        self.create_widgets()
        self.root.title("Macro Recorder")
        self.apply_dark_mode()
        self.root.after(100, self.load_cache)  # Delay loading cache to ensure macro_recorder is set
        self.drag_data = None  # Initialize drag_data

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self.root, border_width=0, fg_color="#2B2B2B")  # Set dark background
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

        self.record_button = ctk.CTkButton(self.main_frame, text="Record", command=self.toggle_record, fg_color="#3B3B3B", border_width=0)
        self.record_button.pack(pady=10)

        self.play_button = ctk.CTkButton(self.main_frame, text="Play", command=self.play_macro, fg_color="#3B3B3B", border_width=0)
        self.play_button.pack(pady=10)

        self.save_button = ctk.CTkButton(self.main_frame, text="Save", command=self.save_macro, fg_color="#3B3B3B", border_width=0)
        self.save_button.pack(pady=10)

        self.load_button = ctk.CTkButton(self.main_frame, text="Load", command=self.load_macro, fg_color="#3B3B3B", border_width=0)
        self.load_button.pack(pady=10)

        # Add Visual Editor button
        self.visual_editor_button = ctk.CTkButton(self.main_frame, text="Visual Editor", command=self.open_visual_editor, fg_color="#3B3B3B", border_width=0)
        self.visual_editor_button.pack(pady=10)

        self.macro_display = ctk.CTkTextbox(self.main_frame, height=100, width=80, state='disabled', font=("Courier", 10), fg_color="#2B2B2B", border_width=0)
        self.macro_display.pack(pady=10, fill=ctk.BOTH, expand=True)

        # Directly add visual_editor_canvas to main_frame
        self.visual_editor_canvas = Canvas(self.main_frame, bg="#2B2B2B", borderwidth=0, highlightthickness=0)  # Use standard tkinter Canvas
        self.visual_editor_canvas.pack(fill=ctk.BOTH, expand=True)
        self.visual_editor_canvas.bind("<Button-1>", self.add_block)
        self.visual_editor_canvas.bind("<Button-3>", self.show_context_menu)  # Bind right-click to show context menu
        self.visual_editor_canvas.bind("<ButtonPress-1>", self.on_node_press)
        self.visual_editor_canvas.bind("<B1-Motion>", self.on_node_motion)
        self.visual_editor_canvas.bind("<ButtonRelease-1>", self.on_node_release)

        # Create context menu for right-click actions
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Add Keystroke", command=self.add_keystroke)
        self.context_menu.add_command(label="Add Mouse Action", command=self.add_mouse_action)

        # Only call render_macro if macro_recorder is set
        if self.macro_recorder:
            self.render_macro()

    def apply_dark_mode(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        # Removed CTkStyle usage

    def toggle_record(self):
        if self.macro_recorder:
            self.macro_recorder.toggle_record()
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

    def open_visual_editor(self):
        # Implement the functionality to open the visual editor
        visual_editor_window = ctk.CTkToplevel(self.root)
        visual_editor_window.title("Visual Editor")
        visual_editor_window.geometry("600x400")
        visual_editor_window.configure(bg="#2B2B2B")

        # Add widgets to the visual editor window
        self.editor_canvas = Canvas(visual_editor_window, bg="#2B2B2B", borderwidth=0, highlightthickness=0)  # Use standard tkinter Canvas
        self.editor_canvas.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Bind events or add controls as needed
        self.editor_canvas.bind("<Button-1>", self.add_block)
        self.editor_canvas.bind("<Button-3>", self.show_context_menu)  # Bind right-click to show context menu
        self.editor_canvas.bind("<ButtonPress-1>", self.on_node_press)
        self.editor_canvas.bind("<B1-Motion>", self.on_node_motion)
        self.editor_canvas.bind("<ButtonRelease-1>", self.on_node_release)

    def add_block(self, event):
        if self.macro_recorder:
            block_type = "mouse" if event.y % 2 == 0 else "key"
            action = (block_type, event.x, event.y, time.time())  # Ensure 'time' is defined
            self.macro_recorder.macro.append(action)
            self.render_macro()
            self.update_macro_display(self.macro_recorder.macro)  # Update text output
            self.save_cache()

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def add_keystroke(self):
        # Add a keystroke action at the current mouse position
        x, y = self.visual_editor_canvas.winfo_pointerxy()
        action = ("key", "a", "down", time.time())  # Example keystroke action
        self.macro_recorder.macro.append(action)
        self.render_macro()
        self.update_macro_display(self.macro_recorder.macro)
        self.save_cache()

    def add_mouse_action(self):
        # Add a mouse action at the current mouse position
        x, y = self.visual_editor_canvas.winfo_pointerxy()
        action = ("mouse", int(x), int(y), time.time())  # Ensure coordinates are integers
        self.macro_recorder.macro.append(action)
        self.render_macro()
        self.update_macro_display(self.macro_recorder.macro)
        self.save_cache()

    def on_node_press(self, event):
        # Store the item and its initial position
        items = self.visual_editor_canvas.find_closest(event.x, event.y)
        if items:
            self.drag_data = {"item": items[0], "x": event.x, "y": event.y}

    def on_node_motion(self, event):
        if self.drag_data:
            # Move the item by the distance of the mouse movement
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.visual_editor_canvas.move(self.drag_data["item"], dx, dy)
            if hasattr(self, 'editor_canvas'):
                self.editor_canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_node_release(self, event):
        if self.drag_data:
            # Update the macro recorder with the new position
            item = self.drag_data["item"]
            x, y = self.visual_editor_canvas.coords(item)[:2]
            for action in self.macro_recorder.macro:
                if action[0] == 'mouse' and (action[1], action[2]) == (self.drag_data["x"], self.drag_data["y"]):
                    action = (action[0], int(x), int(y), action[3])  # Ensure coordinates are integers
                    break
            self.render_macro()
            self.update_macro_display(self.macro_recorder.macro)
            self.save_cache()
            self.drag_data = None

    def render_macro(self):
        if not self.macro_recorder:
            return  # Prevent AttributeError if macro_recorder is None
        self.visual_editor_canvas.delete("all")
        if hasattr(self, 'editor_canvas'):
            self.editor_canvas.delete("all")
        last_pos = None
        for i, action in enumerate(self.macro_recorder.macro):
            if action[0] == 'mouse':
                if last_pos:
                    self.visual_editor_canvas.create_line(last_pos[0], last_pos[1], action[1], action[2], fill="blue", width=2)
                    if hasattr(self, 'editor_canvas'):
                        self.editor_canvas.create_line(last_pos[0], last_pos[1], action[1], action[2], fill="blue", width=2)
                self.visual_editor_canvas.create_oval(action[1] - 5, action[2] - 5, action[1] + 5, action[2] + 5, fill="blue", tags="block")
                if hasattr(self, 'editor_canvas'):
                    self.editor_canvas.create_oval(action[1] - 5, action[2] - 5, action[1] + 5, action[2] + 5, fill="blue", tags="block")
                last_pos = (action[1], action[2])
                # Display action order and delay
                if i > 0:
                    delay = action[3] - self.macro_recorder.macro[i-1][3]
                    self.visual_editor_canvas.create_text(action[1], action[2] - 10, text=f"{i+1} ({delay:.2f}s)", fill="white")
                    if hasattr(self, 'editor_canvas'):
                        self.editor_canvas.create_text(action[1], action[2] - 10, text=f"{i+1} ({delay:.2f}s)", fill="white")
            elif action[0] == 'key':
                self.visual_editor_canvas.create_rectangle(50, 50, 150, 100, fill="green", tags="block")
                self.visual_editor_canvas.create_text(100, 75, text=f"Key: {action[1]}", fill="white")
                if hasattr(self, 'editor_canvas'):
                    self.editor_canvas.create_rectangle(50, 50, 150, 100, fill="green", tags="block")
                    self.editor_canvas.create_text(100, 75, text=f"Key: {action[1]}", fill="white")
                # Display action order and delay
                if i > 0:
                    delay = action[3] - self.macro_recorder.macro[i-1][3]
                    self.visual_editor_canvas.create_text(100, 40, text=f"{i+1} ({delay:.2f}s)", fill="white")
                    if hasattr(self, 'editor_canvas'):
                        self.editor_canvas.create_text(100, 40, text=f"{i+1} ({delay:.2f}s)", fill="white")
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
        self.macro_display.configure(state='normal')
        self.macro_display.delete("1.0", ctk.END)
        for action in macro:
            if action[0] == 'mouse':
                self.macro_display.insert(ctk.END, f"Mouse: Move to ({action[1]}, {action[2]}) at {action[3]:.2f}\n")
            elif action[0] == 'key':
                self.macro_display.insert(ctk.END, f"Key: {action[1]} {action[2]} at {action[3]:.2f}\n")
        self.macro_display.configure(state='disabled')

    def ask_open_file(self):
        return self.file_handler.ask_open_file()

    def show_error(self, message):
        self.file_handler.show_error(message)

    def save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.macro_recorder.macro, f)
