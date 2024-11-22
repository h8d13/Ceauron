# ocr_manager.py

from dataclasses import dataclass
from typing import Dict, Optional
import pytesseract
import cv2
import numpy as np
import threading
import queue
import time

@dataclass
class OCRCheck:
    name: str
    enabled: bool
    language: str = 'eng'
    config: str = ''
    description: str = ""
    preprocess: bool = False
    interval: float = 1.0  # Seconds between OCR checks
    
class OCRManager:
    def __init__(self, config):
        self.config = config
        self.ocr_checks = {}
        self.ocr_queue = queue.Queue(maxsize=10)
        self.results = {}
        self.last_check_times = {}  # Move this up
        self.running = True
        
        self.load_ocr_config()  # Call this after initializing last_check_times
        
        # Start OCR processing thread
        self.ocr_thread = threading.Thread(target=self._process_ocr_queue, daemon=True)
        self.ocr_thread.start()

    def load_ocr_config(self):
        for check_name, check_data in self.config.get('ocr_checks', {}).items():
            self.ocr_checks[check_name] = OCRCheck(
                name=check_data.get('name', check_name),  # Add fallback
                enabled=check_data.get('enabled', True),  # Add fallback
                language=check_data.get('language', 'eng'),
                config=check_data.get('config', ''),
                description=check_data.get('description', ''),
                preprocess=check_data.get('preprocess', False),
                interval=check_data.get('interval', 1.0)
            )
            self.last_check_times[check_name] = 0

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        denoised = cv2.fastNlMeansDenoising(binary)
        return denoised

    def _process_ocr_queue(self):
        while self.running:
            try:
                region_name, image = self.ocr_queue.get(timeout=1)
                check = self.ocr_checks.get(region_name)
                
                if check and check.enabled:
                    try:
                        processed_image = self.preprocess_image(image) if check.preprocess else image
                        text = pytesseract.image_to_string(
                            processed_image,
                            lang=check.language,
                            config=check.config
                        ).strip()
                        self.results[region_name] = text
                    except Exception as e:
                        print(f"OCR error for {region_name}: {str(e)}")
                
                self.ocr_queue.task_done()
            except queue.Empty:
                continue

    def check_all_regions(self, regions: Dict) -> Dict[str, str]:
        current_time = time.time()
        
        # Queue new OCR tasks if interval has passed
        for region_name, (region_img, _) in regions.items():
            if region_name in self.ocr_checks:
                check = self.ocr_checks[region_name]
                last_check = self.last_check_times[region_name]
                
                if current_time - last_check >= check.interval:
                    try:
                        self.ocr_queue.put_nowait((region_name, region_img))
                        self.last_check_times[region_name] = current_time
                    except queue.Full:
                        pass  # Skip if queue is full
        
        # Return current results without waiting
        return self.results.copy()

    def stop(self):
        self.running = False
        self.ocr_thread.join()