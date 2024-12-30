# REGION_COLOR.PY

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import cv2
import json

@dataclass
class Region:
    name: str
    enabled: bool
    x: int
    y: int
    width: int
    height: int
    description: str = ""
    templates: List[str] = field(default_factory=list)

@dataclass
class ColorCheck:
    name: str
    enabled: bool
    x: int
    y: int
    color_space: str
    values: List[int]
    tolerance: int
    description: str = ""

class RegionConfig:
    def __init__(self, config_file: str = 'regions_config.json'):
        self.config_file = config_file
        self.regions: Dict[str, Region] = {}
        self.color_checks: Dict[str, ColorCheck] = {}
        self.config = {}  # Store the raw config
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)  # Store the entire config
            
        # Load regions
        for region_name, region_data in self.config.get('regions', {}).items():
            self.regions[region_name] = Region(
                name=region_data.get('name', region_name),
                enabled=region_data.get('enabled', True),
                x=region_data.get('x', 0),
                y=region_data.get('y', 0),
                width=region_data.get('width', -1),
                height=region_data.get('height', -1),
                description=region_data.get('description', '')
            )

        # Load color checks
        for check_name, check_data in self.config.get('color_checks', {}).items():
            self.color_checks[check_name] = ColorCheck(
                name=check_data.get('name', check_name),
                enabled=check_data.get('enabled', True),
                x=check_data.get('x', 0),
                y=check_data.get('y', 0),
                color_space=check_data.get('color_space', 'BGR'),
                values=check_data.get('values', [0, 0, 0]),
                tolerance=check_data.get('tolerance', 10),
                description=check_data.get('description', '')
            )

class RegionManager:
    def __init__(self, config: RegionConfig):
        self.config = config
        self.regions = config.regions

    def get_region_dimensions(self, image: np.ndarray, region: Region) -> Tuple[int, int, int, int]:
        """Calculate actual region dimensions, handling special cases like -1"""
        img_height, img_width = image.shape[:2]
        
        width = img_width if region.width == -1 else min(region.width, img_width)
        height = img_height if region.height == -1 else min(region.height, img_height)
        
        x = min(max(region.x, 0), img_width - width)
        y = min(max(region.y, 0), img_height - height)
        
        return x, y, width, height

    def extract_region(self, image: np.ndarray, region_name: str) -> Tuple[Optional[np.ndarray], Tuple[int, int]]:
        """Extract a specific region from the image"""
        if region_name not in self.regions:
            print(f"Warning: Region {region_name} not found")
            return None, (0, 0)

        region = self.regions[region_name]
        if not region.enabled:
            return None, (0, 0)

        x, y, width, height = self.get_region_dimensions(image, region)
        region_img = image[y:y+height, x:x+width]
        return region_img, (x, y)

    def get_all_regions(self, image: np.ndarray) -> Dict[str, Tuple[np.ndarray, Tuple[int, int]]]:
        """Extract all enabled regions from the image"""
        regions = {}
        for name, region in self.regions.items():
            if region.enabled:
                region_img, offset = self.extract_region(image, name)
                if region_img is not None:
                    regions[name] = (region_img, offset)
        return regions

class ColorManager:
    def __init__(self, config: RegionConfig):
        self.config = config
        self.color_checks = config.color_checks

    def convert_color_space(self, image: np.ndarray, from_space: str, to_space: str) -> np.ndarray:
        """Convert between color spaces"""
        if from_space == to_space:
            return image
        conversion_code = getattr(cv2, f'COLOR_{from_space}2{to_space}')
        return cv2.cvtColor(image, conversion_code)

    def check_color(self, image: np.ndarray, current_color_space: str, check_name: str) -> Tuple[bool, List[Dict]]:
        """Check if a specific pixel matches the expected color"""
        if check_name not in self.color_checks:
            return False, []

        check = self.color_checks[check_name]
        if not check.enabled:
            return False, []

        try:
            if check.y >= image.shape[0] or check.x >= image.shape[1]:
                return False, []

            pixel = image[check.y, check.x]
            diff = np.abs(pixel - check.values)
            match = np.all(diff <= check.tolerance)

            return match if match else []
            
        except IndexError:
            return False, []
        except Exception:
            return False, []

    def check_all_colors(self, image: np.ndarray, current_color_space: str) -> List[Tuple[str, bool, List[Dict]]]:
        """Check all enabled color points in the image"""
        results = []
        for name, check in self.color_checks.items():
            if check.enabled:
                match = self.check_color(image, current_color_space, name)
                results.append((name, match))
        return results