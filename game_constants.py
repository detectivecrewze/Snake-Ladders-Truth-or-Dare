"""
Konstanta Game - Dikonfigurasi di satu tempat
"""
# ==================================================
# CONFIG (SIDEBAR VERSION)
# ==================================================
TOTAL = 100
COLS = 10
ROWS = 10
CELL = 70

# [BARU] Pengaturan Lebar Sidebar
SIDEBAR_LEFT_WIDTH = 270  # <--- Ruang untuk Gambar Naga/Tema (Kiri)
SIDEBAR_WIDTH = 300       # Ruang untuk Log/History (Kanan)

# Lebar Total = Kiri + Papan + Kanan
WIDTH = SIDEBAR_LEFT_WIDTH + (COLS * CELL) + SIDEBAR_WIDTH 
HEIGHT = ROWS * CELL

ANIM_STEP_DELAY = 120
DICE_ANIM_TIME = 900
DICE_FRAME_DELAY = 60
BOUNCE_SPEED = 0.6

# ==================================================
# PATH
# ==================================================
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
FONT_FILE = os.path.join(BASE_DIR, "assets", "fonts", "medieval_font.ttf")

# ==================================================
# COLORS
# ==================================================
BG_COLOR = (30, 32, 40) # Default background

# Player Colors (Dark & Vivid)
PLAYER_COLORS = [
    (40, 40, 40),    # Player 1: Charcoal / Black
    (140, 0, 160),   # Player 2: Deep Purple
    (0, 120, 255),   # Player 3: Electric Blue
    (200, 50, 50)    # Player 4: Crimson Red
]

# Board Theme (Marble)
TILE_EVEN = {
    'base': (140, 145, 150),
    'highlight': (170, 175, 180),
    'shadow': (100, 105, 110),
    'crack': (80, 85, 90)
}
TILE_ODD = {
    'base': (215, 215, 220),
    'highlight': (240, 240, 245),
    'shadow': (170, 170, 175),
    'crack': (160, 160, 165)
}

