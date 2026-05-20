import random


class Game2048:
    def __init__(self):
        self.grid = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.won = False
        self.keep_playing = False
        self.spawn()
        self.spawn()

    def spawn(self):
        empty = [(r, c) for r in range(4) for c in range(4) if self.grid[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.grid[r][c] = 2 if random.random() < 0.9 else 4

    def _merge_line(self, line):
        new_line = [v for v in line if v != 0]
        i = 0
        while i < len(new_line) - 1:
            if new_line[i] == new_line[i + 1]:
                new_line[i] *= 2
                self.score += new_line[i]
                new_line.pop(i + 1)
            i += 1
        return new_line + [0] * (4 - len(new_line))

    def move(self, direction):
        old_grid = [row[:] for row in self.grid]

        if direction == 0:  # LEFT
            for r in range(4):
                self.grid[r] = self._merge_line(self.grid[r])
        elif direction == 1:  # RIGHT
            for r in range(4):
                self.grid[r] = self._merge_line(self.grid[r][::-1])[::-1]
        elif direction == 2:  # UP
            for c in range(4):
                col = self._merge_line([self.grid[r][c] for r in range(4)])
                for r in range(4):
                    self.grid[r][c] = col[r]
        elif direction == 3:  # DOWN
            for c in range(4):
                col = self._merge_line([self.grid[r][c] for r in range(3, -1, -1)])
                for r in range(4):
                    self.grid[r][c] = col[3 - r]

        changed = self.grid != old_grid
        if changed:
            self.spawn()
            if self.has_won() and not self.won:
                self.won = True

        return changed

    def is_game_over(self):
        if any(0 in row for row in self.grid):
            return False
        for r in range(4):
            for c in range(4):
                val = self.grid[r][c]
                if c < 3 and self.grid[r][c + 1] == val:
                    return False
                if r < 3 and self.grid[r + 1][c] == val:
                    return False
        return True

    def has_won(self):
        return any(v >= 2048 for row in self.grid for v in row)

    def restart(self):
        self.__init__()


# === Renderer ===
import pygame

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 600
CELL_SIZE = 100
GAP = 15
GRID_ORIGIN_X = 20
GRID_ORIGIN_Y = 110

BG_COLOR = (250, 248, 239)
GRID_BG = (187, 173, 160)
SCORE_BG = (187, 173, 160)

TILE_COLORS = {
    0:    (205, 193, 180),
    2:    (238, 228, 218),
    4:    (237, 224, 200),
    8:    (242, 177, 121),
    16:   (245, 149, 99),
    32:   (246, 124, 95),
    64:   (246, 94, 59),
    128:  (237, 207, 114),
    256:  (237, 204, 97),
    512:  (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}


def get_tile_color(value):
    return TILE_COLORS.get(value, (60, 58, 50))


def get_text_color(value):
    return (119, 110, 101) if value <= 4 else (249, 246, 242)


def get_font_size(value):
    if value < 100:
        return 48
    elif value < 1000:
        return 36
    elif value < 10000:
        return 28
    return 22


def draw_game(screen, game, fonts):
    screen.fill(BG_COLOR)

    # Score panel
    pygame.draw.rect(screen, SCORE_BG, (15, 15, 470, 70), border_radius=6)
    title_surf = fonts["title"].render("2048", True, (249, 246, 242))
    screen.blit(title_surf, (30, 22))
    score_surf = fonts["score"].render(f"Score: {game.score}", True, (249, 246, 242))
    screen.blit(score_surf, (200, 32))

    # Grid background
    pygame.draw.rect(screen, GRID_BG, (15, 105, 470, 470), border_radius=6)

    # Tiles
    for r in range(4):
        for c in range(4):
            val = game.grid[r][c]
            x = GRID_ORIGIN_X + c * (CELL_SIZE + GAP)
            y = GRID_ORIGIN_Y + r * (CELL_SIZE + GAP)
            color = get_tile_color(val)
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE), border_radius=5)

            if val != 0:
                font = fonts[get_font_size(val)]
                text_surf = font.render(str(val), True, get_text_color(val))
                text_rect = text_surf.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                screen.blit(text_surf, text_rect)

    # Game Over overlay
    if game.is_game_over():
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        screen.blit(overlay, (0, 0))
        go_text = fonts["overlay_title"].render("Game Over!", True, (119, 110, 101))
        go_rect = go_text.get_rect(center=(250, 300))
        screen.blit(go_text, go_rect)
        restart_text = fonts["overlay_sub"].render("Press R to restart", True, (119, 110, 101))
        restart_rect = restart_text.get_rect(center=(250, 360))
        screen.blit(restart_text, restart_rect)

    # Win overlay
    elif game.won and not game.keep_playing:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        screen.blit(overlay, (0, 0))
        win_text = fonts["overlay_title"].render("You Win!", True, (237, 194, 46))
        win_rect = win_text.get_rect(center=(250, 290))
        screen.blit(win_text, win_rect)
        continue_text = fonts["overlay_sub"].render("Press C to continue", True, (119, 110, 101))
        continue_rect = continue_text.get_rect(center=(250, 350))
        screen.blit(continue_text, continue_rect)
