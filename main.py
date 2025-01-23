from PyQt5.QtWidgets import QApplication
from Scripts.Ui.Ui import Ui
from Scripts.Macro.MacroRecorder import MacroRecorder

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui = Ui(None)  # Initialize UI without MacroRecorder first
    macro_recorder = MacroRecorder(ui)
    ui.macro_recorder = macro_recorder  # Set the MacroRecorder instance in UI
    ui.render_macro()  # Ensure the UI updates after macro_recorder is set
    ui.show()
    sys.exit(app.exec_())
