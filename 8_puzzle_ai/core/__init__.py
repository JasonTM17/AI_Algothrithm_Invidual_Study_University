"""
Core package for 8-puzzle AI.
"""

from .puzzle import PuzzleState, validate_state, parse_state, scramble_state, reconstruct_path, validate_path
from .node import Node, SearchResult
from .heuristics import (
    misplaced_tiles, 
    manhattan_distance, 
    linear_conflict,
    euclidean_distance,
    get_heuristic,
    heuristic_info
)
from .metrics import SearchMetrics, compare_results, generate_comparison_report, get_algorithm_properties
from .utils import (
    format_state_matrix,
    format_state_box,
    Timer,
    create_trace_row,
    get_algorithm_theory
)

__all__ = [
    # Puzzle
    'PuzzleState',
    'validate_state',
    'parse_state',
    'scramble_state',
    'reconstruct_path',
    'validate_path',
    # Node
    'Node',
    'SearchResult',
    # Heuristics
    'misplaced_tiles',
    'manhattan_distance',
    'linear_conflict',
    'euclidean_distance',
    'get_heuristic',
    'heuristic_info',
    # Metrics
    'SearchMetrics',
    'compare_results',
    'generate_comparison_report',
    'get_algorithm_properties',
    # Utils
    'format_state_matrix',
    'format_state_box',
    'Timer',
    'create_trace_row',
    'get_algorithm_theory'
]
