# 🤖 AI Smart Route Finder

> An Artificial Intelligence based route-finding system that demonstrates and compares multiple search algorithms in a grid-based environment.

**👨‍💻 Author:** Ayush  
**🎓 Roll Number:** 2024UIN3367  
**📚 Course:** Artificial Intelligence  
**💻 Language:** Python

---

## 📌 Project Overview

AI Smart Route Finder is a grid-based route-finding application developed to demonstrate the practical application of Artificial Intelligence search algorithms.

The system represents route finding as a **State-Space Search Problem**, where:

- Each grid cell represents a state.
- The starting cell represents the initial state.
- The destination represents the goal state.
- Moving between adjacent cells represents an action.
- Obstacles represent unavailable states.

The application visually demonstrates how different AI search algorithms explore the environment and find a path from the start point to the destination.

---

## ✨ Features

- 🗺️ Interactive grid-based environment
- 🧱 Create obstacles/walls on the grid
- 🎯 Select a destination
- 🔍 Multiple AI search algorithms
- 🎨 Visual representation of explored cells
- 🛣️ Visual representation of the final route
- ⏱️ Execution-time comparison
- 📊 Nodes-explored comparison
- 📏 Path-length comparison
- 🖥️ Simple graphical user interface using Tkinter
- 📚 Designed for understanding classical AI search techniques

---

## 🧠 AI Algorithms Implemented

### 1. Breadth First Search (BFS)

BFS explores nodes level by level.

**Characteristics:**
- Uninformed search
- Uses a Queue
- Finds the shortest path when all movement costs are equal
- Systematically explores neighboring states

---

### 2. Depth First Search (DFS)

DFS explores one branch as deeply as possible before backtracking.

**Characteristics:**
- Uninformed search
- Uses a Stack
- Can use less memory in some situations
- Does not guarantee the shortest path

---

### 3. Greedy Best First Search

Greedy Best First Search selects the state that appears closest to the destination according to the heuristic.

**Characteristics:**
- Informed search
- Uses heuristic information
- Can reach the goal quickly
- Does not always produce the optimal path

---

### 4. A* Search ⭐

A* Search combines the actual cost of reaching a state with an estimated cost to the goal.

The evaluation function is:

### `f(n) = g(n) + h(n)`

Where:

- `g(n)` = cost from the starting state to the current state
- `h(n)` = estimated cost from the current state to the goal
- `f(n)` = estimated total cost of the solution through the current state

For this project, **Manhattan Distance** is used as the heuristic.

A* is the primary informed search technique demonstrated in this project.

---

### 5. Hill Climbing

Hill Climbing is a local search technique that continuously moves toward a better-looking state.

**Characteristics:**
- Local search algorithm
- Uses heuristic evaluation
- Does not maintain a complete search tree
- Can get stuck at local optima

---

## 📊 Algorithm Comparison

| Algorithm | Search Type | Main Data Structure | Uses Heuristic | Shortest Path* |
|-----------|-------------|---------------------|-----------------|----------------|
| BFS | Uninformed | Queue | ❌ | ✅ |
| DFS | Uninformed | Stack | ❌ | ❌ |
| Greedy Best First | Informed | Priority Queue | ✅ | ❌ |
| A* | Informed | Priority Queue | ✅ | ✅ |
| Hill Climbing | Local Search | — | ✅ | ❌ |

\*For the appropriate assumptions, such as equal movement cost and a suitable heuristic.

---

## 🔬 State-Space Representation

The route-finding problem can be represented as:

```text
Initial State
     ↓
  Grid Cell
     ↓
Possible Neighboring States
     ↓
Obstacle Checking
     ↓
Search Algorithm
     ↓
Goal State
     ↓
Final Path
