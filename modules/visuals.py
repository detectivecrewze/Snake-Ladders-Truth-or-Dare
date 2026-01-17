import pygame
import math
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_constants import *

current_w = WIDTH 
current_h = HEIGHT
bg_particles = []

def init_particles_dynamic(width, height):
    """
    Menginisialisasi ulang partikel dengan ukuran layar yang BENAR.
    Fungsi ini WAJIB dipanggil dari game.py setelah screen dibuat.
    """
    global bg_particles, current_w, current_h
    
    current_w = width
    current_h = height
    bg_particles = []
    
    count = int(width / 30) 
    
    for _ in range(count):
        bg_particles.append({
            'x': random.randint(0, width),
            'y': random.randint(0, height),
            'speed': random.uniform(0.2, 0.8), # Kecepatan variatif
            'size': random.randint(2, 5)
        })

init_particles_dynamic(WIDTH, HEIGHT)

def lerp(a, b, t):
    return a + (b - a) * t

def get_tile_center(n):
    """Menghitung koordinat tengah kotak secara otomatis"""
    row = (n - 1) // COLS
    col = (n - 1) % COLS
    if row % 2 == 1:
        col = (COLS - 1) - col
    
    x = col * CELL + (CELL // 2)
    y = HEIGHT - (row * CELL + (CELL // 2)) # HEIGHT ini dari constants (tinggi board)
    return x, y

def draw_background_effects(screen, shake_x=0, shake_y=0):
    """Menggambar efek partikel background"""
    screen.fill(BG_COLOR) 
    
    for p in bg_particles:
        p['y'] -= p['speed']
        
        if p['y'] < -10: 
            p['y'] = current_h + 10
            p['x'] = random.randint(0, current_w) # Reset x acak juga agar organik
            
        s = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 40), (p['size'], p['size']), p['size'])
        screen.blit(s, (p['x'], p['y']))

def draw_snake(screen, start_node, end_node, glow=False):
    """Menggambar ular dengan nomor kotak sebagai input"""
    sx, sy = get_tile_center(start_node)
    ex, ey = get_tile_center(end_node)
    
    time_ms = pygame.time.get_ticks()
    points = []
    steps = 40 # Lebih halus
    
    for i in range(steps + 1):
        t = i / steps
        wave_anim = math.sin(t * math.pi * 2 + time_ms * 0.003) * 8
        x = lerp(sx, ex, t) + wave_anim * 0.5
        y = lerp(sy, ey, t) + math.sin(t * math.pi * 2) * 25 + wave_anim
        points.append((x, y))

    body_color = (50, 205, 50) if glow else (34, 139, 34)
    if len(points) > 1:
        pygame.draw.lines(screen, (20, 80, 20), False, points, 10) # Outer
        pygame.draw.lines(screen, body_color, False, points, 4)    # Inner
    
    if points:
        head = (int(points[0][0]), int(points[0][1]))
        pygame.draw.circle(screen, (0, 100, 0), head, 12)

def draw_ladder(screen, start_node, end_node, glow=False):
    """Menggambar tangga dengan nomor kotak sebagai input"""
    sx, sy = get_tile_center(start_node)
    ex, ey = get_tile_center(end_node)
    color = (255, 215, 0) if glow else (139, 69, 19)
    pygame.draw.line(screen, color, (sx, sy), (ex, ey), 8 if glow else 5)

def draw_scroll(screen, x, y):
    """Menggambar ikon gulungan (scroll)"""
    pygame.draw.rect(screen, (245, 222, 179), (x - 12, y - 10, 24, 20))