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
