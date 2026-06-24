"""
Main entry point for 8-puzzle AI.
"""

__version__ = "1.0.0"
__author__ = "AI Education"

try:
    from .core import (
        PuzzleState,
        Node,
        SearchResult,
        misplaced_tiles,
        manhattan_distance,
        linear_conflict,
        get_heuristic,
        heuristic_info,
        Timer,
        format_state_matrix,
        format_state_box
    )

    from .algorithms import (
        bfs,
        dfs,
        ucs,
        ids,
        greedy,
        astar,
        idastar,
        simple_hill_climbing,
        steepest_ascent_hill_climbing,
        stochastic_hill_climbing,
        random_restart_hill_climbing,
        local_beam_search,
        simulated_annealing,
        and_or_search,
        no_observation_search,
        partially_observable_search,
        online_search,
        csp_backtracking,
        min_conflicts,
        constraint_propagation_demo,
        minimax,
        alpha_beta,
        expectimax,
        ALGORITHMS,
        get_algorithm,
        list_algorithms
    )
except ImportError:
    import os
    import sys

    PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, PACKAGE_DIR)

    from core import (
        PuzzleState,
        Node,
        SearchResult,
        misplaced_tiles,
        manhattan_distance,
        linear_conflict,
        get_heuristic,
        heuristic_info,
        Timer,
        format_state_matrix,
        format_state_box
    )

    from algorithms import (
        bfs,
        dfs,
        ucs,
        ids,
        greedy,
        astar,
        idastar,
        simple_hill_climbing,
        steepest_ascent_hill_climbing,
        stochastic_hill_climbing,
        random_restart_hill_climbing,
        local_beam_search,
        simulated_annealing,
        and_or_search,
        no_observation_search,
        partially_observable_search,
        online_search,
        csp_backtracking,
        min_conflicts,
        constraint_propagation_demo,
        minimax,
        alpha_beta,
        expectimax,
        ALGORITHMS,
        get_algorithm,
        list_algorithms
    )

__all__ = [
    # Core
    'PuzzleState',
    'Node',
    'SearchResult',
    'misplaced_tiles',
    'manhattan_distance',
    'linear_conflict',
    'get_heuristic',
    'heuristic_info',
    'Timer',
    'format_state_matrix',
    'format_state_box',
    
    # Algorithms
    'bfs',
    'dfs',
    'ucs',
    'ids',
    'greedy',
    'astar',
    'idastar',
    'simple_hill_climbing',
    'steepest_ascent_hill_climbing',
    'stochastic_hill_climbing',
    'random_restart_hill_climbing',
    'local_beam_search',
    'simulated_annealing',
    'and_or_search',
    'no_observation_search',
    'partially_observable_search',
    'online_search',
    'csp_backtracking',
    'min_conflicts',
    'constraint_propagation_demo',
    'minimax',
    'alpha_beta',
    'expectimax',
    'ALGORITHMS',
    'get_algorithm',
    'list_algorithms'
]
