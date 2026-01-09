# nm_common/constants.py

# Grid and Screen Settings
GRID_SIZE = 40
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
SIMULATION_TICK_RATE = 15

# Color Map
COLOR_MAP = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 255, 0),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "gray": (100, 100, 100),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "bg": (230, 230, 220)
}

# Simulation Settings
DEFAULT_CAR_LIMIT = 2
PIN_GENERATION_INTERVAL = 10
FAILURE_THRESHOLD_SECONDS = 60.0
MAX_PINS_LIMIT = 10
ESTIMATED_RTT = 40.0
