# mouse_position_debug.py

import pyautogui
import time

def print_mouse_position():
    print("Press Ctrl+C to stop.")
    try:
        while True:
            x, y = pyautogui.position()
            position_str = f"Mouse position: ({x}, {y})"
            print(position_str, end='\r')  # Overwrite the same line
            time.sleep(0.1)  # Update every 0.1 seconds
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    print_mouse_position()
