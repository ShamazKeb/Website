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
        self.fb = Framebuffer()
        self.touch = Touch()
        self.width = 480
        self.height = 320
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
        
        # Circle Center
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
        draw.text((center_x - text_bbox[2]//2, center_y + radius + 10), text, font=self.small_font, fill="gray")
        
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
        draw.text((10, 10), "Thy Projects", font=self.font, fill="#e67e22")
        
        # Buttons Grid (2 buttons side by side)
        # Button 1: Keto
        # Button 2: Handball
        
        # Draw Images (Thumbnails)
        thumb_w, thumb_h = 180, 135
        
        # Keto
        keto_thumb = self.keto_img.resize((thumb_w, thumb_h))
        img.paste(keto_thumb, (30, 60))
        draw.text((30, 200), "Keto Monitor", font=self.small_font, fill="white")
        
        # Handball
        handball_thumb = self.handball_img.resize((thumb_w, thumb_h))
        img.paste(handball_thumb, (270, 60))
        draw.text((270, 200), "Handball Tracker", font=self.small_font, fill="white")
        
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
        print("Admin Display Started...")
        # Initial Draw
        self.fb.show(self.draw_idle())
        
        while True:
            # 1. Read Input
            pos = self.touch.read()
            
            if pos:
                print(f"Touch at {pos}")
                
                # Logic based on State
                if self.state == "IDLE":
                    # Check if click is near center circle (roughly)
                    cx, cy = self.width // 2, self.height // 2
                    if abs(pos[0] - cx) < 100 and abs(pos[1] - cy) < 100:
                        self.perform_update()
                
                elif self.state == "MENU":
                    # Check Button Clicks
                    # Button 1 (Keto): x=30..210, y=60..195
                    if 30 < pos[0] < 210 and 60 < pos[1] < 195:
                        print("Keto Selected - No Action Implemented")
                    
                    # Button 2 (Handball): x=270..450, y=60..195
                    if 270 < pos[0] < 450 and 60 < pos[1] < 195:
                        print("Handball Selected - No Action Implemented")
                        
                    # Back to Idle if clicked elsewhere? Or distinct Back button?
                    # For now: Click Top Left title to go back
                    if pos[0] < 200 and pos[1] < 50:
                        self.state = "IDLE"
                        self.fb.show(self.draw_idle())

            time.sleep(0.1)

if __name__ == "__main__":
    app = App()
    app.run()
