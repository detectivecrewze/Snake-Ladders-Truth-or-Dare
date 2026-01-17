import random

def generate_random_objects(total_cells, num_snakes=6, num_ladders=6):
    snakes = {}
    ladders = {}
    used_cells = {1, total_cells} # Jangan ada objek di start (1) dan finish (70)

    def get_valid_pos(is_snake):
        for _ in range(100):
            start = random.randint(5, total_cells - 5)
            end = random.randint(5, total_cells - 5)
            
            if abs(start - end) < 10: continue
            
            if is_snake:
                if start > end and start not in used_cells and end not in used_cells:
                    return start, end
            else:
                if start < end and start not in used_cells and end not in used_cells:
                    return start, end
        return None, None

    for _ in range(num_ladders):
        s, e = get_valid_pos(is_snake=False)
        if s:
            ladders[s] = e
            used_cells.update([s, e])

    for _ in range(num_snakes):
        s, e = get_valid_pos(is_snake=True)
        if s:
            snakes[s] = e
            used_cells.update([s, e])

    return snakes, ladders