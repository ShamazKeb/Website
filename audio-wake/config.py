# Sheep Configuration

# Audio Settings
# Adjusted based on Docker logs (18.12.2025)
# "3 Microsoft® LifeCam HD-3000: USB Audio (plughw:2,0)"
MIC_DEVICE = "plughw:2,0"
SAMPLE_RATE = 44100
BLOCK_SIZE = 44100 # 1 Second per analysis block
NOISE_THRESHOLD = 0.03 # Lowered from 0.05 per user request

# Energy Settings (in seconds)
MAX_ENERGY = 60      # Maximum awake time capacity
ENERGY_PER_NOISE = 10 # Seconds added per trigger
IDLE_DRAIN = 1       # Seconds lost per second of silence

# Hardware Settings
# Joy-IT 3.5" Display uses GPIO 18 (PWM) for backlight
BACKLIGHT_GPIO_PIN = 18
# True = GPIO, False = File Path
USE_GPIO_BACKLIGHT = True

# Fallback path (not used if GPIO is True)
BACKLIGHT_PATH = "/sys/class/backlight/rpi_backlight/bl_power"
