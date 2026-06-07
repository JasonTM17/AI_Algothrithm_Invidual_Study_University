"""
Adversarial and Stochastic Search Algorithms.

Algorithms:
1. Minimax
2. Alpha-Beta Pruning
3. Expectimax

Note: 8-puzzle is NOT a 2-player game.
These are educational implementations showing how these algorithms work.
We create a simulated 2-player version for demonstration.
"""

from typing import Tuple, Optional, List, Dict, Any
import random
import sys

sys.path.append('..')
from core.puzzle import PuzzleState
from core.node import SearchResult
from core.heuristics import get_heuristic
from core.utils import Timer


def minimax(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_depth: int = 4,
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Minimax algorithm for 2-player game.
    
    Simulated 8-puzzle game:
    - MAX: wants to minimize h (reach goal)
    - MIN: wants to maximize h (opponent)
    
    This is EDUCATIONAL - 8-puzzle is single-player.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    if seed is not None:
        random.seed(seed)
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="Minimax",
            group="Adversarial Search",
            message="Already at goal!",
            optimal="Yes, for 2-player zero-sum",
            complete="Yes",
            notes="Educational: 8-puzzle is single-player, this simulates 2-player"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    def minimax_recursive(state: Tuple[int, ...], depth: int, is_max: bool, path: List[str]) -> Tuple[int, Optional[str]]:
        """Recursive minimax with depth limit."""
        
        puzzle = PuzzleState(state)
        
        # Terminal states
        if state == goal:
            return -1000 + depth, None  # MAX wins (prefer shorter paths)
        
        if depth == 0:
            return h_func(state, goal), None  # Use heuristic as utility
        
        neighbors = puzzle.get_neighbors()
        if not neighbors:
            return 1000 if is_max else -1000, None  # No moves = loss for current player
        
        if is_max:
            # MAX wants to minimize h (maximize -h)
            best_value = float('inf')
            best_action = None
            
            for action, neighbor in neighbors:
                value, _ = minimax_recursive(neighbor.state, depth - 1, False, path + [action])
                if value < best_value:
                    best_value = value
                    best_action = action
            
            return best_value, best_action
        else:
            # MIN wants to maximize h (minimize -h)
            best_value = float('-inf')
            best_action = None
            
            for action, neighbor in neighbors:
                value, _ = minimax_recursive(neighbor.state, depth - 1, True, path + [action])
                if value > best_value:
                    best_value = value
                    best_action = action
            
            return best_value, best_action
    
    # Run minimax from start
    value, best_action = minimax_recursive(start, max_depth, True, [])
    
    # Execute best action
    if best_action:
        puzzle = PuzzleState(start)
        for action, neighbor in puzzle.get_neighbors():
            if action == best_action:
                path = [PuzzleState(start), neighbor]
                actions = [best_action]
                
                if len(trace) < trace_limit:
                    trace.append({
                        "Step": 0,
                        "Algorithm": "Minimax",
                        "Node": str(puzzle),
                        "Action": best_action,
                        "Depth": max_depth,
                        "g": 0,
                        "h": h_func(start, goal),
                        "f": value,
                        "Frontier": 0,
                        "Reached": 1,
                        "Note": f"MAX chooses {best_action} with value {value}"
                    })
                
                result = SearchResult(
                    success=neighbor.state == goal,
                    algorithm="Minimax",
                    group="Adversarial Search",
                    path=path,
                    actions=actions,
                    path_cost=1,
                    trace=trace,
                    message=f"MAX chose {best_action}, value={value}",
                    optimal="Yes, for 2-player zero-sum",
                    complete="Yes",
                    notes="Educational: 8-puzzle is single-player, this simulates 2-player"
                )
                timer.__exit__()
                result.runtime_ms = timer.elapsed_ms
                return result
    
    result = SearchResult(
        success=False,
        algorithm="Minimax",
        group="Adversarial Search",
        trace=trace,
        message="No valid action found",
        optimal="Yes, for 2-player zero-sum",
        complete="Yes",
        notes="Educational: 8-puzzle is single-player, this simulates 2-player"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def alpha_beta(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_depth: int = 6,
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Alpha-Beta Pruning.
    
    Optimized minimax with pruning.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    if seed is not None:
        random.seed(seed)
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    trace = []
    nodes_visited = [0]
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="Alpha-Beta Pruning",
            group="Adversarial Search",
            message="Already at goal!",
            optimal="Yes, for 2-player zero-sum",
            complete="Yes",
            notes="Educational: 8-puzzle is single-player"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    def alpha_beta_recursive(state: Tuple[int, ...], depth: int, alpha: float, beta: float, is_max: bool) -> Tuple[int, Optional[str]]:
        """Alpha-beta pruning."""
        
        nodes_visited[0] += 1
        puzzle = PuzzleState(state)
        
        if state == goal:
            return -1000 + depth, None
        
        if depth == 0:
            return h_func(state, goal), None
        
        neighbors = puzzle.get_neighbors()
        if not neighbors:
            return 1000 if is_max else -1000, None
        
        if is_max:
            best_value = float('inf')
            best_action = None
            
            for action, neighbor in neighbors:
                value, _ = alpha_beta_recursive(neighbor.state, depth - 1, alpha, beta, False)
                if value < best_value:
                    best_value = value
                    best_action = action
                
                beta = min(beta, value)
                if beta <= alpha:
                    # Pruning
                    if len(trace) < trace_limit:
                        trace.append({
                            "Step": len(trace),
                            "Algorithm": "Alpha-Beta",
                            "Node": "PRUNED",
                            "Action": action,
                            "Depth": depth,
                            "g": 0,
                            "h": 0,
                            "f": value,
                            "Frontier": 0,
                            "Reached": nodes_visited[0],
                            "Note": f"Pruned: alpha={alpha}, beta={beta}"
                        })
                    break
            
            return best_value, best_action
        else:
            best_value = float('-inf')
            best_action = None
            
            for action, neighbor in neighbors:
                value, _ = alpha_beta_recursive(neighbor.state, depth - 1, alpha, beta, True)
                if value > best_value:
                    best_value = value
                    best_action = action
                
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            
            return best_value, best_action
    
    value, best_action = alpha_beta_recursive(start, max_depth, float('-inf'), float('inf'), True)
    
    if best_action:
        puzzle = PuzzleState(start)
        for action, neighbor in puzzle.get_neighbors():
            if action == best_action:
                path = [PuzzleState(start), neighbor]
                actions = [best_action]
                
                result = SearchResult(
                    success=neighbor.state == goal,
                    algorithm="Alpha-Beta Pruning",
                    group="Adversarial Search",
                    path=path,
                    actions=actions,
                    path_cost=1,
                    nodes_expanded=nodes_visited[0],
                    trace=trace,
                    message=f"Best action: {best_action}, value={value}",
                    optimal="Yes, for 2-player zero-sum",
                    complete="Yes",
                    notes="Educational: 8-puzzle is single-player"
                )
                timer.__exit__()
                result.runtime_ms = timer.elapsed_ms
                return result
    
    result = SearchResult(
        success=False,
        algorithm="Alpha-Beta Pruning",
        group="Adversarial Search",
        nodes_expanded=nodes_visited[0],
        trace=trace,
        message="No valid action",
        optimal="Yes, for 2-player zero-sum",
        complete="Yes",
        notes="Educational: 8-puzzle is single-player"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def expectimax(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_depth: int = 4,
    success_prob: float = 0.8,
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Expectimax for stochastic games.
    
    Simulates 8-puzzle with probability of action success.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    if seed is not None:
        random.seed(seed)
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="Expectimax",
            group="Adversarial Search",
            message="Already at goal!",
            optimal="No, for stochastic games",
            complete="Yes",
            notes="Educational: Simulates stochastic 8-puzzle"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    def expectimax_recursive(state: Tuple[int, ...], depth: int, is_max: bool) -> Tuple[float, Optional[str]]:
        """Expectimax with chance nodes."""
        
        puzzle = PuzzleState(state)
        
        if state == goal:
            return -1000 + depth, None
        
        if depth == 0:
            return h_func(state, goal), None
        
        neighbors = puzzle.get_neighbors()
        if not neighbors:
            return 1000, None
        
        if is_max:
            # MAX node: choose action
            best_value = float('inf')
            best_action = None
            
            for action, neighbor in neighbors:
                # Chance node: expected value
                # Success with prob success_prob
                # Failure: random other outcome
                expected_value = success_prob * expectimax_recursive(neighbor.state, depth - 1, False)[0]
                
                # Add failure cases
                other_neighbors = [(a, n) for a, n in neighbors if a != action]
                if other_neighbors:
                    fail_prob = (1 - success_prob) / len(other_neighbors)
                    for _, other in other_neighbors:
                        expected_value += fail_prob * expectimax_recursive(other.state, depth - 1, False)[0]
                
                if expected_value < best_value:
                    best_value = expected_value
                    best_action = action
            
            return best_value, best_action
        else:
            # Chance node: expected value
            expected_value = 0.0
            for action, neighbor in neighbors:
                expected_value += (1.0 / len(neighbors)) * expectimax_recursive(neighbor.state, depth - 1, True)[0]
            
            return expected_value, None
    
    value, best_action = expectimax_recursive(start, max_depth, True)
    
    if best_action:
        puzzle = PuzzleState(start)
        for action, neighbor in puzzle.get_neighbors():
            if action == best_action:
                path = [PuzzleState(start), neighbor]
                actions = [best_action]
                
                if len(trace) < trace_limit:
                    trace.append({
                        "Step": 0,
                        "Algorithm": "Expectimax",
                        "Node": str(puzzle),
                        "Action": best_action,
                        "Depth": max_depth,
                        "g": 0,
                        "h": h_func(start, goal),
                        "f": value,
                        "Frontier": 0,
                        "Reached": 1,
                        "Note": f"MAX chooses {best_action}, expected value={value:.2f}"
                    })
                
                result = SearchResult(
                    success=neighbor.state == goal,
                    algorithm="Expectimax",
                    group="Adversarial Search",
                    path=path,
                    actions=actions,
                    path_cost=1,
                    trace=trace,
                    message=f"Best action: {best_action}, expected value={value:.2f}",
                    optimal="No, for stochastic games",
                    complete="Yes",
                    notes="Educational: Simulates stochastic 8-puzzle"
                )
                timer.__exit__()
                result.runtime_ms = timer.elapsed_ms
                return result
    
    result = SearchResult(
        success=False,
        algorithm="Expectimax",
        group="Adversarial Search",
        trace=trace,
        message="No valid action",
        optimal="No, for stochastic games",
        complete="Yes",
        notes="Educational: Simulates stochastic 8-puzzle"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result
