import mmap
import os

class Framebuffer:
    def __init__(self, dev='/dev/fb1', w=320, h=480):
        self.w, self.h = w, h
        # RGB565 = 2 bytes per pixel
        self.screensize = w * h * 2
        self.mm = None
        
        try:
            self.f = open(dev, 'r+b')
            self.mm = mmap.mmap(self.f.fileno(), self.screensize)
        except Exception as e:
            print(f"FB Error: {e} (Are you root? Is SPI active?)")
            # Fallback for testing on non-Pi systems (optional, but good for stability)
            self.mm = None

    def show(self, pil_image):
        if not self.mm: return
        
        # 1. Resize/Ensure RGB
        img = pil_image.convert('RGB').resize((self.w, self.h))
        pixels = img.load()
        
        # 2. Convert to RGB565 (Native Python implementation)
        # Optimized slightly for readability.
        # Note: This loop is slow in pure Python (~0.5s). 
        # For a simple menu it's acceptable.
        buf = bytearray(self.screensize)
        idx = 0
        for y in range(self.h):
            for x in range(self.w):
                r, g, b = pixels[x, y]
                # Formula: R5(11-15) | G6(5-10) | B5(0-4)
                # Little Endian for Pi FB: Low Byte, High Byte
                val = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                
                # Write Little Endian
                buf[idx] = val & 0xFF      # Low byte
                buf[idx+1] = (val >> 8) & 0xFF # High byte
                idx += 2
        
        # 3. Blit
        # Move cursor to start
        self.mm.seek(0)
        self.mm.write(buf)

    def close(self):
        if self.mm:
            self.mm.close()
            self.f.close()
