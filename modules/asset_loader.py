import pygame
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, Optional, Tuple, Any
from pathlib import Path
from modules.game_logger import logger

class AssetLoader:
    """Centralized asset handler with error logging and caching"""
    
    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)
        self._cache: Dict[Tuple[str, Optional[Tuple[int, int]]], pygame.Surface] = {}
        
    def load_image(self, path: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
        """
        Load an image safely by relative path. Returns placeholder if fails.
        """
        key = (path, size)
        if key in self._cache:
            return self._cache[key]
            
        full_path = self.base_dir / path
        try:
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {full_path}")
                
            img = pygame.image.load(str(full_path)).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
                
            self._cache[key] = img
            logger.info(f"Loaded asset: {path}")
            return img
            
        except Exception as e:
            logger.error(f"Failed to load image {path}: {e}")
            return self._create_placeholder(size if size else (64, 64))

    def _create_placeholder(self, size: Tuple[int, int]) -> pygame.Surface:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 255, 128)) # Magenta transparent for visibility
        pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)
        return surf
        
    def load_font(self, path: str, size: int) -> pygame.font.Font:
        full_path = self.base_dir / path
        try:
            font = pygame.font.Font(str(full_path), size)
            logger.info(f"Loaded font: {path}")
            return font
        except Exception as e:
            logger.error(f"Failed to load font {path}: {e}. Using SysFont.")
            return pygame.font.SysFont("arial", size)
            
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        full_path = self.base_dir / path
        try:
             s = pygame.mixer.Sound(str(full_path))
             logger.info(f"Loaded sound: {path}")
             return s
        except Exception as e:
            logger.warning(f"Failed to load sound {path}: {e}")
            return None
