# capture_utils.py

import os
import cv2
from collections import deque
import queue
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict, Any
from contextlib import contextmanager
import sys
import subprocess
from mss import mss
from PIL import Image
import numpy as np

# UTILS
class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        # Existing settings
        self.target_window = 'Untitled - Notepad'
        self.capture_interval = 4
        self.template_dir = '.venv/templates'
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.5
        }
        self.fullscreen = False
        self.use_camera = False
        self.camera_index = 0
        self.camera_width = 640
        self.camera_height = 480

        # Add new feature toggles with defaults
        self.enable_pixel_checks = True
        self.enable_motion_detection = False

        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Load existing settings
            self.target_window = config.get('target_window', self.target_window)
            self.capture_interval = config.get('capture_interval', self.capture_interval)
            self.template_dir = config.get('template_dir', self.template_dir)
                        # Load confidence thresholds
            if 'confidence_thresholds' in config:
                self.confidence_thresholds.update(config['confidence_thresholds'])
            self.fullscreen = config.get('fullscreen', self.fullscreen)
            self.use_camera = config.get('use_camera', self.use_camera)
            self.camera_index = config.get('camera_index', self.camera_index)
            self.camera_width = config.get('camera_width', self.camera_width)
            self.camera_height = config.get('camera_height', self.camera_height)

            # Load new feature toggles
            self.enable_pixel_checks = config.get('enable_pixel_checks', self.enable_pixel_checks)
            self.enable_motion_detection = config.get('enable_motion_detection', self.enable_motion_detection)

        except FileNotFoundError:
            print(f"Config file {self.config_file} not found. Using defaults.")
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self.config_file}. Using defaults.")


@dataclass
class Template:
    name: str
    image: np.ndarray
    category: str
    value: int

# LOAD TEMPLATES AND METADATA
class TemplateManager:
    def __init__(self, template_dir: str, metadata_file: str = 'templates_metadata.json'):
        self.template_dir = template_dir
        self.metadata_file = metadata_file
        self.templates: List[Template] = self.load_templates()

    def load_templates(self) -> List[Template]:
        if not os.path.exists(self.template_dir):
            raise ValueError(f"Template directory not found: {self.template_dir}")

        metadata = self.load_metadata()
        templates = []

        for filename in os.listdir(self.template_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                template_path = os.path.join(self.template_dir, filename)
                template_image = cv2.imread(template_path, 0)
                if template_image is not None:
                    template_info = metadata.get(filename, {})
                    templates.append(Template(
                        name=filename,
                        image=template_image,
                        category=template_info.get('category', 'uncategorized'),
                        value=template_info.get('value', 0),
                    ))
                else:
                    print(f"Warning: Could not load template {filename}")

        if not templates:
            raise ValueError("No valid template images found in the templates directory.")

        return templates

    def load_metadata(self) -> Dict:
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Metadata file {self.metadata_file} not found. Using default values.")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {self.metadata_file}. Using default values.")
            return {}

#CAMERAS

class CameraManager:
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None

    def initialize(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            if not self.cap.isOpened():
                raise ValueError(f"Cannot open camera {self.camera_index}")

    def capture(self):
        if self.cap is None:
            self.initialize()
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to capture frame from camera")
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb), (0, 0)  # Return PIL Image and (0,0) as window position

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None


# GET WINDOW
class WindowManager:
    def __init__(self, target_window):
        self.target_window = target_window

    def get_target_window(self):
        if sys.platform == 'win32':
            return self.get_windows_window()
        elif sys.platform == 'darwin':
            return self.get_macos_window()
        elif sys.platform.startswith('linux'):
            return self.get_linux_window()
        else:
            raise NotImplementedError("Unsupported platform")

    def get_windows_window(self):
        import win32gui  # type: ignore

        def enum_windows_callback(hwnd, target_windows):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if self.target_window.lower() in window_text.lower():
                    target_windows.append(hwnd)
            return True

        target_windows = []
        win32gui.EnumWindows(enum_windows_callback, target_windows)

        if target_windows:
            hwnd = target_windows[0]
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width, height = right - left, bottom - top
            return {'hwnd': hwnd, 'left': left, 'top': top, 'width': width, 'height': height}
        else:
            return None

    def get_linux_window(self):
        try:
            output = subprocess.check_output(['wmctrl', '-lG']).decode()
            for line in output.splitlines():
                parts = line.split()
                window_id = parts[0]
                desktop_id = parts[1]
                x = int(parts[2])
                y = int(parts[3])
                w = int(parts[4])
                h = int(parts[5])
                host = parts[6]
                window_title = ' '.join(parts[7:])
                if self.target_window.lower() in window_title.lower():
                    return {'window_id': window_id, 'left': x, 'top': y, 'width': w, 'height': h}
        except Exception as e:
            print(f"Error getting window on Linux: {e}")
        return None

    def get_macos_window(self):
        try:
            from AppKit import NSWorkspace  # type: ignore
            from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID  # type: ignore

            options = kCGWindowListOptionOnScreenOnly
            window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            for window in window_list:
                owner_name = window.get('kCGWindowOwnerName', '')
                window_name = window.get('kCGWindowName', '')
                if self.target_window.lower() in window_name.lower() or self.target_window.lower() in owner_name.lower():
                    bounds = window.get('kCGWindowBounds', {})
                    x = int(bounds.get('X', 0))
                    y = int(bounds.get('Y', 0))
                    width = int(bounds.get('Width', 0))
                    height = int(bounds.get('Height', 0))
                    return {'left': x, 'top': y, 'width': width, 'height': height}
        except Exception as e:
            print(f"Error getting window on MacOS: {e}")
        return None

# INITIAL SCREENSHOT
class ScreenshotManager:
    def __init__(self, max_screenshots=5):
        self.max_screenshots = max_screenshots
        self.screenshot_queue = deque(maxlen=max_screenshots)
        os.makedirs('screenshots', exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.thread_local = threading.local()
        self.deletion_queue = queue.Queue()
        self.cleanup_thread = threading.Thread(target=self.cleanup_old_screenshots, daemon=True)
        self.cleanup_thread.start()

    @contextmanager
    def get_mss(self):
        if not hasattr(self.thread_local, 'sct'):
            self.thread_local.sct = mss()
        yield self.thread_local.sct

    def capture_window(self, window_info, fullscreen=False):
        with self.get_mss() as sct:
            if fullscreen:
                # Capture the primary monitor
                monitor = sct.monitors[1]  # Primary monitor
                left, top = 0, 0
            else:
                screen_width = sct.monitors[0]['width']
                screen_height = sct.monitors[0]['height']
                left = max(0, window_info['left'])
                top = max(0, window_info['top'])
                width = min(window_info['width'], screen_width - left)
                height = min(window_info['height'], screen_height - top)
                monitor = {"top": top, "left": left, "width": width, "height": height}

            print(f"{'Fullscreen' if fullscreen else 'Window'} capture - Monitor: {monitor}")

            try:
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            except mss.exception.ScreenShotError as e:
                print(f"Failed to capture screen: {e}")
                return None, None

        timestamp = int(time.time())
        screenshot_path = os.path.join('screenshots', f'screenshot_{timestamp}.png')

        # Save the screenshot asynchronously
        self.executor.submit(self.save_screenshot, img, screenshot_path)
        self.manage_screenshot_queue(timestamp)

        return img, (left, top)

    def save_screenshot(self, img, path):
        with open(path, 'wb') as f:
            img.save(f, format='PNG', optimize=True)

    def manage_screenshot_queue(self, timestamp):
        self.screenshot_queue.append(timestamp)
        if len(self.screenshot_queue) == self.max_screenshots:
            old_timestamp = self.screenshot_queue[0]
            old_file = os.path.join('screenshots', f'screenshot_{old_timestamp}.png')
            self.deletion_queue.put(old_file)

    def cleanup_old_screenshots(self):
        while True:
            try:
                file_to_delete = self.deletion_queue.get(timeout=1)
                if file_to_delete is None:
                    break
                self.delete_file_with_retry(file_to_delete)
            except queue.Empty:
                continue

    def delete_file_with_retry(self, file_path, max_attempts=5, delay=1):
        for attempt in range(max_attempts):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                break
            except PermissionError:
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                else:
                    print(f"Failed to delete {file_path} after {max_attempts} attempts")

    def __del__(self):
        self.executor.shutdown(wait=True)
        # Wait for the cleanup thread to finish
        self.deletion_queue.put(None)  # Signal to stop the cleanup thread
        self.cleanup_thread.join(timeout=5)

# LOGGER
class Logger:
    def __init__(self, log_file):
        self.log_file = log_file

    def write_log(self, timestamp, log_entries):
        log_content = f"Timestamp: {timestamp}\n" + "\n".join(log_entries) + "\n" + "-" * 50 + "\n"
        with open(self.log_file, 'a') as f:
            f.write(log_content)
            print(f"{timestamp} Log written.")

# SAVE IMAGES FOR DEBUG (CAN COMMENT OUT FOR PEROFOMANCE BUT GOOD DEBUG)
class ImageSaver:
    def __init__(self, max_saved_images=5):
        self.max_saved_images = max_saved_images
        self.processed_queue = deque(maxlen=max_saved_images)

    def save_processed_image(self, timestamp, img_cv):
        os.makedirs('processed', exist_ok=True)
        cv2.imwrite(f'processed/processed_{timestamp}.png', img_cv)

        self.processed_queue.append(timestamp)
        if len(self.processed_queue) == self.max_saved_images:
            old_timestamp = self.processed_queue[0]
            old_file = f'processed/processed_{old_timestamp}.png'
            if os.path.exists(old_file):
                os.remove(old_file)
