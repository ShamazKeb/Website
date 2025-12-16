# Developer Guide: Raspberry Pi Touch Display (Headless/Python)

This document contains the verified technical knowledge required to control a **3.5" SPI Touch Display** (e.g., XPT2046/ADS7846) on **Raspberry Pi OS Lite (Headless)** using Python.

**Target Audience:** AI Agents & Developers building embedded UIs without Desktop environments (X11/Wayland).

---

## 1. Hard Constraints & Philosophy

*   **OS:** Raspberry Pi OS Lite (CLI only).
*   **No Window Manager:** Do NOT use `tkinter`, `pyqt`, `kivy` (unless raw Kivy), or `pygame` (unless distinct SDL setup).
*   **Method:** Direct Framebuffer Access (`/dev/fb1`) + Direct Input Event Reading (`/dev/input/event0`).
*   **Performance:** SPI bus is the bottleneck. Minimize full-screen refreshes.

## 2. Hardware Interfaces

### Display (Framebuffer)
*   **Device:** `/dev/fb1` (usually; fb0 is HDMI).
*   **Format:** RGB565 (16-bit). 5 bits Red, 6 bits Green, 5 bits Blue.
*   **Resolution:** Typically 480x320.
*   **Access:** Memory Mapped File (`mmap`).

### Touch (Input)
*   **Driver:** ADS7846 / XPT2046.
*   **Device:** `/dev/input/event0` (check via `ls -l /dev/input/by-path/`).
*   **Protocol:** `evdev` (Linux Input Subsystem).
*   **Calibration:** Raw values (0..4095) must be chemically mapped to Screen Coordinates (0..480).

---

## 3. Implementation Patterns (Python)

### A. Framebuffer Driver (`fb.py`)

**Core Logic:**
1.  Open `/dev/fb1` in binary mode.
2.  `mmap` the file to memory.
3.  Convert an RGB888 Image (Pillow) to a byte array of RGB565.
4.  Seek 0 and Write to mmap.

```python
import mmap
import os

class Framebuffer:
    def __init__(self, dev='/dev/fb1', w=480, h=320):
        self.w, self.h = w, h
        # RGB565 = 2 bytes per pixel
        self.screensize = w * h * 2
        
        try:
            self.f = open(dev, 'r+b')
            self.mm = mmap.mmap(self.f.fileno(), self.screensize)
        except Exception as e:
            print(f"FB Error: {e} (Are you root? Is SPI active?)")
            self.mm = None

    def show(self, pil_image):
        if not self.mm: return
        
        # 1. Resize/Ensure RGB
        img = pil_image.convert('RGB').resize((self.w, self.h))
        pixels = img.load()
        
        # 2. Convert to RGB565 (Native Python implementation)
        # Optimized approach: Use multiple lookup tables or C-extensions/numpy for speed.
        # Simple approach (suffices for 15fps):
        buf = bytearray(self.screensize)
        idx = 0
        for y in range(self.h):
            for x in range(self.w):
                r, g, b = pixels[x, y]
                # Formula: R5(11-15) | G6(5-10) | B5(0-4)
                # Note: Little Endian for Pi FB usually
                val = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                buf[idx] = val & 0xFF
                buf[idx+1] = (val >> 8) & 0xFF
                idx += 2
        
        # 3. Blit
        self.mm.seek(0)
        self.mm.write(buf)
```

### B. Touch Driver (`touch.py`)

**Core Logic:**
1.  Use `evdev` library.
2.  Poll for `ABS_X`, `ABS_Y`, and `BTN_TOUCH`.
3.  **Scale:** Map Min/Max of driver to Screen Width/Height.

```python
import evdev
from evdev import ecodes

class Touch:
    def __init__(self, dev_path='/dev/input/event0'):
        self.device = evdev.InputDevice(dev_path)
        self.x, self.y = 0, 0
    
    def read(self):
        # Non-blocking read recommended
        try:
            for event in self.device.read():
                if event.type == ecodes.EV_ABS:
                    if event.code == ecodes.ABS_X:
                        # Heuristic Calibration
                        self.x = int((event.value / 4095.0) * 480) 
                    elif event.code == ecodes.ABS_Y:
                        self.y = int((event.value / 4095.0) * 320)
                elif event.type == ecodes.EV_KEY:
                    if event.code == ecodes.BTN_TOUCH and event.value == 1:
                        return (self.x, self.y) # Touch Down
        except BlockingIOError:
            pass
        return None
```

### C. UI Rendering (`ui.py`)

**Core Logic:**
1.  Draw everything into a virtual canvas using `Pillow` (PIL).
2.  Send the final image to Framebuffer.
3.  **Optimization:** Only call `fb.show()` when the UI state changes (Dirty Flag).

---

## 4. System Prerequisites

The "Agent" planning the project must ensure these commands are run on the Pi:

```bash
# 1. Enable SPI & Overlays
# Add to /boot/config.txt:
# dtoverlay=piscreen,speed=16000000,rotate=90

# 2. Permissions
# User must be in 'video' (fb) and 'input' (touch) groups
sudo usermod -a -G video,input $USER

# 3. Dependencies
sudo apt install python3-pil python3-evdev
```

## 5. Troubleshooting "Verified Lessons"

1.  **"Permission Denied"**: You are not root or not in the `video` group. Run with `sudo`.
2.  **Wrong Colors (Blue is Red)**: RGB565 conversion issue. Swap byte order or RGB shift logic.
3.  **Touch Axis Inverted**: Fix in python code `x = width - x` or usage of `dtoverlay` rotation parameters.
4.  **Slow Refresh**: The Python loop for RGB565 is slow. Mitigation: Only update changed rectangles or use `numpy` for array ops.
