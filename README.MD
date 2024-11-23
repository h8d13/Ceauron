# Ceauron - Automation Tool

Computer vision system to detects templates, performs OCR, checks pixel colors, and executes automated actions based on visual input.

## Features

- Multiple capture modes (Window, Fullscreen, Camera)
  - Camera processing time: ~0.08s average
  - Screenshot processing time: ~0.3s average (could be reduced with downsizing and scale of template matches) 
- ROI (Region of Interest) breakdown for targeted monitoring
- Template matching with configurable confidence thresholds + Scaling (useful for changing or small items)
- Optical Character Recognition (OCR) integration
- Color detection and pixel analysis
- Motion detection 
- Automated actions based on detection results

## Performance oriented
- Multi-threaded processing
- Configurable 

### 



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
## Prerequisites

### Linux
```bash
pip3 install numpy opencv-python pillow mss pyautogui pytesseract wmctrl
```

### Windows
```bash
pip install numpy opencv-python pillow mss pyautogui pytesseract pywin32
```

### MacOS
```bash
pip3 install numpy opencv-python pillow mss pyautogui pytesseract pyobjc-framework-Quartz
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

Notes: OCR slows down processing (~0.3s) but can be used more periodically. 
Fullscreen or camera mode overides the target_window setting. 
Also keep the save_debug_images to true. 

Careful that naming differs on platforms and is usually case sensitive (you can go in your ressource monitor to find the exact process handles):

```bash
# Windows
GoogleChrome.exe

# Linux
Chromium

# Mac
Google Chrome
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
                    "text": "Hello World from Ceauron",
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
- Make sure to have at least 1 template (again metadata is case sensitive)
Then run the main script:
```bash
python csauron.py
```
# Xanth

Xanths are automation modules. Use cases with documentation.

# Zigils

Zigils are processing techniques that are callable within-in. 
- Binary Thresholding (Edge detection)
- Heatmaps 
- Recoloring
- Etc

# Zollum

Zollum is the action manager which is currently under-development. 

## Note

This project is currently being tested primarily on Linux, with ongoing work to ensure cross-platform compatibility.

```bash
                                                 ░   ▄████████▄    ░                 
                                             ░  ░ ▄███▀░▒▒░░░░▀███▄  ░             
                                       ▄▄█▀ ▄██░█▀░░░▒▒▒▒▒░░░▀████▄░░░▀▀█▄     
                                     █▀▒█▀ ▄█░█▀░░░▒▒▓▓█████▓▓ ▒░░░▀██▄ ▀█▒▀█▄   
                                  ▄█▀▒▓▒▀▄█▀░░░▒▒▓███▀▀▀███▀▀▀███▓▒▒░░░▀█▄▀▒▓▒▀█▄
                                 █▀▒▓▓▒██░░░░▒▓████   ▄██ ██▄   ████▓▒░░░░██▒▓▓▒▀█
                                █▄▒▓▓█▀░░▒▓█████   ██▀▀▒▒▓▒▒▀██   █████▓▒░░▀█▓▓▒▄█░▄
                                ▀███▀░░░▒▓█████   ███░░▒▓█▓▒░░███  ██████▓▒░░░▀███▀░
                                  ░░░ ▒▓████████ ██▓░ ▒ ███   ░▓██   ███████▓▒▒░░░  
                                ▄███▀░░░▒▓█████  ████░ ▒▓█▓▒ ░████  █████▓▒░░░▀███▄░
                                █▄▒▓▓█▀░░▒▓█████   ██▄▄▒▒▓▒▒▄██   █████▓▒░░▀█▓▓▒▄█░▄
                                 █▀▒▓▓▒██░░░░▒▓████   ▀██ █▓▀   ████▓▒░░░░██▒▓▓▒▀█
                                  ▀█▀▒▓▒▀▄█▀░░░▒▒▓███▄▄▄███▄▄▄███▓▒▒░░ ░█▄▀▒▓▒▀█
                                    ▀█▀▒█▀ ▄ █▀░░░░▒▒▓▓█████▓▓▒▒░░░▀██  ▀█▒█▀
                                       ▀▄▀░░ ▀██ █▄░░░▒▒▒▒▒░░░▄████▀ ░░▀▄▀▀
                                        ░█▀▄░░   ▀▀███▄░░░░░▄█ █▀▀   ░░▄▀█░
                                         ▀█▒▄░ ░░   ▀▀████████▀▀    ░░░▄▒▀
                                           ▀▄░░░░      ▀▀▀▀      ░░░░▄▀
                                             ▀▄░░░░░  ░░    ░░░ ░░░▄▀
                                               ▀▄▄░░░░░░░░░░░░░░▄▄▀
                                                  ▀▀▄▄░░░░░░▄▄▀▀
                                                      ▀▀▀▀▀▀
-------------------------------------------------------------------------------------------------------------------------
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
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
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```
