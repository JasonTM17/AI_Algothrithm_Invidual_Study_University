"""
Node representation for search algorithms.
"""

from typing import Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class Node:
    """
    Represents a search node in the search tree.
    
    Attributes:
        state: The puzzle state (tuple of 9 integers)
        parent: Parent node (None for root)
        action: Action that led to this state
        g: Path cost from start (g(n))
        depth: Depth in search tree
        h: Heuristic value (h(n))
    """
    
    state: Tuple[int, ...]
    parent: Optional['Node'] = None
    action: str = "Start"
    g: int = 0
    depth: int = 0
    h: int = 0
    
    @property
    def f(self) -> int:
        """Total estimated cost f(n) = g(n) + h(n)."""
        return self.g + self.h
    
    def __lt__(self, other: 'Node') -> bool:
        """Comparison for priority queue (by f, then g)."""
        if self.f != other.f:
            return self.f < other.f
        return self.g < other.g
    
    def __hash__(self):
        return hash(self.state)
    
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.state == other.state
        return False
    
    def __repr__(self):
        return f"Node(state={self.state}, g={self.g}, h={self.h}, f={self.f})"
    
    def path_to_root(self) -> list:
        """Get path from this node back to root."""
        path = []
        current = self
        while current is not None:
            path.append(current)
            current = current.parent
        return list(reversed(path))
    
    def get_actions(self) -> list:
        """Get list of actions from root to this node."""
        actions = []
        current = self
        while current is not None and current.action != "Start":
            actions.append(current.action)
            current = current.parent
        return list(reversed(actions))


@dataclass
class SearchResult:
    """
    Result of a search algorithm.
    
    Attributes:
        success: Whether goal was found
        algorithm: Name of algorithm used
        group: Algorithm group (Uninformed, Informed, etc.)
        path: List of states from start to goal
        actions: List of actions
        path_cost: Total cost of path
        nodes_expanded: Number of nodes expanded
        nodes_generated: Total nodes generated
        max_frontier_size: Maximum frontier size
        reached_size: Number of states reached
        runtime_ms: Runtime in milliseconds
        trace: List of trace dictionaries
        message: Additional message
        notes: Additional notes for educational/demo algorithms
        optimal: Whether result is optimal
        complete: Whether algorithm is complete
        timeout: Whether search timed out
        max_nodes_exceeded: Whether node limit was exceeded
    """
    
    success: bool = False
    algorithm: str = ""
    group: str = ""
    path: list = None
    actions: list = None
    path_cost: Optional[int] = None
    nodes_expanded: int = 0
    nodes_generated: int = 0
    max_frontier_size: int = 0
    reached_size: int = 0
    runtime_ms: float = 0.0
    trace: list = None
    message: str = ""
    notes: str = ""
    optimal: str = "Unknown"
    complete: str = "Unknown"
    timeout: bool = False
    max_nodes_exceeded: bool = False
    
    def __post_init__(self):
        if self.path is None:
            self.path = []
        if self.actions is None:
            self.actions = []
        if self.trace is None:
            self.trace = []
    
    def to_dict(self) -> dict:
        """Convert to dictionary for display."""
        return {
            "Algorithm": self.algorithm,
            "Group": self.group,
            "Success": self.success,
            "Path Length": self.path_cost if self.path_cost is not None else "N/A",
            "Nodes Expanded": self.nodes_expanded,
            "Nodes Generated": self.nodes_generated,
            "Max Frontier": self.max_frontier_size,
            "Reached Size": self.reached_size,
            "Runtime (ms)": f"{self.runtime_ms:.2f}",
            "Optimal": self.optimal,
            "Complete": self.complete,
            "Message": self.message
        }
