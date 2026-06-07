"""
8-Puzzle Core Module
Contains PuzzleState class and core puzzle operations.
"""

from typing import Tuple, List, Optional, Set
import random
import copy


class PuzzleState:
    """
    Represents an 8-puzzle state.
    
    State is stored as a tuple of 9 integers (0-8).
    0 represents the blank tile.
    """
    
    GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    BOARD_SIZE = 3
    
    def __init__(self, state: Tuple[int, ...]):
        """Initialize puzzle state."""
        if len(state) != 9:
            raise ValueError("State must have exactly 9 elements")
        if not self._is_valid_state(state):
            raise ValueError("Invalid state: must contain all numbers 0-8 exactly once")
        
        self.state = state
        self._blank_index = None
    
    @property
    def blank_index(self) -> int:
        """Get index of blank tile (lazy evaluation)."""
        if self._blank_index is None:
            self._blank_index = self.state.index(0)
        return self._blank_index
    
    @property
    def blank_pos(self) -> Tuple[int, int]:
        """Get (row, col) position of blank tile."""
        idx = self.blank_index
        return (idx // 3, idx % 3)
    
    def _is_valid_state(self, state: Tuple[int, ...]) -> bool:
        """Check if state contains all numbers 0-8 exactly once."""
        return sorted(state) == list(range(9))
    
    def is_goal(self) -> bool:
        """Check if current state is goal state."""
        return self.state == self.GOAL_STATE
    
    def get_neighbors(self, action_order: str = "LRUD") -> List[Tuple[str, 'PuzzleState']]:
        """
        Get all valid neighbor states.
        
        Returns list of (action, new_state) tuples.
        Action order determines priority when iterating.
        """
        neighbors = []
        row, col = self.blank_pos
        
        # Define actions: (name, row_delta, col_delta)
        actions = {
            'L': (0, -1),  # Move blank left
            'R': (0, 1),   # Move blank right
            'U': (-1, 0),  # Move blank up
            'D': (1, 0)    # Move blank down
        }
        
        for action in action_order:
            if action not in actions:
                continue
            
            dr, dc = actions[action]
            new_row, new_col = row + dr, col + dc
            
            # Check bounds
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_state = self._swap(row, col, new_row, new_col)
                neighbors.append((action, PuzzleState(new_state)))
        
        return neighbors
    
    def _swap(self, r1: int, c1: int, r2: int, c2: int) -> Tuple[int, ...]:
        """Swap two positions and return new state."""
        state_list = list(self.state)
        idx1 = r1 * 3 + c1
        idx2 = r2 * 3 + c2
        state_list[idx1], state_list[idx2] = state_list[idx2], state_list[idx1]
        return tuple(state_list)
    
    def apply_action(self, action: str) -> Optional['PuzzleState']:
        """Apply single action and return new state, or None if invalid."""
        neighbors = self.get_neighbors(action_order=action)
        for a, state in neighbors:
            if a == action:
                return state
        return None
    
    def inversion_count(self) -> int:
        """
        Count inversions (pairs where larger number appears before smaller).
        Used to check solvability.
        """
        inversions = 0
        state_no_zero = [x for x in self.state if x != 0]
        
        for i in range(len(state_no_zero)):
            for j in range(i + 1, len(state_no_zero)):
                if state_no_zero[i] > state_no_zero[j]:
                    inversions += 1
        
        return inversions
    
    def is_solvable(self) -> bool:
        """
        Check if puzzle is solvable.
        For 8-puzzle (3x3), solvable if inversions is even.
        """
        return self.inversion_count() % 2 == 0
    
    def pretty_print(self) -> str:
        """Return formatted string representation of the puzzle."""
        lines = []
        lines.append("┌───┬───┬───┐")
        
        for i in range(3):
            row = self.state[i*3:(i+1)*3]
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
    
    def to_matrix_string(self) -> str:
        """Return simple matrix string for display."""
        lines = []
        for i in range(3):
            row = self.state[i*3:(i+1)*3]
            lines.append(" ".join(str(x) for x in row))
        return "\n".join(lines)
    
    def __hash__(self):
        return hash(self.state)
    
    def __eq__(self, other):
        if isinstance(other, PuzzleState):
            return self.state == other.state
        return False
    
    def __repr__(self):
        return f"PuzzleState({self.state})"
    
    def __str__(self):
        return self.to_matrix_string()


def validate_state(state: Tuple[int, ...]) -> Tuple[bool, str]:
    """
    Validate a puzzle state.
    
    Returns (is_valid, message).
    """
    if len(state) != 9:
        return False, f"State must have 9 elements, got {len(state)}"
    
    if set(state) != set(range(9)):
        return False, "State must contain all numbers 0-8 exactly once"
    
    return True, "Valid state"


def parse_state(state_str: str) -> Tuple[int, ...]:
    """
    Parse state from string.
    
    Accepts formats:
    - "1 2 3 4 5 6 7 8 0"
    - "1,2,3,4,5,6,7,8,0"
    - "123456780"
    """
    state_str = state_str.strip()
    
    # Try comma-separated
    if ',' in state_str:
        parts = state_str.split(',')
    # Try space-separated
    elif ' ' in state_str:
        parts = state_str.split()
    # Try single string
    else:
        parts = list(state_str)
    
    try:
        state = tuple(int(p.strip()) for p in parts)
        return state
    except ValueError:
        raise ValueError(f"Cannot parse state: {state_str}")


def scramble_state(num_moves: int = 20, seed: Optional[int] = None) -> PuzzleState:
    """
    Generate random solvable state by scrambling from goal.
    
    Args:
        num_moves: Number of random moves to make
        seed: Random seed for reproducibility
    
    Returns:
        PuzzleState: Random solvable state
    """
    if seed is not None:
        random.seed(seed)
    
    state = PuzzleState(PuzzleState.GOAL_STATE)
    visited = {state.state}
    
    for _ in range(num_moves):
        neighbors = state.get_neighbors()
        if not neighbors:
            break
        
        # Prefer unvisited states
        unvisited = [(a, s) for a, s in neighbors if s.state not in visited]
        if unvisited:
            action, new_state = random.choice(unvisited)
        else:
            action, new_state = random.choice(neighbors)
        
        state = new_state
        visited.add(state.state)
    
    return state


def reconstruct_path(node: 'Node') -> Tuple[List[PuzzleState], List[str]]:
    """
    Reconstruct path from goal node to start.
    
    Returns (path_states, actions).
    """
    path = []
    actions = []
    current = node
    
    while current is not None:
        path.append(PuzzleState(current.state))
        if current.action != "Start":
            actions.append(current.action)
        current = current.parent
    
    path.reverse()
    actions.reverse()
    return path, actions


def validate_path(start: PuzzleState, actions: List[str], goal: PuzzleState) -> Tuple[bool, str]:
    """
    Validate that a sequence of actions leads from start to goal.
    
    Returns (is_valid, message).
    """
    current = start
    
    for i, action in enumerate(actions):
        next_state = current.apply_action(action)
        if next_state is None:
            return False, f"Invalid action '{action}' at step {i}"
        current = next_state
    
    if current.state != goal.state:
        return False, f"Path does not reach goal. Final state: {current.state}"
    
    return True, "Valid path"
