"""
AI Smart Route Finder
B.Tech Artificial Intelligence Course Project

Algorithms:
1. Breadth First Search (BFS)
2. Depth First Search (DFS)
3. Greedy Best First Search
4. A* Search
5. Hill Climbing

The application visualizes state-space search on a grid.
No external Python packages are required.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import heapq, time, random, math

ROWS, COLS = 20, 30
CELL = 25

EMPTY, WALL, START, GOAL, VISITED, PATH = 0, 1, 2, 3, 4, 5

class RouteFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Smart Route Finder — Search Algorithm Visualizer")
        self.root.resizable(False, False)

        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.start = (2, 2)
        self.goal = (17, 27)
        self.running = False

        top = ttk.Frame(root, padding=8)
        top.grid(row=0, column=0, sticky="ew")

        ttk.Label(top, text="Algorithm:").grid(row=0, column=0, padx=4)
        self.algorithm = ttk.Combobox(
            top, state="readonly", width=22,
            values=["A* Search", "BFS", "DFS", "Greedy Best First", "Hill Climbing"]
        )
        self.algorithm.current(0)
        self.algorithm.grid(row=0, column=1, padx=4)

        ttk.Button(top, text="Find Path", command=self.run).grid(row=0, column=2, padx=4)
        ttk.Button(top, text="Clear", command=self.clear).grid(row=0, column=3, padx=4)
        ttk.Button(top, text="Random Maze", command=self.random_maze).grid(row=0, column=4, padx=4)
        ttk.Button(top, text="Compare All", command=self.compare).grid(row=0, column=5, padx=4)

        self.canvas = tk.Canvas(root, width=COLS*CELL, height=ROWS*CELL,
                                bg="white", highlightthickness=0)
        self.canvas.grid(row=1, column=0, padx=8, pady=4)
        self.canvas.bind("<Button-1>", self.toggle_wall)
        self.canvas.bind("<Button-3>", self.set_goal)

        info = ttk.Frame(root, padding=8)
        info.grid(row=2, column=0, sticky="ew")

        self.status = tk.StringVar(value="Click cells to add/remove walls. Left-click toggles wall; right-click sets destination.")
        self.stats = tk.StringVar(value="Ready.")
        ttk.Label(info, textvariable=self.status, wraplength=760).grid(row=0, column=0, sticky="w")
        ttk.Label(info, textvariable=self.stats, font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(5,0))

        legend = ttk.Frame(root, padding=(8, 0, 8, 8))
        legend.grid(row=3, column=0)
        for text, color in [("Start","#35a853"),("Goal","#ea4335"),("Wall","#333333"),
                            ("Visited","#b7d9ff"),("Path","#ffd54f")]:
            tk.Label(legend, text="  "+text+"  ", bg=color,
                     fg="white" if color in ["#333333","#35a853","#ea4335"] else "black").pack(side="left", padx=3)

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c*CELL, r*CELL
                x2, y2 = x1+CELL, y1+CELL
                val = self.grid[r][c]
                color = {
                    EMPTY:"#ffffff", WALL:"#333333", START:"#35a853",
                    GOAL:"#ea4335", VISITED:"#b7d9ff", PATH:"#ffd54f"
                }[val]
                self.canvas.create_rectangle(x1,y1,x2,y2,fill=color,outline="#dddddd")
        sr, sc = self.start
        gr, gc = self.goal
        self.canvas.create_text(sc*CELL+CELL/2, sr*CELL+CELL/2, text="S", font=("Arial",11,"bold"),
                                fill="white")
        self.canvas.create_text(gc*CELL+CELL/2, gr*CELL+CELL/2, text="G", font=("Arial",11,"bold"),
                                fill="white")

    def clear(self):
        if self.running: return
        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.draw()
        self.stats.set("Ready.")

    def random_maze(self):
        if self.running: return
        self.grid = [[WALL if random.random() < 0.25 else EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        sr, sc = self.start
        gr, gc = self.goal
        self.grid[sr][sc] = EMPTY
        self.grid[gr][gc] = EMPTY
        # Guarantee a simple corridor so the demo usually has a solution.
        for c in range(sc, gc+1):
            self.grid[sr][c] = EMPTY
        for r in range(sr, gr+1):
            self.grid[r][gc] = EMPTY
        self.draw()

    def toggle_wall(self, event):
        if self.running: return
        c, r = event.x // CELL, event.y // CELL
        if not (0 <= r < ROWS and 0 <= c < COLS): return
        p = (r,c)
        if p in (self.start, self.goal): return
        self.grid[r][c] = EMPTY if self.grid[r][c] == WALL else WALL
        self.draw()

    def set_goal(self, event):
        if self.running: return
        c, r = event.x // CELL, event.y // CELL
        if not (0 <= r < ROWS and 0 <= c < COLS): return
        if self.grid[r][c] == WALL or (r,c) == self.start: return
        self.goal = (r,c)
        self.draw()

    def neighbors(self, p):
        r,c = p
        # Fixed order makes demonstrations reproducible.
        for dr,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr,nc = r+dr,c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid[nr][nc] != WALL:
                yield (nr,nc)

    @staticmethod
    def h(a,b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def search(self, algorithm):
        start, goal = self.start, self.goal
        parent = {start: None}
        visited_order = []

        if algorithm == "BFS":
            frontier = deque([start])
            seen = {start}
            while frontier:
                cur = frontier.popleft()
                visited_order.append(cur)
                if cur == goal: break
                for nxt in self.neighbors(cur):
                    if nxt not in seen:
                        seen.add(nxt); parent[nxt] = cur; frontier.append(nxt)

        elif algorithm == "DFS":
            frontier = [start]
            seen = {start}
            while frontier:
                cur = frontier.pop()
                visited_order.append(cur)
                if cur == goal: break
                ns = list(self.neighbors(cur))
                for nxt in reversed(ns):
                    if nxt not in seen:
                        seen.add(nxt); parent[nxt] = cur; frontier.append(nxt)

        elif algorithm == "Greedy Best First":
            counter = 0
            frontier = [(self.h(start,goal), counter, start)]
            seen = {start}
            while frontier:
                _,_,cur = heapq.heappop(frontier)
                visited_order.append(cur)
                if cur == goal: break
                for nxt in self.neighbors(cur):
                    if nxt not in seen:
                        seen.add(nxt); parent[nxt] = cur
                        counter += 1
                        heapq.heappush(frontier, (self.h(nxt,goal), counter, nxt))

        elif algorithm == "A* Search":
            counter = 0
            g = {start: 0}
            frontier = [(self.h(start,goal), counter, start)]
            closed = set()
            while frontier:
                _,_,cur = heapq.heappop(frontier)
                if cur in closed: continue
                closed.add(cur)
                visited_order.append(cur)
                if cur == goal: break
                for nxt in self.neighbors(cur):
                    new_g = g[cur] + 1
                    if new_g < g.get(nxt, math.inf):
                        g[nxt] = new_g
                        parent[nxt] = cur
                        counter += 1
                        f = new_g + self.h(nxt,goal)
                        heapq.heappush(frontier, (f, counter, nxt))

        elif algorithm == "Hill Climbing":
            cur = start
            seen = {cur}
            visited_order.append(cur)
            while cur != goal:
                candidates = [n for n in self.neighbors(cur) if n not in seen]
                if not candidates: break
                nxt = min(candidates, key=lambda x: self.h(x,goal))
                if self.h(nxt,goal) >= self.h(cur,goal):
                    break
                parent[nxt] = cur
                cur = nxt
                seen.add(cur)
                visited_order.append(cur)

        path = []
        if goal in parent:
            cur = goal
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
        return visited_order, path

    def animate(self, visited, path, algorithm, i=0):
        if i < len(visited):
            p = visited[i]
            if p not in (self.start, self.goal):
                self.grid[p[0]][p[1]] = VISITED
            self.draw()
            self.root.after(12, lambda: self.animate(visited,path,algorithm,i+1))
            return
        self.animate_path(path, algorithm)

    def animate_path(self, path, algorithm, i=0):
        if i < len(path):
            p = path[i]
            if p not in (self.start, self.goal):
                self.grid[p[0]][p[1]] = PATH
            self.draw()
            self.root.after(35, lambda: self.animate_path(path,algorithm,i+1))
            return
        self.running = False
        if path:
            self.stats.set(f"{algorithm}: path length = {len(path)-1} | nodes explored = {len(self.last_visited)}")
            self.status.set("Path found. Green = start, red = goal, yellow = selected path.")
        else:
            self.stats.set(f"{algorithm}: no path found | nodes explored = {len(self.last_visited)}")
            self.status.set("No path found with this search strategy.")

    def run(self):
        if self.running: return
        # Remove previous result while keeping walls.
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] in (VISITED, PATH):
                    self.grid[r][c] = EMPTY
        algorithm = self.algorithm.get()
        self.running = True
        self.status.set(f"Running {algorithm}...")
        self.stats.set("Searching...")
        self.draw()
        self.last_visited, path = self.search(algorithm)
        self.animate(self.last_visited, path, algorithm)

    def compare(self):
        if self.running: return
        results = []
        for algorithm in ["BFS","DFS","Greedy Best First","A* Search","Hill Climbing"]:
            t0 = time.perf_counter()
            visited, path = self.search(algorithm)
            elapsed = (time.perf_counter()-t0)*1000
            results.append((algorithm, len(path)-1 if path else "—", len(visited), elapsed))
        win = tk.Toplevel(self.root)
        win.title("Algorithm Comparison")
        win.resizable(False,False)
        ttk.Label(win, text="Search Algorithm Comparison", font=("Arial",13,"bold")).pack(pady=10)
        tree = ttk.Treeview(win, columns=("Algorithm","Path","Visited","Time"), show="headings", height=6)
        for col, heading in zip(("Algorithm","Path","Visited","Time"),
                                ("Algorithm","Path Length","Nodes Explored","Time (ms)")):
            tree.heading(col,text=heading)
            tree.column(col,width=145,anchor="center")
        for row in results:
            tree.insert("", "end", values=(row[0],row[1],row[2],f"{row[3]:.3f}"))
        tree.pack(padx=10,pady=10)
        ttk.Label(win, text="A* uses f(n)=g(n)+h(n) and is the main proposed algorithm.",
                  wraplength=620).pack(padx=10,pady=(0,10))

if __name__ == "__main__":
    root = tk.Tk()
    RouteFinder(root)
    root.mainloop()
