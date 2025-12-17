ENERGY_PER_NOISE = 10 # Seconds added per trigger
IDLE_DRAIN = 1       # Seconds lost per second of silence

# Hardware Settings
# Try typical Pi backlight path triggers
BACKLIGHT_PATH = "/sys/class/backlight/rpi_backlight/bl_power"
# 0 = On, 1 = Off (Usually) - Verify!
DISPLAY_ON = 0
DISPLAY_OFF = 1
