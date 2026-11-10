"""Snake game in Python using tkinter (no extra installs needed).

Controls:
    Arrow keys / WASD  - move
    P                  - pause / resume
    R / Space          - restart after game over
    Esc                - quit
"""

import random
import tkinter as tk

CELL = 20          # size of one grid cell in pixels
COLS = 30          # grid width in cells
ROWS = 22          # grid height in cells
START_SPEED = 120  # ms per step (lower = faster)
MIN_SPEED = 50

BG = "#111827"
GRID = "#1f2937"
SNAKE_HEAD = "#22c55e"
SNAKE_BODY = "#16a34a"
FOOD = "#ef4444"
TEXT = "#f9fafb"

DIRECTIONS = {
    "Up": (0, -1), "w": (0, -1), "W": (0, -1),
    "Down": (0, 1), "s": (0, 1), "S": (0, 1),
    "Left": (-1, 0), "a": (-1, 0), "A": (-1, 0),
    "Right": (1, 0), "d": (1, 0), "D": (1, 0),
}


class SnakeGame:
    def __init__(self, root):
        self.root = root
        root.title("Snake")
        root.resizable(False, False)

        self.high_score = 0
        self.score_label = tk.Label(root, font=("Consolas", 14, "bold"),
                                    bg=BG, fg=TEXT, anchor="w", padx=10, pady=6)
        self.score_label.pack(fill="x")

        self.canvas = tk.Canvas(root, width=COLS * CELL, height=ROWS * CELL,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        root.configure(bg=BG)
        root.bind("<Key>", self.on_key)

        self.after_id = None
        self.reset()

    # ----- game state -----
    def reset(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.pending_dirs = []
        self.score = 0
        self.speed = START_SPEED
        self.running = True
        self.paused = False
        self.food = self.spawn_food()
        self.update_score()
        self.draw()
        self.after_id = self.root.after(self.speed, self.tick)

    def spawn_food(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in self.snake]
        return random.choice(free) if free else None

    def update_score(self):
        self.score_label.config(
            text=f"Score: {self.score}    High score: {self.high_score}")

    # ----- input -----
    def on_key(self, event):
        key = event.keysym
        if key == "Escape":
            self.root.destroy()
            return
        if not self.running:
            if key in ("r", "R", "space"):
                self.reset()
            return
        if key in ("p", "P"):
            self.paused = not self.paused
            self.draw()
            return
        if key in DIRECTIONS and not self.paused:
            new = DIRECTIONS[key]
            last = self.pending_dirs[-1] if self.pending_dirs else self.direction
            # ignore reversing into itself and duplicate presses
            if new != last and (new[0] != -last[0] or new[1] != -last[1]):
                if len(self.pending_dirs) < 3:
                    self.pending_dirs.append(new)

    # ----- main loop -----
    def tick(self):
        if not self.running:
            return
        if not self.paused:
            self.step()
        self.draw()
        if self.running:
            self.after_id = self.root.after(self.speed, self.tick)

    def step(self):
        if self.pending_dirs:
            self.direction = self.pending_dirs.pop(0)
        hx, hy = self.snake[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        eating = new_head == self.food
        body = self.snake if eating else self.snake[:-1]

        if (not 0 <= new_head[0] < COLS or not 0 <= new_head[1] < ROWS
                or new_head in body):
            self.game_over()
            return

        self.snake.insert(0, new_head)
        if eating:
            self.score += 10
            self.high_score = max(self.high_score, self.score)
            self.speed = max(MIN_SPEED, self.speed - 3)
            self.update_score()
            self.food = self.spawn_food()
            if self.food is None:  # board filled - you win
                self.game_over(won=True)
        else:
            self.snake.pop()

    def game_over(self, won=False):
        self.running = False
        self.won = won

    # ----- drawing -----
    def draw(self):
        c = self.canvas
        c.delete("all")
        for x in range(COLS):
            for y in range(ROWS):
                if (x + y) % 2 == 0:
                    c.create_rectangle(x * CELL, y * CELL, (x + 1) * CELL,
                                       (y + 1) * CELL, fill=GRID, outline="")
        if self.food:
            fx, fy = self.food
            c.create_oval(fx * CELL + 3, fy * CELL + 3, (fx + 1) * CELL - 3,
                          (fy + 1) * CELL - 3, fill=FOOD, outline="")
        for i, (x, y) in enumerate(self.snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            c.create_rectangle(x * CELL + 1, y * CELL + 1, (x + 1) * CELL - 1,
                               (y + 1) * CELL - 1, fill=color, outline="")

        w, h = COLS * CELL, ROWS * CELL
        if not self.running:
            title = "YOU WIN!" if getattr(self, "won", False) else "GAME OVER"
            c.create_text(w / 2, h / 2 - 20, text=title, fill=TEXT,
                          font=("Consolas", 32, "bold"))
            c.create_text(w / 2, h / 2 + 20,
                          text="Press R or Space to restart, Esc to quit",
                          fill=TEXT, font=("Consolas", 12))
        elif self.paused:
            c.create_text(w / 2, h / 2, text="PAUSED", fill=TEXT,
                          font=("Consolas", 28, "bold"))


def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
