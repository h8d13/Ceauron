# capture_processor.py

import numpy as np
import cv2
import time
from concurrent.futures import ThreadPoolExecutor
import traceback

from zauron.region_color import RegionConfig, RegionManager, ColorManager

## MAIN PROCESSOR
class ImageProcessor:
    def __init__(self, config, templates, region_config_file='regions_config.json',
                enable_pixel_checks=True, enable_motion_detection=False):
        self.config = config  
        self.confidence_threshold = config.confidence_thresholds
        self.templates = templates
        self.previous_frame = None
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Feature flags
        self.enable_pixel_checks = enable_pixel_checks
        self.enable_motion_detection = enable_motion_detection

        # Initialize components based on enabled features
        self.region_config = RegionConfig(region_config_file)
        self.region_manager = RegionManager(self.region_config)
        
        if self.enable_pixel_checks:
            self.color_manager = ColorManager(self.region_config)


    def adjust_positions(self, result, region_offset):
        """
        Adjust template match positions to account for region offset
        """
        if result is None:
            return None
            
        template, startX, startY, endX, endY, scale, confidence = result
        
        # Add region offset to coordinates
        startX += region_offset[0]
        startY += region_offset[1]
        endX += region_offset[0]
        endY += region_offset[1]
        
        return (template, startX, startY, endX, endY, scale, confidence)
        
    def process_image(self, img, window_position):
        timestamp = time.time()
        log_entries = []

        # Convert image once for all processing
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Process each region
        regions = self.region_manager.get_all_regions(img_cv)

       # DEBUG ROIs
        for region_name, (region_img, region_offset) in regions.items():
            log_entries.append(f"ROI Size: {region_img.shape}")
            log_entries.append(f"ROI Offset: {region_offset}")
            region_gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)

            # Template matching within region
            template_results = self.match_templates(region_gray, self.templates)
            for result in template_results:
                if result is not None:
                    adjusted_result = self.adjust_positions(result, region_offset)
                    if adjusted_result:
                        log_entry = self.process_template_result(adjusted_result, window_position, img_cv)
                        log_entries.extend(log_entry)

        # Color checking if enabled
        if self.enable_pixel_checks:
            color_results = self.color_manager.check_all_colors(img_cv, 'BGR')
            for name, match in color_results:
                log_entries.append(f"Color check '{name}': {'Match' if match else 'No match'}")

        # Motion detection if enabled
        if self.enable_motion_detection and self.previous_frame is not None:
            change_log = self.detect_changes(img_gray)
            if change_log:
                log_entries.append(change_log)
        
       # SET PREVIOUS FOR CHANGE DETECTING 
        self.previous_frame = img_gray

        return timestamp, img_cv, log_entries

    def match_templates(self, img_gray, templates):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for template in templates:
                futures.append(executor.submit(self.match_template, img_gray, template.image))
            
            results = []
            for template, future in zip(templates, futures):
                match_result = future.result()
                if match_result:
                    results.append((template, *match_result))
        return results

    def process_template_result(self, result, window_position, img_cv):
        try:
            template, startX, startY, endX, endY, scale, confidence = result
            abs_startX, abs_startY = window_position[0] + startX, window_position[1] + startY
            window_x, window_y = window_position[0], window_position[1]
            abs_endX, abs_endY = window_position[0] + endX, window_position[1] + endY

            log_entries = []
            
            # Check confidence levels and color-code accordingly
            if confidence >= self.config.confidence_thresholds['high']:
                cv2.rectangle(img_cv, (startX, startY), (endX, endY), (0, 255, 0), 1)  # Green for high
                confidence_level = "HIGH"
            elif confidence >= self.config.confidence_thresholds['medium']:
                cv2.rectangle(img_cv, (startX, startY), (endX, endY), (0, 255, 255), 1)  # Yellow for medium
                confidence_level = "MEDIUM"
            else:
                cv2.rectangle(img_cv, (startX, startY), (endX, endY), (0, 0, 255), 1)  # Red for low
                confidence_level = "LOW"

            log_entries.append(
                f"Conf: {confidence:.4f} ({confidence_level})\n"
                f"Match: {template.name} Scale: {scale:.2f}\n"
                f"Category: {template.category}\n"
                f"Value: {template.value}\n"
                f"Pos: ({startX}, {startY}):({endX}, {endY})\n"
                f"Abs: ({abs_startX}, {abs_startY}):({abs_endX}, {abs_endY})"
            )
            print(f"{confidence_level} confidence detected: {template.name} (Confidence: {confidence:.4f})")


            return log_entries

        except Exception:
            print("Error in process_template_result:")
            print(traceback.format_exc())
            return [], []

    ## GRAYSCALE
    def detect_changes(self, img_gray):
        if self.previous_frame is not None:
            if self.previous_frame.shape != img_gray.shape:
                self.previous_frame = cv2.resize(self.previous_frame, (img_gray.shape[1], img_gray.shape[0]))

            frame_diff = cv2.absdiff(self.previous_frame, img_gray)
            change_percentage = np.mean(frame_diff) / 255 * 100
            self.previous_frame = img_gray
            return f"CS: {change_percentage:.2f}%"

        self.previous_frame = img_gray
        return None

    def match_template(self, img_gray, template):
        h, w = template.shape[:2]
        found = None
        for scale in np.linspace(0.3, 1.0, 3)[::-1]:
            resized = cv2.resize(img_gray, (int(img_gray.shape[1] * scale), int(img_gray.shape[0] * scale)))
            r = img_gray.shape[1] / float(resized.shape[1])

            if resized.shape[0] < h or resized.shape[1] < w:
                break

            res = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
            _, maxVal, _, maxLoc = cv2.minMaxLoc(res)

            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        if found:
            maxVal, maxLoc, r = found
            startX, startY = int(maxLoc[0] * r), int(maxLoc[1] * r)
            endX, endY = int((maxLoc[0] + w) * r), int((maxLoc[1] + h) * r)
            return startX, startY, endX, endY, 1/r, maxVal
        return None