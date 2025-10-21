import tkinter as tk
from tkinter import simpledialog, messagebox
import heapq
import time
import math

CELL_SIZE = 28

# cell types
EMPTY, WALL, POISON, START, GOAL, PATH = 0, 1, 2, 3, 4, 5
COLORS = {
    EMPTY: "white",
    WALL: "black",
    POISON: "purple",
    START: "green",
    GOAL: "red",
    PATH: "yellow"
}

class GridApp:
    def __init__(self, root):
        self.root = root
        root.title("Hormiga - Dynamic Weighting")

        # default grid
        self.rows = 15
        self.cols = 20
        self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.goal = None

        # search params
        self.avoid_poison = tk.BooleanVar(value=False)
        self.poison_cost = tk.DoubleVar(value=5.0)  # penalty to enter poison
        self.epsilon = tk.DoubleVar(value=2.0)  # epsilon for dynamic weighting
        self.animation_speed = tk.DoubleVar(value=0.05)

        # UI controls
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(control_frame, text="Tamaño grid", command=self.ask_grid_size).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Borrar todo", command=self.clear_grid).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Colocar inicio", command=lambda: self.set_tool("start")).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Colocar meta", command=lambda: self.set_tool("goal")).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Colocar pared", command=lambda: self.set_tool("wall")).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Colocar veneno", command=lambda: self.set_tool("poison")).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Borrar celda", command=lambda: self.set_tool("erase")).pack(side=tk.LEFT)

        tk.Checkbutton(control_frame, text="Evitar veneno (prohibir)", variable=self.avoid_poison).pack(side=tk.LEFT, padx=6)
        tk.Label(control_frame, text="Eps").pack(side=tk.LEFT)
        tk.Entry(control_frame, textvariable=self.epsilon, width=4).pack(side=tk.LEFT)
        tk.Label(control_frame, text="Penal veneno").pack(side=tk.LEFT)
        tk.Entry(control_frame, textvariable=self.poison_cost, width=4).pack(side=tk.LEFT)
        tk.Label(control_frame, text="Vel anim").pack(side=tk.LEFT)
        tk.Entry(control_frame, textvariable=self.animation_speed, width=4).pack(side=tk.LEFT)

        tk.Button(control_frame, text="RUN", command=self.run_search, bg="lightblue").pack(side=tk.RIGHT)

        # canvas
        self.canvas = tk.Canvas(root, width=self.cols*CELL_SIZE, height=self.rows*CELL_SIZE, bg="grey")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.canvas_click)

        self.tool = "wall"  # default
        self.draw()

    def ask_grid_size(self):
        r = simpledialog.askinteger("Filas", "Número de filas:", initialvalue=self.rows, minvalue=5, maxvalue=60)
        c = simpledialog.askinteger("Columnas", "Número de columnas:", initialvalue=self.cols, minvalue=5, maxvalue=60)
        if r and c:
            self.rows, self.cols = r, c
            self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
            self.start = None; self.goal = None
            self.canvas.config(width=self.cols*CELL_SIZE, height=self.rows*CELL_SIZE)
            self.draw()

    def clear_grid(self):
        self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None; self.goal = None
        self.draw()

    def set_tool(self, t):
        self.tool = t

    def canvas_click(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols: return
        t = self.tool
        if t == "start":
            if self.start: self.grid[self.start[0]][self.start[1]] = EMPTY
            self.start = (r, c)
            self.grid[r][c] = START
        elif t == "goal":
            if self.goal: self.grid[self.goal[0]][self.goal[1]] = EMPTY
            self.goal = (r, c)
            self.grid[r][c] = GOAL
        elif t == "wall":
            if self.grid[r][c] in (START, GOAL):
                if self.grid[r][c] == START: self.start = None
                if self.grid[r][c] == GOAL: self.goal = None
            self.grid[r][c] = WALL
        elif t == "poison":
            if self.grid[r][c] in (START, GOAL):
                messagebox.showinfo("Info", "No puedes poner veneno sobre inicio/meta")
            else:
                self.grid[r][c] = POISON
        elif t == "erase":
            if self.grid[r][c] == START: self.start = None
            if self.grid[r][c] == GOAL: self.goal = None
            self.grid[r][c] = EMPTY
        self.draw()

    def draw(self, highlight_path=None):
        self.canvas.delete("all")
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.grid[i][j]
                color = COLORS.get(cell, "white")
                x0, y0 = j*CELL_SIZE, i*CELL_SIZE
                x1, y1 = x0+CELL_SIZE, y0+CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="lightgrey")
        if highlight_path:
            for (r,c) in highlight_path:
                if self.grid[r][c] not in (START, GOAL):
                    x0, y0 = c*CELL_SIZE, r*CELL_SIZE
                    x1, y1 = x0+CELL_SIZE, y0+CELL_SIZE
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=COLORS[PATH], outline="lightgrey")
        self.root.update()

    def heuristic(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def neighbors(self, node):
        r,c = node
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                yield (nr,nc)

    def run_search(self):
        if not self.start or not self.goal:
            messagebox.showinfo("Info", "Define inicio y meta")
            return
        path = self.dynamic_weighting_search()
        if path:
            for step in path:
                self.draw(highlight_path=[step])
                time.sleep(self.animation_speed.get())
            self.draw(highlight_path=path)
            messagebox.showinfo("Resultado", f"Ruta encontrada. Longitud: {len(path)-1} pasos.")
        else:
            messagebox.showinfo("Resultado", "No se encontró ruta.")

    def reconstruct(self, came_from, node):
        path = [node]
        while node in came_from:
            node = came_from[node]
            path.append(node)
        return list(reversed(path))

    def dynamic_weighting_search(self):
        start = self.start; goal = self.goal
        N = max(1, self.heuristic(start, goal))
        eps = float(self.epsilon.get())
        poison_cost = float(self.poison_cost.get())
        avoid_poison = self.avoid_poison.get()

        open_heap = []
        counter = 0
        gscore = {start: 0}
        depths = {start: 0}
        came_from = {}

        h0 = self.heuristic(start, goal)
        f0 = 0 + h0 + eps*(1 - 0/N)*h0
        heapq.heappush(open_heap, (f0, 0, 0, start, counter)); counter += 1
        closed = set()

        while open_heap:
            f, g, d, node, _ = heapq.heappop(open_heap)
            if node in closed: continue
            closed.add(node)

            if node == goal:
                return self.reconstruct(came_from, node)

            for nei in self.neighbors(node):
                if self.grid[nei[0]][nei[1]] == WALL: continue
                if avoid_poison and self.grid[nei[0]][nei[1]] == POISON: continue

                step_cost = 1.0
                if self.grid[nei[0]][nei[1]] == POISON:
                    step_cost += poison_cost

                tentative_g = g + step_cost
                nd = d + 1
                if tentative_g < gscore.get(nei, math.inf):
                    gscore[nei] = tentative_g
                    depths[nei] = nd
                    came_from[nei] = node
                    h = self.heuristic(nei, goal)
                    weight = eps * (1.0 - (nd / float(N)))
                    if weight < 0: weight = 0.0
                    fval = tentative_g + h + weight * h
                    heapq.heappush(open_heap, (fval, tentative_g, nd, nei, counter)); counter += 1
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    root.mainloop()