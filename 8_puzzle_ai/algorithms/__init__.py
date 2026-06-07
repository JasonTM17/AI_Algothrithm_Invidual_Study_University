"""
Algorithms package for 8-puzzle AI.
"""

from .uninformed import bfs, dfs, ucs, ids
from .informed import greedy, astar, idastar
from .local_search import (
    simple_hill_climbing,
    steepest_ascent_hill_climbing,
    stochastic_hill_climbing,
    random_restart_hill_climbing,
    local_beam_search,
    simulated_annealing
)
from .complex_env import (
    and_or_search,
    no_observation_search,
    partially_observable_search,
    online_search
)
from .csp import (
    csp_backtracking,
    min_conflicts,
    constraint_propagation_demo
)
from .adversarial import minimax, alpha_beta, expectimax

# Algorithm registry
ALGORITHMS = {
    # Uninformed
    "BFS": {"function": bfs, "group": "Uninformed Search"},
    "DFS": {"function": dfs, "group": "Uninformed Search"},
    "UCS": {"function": ucs, "group": "Uninformed Search"},
    "IDS": {"function": ids, "group": "Uninformed Search"},
    
    # Informed
    "Greedy": {"function": greedy, "group": "Informed Search"},
    "A*": {"function": astar, "group": "Informed Search"},
    "IDA*": {"function": idastar, "group": "Informed Search"},
    
    # Local Search
    "Simple Hill Climbing": {"function": simple_hill_climbing, "group": "Local Search"},
    "Steepest-Ascent Hill Climbing": {"function": steepest_ascent_hill_climbing, "group": "Local Search"},
    "Stochastic Hill Climbing": {"function": stochastic_hill_climbing, "group": "Local Search"},
    "Random-Restart Hill Climbing": {"function": random_restart_hill_climbing, "group": "Local Search"},
    "Local Beam Search": {"function": local_beam_search, "group": "Local Search"},
    "Simulated Annealing": {"function": simulated_annealing, "group": "Local Search"},
    
    # Complex Environments
    "AND-OR Search": {"function": and_or_search, "group": "Complex Environments"},
    "No Observation": {"function": no_observation_search, "group": "Complex Environments"},
    "Partially Observable": {"function": partially_observable_search, "group": "Complex Environments"},
    "Online Search": {"function": online_search, "group": "Complex Environments"},
    
    # CSP
    "CSP Backtracking": {"function": csp_backtracking, "group": "Constraint Satisfaction"},
    "Min-Conflicts": {"function": min_conflicts, "group": "Constraint Satisfaction"},
    "Constraint Propagation": {"function": constraint_propagation_demo, "group": "Constraint Satisfaction"},
    
    # Adversarial
    "Minimax": {"function": minimax, "group": "Adversarial Search"},
    "Alpha-Beta Pruning": {"function": alpha_beta, "group": "Adversarial Search"},
    "Expectimax": {"function": expectimax, "group": "Adversarial Search"},
}

def get_algorithm(name: str):
    """Get algorithm function by name."""
    if name in ALGORITHMS:
        return ALGORITHMS[name]["function"]
    raise ValueError(f"Unknown algorithm: {name}. Options: {list(ALGORITHMS.keys())}")

def get_algorithm_group(name: str) -> str:
    """Get algorithm group by name."""
    if name in ALGORITHMS:
        return ALGORITHMS[name]["group"]
    return "Unknown"

def list_algorithms() -> dict:
    """List all algorithms grouped."""
    groups = {}
    for name, info in ALGORITHMS.items():
        group = info["group"]
        if group not in groups:
            groups[group] = []
        groups[group].append(name)
    return groups

__all__ = [
    'bfs', 'dfs', 'ucs', 'ids',
    'greedy', 'astar', 'idastar',
    'simple_hill_climbing', 'steepest_ascent_hill_climbing',
    'stochastic_hill_climbing', 'random_restart_hill_climbing',
    'local_beam_search', 'simulated_annealing',
    'and_or_search', 'no_observation_search',
    'partially_observable_search', 'online_search',
    'csp_backtracking', 'min_conflicts', 'constraint_propagation_demo',
    'minimax', 'alpha_beta', 'expectimax',
    'ALGORITHMS', 'get_algorithm', 'get_algorithm_group', 'list_algorithms'
]
