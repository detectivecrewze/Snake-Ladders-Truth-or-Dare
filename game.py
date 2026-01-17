import pygame
import json
import random
import os
import time
import math
import re
from typing import Optional
import sys
from modules.dice_generator import generate_dice_sprites
from modules.board_assets import get_challenge_image
from modules.challenge_parser import get_move_effect
from modules.board_generator import generate_random_objects
from modules.visuals import draw_background_effects, draw_scroll
from modules.sidebar_manager import SidebarManager
from modules.menu_manager import show_main_menu, show_pause_menu
from modules.left_sidebar import LeftSidebar
import modules.popup_manager as popup_manager
from game_constants import *
from modules.game_logger import logger
from modules.asset_loader import AssetLoader
from modules.game_state import GameState
from modules.game_renderer import GameRenderer
from modules.game_deck import ChallengeDeck
from modules.game_utils import (
    resource_path,
    get_timer_duration,
    board_xy as board_xy_from_utils,
    lerp,
    overflow_reflect,
    play_sound,
    fade_to_dark,
    fade_from_dark,
    distribute_random_challenges,
)
from modules.game_victory import show_victory_screen
from modules.game_state import GameState

def board_xy(n):
    """Wrapper untuk board_xy dengan konstanta lokal + OFFSET KIRI + CENTER"""
    idx = max(0, n - 1)

    base_x, base_y = board_xy_from_utils(idx, COLS, ROWS, CELL)

    final_x = base_x + SIDEBAR_LEFT_WIDTH

    center_x = final_x + (CELL // 2)
    center_y = base_y + (CELL // 2)

    return center_x, center_y

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED, vsync=1)
pygame.display.set_caption("Snake & Ladder")

icon_path = os.path.join(IMAGE_DIR, "logo.png")
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)

from modules import visuals  # Pastikan sudah di-import

logger.info("Initializing Game...")
asset_loader = AssetLoader(BASE_DIR)

SCROLL_IMG = asset_loader.load_image("images/scroll_medieval.png", (100, 100))
SCROLL_TRUTH_IMG = asset_loader.load_image("images/scroll_truth.png", (100, 100))
SCROLL_DARE_IMG = asset_loader.load_image("images/scroll_dare.png", (100, 100))

font = asset_loader.load_font(FONT_FILE, 24)
big_font = asset_loader.load_font(FONT_FILE, 48)
log_bold_font = asset_loader.load_font(FONT_FILE, 20)
tile_font = pygame.font.SysFont("arial", 20, bold=True)
small_font = pygame.font.SysFont("arial", 14)

dice_images = generate_dice_sprites(80)

hero_avatars = []
for i in range(1, 5):
    img = asset_loader.load_image(f"images/hero_{i}.png", (64, 64))
    hero_avatars.append(img)

RIGHT_SIDEBAR_BG = None
try:
    path_bg = os.path.join(IMAGE_DIR, "sidebar_right_bg.png")
    if os.path.exists(path_bg):
        raw = pygame.image.load(path_bg).convert()
        RIGHT_SIDEBAR_BG = pygame.transform.smoothscale(raw, (SIDEBAR_WIDTH, HEIGHT))
        print("✅ Background Sidebar Kanan diload!")
    else:
        print("ℹ️ sidebar_right_bg.png tidak ditemukan (Pakai warna polos).")
except Exception as e:
    print(f"⚠️ Error load sidebar kanan: {e}")

sidebar_helper = SidebarManager(
    IMAGE_DIR, dice_images, hero_avatars, font_path=FONT_FILE
)
left_sidebar_visual = LeftSidebar(
    SIDEBAR_LEFT_WIDTH, HEIGHT, IMAGE_DIR, font_path=FONT_FILE
)
clock = pygame.time.Clock()

assets = {
    "scroll_default": SCROLL_IMG,
    "scroll_truth": SCROLL_TRUTH_IMG,
    "scroll_dare": SCROLL_DARE_IMG,
    "hero_avatars": hero_avatars,
    "right_sidebar_bg": RIGHT_SIDEBAR_BG,
}
fonts_collection = {
    "big": big_font,
    "font": font,
    "small": small_font,
    "log": log_bold_font,
}
renderer = GameRenderer(screen, assets, fonts_collection)

try:
    step_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "step.wav"))
    dice_roll = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "dice_roll.wav"))
    dice_end = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "dice_end.wav"))
except Exception:
    step_sound = None
    dice_roll = None
    dice_end = None

try:
    with open(os.path.join(BASE_DIR, "challenges.json"), encoding="utf-8") as f:
        challenges = json.load(f)
except FileNotFoundError:
    challenges = {}

from modules.board_generator import generate_random_objects

p_config = {
    "WIDTH": WIDTH,
    "HEIGHT": HEIGHT,
    "big_font": big_font,
    "font": font,
    "clock": clock,
}

players, game_level = show_main_menu(screen, p_config)
dark_overlay = fade_to_dark(screen, WIDTH, HEIGHT)

raw_challenges_data = {}
try:
    filename = f"challenges_lv{game_level}.json"
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        raw_challenges_data = json.load(f)
    logger.info(f"Berhasil memuat tantangan Level {game_level}")
except FileNotFoundError:
    logger.warning(f"File {filename} tidak ada, menggunakan default.")
    try:
        with open(os.path.join(BASE_DIR, "challenges.json"), encoding="utf-8") as f:
            raw_challenges_data = json.load(f)
    except:
        raw_challenges_data = {}

CHALLENGE_DECK = ChallengeDeck(raw_challenges_data)

state = GameState(players, game_level)

state.snakes, state.ladders = generate_random_objects(
    TOTAL, num_snakes=3, num_ladders=2
)

if raw_challenges_data:
    state.challenges = distribute_random_challenges(
        CHALLENGE_DECK, state.snakes, state.ladders, amount=40
    )
    logger.info(f"Berhasil menyebar {len(state.challenges)} tantangan di papan.")

positions = state.positions
colors = state.colors
bounce_phase = state.bounce_phase
pulse_scale = state.pulse_scale
snakes = state.snakes
ladders = state.ladders
challenges = state.challenges
turn = state.turn

log_manager = state.log_manager
sidebar_snapshot = None  # Visual cache handled locally

def start_turn(player):
    log_manager.start_turn(player)

def log_turn(text):
    log_manager.log_turn(text)

def end_turn():
    log_manager.end_turn()
    global sidebar_snapshot
    sidebar_snapshot = log_manager.sidebar_snapshot

history = log_manager.history
current_turn_log = log_manager.current_turn_log

def board_xy(n):
    """Wrapper untuk board_xy dengan konstanta lokal + OFFSET KIRI"""
    idx = max(0, n - 1)

    base_x, base_y = board_xy_from_utils(idx, COLS, ROWS, CELL)

    final_x = base_x + SIDEBAR_LEFT_WIDTH

    center_x = final_x + (CELL // 2)
    center_y = base_y + (CELL // 2)

    return center_x, center_y

def draw_board():
    global SCROLL_IMG
    local_rng = random.Random()

    for i in range(1, TOTAL + 1):
        n = i - 1
        row_idx = n // COLS
        col_idx = n % COLS
        row = ROWS - 1 - row_idx
        col = col_idx if (row_idx % 2) == 0 else COLS - 1 - col_idx

        x = (col * CELL) + SIDEBAR_LEFT_WIDTH  # <--- GANTI BARIS INI
        y = row * CELL

        rect = pygame.Rect(x, y, CELL, CELL)

        if i % 2 == 0:
            base_col = (140, 145, 150)
            highlight = (170, 175, 180)  # Pinggir terang
            shadow = (100, 105, 110)  # Bayangan
            crack_col = (80, 85, 90)  # Warna retakan
        else:
            base_col = (215, 215, 220)
            highlight = (240, 240, 245)
            shadow = (170, 170, 175)
            crack_col = (160, 160, 165)

        pygame.draw.rect(screen, base_col, rect)

        local_rng.seed(i)

        for _ in range(3):
            vx_start = local_rng.randint(x, x + CELL)
            vy_start = local_rng.randint(y, y + CELL)
            vx_end = vx_start + local_rng.randint(-20, 20)
            vy_end = vy_start + local_rng.randint(-20, 20)
            vein_color = shadow
            pygame.draw.line(
                screen, vein_color, (vx_start, vy_start), (vx_end, vy_end), 1
            )

        for _ in range(5):
            nx = local_rng.randint(x + 4, x + CELL - 4)
            ny = local_rng.randint(y + 4, y + CELL - 4)
            pygame.draw.circle(screen, crack_col, (nx, ny), 1)

        if local_rng.random() > 0.75:
            sx_crack = local_rng.randint(x + 15, x + CELL - 15)
            sy_crack = local_rng.randint(y + 15, y + CELL - 15)
            points = [(sx_crack, sy_crack)]
            for _ in range(3):
                sx_crack += local_rng.randint(-6, 6)
                sy_crack += local_rng.randint(-6, 6)
                points.append((sx_crack, sy_crack))

            if len(points) > 1:
                pygame.draw.lines(screen, crack_col, False, points, 2)

        pygame.draw.line(screen, highlight, (x, y), (x + CELL, y), 3)  # Atas
        pygame.draw.line(screen, highlight, (x, y), (x, y + CELL), 3)  # Kiri
        pygame.draw.line(
            screen, shadow, (x, y + CELL), (x + CELL, y + CELL), 3
        )  # Bawah
        pygame.draw.line(
            screen, shadow, (x + CELL, y), (x + CELL, y + CELL), 3
        )  # Kanan

        rivet_col = (60, 60, 70)
        offset = 6
        for pos in [
            (x + offset, y + offset),
            (x + CELL - offset, y + offset),
            (x + offset, y + CELL - offset),
            (x + CELL - offset, y + CELL - offset),
        ]:
            pygame.draw.circle(screen, rivet_col, pos, 2)
            pygame.draw.circle(screen, (150, 150, 160), (pos[0] - 1, pos[1] - 1), 1)

        seal_center = (x + 18, y + 18)

        local_rng.seed(i * 100)
        blob_points = []
        for ang in range(0, 360, 45):
            rad = local_rng.randint(11, 15)
            bx = seal_center[0] + math.cos(math.radians(ang)) * rad
            by = seal_center[1] + math.sin(math.radians(ang)) * rad
            blob_points.append((bx, by))

        pygame.draw.polygon(screen, (140, 20, 20), blob_points)
        pygame.draw.circle(screen, (180, 40, 40), seal_center, 10)  # Badan Segel

        pygame.draw.circle(
            screen, (220, 100, 100), (seal_center[0] - 3, seal_center[1] - 3), 2
        )

        display_text = str(i)
        num_surf = small_font.render(display_text, True, (255, 240, 200))
        num_rect = num_surf.get_rect(center=seal_center)
        screen.blit(num_surf, num_rect)

        is_snake_head = i in snakes
        is_ladder_base = i in ladders

        if str(i) in challenges and not is_snake_head and not is_ladder_base:
            cx, cy = x + CELL // 2, y + CELL // 2
            float_y = math.sin(pygame.time.get_ticks() * 0.005 + i) * 6

            challenge_text = challenges[str(i)].lower()
            scroll_to_use = SCROLL_IMG  # Default scroll

            if "truth" in challenge_text or "kebenaran" in challenge_text:
                if SCROLL_TRUTH_IMG:
                    scroll_to_use = SCROLL_TRUTH_IMG
            elif "dare" in challenge_text or "tantangan" in challenge_text:
                if SCROLL_DARE_IMG:
                    scroll_to_use = SCROLL_DARE_IMG

            if scroll_to_use:
                shadow_rect = pygame.Rect(cx - 10, cy + 18, 20, 6)
                pygame.draw.ellipse(screen, (0, 0, 0, 60), shadow_rect)

                scroll_rect = scroll_to_use.get_rect(center=(cx, cy + float_y))
                screen.blit(scroll_to_use, scroll_rect)
            else:
                draw_scroll(screen, cx, cy + float_y)

def draw_snake(start, end, glow=False):
    sx, sy = board_xy(start)
    ex, ey = board_xy(end)

    time_ms = pygame.time.get_ticks()
    breath = math.sin(time_ms * 0.005) * 2  # Naga sedikit mengembang/mengempis

    points = []
    steps = 45
    for i in range(steps):
        t = i / (steps - 1)

        bx = lerp(sx, ex, t)
        by = lerp(sy, ey, t)

        freq = 3.5
        amp = 25

        curve = math.sin(t * math.pi * freq + (time_ms * 0.002)) * amp

        px = bx + curve
        py = by  # y tetap turun ke bawah

        points.append((px, py))

    shadow_points = [(p[0] + 8, p[1] + 8) for p in points]
    if len(points) > 1:
        pygame.draw.lines(screen, (0, 0, 0, 80), False, shadow_points, 24)

    if glow:
        for w in range(20, 0, -4):
            alpha = 150 - (w * 5)
            glow_col = (255, 50, 50, alpha) if glow else (0, 0, 0, 0)
            pygame.draw.lines(screen, glow_col, False, points, 22 + w)

    pygame.draw.lines(screen, (10, 30, 10), False, points, 20 + int(breath))

    pygame.draw.lines(screen, (20, 80, 20), False, points, 16 + int(breath))

    pygame.draw.lines(screen, (40, 180, 60), False, points, 6)

    for i in range(2, len(points) - 5, 4):
        p_curr = points[i]
        p_next = points[i + 1]

        dx, dy = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
        angle = math.atan2(dy, dx)

        spine_len = 10
        sx = p_curr[0] + math.sin(angle) * spine_len
        sy = p_curr[1] - math.cos(angle) * spine_len

        pygame.draw.circle(screen, (200, 190, 140), (int(sx), int(sy)), 3)

    hx, hy = points[0]

    head_color = (20, 100, 30)
    pygame.draw.circle(screen, (10, 30, 10), (hx, hy), 18)  # Outline kepala
    pygame.draw.circle(screen, head_color, (hx, hy), 14)  # Isi kepala

    pygame.draw.circle(screen, (15, 80, 25), (hx, hy + 8), 10)

    eye_color = (255, 200, 0) if not glow else (255, 0, 0)
    pygame.draw.line(
        screen, (0, 0, 0), (hx - 6, hy - 4), (hx - 10, hy - 8), 5
    )  # Alis garang
    pygame.draw.line(
        screen, (0, 0, 0), (hx + 6, hy - 4), (hx + 10, hy - 8), 5
    )  # Alis garang

    pygame.draw.circle(screen, eye_color, (hx - 5, hy - 2), 3)  # Mata Kiri
    pygame.draw.circle(screen, eye_color, (hx + 5, hy - 2), 3)  # Mata Kanan

    horn_col = (220, 210, 180)
    pygame.draw.line(screen, horn_col, (hx - 8, hy - 10), (hx - 18, hy - 25), 4)
    pygame.draw.line(screen, horn_col, (hx + 8, hy - 10), (hx + 18, hy - 25), 4)

    pygame.draw.circle(screen, (0, 20, 0), (hx - 3, hy + 10), 1)
    pygame.draw.circle(screen, (0, 20, 0), (hx + 3, hy + 10), 1)

def draw_ladder(start, end, glow=False):
    sx, sy = board_xy(start)
    ex, ey = board_xy(end)

    wood_main = (60, 40, 20)
    wood_light = (90, 65, 35)  # Highlight pinggiran
    wood_dark = (30, 20, 10)  # Shading dalam

    iron_col = (50, 50, 55)

    width = 14

    l1 = (sx - width, sy)
    r1 = (sx + width, sy)
    l2 = (ex - width, ey)
    r2 = (ex + width, ey)

    pygame.draw.line(
        screen, (0, 0, 0, 80), (l1[0] + 6, l1[1] + 6), (l2[0] + 6, l2[1] + 6), 6
    )
    pygame.draw.line(
        screen, (0, 0, 0, 80), (r1[0] + 6, r1[1] + 6), (r2[0] + 6, r2[1] + 6), 6
    )

    steps = 9  # Jumlah anak tangga
    for i in range(steps + 1):
        t = i / steps
        px1, py1 = lerp(l1[0], l2[0], t), lerp(l1[1], l2[1], t)
        px2, py2 = lerp(r1[0], r2[0], t), lerp(r1[1], r2[1], t)

        pygame.draw.line(
            screen, (0, 0, 0, 100), (px1 + 4, py1 + 4), (px2 + 4, py2 + 4), 8
        )

        pygame.draw.line(screen, wood_dark, (px1, py1), (px2, py2), 10)  # Outline tebal
        pygame.draw.line(
            screen, wood_main, (px1 + 1, py1), (px2 - 1, py2), 6
        )  # Isi kayu

        pygame.draw.line(screen, wood_light, (px1 + 2, py1 - 2), (px2 - 2, py2 - 2), 2)

        pygame.draw.circle(screen, iron_col, (int(px1), int(py1)), 4)
        pygame.draw.circle(screen, iron_col, (int(px2), int(py2)), 4)
        pygame.draw.circle(screen, (100, 100, 110), (int(px1) - 1, int(py1) - 1), 1)
        pygame.draw.circle(screen, (100, 100, 110), (int(px2) - 1, int(py2) - 1), 1)

    pygame.draw.line(screen, wood_dark, l1, l2, 10)  # Outline gelap
    pygame.draw.line(screen, wood_main, l1, l2, 6)  # Warna utama

    pygame.draw.line(screen, wood_dark, r1, r2, 10)
    pygame.draw.line(screen, wood_main, r1, r2, 6)

    if glow:
        glow_col = (255, 215, 0)  # Emas
        pygame.draw.line(screen, glow_col, l1, l2, 2)
        pygame.draw.line(screen, glow_col, r1, r2, 2)
        pygame.draw.circle(screen, glow_col, (int(l1[0]), int(l1[1])), 5)
        pygame.draw.circle(screen, glow_col, (int(r2[0]), int(r2[1])), 5)

def draw_pion(pos, color, offset, idx):
    x, y = board_xy(pos)

    bounce = int(6 * abs(math.sin(bounce_phase[idx])))
    bounce_phase[idx] += BOUNCE_SPEED

    pulse_scale[idx] += (1.0 - pulse_scale[idx]) * 0.15
    r = int(12 * pulse_scale[idx])  # Radius dasar

    cx = x + offset
    cy = y - bounce

    if idx == state.turn:
        time_ms = pygame.time.get_ticks()

        angle_offset = time_ms * 0.002
        radius_ring = 22

        for k in range(3):
            start_angle = angle_offset + (k * (2 * math.pi / 3))
            end_angle = start_angle + 1.5  # Panjang busur

            arc_points = []
            for j in range(10):
                theta = start_angle + (end_angle - start_angle) * (j / 9)
                ax = cx + math.cos(theta) * radius_ring
                ay = (y + 15) + math.sin(theta) * (
                    radius_ring * 0.5
                )  # Dibuat gepeng (perspektif isometrik)
                arc_points.append((ax, ay))

            if len(arc_points) > 1:
                aura_col = (*color, 200)
                pygame.draw.lines(screen, color, False, arc_points, 2)

        pulse = (math.sin(time_ms * 0.005) + 1) * 0.5  # 0.0 s/d 1.0
        inner_r = 10 + (pulse * 5)

        glow_surf = pygame.Surface((60, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(
            glow_surf,
            (*color, 100 - int(pulse * 50)),
            (30 - inner_r, 20 - inner_r / 2, inner_r * 2, inner_r),
            0,
        )
        screen.blit(glow_surf, (cx - 30, y + 15 - 20))

    shadow_col = [max(c - 60, 0) for c in color]
    deep_shadow = [max(c - 100, 0) for c in color]
    highlight_col = [min(c + 90, 255) for c in color]

    shadow_w = max(4, r * 2 - bounce // 2)
    pygame.draw.ellipse(
        screen, (20, 20, 30, 80), (cx - shadow_w // 2, y + 15, shadow_w, 6)
    )

    cloak_rect = (cx - r - 5, cy - 2, (r + 5) * 2, r * 2 + 4)
    pygame.draw.arc(screen, shadow_col, cloak_rect, 0, 3.14, 4)

    body_poly = [
        (cx - r - 2, cy + r + 4),
        (cx + r + 2, cy + r + 4),
        (cx + r + 6, cy - 4),
        (cx - r - 6, cy - 4),
    ]
    pygame.draw.polygon(screen, deep_shadow, body_poly)  # Outline
    pygame.draw.polygon(screen, color, [(p[0], p[1] - 2) for p in body_poly])  # Isi

    helm_rect = pygame.Rect(cx - r + 2, cy - r - 12, (r - 2) * 2, r + 8)
    pygame.draw.rect(
        screen, color, helm_rect, border_top_left_radius=6, border_top_right_radius=6
    )

    pygame.draw.rect(screen, (10, 10, 15), (cx - r + 5, cy - r - 3, (r - 5) * 2, 3))

    if idx == state.turn:
        pygame.draw.line(screen, (255, 50, 50), (cx, cy - r - 12), (cx, cy - r - 18), 3)

    shield_pts = [
        (cx - r - 8, cy),
        (cx - r - 2, cy),
        (cx - r - 2, cy + 14),
        (cx - r - 5, cy + 18),
        (cx - r - 8, cy + 14),
    ]
    pygame.draw.polygon(screen, highlight_col, shield_pts)
    pygame.draw.polygon(screen, (30, 30, 40), shield_pts, 1)  # Outline perisai

    pygame.draw.line(
        screen, (255, 255, 255), (cx - r + 4, cy - r - 10), (cx - r + 4, cy - 6), 2
    )

def draw_cinematic_overlay(target_pos_idx):
    """Efek Vignette (Pinggir Gelap) dan Spotlight (Sorotan Cahaya)"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 5, 0, 120))  # Gelap kecoklatan (Vignette)

    if 0 <= target_pos_idx < len(players):
        px, py = board_xy(positions[target_pos_idx])

        spotlight = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        pygame.draw.circle(spotlight, (255, 255, 255, 255), (px, py), 130)

        for i in range(50):
            pygame.draw.circle(spotlight, (255, 255, 255, 5), (px, py), 130 + i * 2)

        overlay.blit(spotlight, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    screen.blit(overlay, (0, 0))

sidebar_snapshot = None
last_history_len = -1

def draw_panel():
    global sidebar_snapshot, last_history_len

    full_log = log_manager.get_full_log()
    sidebar_rect = pygame.Rect(WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)

    current_len = len(full_log)
    if current_len != last_history_len:
        sidebar_snapshot = None

    if sidebar_snapshot is not None:
        screen.blit(sidebar_snapshot, (WIDTH - SIDEBAR_WIDTH, 0))
        draw_current_turn_header()
        return

    last_history_len = current_len

    if RIGHT_SIDEBAR_BG:
        screen.blit(RIGHT_SIDEBAR_BG, (WIDTH - SIDEBAR_WIDTH, 0))

        overlay = pygame.Surface((SIDEBAR_WIDTH, HEIGHT), pygame.SRCALPHA)

        overlay.fill((20, 23, 30, 180))

        screen.blit(overlay, (WIDTH - SIDEBAR_WIDTH, 0))
    else:
        pygame.draw.rect(screen, (25, 28, 35), sidebar_rect)

    pygame.draw.line(
        screen,
        (10, 10, 15),
        (WIDTH - SIDEBAR_WIDTH, 0),
        (WIDTH - SIDEBAR_WIDTH, HEIGHT),
        4,
    )
    pygame.draw.line(
        screen,
        (60, 50, 40),
        (WIDTH - SIDEBAR_WIDTH + 4, 0),
        (WIDTH - SIDEBAR_WIDTH + 4, HEIGHT),
        1,
    )

    draw_current_turn_header()

    sidebar_helper.draw_history_ui(
        screen,
        full_log,
        players,
        colors,
        challenges,
        start_y=135,
        sidebar_width=SIDEBAR_WIDTH,
        width_total=WIDTH,
    )

    sidebar_snapshot = screen.subsurface(sidebar_rect).copy()
    log_manager.sidebar_snapshot = sidebar_snapshot

def draw_current_turn_header():
    """
    Menggunakan Font Custom sepenuhnya.
    """
    curr_idx = state.turn
    curr_name = players[curr_idx]
    curr_col = colors[curr_idx]

    card_margin_x = 12
    card_w = SIDEBAR_WIDTH - (card_margin_x * 2)
    card_h = 85  # Tinggi kartu yang compact tapi lega

    card_x = WIDTH - SIDEBAR_WIDTH + card_margin_x
    card_y = 20  # Jarak dari atas layar

    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

    shadow_rect = card_rect.move(0, 4)
    pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=12)

    pygame.draw.rect(screen, (30, 32, 40), card_rect, border_radius=12)

    pygame.draw.rect(screen, curr_col, card_rect, 1, border_radius=12)

    avatar_size = 56  # Ukuran avatar
    av_padding = 10  # Jarak avatar dari pinggir kiri kartu

    av_center_x = card_x + av_padding + (avatar_size // 2)
    av_center_y = (
        card_y + (card_h // 2) - 4
    )  # Sedikit ke atas karena ada progress bar di bawah

    pygame.draw.circle(
        screen, (20, 20, 25), (av_center_x, av_center_y), (avatar_size // 2) + 2
    )
    pygame.draw.circle(
        screen, curr_col, (av_center_x, av_center_y), (avatar_size // 2), 1
    )  # Ring tipis warna player

    if curr_idx < len(hero_avatars):
        raw_img = hero_avatars[curr_idx]
        av_img = pygame.transform.smoothscale(
            raw_img, (avatar_size - 6, avatar_size - 6)
        )
        av_rect = av_img.get_rect(center=(av_center_x, av_center_y))
        screen.blit(av_img, av_rect)

    text_start_x = av_center_x + (avatar_size // 2) + 12
    text_center_y = av_center_y

    try:
        lbl_font = pygame.font.Font(FONT_FILE, 10)
        name_font = pygame.font.Font(FONT_FILE, 22)
        info_font = pygame.font.Font(FONT_FILE, 12)
    except:
        lbl_font = pygame.font.SysFont("georgia", 9, bold=True)
        name_font = pygame.font.SysFont("georgia", 20, bold=True)
        info_font = pygame.font.SysFont("arial", 11)

    lbl_surf = lbl_font.render("CURRENT TURN", True, (150, 160, 170))
    screen.blit(lbl_surf, (text_start_x, text_center_y - 24))

    lum = 0.299 * curr_col[0] + 0.587 * curr_col[1] + 0.114 * curr_col[2]
    name_color = (255, 255, 255) if lum < 120 else (20, 20, 20)
    if lum > 120:
        name_color = (240, 240, 230)  # Putih tulang jika player gelap

    name_shadow = name_font.render(curr_name, True, (0, 0, 0))
    screen.blit(name_shadow, (text_start_x + 1, text_center_y - 8))

    name_surf = name_font.render(
        curr_name, True, curr_col
    )  # Pakai warna player biar keren
    screen.blit(name_surf, (text_start_x, text_center_y - 9))

    pos_val = positions[curr_idx]
    info_text = f"Tile: {pos_val} / {TOTAL}"
    info_surf = info_font.render(info_text, True, (180, 180, 180))
    screen.blit(info_surf, (text_start_x, text_center_y + 14))

    bar_h = 4
    bar_w = card_w - 20  # Padding kiri kanan 10
    bar_x = card_x + 10
    bar_y = card_y + card_h - 10  # 10px dari bawah kartu

    pygame.draw.rect(
        screen, (20, 20, 25), (bar_x, bar_y, bar_w, bar_h), border_radius=2
    )

    progress = pos_val / TOTAL
    fill_w = int(bar_w * progress)
    if fill_w > 0:
        glow_surf = pygame.Surface((fill_w + 4, bar_h + 4), pygame.SRCALPHA)
        pygame.draw.rect(
            glow_surf, (*curr_col, 100), (0, 0, fill_w + 4, bar_h + 4), border_radius=4
        )
        screen.blit(glow_surf, (bar_x - 2, bar_y - 2))

        pygame.draw.rect(
            screen, curr_col, (bar_x, bar_y, fill_w, bar_h), border_radius=2
        )

def redraw(active_snake: Optional[int] = None, active_ladder: Optional[int] = None):
    shake_x, shake_y = 0, 0
    if state.shake_intensity > 0.5:
        shake_x = random.randint(
            -int(state.shake_intensity), int(state.shake_intensity)
        )
        shake_y = random.randint(
            -int(state.shake_intensity), int(state.shake_intensity)
        )
        state.shake_intensity *= state.shake_decay

    draw_background_effects(screen, shake_x, shake_y)

    if "left_sidebar_visual" in globals():
        left_sidebar_visual.draw(screen, shake_x, shake_y)

    renderer.draw_board(state)

    board_rect = pygame.Rect(
        SIDEBAR_LEFT_WIDTH - 5, -5, (COLS * CELL) + 10, (ROWS * CELL) + 10
    )
    pygame.draw.rect(screen, (80, 80, 90), board_rect, 6, border_radius=4)
    pygame.draw.rect(screen, (40, 40, 50), board_rect, 2, border_radius=4)

    for start, end in state.ladders.items():
        is_active = start == active_ladder
        renderer.draw_ladder(start, end, glow=is_active)

    for start, end in state.snakes.items():
        is_active = start == active_snake
        renderer.draw_snake(start, end, glow=is_active)

    for i in range(len(state.players)):
        stack_offset = (i * 8) - 12
        renderer.draw_pion(state, i, offset=stack_offset)

    renderer.draw_panel(state, sidebar_helper)

    if state.shake_intensity > 1:
        current_screen = screen.copy()
        screen.fill((0, 0, 0))
        screen.blit(current_screen, (shake_x, shake_y))

    pygame.display.flip()

def redraw_for_animation(moving_idx, anim_x, anim_y, jump_h=0):
    screen.fill((180, 200, 220))
    draw_background_effects(screen)
    if "left_sidebar_visual" in globals():
        left_sidebar_visual.draw(screen)

    renderer.draw_board(state)
    board_rect = pygame.Rect(
        SIDEBAR_LEFT_WIDTH - 5, -5, (COLS * CELL) + 10, (ROWS * CELL) + 10
    )
    pygame.draw.rect(screen, (80, 80, 90), board_rect, 6, border_radius=4)
    pygame.draw.rect(screen, (40, 40, 50), board_rect, 2, border_radius=4)

    for s, e in state.ladders.items():
        renderer.draw_ladder(s, e)
    for s, e in state.snakes.items():
        renderer.draw_snake(s, e)

    for i in range(len(state.players)):
        if i == moving_idx:
            continue
        stack_offset = (i * 8) - 12
        renderer.draw_pion(state, i, offset=stack_offset)

    stack_offset = (moving_idx * 8) - 12

    render_x = anim_x + stack_offset
    render_y = anim_y

    shadow_size = max(4, 12 - int(jump_h * 0.15))
    pygame.draw.circle(
        screen, (0, 0, 0, 60), (int(render_x), int(anim_y + 18)), shadow_size
    )

    stretch = 1.0 + (jump_h * 0.015)  # Sedikit lebih melar biar kartunis
    p_w = int(26 / stretch)
    p_h = int(26 * stretch)

    visual_y = render_y - jump_h - p_h - 15

    rect = pygame.Rect(render_x - p_w // 2, visual_y, p_w, p_h)

    pygame.draw.ellipse(screen, colors[moving_idx], rect)
    pygame.draw.ellipse(
        screen,
        (255, 255, 255),
        (rect.x + p_w // 3, rect.y + p_h // 4, p_w // 3, p_h // 4),
        0,
    )

    draw_panel()
    pygame.display.flip()

def animate_dice_roll() -> int:
    start_ms = pygame.time.get_ticks()
    last_frame = start_ms
    face = 1
    play_sound(dice_roll)

    while True:
        now = pygame.time.get_ticks()
        elapsed = now - start_ms

        if now - last_frame >= DICE_FRAME_DELAY:
            face = random.randint(1, 6)
            last_frame = now

        redraw()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 190))
        screen.blit(overlay, (0, 0))

        dice_rect = dice_images[face].get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        screen.blit(dice_images[face], dice_rect)

        label = big_font.render(f"Mengocok...", True, (0, 0, 0))
        screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

        pygame.display.flip()
        clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()

        if elapsed >= DICE_ANIM_TIME:
            break

    redraw()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 100))  # Lebih terang sedikit saat freeze
    screen.blit(overlay, (0, 0))
    screen.blit(dice_images[face], dice_rect)

    final_label = big_font.render(f"Hasil: {face}", True, (0, 0, 0))
    screen.blit(
        final_label, final_label.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    )

    pygame.display.flip()

    pygame.time.delay(700)

    play_sound(dice_end)
    return face

def animate_move_piece(idx: int, final_target: int):
    """
    Visual-only animation loop. Non-blocking.
    Handles smooth token interpolation to target.
    """
    final_target = overflow_reflect(final_target)
    start_pos = positions[idx]

    total_steps = abs(final_target - start_pos)
    direction = 1 if final_target > start_pos else -1

    STEP_DURATION = 130

    for i in range(1, total_steps + 1):
        next_tile = start_pos + (i * direction)

        prev_tile = next_tile - direction
        start_x, start_y = board_xy(prev_tile)
        end_x, end_y = board_xy(next_tile)

        if step_sound:
            step_sound.stop()
            step_sound.play()

        anim_start = pygame.time.get_ticks()

        while True:
            now = pygame.time.get_ticks()
            t = (now - anim_start) / STEP_DURATION

            if t >= 1.0:
                redraw_for_animation(idx, end_x, end_y, jump_h=0)
                break

            curr_x = start_x + (end_x - start_x) * t
            curr_y = start_y + (end_y - start_y) * t

            jump_height = math.sin(t * math.pi) * 55

            redraw_for_animation(idx, curr_x, curr_y, jump_h=jump_height)
            clock.tick(60)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()

        positions[idx] = next_tile

        pygame.display.flip()

    state.pulse_scale[idx] = 1.6
    final_x, final_y = board_xy(final_target)
    redraw_for_animation(idx, final_x, final_y, jump_h=0)

def show_victory_screen(screen, winner_name, winner_color):
    """
    Theme: Ember Ascension (Particle System).
    Renders dark background with floating ember particles.
    """
    try:
        title_font = pygame.font.Font(FONT_FILE, 90)
        sub_font = pygame.font.Font(FONT_FILE, 40)
        hint_font = pygame.font.Font(FONT_FILE, 16)
    except:
        title_font = pygame.font.SysFont("georgia", 80, bold=True)
        sub_font = pygame.font.SysFont("georgia", 30)
        hint_font = pygame.font.SysFont("arial", 12)

    embers = []
    for _ in range(150):
        embers.append(
            {
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT),
                "speed": random.uniform(0.5, 2.0),
                "size": random.randint(2, 4),
                "alpha": random.randint(50, 255),
                "drift": random.uniform(-0.5, 0.5),  # Gerakan kiri-kanan angin
            }
        )

    clock = pygame.time.Clock()
    running_victory = True

    pulse_val = 0

    while running_victory:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                running_victory = False

        screen.fill((10, 8, 8))  # Hampir hitam, sedikit merah gelap

        for p in embers:
            p["y"] -= p["speed"]  # Naik ke atas
            p["x"] += p["drift"]

            if p["y"] < -10:
                p["y"] = HEIGHT + 10
                p["x"] = random.randint(0, WIDTH)
                p["alpha"] = 255

            if p["alpha"] > 0:
                p["alpha"] -= 0.5

            s = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)

            col_core = (255, 200, 100, int(p["alpha"]))
            pygame.draw.circle(s, col_core, (p["size"], p["size"]), p["size"])
            screen.blit(s, (p["x"], p["y"]))

        center_x, center_y = WIDTH // 2, HEIGHT // 2 - 30

        pulse = (math.sin(pulse_val) + 1) * 0.5  # 0.0 - 1.0
        pulse_r = 100 + (pulse * 20)

        aura_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
        pygame.draw.circle(
            aura_surf, (100, 10, 10, 50), (150, 150), pulse_r
        )  # Merah darah transparan
        screen.blit(aura_surf, (center_x - 150, center_y - 150))

        cx, cy = center_x, center_y

        hero_base = tuple(min(c + 40, 255) for c in winner_color)
        lum = (
            0.299 * winner_color[0] + 0.587 * winner_color[1] + 0.114 * winner_color[2]
        )
        is_dark = lum < 90
        outline_col = (180, 180, 180) if is_dark else (20, 20, 30)  # Silver kusam
        visor_col = (200, 200, 200) if is_dark else (40, 40, 50)

        pygame.draw.circle(screen, outline_col, (cx, cy + 40), 50)  # Bahu
        pygame.draw.circle(screen, hero_base, (cx, cy + 40), 45)
        pygame.draw.circle(screen, outline_col, (cx, cy - 20), 45)  # Kepala
        pygame.draw.circle(screen, hero_base, (cx, cy - 20), 40)

        pygame.draw.rect(
            screen, visor_col, (cx - 20, cy - 20, 40, 10), border_radius=2
        )  # Mata
        pygame.draw.rect(
            screen, visor_col, (cx - 6, cy - 20, 12, 35), border_radius=2
        )  # Hidung

        pulse_val += 0.05

        title_col = (180, 170, 170)
        title_surf = title_font.render("VICTORY", True, title_col)

        shadow_surf = title_font.render("VICTORY", True, (10, 5, 5))
        screen.blit(
            shadow_surf, (center_x - title_surf.get_width() // 2 + 4, center_y + 84)
        )
        screen.blit(title_surf, (center_x - title_surf.get_width() // 2, center_y + 80))

        line_w = 200 + (pulse * 50)
        pygame.draw.line(
            screen,
            (150, 50, 50),
            (center_x - line_w / 2, center_y + 160),
            (center_x + line_w / 2, center_y + 160),
            3,
        )

        name_text = f"Lord {winner_name} has claimed the throne."
        name_surf = sub_font.render(name_text, True, (200, 180, 100))  # Emas Kusam
        screen.blit(name_surf, (center_x - name_surf.get_width() // 2, center_y + 180))

        hint_surf = hint_font.render(
            "[ PRESS ANY KEY TO END THE CHRONICLE ]", True, (80, 80, 80)
        )
        screen.blit(hint_surf, (center_x - hint_surf.get_width() // 2, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)

running = True
redraw()  # Gambar papan game dalam keadaan tertutup layar hitam (karena efek sebelumnya)
fade_from_dark(screen, dark_overlay, WIDTH, HEIGHT)

while running:
    redraw()
    clock.tick(60)

    p_config = {
        "WIDTH": WIDTH,
        "HEIGHT": HEIGHT,
        "IMAGE_DIR": IMAGE_DIR,
        "big_font": big_font,
        "font": font,
        "small_font": small_font,
        "get_challenge_image": get_challenge_image,
        "get_timer_duration": get_timer_duration,
        "get_move_effect": get_move_effect,
        "clock": clock,
        "scroll_truth_img": SCROLL_TRUTH_IMG,  # ← TAMBAH INI
        "scroll_dare_img": SCROLL_DARE_IMG,  # ← TAMBAH INI
    }

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            action = show_pause_menu(screen, p_config)

            if action == "RESUME":
                pass
            elif action == "MAIN_MENU":

                players, game_level = show_main_menu(screen, p_config)

                state.reset_for_new_game(players, game_level)

                state.snakes, state.ladders = generate_random_objects(TOTAL, 3, 2)

                try:
                    fname = f"challenges_lv{game_level}.json"
                    if "resource_path" in globals():
                        target = resource_path(fname)
                    else:
                        target = os.path.join(BASE_DIR, fname)

                    with open(target, encoding="utf-8") as f:
                        raw_data = json.load(f)

                    CHALLENGE_DECK = ChallengeDeck(raw_data)
                    state.challenges = distribute_random_challenges(
                        CHALLENGE_DECK, state.snakes, state.ladders, 40
                    )
                except:
                    state.challenges = {}

                positions = state.positions
                colors = state.colors
                bounce_phase = state.bounce_phase
                pulse_scale = state.pulse_scale
                snakes = state.snakes
                ladders = state.ladders
                challenges = state.challenges
                log_manager = state.log_manager
                history = log_manager.history
                current_turn_log = log_manager.current_turn_log

                redraw()

        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            start_turn(players[state.turn])
            dice = animate_dice_roll()
            log_turn(f"Dice: {dice}")

            target = positions[state.turn] + dice
            animate_move_piece(state.turn, target)

            active_snake = None
            active_ladder = None

            if positions[state.turn] in snakes:
                active_snake = positions[state.turn]
                popup_manager.show_popup(screen, " Oh no! Snake!", None, p_config)
                positions[state.turn] = snakes[positions[state.turn]]
                log_turn(": Slid Down Snake")
                animate_move_piece(state.turn, positions[state.turn])

            elif positions[state.turn] in ladders:
                active_ladder = positions[state.turn]
                popup_manager.show_popup(screen, " Climp Up!", None, p_config)
                positions[state.turn] = ladders[positions[state.turn]]
                log_turn(": Climbed Ladder")
                animate_move_piece(state.turn, positions[state.turn])

            text = challenges.get(str(positions[state.turn]), "")
            if text:
                while True:
                    move_effect = popup_manager.show_popup(
                        screen, text, positions[state.turn], p_config
                    )

                    if move_effect == "NEXT":
                        current_type = "truth"  # Default
                        text_lower = text.lower()

                        if "dare" in text_lower or "tantangan" in text_lower:
                            current_type = "dare"
                        elif "truth" in text_lower or "kebenaran" in text_lower:
                            current_type = "truth"

                        new_card = CHALLENGE_DECK.draw_card(current_type)

                        challenges[str(positions[state.turn])] = new_card
                        text = new_card

                        try:
                            shuffle_sound = pygame.mixer.Sound(
                                os.path.join(BASE_DIR, "sounds", "shuffle.wav")
                            )
                            shuffle_sound.play()
                        except:
                            pass

                        redraw()
                        continue

                    else:
                        log_turn(text)

                        current_type = "truth"
                        text_lower = text.lower()

                        if "dare" in text_lower or "tantangan" in text_lower:
                            current_type = "dare"
                        elif "truth" in text_lower or "kebenaran" in text_lower:
                            current_type = "truth"

                        new_card = CHALLENGE_DECK.draw_card(current_type)

                        challenges[str(positions[state.turn])] = new_card

                        if move_effect != 0:
                            new_target = max(
                                1, min(TOTAL, positions[state.turn] + move_effect)
                            )
                            animate_move_piece(state.turn, new_target)
                            positions[state.turn] = new_target

                        break

            if positions[state.turn] == TOTAL:
                show_victory_screen(screen, players[state.turn], colors[state.turn])
                running = False

            end_turn()
            state.turn = (state.turn + 1) % len(players)

            pygame.event.clear()  # 1. Clear event queue to prevent input buffering.

pygame.quit()
