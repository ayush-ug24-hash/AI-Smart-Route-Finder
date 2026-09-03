# AI Smart Route Finder

A syllabus-oriented B.Tech Artificial Intelligence project that demonstrates state-space search and heuristic search on a grid.

## Algorithms
- Breadth First Search (BFS)
- Depth First Search (DFS)
- Greedy Best First Search
- A* Search
- Hill Climbing

## Main AI Concept
A* evaluates:
**f(n) = g(n) + h(n)**
- g(n): cost from start to current state
- h(n): Manhattan-distance estimate to goal
- f(n): estimated total cost

## How to run
1. Install Python 3.9+.
2. Save `main.py`.
3. Run:
   `python main.py`
4. Use left-click to add/remove walls.
5. Use right-click to set the destination.
6. Select an algorithm and click **Find Path**.
7. Click **Compare All** for a performance comparison.

No external packages are required; it uses Python's built-in Tkinter.

## Suggested demonstration
1. Explain the grid as a state space.
2. Add a few walls.
3. Run BFS.
4. Run A*.
5. Open Compare All.
6. Explain why the heuristic helps A* focus the search toward the goal.
