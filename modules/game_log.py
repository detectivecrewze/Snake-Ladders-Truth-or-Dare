"""
Sistem Log Game - Mengelola history dan current turn log
"""
MAX_LOG = 1000

class LogManager:
    """Mengelola log history dan current turn log"""
    
    def __init__(self):
        self.history = []
        self.current_turn_log = []
        self.sidebar_snapshot = None
        self.max_log = MAX_LOG
    
    def start_turn(self, player):
        """Mulai giliran baru untuk player"""
        self.current_turn_log = [f"▶ {player}"]
    
    def log_turn(self, text):
        """Tambahkan log ke current turn"""
        self.current_turn_log.append("  " + text)
    
    def end_turn(self):
        """Akhiri giliran, pindahkan log ke history"""
        for line in self.current_turn_log:
            self.history.append(line)

        while len(self.history) > self.max_log:
            self.history.pop(0)

        self.current_turn_log = []

        self.sidebar_snapshot = None
    
    def get_full_log(self):
        """Dapatkan gabungan history + current turn log untuk real-time display"""
        return self.history + self.current_turn_log
