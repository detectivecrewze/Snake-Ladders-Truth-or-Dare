"""
Fungsi Utilitas Game
"""
import os
import sys
import random
import re
import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from game_constants import TOTAL

def resource_path(relative_path):
    """ Mencari path file yang benar (baik saat dev maupun di dalam .exe) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_timer_duration(text):
    """Parse durasi timer dari teks tantangan"""
    text = text.lower()
    total_seconds = 0
    
    minute_match = re.search(r'(\d+)\s*(menit|min|m)', text)
    if minute_match:
        total_seconds += int(minute_match.group(1)) * 60
        
    second_match = re.search(r'(\d+)\s*(detik|sec|s)', text)
    if second_match:
        total_seconds += int(second_match.group(1))
    
    if total_seconds == 0:
        only_digit = re.search(r'(\d+)', text)
        if only_digit:
            total_seconds = int(only_digit.group(1))
        else:
            total_seconds = 30 # Default jika hanya kata "Tantangan" tanpa angka
            
    return total_seconds

def board_xy(n, COLS, ROWS, CELL):
    """Konversi nomor sel (1-based) ke posisi pixel (x, y) di board zigzag"""
    n = int(n) - 1
    row_idx = n // COLS
    col_idx = n % COLS
    row = ROWS - 1 - row_idx
    if (row_idx % 2) == 0:
        col = col_idx
    else:
        col = COLS - 1 - col_idx
    return col * CELL + CELL // 2, row * CELL + CELL // 2

def lerp(a, b, t):
    """Linear interpolation antara a dan b dengan faktor t (0.0 - 1.0)"""
    return a + (b - a) * t

def overflow_reflect(target):
    """Pantulkan jika target melewati TOTAL (overflow handling)"""
    if target > TOTAL:
        return TOTAL - (target - TOTAL)
    return target

def play_sound(snd):
    """Play sound jika tersedia"""
    if snd:
        try:
            snd.play()
        except Exception:
            pass

def fade_to_dark(screen, width, height):
    """Transisi Menu -> Gelap (Durasi ~1.5 Detik)"""
    overlay = pygame.Surface((width, height))
    medieval_dark = (15, 12, 10) 
    overlay.fill(medieval_dark)
    
    for alpha in range(0, 255, 3):
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(18) # Semakin besar angka ini, semakin lambat
        
    return overlay

def fade_from_dark(screen, overlay, width, height):
    """Transisi Gelap -> Game Board (Durasi ~1.5 Detik)"""
    board_snapshot = screen.copy()

    for alpha in range(255, -1, -3):
        screen.blit(board_snapshot, (0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        
        pygame.display.flip()
        pygame.time.delay(18)

def distribute_random_challenges(deck_system, ref_snakes, ref_ladders, amount=30):
    """Distribusikan tantangan secara acak ke kotak kosong di board"""
    distributed = {}
    
    forbidden = set(ref_snakes.keys()) | set(ref_ladders.keys()) | {1, TOTAL}
    available = [i for i in range(2, TOTAL) if i not in forbidden]
    random.shuffle(available)
    
    count = 0
    last_t = -1
    for t in available:
        if count >= amount: break
        
        if abs(t - last_t) > 1:
            card_type = random.choice(["truth", "dare"])
            distributed[str(t)] = deck_system.draw_card(card_type)
            last_t = t
            count += 1
            
    return distributed
