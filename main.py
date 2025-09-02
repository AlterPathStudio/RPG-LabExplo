# mais.py — Mini RPG Tkinter avec nouvelle fonctionnalité (PV + pièges)
import tkinter as tk
from tkinter import messagebox



TILE = 32
RAW_MAP = [
    "############################",
    "#..*........TT......H..H..D#",
    "#...######..TT......H..H...#",
    "#...#....#..........HHHH...#",
    "#...#....#....N......X....##",  # X = piège
    "#...#....#.................#",
    "#...#....#..TT..====......#",
    "#...######..TT..=..=..HH..#",
    "#..*............=..=..HH..#",
    "#..H..H..........=..=.....#",
    "#..H..H......*....====..N.#",
    "#.............TT.........##",
    "#..TT........TT..........#",
    "#.......................N#",
    "#.........................#",
    "############################",
]
H, W = len(RAW_MAP), len(RAW_MAP[0])
SCREEN_W, SCREEN_H = W*TILE, H*TILE

# Couleurs
C_BG = "#121216"
C_FLOOR = "#373a43"
C_WALL = "#6a738c"
C_TREE = "#2e6648"
C_FENCE = "#9b8a67"
C_HOUSE = "#7b6161"
C_NPC = "#50a8d8"
C_PLAYER = "#deb64f"
C_ITEM = "#f4e36b"
C_DOOR = "#b99f6b"
C_TRAP = "#cc3333"
C_PANEL = "#1a1b20"
C_PANEL_BORDER = "#585b66"
C_TEXT = "#ebebf2"

# Collisions
BLOCKED_ALWAYS = {'#','H','T','='}
DOOR = 'D'
ITEM = '*'
TRAP = 'X'

# PNJ
NPCS = {
    (12,4): ["Salut encore!", "Collecte les 3 * dans le village.", "Attention aux pièges X !"],
    (24,10): ["Tu cherches des étoiles? J'en ai vu près des arbres."],
    (23,13): ["La sortie est au nord-est. Il te faut 3 *."],
}

class Game:
    def __init__(self, root):
        self.root = root
        root.title("Mini RPG - Ajout PV & pièges")
        self.canvas = tk.Canvas(root, width=SCREEN_W, height=SCREEN_H, bg=C_BG, highlightthickness=0)
        self.canvas.pack()
        self.grid = [list(r) for r in RAW_MAP]
        self.px, self.py = 2, 2

        self.items_needed = 3
        self.items_collected = 0

        # Nouvelle fonctionnalité : points de vie
        self.hp = 5

        self.dialog_active = False
        self.dialog_lines = []
        self.dialog_index = 0

        for k in ["<Up>", "<Down>", "<Left>", "<Right>", "w", "a", "s", "d", "z", "q", "e", "<Return>"]:
            root.bind(k, self.on_key)

        self.draw_world()

    # --- logique ---
    def in_bounds(self, x, y): return 0 <= x < W and 0 <= y < H

    def can_walk(self, x, y):
        if not self.in_bounds(x,y): return False
        tile = self.grid[y][x]
        if tile in BLOCKED_ALWAYS: return False
        if tile == DOOR and self.items_collected < self.items_needed:
            return False
        return True

    def adjacent_npc(self, x, y):
        for dx,dy in ((0,1),(0,-1),(1,0),(-1,0)):
            p = (x+dx, y+dy)
            if p in NPCS: return p
        return None

    def on_step(self, x, y):
        tile = self.grid[y][x]
        if tile == ITEM:
            self.items_collected += 1
            self.grid[y][x] = '.'  # ramassé
            self.draw_world()
            self.toast(f"Tu as ramassé une étoile! ({self.items_collected}/{self.items_needed})")
        elif tile == TRAP:
            self.hp -= 1
            self.toast(f"Ouch ! Un piège ! PV restants : {self.hp}")
            if self.hp <= 0:
                self.game_over()
        elif tile == DOOR and self.items_collected >= self.items_needed:
            self.victory()

    # --- input ---
    def on_key(self, event):
        key = event.keysym.lower()
        if self.dialog_active:
            if key in ("return","e"):
                self.dialog_index += 1
                if self.dialog_index >= len(self.dialog_lines):
                    self.dialog_active = False
                self.draw_world()
            return

        dx = dy = 0
        if key in ("up","w","z"):
            dy = -1
        elif key in ("down","s"):
            dy = 1
        elif key in ("left","a","q"):
            dx = -1
        elif key in ("right","d"):
            dx = 1
        elif key == "e":
            npc_pos = self.adjacent_npc(self.px, self.py)
            if npc_pos:
                self.dialog_active = True
                self.dialog_lines = NPCS[npc_pos][:]
                self.dialog_index = 0
                self.draw_world()
            return

        nx, ny = self.px + dx, self.py + dy
        if dx or dy:
            if self.can_walk(nx, ny):
                self.px, self.py = nx, ny
                self.on_step(self.px, self.py)
                self.draw_world()

    # --- rendu ---
    def draw_tile(self, x, y, ch):
        x0, y0 = x*TILE, y*TILE
        x1, y1 = x0+TILE, y0+TILE
        if ch == '#':
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=C_WALL, width=0)
        elif ch == 'T':
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=C_FLOOR, width=0)
            self.canvas.create_rectangle(x0+6, y0+4, x1-6, y1-4, fill=C_TREE, width=0)
        elif ch == '=':
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=C_FLOOR, width=0)
            self.canvas.create_rectangle(x0+6, y0+12, x1-6, y0+20, fill=C_FENCE, width=0)
        elif ch == 'H':
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=C_HOUSE, width=0)
        elif ch == 'N':
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=C_FLOOR, width=0)
            self.canvas.create_oval(x0+8, y0+8, x1-8, y1-8, fill=C_NPC, width=0)
        elif ch == ITEM:
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=C_FLOOR, width=0)
            self.canvas.create_oval(x0+10, y0+10, x1-10, y1-10, fill=C_ITEM, width=0)
        elif ch == DOOR:
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=C_DOOR, width=0)
        elif ch == TRAP:
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=C_FLOOR, width=0)
            self.canvas.create_text(x0+TILE//2, y0+TILE//2, text="X", fill=C_TRAP, font=("Arial", 16, "bold"))
        else:
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=C_FLOOR, width=0)

    def draw_dialog(self):
        panel_h = TILE*3
        y0 = SCREEN_H - panel_h
        self.canvas.create_rectangle(0, y0, SCREEN_W, SCREEN_H, fill=C_PANEL, outline=C_PANEL_BORDER, width=2)
        text = self.dialog_lines[self.dialog_index]
        self.canvas.create_text(16, y0+14, text=f'PNJ: "{text}"', anchor="nw", fill=C_TEXT, font=("Arial", 14))
        self.canvas.create_text(16, SCREEN_H-22, text="[Entrée] pour continuer • [E] pour fermer",
                                anchor="nw", fill="#c8c8d1", font=("Arial", 11))

    def draw_world(self):
        self.canvas.delete("all")
        for y,row in enumerate(self.grid):
            for x,ch in enumerate(row):
                self.draw_tile(x,y,ch)
        # joueur
        x0, y0 = self.px*TILE+4, self.py*TILE+4
        self.canvas.create_rectangle(x0, y0, x0+TILE-8, y0+TILE-8, fill=C_PLAYER, width=0)
        # HUD
        self.canvas.create_text(8, 8,
            text=f"Étoiles: {self.items_collected}/{self.items_needed} • PV: {self.hp}",
            anchor="nw", fill=C_TEXT, font=("Arial", 11))
        if self.dialog_active:
            self.draw_dialog()

    # --- UX ---
    def toast(self, msg):
        self.canvas.create_text(SCREEN_W//2, 28, text=msg, fill="#fff", font=("Arial", 12, "bold"))

    def victory(self):
        messagebox.showinfo("Victoire!", "La porte s'ouvre... Tu as gagné! 🎉")
        self.root.destroy()

    def game_over(self):
        messagebox.showerror("Game Over", "Tu n'as plus de points de vie... 💀")
        self.root.destroy()


def main():
    exit()
    root = tk.Tk()
    Game(root)
    root.mainloop()

if __name__ == "__main__":
    main()
