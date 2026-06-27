# core/constants.py

BOARD_SIZE = 4  # 4x4 board

# Directions for piece movement
DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}

# The default holes on the physical Squirrels Go Nuts board
DEFAULT_HOLES = {(0, 2), (1, 0), (2, 1), (3, 3)}

FPS = 60

# Beautiful Color Palette (Premium HSL/Hex values)
BG_COLOR = (244, 241, 234)        # Creamy white warm background
PANEL_COLOR = (255, 255, 255)     # Clean white for panel backgrounds
TEXT_COLOR = (44, 42, 38)         # Dark charcoal for primary text
TEXT_MUTED = (120, 115, 105)      # Grayed text for stats/secondary data
BORDER_COLOR = (220, 215, 205)    # Soft grey for lines/borders

# Grid styling
BOARD_BG_COLOR = (139, 115, 85)   # Wooden brown for the board
CELL_BG_COLOR = (120, 95, 68)     # Darker wood for normal cells
HOLE_COLOR = (35, 30, 25)         # Dark hole color
HOLE_BORDER_COLOR = (180, 150, 110)

# Colors for pieces
PIECE_COLORS = {
    "brown": (160, 110, 70),       # Cute brown for brown squirrel
    "black": (45, 45, 45),         # Dark grey/black for black squirrel
    "white": (230, 230, 230),      # Off-white for white squirrel
    "orange": (235, 120, 40),      # Soft orange for orange squirrel
    "flower": (210, 60, 60),       # Vivid red for the flower obstacle
}

# Nut color
NUT_COLOR = (212, 160, 23)        # Golden amber for acorn
NUT_BORDER = (150, 105, 10)
NUT_SLOT_COLOR = (90, 70, 50)      # Acorn cup holder color

# UI Buttons & Interactive states
BTN_NORMAL = (79, 110, 138)       # Warm Slate Blue
BTN_HOVER = (98, 132, 161)        # Lighter Slate Blue
BTN_PRESSED = (61, 87, 110)
BTN_DISABLED = (180, 180, 180)
BTN_TEXT_COLOR = (255, 255, 255)

# Success / Highlight colors
HIGHLIGHT_COLOR = (100, 200, 120) # Green accent
SELECT_BORDER = (235, 200, 80)    # Golden yellow highlight outline for active piece
Frontier_COLOR = (112, 161, 255)  # Visualizer frontier
Visited_COLOR = (255, 107, 107)    # Visualizer visited
