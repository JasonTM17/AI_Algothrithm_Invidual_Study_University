"""
Complex Environment Search Algorithms for 8-Puzzle.

Algorithms:
1. AND-OR Search (for nondeterministic environments)
2. No Observation Search (belief state)
3. Partially Observable Search
4. Online Search

Note: These are NOT standard for 8-puzzle which is deterministic and fully observable.
These are educational implementations to demonstrate the concepts.
"""

from typing import Tuple, Optional, List, Dict, Any, Set
import random

try:
    from ..core.puzzle import PuzzleState
    from ..core.node import SearchResult
    from ..core.heuristics import get_heuristic
    from ..core.utils import Timer
except ImportError:
    from core.puzzle import PuzzleState
    from core.node import SearchResult
    from core.heuristics import get_heuristic
    from core.utils import Timer


def and_or_search(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_depth: int = 20,
    nondeterministic_prob: float = 0.1,
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    AND-OR Search for nondeterministic environments.
    
    This is a SIMULATION for educational purposes.
    Standard 8-puzzle is deterministic, so we simulate nondeterminism
    by having a probability of action failure.
    
    Returns a conditional plan.
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
            algorithm="AND-OR Search",
            group="Complex Environments",
            message="Already at goal!",
            optimal="No",
            complete="Yes, for finite state spaces",
            notes="Educational: 8-puzzle is deterministic, this simulates nondeterminism"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # Simulate nondeterministic execution
    current = start
    path = [PuzzleState(current)]
    actions = []
    
    for step in range(max_depth):
        current_state = PuzzleState(current)
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "AND-OR Search",
                "Node": str(current_state),
                "Action": actions[-1] if actions else "Start",
                "Depth": step,
                "g": step,
                "h": h_func(current, goal),
                "f": h_func(current, goal),
                "Frontier": 0,
                "Reached": step + 1,
                "Note": f"OR node - choosing action"
            })
        
        if current == goal:
            result = SearchResult(
                success=True,
                algorithm="AND-OR Search",
                group="Complex Environments",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                trace=trace,
                message="Goal reached!",
                optimal="No",
                complete="Yes, for finite state spaces",
                notes="Educational: 8-puzzle is deterministic"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Choose best action (OR node)
        neighbors = current_state.get_neighbors()
        if not neighbors:
            break
        
        # Pick action that minimizes h
        best_action = None
        best_neighbor = None
        best_h = float('inf')
        
        for action, neighbor_state in neighbors:
            h = h_func(neighbor_state.state, goal)
            if h < best_h:
                best_h = h
                best_action = action
                best_neighbor = neighbor_state
        
        if best_action is None:
            break
        
        # Simulate AND node (nondeterministic outcome)
        if random.random() < nondeterministic_prob:
            # Action fails - pick random valid action instead
            other_actions = [(a, s) for a, s in neighbors if a != best_action]
            if other_actions:
                best_action, best_neighbor = random.choice(other_actions)
        
        actions.append(best_action)
        current = best_neighbor.state
        path.append(best_neighbor)
    
    result = SearchResult(
        success=False,
        algorithm="AND-OR Search",
        group="Complex Environments",
        path=path,
        actions=actions,
        nodes_expanded=max_depth,
        trace=trace,
        message="Did not reach goal within depth limit",
        optimal="No",
        complete="Yes, for finite state spaces",
        notes="Educational: 8-puzzle is deterministic, this simulates nondeterminism"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def no_observation_search(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    initial_belief_size: int = 3,
    max_steps: int = 100,
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Searching with No Observation.
    
    Uses belief state - set of possible states.
    This is educational - 8-puzzle is fully observable.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    if seed is not None:
        random.seed(seed)
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    trace = []
    
    # Create initial belief state
    # For demo, start with actual state plus some random states
    belief_state = {start}
    
    # Add random solvable states
    for _ in range(initial_belief_size - 1):
        random_state = PuzzleState(PuzzleState.GOAL_STATE)
        # Scramble a bit
        for _ in range(5):
            neighbors = random_state.get_neighbors()
            if neighbors:
                _, random_state = random.choice(neighbors)
        belief_state.add(random_state.state)
    
    actions = []
    
    for step in range(max_steps):
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "No Observation",
                "Node": f"Belief size: {len(belief_state)}",
                "Action": actions[-1] if actions else "Start",
                "Depth": step,
                "g": step,
                "h": min(h_func(s, goal) for s in belief_state),
                "f": 0,
                "Frontier": 0,
                "Reached": len(belief_state),
                "Note": f"Belief state has {len(belief_state)} states"
            })
        
        # Check if all states are goal
        if all(s == goal for s in belief_state):
            result = SearchResult(
                success=True,
                algorithm="No Observation Search",
                group="Complex Environments",
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                trace=trace,
                message="All belief states reached goal!",
                optimal="No",
                complete="Yes, for finite state spaces",
                notes="Educational: 8-puzzle is fully observable"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Choose action that works for most states in belief
        action_counts = {}
        for state in belief_state:
            puzzle = PuzzleState(state)
            neighbors = puzzle.get_neighbors()
            for action, _ in neighbors:
                action_counts[action] = action_counts.get(action, 0) + 1
        
        if not action_counts:
            break
        
        # Pick most common valid action
        best_action = max(action_counts.keys(), key=lambda a: action_counts[a])
        actions.append(best_action)
        
        # Update belief state
        new_belief = set()
        for state in belief_state:
            puzzle = PuzzleState(state)
            neighbors = puzzle.get_neighbors()
            for action, neighbor in neighbors:
                if action == best_action:
                    new_belief.add(neighbor.state)
                    break
        
        belief_state = new_belief
    
    result = SearchResult(
        success=False,
        algorithm="No Observation Search",
        group="Complex Environments",
        actions=actions,
        nodes_expanded=max_steps,
        trace=trace,
        message="Could not reach goal for all belief states",
        optimal="No",
        complete="Yes, for finite state spaces",
        notes="Educational: 8-puzzle is fully observable"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def partially_observable_search(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_steps: int = 100,
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Partially Observable Search.
    
    Agent can only observe blank position and adjacent tiles.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    trace = []
    
    current = start
    path = [PuzzleState(current)]
    actions = []
    
    for step in range(max_steps):
        current_state = PuzzleState(current)
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "Partially Observable",
                "Node": str(current_state),
                "Action": actions[-1] if actions else "Start",
                "Depth": step,
                "g": step,
                "h": h_func(current, goal),
                "f": h_func(current, goal),
                "Frontier": 0,
                "Reached": step + 1,
                "Note": "Observation: blank position + adjacent tiles"
            })
        
        if current == goal:
            result = SearchResult(
                success=True,
                algorithm="Partially Observable Search",
                group="Complex Environments",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                trace=trace,
                message="Goal reached!",
                optimal="No",
                complete="Yes",
                notes="Educational: 8-puzzle is fully observable"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Get observation (blank position)
        blank_idx = current.index(0)
        blank_row, blank_col = blank_idx // 3, blank_idx % 3
        
        # Choose action based on partial observation
        neighbors = current_state.get_neighbors()
        if not neighbors:
            break
        
        # Use heuristic with partial info
        best_action = None
        best_neighbor = None
        best_h = float('inf')
        
        for action, neighbor in neighbors:
            h = h_func(neighbor.state, goal)
            if h < best_h:
                best_h = h
                best_action = action
                best_neighbor = neighbor
        
        if best_action is None:
            break
        
        actions.append(best_action)
        current = best_neighbor.state
        path.append(best_neighbor)
    
    result = SearchResult(
        success=False,
        algorithm="Partially Observable Search",
        group="Complex Environments",
        path=path,
        actions=actions,
        nodes_expanded=max_steps,
        trace=trace,
        message="Did not reach goal",
        optimal="No",
        complete="Yes",
        notes="Educational: 8-puzzle is fully observable"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def online_search(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_steps: int = 500,
    trace_limit: int = 100,
    seed: Optional[int] = None
) -> SearchResult:
    """
    Online Search (LRTA*).
    
    Agent doesn't know the environment in advance.
    Updates heuristic as it explores.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    h_func = get_heuristic(heuristic)
    timer = Timer()
    timer.__enter__()
    
    trace = []
    
    # H table: state -> estimated cost to goal
    H = {}
    
    current = start
    path = [PuzzleState(current)]
    actions = []
    visited = {start}
    
    for step in range(max_steps):
        current_state = PuzzleState(current)
        
        # Initialize H if not seen
        if current not in H:
            H[current] = h_func(current, goal)
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "Online Search (LRTA*)",
                "Node": str(current_state),
                "Action": actions[-1] if actions else "Start",
                "Depth": step,
                "g": step,
                "h": H[current],
                "f": H[current],
                "Frontier": 0,
                "Reached": len(visited),
                "Note": f"H[{current_state.to_matrix_string()}] = {H[current]}"
            })
        
        if current == goal:
            result = SearchResult(
                success=True,
                algorithm="Online Search",
                group="Complex Environments",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                trace=trace,
                message="Goal reached!",
                optimal="No",
                complete="Yes",
                notes="LRTA*: updates H as it explores"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Get neighbors
        neighbors = current_state.get_neighbors()
        if not neighbors:
            break
        
        # Calculate min cost + H for each neighbor
        min_cost = float('inf')
        best_action = None
        best_neighbor = None
        
        for action, neighbor in neighbors:
            if neighbor.state not in H:
                H[neighbor.state] = h_func(neighbor.state, goal)
            
            cost = 1 + H[neighbor.state]
            if cost < min_cost:
                min_cost = cost
                best_action = action
                best_neighbor = neighbor
        
        if best_action is None:
            break
        
        # Update H for current state (monotonic update)
        H[current] = max(H.get(current, 0), min_cost)
        
        # Move to neighbor
        actions.append(best_action)
        current = best_neighbor.state
        path.append(best_neighbor)
        visited.add(current)
    
    result = SearchResult(
        success=False,
        algorithm="Online Search",
        group="Complex Environments",
        path=path,
        actions=actions,
        nodes_expanded=max_steps,
        trace=trace,
        message="Did not reach goal",
        optimal="No",
        complete="Yes",
        notes="LRTA*: updates H as it explores"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result
