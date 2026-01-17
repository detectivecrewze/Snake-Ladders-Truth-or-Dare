"""
Victory Screen - Tampilan kemenangan
"""
import pygame
import random
import math
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from game_constants import WIDTH, HEIGHT, FONT_FILE

def show_victory_screen(screen, winner_name, winner_color):
    """
    [DARK MEDIEVAL VICTORY]
    Tema: 'The Ember Ascension'.
    Partikel bara api, latar gelap, dan teks besi kuno.
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
        embers.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT),
            'speed': random.uniform(0.5, 2.0),
            'size': random.randint(2, 4),
            'alpha': random.randint(50, 255),
            'drift': random.uniform(-0.5, 0.5) # Gerakan kiri-kanan angin
        })

    clock = pygame.time.Clock()
    running_victory = True
    
    pulse_val = 0

    while running_victory:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                running_victory = False

        screen.fill((10, 8, 8)) # Hampir hitam, sedikit merah gelap

        for p in embers:
            p['y'] -= p['speed'] # Naik ke atas
            p['x'] += p['drift']
            
            if p['y'] < -10:
                p['y'] = HEIGHT + 10
                p['x'] = random.randint(0, WIDTH)
                p['alpha'] = 255
            
            if p['alpha'] > 0:
                p['alpha'] -= 0.5
            
            s = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
            
            col_core = (255, 200, 100, int(p['alpha']))
            pygame.draw.circle(s, col_core, (p['size'], p['size']), p['size'])
            screen.blit(s, (p['x'], p['y']))

        center_x, center_y = WIDTH // 2, HEIGHT // 2 - 30
        
        pulse = (math.sin(pulse_val) + 1) * 0.5 # 0.0 - 1.0
        pulse_r = 100 + (pulse * 20)
        
        aura_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (100, 10, 10, 50), (150, 150), pulse_r) # Merah darah transparan
        screen.blit(aura_surf, (center_x - 150, center_y - 150))

        cx, cy = center_x, center_y
        
        hero_base = tuple(min(c + 40, 255) for c in winner_color)
        lum = 0.299 * winner_color[0] + 0.587 * winner_color[1] + 0.114 * winner_color[2]
        is_dark = lum < 90
        outline_col = (180, 180, 180) if is_dark else (20, 20, 30) # Silver kusam
        visor_col = (200, 200, 200) if is_dark else (40, 40, 50)

        pygame.draw.circle(screen, outline_col, (cx, cy + 40), 50) # Bahu
        pygame.draw.circle(screen, hero_base, (cx, cy + 40), 45)
        pygame.draw.circle(screen, outline_col, (cx, cy - 20), 45) # Kepala
        pygame.draw.circle(screen, hero_base, (cx, cy - 20), 40)
        
        pygame.draw.rect(screen, visor_col, (cx - 20, cy - 20, 40, 10), border_radius=2) # Mata
        pygame.draw.rect(screen, visor_col, (cx - 6, cy - 20, 12, 35), border_radius=2)  # Hidung

        pulse_val += 0.05
        
        title_col = (180, 170, 170) 
        title_surf = title_font.render("VICTORY", True, title_col)
        
        shadow_surf = title_font.render("VICTORY", True, (10, 5, 5))
        screen.blit(shadow_surf, (center_x - title_surf.get_width()//2 + 4, center_y + 84))
        screen.blit(title_surf, (center_x - title_surf.get_width()//2, center_y + 80))
        
        line_w = 200 + (pulse * 50)
        pygame.draw.line(screen, (150, 50, 50), (center_x - line_w/2, center_y + 160), (center_x + line_w/2, center_y + 160), 3)

        name_text = f"Lord {winner_name} has claimed the throne."
        name_surf = sub_font.render(name_text, True, (200, 180, 100)) # Emas Kusam
        screen.blit(name_surf, (center_x - name_surf.get_width()//2, center_y + 180))
        
        hint_surf = hint_font.render("[ PRESS ANY KEY TO END THE CHRONICLE ]", True, (80, 80, 80))
        screen.blit(hint_surf, (center_x - hint_surf.get_width()//2, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)
