import pygame
import os
import re

def clean_log_text(text):
    """
    Membersihkan teks dari karakter error (glitch), 
    TAPI MEMPERTAHANKAN EMOJI & SIMBOL PENTING.
    """
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return cleaned.strip()

class SidebarManager:
    def __init__(self, image_dir, dice_images, hero_avatars, font_path=None):
        self.dice_images = dice_images
        self.hero_avatars = hero_avatars 
        self.icons = {}
        
        if font_path and os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, 13) 
            self.bold_font = pygame.font.Font(font_path, 15) 
        else:
            self.font = pygame.font.SysFont("segoe ui", 13)
            self.bold_font = pygame.font.SysFont("segoe ui", 15, bold=True)
        
        target_size = (20, 20)
        names = {
            "move": "pindah.png", 
            "snake": "ular_icon.png", 
            "ladder": "tangga_icon.png", 
            "challenge": "scroll_icon.png"
        }
        
        for key, filename in names.items():
            path = os.path.join(image_dir, filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                self.icons[key] = pygame.transform.smoothscale(img, target_size)
            except Exception:
                surf = pygame.Surface(target_size, pygame.SRCALPHA)
                pygame.draw.circle(surf, (150, 150, 150), (10, 10), 8)
                self.icons[key] = surf

    def get_contrast_color(self, color):
        lum = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        if lum < 90: return (240, 230, 210)
        return (30, 30, 40)
    
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            w, h = font.size(test_line)
            
            if w < max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines

    def get_icon_for_text(self, text, challenges_dict, players_list, colors_list):
        clean_text = clean_log_text(text)
        target_size = (20, 20)
        lower_text = text.lower()

        scroll_keywords = ["truth", "dare", "tantangan", "challenge", "zonk", "scroll", "misi", "quest"]
        has_symbol = "📝" in text or "📜" in text or "統" in text
        
        is_long_text = len(clean_text) > 20
        is_game_system = "dice" in lower_text or "dadu" in lower_text or "turn" in lower_text or "win" in lower_text
        
        if (any(k in lower_text for k in scroll_keywords) or has_symbol) or (is_long_text and not is_game_system):
            return self.icons.get("challenge"), clean_text

        if "dice" in lower_text or "dadu" in lower_text:
            nums = re.findall(r'\d+', clean_text)
            if nums and 1 <= int(nums[0]) <= 6:
                return pygame.transform.smoothscale(self.dice_images[int(nums[0])], target_size), clean_text
        
        if "snake" in lower_text or "ular" in lower_text or "🐍" in text: 
            return self.icons.get("snake"), clean_text
        if "ladder" in lower_text or "tangga" in lower_text or "🪜" in text: 
            return self.icons.get("ladder"), clean_text
        if "stop" in lower_text or "berhenti" in lower_text: 
            return self.icons.get("move"), clean_text
        
        for idx, name in enumerate(players_list):
            if name in clean_text:
                if idx < len(self.hero_avatars):
                    original_img = self.hero_avatars[idx]
                    small_icon = pygame.transform.smoothscale(original_img, target_size)
                    return small_icon, clean_text
        
        if challenges_dict:
            for c_text in challenges_dict.values():
                if c_text and (clean_text in c_text or c_text in clean_text):
                     return self.icons.get("challenge"), clean_text

        return None, clean_text

    def draw_rich_text(self, screen, text, x, y, base_color, alpha):
        words = text.split(' ')
        cursor_x = x
        for word in words:
            color = base_color
            word_lower = word.lower()
            clean_word = re.sub(r'[^\w]', '', word)
            
            if clean_word.isdigit(): color = (255, 215, 0)
            elif "mundur" in word_lower: color = (255, 100, 100)
            elif "maju" in word_lower: color = (100, 255, 100)
            elif "ular" in word_lower: color = (150, 255, 150)
            
            surf = self.font.render(word + " ", True, color)
            surf.set_alpha(alpha)
            screen.blit(surf, (cursor_x, y))
            cursor_x += surf.get_width()

    def draw_history_ui(self, screen, history, players, colors, challenges, start_y, sidebar_width, width_total):
        y_log = start_y
        sidebar_x = width_total - sidebar_width
        max_y = 680 
        
        turn_blocks = []
        current_block = []
        
        for entry in history:
            is_new_turn = "▶" in entry
            
            if not is_new_turn:
                for p in players:
                    if entry.strip().startswith(f"▶ {p}") or entry.strip() == p:
                        is_new_turn = True
                        break
            
            if is_new_turn and current_block:
                turn_blocks.append(current_block)
                current_block = []
            
            current_block.append(entry)
        
        if current_block: turn_blocks.append(current_block)
        reversed_blocks = turn_blocks[::-1] 
        
        PADDING = 12
        LINE_H = 24
        ICON_SIZE = 20
        ICON_GAP = 30
        
        for i, block in enumerate(reversed_blocks):
            wrapped_content = []
            player_idx = -1
            
            for line in block:
                icon, clean_txt = self.get_icon_for_text(line, challenges, players, colors)
                
                is_header = "▶" in line
                if is_header:
                    for idx, p in enumerate(players):
                        if p in clean_txt:
                            player_idx = idx
                            break
                elif icon and player_idx == -1:
                     for idx, p in enumerate(players):
                        if p in clean_txt:
                            player_idx = idx
                            is_header = True
                            break

                display_txt = clean_txt.replace("▶", "").replace("ｶ", "").strip()
                
                max_text_width = sidebar_width - (20 + ICON_GAP + 20)
                target_font = self.bold_font if is_header else self.font
                wrapped_lines = self.wrap_text(display_txt, target_font, max_text_width)
                
                for j, line_txt in enumerate(wrapped_lines):
                    current_icon = icon if j == 0 else None
                    wrapped_content.append({"text": line_txt, "icon": current_icon, "is_header": is_header})

            content_height = len(wrapped_content) * LINE_H
            card_h = content_height + (PADDING * 2)
            
            if y_log + card_h > max_y: break
            
            alpha = 255 if i == 0 else max(220 - (i * 50), 40)
            
            player_color = (100, 100, 100)
            if player_idx != -1: player_color = colors[player_idx]
            
            text_header_color = self.get_contrast_color(player_color)
            card_rect = pygame.Rect(sidebar_x + 10, y_log, sidebar_width - 20, card_h)
            
            shadow_surf = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 80 * (alpha/255)), shadow_surf.get_rect(), border_radius=10)
            screen.blit(shadow_surf, (card_rect.x, card_rect.y + 4))

            bg_col = (45, 48, 60, alpha)
            if i == 0: bg_col = (55, 60, 75, alpha)

            card_surf = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, bg_col, (0, 0, card_rect.width, card_rect.height), border_radius=10)
            pygame.draw.rect(card_surf, (*player_color, alpha), (0, 0, 6, card_rect.height), border_top_left_radius=10, border_bottom_left_radius=10)
            
            pygame.draw.line(card_surf, (255, 255, 255, 30), (0, 0), (card_rect.width, 0), 1)
            pygame.draw.line(card_surf, (0, 0, 0, 100), (0, card_rect.height-1), (card_rect.width, card_rect.height-1), 1)
            screen.blit(card_surf, card_rect.topleft)

            text_y = y_log + PADDING
            text_x = card_rect.x + 18 
            
            for line_data in wrapped_content:
                txt_start_x = text_x + ICON_GAP
                
                if line_data["is_header"]:
                    base_col = (*text_header_color, alpha)
                else:
                    base_col = (200, 200, 210)

                if line_data["icon"]:
                    icon_copy = line_data["icon"].copy()
                    icon_copy.set_alpha(alpha)
                    center_y = text_y + (LINE_H - ICON_SIZE) // 2
                    screen.blit(icon_copy, (text_x, center_y)) 
                
                if line_data["is_header"]:
                    surf = self.bold_font.render(line_data["text"], True, base_col)
                    screen.blit(surf, (txt_start_x, text_y))
                else:
                    self.draw_rich_text(screen, line_data["text"], txt_start_x, text_y, base_col, alpha)
                
                text_y += LINE_H

            y_log += card_h + 10