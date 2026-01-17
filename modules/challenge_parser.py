import re

def get_move_effect(text):
    """
    Mendeteksi perintah 'Mundur' atau 'Maju' dalam teks tantangan.
    Mengembalikan angka (positif untuk maju, negatif untuk mundur).
    """
    if not text:
        return 0

    numbers = re.findall(r'\d+', text)
    if not numbers:
        return 0
    
    steps = int(numbers[0]) # Ambil angka pertama yang ditemukan
    
    text_lower = text.lower()
    
    if "mundur" in text_lower:
        return -steps
    elif "maju" in text_lower or "bonus" in text_lower:
        return steps
        
    return 0