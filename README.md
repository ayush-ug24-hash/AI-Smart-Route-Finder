# AI Smart Route Finder

An AI-based route-finding system that demonstrates different search algorithms on a grid-based environment.

## Project Overview

This project represents route finding as a State-Space Search problem. The user can create obstacles, select a search algorithm, and visualize how the algorithm explores the environment and finds a path from the start point to the destination.

## AI Algorithms Implemented

- Breadth First Search (BFS)
- Depth First Search (DFS)
- Greedy Best First Search
- A* Search
- Hill Climbing

## Main AI Technique

The primary algorithm used in this project is A* Search.

A* uses:

**f(n) = g(n) + h(n)**

Where:

- `g(n)` = cost from the starting point to the current state
- `h(n)` = estimated cost from the current state to the goal
- `f(n)` = estimated total cost

For this project, Manhattan Distance is used as the heuristic.

## Features

- Interactive grid
- Create and remove obstacles
- Set destination
- Visualize explored states
- Visualize the final path
- Compare different AI search algorithms
- Display nodes explored and path length

## Technologies Used

- Python
- Tkinter
- Data Structures
- Artificial Intelligence Search Algorithms

## How to Run

Make sure Python 3 is installed.

Run:

```bash
python main.py
