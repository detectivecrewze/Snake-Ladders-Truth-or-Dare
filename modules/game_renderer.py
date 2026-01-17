import pygame
import math
import random
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from game_constants import *
from typing import Dict, List, Tuple, Any, Optional
from modules.visuals import draw_scroll, draw_background_effects
from modules.game_utils import board_xy, lerp
from modules.game_state import GameState

class GameRenderer:
    screen: pygame.Surface
    assets: Dict[str, Any]
    fonts: Dict[str, pygame.font.Font]
    sidebar_snapshot: Optional[pygame.Surface]
    last_history_len: int

    def __init__(self, screen: pygame.Surface, assets: Dict[str, Any], fonts: Dict[str, pygame.font.Font]) -> None:
        self.screen = screen
        self.assets = assets
        self.fonts = fonts
        self.sidebar_snapshot = None
        self.last_history_len = -1
        
    def draw_board(self, state: GameState) -> None:
        """Draw the game board with marble tiles and scrolls"""
        local_rng = random.Random()
        
        for i in range(1, TOTAL + 1):
            n = i - 1
            row_idx = n // COLS
            col_idx = n % COLS
            row = ROWS - 1 - row_idx
            col = col_idx if (row_idx % 2) == 0 else COLS - 1 - col_idx
            
            x = (col * CELL) + SIDEBAR_LEFT_WIDTH
            y = row * CELL
            
            rect = pygame.Rect(x, y, CELL, CELL)
            
            theme = TILE_EVEN if i % 2 == 0 else TILE_ODD
            
            base_col  = theme['base']
            highlight = theme['highlight']
            shadow    = theme['shadow']
            crack_col = theme['crack']
                
            pygame.draw.rect(self.screen, base_col, rect)

            local_rng.seed(i)
            for _ in range(3):
                vx_start = local_rng.randint(x, x + CELL)
                vy_start = local_rng.randint(y, y + CELL)
                vx_end = vx_start + local_rng.randint(-20, 20)
                vy_end = vy_start + local_rng.randint(-20, 20)
                pygame.draw.line(self.screen, shadow, (vx_start, vy_start), (vx_end, vy_end), 1)

            for _ in range(5):
                nx = local_rng.randint(x + 4, x + CELL - 4)
                ny = local_rng.randint(y + 4, y + CELL - 4)
                pygame.draw.circle(self.screen, crack_col, (nx, ny), 1)

            if local_rng.random() > 0.75:
                sx_crack = local_rng.randint(x + 15, x + CELL - 15)
                sy_crack = local_rng.randint(y + 15, y + CELL - 15)
                points = [(sx_crack, sy_crack)]
                for _ in range(3):
                    sx_crack += local_rng.randint(-6, 6)
                    sy_crack += local_rng.randint(-6, 6)
                    points.append((sx_crack, sy_crack))
                if len(points) > 1:
                    pygame.draw.lines(self.screen, crack_col, False, points, 2)

            pygame.draw.line(self.screen, highlight, (x, y), (x + CELL, y), 3)
            pygame.draw.line(self.screen, highlight, (x, y), (x, y + CELL), 3)
            pygame.draw.line(self.screen, shadow, (x, y + CELL), (x + CELL, y + CELL), 3)
            pygame.draw.line(self.screen, shadow, (x + CELL, y), (x + CELL, y + CELL), 3)

            rivet_col = (60, 60, 70)
            offset = 6
            for pos in [(x+offset, y+offset), (x+CELL-offset, y+offset), 
                       (x+offset, y+CELL-offset), (x+CELL-offset, y+CELL-offset)]:
                pygame.draw.circle(self.screen, rivet_col, pos, 2)
                pygame.draw.circle(self.screen, (150, 150, 160), (pos[0]-1, pos[1]-1), 1)

            seal_center = (x + 18, y + 18)
            local_rng.seed(i * 100)
            blob_points = []
            for ang in range(0, 360, 45):
                rad = local_rng.randint(11, 15)
                bx = seal_center[0] + math.cos(math.radians(ang)) * rad
                by = seal_center[1] + math.sin(math.radians(ang)) * rad
                blob_points.append((bx, by))
            pygame.draw.polygon(self.screen, (140, 20, 20), blob_points)
            pygame.draw.circle(self.screen, (180, 40, 40), seal_center, 10)
            pygame.draw.circle(self.screen, (220, 100, 100), (seal_center[0]-3, seal_center[1]-3), 2)

            num_surf = self.fonts['small'].render(str(i), True, (255, 240, 200))
            num_rect = num_surf.get_rect(center=seal_center)
            self.screen.blit(num_surf, num_rect)

            is_snake_head = i in state.snakes
            is_ladder_base = i in state.ladders

            if str(i) in state.challenges and not is_snake_head and not is_ladder_base:
                cx, cy = x + CELL // 2, y + CELL // 2
                float_y = math.sin(pygame.time.get_ticks() * 0.005 + i) * 6
                
                challenge_text = state.challenges[str(i)].lower()
                scroll_to_use = self.assets.get('scroll_default')
                
                if "truth" in challenge_text or "kebenaran" in challenge_text:
                    if self.assets.get('scroll_truth'):
                        scroll_to_use = self.assets['scroll_truth']
                elif "dare" in challenge_text or "tantangan" in challenge_text:
                    if self.assets.get('scroll_dare'):
                        scroll_to_use = self.assets['scroll_dare']
                
                if scroll_to_use:
                    shadow_rect = pygame.Rect(cx - 10, cy + 18, 20, 6)
                    pygame.draw.ellipse(self.screen, (0,0,0,60), shadow_rect)
                    scroll_rect = scroll_to_use.get_rect(center=(cx, cy + float_y))
                    self.screen.blit(scroll_to_use, scroll_rect)
                else:
                    draw_scroll(self.screen, cx, cy + float_y)

    def _board_xy(self, n: int) -> Tuple[int, int]:
        """Wrapper for board_xy with local offset"""
        x, y = board_xy(n, COLS, ROWS, CELL)
        return x + SIDEBAR_LEFT_WIDTH, y

    def draw_snake(self, start: int, end: int, glow: bool = False) -> None:
        """
        Draw a snake from start tile to end tile.

        Args:
            start: Head position (higher tile number)
            end: Tail position (lower tile number)
            glow: Whether to apply active interaction glow
        """
        sx, sy = self._board_xy(start)
        ex, ey = self._board_xy(end)
        
        time_ms = pygame.time.get_ticks()
        breath = math.sin(time_ms * 0.005) * 2
        
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
            py = by 
            points.append((px, py))

        shadow_points = [(p[0] + 8, p[1] + 8) for p in points]
        if len(points) > 1:
            pygame.draw.lines(self.screen, (0, 0, 0, 80), False, shadow_points, 24)

        if glow:
            for w in range(20, 0, -4):
                alpha = 150 - (w * 5)
                glow_col = (255, 50, 50, alpha)
                pygame.draw.lines(self.screen, glow_col, False, points, 22 + w)

        pygame.draw.lines(self.screen, (10, 30, 10), False, points, 20 + int(breath))
        pygame.draw.lines(self.screen, (20, 80, 20), False, points, 16 + int(breath))
        pygame.draw.lines(self.screen, (40, 180, 60), False, points, 6)

        for i in range(2, len(points) - 5, 4):
            p_curr = points[i]
            p_next = points[i+1]
            dx, dy = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
            angle = math.atan2(dy, dx)
            spine_len = 10
            sx_spine = p_curr[0] + math.sin(angle) * spine_len
            sy_spine = p_curr[1] - math.cos(angle) * spine_len
            pygame.draw.circle(self.screen, (200, 190, 140), (int(sx_spine), int(sy_spine)), 3)

        hx, hy = points[0]
        head_color = (20, 100, 30)
        pygame.draw.circle(self.screen, (10, 30, 10), (hx, hy), 18)
        pygame.draw.circle(self.screen, head_color, (hx, hy), 14)
        pygame.draw.circle(self.screen, (15, 80, 25), (hx, hy + 8), 10) 
        
        eye_color = (255, 200, 0) if not glow else (255, 0, 0)
        pygame.draw.line(self.screen, (0,0,0), (hx - 6, hy - 4), (hx - 10, hy - 8), 5)
        pygame.draw.line(self.screen, (0,0,0), (hx + 6, hy - 4), (hx + 10, hy - 8), 5)
        pygame.draw.circle(self.screen, eye_color, (hx - 5, hy - 2), 3)
        pygame.draw.circle(self.screen, eye_color, (hx + 5, hy - 2), 3)
        
        horn_col = (220, 210, 180)
        pygame.draw.line(self.screen, horn_col, (hx - 8, hy - 10), (hx - 18, hy - 25), 4)
        pygame.draw.line(self.screen, horn_col, (hx + 8, hy - 10), (hx + 18, hy - 25), 4)
        pygame.draw.circle(self.screen, (0, 20, 0), (hx - 3, hy + 10), 1)
        pygame.draw.circle(self.screen, (0, 20, 0), (hx + 3, hy + 10), 1)

    def draw_ladder(self, start: int, end: int, glow: bool = False) -> None:
        """
        Draw a ladder from start tile to end tile.

        Args:
            start: Base position (lower tile number)
            end: Top position (higher tile number)
            glow: Whether to apply active interaction glow
        """
        sx, sy = self._board_xy(start)
        ex, ey = self._board_xy(end)
        
        wood_main  = (60, 40, 20)  
        wood_light = (90, 65, 35)
        wood_dark  = (30, 20, 10)
        iron_col   = (50, 50, 55)
        width = 14 
        
        l1 = (sx - width, sy)
        r1 = (sx + width, sy)
        l2 = (ex - width, ey)
        r2 = (ex + width, ey)

        pygame.draw.line(self.screen, (0, 0, 0, 80), (l1[0]+6, l1[1]+6), (l2[0]+6, l2[1]+6), 6)
        pygame.draw.line(self.screen, (0, 0, 0, 80), (r1[0]+6, r1[1]+6), (r2[0]+6, r2[1]+6), 6)

        steps = 9
        for i in range(steps + 1):
            t = i / steps
            px1, py1 = lerp(l1[0], l2[0], t), lerp(l1[1], l2[1], t)
            px2, py2 = lerp(r1[0], r2[0], t), lerp(r1[1], r2[1], t)
            
            pygame.draw.line(self.screen, (0,0,0,100), (px1+4, py1+4), (px2+4, py2+4), 8)
            pygame.draw.line(self.screen, wood_dark, (px1, py1), (px2, py2), 10)
            pygame.draw.line(self.screen, wood_main, (px1+1, py1), (px2-1, py2), 6)
            pygame.draw.line(self.screen, wood_light, (px1+2, py1-2), (px2-2, py2-2), 2)
            pygame.draw.circle(self.screen, iron_col, (int(px1), int(py1)), 4)
            pygame.draw.circle(self.screen, iron_col, (int(px2), int(py2)), 4)
            pygame.draw.circle(self.screen, (100, 100, 110), (int(px1)-1, int(py1)-1), 1)
            pygame.draw.circle(self.screen, (100, 100, 110), (int(px2)-1, int(py2)-1), 1)

        pygame.draw.line(self.screen, wood_dark, l1, l2, 10)
        pygame.draw.line(self.screen, wood_main, l1, l2, 6)
        pygame.draw.line(self.screen, wood_dark, r1, r2, 10)
        pygame.draw.line(self.screen, wood_main, r1, r2, 6)

        if glow:
            glow_col = (255, 215, 0)
            pygame.draw.line(self.screen, glow_col, l1, l2, 2)
            pygame.draw.line(self.screen, glow_col, r1, r2, 2)
            pygame.draw.circle(self.screen, glow_col, (int(l1[0]), int(l1[1])), 5)
            pygame.draw.circle(self.screen, glow_col, (int(r2[0]), int(r2[1])), 5)

    def draw_pion(self, state: GameState, idx: int, offset: int) -> None:
        """
        Draw a player's pion (avatar) on the board.

        Args:
            state: Current game state
            idx: Index of the player
            offset: Pixel offset for centering/stacking
        """
        x, y = board_xy(state.positions[idx], COLS, ROWS, CELL)
        x += SIDEBAR_LEFT_WIDTH
        
        bounce = int(6 * abs(math.sin(state.bounce_phase[idx])))
        state.bounce_phase[idx] += BOUNCE_SPEED
        
        state.pulse_scale[idx] += (1.0 - state.pulse_scale[idx]) * 0.15
        r = int(12 * state.pulse_scale[idx])
        
        cx = x + offset
        cy = y - bounce

        if idx == state.turn:
            time_ms = pygame.time.get_ticks()
            
            angle_offset = time_ms * 0.002 
            radius_ring = 22
            
            for k in range(3):
                start_angle = angle_offset + (k * (2 * math.pi / 3))
                end_angle = start_angle + 1.5
                
                arc_points = []
                for j in range(10):
                    theta = start_angle + (end_angle - start_angle) * (j / 9)
                    ax = cx + math.cos(theta) * radius_ring
                    ay = (y + 15) + math.sin(theta) * (radius_ring * 0.5)
                    arc_points.append((ax, ay))
                
                if len(arc_points) > 1:
                    aura_col = (*state.colors[idx], 200) 
                    pygame.draw.lines(self.screen, state.colors[idx], False, arc_points, 2)

            pulse = (math.sin(time_ms * 0.005) + 1) * 0.5
            inner_r = 10 + (pulse * 5)
            
            glow_surf = pygame.Surface((60, 40), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (*state.colors[idx], 100 - int(pulse * 50)), (30 - inner_r, 20 - inner_r/2, inner_r*2, inner_r), 0)
            self.screen.blit(glow_surf, (cx - 30, y + 15 - 20))

        shadow_col = [max(c - 60, 0) for c in state.colors[idx]]
        deep_shadow = [max(c - 100, 0) for c in state.colors[idx]]
        highlight_col = [min(c + 90, 255) for c in state.colors[idx]]

        shadow_w = max(4, r * 2 - bounce // 2)
        pygame.draw.ellipse(self.screen, (20, 20, 30, 80), (cx - shadow_w//2, y + 15, shadow_w, 6))

        cloak_rect = (cx - r - 5, cy - 2, (r + 5) * 2, r * 2 + 4)
        pygame.draw.arc(self.screen, shadow_col, cloak_rect, 0, 3.14, 4)

        body_poly = [
            (cx - r - 2, cy + r + 4), 
            (cx + r + 2, cy + r + 4), 
            (cx + r + 6, cy - 4),     
            (cx - r - 6, cy - 4)      
        ]
        pygame.draw.polygon(self.screen, deep_shadow, body_poly)
        pygame.draw.polygon(self.screen, state.colors[idx], [(p[0], p[1]-2) for p in body_poly])

        helm_rect = pygame.Rect(cx - r + 2, cy - r - 12, (r - 2) * 2, r + 8)
        pygame.draw.rect(self.screen, state.colors[idx], helm_rect, border_top_left_radius=6, border_top_right_radius=6)
        
        pygame.draw.rect(self.screen, (10, 10, 15), (cx - r + 5, cy - r - 3, (r - 5) * 2, 3))
        
        if idx == state.turn:
            pygame.draw.line(self.screen, (255, 50, 50), (cx, cy - r - 12), (cx, cy - r - 18), 3)

        shield_pts = [
            (cx - r - 8, cy), (cx - r - 2, cy), 
            (cx - r - 2, cy + 14), (cx - r - 5, cy + 18), (cx - r - 8, cy + 14)
        ]
        pygame.draw.polygon(self.screen, highlight_col, shield_pts)
        pygame.draw.polygon(self.screen, (30, 30, 40), shield_pts, 1)

        pygame.draw.line(self.screen, (255, 255, 255), (cx - r + 4, cy - r - 10), (cx - r + 4, cy - 6), 2)

    def draw_cinematic_overlay(self, state, target_pos_idx):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 5, 0, 120))

        if 0 <= target_pos_idx < len(state.players):
            px, py = self._board_xy(state.positions[target_pos_idx])
            
            spotlight = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(spotlight, (255, 255, 255, 255), (px, py), 130)
            for i in range(50):
                pygame.draw.circle(spotlight, (255, 255, 255, 5), (px, py), 130 + i*2)

            overlay.blit(spotlight, (0,0), special_flags=pygame.BLEND_RGBA_SUB)

        self.screen.blit(overlay, (0,0))

    def draw_current_turn_header(self, state):
        """
        [REMASTERED] Header Player yang Estetik, Rapi, dan Medieval.
        Menggunakan FONT_FILE langsung agar ukurannya pas.
        """
        curr_col = state.colors[state.turn]
        
        card_margin_x = 12
        card_w = SIDEBAR_WIDTH - (card_margin_x * 2)
        card_h = 85 
        
        card_x = WIDTH - SIDEBAR_WIDTH + card_margin_x
        card_y = 20
        
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        shadow_rect = card_rect.move(0, 4)
        pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=12)
        pygame.draw.rect(self.screen, (30, 32, 40), card_rect, border_radius=12)
        pygame.draw.rect(self.screen, curr_col, card_rect, 1, border_radius=12)

        avatar_size = 56
        av_padding = 10
        av_center_x = card_x + av_padding + (avatar_size // 2)
        av_center_y = card_y + (card_h // 2) - 4
        
        pygame.draw.circle(self.screen, (20, 20, 25), (av_center_x, av_center_y), (avatar_size // 2) + 2)
        pygame.draw.circle(self.screen, curr_col, (av_center_x, av_center_y), (avatar_size // 2), 1)
        
        if state.turn < len(self.assets.get('hero_avatars', [])):
            raw_img = self.assets['hero_avatars'][state.turn]
            avatar_img = pygame.transform.smoothscale(raw_img, (avatar_size - 6, avatar_size - 6))
            av_rect = avatar_img.get_rect(center=(av_center_x, av_center_y))
            self.screen.blit(avatar_img, av_rect)

        text_start_x = av_center_x + (avatar_size // 2) + 12
        text_center_y = av_center_y 
        
        try:
            lbl_font = pygame.font.Font(FONT_FILE, 10) 
            name_font = pygame.font.Font(FONT_FILE, 22) # Size 22 jauh lebih rapi daripada 48
            info_font = pygame.font.Font(FONT_FILE, 12)
        except:
            lbl_font = self.fonts['small']
            name_font = self.fonts['font']
            info_font = self.fonts['small']

        lbl_surf = lbl_font.render("CURRENT TURN", True, (150, 160, 170))
        self.screen.blit(lbl_surf, (text_start_x, text_center_y - 24))
        
        p_name = state.players[state.turn]
        lum = 0.299 * curr_col[0] + 0.587 * curr_col[1] + 0.114 * curr_col[2]
        text_color = (245, 235, 215) if lum < 120 else (20, 20, 20)
        if lum > 120: text_color = (240, 240, 230)

        name_shadow = name_font.render(p_name, True, (0, 0, 0))
        self.screen.blit(name_shadow, (text_start_x + 1, text_center_y - 8))
        
        name_surf = name_font.render(p_name, True, text_color)
        self.screen.blit(name_surf, (text_start_x, text_center_y - 9))
        
        info_text = f"Tile: {state.positions[state.turn]} / {TOTAL}"
        info_surf = info_font.render(info_text, True, (180, 180, 180))
        self.screen.blit(info_surf, (text_start_x, text_center_y + 14))

        bar_x = card_x + 10
        bar_y = card_y + card_h - 10
        bar_w = card_w - 20
        bar_h = 4
        
        pygame.draw.rect(self.screen, (20, 20, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        
        progress = state.positions[state.turn] / TOTAL
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            glow_surf = pygame.Surface((fill_w + 4, bar_h + 4), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*curr_col, 100), (0, 0, fill_w + 4, bar_h + 4), border_radius=4)
            self.screen.blit(glow_surf, (bar_x - 2, bar_y - 2))
            
            pygame.draw.rect(self.screen, curr_col, (bar_x, bar_y, fill_w, bar_h), border_radius=2)

    def draw_panel(self, state, sidebar_helper):
        full_log = state.log_manager.get_full_log() 
        sidebar_rect = pygame.Rect(WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)

        current_len = len(full_log)
        if current_len != self.last_history_len:
            self.sidebar_snapshot = None 

        if self.sidebar_snapshot is not None:
            self.screen.blit(self.sidebar_snapshot, (WIDTH - SIDEBAR_WIDTH, 0))
            self.draw_current_turn_header(state)
            return

        self.last_history_len = current_len 
        
        if self.assets.get('right_sidebar_bg'):
            self.screen.blit(self.assets['right_sidebar_bg'], (WIDTH - SIDEBAR_WIDTH, 0))
            overlay = pygame.Surface((SIDEBAR_WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 23, 30, 180)) 
            self.screen.blit(overlay, (WIDTH - SIDEBAR_WIDTH, 0))
        else:
            pygame.draw.rect(self.screen, (25, 28, 35), sidebar_rect) 

        pygame.draw.line(self.screen, (10, 10, 15), (WIDTH - SIDEBAR_WIDTH, 0), (WIDTH - SIDEBAR_WIDTH, HEIGHT), 4)
        pygame.draw.line(self.screen, (60, 50, 40), (WIDTH - SIDEBAR_WIDTH + 4, 0), (WIDTH - SIDEBAR_WIDTH + 4, HEIGHT), 1)

        self.draw_current_turn_header(state)

        sidebar_helper.draw_history_ui(
            self.screen, full_log, state.players, state.colors, state.challenges, 
            start_y=135, sidebar_width=SIDEBAR_WIDTH, width_total=WIDTH
        )

        self.sidebar_snapshot = self.screen.subsurface(sidebar_rect).copy()
        state.log_manager.sidebar_snapshot = self.sidebar_snapshot
