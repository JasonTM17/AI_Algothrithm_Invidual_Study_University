"""
Constraint Satisfaction Problem Algorithms for 8-Puzzle.

Note: 8-puzzle is NOT a standard CSP. It's a state-space search problem.
These implementations are for educational purposes to demonstrate CSP concepts.

We model 8-puzzle as a temporal CSP where:
- Variables: X[t][p] = tile at position p at time t
- Constraints: AllDifferent, Transition, Goal
"""

from typing import Tuple, Optional, List, Dict, Any, Set

try:
    from ..core.puzzle import PuzzleState
    from ..core.node import SearchResult
    from ..core.heuristics import misplaced_tiles
    from ..core.utils import Timer
except ImportError:
    from core.puzzle import PuzzleState
    from core.node import SearchResult
    from core.heuristics import misplaced_tiles
    from core.utils import Timer


def csp_backtracking(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    max_time_steps: int = 10,
    max_nodes: int = 10000,
    trace_limit: int = 100
) -> SearchResult:
    """
    CSP Backtracking for 8-puzzle planning.
    
    Models 8-puzzle as temporal CSP:
    - Variables: X[t][p] for t in 0..T, p in 0..8
    - Domains: {0,1,2,3,4,5,6,7,8}
    - Constraints: AllDifferent, Transition, Goal
    
    This is for EDUCATIONAL purposes - 8-puzzle is not naturally a CSP.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    timer = Timer()
    timer.__enter__()
    
    trace = []
    nodes_expanded = 0
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="CSP Backtracking",
            group="Constraint Satisfaction",
            message="Already at goal!",
            optimal="No",
            complete="Yes, for finite domains",
            notes="Educational: 8-puzzle is state-space search, not static CSP"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # Try different time horizons
    for T in range(1, max_time_steps + 1):
        if nodes_expanded >= max_nodes:
            break
        
        # Try to find plan of length T
        result = _csp_backtrack_recursive(
            start=start,
            goal=goal,
            T=T,
            current_t=0,
            current_state=start,
            path=[start],
            actions=[],
            nodes_expanded=[nodes_expanded],
            max_nodes=max_nodes,
            trace=trace,
            trace_limit=trace_limit
        )
        
        nodes_expanded = result.get("nodes_expanded", nodes_expanded)
        
        if result["success"]:
            search_result = SearchResult(
                success=True,
                algorithm="CSP Backtracking",
                group="Constraint Satisfaction",
                path=[PuzzleState(s) for s in result["path"]],
                actions=result["actions"],
                path_cost=len(result["actions"]),
                nodes_expanded=nodes_expanded,
                trace=trace,
                message=f"Found plan with {T} steps",
                optimal="No",
                complete="Yes, for finite domains",
                notes="Educational: 8-puzzle is state-space search, not static CSP"
            )
            timer.__exit__()
            search_result.runtime_ms = timer.elapsed_ms
            return search_result
    
    result = SearchResult(
        success=False,
        algorithm="CSP Backtracking",
        group="Constraint Satisfaction",
        nodes_expanded=nodes_expanded,
        trace=trace,
        message=f"No solution within {max_time_steps} time steps",
        optimal="No",
        complete="Yes, for finite domains",
        notes="Educational: 8-puzzle is state-space search, not static CSP"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def _csp_backtrack_recursive(
    start: Tuple[int, ...],
    goal: Tuple[int, ...],
    T: int,
    current_t: int,
    current_state: Tuple[int, ...],
    path: List[Tuple[int, ...]],
    actions: List[str],
    nodes_expanded: List[int],
    max_nodes: int,
    trace: List[Dict],
    trace_limit: int
) -> Dict[str, Any]:
    """Recursive backtracking helper."""
    
    nodes_expanded[0] += 1
    
    if nodes_expanded[0] >= max_nodes:
        return {"success": False, "nodes_expanded": nodes_expanded[0]}
    
    # Check if goal reached
    if current_state == goal:
        return {
            "success": True,
            "path": path,
            "actions": actions,
            "nodes_expanded": nodes_expanded[0]
        }
    
    # Check if time limit reached
    if current_t >= T:
        return {"success": False, "nodes_expanded": nodes_expanded[0]}
    
    # Get valid actions
    puzzle = PuzzleState(current_state)
    neighbors = puzzle.get_neighbors()
    
    if len(trace) < trace_limit:
        trace.append({
            "Step": len(trace),
            "Algorithm": "CSP Backtracking",
            "Node": str(puzzle),
            "Action": actions[-1] if actions else "Start",
            "Depth": current_t,
            "g": current_t,
            "h": misplaced_tiles(current_state, goal),
            "f": 0,
            "Frontier": len(neighbors),
            "Reached": current_t + 1,
            "Note": f"Time step {current_t}/{T}"
        })
    
    # Try each action (variable assignment)
    for action, neighbor in neighbors:
        # Check constraint: AllDifferent (implicit in state representation)
        # Check constraint: Transition (valid move)
        
        new_path = path + [neighbor.state]
        new_actions = actions + [action]
        
        result = _csp_backtrack_recursive(
            start=start,
            goal=goal,
            T=T,
            current_t=current_t + 1,
            current_state=neighbor.state,
            path=new_path,
            actions=new_actions,
            nodes_expanded=nodes_expanded,
            max_nodes=max_nodes,
            trace=trace,
            trace_limit=trace_limit
        )
        
        if result["success"]:
            return result
    
    return {"success": False, "nodes_expanded": nodes_expanded[0]}


def min_conflicts(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    max_steps: int = 1000,
    trace_limit: int = 100
) -> SearchResult:
    """
    Min-Conflicts algorithm for CSP.
    
    For 8-puzzle, we interpret this as:
    - Start with current state
    - Count conflicts (misplaced tiles)
    - Try to reduce conflicts
    
    This is EDUCATIONAL - min-conflicts is for CSP repair, not path finding.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    timer = Timer()
    timer.__enter__()
    
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="Min-Conflicts",
            group="Constraint Satisfaction",
            message="Already at goal!",
            optimal="No",
            complete="No",
            notes="Educational: Min-conflicts is for CSP repair, not path finding"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    current = start
    path = [PuzzleState(current)]
    actions = []
    
    for step in range(max_steps):
        current_state = PuzzleState(current)
        conflicts = misplaced_tiles(current, goal)
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": step,
                "Algorithm": "Min-Conflicts",
                "Node": str(current_state),
                "Action": actions[-1] if actions else "Start",
                "Depth": step,
                "g": step,
                "h": conflicts,
                "f": conflicts,
                "Frontier": 0,
                "Reached": step + 1,
                "Note": f"Conflicts: {conflicts}"
            })
        
        if current == goal:
            result = SearchResult(
                success=True,
                algorithm="Min-Conflicts",
                group="Constraint Satisfaction",
                path=path,
                actions=actions,
                path_cost=len(actions),
                nodes_expanded=step,
                trace=trace,
                message="Goal reached!",
                optimal="No",
                complete="No",
                notes="Educational: Min-conflicts is for CSP repair, not path finding"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Find move that minimizes conflicts
        neighbors = current_state.get_neighbors()
        if not neighbors:
            break
        
        best_action = None
        best_neighbor = None
        best_conflicts = conflicts
        
        for action, neighbor in neighbors:
            neighbor_conflicts = misplaced_tiles(neighbor.state, goal)
            if neighbor_conflicts < best_conflicts:
                best_conflicts = neighbor_conflicts
                best_action = action
                best_neighbor = neighbor
        
        if best_action is None:
            # Stuck at local minimum
            break
        
        actions.append(best_action)
        current = best_neighbor.state
        path.append(best_neighbor)
    
    result = SearchResult(
        success=False,
        algorithm="Min-Conflicts",
        group="Constraint Satisfaction",
        path=path,
        actions=actions,
        nodes_expanded=max_steps,
        trace=trace,
        message=f"Stuck at local minimum with {misplaced_tiles(current, goal)} conflicts",
        optimal="No",
        complete="No",
        notes="Educational: Min-conflicts is for CSP repair, not path finding"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def constraint_propagation_demo(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    trace_limit: int = 100
) -> SearchResult:
    """
    Demonstrate constraint propagation on 8-puzzle.
    
    Shows how domains are reduced when applying constraints.
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    timer = Timer()
    timer.__enter__()
    
    trace = []
    
    # Initialize domains for each position
    # For goal state, each position has a fixed value
    domains = {i: set(range(9)) for i in range(9)}
    
    # Apply goal constraint: each position must have specific value
    goal_domains = {}
    for i, val in enumerate(goal):
        goal_domains[i] = {val}
    
    # Apply AllDifferent constraint
    # For goal, this is satisfied
    
    for i in range(9):
        if len(trace) < trace_limit:
            trace.append({
                "Step": i,
                "Algorithm": "Constraint Propagation",
                "Node": f"Position {i}",
                "Action": "-",
                "Depth": 0,
                "g": 0,
                "h": 0,
                "f": 0,
                "Frontier": 0,
                "Reached": i + 1,
                "Note": f"Position {i}: domain reduced to {{{goal[i]}}}"
            })
    
    result = SearchResult(
        success=True,
        algorithm="Constraint Propagation Demo",
        group="Constraint Satisfaction",
        trace=trace,
        message="Demonstrated constraint propagation on goal state",
        optimal="No",
        complete="No",
        notes="Educational: Shows how constraints reduce domains"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result
