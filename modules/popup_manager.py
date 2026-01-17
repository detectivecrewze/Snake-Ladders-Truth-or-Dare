import pygame
import math
import time
import os

def show_popup(screen, text, step_number, config):
    WIDTH, HEIGHT = config['WIDTH'], config['HEIGHT']
    IMAGE_DIR = config['IMAGE_DIR']
    SOUND_DIR = os.path.join(os.path.dirname(IMAGE_DIR), "sounds")
    
    snapshot = screen.copy()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 20, 230))

    clean_text = text.replace("🎯", "").replace("📜", "").strip()
    
    is_truth = "truth" in clean_text.lower() or "kebenaran" in clean_text.lower()
    is_dare = "dare" in clean_text.lower() or "tantangan" in clean_text.lower()
    is_win = any(k in clean_text.upper() for k in ["MENANG", "WINNER", "JUARA", "WIN"])
    is_snake_ladder = "Ular" in clean_text or "Tangga" in clean_text
    
    is_challenge = any(k in clean_text.lower() for k in ["tantangan", "detik", "menit", "timer"])
    timer_duration = config['get_timer_duration'](clean_text) if is_challenge else 0
    timer_started, timer_finished = False, False
    start_ticks, time_left, sound_played = 0, timer_duration, False

    challenge_img = None
    
    if is_truth and config.get('scroll_truth_img'):
        path = os.path.join(IMAGE_DIR, "scroll_truth.png")
        try:
            challenge_img = pygame.image.load(path).convert_alpha()
        except:
            challenge_img = config['scroll_truth_img']
    elif is_dare and config.get('scroll_dare_img'):
        path = os.path.join(IMAGE_DIR, "scroll_dare.png")
        try:
            challenge_img = pygame.image.load(path).convert_alpha()
        except:
            challenge_img = config['scroll_dare_img']
    
    if challenge_img is None:
        if "Ular" in clean_text:
            path = os.path.join(IMAGE_DIR, "ular_icon.png")
            if os.path.exists(path): 
                challenge_img = pygame.image.load(path).convert_alpha()
        elif "Tangga" in clean_text:
            path = os.path.join(IMAGE_DIR, "tangga_icon.png")
            if os.path.exists(path): 
                challenge_img = pygame.image.load(path).convert_alpha()
    
    if challenge_img is None and step_number:
        challenge_img = config['get_challenge_image'](step_number)
    
    if challenge_img is None and not is_win:
        d_path = os.path.join(IMAGE_DIR, "default_challenge.png")
        if os.path.exists(d_path): 
            challenge_img = pygame.image.load(d_path).convert_alpha()

    if challenge_img:
        challenge_img = pygame.transform.smoothscale(challenge_img, (200, 200))

    focused_button = 0  # 0 = Kiri, 1 = Kanan
    
    def wrap_text_smart(text, font, max_width):
        """Wrap teks berdasarkan LEBAR PIXEL, bukan jumlah karakter"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            text_width = font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    MAX_TEXT_WIDTH = 640  # Lebar maksimal kotak teks
    wrapped_lines = wrap_text_smart(clean_text, config['font'], MAX_TEXT_WIDTH)
    
    line_height = 32
    text_block_height = len(wrapped_lines) * line_height
    min_text_height = 120  # Minimal tinggi kotak teks
    dialog_height = max(min_text_height, text_block_height + 40)  # +40 padding
    
    while True:
        screen.blit(snapshot, (0, 0))
        screen.blit(overlay, (0, 0))

        t = pygame.time.get_ticks() * 0.003
        float_offset = math.sin(t) * 8

        if is_challenge and timer_started and not timer_finished:
            passed = (pygame.time.get_ticks() - start_ticks) / 1000
            time_left = max(0, timer_duration - passed)
            if time_left <= 0:
                timer_finished = True
                if not sound_played:
                    try:
                        s_path = os.path.join(SOUND_DIR, "timer_end.wav")
                        if os.path.exists(s_path): 
                            pygame.mixer.Sound(s_path).play()
                        sound_played = True
                    except: 
                        pass
        
        popup_height = 560 + (dialog_height - min_text_height)  # Tambah tinggi jika perlu
        popup_rect = pygame.Rect(0, 0, 760, popup_height)
        popup_rect.center = (WIDTH // 2, HEIGHT // 2 + float_offset)
        
        for i in range(10, 0, -1):
            s_rect = popup_rect.inflate(i*2, i*2)
            pygame.draw.rect(screen, (5, 5, 8, 100 // i), s_rect, border_radius=35 + i)

        pygame.draw.rect(screen, (22, 24, 28), popup_rect, border_radius=35)
        pygame.draw.rect(screen, (60, 65, 75), popup_rect, 2, border_radius=35)
        
        pygame.draw.line(screen, (150, 155, 170), 
                         (popup_rect.left + 80, popup_rect.top + 3), 
                         (popup_rect.right - 80, popup_rect.top + 3), 1)

        content_y = popup_rect.centery - 160
        dialog_y_offset = 180  # Jarak dialog dari gambar

        if is_win:
            v_surf = config['big_font'].render("VICTORY", True, (180, 160, 100))
            screen.blit(v_surf, v_surf.get_rect(center=(WIDTH // 2, content_y)))
        else:
            if challenge_img:
                pygame.draw.circle(screen, (15, 15, 18), (WIDTH // 2, content_y), 110)
                screen.blit(challenge_img, challenge_img.get_rect(center=(WIDTH // 2, content_y)))
            
            if is_challenge and timer_duration > 0:
                angle = (time_left / timer_duration) * 360
                arc_col = (100, 200, 150) if time_left > 10 else (180, 70, 70)
                pygame.draw.arc(screen, arc_col, 
                               (WIDTH//2-110, content_y-110, 220, 220), 
                               math.radians(-90), math.radians(angle-90), 8)
                
                t_str = f"{int(time_left // 60):02d}:{int(time_left % 60):02d}"
                t_surf = config['big_font'].render(t_str, True, (200, 200, 205))
                screen.blit(t_surf, t_surf.get_rect(center=(WIDTH // 2, content_y + 140)))

        dialog_rect = pygame.Rect(0, 0, 680, dialog_height)
        dialog_rect.center = (WIDTH // 2, content_y + dialog_y_offset + (dialog_height // 2))
        
        pygame.draw.rect(screen, (45, 48, 55), dialog_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 105, 115), dialog_rect, 2, border_radius=15)
        
        inner_shadow = dialog_rect.inflate(-4, -4)
        pygame.draw.rect(screen, (35, 38, 45), inner_shadow, border_radius=12)

        ty = dialog_rect.centery - (len(wrapped_lines) * line_height // 2)
        for i, line in enumerate(wrapped_lines):
            col = (240, 240, 245) if i % 2 == 0 else (170, 175, 185)
            s_line = config['font'].render(line, True, col)
            screen.blit(s_line, s_line.get_rect(center=(WIDTH // 2, ty + (i * line_height))))

        btn_y = popup_rect.bottom + 45
        btn_width = 280
        btn_height = 50
        btn_gap = 20
        
        show_next_btn = True
        
        if is_win:
            left_msg, left_col = "DONE", (100, 90, 60)
            show_next_btn = False
        elif is_challenge:
            if timer_started and not timer_finished:
                left_msg, left_col = "SKIP", (100, 40, 40)
                show_next_btn = False
                focused_button = 0
            elif not timer_started:
                left_msg, left_col = "START", (40, 70, 100)
            else:
                left_msg, left_col = "CONTINUE", (40, 80, 60)
        elif is_truth or is_dare:
            left_msg, left_col = "CONTINUE", (70, 75, 85)
        else:
            left_msg, left_col = "CONTINUE", (70, 75, 85)
            show_next_btn = False
        
        if show_next_btn:
            total_width = (btn_width * 2) + btn_gap
            left_btn_x = (WIDTH // 2) - (total_width // 2) + (btn_width // 2)
            right_btn_x = left_btn_x + btn_width + btn_gap
        else:
            left_btn_x = WIDTH // 2
            right_btn_x = None
        
        left_rect = pygame.Rect(0, 0, btn_width, btn_height)
        left_rect.center = (left_btn_x, btn_y)
        is_left_focused = (focused_button == 0)
        
        bg_col = (40, 45, 55) if is_left_focused else (15, 16, 20)
        pygame.draw.rect(screen, bg_col, left_rect, border_radius=10)
        
        border_width = 4 if is_left_focused else 1
        pygame.draw.rect(screen, left_col, left_rect, border_width, border_radius=10)
        
        if is_left_focused:
            glow_rect = left_rect.inflate(12, 12)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*left_col, 120), (0, 0, glow_rect.width, glow_rect.height), border_radius=14)
            screen.blit(glow_surf, glow_rect.topleft)
            
            highlight_rect = left_rect.inflate(-6, -6)
            pygame.draw.rect(screen, (*left_col, 40), highlight_rect, border_radius=8)
        
        text_col = (255, 255, 100) if is_left_focused else (180, 185, 190)
        t_left = config['font'].render(left_msg, True, text_col)
        
        if is_left_focused:
            shadow = config['font'].render(left_msg, True, (0, 0, 0))
            screen.blit(shadow, (left_rect.centerx - t_left.get_width()//2 + 2, 
                                 left_rect.centery - t_left.get_height()//2 + 2))
        
        screen.blit(t_left, t_left.get_rect(center=left_rect.center))
        
        next_rect = None
        if show_next_btn:
            next_rect = pygame.Rect(0, 0, btn_width, btn_height)
            next_rect.center = (right_btn_x, btn_y)
            is_right_focused = (focused_button == 1)
            next_col = (255, 180, 50)
            
            bg_col = (50, 40, 25) if is_right_focused else (15, 16, 20)
            pygame.draw.rect(screen, bg_col, next_rect, border_radius=10)
            
            border_width = 4 if is_right_focused else 1
            pygame.draw.rect(screen, next_col, next_rect, border_width, border_radius=10)
            
            if is_right_focused:
                glow_rect = next_rect.inflate(12, 12)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*next_col, 120), (0, 0, glow_rect.width, glow_rect.height), border_radius=14)
                screen.blit(glow_surf, glow_rect.topleft)
                
                highlight_rect = next_rect.inflate(-6, -6)
                pygame.draw.rect(screen, (*next_col, 40), highlight_rect, border_radius=8)
            
            text_col = (255, 255, 100) if is_right_focused else (255, 220, 100)
            t_next = config['font'].render("NEXT CHALLENGE?", True, text_col)
            
            if is_right_focused:
                shadow = config['font'].render("NEXT CHALLENGE?", True, (0, 0, 0))
                screen.blit(shadow, (next_rect.centerx - t_next.get_width()//2 + 2, 
                                     next_rect.centery - t_next.get_height()//2 + 2))
            
            screen.blit(t_next, t_next.get_rect(center=next_rect.center))
        
        hint_y = btn_y + 60
        if focused_button == 0:
            hint_text = "← → navigate  |  SPACE/ENTER: Continue  |  ESC: skip"
            hint_col = left_col
        else:
            hint_text = "← → navigate  |  SPACE/ENTER: Next Question  |  ESC: skip"
            hint_col = (255, 180, 50)
        
        hint_surf = config['small_font'].render(hint_text, True, hint_col)
        screen.blit(hint_surf, hint_surf.get_rect(center=(WIDTH // 2, hint_y)))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                pygame.quit(); exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if next_rect and next_rect.collidepoint(mouse_pos):
                    return "NEXT"
                
                if left_rect.collidepoint(mouse_pos):
                    if is_win:
                        return config['get_move_effect'](clean_text)
                    
                    if is_challenge:
                        if not timer_started:
                            timer_started, start_ticks = True, pygame.time.get_ticks()
                        elif timer_started and not timer_finished:
                            timer_finished = True
                            time_left = 0
                        elif timer_finished:
                            return config['get_move_effect'](clean_text)
                    else:
                        return config['get_move_effect'](clean_text)
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT and show_next_btn:
                    focused_button = 0
                if e.key == pygame.K_RIGHT and show_next_btn:
                    focused_button = 1
                
                if e.key == pygame.K_RETURN:
                    if focused_button == 1 and show_next_btn:
                        return "NEXT"
                    else:
                        if is_win:
                            return config['get_move_effect'](clean_text)
                        if is_challenge:
                            if not timer_started:
                                timer_started, start_ticks = True, pygame.time.get_ticks()
                            elif timer_started and not timer_finished:
                                timer_finished = True
                                time_left = 0
                            elif timer_finished:
                                return config['get_move_effect'](clean_text)
                        else:
                            return config['get_move_effect'](clean_text)
                
                if e.key == pygame.K_SPACE:
                    if focused_button == 1 and show_next_btn:
                        return "NEXT"
                    
                    if is_win:
                        return config['get_move_effect'](clean_text)
                    if is_challenge:
                        if not timer_started:
                            timer_started, start_ticks = True, pygame.time.get_ticks()
                        elif timer_started and not timer_finished:
                            timer_finished = True
                            time_left = 0
                        elif timer_finished:
                            return config['get_move_effect'](clean_text)
                    else:
                        return config['get_move_effect'](clean_text)
                
                if e.key == pygame.K_ESCAPE and is_challenge and timer_started and not timer_finished:
                    timer_finished = True
                    time_left = 0
        
        config['clock'].tick(60)