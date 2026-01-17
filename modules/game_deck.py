"""
Sistem Deck Challenge - Mengelola kartu Truth dan Dare
"""
import random

class ChallengeDeck:
    """Mengelola deck kartu Truth dan Dare"""
    
    def __init__(self, source_dict):
        self.truth_master = []
        self.dare_master = []
        
        for v in source_dict.values():
            if v and str(v).strip():
                text_lower = str(v).lower()
                if "truth" in text_lower or "kebenaran" in text_lower:
                    self.truth_master.append(v)
                elif "dare" in text_lower or "tantangan" in text_lower:
                    self.dare_master.append(v)
        
        self.truth_pool = []
        self.dare_pool = []
        
        self.shuffle_pool()
        
        print(f"🔵 Truth Cards: {len(self.truth_master)}")
        print(f"🔴 Dare Cards: {len(self.dare_master)}")

    def shuffle_pool(self):
        """Isi ulang kedua tumpukan kartu"""
        self.truth_pool = list(self.truth_master)
        self.dare_pool = list(self.dare_master)
        random.shuffle(self.truth_pool)
        random.shuffle(self.dare_pool)
        print(f"🔄 Deck Dikocok! Truth: {len(self.truth_pool)}, Dare: {len(self.dare_pool)}")

    def draw_card(self, card_type="any"):
        """
        Ambil kartu berdasarkan tipe
        card_type: "truth", "dare", atau "any" (random)
        """
        if card_type == "truth":
            if not self.truth_pool:
                self.shuffle_pool()
            if self.truth_pool:
                return self.truth_pool.pop()
        
        elif card_type == "dare":
            if not self.dare_pool:
                self.shuffle_pool()
            if self.dare_pool:
                return self.dare_pool.pop()
        
        else:  # "any" - random antara truth atau dare
            choice = random.choice(["truth", "dare"])
            return self.draw_card(choice)
        
        return "Zonk! Tidak ada tantangan."
