import time
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
from fb import Framebuffer
from touch import Touch

# --- Configuration ---
FAVICON_PATH = "../landing-page/images/favicon.png"
KETO_IMG_PATH = "../landing-page/images/keto-monitor.png"
HANDBALL_IMG_PATH = "../landing-page/images/handball-tracker.png"
UPDATE_SCRIPT = "../update.sh"

class App:
    def __init__(self):
        self.fb = Framebuffer(w=320, h=480) # Fixed Resolution
        self.touch = Touch(w=320, h=480)    # Pass resolution to touch
        self.width = 320
        self.height = 480
        self.state = "IDLE" # IDLE, UPDATING, MENU
        
        # Load Assets
        try:
            self.icon = Image.open(FAVICON_PATH).convert("RGBA")
            self.keto_img = Image.open(KETO_IMG_PATH).convert("RGBA")
            self.handball_img = Image.open(HANDBALL_IMG_PATH).convert("RGBA")
        except FileNotFoundError:
            print("Assets not found, using empty images")
            self.icon = Image.new("RGBA", (100,100), "orange")
            self.keto_img = Image.new("RGBA", (100,100), "green")
            self.handball_img = Image.new("RGBA", (100,100), "blue")
            
        # Fonts
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            self.font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()

    def draw_idle(self):
        # Black background
        img = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(img)
        
        # Circle Center (Vertical Center)
        center_x, center_y = self.width // 2, self.height // 2
        radius = 80
        
        # Draw Circle
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), 
                     fill="#1a1a1a", outline="#e67e22", width=3)
        
        # Paste Favicon in Center (Resized)
        icon_size = 100
        resized_icon = self.icon.resize((icon_size, icon_size))
        img.paste(resized_icon, (center_x - icon_size//2, center_y - icon_size//2), resized_icon)
        
        # Text
        text = "Tap to Update"
        text_bbox = draw.textbbox((0,0), text, font=self.small_font)
        draw.text((center_x - text_bbox[2]//2, center_y + radius + 20), text, font=self.small_font, fill="gray")
        
        return img

    def draw_updating(self):
        img = Image.new("RGB", (self.width, self.height), "#2c3e50")
        draw = ImageDraw.Draw(img)
        
        text = "Updating..."
        bbox = draw.textbbox((0,0), text, font=self.font)
        draw.text(((self.width - bbox[2])//2, (self.height - bbox[3])//2), text, font=self.font, fill="white")
        
        return img

    def draw_menu(self):
        img = Image.new("RGB", (self.width, self.height), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        
        # Title
        draw.text((20, 20), "Thy Projects", font=self.font, fill="#e67e22")
        
        # Buttons Grid (Vertical Stack for Portrait)
        thumb_w, thumb_h = 240, 150 # Larger thumbnails
        
        # Keto (Top)
        keto_thumb = self.keto_img.resize((thumb_w, thumb_h))
        img.paste(keto_thumb, (40, 80))
        draw.text((40, 240), "Keto Monitor", font=self.small_font, fill="white")
        
        # Handball (Bottom)
        handball_thumb = self.handball_img.resize((thumb_w, thumb_h))
        img.paste(handball_thumb, (40, 280))
        draw.text((40, 440), "Handball Tracker", font=self.small_font, fill="white")
        
        return img

    def perform_update(self):
        self.state = "UPDATING"
        self.fb.show(self.draw_updating())
        
        print("Running Update Script...")
        try:
            # We run it relative to the script location
            script_path = os.path.join(os.path.dirname(__file__), UPDATE_SCRIPT)
            result = subprocess.run([script_path], capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        except Exception as e:
            print(f"Update failed: {e}")
            
        time.sleep(2) # Show "Updating" for at least a moment
        self.state = "MENU"
        self.fb.show(self.draw_menu())

    def run(self):
        print(f"Admin Display Started ({self.width}x{self.height})...")
        # Initial Draw
        self.fb.show(self.draw_idle())
        
        while True:
            # 1. Read Input
            pos = self.touch.read()
            
            if pos:
                print(f"Touch at {pos}")
                
                # Logic based on State
                if self.state == "IDLE":
                    # Check if click is near center circle
                    cx, cy = self.width // 2, self.height // 2
                    if abs(pos[0] - cx) < 120 and abs(pos[1] - cy) < 120:
                        self.perform_update()
                
                elif self.state == "MENU":
                    # Vertical Menu Logic
                    # Button 1 (Keto): x=40..280, y=80..230
                    if 40 < pos[0] < 280 and 80 < pos[1] < 230:
                        print("Keto Selected - No Action Implemented")
                    
                    # Button 2 (Handball): x=40..280, y=280..430
                    if 40 < pos[0] < 280 and 280 < pos[1] < 430:
                        print("Handball Selected - No Action Implemented")
                        
                    # Back to Idle if clicked top title
                    if pos[1] < 60:
                        self.state = "IDLE"
                        self.fb.show(self.draw_idle())

            time.sleep(0.1)

if __name__ == "__main__":
    app = App()
    app.run()
