import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from Scripts.Ui.Ui import Ui
from Scripts.Macro.MacroRecorder import MacroRecorder
from Scripts.FileHandler.Files import FileHandler

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    file_handler = FileHandler()
    ui = Ui(root, None)  # Initialize UI without MacroRecorder first
    macro_recorder = MacroRecorder(ui)
    ui.macro_recorder = macro_recorder  # Set the MacroRecorder instance in UI
    # After assigning macro_recorder, explicitly call methods that depend on it if necessary
    ui.render_macro()  # Ensure the UI updates after macro_recorder is set
    root.mainloop()
