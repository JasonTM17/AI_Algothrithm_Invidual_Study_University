"""
Heuristic functions for 8-puzzle.
"""

from typing import Tuple, Dict
import math


def misplaced_tiles(state: Tuple[int, ...], goal: Tuple[int, ...] = None) -> int:
    """
    Count number of misplaced tiles (excluding blank).
    
    This heuristic is:
    - Admissible: Never overestimates
    - Consistent: h(n) <= cost(n,n') + h(n')
    
    Args:
        state: Current puzzle state
        goal: Goal state (default: standard goal)
    
    Returns:
        Number of misplaced tiles
    """
    if goal is None:
        goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    
    count = 0
    for i in range(9):
        if state[i] != 0 and state[i] != goal[i]:
            count += 1
    return count


def manhattan_distance(state: Tuple[int, ...], goal: Tuple[int, ...] = None) -> int:
    """
    Sum of Manhattan distances of each tile from its goal position.
    
    This heuristic is:
    - Admissible: Never overestimates
    - Consistent: h(n) <= cost(n,n') + h(n')
    
    Manhattan distance is better than misplaced tiles because:
    - More informed (higher values)
    - Still admissible
    - Better pruning in A*
    
    Args:
        state: Current puzzle state
        goal: Goal state (default: standard goal)
    
    Returns:
        Sum of Manhattan distances
    """
    if goal is None:
        goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    
    # Build goal position map: tile -> (row, col)
    goal_pos = {}
    for i, tile in enumerate(goal):
        goal_pos[tile] = (i // 3, i % 3)
    
    distance = 0
    for i, tile in enumerate(state):
        if tile != 0:  # Skip blank
            current_row, current_col = i // 3, i % 3
            goal_row, goal_col = goal_pos[tile]
            distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    
    return distance


def linear_conflict(state: Tuple[int, ...], goal: Tuple[int, ...] = None) -> int:
    """
    Manhattan distance + 2 * linear conflicts.
    
    A linear conflict occurs when two tiles are in their goal row/column
    but in wrong order relative to each other.
    
    This heuristic is:
    - Admissible: Never overestimates
    - More informed than Manhattan distance
    
    Note: Counting all pairwise conflicts could theoretically overcount 
    in rare edge cases (e.g. 3+ tiles in conflict). A strictly optimal
    implementation would use the maximum independent set of conflicts.
    
    Args:
        state: Current puzzle state
        goal: Goal state (default: standard goal)
    
    Returns:
        Manhattan distance + 2 * linear conflicts
    """
    if goal is None:
        goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    
    # Start with Manhattan distance
    h = manhattan_distance(state, goal)
    
    # Build goal position map
    goal_pos = {}
    for i, tile in enumerate(goal):
        goal_pos[tile] = (i // 3, i % 3)
    
    # Count linear conflicts in rows
    for row in range(3):
        tiles_in_row = []
        for col in range(3):
            idx = row * 3 + col
            tile = state[idx]
            if tile != 0:
                goal_row, goal_col = goal_pos[tile]
                if goal_row == row:  # Tile belongs in this row
                    tiles_in_row.append((col, goal_col, tile))
        
        # Check for conflicts
        conflicts = {i: [] for i in range(len(tiles_in_row))}
        for i in range(len(tiles_in_row)):
            for j in range(i + 1, len(tiles_in_row)):
                curr_col_i, goal_col_i, _ = tiles_in_row[i]
                curr_col_j, goal_col_j, _ = tiles_in_row[j]
                
                # Conflict: tile i is to the left of tile j,
                # but tile i's goal is to the right of tile j's goal
                if curr_col_i < curr_col_j and goal_col_i > goal_col_j:
                    conflicts[i].append(j)
                    conflicts[j].append(i)
                    
        # Resolve conflicts by removing the tile with max conflicts
        while True:
            max_conflicts = 0
            max_tile = -1
            for k, v in conflicts.items():
                if len(v) > max_conflicts:
                    max_conflicts = len(v)
                    max_tile = k
            
            if max_conflicts == 0:
                break
                
            for neighbor in conflicts[max_tile]:
                conflicts[neighbor].remove(max_tile)
            conflicts[max_tile] = []
            h += 2
    
    # Count linear conflicts in columns
    for col in range(3):
        tiles_in_col = []
        for row in range(3):
            idx = row * 3 + col
            tile = state[idx]
            if tile != 0:
                goal_row, goal_col = goal_pos[tile]
                if goal_col == col:  # Tile belongs in this column
                    tiles_in_col.append((row, goal_row, tile))
        
        # Check for conflicts
        conflicts = {i: [] for i in range(len(tiles_in_col))}
        for i in range(len(tiles_in_col)):
            for j in range(i + 1, len(tiles_in_col)):
                curr_row_i, goal_row_i, _ = tiles_in_col[i]
                curr_row_j, goal_row_j, _ = tiles_in_col[j]
                
                if curr_row_i < curr_row_j and goal_row_i > goal_row_j:
                    conflicts[i].append(j)
                    conflicts[j].append(i)
                    
        # Resolve conflicts by removing the tile with max conflicts
        while True:
            max_conflicts = 0
            max_tile = -1
            for k, v in conflicts.items():
                if len(v) > max_conflicts:
                    max_conflicts = len(v)
                    max_tile = k
            
            if max_conflicts == 0:
                break
                
            for neighbor in conflicts[max_tile]:
                conflicts[neighbor].remove(max_tile)
            conflicts[max_tile] = []
            h += 2
    
    return h


def euclidean_distance(state: Tuple[int, ...], goal: Tuple[int, ...] = None) -> float:
    """
    Sum of Euclidean distances.
    
    This heuristic is:
    - Admissible: Never overestimates (straight line is shortest)
    - Consistent: h(n) <= cost(n,n') + h(n')
    
    Note: While admissible, it is less informed than Manhattan distance 
    because diagonal movement is not allowed in the 8-puzzle.
    
    Args:
        state: Current puzzle state
        goal: Goal state (default: standard goal)
    
    Returns:
        Sum of Euclidean distances
    """
    if goal is None:
        goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    
    goal_pos = {}
    for i, tile in enumerate(goal):
        goal_pos[tile] = (i // 3, i % 3)
    
    distance = 0.0
    for i, tile in enumerate(state):
        if tile != 0:
            current_row, current_col = i // 3, i % 3
            goal_row, goal_col = goal_pos[tile]
            distance += math.sqrt((current_row - goal_row)**2 + (current_col - goal_col)**2)
    
    return distance


# Heuristic registry
HEURISTICS: Dict[str, callable] = {
    "misplaced": misplaced_tiles,
    "manhattan": manhattan_distance,
    "linear_conflict": linear_conflict,
    "euclidean": euclidean_distance
}


def get_heuristic(name: str):
    """Get heuristic function by name."""
    name_lower = name.lower().replace("-", "_").replace(" ", "_")
    
    # Handle various names
    if name_lower in ["misplaced", "misplaced_tiles", "misplaced tiles"]:
        return misplaced_tiles
    elif name_lower in ["manhattan", "manhattan_distance", "manhattan distance"]:
        return manhattan_distance
    elif name_lower in ["linear_conflict", "linear conflict", "linear"]:
        return linear_conflict
    elif name_lower in ["euclidean", "euclidean_distance", "euclidean distance"]:
        return euclidean_distance
    else:
        raise ValueError(f"Unknown heuristic: {name}. Options: {list(HEURISTICS.keys())}")


def heuristic_info() -> Dict[str, dict]:
    """
    Return information about each heuristic.
    
    Returns:
        Dictionary with heuristic details
    """
    return {
        "Misplaced Tiles": {
            "description": "Count of tiles not in goal position",
            "admissible": True,
            "consistent": True,
            "complexity": "O(1)",
            "notes": "Weakest admissible heuristic for 8-puzzle"
        },
        "Manhattan Distance": {
            "description": "Sum of horizontal + vertical distances to goal",
            "admissible": True,
            "consistent": True,
            "complexity": "O(1)",
            "notes": "Best trade-off between accuracy and computation. Recommended for A*."
        },
        "Linear Conflict": {
            "description": "Manhattan + 2 * linear conflicts",
            "admissible": True,
            "consistent": True,
            "complexity": "O(n)",
            "notes": "More informed than Manhattan but slower to compute"
        },
        "Euclidean Distance": {
            "description": "Sum of straight-line distances",
            "admissible": True,
            "consistent": True,
            "complexity": "O(1)",
            "notes": "Admissible but less informed than Manhattan distance."
        }
    }
