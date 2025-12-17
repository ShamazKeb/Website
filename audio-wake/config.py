# Sheep Configuration

# Audio Settings
MIC_DEVICE = "plughw:CARD=HD3000,DEV=0"
SAMPLE_RATE = 44100
BLOCK_SIZE = 44100 # 1 Second per analysis block
NOISE_THRESHOLD = 0.05 # Initial guess, calibrate via test script

# Energy Settings (in seconds)
MAX_ENERGY = 60      # Maximum awake time capacity
ENERGY_PER_NOISE = 10 # Seconds added per trigger
IDLE_DRAIN = 1       # Seconds lost per second of silence

# Hardware Settings
# Try typical Pi backlight path triggers
BACKLIGHT_PATH = "/sys/class/backlight/rpi_backlight/bl_power"
# 0 = On, 1 = Off (Usually) - Verify!
DISPLAY_ON = 0
DISPLAY_OFF = 1
