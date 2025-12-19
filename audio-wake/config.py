# Sheep Configuration

# Audio Settings
# Adjusted based on Docker logs (18.12.2025)
# "3 Microsoft® LifeCam HD-3000: USB Audio (plughw:2,0)"
MIC_DEVICE = "plughw:2,0"
SAMPLE_RATE = 44100
BLOCK_SIZE = 44100 # 1 Second per analysis block
NOISE_THRESHOLD = 0.03

# Energy Settings (in seconds)
MAX_ENERGY = 180    # Maximum awake time capacity
ENERGY_PER_NOISE = 60 # Seconds added per trigger
IDLE_DRAIN = 1       # Seconds lost per second of silence

# Hardware Settings
# GPIO Failed. Switching to Framebuffer Blanking.
# 1 = Power Off (Blank), 0 = Power On (Unblank)
FB_BLANK_PATH = "/sys/class/graphics/fb1/blank" 

BACKLIGHT_GPIO_PIN = 18
USE_GPIO_BACKLIGHT = False
