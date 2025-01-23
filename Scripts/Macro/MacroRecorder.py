import pyautogui
import time
import keyboard
import mouse
import threading
import json
from PyQt5.QtCore import QTimer, QMetaObject, Qt, Q_ARG, QVariant
import win32gui  # Add this import
import win32con
from contextlib import contextmanager

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
        self.last_window = None
        self.action_retry_count = 3  # Number of retries for failed actions
        self.error_tolerance = 2  # Reduced for faster operation
        pyautogui.FAILSAFE = True
        # Only keep failsafe
        pyautogui.FAILSAFE = True
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.PAUSE = 0

    @contextmanager
    def error_handler(self):
        try:
            yield
        except pyautogui.FailSafeException:
            self.playing = False
            self.ui.show_error("Macro stopped - failsafe triggered (mouse to corner)")
        except Exception as e:
            self.ui.show_warning(f"Action error: {str(e)}")

    def verify_mouse_position(self, target_x, target_y):
        """Verify if mouse reached the target position within tolerance"""
        current_x, current_y = pyautogui.position()
        return (abs(current_x - target_x) <= self.error_tolerance and 
                abs(current_y - target_y) <= self.error_tolerance)

    def retry_action(self, action_func, verify_func=None, retries=None):
        """Retry an action until it succeeds or runs out of retries"""
        retries = retries or self.action_retry_count
        for _ in range(retries):
            with self.error_handler():
                action_func()
                if verify_func is None or verify_func():
                    return True
                time.sleep(0.1)  # Small delay between retries
        return False

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
        self.update_macro_display_safe(self.macro)
        keyboard.hook(self.record_key)
        self.timer.start(10)  # Schedule record_step every 10 ms

    def record_step(self):
        if self.recording:
            # Get current window info
            current_window = win32gui.GetForegroundWindow()
            current_title = win32gui.GetWindowText(current_window)
            
            # Skip recording if it's our own UI
            if "Macro Recorder" in current_title:
                return
                
            # Record window focus change
            if self.last_window != current_window:
                self.last_window = current_window
                self.macro.append(('window_focus', current_title, None, time.time()))
                self.update_macro_display_safe(self.macro)
            
            # Record mouse position and clicks
            x, y = pyautogui.position()
            left_pressed = mouse.is_pressed(button='left')
            right_pressed = mouse.is_pressed(button='right')
            middle_pressed = mouse.is_pressed(button='middle')
            
            # Always record position changes and clicks
            should_record = (
                not self.macro or
                (self.macro[-1][1], self.macro[-1][2]) != (x, y) or
                left_pressed or right_pressed or middle_pressed
            )
            
            if should_record:
                action_type = 'mouse'
                if left_pressed:
                    action_type = 'left_click'
                elif right_pressed:
                    action_type = 'right_click'
                elif middle_pressed:
                    action_type = 'middle_click'
                
                self.macro.append((action_type, x, y, time.time()))
                self.update_macro_display_safe(self.macro)

    def record_key(self, event):
        if self.recording:
            self.macro.append(('key', event.name, event.event_type, time.time()))
            self.update_macro_display_safe(self.macro)

    def play_macro(self, loops=1):
        if not self.macro:
            self.ui.show_warning("No macro recorded!")
            return
        self.playing = True
        keyboard.on_press_key("esc", self.stop_playback)
        threading.Thread(target=self._play_macro_thread, args=(loops,)).start()

    def _play_macro_thread(self, loops=1):
        try:
            for loop in range(loops):
                if not self.playing:
                    break

                # Store the start time of this loop iteration
                start_time = time.time()
                first_action_time = self.macro[0][3]
                last_action_time = first_action_time

                for i, action in enumerate(self.macro):
                    if not self.playing:
                        break

                    # Calculate and wait for the exact recorded delay
                    if i > 0:
                        recorded_delay = action[3] - last_action_time
                        time.sleep(max(0, recorded_delay))
                    
                    last_action_time = action[3]

                    # Execute the action
                    action_type = action[0]
                    if action_type == 'window_focus':
                        try:
                            window = win32gui.FindWindow(None, action[1])
                            if window:
                                win32gui.SetForegroundWindow(window)
                        except Exception:
                            pass

                    elif action_type in ('mouse', 'left_click', 'right_click', 'middle_click'):
                        x, y = action[1], action[2]
                        pyautogui.moveTo(x, y)
                        if action_type != 'mouse':
                            pyautogui.click(button=action_type.split('_')[0])

                    elif action_type == 'key':
                        key, event_type = action[1], action[2]
                        if event_type == 'down':
                            keyboard.press(key)
                        else:
                            keyboard.release(key)

                # Wait before starting next loop to maintain timing
                if loop < loops - 1:
                    total_macro_time = self.macro[-1][3] - first_action_time
                    elapsed = time.time() - start_time
                    if elapsed < total_macro_time:
                        time.sleep(total_macro_time - elapsed)

        except Exception as e:
            self.ui.show_error(f"Macro playback error: {str(e)}")
        finally:
            self.playing = False
            keyboard.unhook_all()
            if self.playing:
                self.ui.show_info(f"Macro playback completed ({loops} loops)")

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
        last_window = None
        
        for action in self.macro:
            if action[0] == 'window_focus':
                if last_window != action[1]:  # Only record unique window changes
                    optimized.append(('window_focus', action[1], None, action[3] - base_time))
                    last_window = action[1]
            elif action[0] == 'mouse':
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
                            if action[0] == 'window_focus':
                                self.macro.append(('window_focus', action[1], None, base_time + float(action[3])))
                            elif action[0] == 'mouse':
                                self.macro.append(('mouse', int(action[1]), int(action[2]), base_time + float(action[3])))
                            elif action[0] == 'key':
                                self.macro.append(('key', action[1], action[2], base_time + float(action[3])))
                        self.update_macro_display_safe(self.macro)
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
                    if parts[0] == 'window_focus':
                        self.macro.append(('window_focus', parts[1], None, base_time + float(parts[3])))
                    elif parts[0] == 'mouse':
                        self.macro.append(('mouse', int(parts[1]), int(parts[2]), base_time + float(parts[3])))
                    elif parts[0] == 'key':
                        self.macro.append(('key', parts[1], parts[2], base_time + float(parts[3])))
            self.update_macro_display_safe(self.macro)
            self.ui.show_info("Macro loaded successfully (legacy format)!")
            self.ui.save_cache()
        except Exception as e:
            self.ui.show_error(f"Error loading legacy format: {str(e)}")

    def update_macro_display_safe(self, macro):
        QMetaObject.invokeMethod(
            self.ui, 
            "update_macro_display",
            Qt.QueuedConnection,
            Q_ARG(list, macro)
        )
