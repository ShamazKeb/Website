import threading
import time
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
from fb import Framebuffer
from fb import Framebuffer
from touch import Touch
from tapo_manager import TapoManager
from pihole_manager import PiholeManager

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
        self.last_touch_pos = None # For debug visualization
        
        # Log & Animation State
        self.log_lines = []
        self.animation_angle = 0
        self.update_process = None
        self.is_updating = False
        self.is_updating = False
        self.completed_steps = set()
        
        # Smart Home Manager
        self.tapo_manager = TapoManager("johann@thygs.com", "SmartHome!")
        
        # Pi-hole Manager (localhost, port 8080)
        self.pihole_manager = PiholeManager(host="localhost", port=8080)
        
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

    def perform_reboot(self):
        print("Rebooting System...")
        try:
            # Draw "Rebooting..." text before dying
            img = Image.new("RGB", (self.width, self.height), "black")
            draw = ImageDraw.Draw(img)
            draw.text((80, 220), "Rebooting...", font=self.font, fill="red")
            self.fb.show(img)
            time.sleep(1)
            subprocess.run(["sudo", "reboot"])
        except Exception as e:
            print(f"Reboot failed: {e}")

    def draw_start_menu(self):
        img = Image.new("RGB", (self.width, self.height), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.text((20, 30), "THY ADMIN", font=self.font, fill="#e67e22")
        draw.line((20, 65, 240, 65), fill="#333333", width=2)
        
        # Power/Reboot Button (Top Right)
        # Location: x=260, y=15, size=50
        rx, ry, rs = 260, 15, 45
        draw.ellipse((rx, ry, rx+rs, ry+rs), fill="#c0392b", outline="#e74c3c", width=2)
        
        # Draw "Reboot Arrow" (White)
        cx, cy = rx + rs/2, ry + rs/2
        r = 12
        # Standard Power/Reboot: Gap at Top (270 deg)
        # PIL Angles: 0=Right, 90=Bottom, 180=Left, 270=Top
        # Arc from 290 (Top Right) to 250 (Top Left) clockwise
        draw.arc((cx-r, cy-r, cx+r, cy+r), start=290, end=250, fill="white", width=3)
        
        # Arrow Head at the "End" (250 deg -> Top Left)
        # 250 deg is approx (-x, -y) from center?
        # Math: 250 is 10 deg past 240. 
        # Let's verify: 
        # 270 is top (0, -r). 
        # 250 is slightly left of top.
        # Arrow: Pointing in clockwise direction.
        
        # Simple Triangle at Top Left of arc
        # Coords approx: cx-4, cy-12
        draw.polygon([(cx-8, cy-14), (cx+2, cy-14), (cx-4, cy-8)], fill="white")
        # Just a generic wedge at the top-left gap
        
        # Dot in center for "Power On" look? Or just open circle?
        # User said "Red on/off button". 
        draw.line((cx, cy-4, cx, cy+4), fill="white", width=3) # Power line (Vertical in center)
        
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
        
        # Button 2: Smart Home
        btn2_y = 200
        # Draw Button Background
        draw.rounded_rectangle((btn_x, btn2_y, btn_x + btn_w, btn2_y + btn_h), radius=15, fill="#2c3e50", outline="#34495e", width=2)
        draw.text((btn_x + 20, btn2_y + 25), "🏠", font=self.font, fill="white")
        draw.text((btn_x + 60, btn2_y + 30), "Smart Home", font=self.small_font, fill="white")
        
        # Button 3: Ad-Blocker
        btn3_y = 300
        # Color based on Pi-hole status (green if enabled)
        pihole_color = "#27ae60" if self.pihole_manager.enabled else "#c0392b"
        pihole_outline = "#2ecc71" if self.pihole_manager.enabled else "#e74c3c"
        draw.rounded_rectangle((btn_x, btn3_y, btn_x + btn_w, btn3_y + btn_h), radius=15, fill=pihole_color, outline=pihole_outline, width=2)
        draw.text((btn_x + 20, btn3_y + 25), "🛡️", font=self.font, fill="white")
        draw.text((btn_x + 60, btn3_y + 30), "Ad-Blocker", font=self.small_font, fill="white")

        return img

    def draw_smart_home(self):
        img = Image.new("RGB", (self.width, self.height), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        
        # Header & Back
        draw.text((10, 10), "< Back", font=self.small_font, fill="#aeaaaa")
        draw.text((80, 10), "Smart Home", font=self.font, fill="#e67e22")
        draw.line((20, 50, 300, 50), fill="#333333", width=2)
        
        # 2x2 Grid for Devices
        # Margins: 20px
        # W=320 -> 280 usable -> 130 per button + 20 gap
        # H=480 -> Start Y=70
        
        devices = self.tapo_manager.devices
        
        start_y = 70
        btn_w = 135
        btn_h = 135
        gap = 10
        margin_x = 20
        
        for i, dev in enumerate(devices):
            row = i // 2
            col = i % 2
            
            x = margin_x + col * (btn_w + gap)
            y = start_y + row * (btn_h + gap)
            
            # Color based on state
            color = "#27ae60" if dev["state"] else "#34495e" # Green if on, Dark Blue/Gray if off
            outline = "#2ecc71" if dev["state"] else "#555555"
            
            draw.rounded_rectangle((x, y, x + btn_w, y + btn_h), radius=10, fill=color, outline=outline, width=2)
            
            # Icon/Name (Simply use name for now)
            # Center text
            name = dev["name"]
            # Split name if too long?
            if " " in name:
                parts = name.split(" ")
                draw.text((x + 10, y + 40), parts[0], font=self.small_font, fill="white")
                draw.text((x + 10, y + 65), parts[1], font=self.small_font, fill="white")
            else:
                draw.text((x + 10, y + 50), name, font=self.small_font, fill="white")
                
            # State Text
            state_text = "ON" if dev["state"] else "OFF"
            draw.text((x + 10, y + 100), state_text, font=self.log_font, fill="#cccccc")

        return img

    def draw_pihole(self):
        """Draw Pi-hole / Ad-Blocker control screen."""
        img = Image.new("RGB", (self.width, self.height), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        
        # Header & Back
        draw.text((10, 10), "< Back", font=self.small_font, fill="#aeaaaa")
        draw.text((80, 10), "Ad-Blocker", font=self.font, fill="#e67e22")
        draw.line((20, 50, 300, 50), fill="#333333", width=2)
        
        # Main Toggle Button (large, centered)
        toggle_x = 60
        toggle_y = 80
        toggle_w = 200
        toggle_h = 120
        
        if self.pihole_manager.enabled:
            color = "#27ae60"
            outline = "#2ecc71"
            status_text = "ACTIVE"
            icon = "🛡️"
        else:
            color = "#c0392b"
            outline = "#e74c3c"
            status_text = "PAUSED"
            icon = "⛔"
        
        draw.rounded_rectangle((toggle_x, toggle_y, toggle_x + toggle_w, toggle_y + toggle_h), 
                               radius=20, fill=color, outline=outline, width=3)
        
        # Icon and status
        draw.text((toggle_x + 80, toggle_y + 20), icon, font=self.font, fill="white")
        draw.text((toggle_x + 60, toggle_y + 70), status_text, font=self.small_font, fill="white")
        
        # Quick Actions
        qa_y = 230
        qa_h = 50
        qa_w = 130
        
        # 5 Min Pause
        draw.rounded_rectangle((20, qa_y, 20 + qa_w, qa_y + qa_h), radius=10, fill="#7f8c8d", outline="#95a5a6", width=2)
        draw.text((35, qa_y + 15), "5 Min Pause", font=self.log_font, fill="white")
        
        # 30 Min Pause
        draw.rounded_rectangle((170, qa_y, 170 + qa_w, qa_y + qa_h), radius=10, fill="#7f8c8d", outline="#95a5a6", width=2)
        draw.text((180, qa_y + 15), "30 Min Pause", font=self.log_font, fill="white")
        
        # Statistics Section
        stats_y = 310
        draw.line((20, stats_y, 300, stats_y), fill="#333333", width=1)
        draw.text((20, stats_y + 10), "Statistics", font=self.small_font, fill="#e67e22")
        
        stats = self.pihole_manager.get_stats()
        
        # Queries Today
        draw.text((20, stats_y + 45), f"Queries Today:", font=self.log_font, fill="#888888")
        draw.text((150, stats_y + 45), f"{stats['queries_today']:,}", font=self.log_font, fill="white")
        
        # Blocked Today
        draw.text((20, stats_y + 70), f"Blocked Today:", font=self.log_font, fill="#888888")
        draw.text((150, stats_y + 70), f"{stats['blocked_today']:,}", font=self.log_font, fill="white")
        
        # Percentage
        draw.text((20, stats_y + 95), f"Block Rate:", font=self.log_font, fill="#888888")
        draw.text((150, stats_y + 95), f"{stats['percent_blocked']:.1f}%", font=self.log_font, fill="#2ecc71")
        
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
        print("perform_update() called")
        if self.is_updating: 
            print("Already updating, ignoring.")
            return
        
        print("Starting Update Process...")
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
                    
                    # Check Reboot Button (Top Right)
                    # Circle at 260, 15, size 45 -> Hitbox approx x>250, y<70
                    if pos[0] > 250 and pos[1] < 70:
                        self.perform_reboot()
                        
                    # Button 1: System Update (y=100 to y=180)
                    elif 20 < pos[0] < 300 and 100 < pos[1] < 180:
                        self.state = "IDLE" # Transition to Update Screen
                        time.sleep(0.2) # Debounce
                        
                    # Button 2: Smart Home (y=200 to y=280)
                    elif 20 < pos[0] < 300 and 200 < pos[1] < 280:
                        self.state = "SMART_HOME"
                        # Optimistic background update?
                        t = threading.Thread(target=self.tapo_manager.update_states)
                        t.start()
                        time.sleep(0.2)
                        
                    # Button 3: Ad-Blocker (y=300 to y=380)
                    elif 20 < pos[0] < 300 and 300 < pos[1] < 380:
                        self.state = "PIHOLE"
                        # Fetch current stats in background
                        t = threading.Thread(target=self.pihole_manager.update_stats)
                        t.start()
                        time.sleep(0.2)

            # 1b. Smart Home Logic
            elif self.state == "SMART_HOME":
                self.fb.show(self.draw_smart_home())
                pos = self.touch.read()
                if pos:
                    print(f"Smart Home Touch: {pos}")
                    # Back Button
                    if pos[0] < 80 and pos[1] < 50:
                        self.state = "START_MENU"
                        time.sleep(0.2)
                    else:
                        # Grid Calculation
                        start_y = 70
                        btn_w = 135
                        btn_h = 135
                        gap = 10
                        margin_x = 20
                        
                        # Check which button
                        for i in range(4):
                            row = i // 2
                            col = i % 2
                            x = margin_x + col * (btn_w + gap)
                            y = start_y + row * (btn_h + gap)
                            
                            if x < pos[0] < x + btn_w and y < pos[1] < y + btn_h:
                                print(f"Toggling Device {i}")
                                # Toggle in thread to avoid blocking UI
                                def do_toggle(idx):
                                    self.tapo_manager.toggle(idx)
                                    
                                t = threading.Thread(target=do_toggle, args=(i,))
                                t.start()
                                time.sleep(0.2) # Debounce

            # 1c. Pi-hole / Ad-Blocker Logic
            elif self.state == "PIHOLE":
                self.fb.show(self.draw_pihole())
                pos = self.touch.read()
                if pos:
                    print(f"Pihole Touch: {pos}")
                    # Back Button
                    if pos[0] < 80 and pos[1] < 50:
                        self.state = "START_MENU"
                        time.sleep(0.2)
                    # Main Toggle Button (y=80-200, x=60-260)
                    elif 60 < pos[0] < 260 and 80 < pos[1] < 200:
                        def do_toggle_pihole():
                            self.pihole_manager.toggle()
                        t = threading.Thread(target=do_toggle_pihole)
                        t.start()
                        time.sleep(0.3)
                    # 5 Min Pause (y=230-280, x=20-150)
                    elif 20 < pos[0] < 150 and 230 < pos[1] < 280:
                        def do_pause_5():
                            self.pihole_manager.disable(300)  # 5 * 60 = 300 seconds
                        t = threading.Thread(target=do_pause_5)
                        t.start()
                        time.sleep(0.2)
                    # 30 Min Pause (y=230-280, x=170-300)
                    elif 170 < pos[0] < 300 and 230 < pos[1] < 280:
                        def do_pause_30():
                            self.pihole_manager.disable(1800)  # 30 * 60 = 1800 seconds
                        t = threading.Thread(target=do_pause_30)
                        t.start()
                        time.sleep(0.2)

            # 2. Update Update Screen (IDLE)
            elif self.state == "IDLE":
                pos = self.touch.read()
                if pos:
                    print(f"IDLE Touch: {pos}")
                
                    # Check Buttons
                    # Back Button (Top Left area)
                    if pos[0] < 100 and pos[1] < 50:
                        self.state = "START_MENU"
                        time.sleep(0.2) 
                    else:
                        # Center Update Button
                        cx, cy = self.width // 2, self.height // 2
                        # Button region
                        if abs(pos[0] - cx) < 120 and abs(pos[1] - cy) < 120:
                             self.perform_update()

                self.fb.show(self.draw_idle())
                
                # Decay touch debug (remove after a frame or so? Or keep it?)
                # for now keep it consistent 


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
