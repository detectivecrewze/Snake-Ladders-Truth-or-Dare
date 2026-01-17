import pygame
import sys
import os
import random
import math
import time

THEMES = {
    "MEDIEVAL": {
        "text": (255, 230, 200), 
        "accent": (255, 100, 50),
        "panel_bg": (30, 15, 10), 
        "panel_border": (180, 60, 20),
        "fallback_top": (10, 5, 8), 
        "fallback_bot": (40, 10, 5)
    },
    "RELAXING": {  # THEME GHIBLI / LANGIT
        "text": (20, 45, 75),           # [UBAH INI] Biru Navy Gelap (Agar tulisan terbaca di awan)
        "accent": (255, 140, 0),        # [UBAH INI] Oranye Tua (Agar tombol terlihat jelas)
        "panel_bg": (255, 255, 255, 180), # Panel Putih Transparan
        "panel_border": (100, 149, 237),# Border Cornflower Blue
        "fallback_top": (135, 206, 235), 
        "fallback_bot": (34, 139, 34)
    },
    "LOVES": {     # DULU: CINTA
        "text": (255, 105, 180),        # Pink Hot
        "accent": (255, 20, 147),       # Deep Pink
        "panel_bg": (255, 240, 245, 230), # Lavender Blush Transparan
        "panel_border": (255, 105, 180),
        "fallback_top": (255, 192, 203), 
        "fallback_bot": (255, 105, 180)
    }
}

current_theme_key = "MEDIEVAL"

def draw_heart(surface, x, y, size, color):
    """Menggambar hati untuk tema Loves"""
    ps = [(x, y + size // 4), (x - size // 2, y - size // 4), (x - size // 2, y - size // 2),
          (x - size // 4, y - size * 3 // 4), (x, y - size // 2), (x + size // 4, y - size * 3 // 4),
          (x + size // 2, y - size // 2), (x + size // 2, y - size // 4)]
    pygame.draw.polygon(surface, color, ps)

def draw_cloud(surface, x, y, size, color):
    """Menggambar awan untuk tema Relaxing"""
    pygame.draw.circle(surface, color, (x, y), size)
    pygame.draw.circle(surface, color, (x + size, y + size//4), int(size * 0.8))
    pygame.draw.circle(surface, color, (x - size, y + size//4), int(size * 0.8))

def render_background(screen, width, height, particles, bg_images):
    theme = THEMES[current_theme_key]
    
    bg_img = bg_images.get(current_theme_key)
    
    if bg_img:
        screen.blit(bg_img, (0, 0))
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        if current_theme_key == "MEDIEVAL": overlay.fill((0, 0, 0, 80)) 
        elif current_theme_key == "RELAXING": overlay.fill((255, 255, 255, 20)) # Overlay putih tipis
        else: overlay.fill((255, 200, 200, 30))
        screen.blit(overlay, (0,0))
    else:
        if current_theme_key == "MEDIEVAL":
            screen.fill(theme["fallback_top"])
            glow = pygame.Surface((width, 200), pygame.SRCALPHA)
            for i in range(200):
                alpha = int((i/200) * 100)
                pygame.draw.line(glow, (*theme["accent"], alpha), (0, i), (width, i))
            screen.blit(glow, (0, height - 200))
        elif current_theme_key == "RELAXING":
            screen.fill(theme["fallback_top"])
            pygame.draw.ellipse(screen, theme["fallback_bot"], (-100, height-250, width+200, 400))
        elif current_theme_key == "LOVES":
            screen.fill(theme["fallback_top"])
            pygame.draw.rect(screen, theme["fallback_bot"], (0, height-150, width, 150))

    for p in particles:
        p['y'] -= p['speed']
        p['x'] += math.sin(time.time() + p['y']*0.01) * 0.5
        if p['y'] < -20: 
            p['y'] = height + 20; p['x'] = random.randint(0, width)
        
        if current_theme_key == "MEDIEVAL":
            col = (255, random.randint(100, 200), 50)
            pygame.draw.circle(screen, col, (int(p['x']), int(p['y'])), random.randint(2, 4))
        elif current_theme_key == "RELAXING":
            draw_cloud(screen, int(p['x']), int(p['y']), p['size'], (255, 255, 255))
        elif current_theme_key == "LOVES":
            draw_heart(screen, int(p['x']), int(p['y']), p['size']*3, theme["accent"])

def show_main_menu(screen, config):
    global current_theme_key
    WIDTH, HEIGHT = config['WIDTH'], config['HEIGHT']
    
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(CURRENT_DIR)
    SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
    IMAGES_DIR = os.path.join(BASE_DIR, "images")

    bg_images = {}
    img_files = {
        "MEDIEVAL": "bg_medieval.png", 
        "RELAXING": "bg_ghibli.png", # File tetap pakai nama lama gpp
        "LOVES": "bg_cinta.png"
    }
    for key, fname in img_files.items():
        path = os.path.join(IMAGES_DIR, fname)
        if os.path.exists(path):
            try:
                raw = pygame.image.load(path).convert()
                bg_images[key] = pygame.transform.smoothscale(raw, (WIDTH, HEIGHT))
            except: pass

    sfx_hover, sfx_click = None, None
    try:
        if os.path.exists(os.path.join(SOUNDS_DIR, "hover.wav")):
            sfx_hover = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "hover.wav")); sfx_hover.set_volume(0.4)
        if os.path.exists(os.path.join(SOUNDS_DIR, "click.wav")):
            sfx_click = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "click.wav")); sfx_click.set_volume(0.8)
    except: pass

    def play_sfx(type):
        if type == "hover" and sfx_hover: sfx_hover.play()
        if type == "click" and sfx_click: sfx_click.play()

    def play_theme_music(theme_name):
        music_map = {"MEDIEVAL": "medieval_theme.mp3", "RELAXING": "ghibli_theme.mp3", "LOVES": "love_theme.mp3"}
        filename = music_map.get(theme_name, "menu_theme.mp3")
        path = os.path.join(SOUNDS_DIR, filename)
        if not os.path.exists(path): path = os.path.join(SOUNDS_DIR, "menu_theme.mp3")
        try:
            if os.path.exists(path):
                pygame.mixer.music.fadeout(500)
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)
        except: pass

    play_theme_music(current_theme_key)

    FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "medieval_font.ttf")
    try:
        title_font = pygame.font.Font(FONT_PATH, 90) 
        ui_font = pygame.font.Font(FONT_PATH, 35)
        input_font = pygame.font.Font(FONT_PATH, 40)
        small_font = pygame.font.Font(FONT_PATH, 20)
    except:
        title_font = pygame.font.SysFont("georgia", 70, bold=True)
        ui_font = pygame.font.SysFont("arial", 30)
        input_font = pygame.font.SysFont("arial", 36)
        small_font = pygame.font.SysFont("arial", 16)

    particles = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'speed': random.uniform(1, 3), 'size': random.randint(2, 5)} for _ in range(60)]
    
    state = "MAIN"
    idx_main = 0; idx_settings = 0; idx_player = 0; idx_level = 0
    num_players = 2; player_names = []; temp_name = ""
    last_hovered_btn = None
    clock = config['clock']
    running = True

    while running:
        theme = THEMES[current_theme_key]
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        current_hovered_btn = None
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1: mouse_clicked = True
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    play_sfx("click")
                    if state == "THEMES": state = "MAIN" # Balik ke MAIN
                    elif state == "SELECT_COUNT": state = "MAIN"
                    elif state == "INPUT_NAMES": state = "SELECT_COUNT"; player_names = []; temp_name = ""
                    elif state == "SELECT_LEVEL": state = "INPUT_NAMES"
                
                elif state == "MAIN":
                    if e.key == pygame.K_UP: idx_main = (idx_main - 1) % 3; play_sfx("hover")
                    elif e.key == pygame.K_DOWN: idx_main = (idx_main + 1) % 3; play_sfx("hover")
                    elif e.key == pygame.K_RETURN:
                        play_sfx("click")
                        if idx_main == 0: state = "SELECT_COUNT"
                        elif idx_main == 1: state = "THEMES" # Ke menu Themes
                        elif idx_main == 2: pygame.quit(); sys.exit()

                elif state == "THEMES":
                    if e.key == pygame.K_UP: idx_settings = (idx_settings - 1) % 4; play_sfx("hover")
                    elif e.key == pygame.K_DOWN: idx_settings = (idx_settings + 1) % 4; play_sfx("hover")
                    elif e.key == pygame.K_RETURN:
                        play_sfx("click"); old = current_theme_key
                        if idx_settings == 0: current_theme_key = "MEDIEVAL"
                        elif idx_settings == 1: current_theme_key = "RELAXING"
                        elif idx_settings == 2: current_theme_key = "LOVES"
                        elif idx_settings == 3: state = "MAIN"
                        if current_theme_key != old: play_theme_music(current_theme_key)

                elif state == "SELECT_COUNT":
                    if e.key in [pygame.K_LEFT, pygame.K_UP]: idx_player = 0; num_players = 2; play_sfx("hover")
                    elif e.key in [pygame.K_RIGHT, pygame.K_DOWN]: idx_player = 1; num_players = 3; play_sfx("hover")
                    elif e.key == pygame.K_RETURN: play_sfx("click"); state = "INPUT_NAMES"
                
                elif state == "INPUT_NAMES":
                    if e.key == pygame.K_RETURN:
                        final = temp_name.strip() if temp_name.strip() else f"Player {len(player_names)+1}"
                        player_names.append(final); temp_name = ""
                        if len(player_names) == num_players: state = "SELECT_LEVEL"
                    elif e.key == pygame.K_BACKSPACE: temp_name = temp_name[:-1]
                    elif len(temp_name) < 12 and e.unicode.isprintable(): temp_name += e.unicode

                elif state == "SELECT_LEVEL":
                    if e.key == pygame.K_LEFT: idx_level = (idx_level - 1) % 3; play_sfx("hover")
                    elif e.key == pygame.K_RIGHT: idx_level = (idx_level + 1) % 3; play_sfx("hover")
                    elif e.key == pygame.K_RETURN:
                        play_sfx("click"); selected_level = idx_level + 1; pygame.mixer.music.fadeout(1000)
                        return player_names, selected_level

        render_background(screen, WIDTH, HEIGHT, particles, bg_images)

        def draw_btn(text, cx, cy, w, h, is_hl, is_act=False):
            rect = pygame.Rect(0, 0, w, h); rect.center = (cx, cy)
            scale = 1.1 if is_hl else 1.0
            cur_w, cur_h = int(w*scale), int(h*scale)
            d_rect = pygame.Rect(0,0, cur_w, cur_h); d_rect.center = (cx, cy)
            
            bg_col = theme["panel_bg"]
            if len(bg_col) == 4:
                shape_surf = pygame.Surface((cur_w, cur_h), pygame.SRCALPHA)
                pygame.draw.rect(shape_surf, bg_col, shape_surf.get_rect(), border_radius=15)
                screen.blit(shape_surf, d_rect.topleft)
            else:
                pygame.draw.rect(screen, bg_col, d_rect, border_radius=15)
            
            border_c = theme["accent"] if (is_hl or is_act) else theme["panel_border"]
            pygame.draw.rect(screen, border_c, d_rect, 3 if is_hl else 1, border_radius=15)
            
            txt_col = theme["text"]
            if is_hl: txt_col = theme["accent"] # Text Highlight
            
            tsurf = ui_font.render(text, True, txt_col)
            screen.blit(tsurf, tsurf.get_rect(center=(cx, cy)))
            return d_rect

        # --- JUDUL & SUBTITLE ---
        float_offset = math.sin(time.time() * 2) * 6
        title_y = (HEIGHT // 5) + float_offset
        
        # 1. Judul Utama
        title_txt = title_font.render("Snake & Ladder", True, theme["accent"])
        t_shad = title_font.render("Snake & Ladder", True, (0,0,0))
        tr = title_txt.get_rect(center=(WIDTH//2, title_y))
        
        # 2. Subtitle (Truth or Dare Edition) - DIBUAT BOLD MANUAL
        sub_text_str = "Truth or Dare Edition"
        sub_col = theme["text"]
        
        # Render Teks Utama
        sub_txt = input_font.render(sub_text_str, True, sub_col) 
        sub_rect = sub_txt.get_rect(center=(WIDTH//2, title_y + 65))

        # Render Outline (Bayangan di 4 arah agar terlihat TEBAL)
        outline_col = (255, 255, 255) if current_theme_key == "RELAXING" else (0, 0, 0)
        offsets = [(-2, 0), (2, 0), (0, -2), (0, 2)] # Kiri, Kanan, Atas, Bawah
        
        # 3. Gambar Garis Dekorasi (Di samping Judul Utama)
        line_len = 80; gap = 25; mid_y = tr.centery + 5
        pygame.draw.line(screen, theme["accent"], (tr.left - gap - line_len, mid_y), (tr.left - gap, mid_y), 3)
        pygame.draw.circle(screen, theme["text"], (tr.left - gap - line_len, mid_y), 4)
        pygame.draw.line(screen, theme["accent"], (tr.right + gap, mid_y), (tr.right + gap + line_len, mid_y), 3)
        pygame.draw.circle(screen, theme["text"], (tr.right + gap + line_len, mid_y), 4)

        # 4. Render ke Layar
        # A. Judul Utama
        screen.blit(t_shad, (tr.x+4, tr.y+4)) 
        screen.blit(title_txt, tr)
        
        # B. Subtitle (Gambar Outline dulu, baru teks utama)
        for dx, dy in offsets:
            shadow_surf = input_font.render(sub_text_str, True, outline_col)
            screen.blit(shadow_surf, (sub_rect.x + dx, sub_rect.y + dy))
        
        screen.blit(sub_txt, sub_rect)

        # Geser tombol menu
        menu_start_y = title_y + 190 

        if state == "MAIN":
            items = ["START GAME", "THEMES", "EXIT"] # Nama menu diperbarui
            for i, item in enumerate(items):
                btn = draw_btn(item, WIDTH//2, menu_start_y + (i*70), 280, 55, (i==idx_main))
                if btn.collidepoint(mouse_pos):
                    idx_main = i; current_hovered_btn = f"m_{i}"
                    if mouse_clicked:
                        play_sfx("click")
                        if i==0: state="SELECT_COUNT"
                        elif i==1: state="THEMES"
                        elif i==2: pygame.quit(); sys.exit()

        elif state == "THEMES": # Ganti SETTINGS jadi THEMES
            lbl_y = menu_start_y - 40
            lbl = small_font.render("- SELECT THEME -", True, theme["text"])
            screen.blit(lbl, lbl.get_rect(center=(WIDTH//2, lbl_y)))
            
            opts = ["MEDIEVAL", "RELAXING", "LOVES", "BACK"] # Opsi baru
            settings_btn_y = lbl_y + 50 
            
            for i, opt in enumerate(opts):
                disp = f"> {opt} <" if opt == current_theme_key else opt
                btn = draw_btn(disp, WIDTH//2, settings_btn_y + (i*65), 260, 50, (i==idx_settings))
                if btn.collidepoint(mouse_pos):
                    idx_settings = i; current_hovered_btn = f"s_{i}"
                    if mouse_clicked:
                        play_sfx("click"); old = current_theme_key
                        if i==0: current_theme_key="MEDIEVAL"
                        elif i==1: current_theme_key="RELAXING"
                        elif i==2: current_theme_key="LOVES"
                        elif i==3: state="MAIN"
                        if current_theme_key != old: play_theme_music(current_theme_key)

        elif state == "SELECT_COUNT":
            lbl_y = menu_start_y - 20
            lbl = ui_font.render("How many players?", True, theme["text"])
            screen.blit(lbl, lbl.get_rect(center=(WIDTH//2, lbl_y)))
            if draw_btn("< BACK", 80, HEIGHT-50, 120, 40, False).collidepoint(mouse_pos) and mouse_clicked: state="MAIN"; play_sfx("click")
            
            coords = [(WIDTH//2-100, lbl_y + 80), (WIDTH//2+100, lbl_y + 80)]
            vals = [2, 3]
            for i, pos in enumerate(coords):
                is_hl = (i==idx_player)
                btn = draw_btn(f"{vals[i]} Players", pos[0], pos[1], 180, 100, is_hl, (num_players==vals[i]))
                if btn.collidepoint(mouse_pos):
                    idx_player = i; current_hovered_btn = f"p_{i}"
                    if mouse_clicked: num_players = vals[i]; state="INPUT_NAMES"; play_sfx("click")

        elif state == "INPUT_NAMES":
            if draw_btn("< BACK", 80, HEIGHT-50, 120, 40, False).collidepoint(mouse_pos) and mouse_clicked: state="SELECT_COUNT"; player_names=[]; play_sfx("click")
            p_idx = len(player_names) + 1
            center_y = HEIGHT // 2 + 40
            lbl = ui_font.render(f"Enter Name for Player {p_idx}", True, theme["text"])
            screen.blit(lbl, lbl.get_rect(center=(WIDTH//2, center_y - 60)))
            
            box = pygame.Rect(0,0, 400, 70); box.center=(WIDTH//2, center_y + 10)
            
            bg_col = theme["panel_bg"]
            if len(bg_col) == 4:
                shape_surf = pygame.Surface((400, 70), pygame.SRCALPHA)
                pygame.draw.rect(shape_surf, bg_col, shape_surf.get_rect(), border_radius=10)
                screen.blit(shape_surf, box.topleft)
            else:
                pygame.draw.rect(screen, bg_col, box, border_radius=10)
                
            pygame.draw.rect(screen, theme["accent"], box, 2, border_radius=10)
            
            cur = "|" if int(time.time()*2)%2==0 else ""
            nm = input_font.render(temp_name + cur, True, theme["text"])
            screen.blit(nm, nm.get_rect(center=box.center))
            hint = small_font.render("Press ENTER to confirm", True, theme["text"])
            screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT - 100)))

        elif state == "SELECT_LEVEL":
            if draw_btn("< BACK", 80, HEIGHT-50, 120, 40, False).collidepoint(mouse_pos) and mouse_clicked: state="INPUT_NAMES"; play_sfx("click")
            lbl_y = menu_start_y - 20
            lbl = ui_font.render("Select Difficulty", True, theme["text"])
            screen.blit(lbl, lbl.get_rect(center=(WIDTH//2, lbl_y)))
            lvls = ["EASY", "NORMAL", "HARD"]
            for i, lv in enumerate(lvls):
                btn = draw_btn(lv, WIDTH//2 + (i-1)*220, lbl_y + 100, 180, 120, (i==idx_level))
                if btn.collidepoint(mouse_pos):
                    idx_level = i; current_hovered_btn = f"l_{i}"
                    if mouse_clicked:
                        play_sfx("click"); selected_level = i+1; pygame.mixer.music.fadeout(1000)
                        return player_names, selected_level

        if current_hovered_btn != last_hovered_btn and current_hovered_btn is not None: play_sfx("hover")
        last_hovered_btn = current_hovered_btn
        pygame.display.flip(); clock.tick(60)

def show_pause_menu(screen, config):
    """
    Menampilkan menu pause di atas game.
    Return: "RESUME", "MAIN_MENU", atau "EXIT"
    """
    WIDTH, HEIGHT = config['WIDTH'], config['HEIGHT']
    
    try:
        title_font = config['big_font']
        ui_font = config['font']
    except:
        title_font = pygame.font.SysFont("georgia", 60, bold=True)
        ui_font = pygame.font.SysFont("arial", 30)

    game_snapshot = screen.copy()
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Hitam transparan (Alpha 180)

    running_pause = True
    selected_idx = 0
    items = ["RESUME", "MAIN MENU", "EXIT GAME"]

    while running_pause:
        screen.blit(game_snapshot, (0, 0))
        screen.blit(overlay, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "EXIT"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse_clicked = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "RESUME" # Tekan ESC lagi untuk lanjut main
                if e.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(items)
                if e.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(items)
                if e.key == pygame.K_RETURN:
                    if selected_idx == 0: return "RESUME"
                    if selected_idx == 1: return "MAIN_MENU"
                    if selected_idx == 2: return "EXIT"

        title_surf = title_font.render("GAME PAUSED", True, (255, 215, 0)) # Warna Emas
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))

        btn_start_y = HEIGHT // 2 - 20
        for i, item in enumerate(items):
            btn_rect = pygame.Rect(WIDTH//2 - 125, btn_start_y + (i*70), 250, 55)
            is_hover = btn_rect.collidepoint(mouse_pos)
            if is_hover: selected_idx = i
            
            is_selected = (i == selected_idx)
            bg_col = (60, 60, 70) if is_selected else (30, 30, 40)
            border_col = (255, 100, 50) if is_selected else (100, 100, 100)
            text_col = (255, 255, 255) if is_selected else (180, 180, 180)

            pygame.draw.rect(screen, bg_col, btn_rect, border_radius=10)
            pygame.draw.rect(screen, border_col, btn_rect, 3 if is_selected else 1, border_radius=10)
            
            txt_surf = ui_font.render(item, True, text_col)
            screen.blit(txt_surf, txt_surf.get_rect(center=btn_rect.center))

            if is_selected and mouse_clicked:
                if i == 0: return "RESUME"
                if i == 1: return "MAIN_MENU"
                if i == 2: return "EXIT"

        pygame.display.flip()
        config['clock'].tick(60)