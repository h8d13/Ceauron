# csauron.py

import time
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import traceback
import numpy as np
import os
import shutil

from zauron.capture_utils import Config, TemplateManager, WindowManager, ScreenshotManager, Logger, ImageSaver, CameraManager
from zauron.capture_processor import ImageProcessor

class WindowCapture:
    def __init__(self, config_file='config.json'):
        self.config = Config(config_file)
        self.initialize_components()
        self.setup_execution_environment()

        capture_mode = "Camera" if self.config.use_camera else ("Fullscreen" if self.config.fullscreen else "Window")
        print(f"Capture mode: {capture_mode}")

    def initialize_components(self):
        self.template_manager = TemplateManager(self.config.template_dir)
        self.window_manager = WindowManager(self.config.target_window)
        self.screenshot_manager = ScreenshotManager()

        if self.config.use_camera:
            self.camera_manager = CameraManager(
                self.config.camera_index,
                self.config.camera_width,
                self.config.camera_height
            )
        else:
            self.camera_manager = None
        self.image_processor = ImageProcessor(
            self.config,  # Pass the config object
            self.template_manager.templates,
            'regions_config.json',
            enable_ocr=self.config.enable_ocr,
            enable_pixel_checks=self.config.enable_pixel_checks,
            enable_motion_detection=self.config.enable_motion_detection
        )
        
        # Initialize debug components if enabled
        if self.config.save_debug_images:
            self.logger = Logger('csauron_log.txt')
            self.image_saver = ImageSaver()
        else:
            self.logger = None
            self.image_saver = None

    def setup_execution_environment(self):
        self.processing_queue = queue.Queue(maxsize=5)
        self.running = False
        self.paused = False
        self.last_capture_time = 0
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.action_queue = queue.Queue()

    def handle_exception(self, error_message):
        print(f"Error: {error_message}")
        print(traceback.format_exc())

    def capture_and_process_loop(self):
        while self.running:
            if not self.paused:
                try:
                    current_time = time.time()
                    if current_time - self.last_capture_time >= self.config.capture_interval:
                        self.capture_and_enqueue()
                        self.last_capture_time = current_time

                    try:
                        img, window_position = self.processing_queue.get(timeout=0.01)
                        self.executor.submit(self.process_image, img, window_position)
                    except queue.Empty:
                        pass
                except Exception:
                    print("Error in capture and process loop:")
                    print(traceback.format_exc())
            else:
                time.sleep(0.01)  # Sleep briefly when paused to reduce CPU usage

    def capture_and_enqueue(self):
        try:
            if self.config.use_camera:
                img, window_position = self.camera_manager.capture()
                try:
                    self.processing_queue.put_nowait((img, window_position))
                except queue.Full:
                    print("Processing queue is full. Skipping this frame.")
            elif self.config.fullscreen:
                img, window_position = self.screenshot_manager.capture_window(None, fullscreen=True)
                try:
                    self.processing_queue.put_nowait((img, window_position))
                except queue.Full:
                    print("Processing queue is full. Skipping this frame.")
            else:
                window_info = self.window_manager.get_target_window()
                if window_info:
                    img, window_position = self.screenshot_manager.capture_window(window_info)
                    try:
                        self.processing_queue.put_nowait((img, window_position))
                    except queue.Full:
                        print("Processing queue is full. Skipping this frame.")
                else:
                    print("Target window not found.")
        except Exception:
            print("Error in capture_and_enqueue:")
            print(traceback.format_exc())

    def process_image(self, img, window_position):
        try:
            start_time = time.time()
            timestamp, processed_img, log_entries, actions_to_execute = self.image_processor.process_image_with_actions(img, window_position)
            self.logger.write_log(timestamp, log_entries)
            self.image_saver.save_processed_image(timestamp, processed_img)
            if not isinstance(img, np.ndarray):
                img = np.array(img)
            # Put actions into the action queue
            for action_name, action_params in actions_to_execute:
                self.action_queue.put((action_name, action_params))
            processing_time = time.time() - start_time
            print(f"Screenshot processed in {processing_time:.3f} seconds")
        except Exception:
            print("Error in process_image:")
            print(traceback.format_exc())

    # RUNNER UTILS

    def stop_capture(self):
        self.running = False
        if hasattr(self, 'image_processor'):
            self.image_processor.ocr_manager.stop()
        if self.camera_manager:
            self.camera_manager.release()

    # MAIN LOOP
    def run(self):
        self.running = True
        print(f"Waiting 3 seconds before starting at interval (seconds) {self.config.capture_interval}...")
        time.sleep(3)

        capture_thread = threading.Thread(target=self.capture_and_process_loop)
        capture_thread.start()

        try:
            while self.running:
                time.sleep(0.01)
                # Process actions from the queue
                try:
                    while not self.action_queue.empty():
                        action_name, action_params = self.action_queue.get_nowait()
                        self.image_processor.action_manager.execute_action(action_name, **action_params)
                except queue.Empty:
                    pass
        except KeyboardInterrupt:
            self.stop_capture()
        except Exception:
            print("Unexpected error in main loop:")
            print(traceback.format_exc())
        finally:
            self.running = False
            capture_thread.join()
            self.executor.shutdown(wait=True)
            print("Capture stopped.")

def clean_directories(directories):
    for directory in directories:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"Cleaned directory: {directory}")
            except Exception as e:
                print(f"Error cleaning directory {directory}: {e}")
        os.makedirs(directory, exist_ok=True)

if __name__ == '__main__':
    try:
        clean_directories(['screenshots', 'processed'])
        window_capture = WindowCapture()
        window_capture.run()

    except Exception:
        print("Fatal error:")
        print(traceback.format_exc())
