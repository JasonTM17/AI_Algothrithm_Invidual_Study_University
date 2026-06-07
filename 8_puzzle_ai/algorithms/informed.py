"""
Informed Search Algorithms for 8-Puzzle.

Algorithms:
1. Greedy Best-First Search
2. A* Search
3. IDA* Search
"""

from typing import Tuple, Optional, List, Dict, Any, Set
import heapq
import sys

sys.path.append('..')
from core.puzzle import PuzzleState, reconstruct_path
from core.node import Node, SearchResult
from core.heuristics import get_heuristic
from core.metrics import SearchMetrics
from core.utils import Timer, create_trace_row


def greedy(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_nodes: int = 100000,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100
) -> SearchResult:
    """
    Greedy Best-First Search.
    
    Expands node with lowest h(n).
    Fast but NOT optimal.
    
    Args:
        start: Starting state
        goal: Goal state
        heuristic: Heuristic function name
        max_nodes: Maximum nodes to expand
        max_time_ms: Maximum runtime
        action_order: Action order
        trace_limit: Trace limit
    
    Returns:
        SearchResult
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
            algorithm="Greedy",
            group="Informed Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            nodes_expanded=0,
            nodes_generated=1,
            message="Already at goal!",
            optimal="No",
            complete="No, limited by max expansions"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    if not start_state.is_solvable():
        result = SearchResult(
            success=False,
            algorithm="Greedy",
            group="Informed Search",
            message="Puzzle is not solvable",
            optimal="No",
            complete="No, limited by max expansions"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # Priority queue by h
    frontier = []
    counter = 0
    h_start = h_func(start, goal)
    start_node = Node(state=start, g=0, depth=0, h=h_start)
    heapq.heappush(frontier, (h_start, counter, start_node))
    counter += 1
    
    reached: Set[Tuple[int, ...]] = {start}
    
    step = 0
    
    while frontier:
        if metrics.nodes_expanded >= max_nodes:
            result = SearchResult(
                success=False,
                algorithm="Greedy",
                group="Informed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message=f"Max nodes ({max_nodes}) exceeded",
                max_nodes_exceeded=True,
                optimal="No",
                complete="No, limited by max expansions"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        if timer.elapsed > max_time_ms:
            result = SearchResult(
                success=False,
                algorithm="Greedy",
                group="Informed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message=f"Timeout ({max_time_ms}ms) exceeded",
                timeout=True,
                optimal="No",
                complete="No, limited by max expansions"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        _, _, node = heapq.heappop(frontier)
        metrics.increment_expanded()
        
        current_state = PuzzleState(node.state)
        
        if len(trace) < trace_limit:
            trace.append(create_trace_row(
                step=step,
                algorithm="Greedy",
                node_state=node.state,
                action=node.action,
                depth=node.depth,
                g=node.g,
                h=node.h,
                f=node.h,
                frontier=[n[2].state for n in frontier[:5]],
                reached=reached,
                note=f"h={node.h}"
            ))
        
        step += 1
        
        if node.state == goal:
            path, actions = reconstruct_path(node)
            result = SearchResult(
                success=True,
                algorithm="Greedy",
                group="Informed Search",
                path=path,
                actions=actions,
                path_cost=node.g,
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message="Goal found!",
                optimal="No",
                complete="No, limited by max expansions"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_generated(len(neighbors))
        
        for action, neighbor_state in neighbors:
            if neighbor_state.state not in reached:
                reached.add(neighbor_state.state)
                h = h_func(neighbor_state.state, goal)
                child = Node(
                    state=neighbor_state.state,
                    parent=node,
                    action=action,
                    g=node.g + 1,
                    depth=node.depth + 1,
                    h=h
                )
                heapq.heappush(frontier, (h, counter, child))
                counter += 1
        
        metrics.update_frontier(len(frontier))
        metrics.update_reached(len(reached))
    
    result = SearchResult(
        success=False,
        algorithm="Greedy",
        group="Informed Search",
        nodes_expanded=metrics.nodes_expanded,
        nodes_generated=metrics.nodes_generated,
        max_frontier_size=metrics.max_frontier_size,
        reached_size=len(reached),
        trace=trace,
        message="No solution found",
        optimal="No",
        complete="No, limited by max expansions"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def astar(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_nodes: int = 100000,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100
) -> SearchResult:
    """
    A* Search.
    
    Expands node with lowest f(n) = g(n) + h(n).
    Optimal with admissible/consistent heuristic.
    BEST for 8-puzzle.
    
    Args:
        start: Starting state
        goal: Goal state
        heuristic: Heuristic function
        max_nodes: Maximum nodes
        max_time_ms: Maximum runtime
        action_order: Action order
        trace_limit: Trace limit
    
    Returns:
        SearchResult
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
            algorithm="A*",
            group="Informed Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            nodes_expanded=0,
            nodes_generated=1,
            message="Already at goal!",
            optimal="Yes, with admissible heuristic",
            complete="Yes, with finite state space and admissible heuristic"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    if not start_state.is_solvable():
        result = SearchResult(
            success=False,
            algorithm="A*",
            group="Informed Search",
            message="Puzzle is not solvable",
            optimal="Yes, with admissible heuristic",
            complete="Yes, with finite state space and admissible heuristic"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # Priority queue by f = g + h
    frontier = []
    counter = 0
    h_start = h_func(start, goal)
    start_node = Node(state=start, g=0, depth=0, h=h_start)
    heapq.heappush(frontier, (h_start, counter, start_node))
    counter += 1
    
    # Track best g for each state
    best_g: Dict[Tuple[int, ...], int] = {start: 0}
    
    step = 0
    
    while frontier:
        if metrics.nodes_expanded >= max_nodes:
            result = SearchResult(
                success=False,
                algorithm="A*",
                group="Informed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(best_g),
                trace=trace,
                message=f"Max nodes ({max_nodes}) exceeded",
                max_nodes_exceeded=True,
                optimal="Yes, with admissible heuristic",
                complete="Yes, with finite state space and admissible heuristic"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        if timer.elapsed > max_time_ms:
            result = SearchResult(
                success=False,
                algorithm="A*",
                group="Informed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(best_g),
                trace=trace,
                message=f"Timeout ({max_time_ms}ms) exceeded",
                timeout=True,
                optimal="Yes, with admissible heuristic",
                complete="Yes, with finite state space and admissible heuristic"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        _, _, node = heapq.heappop(frontier)
        
        # Skip if we've found better path
        if node.state in best_g and best_g[node.state] < node.g:
            continue
        
        metrics.increment_expanded()
        
        current_state = PuzzleState(node.state)
        
        if len(trace) < trace_limit:
            trace.append(create_trace_row(
                step=step,
                algorithm="A*",
                node_state=node.state,
                action=node.action,
                depth=node.depth,
                g=node.g,
                h=node.h,
                f=node.f,
                frontier=[n[2].state for n in frontier[:5]],
                reached=set(best_g.keys()),
                note=f"f={node.f} (g={node.g}, h={node.h})"
            ))
        
        step += 1
        
        if node.state == goal:
            path, actions = reconstruct_path(node)
            result = SearchResult(
                success=True,
                algorithm="A*",
                group="Informed Search",
                path=path,
                actions=actions,
                path_cost=node.g,
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(best_g),
                trace=trace,
                message="Goal found!",
                optimal="Yes, with admissible heuristic",
                complete="Yes, with finite state space and admissible heuristic"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_generated(len(neighbors))
        
        for action, neighbor_state in neighbors:
            new_g = node.g + 1
            
            if neighbor_state.state not in best_g or new_g < best_g[neighbor_state.state]:
                best_g[neighbor_state.state] = new_g
                h = h_func(neighbor_state.state, goal)
                child = Node(
                    state=neighbor_state.state,
                    parent=node,
                    action=action,
                    g=new_g,
                    depth=node.depth + 1,
                    h=h
                )
                heapq.heappush(frontier, (child.f, counter, child))
                counter += 1
        
        metrics.update_frontier(len(frontier))
        metrics.update_reached(len(best_g))
    
    result = SearchResult(
        success=False,
        algorithm="A*",
        group="Informed Search",
        nodes_expanded=metrics.nodes_expanded,
        nodes_generated=metrics.nodes_generated,
        max_frontier_size=metrics.max_frontier_size,
        reached_size=len(best_g),
        trace=trace,
        message="No solution found",
        optimal="Yes, with admissible heuristic",
        complete="Yes, with finite state space and admissible heuristic"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def idastar(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_iterations: int = 100,
    max_nodes: int = 100000,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100
) -> SearchResult:
    """
    IDA* Search.
    
    Iterative deepening on f-cost threshold.
    Optimal with admissible heuristic.
    Low memory like IDS.
    
    Args:
        start: Starting state
        goal: Goal state
        heuristic: Heuristic function
        max_iterations: Maximum iterations
        max_nodes: Maximum nodes
        max_time_ms: Maximum runtime
        action_order: Action order
        trace_limit: Trace limit
    
    Returns:
        SearchResult
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
            algorithm="IDA*",
            group="Informed Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            nodes_expanded=0,
            nodes_generated=1,
            message="Already at goal!",
            optimal="Yes, with admissible heuristic and enough iterations",
            complete="Yes, up to configured iteration/expansion limits"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    if not start_state.is_solvable():
        result = SearchResult(
            success=False,
            algorithm="IDA*",
            group="Informed Search",
            message="Puzzle is not solvable",
            optimal="Yes, with admissible heuristic and enough iterations",
            complete="Yes, up to configured iteration/expansion limits"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # Initial threshold = h(start)
    threshold = h_func(start, goal)
    
    for iteration in range(max_iterations):
        if metrics.nodes_expanded >= max_nodes:
            break
        
        if timer.elapsed > max_time_ms:
            break
        
        if len(trace) < trace_limit:
            trace.append({
                "Step": len(trace),
                "Algorithm": "IDA*",
                "Node": f"Iteration {iteration}",
                "Action": "-",
                "Depth": 0,
                "g": 0,
                "h": 0,
                "f": threshold,
                "Frontier": 0,
                "Reached": metrics.reached_size,
                "Note": f"Threshold = {threshold}"
            })
        
        # Run DFS with f threshold
        result = _ida_star_search(
            start=start,
            goal=goal,
            threshold=threshold,
            h_func=h_func,
            metrics=metrics,
            action_order=action_order
        )
        
        if result["found"]:
            node = result["node"]
            path, actions = reconstruct_path(node)
            
            search_result = SearchResult(
                success=True,
                algorithm="IDA*",
                group="Informed Search",
                path=path,
                actions=actions,
                path_cost=node.g,
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=metrics.reached_size,
                trace=trace,
                message=f"Goal found with threshold {threshold}",
                optimal="Yes, with admissible heuristic and enough iterations",
                complete="Yes, up to configured iteration/expansion limits"
            )
            timer.__exit__()
            search_result.runtime_ms = timer.elapsed_ms
            return search_result
        
        # Update threshold to minimum f that exceeded
        if result["min_exceeded"] == float('inf'):
            break
        threshold = result["min_exceeded"]
    
    result = SearchResult(
        success=False,
        algorithm="IDA*",
        group="Informed Search",
        nodes_expanded=metrics.nodes_expanded,
        nodes_generated=metrics.nodes_generated,
        max_frontier_size=metrics.max_frontier_size,
        reached_size=metrics.reached_size,
        trace=trace,
        message=f"No solution found within {max_iterations} iterations",
        optimal="Yes, with admissible heuristic and enough iterations",
        complete="Yes, up to configured iteration/expansion limits"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def _ida_star_search(
    start: Tuple[int, ...],
    goal: Tuple[int, ...],
    threshold: int,
    h_func,
    metrics: SearchMetrics,
    action_order: str = "LRUD"
) -> Dict[str, Any]:
    """
    Helper: DFS with f threshold for IDA*.
    """
    min_exceeded = float('inf')
    stack = []
    
    h_start = h_func(start, goal)
    start_node = Node(state=start, g=0, depth=0, h=h_start)
    stack.append(start_node)
    
    while stack:
        node = stack.pop()
        metrics.increment_expanded()
        metrics.update_frontier(len(stack))
        
        if node.f > threshold:
            min_exceeded = min(min_exceeded, node.f)
            continue
        
        if node.state == goal:
            return {"found": True, "node": node, "min_exceeded": min_exceeded}
        
        current_state = PuzzleState(node.state)
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_generated(len(neighbors))
        
        for action, neighbor_state in neighbors:
            h = h_func(neighbor_state.state, goal)
            child = Node(
                state=neighbor_state.state,
                parent=node,
                action=action,
                g=node.g + 1,
                depth=node.depth + 1,
                h=h
            )
            stack.append(child)
            metrics.update_frontier(len(stack))
    
    return {"found": False, "node": None, "min_exceeded": min_exceeded}
