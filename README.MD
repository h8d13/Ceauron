# Ceauron - Computer Vision Automation Tool

A cross-platform computer vision automation tool that detects templates, performs OCR, checks pixel colors, and executes automated actions based on visual input.

## Features

- Multiple capture modes (Window, Fullscreen, Camera)
  - Camera processing time: ~0.08s average
  - Screenshot processing time: ~0.3s average
- ROI (Region of Interest) breakdown for targeted monitoring
- Template matching with configurable confidence thresholds
- Optical Character Recognition (OCR) integration
- Color detection and pixel analysis
- Motion detection capabilities
- Automated actions based on detection results
- Debug image saving functionality
- Multi-threaded processing
- Configurable intervals and thresholds

## Prerequisites

### Linux
```bash
pip3 install numpy opencv-python pillow mss pyautogui pytesseract wmctrl
```

### Windows
```bash
pip install numpy opencv-python pillow mss pyautogui pytesseract python-win32
```

### MacOS
```bash
pip3 install numpy opencv-python pillow mss pyautogui pytesseract pyobjc-framework-Quartz
```

## Installation

1. Create and activate virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate on Linux/Mac
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

2. Run setup script:
```bash
python setup.py
```
This will create:
- Template folder
- Screenshots/processed directories
- Default configuration files (templates metadata, regions config, main config)

## Configuration

### Main Configuration

```json
{
    "target_window": "Chromium",
    "capture_interval": 4,
    "template_dir": "templates",
    "confidence_thresholds": {
        "high": 0.8,
        "medium": 0.5
    },
    "fullscreen": true,
    "use_camera": false,
    "camera_index": 0,
    "camera_width": 640,
    "camera_height": 480,
    "enable_ocr": true,
    "enable_pixel_checks": true,
    "enable_motion_detection": true,
    "save_debug_images": true
}
```

Notes: OCR slows down processing (~0.3s) but can be used more periodically. Fullscreen or camera mode overides the target_window setting. 
Also keep the save_debug_images to true. 

Careful that naming differs on platforms on windows:

```bash
# Windows
GoogleChrome.exe

# Linux
Chromium

# Mac
.venv\Scripts\activate
```



### Template Configuration

```json
{
    "Capture.PNG": {
        "category": "Chrome Icons",
        "value": 10,
        "actions": [
            {
                "action": "type_action",
                "action_params": {
                    "text": "Hello World",
                    "interval": 0.05
                }
            }
        ]
    }
}
```

### Regions, Pixels, and OCR Configuration

```json
{
    "regions": {
        "full": {
            "name": "full",
            "enabled": true,
            "x": 0,
            "y": 0,
            "width": -1,
            "height": -1,
            "description": "Full capture area"
        },
        "top_bar": {
            "name": "top_bar",
            "enabled": true,
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
            "enabled": true,
            "x": 200,
            "y": 200,
            "color_space": "BGR",
            "values": [0, 0, 0],
            "tolerance": 30,
            "description": "Check for black pixel"
        }
    },
    "ocr_checks": {
        "top_bar": {
            "name": "top_bar",
            "enabled": true,
            "language": "eng",
            "config": "--psm 6",
            "description": "Read text from top bar",
            "preprocess": true,
            "interval": 5.0
        }
    }
}
```

## Usage

To start the automation:

```bash
python csauron.py
```

## Use Cases

- Browser automation
- Game automation
- Visual monitoring and automation tasks

## Note

This project is currently being tested primarily on Linux, with ongoing work to ensure cross-platform compatibility.

--------------------------------------------------------

                     ▄████████▄                     
                  ▄███▀░▒▒░░░░▀███▄  ░             
      ▄▄█▀▀ ░ ▄████▀░░░▒▒▒▒▒░░░▀████▄░░░▀▀█▄     
    ▄█▀▒█▀ ▄█░█▀░░░░▒▒▓▓█████▓▓▒▒░░░▀██▄ ▀█▒▀█▄   
  ▄█▀▒▓▒▀▄█▀░░░▒▒▓███▀▀▀███▀▀▀███▓▒▒░░░▀█▄▀▒▓▒▀█▄
 █▀▒▓▓▒██░░░░▒▓████   ▄██ ██▄   ████▓▒░░░░██▒▓▓▒▀█
█▄▒▓▓█▀░░▒▓█████   ██▀▀▒▒▓▒▒▀██   █████▓▒░░▀█▓▓▒▄█░▄
▀███▀░░░▒▓█████   ███░░▒▓█▓▒░░███  ██████▓▒░░░▀███▀░
  ░░░▒▒▓████████ ██▓░ ▒ ███   ░▓██   ███████▓▒▒░░░  
▄███▀░░░▒▓█████  ████░ ▒▓█▓▒ ░████  █████▓▒░░░▀███▄░
█▄▒▓▓█▀░░▒▓█████   ██▄▄▒▒▓▒▒▄██   █████▓▒░░▀█▓▓▒▄█░▄
 █▀▒▓▓▒██░░░░▒▓████   ▀██ █▓▀   ████▓▒░░░░██▒▓▓▒▀█
  ▀█▀▒▓▒▀▄█▀░░░▒▒▓███▄▄▄███▄▄▄███▓▒▒░░ ░█▄▀▒▓▒▀█
    ▀█▀▒█▀ ▄██▀░░░░▒▒▓▓█████▓▓▒▒░░░▀██▄ ▀█▒▀█▀
      ▀▀▄▀░░ ▀████▄░░░▒▒▒▒▒░░░▄████▀ ░░▀▄▀▀
        ░█▀▄░░   ▀▀███▄░░░░░▄███▀▀   ░░▄▀█░
         ▀█▒▄░░░    ▀▀████████▀▀    ░░░▄▒█▀
           ▀▄░░░░      ▀▀▀▀      ░░░░▄▀
             ▀▄░░░░░          ░░░░░▄▀
               ▀▄▄░░░░░░░░░░░░░░▄▄▀
                  ▀▀▄▄░░░░░░▄▄▀▀
                      ▀▀▀▀▀▀
-------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------
    ,o888888o.    8 8888888888            .8.          8 8888      88 8 888888888o.       ,o888888o.     b.             8 
   8888     `88.  8 8888                 .888.         8 8888      88 8 8888    `88.   . 8888     `88.   888o.          8 
,8 8888       `8. 8 8888                :88888.        8 8888      88 8 8888     `88  ,8 8888       `8b  Y88888o.       8 
88 8888           8 8888               . `88888.       8 8888      88 8 8888     ,88  88 8888        `8b .`Y888888o.    8 
88 8888           8 888888888888      .8. `88888.      8 8888      88 8 8888.   ,88'  88 8888         88 8o. `Y888888o. 8 
88 8888           8 8888             .8`8. `88888.     8 8888      88 8 888888888P'   88 8888         88 8`Y8o. `Y88888o8 
88 8888           8 8888            .8' `8. `88888.    8 8888      88 8 8888`8b       88 8888        ,8P 8   `Y8o. `Y8888 
`8 8888       .8' 8 8888           .8'   `8. `88888.   ` 8888     ,8P 8 8888 `8b.     `8 8888       ,8P  8      `Y8o. `Y8 
   8888     ,88'  8 8888          .888888888. `88888.    8888   ,d8P  8 8888   `8b.    ` 8888     ,88'   8         `Y8o.` 
    `8888888P'    8 888888888888 .8'       `8. `88888.    `Y88888P'   8 8888     `88.     `8888888P'     8            `Yo 
-------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------

