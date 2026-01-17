import pygame
import os

class LeftSidebar:
    def __init__(self, width, height, image_dir, font_path=None):
        self.width = width
        self.height = height
        
        self.bg_image = None
        try:
            bg_path = os.path.join(image_dir, "sidebar_bg.png")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.smoothscale(raw_bg, (width, height))
        except:
            pass

        if font_path and os.path.exists(font_path):
            self.title_font = pygame.font.Font(font_path, 22)
            self.head_font = pygame.font.Font(font_path, 16)
            self.body_font = pygame.font.Font(font_path, 13)
        else:
            self.title_font = pygame.font.SysFont("georgia", 20, bold=True)
            self.head_font = pygame.font.SysFont("tahoma", 14, bold=True)
            self.body_font = pygame.font.SysFont("arial", 12)

        self.rules_data = [
            ("1. KOCOK DADU", ["Tekan SPASI untuk mengocok.", "Pion akan jalan otomatis."]),
            ("2. ULAR & TANGGA", ["Tangga: Naik ke atas.", "Ular: Turun ke bawah."]),
            ("3. KOTAK TANTANGAN", ["Berisi kartu Truth or Dare.", "Wajib dilakukan!"]),
            ("4. CARA MENANG", ["Pemain pertama yang", "mencapai kotak 100."])
        ]

    def draw(self, screen, shake_x=0, shake_y=0):
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80)) 
            screen.blit(overlay, (0, 0))
        else:
            pygame.draw.rect(screen, (30, 32, 38), (0, 0, self.width, self.height))

        margin_x = 35 
        card_w = self.width - (margin_x * 2)
        card_h = 420 # Tinggi fix yang proporsional
        
        card_x = margin_x
        card_y = (self.height - card_h) // 2

        shadow_rect = pygame.Rect(card_x + 8, card_y + 8, card_w, card_h)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)

        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((20, 25, 35, 200)) 
        screen.blit(card_surf, (card_x, card_y))

        header_h = 50
        header_rect = pygame.Rect(card_x, card_y, card_w, header_h)
        pygame.draw.rect(screen, (15, 18, 25), header_rect, border_top_left_radius=12, border_top_right_radius=12)
        
        pygame.draw.line(screen, (180, 150, 80), (card_x, card_y + header_h), (card_x + card_w, card_y + header_h), 2)

        full_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(screen, (100, 90, 70), full_rect, 2, border_radius=12)

        title_surf = self.title_font.render("GAME RULES", True, (220, 200, 150)) # Warna Krem Emas
        t_x = card_x + (card_w - title_surf.get_width()) // 2
        t_y = card_y + (header_h - title_surf.get_height()) // 2
        screen.blit(title_surf, (t_x, t_y))

        content_start_y = card_y + header_h + 25 # Mulai tulis di bawah garis header
        text_margin_left = card_x + 20
        
        for header, lines in self.rules_data:
            h_surf = self.head_font.render(header, True, (255, 180, 60))
            screen.blit(h_surf, (text_margin_left, content_start_y))
            content_start_y += 20
            
            for line in lines:
                if self.body_font.size(line)[0] > card_w - 30:
                     b_surf = pygame.transform.smoothscale(
                        self.body_font.render(line, True, (200, 200, 210)),
                        (card_w - 30, 14)
                    )
                else:
                    b_surf = self.body_font.render(line, True, (200, 200, 210))
                
                screen.blit(b_surf, (text_margin_left, content_start_y))
                content_start_y += 16
            
            content_start_y += 12 # Jarak antar poin

        pygame.draw.line(screen, (80, 70, 50), (self.width, 0), (self.width, self.height), 4)