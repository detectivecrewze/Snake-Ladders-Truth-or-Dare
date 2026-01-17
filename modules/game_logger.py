import logging
from pathlib import Path
import sys

def setup_logger(name: str = "SnakeLadder") -> logging.Logger:
    """
    Configure and return a standardized logger.
    
    Creates a 'logs' directory if it doesn't exist.
    Logs to both file (detailed) and console (concise).
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        return logger
        
    file_handler = logging.FileHandler(log_dir / "game.log", encoding='utf-8')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
