# game.py — Commit 1
import tkinter as tk

TILE = 32
RAW_MAP = [
    "####################",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "#..................#",
    "####################",
]
H, W = len(RAW_MAP), len(RAW_MAP[0])
SCREEN_W, SCREEN_H = W*TILE, H*TILE

COLOR_BG = "#121216"
COLOR_FLOOR = "#32343c"
COLOR_WALL = "#677189"
COLOR_PLAYER = "#deb64f"
COLOR_TEXT = "#e6e6eb"

BLOCKED = {'#'}

class Game:
    def __init__(self, root):
        self.root = root
        root.title("Mini RPG - Commit 1 (Tkinter)")
        self.canvas = tk.Canvas(root, width=SCREEN_W, height=SCREEN_H, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack()
        self.grid = [list(r) for r in RAW_MAP]
        self.px, self.py = 2, 2

        # Bind clavier
        for k in ["<Up>", "<Down>", "<Left>", "<Right>", "w", "a", "s", "d", "z", "q"]:
            root.bind(k, self.on_key)

        self.draw_world()

    def can_walk(self, x, y):
        if x < 0 or y < 0 or x >= W or y >= H:
            return False
        return self.grid[y][x] not in BLOCKED

    def on_key(self, event):
        key = event.keysym.lower()
        dx = dy = 0
        if key in ("up", "w", "z"):
            dy = -1
        elif key in ("down", "s"):
            dy = 1
        elif key in ("left", "a", "q"):
            dx = -1
        elif key in ("right", "d"):
            dx = 1
        nx, ny = self.px + dx, self.py + dy
        if dx or dy:
            if self.can_walk(nx, ny):
                self.px, self.py = nx, ny
                self.draw_world()

    def draw_world(self):
        self.canvas.delete("all")
        # tuiles
        for y, row in enumerate(self.grid):
            for x, ch in enumerate(row):
                x0, y0 = x*TILE, y*TILE
                x1, y1 = x0+TILE, y0+TILE
                if ch == '#':
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=COLOR_WALL, width=0)
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=COLOR_FLOOR, width=0)
        # joueur
        x0, y0 = self.px*TILE+4, self.py*TILE+4
        self.canvas.create_rectangle(x0, y0, x0+TILE-8, y0+TILE-8, fill=COLOR_PLAYER, width=0)
        # HUD
        self.canvas.create_text(8, 8, text="WASD/Flèches pour bouger • Fermer la fenêtre pour quitter",
                                anchor="nw", fill=COLOR_TEXT, font=("Arial", 11))

def main():
    root = tk.Tk()
    Game(root)
    root.mainloop()

if __name__ == "__main__":
    main()
