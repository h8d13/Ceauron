# actions.py

import pyautogui
import time

# Define action functions

def click_action(x, y, button='left', clicks=1, interval=0.0, **kwargs):
    """Click at the specified position."""
    pyautogui.moveTo(x, y)
    pyautogui.click(button=button, clicks=clicks, interval=interval)
    print(f"Clicked at ({x}, {y}) with button '{button}', {clicks} times.")

def double_click_action(x, y, button='left', **kwargs):
    """Double-click at the specified position."""
    pyautogui.moveTo(x, y)
    pyautogui.doubleClick(x, y, button=button)
    print(f"Double-clicked at ({x}, {y}) with button '{button}'.")

def right_click_action(x, y, **kwargs):
    """Right-click at the specified position."""
    pyautogui.moveTo(x, y)
    pyautogui.click(button='right')
    print(f"Right-clicked at ({x}, {y}).")

def drag_action(end_x, end_y, duration=0.5, button='left', **kwargs):
    """Drag the mouse from start position to end position."""
    pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
    print(f"Dragged mouse to ({end_x}, {end_y}) with button '{button}'.")

def move_action(x, y, duration=0.0, **kwargs):
    """Move the mouse to the specified position."""
    pyautogui.moveTo(x, y, duration=duration)
    print(f"Moved mouse to ({x}, {y}).")

def type_action(text, interval=0.0, **kwargs):
    """Type the specified text."""
    pyautogui.write(text, interval=interval)
    print(f"Typed text: {text}")

def press_key_action(key, **kwargs):
    """Press a single key."""
    pyautogui.press(key)
    print(f"Pressed key: {key}")

def custom_action(*args, **kwargs):
    """Custom action with arbitrary arguments."""
    print("Custom action executed with args:", args, "and kwargs:", kwargs)

