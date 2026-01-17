import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Dict, Tuple, Optional
from modules.game_log import LogManager 
from game_constants import PLAYER_COLORS

class GameState:
    """Centralized game state management"""
    
    players: List[str]
    game_level: int
    positions: List[int]
    colors: List[Tuple[int, int, int]]
    turn: int
    bounce_phase: List[float]
    pulse_scale: List[float]
    shake_intensity: float
    shake_decay: float
    snakes: Dict[int, int]
    ladders: Dict[int, int]
    challenges: Dict[str, str]
    log_manager: LogManager

    def __init__(self, players: List[str], game_level: int) -> None:
        self.players = players
        self.game_level = game_level
        self.positions = [1] * len(players)
        self.colors = self._assign_colors(len(players))
        self.turn = 0
        
        self.bounce_phase = [0.0] * len(players)
        self.pulse_scale = [1.0] * len(players)
        self.shake_intensity = 0
        self.shake_decay = 0.8
        
        self.snakes = {}
        self.ladders = {}
        self.challenges = {}
        
        self.move_queue: List[Tuple[int, int]] = [] # [(player_idx, target_tile), ...]
        
        self.log_manager = LogManager()
        
    @property
    def history(self) -> List[str]:
        return self.log_manager.history
        
    @property
    def current_turn_log(self) -> List[str]:
        return self.log_manager.current_turn_log
    
    def _assign_colors(self, count: int) -> List[Tuple[int, int, int]]:
        """Assign colors to players based on count"""
        return PLAYER_COLORS[:count]
    
    def next_turn(self) -> None:
        """Advance to next player's turn"""
        self.turn = (self.turn + 1) % len(self.players)
    
    def current_player_name(self) -> str:
        """Get current player name"""
        return self.players[self.turn]

    def reset_for_new_game(self, players: List[str], game_level: int) -> None:
        """Reset state for a new game"""
        self.__init__(players, game_level)
