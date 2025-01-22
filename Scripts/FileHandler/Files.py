from tkinter import filedialog, messagebox

class FileHandler:
    @staticmethod
    def ask_save_file():
        return filedialog.asksaveasfilename(initialdir=".", defaultextension=".MacroScript", filetypes=[("Macro Script", "*.MacroScript")])

    @staticmethod
    def ask_open_file():
        return filedialog.askopenfilename(initialdir=".", defaultextension=".MacroScript", filetypes=[("Macro Script", "*.MacroScript")])

    @staticmethod
    def show_info(message):
        messagebox.showinfo("Info", message)

    @staticmethod
    def show_warning(message):
        messagebox.showwarning("Warning", message)

    @staticmethod
    def show_error(message):
        messagebox.showerror("Error", message)
