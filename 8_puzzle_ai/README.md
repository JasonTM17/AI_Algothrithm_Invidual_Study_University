# 8-Puzzle AI Solver

Secondary package implementation of AI search algorithms for the 8-puzzle problem.

The canonical app for demos and reports is the root-level pair:

- `../eight_puzzle_search_app.py`
- `../streamlit_eight_puzzle_app.py`

This package is kept as an educational/reference implementation. Complex environment, CSP, and adversarial algorithms are simulations for explaining AI concepts; they are not natural solvers for the standard deterministic single-player 8-puzzle.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run this secondary app
streamlit run app.py
```

## 📚 Algorithm Groups

### 1. Uninformed Search
- **BFS** - Breadth-First Search (Optimal for unit cost)
- **DFS** - Depth-First Search (Not optimal)
- **UCS** - Uniform Cost Search (Same as BFS for unit cost)
- **IDS** - Iterative Deepening Search (Optimal, low memory)

### 2. Informed Search
- **Greedy** - Best-First Search (Fast, not optimal)
- **A*** - A* Search (Optimal with admissible heuristic) ⭐ BEST
- **IDA*** - Iterative Deepening A* (Optimal, low memory)

### 3. Local Search
- **Simple Hill Climbing** - First improving neighbor
- **Steepest-Ascent Hill Climbing** - Best improving neighbor
- **Stochastic Hill Climbing** - Random improving neighbor
- **Random-Restart Hill Climbing** - Multiple restarts
- **Local Beam Search** - Keep k best states
- **Simulated Annealing** - Accept worse with probability

### 4. Complex Environments
- **AND-OR Search** - For nondeterministic environments
- **No Observation** - Belief state search
- **Partially Observable** - Partial observations
- **Online Search** - LRTA* algorithm

### 5. Constraint Satisfaction
- **CSP Backtracking** - Temporal CSP planning
- **Min-Conflicts** - Conflict minimization
- **Constraint Propagation** - Domain reduction

### 6. Adversarial Search
- **Minimax** - 2-player game tree
- **Alpha-Beta Pruning** - Optimized Minimax
- **Expectimax** - Stochastic games

## 🎯 Heuristics

| Heuristic | Admissible | Consistent | Notes |
|-----------|------------|------------|-------|
| Misplaced Tiles | ✅ | ✅ | Weakest admissible |
| Manhattan Distance | ✅ | ✅ | Best trade-off ⭐ |
| Linear Conflict | ✅ | ✅ | More informed |

## 📊 Algorithm Comparison

| Algorithm | Complete | Optimal | Memory | Best For |
|-----------|----------|---------|--------|----------|
| BFS | ✅ | ✅ | High | Shortest path |
| DFS | ❌ | ❌ | Low | Deep search |
| IDS | ✅ | ✅ | Low | Memory-limited |
| A* | ✅ | ✅ | High | General use ⭐ |
| IDA* | ✅ | ✅ | Low | Memory-limited |
| Greedy | ❌ | ❌ | Medium | Fast solution |
| Hill Climbing | ❌ | ❌ | O(1) | Local opt |
| Simulated Annealing | ✅ | ❌ | O(1) | Escape local opt |

## 🎮 Features

- **Interactive Play** - Move tiles manually
- **Algorithm Visualization** - Step-by-step trace
- **Comparison Mode** - Compare multiple algorithms
- **Theory Reference** - Algorithm explanations
- **Custom Parameters** - Tune algorithm settings

## ⚠️ Important Notes

1. **8-puzzle is deterministic** - Complex environment algorithms are for education
2. **8-puzzle is single-player** - Adversarial algorithms are simulated
3. **8-puzzle is state-space search** - CSP algorithms are modeled differently

## 📖 Exam Tips

- **BFS**: Optimal for unit cost, uses Queue (FIFO)
- **DFS**: Not optimal, uses Stack (LIFO)
- **A***: Optimal with admissible h, f = g + h
- **IDA***: Like IDS but with f threshold
- **Hill Climbing**: Can get stuck at local optimum
- **Simulated Annealing**: P(accept) = exp(-Δ/T)

## 🏆 Recommended Algorithms

1. **A*** with Manhattan Distance - Best overall
2. **IDA*** - When memory is limited
3. **BFS** - When you need guaranteed optimal
4. **Greedy** - When speed matters more than optimality

---

Created for AI Education 🎓
