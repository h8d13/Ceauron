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
sudo pip3 install numpy opencv-python pillow mss pyautogui pytesseract wmctrl

### Windows
pip install numpy opencv-python pillow mss pyautogui pytesseract python-win32

### Mac

pip3 install numpy opencv-python pillow mss pyautogui pytesseract pyobjc-framework-Quartz
Not 100% sure for support as the libraries for low-level screenshots are dependant on distribution year of model. 
