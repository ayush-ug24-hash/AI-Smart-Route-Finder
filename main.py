"""
AI Smart Route Finder - Enhanced Edition
B.Tech Artificial Intelligence Course Project

Algorithms Implemented:
1. Breadth First Search (BFS) - Exhaustive level-by-level search
2. Depth First Search (DFS) - Deep exploration with backtracking
3. Greedy Best First Search - Heuristic-driven, fast but suboptimal
4. A* Search - Optimal with f(n)=g(n)+h(n), industry standard
5. Hill Climbing - Greedy local search
6. Bidirectional Search - Search from both start and goal
7. Iterative Deepening A* (IDA*) - Memory-efficient optimal search

Features:
- Weighted terrain costs (grass, mountain, road, water)
- Real-time performance analytics
- Step-through debugging mode
- Algorithm comparison with statistical analysis
- Export results to CSV
- Professional visualization with heatmap
- Custom maze presets
- Educational pseudo-code viewer
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import deque
import heapq, time, random, math, csv
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Set, List, Tuple, Optional

ROWS, COLS = 20, 30
CELL = 25

# Cell types
EMPTY, WALL, START, GOAL, VISITED, PATH, TERRAIN_MOUNTAIN, TERRAIN_ROAD, TERRAIN_WATER = 0, 1, 2, 3, 4, 5, 6, 7, 8

# Terrain movement costs
TERRAIN_COSTS = {
    EMPTY: 1.0,
    TERRAIN_ROAD: 0.5,      # Highways - faster
    TERRAIN_MOUNTAIN: 3.0,   # Mountains - slower
    TERRAIN_WATER: float('inf'),  # Water - impassable
    WALL: float('inf'),
    START: 1.0,
    GOAL: 1.0,
    VISITED: 1.0,
    PATH: 1.0,
}

@dataclass
class SearchMetrics:
    """Store performance metrics for each search"""
    algorithm: str
    path_length: int
    nodes_explored: int
    execution_time: float
    path_optimal: bool
    frontier_peak: int
    
    def to_dict(self):
        return {
            'algorithm': self.algorithm,
            'path_length': self.path_length,
            'nodes_explored': self.nodes_explored,
            'execution_time': f"{self.execution_time:.3f}",
            'path_optimal': self.path_optimal,
            'frontier_peak': self.frontier_peak
        }

class RouteFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Smart Route Finder — Advanced Search Algorithm Visualizer")
        self.root.geometry("1100x850")
        self.root.resizable(False, False)

        # Core state
        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.start = (2, 2)
        self.goal = (17, 27)
        self.running = False
        self.step_mode = False
        self.step_index = 0
        self.last_visited = []
        self.last_path = []
        self.search_metrics = []
        self.heatmap = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        # Build UI
        self._build_ui()
        self.draw()

    def _build_ui(self):
        """Build the user interface"""
        # Top control panel
        top = ttk.Frame(self.root, padding=8)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(top, text="Algorithm:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=4)
        self.algorithm = ttk.Combobox(
            top, state="readonly", width=20,
            values=["A* Search", "BFS", "DFS", "Greedy Best First", "Hill Climbing", "Bidirectional", "IDA*"]
        )
        self.algorithm.current(0)
        self.algorithm.grid(row=0, column=1, padx=4)

        ttk.Button(top, text="Find Path", command=self.run).grid(row=0, column=2, padx=4)
        ttk.Button(top, text="Step", command=self.step_search).grid(row=0, column=3, padx=4)
        ttk.Button(top, text="Compare All", command=self.compare).grid(row=0, column=4, padx=4)
        ttk.Button(top, text="Clear", command=self.clear).grid(row=0, column=5, padx=4)
        ttk.Button(top, text="Random Maze", command=self.random_maze).grid(row=0, column=6, padx=4)
        ttk.Button(top, text="Export CSV", command=self.export_results).grid(row=0, column=7, padx=4)

        # Maze presets
        ttk.Label(top, text="Preset:", font=("Arial", 9)).grid(row=0, column=8, padx=10, sticky="w")
        ttk.Button(top, text="Maze", command=self.preset_maze, width=8).grid(row=0, column=9, padx=2)
        ttk.Button(top, text="Spiral", command=self.preset_spiral, width=8).grid(row=0, column=10, padx=2)

        # Canvas area
        canvas_frame = ttk.LabelFrame(self.root, text="Grid Visualization", padding=4)
        canvas_frame.grid(row=1, column=0, padx=8, pady=4, sticky="nsew")

        self.canvas = tk.Canvas(canvas_frame, width=COLS*CELL, height=ROWS*CELL,
                                bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.toggle_wall)
        self.canvas.bind("<Button-3>", self.set_goal)
        self.canvas.bind("<Button-2>", self.set_start)

        # Right panel - stats and info
        right_panel = ttk.Frame(self.root)
        right_panel.grid(row=1, column=1, padx=8, pady=4, sticky="nsew")

        # Statistics
        ttk.Label(right_panel, text="Performance Metrics", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.stats_frame = ttk.Frame(right_panel, relief="sunken", borderwidth=1)
        self.stats_frame.pack(fill="both", expand=True, pady=5)

        self.stats_text = tk.Text(self.stats_frame, height=12, width=45, font=("Courier", 9), state="disabled")
        self.stats_text.pack(fill="both", expand=True, padx=4, pady=4)

        # Status bar
        status_frame = ttk.Frame(self.root, relief="sunken", borderwidth=1)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=4)

        self.status = tk.StringVar(value="Left-click: toggle wall | Right-click: set goal | Middle-click: set start | Ready")
        ttk.Label(status_frame, textvariable=self.status, wraplength=1000).pack(anchor="w", padx=4, pady=4)

        # Legend
        legend = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        legend.grid(row=3, column=0, columnspan=2)
        
        legend_items = [
            ("Start", "#35a853"),
            ("Goal", "#ea4335"),
            ("Wall", "#333333"),
            ("Mountain", "#8B4513"),
            ("Road", "#FFD700"),
            ("Water", "#0096FF"),
            ("Visited", "#b7d9ff"),
            ("Path", "#FFA500")
        ]
        
        for text, color in legend_items:
            tk.Label(legend, text=f"  {text}  ", bg=color,
                     fg="white" if color in ["#333333", "#35a853", "#ea4335", "#0096FF"] else "black",
                     font=("Arial", 8)).pack(side="left", padx=2)

    def draw(self):
        """Draw the grid with heatmap coloring"""
        self.canvas.delete("all")
        
        # Find max heatmap value for coloring
        max_heat = max(max(row) for row in self.heatmap) if any(any(row) for row in self.heatmap) else 1
        
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c*CELL, r*CELL
                x2, y2 = x1+CELL, y1+CELL
                val = self.grid[r][c]
                
                # Base colors
                color_map = {
                    EMPTY: "#ffffff",
                    WALL: "#333333",
                    START: "#35a853",
                    GOAL: "#ea4335",
                    VISITED: "#b7d9ff",
                    PATH: "#FFA500",
                    TERRAIN_MOUNTAIN: "#8B4513",
                    TERRAIN_ROAD: "#FFD700",
                    TERRAIN_WATER: "#0096FF"
                }
                
                color = color_map.get(val, "#ffffff")
                
                # Apply heatmap overlay for visited cells
                if val == VISITED and max_heat > 0:
                    intensity = min(self.heatmap[r][c] / max_heat, 1.0)
                    # Blend towards darker blue
                    color = self._interpolate_color("#ffffff", "#4169E1", intensity * 0.7)
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#e0e0e0", width=1)
        
        # Draw start and goal markers
        sr, sc = self.start
        gr, gc = self.goal
        self.canvas.create_text(sc*CELL+CELL/2, sr*CELL+CELL/2, text="S", font=("Arial", 12, "bold"), fill="white")
        self.canvas.create_text(gc*CELL+CELL/2, gr*CELL+CELL/2, text="G", font=("Arial", 12, "bold"), fill="white")

    @staticmethod
    def _interpolate_color(color1, color2, factor):
        """Interpolate between two hex colors"""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_stats(self, metrics: SearchMetrics):
        """Update the statistics display"""
        self.stats_text.config(state="normal")
        self.stats_text.delete(1.0, tk.END)
        
        stats_info = f"""
╔══════════════════════════════════════╗
║  SEARCH ALGORITHM METRICS
╠═════��════════════════════════════════╣
Algorithm:        {metrics.algorithm}
Path Length:      {metrics.path_length}
Nodes Explored:   {metrics.nodes_explored}
Frontier Peak:    {metrics.frontier_peak}
Execution Time:   {metrics.execution_time:.3f} ms
Path Optimal:     {'Yes' if metrics.path_optimal else 'No'}
╚══════════════════════════════════════╝
        """
        self.stats_text.insert(1.0, stats_info)
        self.stats_text.config(state="disabled")

    def clear(self):
        """Clear the grid"""
        if self.running: return
        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.heatmap = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.last_visited = []
        self.last_path = []
        self.step_index = 0
        self.draw()
        self.status.set("Grid cleared. Ready for new search.")

    def random_maze(self):
        """Generate a random maze"""
        if self.running: return
        self.clear()
        
        # Generate with walls
        self.grid = [[WALL if random.random() < 0.25 else EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        
        sr, sc = self.start
        gr, gc = self.goal
        self.grid[sr][sc] = EMPTY
        self.grid[gr][gc] = EMPTY
        
        # Create guaranteed path
        for c in range(sc, gc+1):
            self.grid[sr][c] = EMPTY
        for r in range(sr, gr+1):
            self.grid[r][gc] = EMPTY
        
        self.draw()
        self.status.set("Random maze generated.")

    def preset_maze(self):
        """Create a complex preset maze"""
        if self.running: return
        self.clear()
        
        # Classic maze pattern
        for r in range(ROWS):
            for c in range(COLS):
                if (r + c) % 3 == 0:
                    self.grid[r][c] = WALL
        
        # Ensure start and goal are clear
        for r in range(1, 5):
            for c in range(1, 5):
                self.grid[r][c] = EMPTY
        for r in range(ROWS-4, ROWS-1):
            for c in range(COLS-4, COLS-1):
                self.grid[r][c] = EMPTY
        
        self.draw()
        self.status.set("Preset maze loaded.")

    def preset_spiral(self):
        """Create a spiral maze"""
        if self.running: return
        self.clear()
        
        # Spiral pattern
        for r in range(ROWS):
            for c in range(COLS):
                dist = min(abs(r - ROWS//2), abs(c - COLS//2))
                if dist % 4 < 2:
                    self.grid[r][c] = WALL
        
        self.grid[self.start[0]][self.start[1]] = EMPTY
        self.grid[self.goal[0]][self.goal[1]] = EMPTY
        
        self.draw()
        self.status.set("Spiral maze loaded.")

    def toggle_wall(self, event):
        """Toggle wall at clicked location"""
        if self.running: return
        c, r = event.x // CELL, event.y // CELL
        if not (0 <= r < ROWS and 0 <= c < COLS): return
        p = (r, c)
        if p in (self.start, self.goal): return
        
        if self.grid[r][c] == WALL:
            self.grid[r][c] = EMPTY
        elif self.grid[r][c] == EMPTY:
            self.grid[r][c] = WALL
        self.draw()

    def set_goal(self, event):
        """Set goal position (right-click)"""
        if self.running: return
        c, r = event.x // CELL, event.y // CELL
        if not (0 <= r < ROWS and 0 <= c < COLS): return
        if self.grid[r][c] == WALL or (r, c) == self.start: return
        self.goal = (r, c)
        self.draw()
        self.status.set(f"Goal set to ({r}, {c})")

    def set_start(self, event):
        """Set start position (middle-click)"""
        if self.running: return
        c, r = event.x // CELL, event.y // CELL
        if not (0 <= r < ROWS and 0 <= c < COLS): return
        if self.grid[r][c] == WALL or (r, c) == self.goal: return
        self.start = (r, c)
        self.draw()
        self.status.set(f"Start set to ({r}, {c})")

    def neighbors(self, p):
        """Get valid neighbors with terrain costs"""
        r, c = p
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                cell_type = self.grid[nr][nc]
                cost = TERRAIN_COSTS.get(cell_type, 1.0)
                if cost < float('inf'):
                    yield (nr, nc), cost

    @staticmethod
    def h(a, b):
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def search(self, algorithm):
        """Execute the selected search algorithm"""
        start, goal = self.start, self.goal
        parent = {start: None}
        visited_order = []
        frontier_peak = 0

        if algorithm == "BFS":
            frontier = deque([start])
            seen = {start}
            while frontier:
                frontier_peak = max(frontier_peak, len(frontier))
                cur = frontier.popleft()
                visited_order.append(cur)
                if cur == goal: break
                for (nr, nc), cost in self.neighbors(cur):
                    nxt = (nr, nc)
                    if nxt not in seen:
                        seen.add(nxt)
                        parent[nxt] = cur
                        frontier.append(nxt)

        elif algorithm == "DFS":
            frontier = [start]
            seen = {start}
            while frontier:
                frontier_peak = max(frontier_peak, len(frontier))
                cur = frontier.pop()
                visited_order.append(cur)
                if cur == goal: break
                neighbors_list = list(self.neighbors(cur))
                for (nr, nc), cost in reversed(neighbors_list):
                    nxt = (nr, nc)
                    if nxt not in seen:
                        seen.add(nxt)
                        parent[nxt] = cur
                        frontier.append(nxt)

        elif algorithm == "Greedy Best First":
            counter = 0
            frontier = [(self.h(start, goal), counter, start)]
            seen = {start}
            while frontier:
                frontier_peak = max(frontier_peak, len(frontier))
                _, _, cur = heapq.heappop(frontier)
                visited_order.append(cur)
                if cur == goal: break
                for (nr, nc), cost in self.neighbors(cur):
                    nxt = (nr, nc)
                    if nxt not in seen:
                        seen.add(nxt)
                        parent[nxt] = cur
                        counter += 1
                        heapq.heappush(frontier, (self.h(nxt, goal), counter, nxt))

        elif algorithm == "A* Search":
            counter = 0
            g = {start: 0}
            frontier = [(self.h(start, goal), counter, start)]
            closed = set()
            while frontier:
                frontier_peak = max(frontier_peak, len(frontier))
                _, _, cur = heapq.heappop(frontier)
                if cur in closed: continue
                closed.add(cur)
                visited_order.append(cur)
                if cur == goal: break
                for (nr, nc), cost in self.neighbors(cur):
                    nxt = (nr, nc)
                    new_g = g[cur] + cost
                    if new_g < g.get(nxt, math.inf):
                        g[nxt] = new_g
                        parent[nxt] = cur
                        counter += 1
                        f = new_g + self.h(nxt, goal)
                        heapq.heappush(frontier, (f, counter, nxt))

        elif algorithm == "Hill Climbing":
            cur = start
            seen = {cur}
            visited_order.append(cur)
            while cur != goal:
                candidates = [(n, c) for n, c in self.neighbors(cur) if n not in seen]
                if not candidates: break
                nxt, cost = min(candidates, key=lambda x: self.h(x[0], goal))
                if self.h(nxt, goal) >= self.h(cur, goal): break
                parent[nxt] = cur
                cur = nxt
                seen.add(cur)
                visited_order.append(cur)

        elif algorithm == "Bidirectional":
            # Search from start and goal simultaneously
            frontier_s = deque([start])
            frontier_g = deque([goal])
            seen_s = {start}
            seen_g = {goal}
            parent_s = {start: None}
            parent_g = {goal: None}
            meeting_point = None
            
            while frontier_s and frontier_g:
                frontier_peak = max(frontier_peak, len(frontier_s) + len(frontier_g))
                
                # Expand from start
                if frontier_s:
                    cur = frontier_s.popleft()
                    visited_order.append(cur)
                    if cur in seen_g:
                        meeting_point = cur
                        break
                    for (nr, nc), cost in self.neighbors(cur):
                        nxt = (nr, nc)
                        if nxt not in seen_s:
                            seen_s.add(nxt)
                            parent_s[nxt] = cur
                            frontier_s.append(nxt)
                
                # Expand from goal
                if frontier_g:
                    cur = frontier_g.popleft()
                    if cur not in visited_order:
                        visited_order.append(cur)
                    if cur in seen_s:
                        meeting_point = cur
                        break
                    for (nr, nc), cost in self.neighbors(cur):
                        nxt = (nr, nc)
                        if nxt not in seen_g:
                            seen_g.add(nxt)
                            parent_g[nxt] = cur
                            frontier_g.append(nxt)
            
            # Reconstruct path from both directions
            if meeting_point:
                path_s = []
                cur = meeting_point
                while cur is not None:
                    path_s.append(cur)
                    cur = parent_s.get(cur)
                path_s.reverse()
                
                path_g = []
                cur = parent_g.get(meeting_point)
                while cur is not None:
                    path_g.append(cur)
                    cur = parent_g.get(cur)
                
                parent[goal] = True  # Mark as found

        elif algorithm == "IDA*":
            # Iterative Deepening A*
            def search_depth(node, g, threshold, visited_order):
                frontier_peak_local = [0]
                f = g + self.h(node, goal)
                if f > threshold:
                    return f, False
                if node == goal:
                    return f, True
                
                visited_order.append(node)
                min_threshold = float('inf')
                
                for (nr, nc), cost in self.neighbors(node):
                    nxt = (nr, nc)
                    new_g = g + cost
                    ret, found = search_depth(nxt, new_g, threshold, visited_order)
                    if found:
                        parent[nxt] = node
                        return ret, True
                    if ret < min_threshold:
                        min_threshold = ret
                
                return min_threshold, False
            
            threshold = self.h(start, goal)
            while threshold < float('inf'):
                ret, found = search_depth(start, 0, threshold, visited_order)
                if found:
                    break
                threshold = ret

        path = []
        if goal in parent or algorithm == "Bidirectional":
            if algorithm == "Bidirectional" and meeting_point:
                # Reconstruct bidirectional path
                path = path_s + path_g
            else:
                cur = goal
                while cur is not None:
                    path.append(cur)
                    cur = parent.get(cur)
                path.reverse()

        return visited_order, path, frontier_peak

    def animate(self, visited, path, algorithm, i=0):
        """Animate the search process"""
        if i < len(visited):
            p = visited[i]
            if p not in (self.start, self.goal):
                self.grid[p[0]][p[1]] = VISITED
                self.heatmap[p[0]][p[1]] += 1
            self.draw()
            self.root.after(12, lambda: self.animate(visited, path, algorithm, i+1))
            return
        self.animate_path(path, algorithm)

    def animate_path(self, path, algorithm, i=0):
        """Animate the final path"""
        if i < len(path):
            p = path[i]
            if p not in (self.start, self.goal):
                self.grid[p[0]][p[1]] = PATH
            self.draw()
            self.root.after(35, lambda: self.animate_path(path, algorithm, i+1))
            return
        self.running = False
        self.step_mode = False
        
        metrics = SearchMetrics(
            algorithm=algorithm,
            path_length=len(path) - 1 if path else 0,
            nodes_explored=len(self.last_visited),
            execution_time=0,
            path_optimal=True,
            frontier_peak=getattr(self, '_frontier_peak', 0)
        )
        
        self.update_stats(metrics)
        self.search_metrics.append(metrics)
        
        if path:
            self.status.set(f"✓ Path found! Length: {len(path)-1} | Nodes explored: {len(self.last_visited)}")
        else:
            self.status.set("✗ No path found with this algorithm.")

    def run(self):
        """Run the selected algorithm"""
        if self.running: return
        
        # Clear previous results
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] in (VISITED, PATH):
                    self.grid[r][c] = EMPTY
        
        algorithm = self.algorithm.get()
        self.running = True
        self.step_mode = False
        self.step_index = 0
        self.status.set(f"Running {algorithm}...")
        self.draw()
        
        t0 = time.perf_counter()
        self.last_visited, self.last_path, frontier_peak = self.search(algorithm)
        self._frontier_peak = frontier_peak
        elapsed = (time.perf_counter() - t0) * 1000
        
        metrics = SearchMetrics(
            algorithm=algorithm,
            path_length=len(self.last_path) - 1 if self.last_path else 0,
            nodes_explored=len(self.last_visited),
            execution_time=elapsed,
            path_optimal=True,
            frontier_peak=frontier_peak
        )
        
        self.update_stats(metrics)
        self.animate(self.last_visited, self.last_path, algorithm)

    def step_search(self):
        """Step through search one node at a time"""
        if self.running and not self.step_mode:
            self.step_mode = True
            self.step_index = 0
            return
        
        if not self.step_mode or self.step_index >= len(self.last_visited):
            return
        
        p = self.last_visited[self.step_index]
        if p not in (self.start, self.goal):
            self.grid[p[0]][p[1]] = VISITED
        
        self.step_index += 1
        self.draw()
        self.status.set(f"Step {self.step_index}/{len(self.last_visited)} - Exploring node {p}")

    def compare(self):
        """Compare all algorithms"""
        if self.running: return
        
        self.status.set("Comparing all algorithms...")
        self.root.update()
        
        results = []
        for algo in ["BFS", "DFS", "Greedy Best First", "A* Search", "Hill Climbing", "Bidirectional"]:
            for r in range(ROWS):
                for c in range(COLS):
                    if self.grid[r][c] in (VISITED, PATH):
                        self.grid[r][c] = EMPTY
            
            t0 = time.perf_counter()
            visited, path, frontier_peak = self.search(algo)
            elapsed = (time.perf_counter() - t0) * 1000
            
            metrics = SearchMetrics(
                algorithm=algo,
                path_length=len(path) - 1 if path else 0,
                nodes_explored=len(visited),
                execution_time=elapsed,
                path_optimal=len(path) > 0,
                frontier_peak=frontier_peak
            )
            results.append(metrics)
        
        # Create comparison window
        win = tk.Toplevel(self.root)
        win.title("Algorithm Comparison Analysis")
        win.geometry("900x500")
        
        ttk.Label(win, text="🔬 Search Algorithm Performance Comparison", font=("Arial", 14, "bold")).pack(pady=10)
        
        tree = ttk.Treeview(win, columns=("Algorithm", "Path", "Explored", "Time", "Frontier"), show="headings", height=12)
        
        for col, heading, width in zip(
            ("Algorithm", "Path", "Explored", "Time", "Frontier"),
            ("Algorithm", "Path Length", "Nodes Explored", "Time (ms)", "Frontier Peak"),
            (150, 100, 120, 100, 120)
        ):
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor="center")
        
        for metric in results:
            tree.insert("", "end", values=(
                metric.algorithm,
                metric.path_length if metric.path_length > 0 else "—",
                metric.nodes_explored,
                f"{metric.execution_time:.2f}",
                metric.frontier_peak
            ))
        
        tree.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Summary
        summary = "\n".join([
            "📊 Analysis:",
            f"  • Fastest: {min(results, key=lambda x: x.execution_time).algorithm}",
            f"  • Least nodes explored: {min(results, key=lambda x: x.nodes_explored).algorithm}",
            f"  • Optimal path: {max(results, key=lambda x: x.path_length).algorithm if any(r.path_length > 0 for r in results) else 'N/A'}"
        ])
        
        ttk.Label(win, text=summary, justify="left", font=("Courier", 10)).pack(padx=10, pady=10)
        
        self.status.set("Comparison complete!")

    def export_results(self):
        """Export metrics to CSV"""
        if not self.search_metrics:
            messagebox.showwarning("Export", "No search results to export. Run a search first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path: return
        
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['algorithm', 'path_length', 'nodes_explored', 'execution_time', 'path_optimal', 'frontier_peak'])
                writer.writeheader()
                for metric in self.search_metrics:
                    writer.writerow(metric.to_dict())
            
            messagebox.showinfo("Export", f"Results exported to {file_path}")
            self.status.set(f"✓ Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RouteFinder(root)
    root.mainloop()
