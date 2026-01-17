import pygame
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.game_logger import logger

def get_challenge_image(step_number, size=(250, 250)):
    """Mengambil gambar tantangan dari folder images"""
    base_path = os.path.join(os.path.dirname(__file__), "images")
    
    img_path = os.path.join(base_path, f"{step_number}.png")
    
    if os.path.exists(img_path):
        try:
            img = pygame.image.load(img_path).convert_alpha()
            return pygame.transform.smoothscale(img, size)
        except Exception as e:
            logger.error(f"Gagal memuat gambar {step_number}: {e}")
            return None
    
    return None