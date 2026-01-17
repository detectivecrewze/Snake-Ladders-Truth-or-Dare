import pygame

def generate_dice_sprites(size=64):
    """Menghasilkan list berisi 6 Surface gambar dadu (1-6)"""
    sprites = {}
    
    BG_COLOR = (255, 255, 255)      # Putih
    DOT_COLOR = (20, 20, 20)       # Hitam/Abu gelap
    BORDER_COLOR = (200, 200, 200) # Abu terang untuk pinggiran
    
    for i in range(1, 7):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        rect = pygame.Rect(0, 0, size, size)
        pygame.draw.rect(surf, BORDER_COLOR, rect, border_radius=12) # Border
        pygame.draw.rect(surf, BG_COLOR, rect.inflate(-4, -4), border_radius=10) # Isi
        
        padding = size // 4
        mid = size // 2
        p1 = padding
        p2 = size - padding
        
        dots = {
            1: [(mid, mid)],
            2: [(p1, p1), (p2, p2)],
            3: [(p1, p1), (mid, mid), (p2, p2)],
            4: [(p1, p1), (p2, p1), (p1, p2), (p2, p2)],
            5: [(p1, p1), (p2, p1), (mid, mid), (p1, p2), (p2, p2)],
            6: [(p1, p1), (p2, p1), (p1, mid), (p2, mid), (p1, p2), (p2, p2)]
        }
        
        dot_radius = size // 10
        for pos in dots[i]:
            pygame.draw.circle(surf, DOT_COLOR, pos, dot_radius)
            
        sprites[i] = surf
        
    return sprites