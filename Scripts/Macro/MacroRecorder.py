import pyautogui
import time
import keyboard
import threading
import json
from PyQt5.QtCore import QTimer

class MacroRecorder:
    def __init__(self, ui):
        self.ui = ui
        self.recording = False
        self.macro = []
        self.playing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.record_step)
        pyautogui.MINIMUM_DURATION = 0  # Remove minimum sleep time
        pyautogui.PAUSE = 0  # Remove delays between actions

    def toggle_record(self):
        self.recording = not self.recording
        if self.recording:
            self.ui.record_button.setText("Stop")
            self.start_recording()
        else:
            self.ui.record_button.setText("Record")
            keyboard.unhook_all()
            self.ui.save_cache()

    def start_recording(self):
        self.macro = []
        self.ui.update_macro_display(self.macro)
        keyboard.hook(self.record_key)
        self.timer.start(10)  # Schedule record_step every 10 ms

    def record_step(self):
        if self.recording:
            x, y = pyautogui.position()
            if not self.macro or (self.macro[-1][1], self.macro[-1][2]) != (x, y):
                self.macro.append(('mouse', x, y, time.time()))
                self.ui.update_macro_display(self.macro)

    def record_key(self, event):
        if self.recording:
            self.macro.append(('key', event.name, event.event_type, time.time()))
            self.ui.update_macro_display(self.macro)

    def play_macro(self):
        if not self.macro:
            self.ui.show_warning("No macro recorded!")
            return
        self.playing = True
        keyboard.on_press_key("esc", self.stop_playback)
        threading.Thread(target=self._play_macro_thread).start()

    def _play_macro_thread(self):
        try:
            start_time = self.macro[0][3]
            for i, action in enumerate(self.macro):
                if not self.playing:
                    break
                
                current_time = action[3]
                # Calculate exact delay between actions
                if i > 0:
                    delay = current_time - self.macro[i-1][3]
                    if delay > 0:
                        time.sleep(delay)

                if action[0] == 'mouse':
                    _, x, y, _ = action
                    pyautogui.moveTo(x, y)
                elif action[0] == 'key':
                    _, key, event_type, _ = action
                    if event_type == 'down':
                        keyboard.press(key)
                    elif event_type == 'up':
                        keyboard.release(key)
        finally:
            self.playing = False

    def stop_playback(self, event=None):
        self.playing = False
        keyboard.unhook_key("esc")

    def optimize_macro(self):
        """Remove redundant mouse movements and convert to relative timestamps"""
        if not self.macro:
            return []
        
        optimized = []
        base_time = self.macro[0][3]
        last_pos = None
        
        for action in self.macro:
            if action[0] == 'mouse':
                # Only save position if it's different from last position
                if last_pos != (action[1], action[2]):
                    optimized.append(('mouse', action[1], action[2], action[3] - base_time))
                    last_pos = (action[1], action[2])
            elif action[0] == 'key':
                optimized.append(('key', action[1], action[2], action[3] - base_time))
        
        return optimized

    def save_macro(self):
        file_path = self.ui.ask_save_file()
        if file_path:
            optimized_macro = self.optimize_macro()
            try:
                with open(file_path, "w") as f:
                    json.dump({
                        'version': 1,
                        'timestamp': time.time(),
                        'actions': optimized_macro
                    }, f)
                self.ui.show_info("Macro saved successfully!")
                self.ui.save_cache()
            except Exception as e:
                self.ui.show_error(f"Error saving macro: {str(e)}")

    def load_macro(self):
        file_path = self.ui.ask_open_file()
        if file_path:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    if data.get('version') == 1:
                        actions = data['actions']
                        # Convert relative timestamps back to absolute
                        base_time = time.time()
                        self.macro = []
                        for action in actions:
                            if action[0] == 'mouse':
                                self.macro.append(('mouse', int(action[1]), int(action[2]), base_time + float(action[3])))
                            elif action[0] == 'key':
                                self.macro.append(('key', action[1], action[2], base_time + float(action[3])))
                        self.ui.update_macro_display(self.macro)
                        self.ui.show_info("Macro loaded successfully!")
                        self.ui.save_cache()
                    else:
                        self.load_legacy_format(file_path)
            except json.JSONDecodeError:
                # Try loading as legacy format
                self.load_legacy_format(file_path)
            except Exception as e:
                self.ui.show_error(f"Error loading macro: {str(e)}")

    def load_legacy_format(self, file_path):
        """Handle loading of old format files"""
        try:
            with open(file_path, "r") as f:
                self.macro = []
                base_time = time.time()
                for line in f:
                    parts = line.strip().split(',')
                    if parts[0] == 'mouse':
                        self.macro.append(('mouse', int(parts[1]), int(parts[2]), base_time + float(parts[3])))
                    elif parts[0] == 'key':
                        self.macro.append(('key', parts[1], parts[2], base_time + float(parts[3])))
            self.ui.update_macro_display(self.macro)
            self.ui.show_info("Macro loaded successfully (legacy format)!")
            self.ui.save_cache()
        except Exception as e:
            self.ui.show_error(f"Error loading legacy format: {str(e)}")
