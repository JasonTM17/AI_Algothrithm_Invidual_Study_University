"""
Utility functions for 8-puzzle.
"""

from typing import Tuple, List, Dict, Any
import time


def format_state_matrix(state: Tuple[int, ...]) -> str:
    """Format state as 3x3 matrix string."""
    lines = []
    for i in range(3):
        row = state[i*3:(i+1)*3]
        lines.append(" ".join(str(x) for x in row))
    return "\n".join(lines)


def format_state_box(state: Tuple[int, ...]) -> str:
    """Format state as boxed 3x3 matrix."""
    lines = ["┌───┬───┬───┐"]
    for i in range(3):
        row = state[i*3:(i+1)*3]
        row_str = "│"
        for val in row:
            if val == 0:
                row_str += "   │"
            else:
                row_str += f" {val} │"
        lines.append(row_str)
        if i < 2:
            lines.append("├───┼───┼───┤")
    lines.append("└───┴───┴───┘")
    return "\n".join(lines)


def format_frontier_preview(frontier: list, max_items: int = 5) -> str:
    """Format frontier preview for trace."""
    if not frontier:
        return "[]"
    
    items = list(frontier)[:max_items]
    preview = [format_state_matrix(getattr(item, 'state', item)) for item in items]
    
    if len(frontier) > max_items:
        preview.append(f"... and {len(frontier) - max_items} more")
    
    return "\n\n".join(preview)


def format_reached_preview(reached: set, max_items: int = 5) -> str:
    """Format reached set preview for trace."""
    if not reached:
        return "{}"
    
    items = list(reached)[:max_items]
    preview = [format_state_matrix(s) for s in items]
    
    if len(reached) > max_items:
        preview.append(f"... and {len(reached) - max_items} more")
    
    return "\n\n".join(preview)


class Timer:
    """Context manager for timing code blocks."""
    
    def __init__(self):
        self.start_time = None
        self.elapsed_ms = 0.0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.start_time is None:
            return 0.0
        return (time.perf_counter() - self.start_time) * 1000


def create_trace_row(
    step: int,
    algorithm: str,
    node_state: Tuple[int, ...],
    action: str,
    depth: int,
    g: int,
    h: int,
    f: int,
    frontier: list,
    reached: set,
    note: str = ""
) -> Dict[str, Any]:
    """Create a trace row dictionary."""
    return {
        "Step": step,
        "Algorithm": algorithm,
        "Node": format_state_matrix(node_state),
        "Action": action,
        "Depth": depth,
        "g": g,
        "h": h,
        "f": f,
        "Frontier": len(frontier),
        "Reached": len(reached),
        "Note": note
    }


def get_algorithm_theory(algorithm: str) -> Dict[str, str]:
    """
    Get theory information for an algorithm.
    
    Returns dictionary with:
    - name, group, description, pseudocode, etc.
    """
    theories = {
        "BFS": {
            "name": "Breadth-First Search (BFS)",
            "group": "Uninformed Search",
            "description": "Explores all nodes at depth d before exploring nodes at depth d+1.",
            "idea": "Use a FIFO queue for frontier. Expand shallowest node first.",
            "data_structure": "Queue (FIFO)",
            "complete": "Yes, for finite state spaces",
            "optimal": "Yes, when all step costs are equal",
            "time_complexity": "O(b^d) where b=branching factor, d=depth",
            "space_complexity": "O(b^d) - must store all nodes at frontier",
            "suitable": "Yes, optimal for 8-puzzle with unit cost",
            "strengths": "Optimal, complete, finds shortest path",
            "weaknesses": "High memory usage, stores all frontier nodes",
            "when_to_use": "When memory is not a concern and optimal solution needed",
            "exam_tips": "BFS is optimal for unit cost. Remember: uses Queue (FIFO)."
        },
        "DFS": {
            "name": "Depth-First Search (DFS)",
            "group": "Uninformed Search",
            "description": "Explores deepest node first, backtracks when stuck.",
            "idea": "Use a LIFO stack for frontier. Expand deepest node first.",
            "data_structure": "Stack (LIFO)",
            "complete": "No, can get stuck in infinite paths",
            "optimal": "No, may find long paths",
            "time_complexity": "O(b^m) where m=max depth",
            "space_complexity": "O(bm) - only stores path",
            "suitable": "No, may not find solution or find very long path",
            "strengths": "Low memory usage",
            "weaknesses": "Not complete, not optimal, can go deep wrong direction",
            "when_to_use": "When memory is limited and solution depth is unknown",
            "exam_tips": "DFS is NOT optimal. Uses Stack (LIFO). Can miss solution."
        },
        "UCS": {
            "name": "Uniform Cost Search (UCS)",
            "group": "Uninformed Search",
            "description": "Expands node with lowest path cost g(n).",
            "idea": "Use priority queue ordered by g(n).",
            "data_structure": "Priority Queue (by g)",
            "complete": "Yes, for finite state spaces with positive costs",
            "optimal": "Yes, always finds optimal path",
            "time_complexity": "O(b^(C*/ε)) where C*=optimal cost",
            "space_complexity": "O(b^(C*/ε))",
            "suitable": "Yes, but same as BFS for unit cost",
            "strengths": "Optimal for any positive costs",
            "weaknesses": "High memory, same as BFS for unit cost",
            "when_to_use": "When step costs vary",
            "exam_tips": "UCS = BFS when all costs = 1. Uses Priority Queue by g."
        },
        "IDS": {
            "name": "Iterative Deepening Search (IDS)",
            "group": "Uninformed Search",
            "description": "Run DFS with increasing depth limits.",
            "idea": "DFS with limit 0, 1, 2, ... until goal found.",
            "data_structure": "Stack with depth limit",
            "complete": "Yes, for finite state spaces",
            "optimal": "Yes, for unit costs",
            "time_complexity": "O(b^d)",
            "space_complexity": "O(bd) - only stores current path",
            "suitable": "Yes, good for 8-puzzle",
            "strengths": "Optimal, complete, low memory",
            "weaknesses": "Re-expands nodes, more time than BFS",
            "when_to_use": "When memory is limited but optimal solution needed",
            "exam_tips": "IDS = BFS optimal + DFS memory. Re-expands nodes."
        },
        "Greedy": {
            "name": "Greedy Best-First Search",
            "group": "Informed Search",
            "description": "Expands node that appears closest to goal (lowest h).",
            "idea": "Use priority queue ordered by h(n).",
            "data_structure": "Priority Queue (by h)",
            "complete": "No, can get stuck in loops",
            "optimal": "No, greedy choice may not be optimal",
            "time_complexity": "O(b^m)",
            "space_complexity": "O(b^m)",
            "suitable": "Yes, but not optimal",
            "strengths": "Very fast, uses heuristic",
            "weaknesses": "Not optimal, can get stuck",
            "when_to_use": "When speed matters more than optimality",
            "exam_tips": "Greedy uses h only. NOT optimal. Can be faster than A*."
        },
        "A*": {
            "name": "A* Search",
            "group": "Informed Search",
            "description": "Expands node with lowest f(n) = g(n) + h(n).",
            "idea": "Combine path cost g and heuristic h.",
            "data_structure": "Priority Queue (by f=g+h)",
            "complete": "Yes, for finite state spaces",
            "optimal": "Yes, with admissible/consistent heuristic",
            "time_complexity": "O(b^d) - depends on heuristic",
            "space_complexity": "O(b^d)",
            "suitable": "Yes, BEST for 8-puzzle",
            "strengths": "Optimal, complete, efficient with good heuristic",
            "weaknesses": "High memory, needs good heuristic",
            "when_to_use": "When optimal solution needed with heuristic",
            "exam_tips": "A* is optimal with admissible h. f = g + h. Best for 8-puzzle."
        },
        "IDA*": {
            "name": "Iterative Deepening A*",
            "group": "Informed Search",
            "description": "A* with iterative deepening on f-cost threshold.",
            "idea": "DFS with f-limit, increase threshold each iteration.",
            "data_structure": "Stack with f-threshold",
            "complete": "Yes, for finite state spaces",
            "optimal": "Yes, with admissible heuristic",
            "time_complexity": "O(b^d)",
            "space_complexity": "O(bd)",
            "suitable": "Yes, good for 8-puzzle",
            "strengths": "Optimal, low memory like IDS",
            "weaknesses": "Re-expands nodes",
            "when_to_use": "When memory is limited but optimal needed",
            "exam_tips": "IDA* = A* optimal + IDS memory. Uses f-threshold."
        },
        "Simulated Annealing": {
            "name": "Simulated Annealing",
            "group": "Local Search",
            "description": "Hill climbing with probability of accepting worse states.",
            "idea": "Accept worse moves with probability exp(-Δ/T). Temperature decreases.",
            "data_structure": "Current state only",
            "complete": "No (theoretically yes with infinitely slow cooling, impractical)",
            "optimal": "No, but can find good solutions",
            "time_complexity": "Depends on cooling schedule",
            "space_complexity": "O(1)",
            "suitable": "No, not designed for 8-puzzle",
            "strengths": "Can escape local optima",
            "weaknesses": "Random results, not optimal, needs tuning",
            "when_to_use": "For optimization problems with many local optima",
            "exam_tips": "SA can escape local optima. P(accept) = exp(-Δ/T). Not for 8-puzzle."
        }
    }
    
    return theories.get(algorithm, {
        "name": algorithm,
        "group": "Unknown",
        "description": "Algorithm description not available."
    })


# Create __init__.py files
__all__ = [
    'format_state_matrix',
    'format_state_box',
    'format_frontier_preview',
    'format_reached_preview',
    'Timer',
    'create_trace_row',
    'get_algorithm_theory'
]
