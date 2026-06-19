"""
Local Search Algorithms for 8-Puzzle.

Algorithms:
1. Simple Hill Climbing
2. Steepest-Ascent Hill Climbing
3. Stochastic Hill Climbing
4. Random-Restart Hill Climbing
5. Local Beam Search
6. Simulated Annealing
"""

from typing import Tuple, Optional, List, Dict, Any, Set
import random
import math
import sys

sys.path.append('..')
from core.puzzle import PuzzleState, reconstruct_path, scramble_state
from core.node import Node, SearchResult
from core.heuristics import get_heuristic
from core.metrics import SearchMetrics
from core.utils import Timer, create_trace_row


def simple_hill_climbing(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_steps: int = 500,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Simple Hill Climbing.
    
    Takes first neighbor that improves h.
    Can get stuck at local optimum.
    
    Args:
        start: Starting state
        goal: Goal state
        heuristic: Heuristic function
        max_steps: Maximum steps
        max_time_ms: Maximum runtime
        action_order: Action order
        trace_limit: Trace limit
        seed: Random seed
    
    Returns:
        SearchResult
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    if seed is not None:
        random.seed(seed)
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    metrics = SearchMetrics()
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="Simple Hill Climbing",
            group="Local Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            message="Already at goal!",
            optimal="No",
            complete="No"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    current = start
    current_h = h_func(current, goal)
    
    path = [PuzzleState(current)]
    actions = []
    
    for step in range(max_steps):
        if timer.elapsed > max_time_ms:
            break
        
        current_state = PuzzleState(current)
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "Simple Hill Climbing",
                "Node": str(current_state),
                "Action": actions[-1] if actions else "Start",
                "Depth": step,
                "g": step,
                "h": current_h,
                "f": current_h,
                "Frontier": 0,
                "Reached": step + 1,
                "Note": f"h={current_h}"
            })
        
        if current == goal:
            result = SearchResult(
                success=True,
                algorithm="Simple Hill Climbing",
                group="Local Search",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                nodes_generated=step * 4,
                trace=trace,
                message=f"Goal found after {step} steps",
                optimal="No",
                complete="No"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Get neighbors in action order
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_expanded()
        metrics.increment_generated(len(neighbors))
        
        # Take first improving neighbor
        moved = False
        for action, neighbor_state in neighbors:
            neighbor_h = h_func(neighbor_state.state, goal)
            
            if neighbor_h < current_h:
                current = neighbor_state.state
                current_h = neighbor_h
                actions.append(action)
                path.append(neighbor_state)
                moved = True
                break
        
        if not moved:
            # Stuck at local optimum
            result = SearchResult(
                success=False,
                algorithm="Simple Hill Climbing",
                group="Local Search",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                nodes_generated=step * 4,
                trace=trace,
                message=f"Stuck at local optimum (h={current_h}) after {step} steps",
                optimal="No",
                complete="No"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
    
    result = SearchResult(
        success=False,
        algorithm="Simple Hill Climbing",
        group="Local Search",
        path=path,
        actions=actions,
        path_cost=len(actions),
        nodes_expanded=max_steps,
        nodes_generated=max_steps * 4,
        trace=trace,
        message=f"Max steps ({max_steps}) reached",
        optimal="No",
        complete="No"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def steepest_ascent_hill_climbing(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_steps: int = 500,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100
) -> SearchResult:
    """
    Steepest-Ascent Hill Climbing.
    
    Examines ALL neighbors, chooses best.
    Better than simple but still can get stuck.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    metrics = SearchMetrics()
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="Steepest-Ascent Hill Climbing",
            group="Local Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            message="Already at goal!",
            optimal="No",
            complete="No"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    current = start
    current_h = h_func(current, goal)
    
    path = [PuzzleState(current)]
    actions = []
    
    for step in range(max_steps):
        if timer.elapsed > max_time_ms:
            break
        
        current_state = PuzzleState(current)
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "Steepest-Ascent HC",
                "Node": str(current_state),
                "Action": actions[-1] if actions else "Start",
                "Depth": step,
                "g": step,
                "h": current_h,
                "f": current_h,
                "Frontier": 0,
                "Reached": step + 1,
                "Note": f"h={current_h}"
            })
        
        if current == goal:
            result = SearchResult(
                success=True,
                algorithm="Steepest-Ascent Hill Climbing",
                group="Local Search",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                nodes_generated=step * 4,
                trace=trace,
                message=f"Goal found after {step} steps",
                optimal="No",
                complete="No"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_expanded()
        metrics.increment_generated(len(neighbors))
        
        # Find best neighbor
        best_neighbor = None
        best_h = current_h
        best_action = None
        
        for action, neighbor_state in neighbors:
            neighbor_h = h_func(neighbor_state.state, goal)
            if neighbor_h < best_h:
                best_h = neighbor_h
                best_neighbor = neighbor_state.state
                best_action = action
        
        if best_neighbor is None:
            result = SearchResult(
                success=False,
                algorithm="Steepest-Ascent Hill Climbing",
                group="Local Search",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                nodes_generated=step * 4,
                trace=trace,
                message=f"Stuck at local optimum (h={current_h})",
                optimal="No",
                complete="No"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        current = best_neighbor
        current_h = best_h
        actions.append(best_action)
        path.append(PuzzleState(current))
    
    result = SearchResult(
        success=False,
        algorithm="Steepest-Ascent Hill Climbing",
        group="Local Search",
        path=path,
        actions=actions,
        path_cost=len(actions),
        nodes_expanded=max_steps,
        nodes_generated=max_steps * 4,
        trace=trace,
        message=f"Max steps ({max_steps}) reached",
        optimal="No",
        complete="No"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def stochastic_hill_climbing(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_steps: int = 500,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Stochastic Hill Climbing.
    
    Randomly selects from improving neighbors.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    if seed is not None:
        random.seed(seed)
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    metrics = SearchMetrics()
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="Stochastic Hill Climbing",
            group="Local Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            message="Already at goal!",
            optimal="No",
            complete="No"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    current = start
    current_h = h_func(current, goal)
    
    path = [PuzzleState(current)]
    actions = []
    
    for step in range(max_steps):
        if timer.elapsed > max_time_ms:
            break
        
        current_state = PuzzleState(current)
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "Stochastic HC",
                "Node": str(current_state),
                "Action": actions[-1] if actions else "Start",
                "Depth": step,
                "g": step,
                "h": current_h,
                "f": current_h,
                "Frontier": 0,
                "Reached": step + 1,
                "Note": f"h={current_h}"
            })
        
        if current == goal:
            result = SearchResult(
                success=True,
                algorithm="Stochastic Hill Climbing",
                group="Local Search",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                nodes_generated=step * 4,
                trace=trace,
                message=f"Goal found after {step} steps",
                optimal="No",
                complete="No"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_expanded()
        metrics.increment_generated(len(neighbors))
        
        # Find all improving neighbors
        improving = []
        for action, neighbor_state in neighbors:
            neighbor_h = h_func(neighbor_state.state, goal)
            if neighbor_h < current_h:
                improving.append((action, neighbor_state.state, neighbor_h))
        
        if not improving:
            result = SearchResult(
                success=False,
                algorithm="Stochastic Hill Climbing",
                group="Local Search",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                nodes_generated=step * 4,
                trace=trace,
                message=f"Stuck at local optimum (h={current_h})",
                optimal="No",
                complete="No"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Randomly select from improving
        action, new_state, new_h = random.choice(improving)
        current = new_state
        current_h = new_h
        actions.append(action)
        path.append(PuzzleState(current))
    
    result = SearchResult(
        success=False,
        algorithm="Stochastic Hill Climbing",
        group="Local Search",
        path=path,
        actions=actions,
        path_cost=len(actions),
        nodes_expanded=max_steps,
        nodes_generated=max_steps * 4,
        trace=trace,
        message=f"Max steps ({max_steps}) reached",
        optimal="No",
        complete="No"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def random_restart_hill_climbing(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_restarts: int = 50,
    max_steps_per_restart: int = 200,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Random-Restart Hill Climbing.
    
    Runs hill climbing multiple times from different starts.
    Complete with enough restarts.
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
            algorithm="Random-Restart Hill Climbing",
            group="Local Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            message="Already at goal!",
            optimal="No",
            complete="Yes, with enough restarts"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    best_path = None
    best_actions = None
    best_h = float('inf')
    
    total_expanded = 0
    total_generated = 0
    
    for restart in range(max_restarts):
        if timer.elapsed > max_time_ms:
            break
        
        # Choose starting state
        if restart == 0:
            current = start
        else:
            # Generate random solvable state
            random_state = scramble_state(num_moves=20, seed=seed + restart if seed else None)
            current = random_state.state
        
        current_h = h_func(current, goal)
        path = [PuzzleState(current)]
        actions = []
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": len(trace),
                "Algorithm": "Random-Restart HC",
                "Node": f"Restart {restart}",
                "Action": "-",
                "Depth": 0,
                "g": 0,
                "h": current_h,
                "f": current_h,
                "Frontier": 0,
                "Reached": restart + 1,
                "Note": f"Starting restart {restart}, h={current_h}"
            })
        
        for step in range(max_steps_per_restart):
            if current == goal:
                result = SearchResult(
                    success=True,
                    algorithm="Random-Restart Hill Climbing",
                    group="Local Search",
                    path=path,
                    actions=actions,
                    path_cost=len(actions),
                    nodes_expanded=total_expanded + step,
                    nodes_generated=total_generated + step * 4,
                    trace=trace,
                    message=f"Goal found after restart {restart}",
                    optimal="No",
                    complete="Yes, with enough restarts"
                )
                timer.__exit__()
                result.runtime_ms = timer.elapsed_ms
                return result
            
            current_state = PuzzleState(current)
            neighbors = current_state.get_neighbors(action_order)
            total_expanded += 1
            total_generated += len(neighbors)
            
            best_neighbor = None
            best_neighbor_h = current_h
            best_action = None
            
            for action, neighbor_state in neighbors:
                neighbor_h = h_func(neighbor_state.state, goal)
                if neighbor_h < best_neighbor_h:
                    best_neighbor_h = neighbor_h
                    best_neighbor = neighbor_state.state
                    best_action = action
            
            if best_neighbor is None:
                break
            
            current = best_neighbor
            current_h = best_neighbor_h
            actions.append(best_action)
            path.append(PuzzleState(current))
        
        # Track best result
        if current_h < best_h:
            best_h = current_h
            best_path = path
            best_actions = actions
    
    result = SearchResult(
        success=False,
        algorithm="Random-Restart Hill Climbing",
        group="Local Search",
        path=best_path,
        actions=best_actions,
        path_cost=len(best_actions) if best_actions else 0,
        nodes_expanded=total_expanded,
        nodes_generated=total_generated,
        trace=trace,
        message=f"Best h={best_h} after {max_restarts} restarts",
        optimal="No",
        complete="Yes, with enough restarts"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def local_beam_search(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    beam_width: int = 4,
    max_steps: int = 500,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100
) -> SearchResult:
    """
    Local Beam Search.
    
    Keeps k best states at each step.
    Better than single hill climbing.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    metrics = SearchMetrics()
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="Local Beam Search",
            group="Local Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            message="Already at goal!",
            optimal="No",
            complete="No"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # Beam entries: (current_state, action_path, state_path, heuristic)
    beam = [(start, [], [start], h_func(start, goal))]
    
    # Initialize with diversity
    for _ in range(beam_width - 1):
        curr_st = PuzzleState(start)
        curr_actions = []
        curr_path = [start]
        for _ in range(10):  # random walk
            neighbors = curr_st.get_neighbors()
            if neighbors:
                a, nxt = random.choice(neighbors)
                curr_actions.append(a)
                curr_path.append(nxt.state)
                curr_st = nxt
        beam.append((curr_st.state, curr_actions, curr_path, h_func(curr_st.state, goal)))

    
    for step in range(max_steps):
        if timer.elapsed > max_time_ms:
            break
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "Local Beam Search",
                "Node": f"Beam size: {len(beam)}",
                "Action": "-",
                "Depth": step,
                "g": 0,
                "h": min(b[3] for b in beam),
                "f": min(b[3] for b in beam),
                "Frontier": len(beam),
                "Reached": len(beam),
                "Note": f"Best h={min(b[3] for b in beam)}"
            })
        
        # Check if goal in beam
        for state, actions, state_path, h in beam:
            if state == goal:
                result = SearchResult(
                    success=True,
                    algorithm="Local Beam Search",
                    group="Local Search",
                    path=[PuzzleState(s) for s in state_path],
                    actions=actions,
                    path_cost=len(actions),
                    nodes_expanded=step,
                    nodes_generated=step * beam_width * 4,
                    trace=trace,
                    message=f"Goal found among beam candidates",
                    optimal="No",
                    complete="No"
                )
                timer.__exit__()
                result.runtime_ms = timer.elapsed_ms
                return result
        
        # Generate all successors
        all_successors = []
        for state, actions, state_path, h in beam:
            current_state = PuzzleState(state)
            neighbors = current_state.get_neighbors(action_order)
            metrics.increment_expanded()
            metrics.increment_generated(len(neighbors))
            
            for action, neighbor_state in neighbors:
                new_h = h_func(neighbor_state.state, goal)
                all_successors.append((
                    neighbor_state.state,
                    actions + [action],
                    state_path + [neighbor_state.state],
                    new_h
                ))
        
        # Select k best
        all_successors.sort(key=lambda x: x[3])
        beam = all_successors[:beam_width]
        
        # Remove duplicates
        seen = set()
        unique_beam = []
        for state, actions, state_path, h in beam:
            if state not in seen:
                seen.add(state)
                unique_beam.append((state, actions, state_path, h))
        beam = unique_beam[:beam_width]
        
        if not beam:
            break
    
    result = SearchResult(
        success=False,
        algorithm="Local Beam Search",
        group="Local Search",
        nodes_expanded=metrics.nodes_expanded,
        nodes_generated=metrics.nodes_generated,
        trace=trace,
        message=f"No solution found within {max_steps} steps",
        optimal="No",
        complete="No"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def simulated_annealing(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    initial_temp: float = 100.0,
    cooling_rate: float = 0.995,
    min_temp: float = 0.01,
    max_steps: int = 10000,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Simulated Annealing.
    
    Accepts worse moves with probability exp(-delta/T).
    Can escape local optima.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    if seed is not None:
        random.seed(seed)
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    metrics = SearchMetrics()
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="Simulated Annealing",
            group="Local Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            message="Already at goal!",
            optimal="No",
            complete="Yes, with slow cooling"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    current = start
    current_h = h_func(current, goal)
    
    best_state = current
    best_h = current_h
    best_path = [PuzzleState(current)]
    best_actions = []
    
    path = [PuzzleState(current)]
    actions = []
    
    T = initial_temp
    
    for step in range(max_steps):
        if timer.elapsed > max_time_ms:
            break
        
        if T < min_temp:
            break
        
        current_state = PuzzleState(current)
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "Simulated Annealing",
                "Node": str(current_state),
                "Action": actions[-1] if actions else "Start",
                "Depth": step,
                "g": step,
                "h": current_h,
                "f": current_h,
                "Frontier": 0,
                "Reached": step + 1,
                "Note": f"T={T:.2f}, h={current_h}, best_h={best_h}"
            })
        
        if current == goal:
            result = SearchResult(
                success=True,
                algorithm="Simulated Annealing",
                group="Local Search",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                nodes_generated=step * 4,
                trace=trace,
                message=f"Goal found at step {step}",
                optimal="No",
                complete="Yes, with slow cooling"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Get random neighbor
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_expanded()
        metrics.increment_generated(len(neighbors))
        
        if not neighbors:
            break
        
        action, neighbor_state = random.choice(neighbors)
        neighbor_h = h_func(neighbor_state.state, goal)
        
        delta = neighbor_h - current_h
        
        # Accept if better, or with probability exp(-delta/T)
        if delta < 0 or random.random() < math.exp(-delta / T):
            current = neighbor_state.state
            current_h = neighbor_h
            actions.append(action)
            path.append(neighbor_state)
            
            # Track best
            if current_h < best_h:
                best_h = current_h
                best_state = current
                best_path = list(path)
                best_actions = list(actions)
        
        # Cool down
        T *= cooling_rate
    
    # Return best found
    if best_state == goal:
        result = SearchResult(
            success=True,
            algorithm="Simulated Annealing",
            group="Local Search",
            path=best_path,
            actions=best_actions,
            path_cost=len(best_actions),
            nodes_expanded=metrics.nodes_expanded,
            nodes_generated=metrics.nodes_generated,
            trace=trace,
            message="Goal found!",
            optimal="No",
            complete="Yes, with slow cooling"
        )
    else:
        result = SearchResult(
            success=False,
            algorithm="Simulated Annealing",
            group="Local Search",
            path=best_path,
            actions=best_actions,
            path_cost=len(best_actions) if best_actions else 0,
            nodes_expanded=metrics.nodes_expanded,
            nodes_generated=metrics.nodes_generated,
            trace=trace,
            message=f"Best h={best_h} (not goal)",
            optimal="No",
            complete="Yes, with slow cooling"
        )
    
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result
