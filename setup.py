import json
import os

def create_config_json():
    config = {
        "target_window": "Chromium",
        "capture_interval": 4,
        "template_dir": "templates",
        "confidence_thresholds": {
            "high": 0.8,
            "medium": 0.5
        },
        "fullscreen": True,
        "use_camera": False,
        "camera_index": 0,
        "camera_width": 640,
        "camera_height": 480,
        "enable_pixel_checks": True,
        "enable_motion_detection": True,
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    print("Created config.json")

def create_regions_config_json():
    regions_config = {
        "regions": {
            "full": {
                "name": "full",
                "enabled": True,
                "x": 0,
                "y": 0,
                "width": -1,
                "height": -1,
                "description": "Full capture area"
            },
            "top_bar": {
                "name": "top_bar",
                "enabled": True,
                "x": 0,
                "y": 0,
                "width": 1920,
                "height": 100,
                "description": "Top bar area"
            }
        },
        "color_checks": {
            "black_pixel": {
                "name": "black_pixel",
                "enabled": True,
                "x": 200,
                "y": 200,
                "color_space": "BGR",
                "values": [0, 0, 0],
                "tolerance": 30,
                "description": "Check for black pixel"
            },
            "white_pixel": {
                "name": "white_pixel",
                "enabled": True,
                "x": 100,
                "y": 100,
                "color_space": "BGR",
                "values": [255, 255, 255],
                "tolerance": 20,
                "description": "Check for white pixel"
            }
        }
    }
    
    with open('regions_config.json', 'w') as f:
        json.dump(regions_config, f, indent=4)
    print("Created regions_config.json")

def create_templates_metadata_json():
    templates_metadata = {
        "Capture.PNG": {
            "category": "Chrome Icons",
            "value": 10,
        }
    }
    with open('templates_metadata.json', 'w') as f:
        json.dump(templates_metadata, f, indent=4)
    print("Created templates_metadata.json")

def create_templates_directory():
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("Created templates directory")
    else:
        print("Templates directory already exists")

def create_debug_directories():
    directories = ['screenshots', 'processed']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created {directory} directory")
        else:
            print(f"{directory} directory already exists")

def main():
    print("Creating necessary files and directories...")
    create_config_json()
    create_regions_config_json()
    create_templates_metadata_json()
    create_templates_directory()
    create_debug_directories()
    print("Setup complete!")

if __name__ == "__main__":
    main()