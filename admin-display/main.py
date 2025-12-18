import threading
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
        self.fb = Framebuffer(w=320, h=480)
        # Calibration based on user diagnostics (17.12.2025)
        # TL: ~3750, 3780 | BR: ~410, 270
        self.touch = Touch(w=320, h=480, 
                           invert_x=True, invert_y=True, 
                           x_min=380, x_max=3780, 
                           y_min=260, y_max=3800)
        self.width = 320
        self.height = 480
        self.state = "START_MENU"
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
            self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            self.log_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
        except:
            self.font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
            self.log_font = ImageFont.load_default()

    def draw_start_menu(self):
        img = Image.new("RGB", (self.width, self.height), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.text((20, 30), "THY ADMIN", font=self.font, fill="#e67e22")
        draw.line((20, 65, 300, 65), fill="#333333", width=2)
        
        # Button 1: System Update
        btn_y = 100
        btn_h = 80
        btn_w = 280
        btn_x = 20
        
        # Draw Button Background
        draw.rounded_rectangle((btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), radius=15, fill="#2c3e50", outline="#34495e", width=2)
        
        # Icon placeholder (Update Icon)
        draw.text((btn_x + 20, btn_y + 25), "🔄", font=self.font, fill="white")
        draw.text((btn_x + 60, btn_y + 30), "System Update", font=self.small_font, fill="white")
        
        # Button 2: Placeholder
        btn2_y = 200
        draw.rounded_rectangle((btn_x, btn2_y, btn_x + btn_w, btn2_y + btn_h), radius=15, fill="#1a1a1a", outline="#333333", width=2)
        draw.text((btn_x + 60, btn2_y + 30), "Coming Soon...", font=self.small_font, fill="#666666")

        return img

    # ... (draw_idle and draw_menu remain largely the same, maybe minor adjustments optional) ...
    def draw_idle(self):
        img = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(img)
        
        # Back Button (Top Left)
        draw.text((10, 10), "< Back", font=self.small_font, fill="#666666")
        
        center_x, center_y = self.width // 2, self.height // 2
        radius = 80
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), 
                     fill="#1a1a1a", outline="#e67e22", width=3)
        icon_size = 100
        resized_icon = self.icon.resize((icon_size, icon_size))
        img.paste(resized_icon, (center_x - icon_size//2, center_y - icon_size//2), resized_icon)
        text = "Tap to Update"
        text_bbox = draw.textbbox((0,0), text, font=self.small_font)
        draw.text((center_x - text_bbox[2]//2, center_y + radius + 20), text, font=self.small_font, fill="gray")
        return img

    def draw_menu(self):
        img = Image.new("RGB", (self.width, self.height), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "Thy Projects", font=self.font, fill="#e67e22")
        thumb_w, thumb_h = 240, 150
        keto_thumb = self.keto_img.resize((thumb_w, thumb_h))
        img.paste(keto_thumb, (40, 80))
        draw.text((40, 240), "Keto Monitor", font=self.small_font, fill="white")
        handball_thumb = self.handball_img.resize((thumb_w, thumb_h))
        img.paste(handball_thumb, (40, 280))
        draw.text((40, 440), "Handball Tracker", font=self.small_font, fill="white")
        return img

    def draw_updating(self):
        img = Image.new("RGB", (self.width, self.height), "#101010")
        draw = ImageDraw.Draw(img)
        
        # 0. Read Status
        status_file = "/tmp/admin_update_status"
        current_step = ""
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    current_step = f.read().strip()
            except:
                pass

        # 1. Background Logs (Matrix Style) - Keep as background
        lines_per_screen = self.height // 14
        visible_logs = self.log_lines[-lines_per_screen:] 
        y_log = 80 # Start logs lower to make room for header
        for line in visible_logs:
            draw.text((10, y_log), "> " + line, font=self.log_font, fill="#333333")
            y_log += 12

        # 2. Progress Bar (Top)
        STEPS = ["CODE", "INFRA", "LANDING", "KETO", "HANDBALL", "AUDIO", "ADMIN"]
        # Map Steps to Display Names and Colors (for finished state)
        STEP_META = {
            "CODE": ("Git", "#f39c12"),
            "INFRA": ("NPM", "#3498db"),
            "LANDING": ("Web", "#2ecc71"),
            "KETO": ("Keto", "#e74c3c"),
            "HANDBALL": ("HB", "#9b59b6"),
            "AUDIO": ("Mic", "#1abc9c"),
            "ADMIN": ("GUI", "#95a5a6"),
            "DONE": ("✅", "white")
        }

        # Determine Progress Index
        current_idx = -1
        if current_step in STEPS:
            current_idx = STEPS.index(current_step)
        elif current_step == "DONE":
            current_idx = len(STEPS) # All done

        # Draw Icons Row
        margin_x = 10
        top_y = 10
        icon_size = 36
        gap = (self.width - 2*margin_x - len(STEPS)*icon_size) / (len(STEPS) - 1)
        
        for i, step_key in enumerate(STEPS):
            x = margin_x + i * (icon_size + gap)
            y = top_y
            
            label, color = STEP_META.get(step_key, ("?", "white"))
            
            # State Logic
            if i < current_idx:
                # DONE -> Colored
                fill_color = color
                outline_color = color
                text_color = "black" if step_key in ["CODE", "LANDING", "AUDIO"] else "white" # High contrast
            elif i == current_idx:
                # CURRENT -> Gray/Pulse? User said "Grayed out". 
                # Let's make it highlighted gray with white border
                fill_color = "#444444"
                outline_color = "white"
                text_color = "white"
            else:
                # PENDING -> Dark Gray
                fill_color = "#222222"
                outline_color = "#333333"
                text_color = "#555555"

            # Draw Circle
            draw.ellipse((x, y, x+icon_size, y+icon_size), fill=fill_color, outline=outline_color, width=2)
            
            # Draw Label (centered)
            # Using log_font for small labels inside icons
            bbox = draw.textbbox((0,0), label, font=self.log_font)
            txt_w = bbox[2] - bbox[0]
            txt_h = bbox[3] - bbox[1]
            draw.text((x + (icon_size-txt_w)/2, y + (icon_size-txt_h)/2), label, font=self.log_font, fill=text_color)

        # 2b. Restore Rotating Arcs (Center)
        center_x, center_y = self.width // 2, self.height // 2
        radius = 70
        start_angle = self.animation_angle
        end_angle = self.animation_angle + 120
        # White arc
        draw.arc((center_x - radius, center_y - radius, center_x + radius, center_y + radius), 
                 start=start_angle, end=end_angle, fill="white", width=5)
        # Second symmetrical arc
        draw.arc((center_x - radius, center_y - radius, center_x + radius, center_y + radius), 
                 start=start_angle + 180, end=end_angle + 180, fill="white", width=5)
        
        # Center Icon background
        bg_radius = 65
        draw.ellipse((center_x - bg_radius, center_y - bg_radius, center_x + bg_radius, center_y + bg_radius), fill="#101010")
        
        icon_size = 80
        resized_icon = self.icon.resize((icon_size, icon_size))
        img.paste(resized_icon, (center_x - icon_size//2, center_y - icon_size//2), resized_icon)

        # 3. Status Text (Below Icons)
        status_text = "Preparing..."
        if current_step in STEPS:
            # User wants: "Updating keto" etc
            pretty_name = STEP_META[current_step][0]
            # Use full names if possible?
            FULL_NAMES = {
                "CODE": "Updating Code...",
                "INFRA": "Updating Infrastructure...",
                "LANDING": "Updating Landing Page...",
                "KETO": "Updating Keto Monitor...",
                "HANDBALL": "Updating Handball Tracker...",
                "AUDIO": "Updating Audio Wake...",
                "ADMIN": "Updating Admin Interface..."
            }
            status_text = FULL_NAMES.get(current_step, f"Updating {pretty_name}...")
        elif current_step == "DONE":
            status_text = "Update Complete!"
            
        # Draw Center STATUS
        # Draw a bar behind text?
        bar_y = 60
        draw.line((0, bar_y + 12, self.width, bar_y + 12), fill="#333333", width=1)
        
        # Draw Text
        bbox = draw.textbbox((0,0), status_text, font=self.small_font)
        w = bbox[2] - bbox[0]
        draw.text(((self.width - w) / 2, bar_y), status_text, font=self.small_font, fill="white")

        return img

    def _run_update_process(self):
        try:
            script_path = os.path.join(os.path.dirname(__file__), UPDATE_SCRIPT)
            # Use Popen to read stdout line by line
            self.update_process = subprocess.Popen(
                [script_path], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                bufsize=1
            )
            
            for line in self.update_process.stdout:
                line = line.strip()
                if line:
                    self.log_lines.append(line)
                    # Keep log buffer reasonable
                    if len(self.log_lines) > 50:
                        self.log_lines.pop(0)
                        
            self.update_process.wait()
            self.log_lines.append("Done! Return code: " + str(self.update_process.returncode))
            
        except Exception as e:
            self.log_lines.append(f"Error: {e}")
        
        time.sleep(2) # Show "Done" briefly
        self.is_updating = False

    def perform_update(self):
        if self.is_updating: return
        
        self.state = "UPDATING"
        self.is_updating = True
        self.log_lines = ["Preparing update..."]
        self.completed_steps = set()
        
        # Start Thread
        t = threading.Thread(target=self._run_update_process)
        t.start()

    def run(self):
        print(f"Admin Display Started ({self.width}x{self.height})...")
        
        while True:
            # 1. Start Menu Logic
            if self.state == "START_MENU":
                self.fb.show(self.draw_start_menu())
                pos = self.touch.read()
                if pos:
                    print(f"Start Menu Touch: {pos}")
                    # Button 1: System Update (y=100 to y=180)
                    if 20 < pos[0] < 300 and 100 < pos[1] < 180:
                        self.state = "IDLE" # Transition to Update Screen
                        time.sleep(0.2) # Debounce

            # 2. Update Update Screen (IDLE)
            elif self.state == "IDLE":
                self.fb.show(self.draw_idle())
                pos = self.touch.read()
                if pos:
                    print(f"IDLE Touch: {pos}")
                    # Back Button (Top Left area)
                    if pos[0] < 100 and pos[1] < 50:
                        self.state = "START_MENU"
                        time.sleep(0.2) 
                    else:
                        # Center Update Button
                        cx, cy = self.width // 2, self.height // 2
                        if abs(pos[0] - cx) < 120 and abs(pos[1] - cy) < 120:
                            self.perform_update()

            # 3. Handle Updating State Animation
            elif self.state == "UPDATING":
                self.animation_angle = (self.animation_angle + 15) % 360
                self.fb.show(self.draw_updating())
                
                # Check transition condition (Thread finished)
                if not self.is_updating:
                    self.state = "MENU"
                    self.fb.show(self.draw_menu())
                
                # Small sleep to control framerate (e.g. 10-15 FPS)
                time.sleep(0.05)
                continue # Skip Touch input during update
            
            # 4. IPC Check (Sleep Mode)
            if os.path.exists("/tmp/sheep_state"):
                try:
                    with open("/tmp/sheep_state", "r") as f:
                        state = f.read().strip()
                    if state == "SLEEP":
                        if self.state != "SLEEPING":
                            print("Received SLEEP command. Going dark.")
                            self.fb.show(Image.new("RGB", (self.width, self.height), "black"))
                            # Hardware Blanking (Host Side)
                            os.system("echo 1 > /sys/class/graphics/fb1/blank")
                            self.state = "SLEEPING"
                        time.sleep(1)
                        continue
                    elif state == "WAKE" and self.state == "SLEEPING":
                        print("Received WAKE command.")
                        # Hardware Unblanking
                        os.system("echo 0 > /sys/class/graphics/fb1/blank")
                        self.state = "START_MENU"
                except:
                    pass

            time.sleep(0.1)

            time.sleep(0.1)

if __name__ == "__main__":
    app = App()
    app.run()
