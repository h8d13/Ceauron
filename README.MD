# Ceauron - Automation Tool

Computer vision system to detects templates, checks pixel colors based on ANY visual input.

## Features

- Multiple capture modes (Window, Fullscreen, Camera)
  - Camera processing time: ~0.03s to 0.1s average
  - Screenshot processing time: ~0.3s average on Linux and 0.15s on Windows (could be reduced with downsizing and scale of template matches) 
- ROI (Region of Interest) breakdown for targeted monitoring
- Template matching with configurable confidence thresholds + Scaling (useful for changing or small items)
- Color detection and pixel analysis
- Motion detection 

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
pip3 install numpy opencv-python pillow mss pyautogui wmctrl
```

### Windows
```bash
pip install numpy opencv-python pillow mss pyautogui pywin32
```

### MacOS
```bash
pip3 install numpy opencv-python pillow mss pyautogui pyobjc-framework-Quartz
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
    "enable_pixel_checks": true,
    "enable_motion_detection": true
}
```

Fullscreen or camera mode overides the target_window setting. 

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
        "value": 10
    }
}
```

### Regions, Pixels

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

```
