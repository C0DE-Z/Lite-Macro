<div align="center">
  <img src="./ezmacro.png" alt="Title" width="800"/>
</div>

# EzMacro

EzMacro is a macro recording and playback tool that allows users to automate repetitive tasks by recording mouse movements and keystrokes. The tool provides a visual editor for editing recorded macros and supports saving and loading macros from files.

## Features

- Record mouse movements and keystrokes
- Play back recorded macros
- Visual editor for editing macros
- Save and load macros from files
- Optimized macro playback with relative timestamps

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/EzMacro.git
    cd EzMacro
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the application**:
    ```sh
    python main.py
    ```

## Usage

### Recording a Macro

1. Click the "Record" button to start recording.
2. Perform the actions you want to record (mouse movements, clicks, and keystrokes).
3. Click the "Stop" button to stop recording.

### Playing a Macro

1. Click the "Play" button to play back the recorded macro.
2. Press the "Esc" key to stop playback at any time.

### Saving a Macro

1. Click the "Save" button to save the recorded macro to a file.
2. Choose a location and filename for the macro file.

### Loading a Macro

1. Click the "Load" button to load a macro from a file.
2. Select the macro file to load.

### Editing a Macro

1. Use the visual editor to view and edit the recorded macro.
2. Right-click on a node to remove it.
3. Drag nodes to move them to a new position.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgements

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro) for the GUI framework
- [pyautogui](https://pyautogui.readthedocs.io/en/latest/) for mouse and keyboard automation
- [keyboard](https://github.com/boppreh/keyboard) for keyboard event handling