"""
Uninformed Search Algorithms for 8-Puzzle.

Algorithms:
1. BFS - Breadth-First Search
2. DFS - Depth-First Search
3. UCS - Uniform Cost Search
4. IDS - Iterative Deepening Search
"""

from typing import Tuple, Optional, List, Dict, Any, Set
from collections import deque
import heapq
import sys

sys.path.append('..')
from core.puzzle import PuzzleState, reconstruct_path
from core.node import Node, SearchResult
from core.heuristics import get_heuristic
from core.metrics import SearchMetrics
from core.utils import Timer, create_trace_row


def bfs(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    max_nodes: int = 100000,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100
) -> SearchResult:
    """
    Breadth-First Search.
    
    Uses FIFO queue. Expands shallowest node first.
    Optimal for unit cost. Complete for finite state spaces.
    
    Args:
        start: Starting state tuple
        goal: Goal state tuple (default: standard goal)
        max_nodes: Maximum nodes to expand
        max_time_ms: Maximum runtime in milliseconds
        action_order: Order to try actions
        trace_limit: Maximum trace rows to record
    
    Returns:
        SearchResult with path, metrics, and trace
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    timer = Timer()
    timer.__enter__()
    
    metrics = SearchMetrics()
    trace = []
    
    # Initialize
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    # Check if already solved
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="BFS",
            group="Uninformed Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            nodes_expanded=0,
            nodes_generated=1,
            max_frontier_size=0,
            reached_size=1,
            trace=[],
            message="Already at goal!",
            optimal="Yes, when every step cost is 1",
            complete="Yes, with finite state space"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # Check solvability
    if not start_state.is_solvable():
        result = SearchResult(
            success=False,
            algorithm="BFS",
            group="Uninformed Search",
            message="Puzzle is not solvable (odd inversions)",
            optimal="Yes, when every step cost is 1",
            complete="Yes, with finite state space"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # BFS uses FIFO queue
    frontier = deque()
    start_node = Node(state=start, g=0, depth=0)
    frontier.append(start_node)
    
    reached: Set[Tuple[int, ...]] = {start}
    
    step = 0
    
    while frontier:
        # Check limits
        if metrics.nodes_expanded >= max_nodes:
            result = SearchResult(
                success=False,
                algorithm="BFS",
                group="Uninformed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message=f"Max nodes ({max_nodes}) exceeded",
                max_nodes_exceeded=True,
                optimal="Yes, when every step cost is 1",
                complete="Yes, with finite state space"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        if timer.elapsed > max_time_ms:
            result = SearchResult(
                success=False,
                algorithm="BFS",
                group="Uninformed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message=f"Timeout ({max_time_ms}ms) exceeded",
                timeout=True,
                optimal="Yes, when every step cost is 1",
                complete="Yes, with finite state space"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Pop from front (FIFO)
        node = frontier.popleft()
        metrics.increment_expanded()
        
        current_state = PuzzleState(node.state)
        
        # Record trace
        if len(trace) < trace_limit:
            trace.append(create_trace_row(
                step=step,
                algorithm="BFS",
                node_state=node.state,
                action=node.action,
                depth=node.depth,
                g=node.g,
                h=0,
                f=node.g,
                frontier=list(frontier),
                reached=reached,
                note=f"Expanded node at depth {node.depth}"
            ))
        
        step += 1
        
        # Goal check moved to generation time (Early Goal Test)
        # Expand
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_generated(len(neighbors))
        
        for action, neighbor_state in neighbors:
            if neighbor_state.state not in reached:
                reached.add(neighbor_state.state)
                child = Node(
                    state=neighbor_state.state,
                    parent=node,
                    action=action,
                    g=node.g + 1,
                    depth=node.depth + 1
                )
                
                # Check goal immediately upon generation (Early Goal Test)
                if child.state == goal:
                    path, actions = reconstruct_path(child)
                    result = SearchResult(
                        success=True,
                        algorithm="BFS",
                        group="Uninformed Search",
                        path=path,
                        actions=actions,
                        path_cost=child.g,
                        nodes_expanded=metrics.nodes_expanded,
                        nodes_generated=metrics.nodes_generated,
                        max_frontier_size=metrics.max_frontier_size,
                        reached_size=len(reached),
                        trace=trace,
                        message="Goal found!",
                        optimal="Yes, when every step cost is 1",
                        complete="Yes, with finite state space"
                    )
                    timer.__exit__()
                    result.runtime_ms = timer.elapsed_ms
                    return result
                
                frontier.append(child)
        
        metrics.update_frontier(len(frontier))
        metrics.update_reached(len(reached))
    
    # No solution
    result = SearchResult(
        success=False,
        algorithm="BFS",
        group="Uninformed Search",
        nodes_expanded=metrics.nodes_expanded,
        nodes_generated=metrics.nodes_generated,
        max_frontier_size=metrics.max_frontier_size,
        reached_size=len(reached),
        trace=trace,
        message="No solution found",
        optimal="Yes, when every step cost is 1",
        complete="Yes, with finite state space"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def dfs(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    max_depth: int = 50,
    max_nodes: int = 100000,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100
) -> SearchResult:
    """
    Depth-First Search with depth limit.
    
    Uses LIFO stack. Expands deepest node first.
    NOT optimal. NOT complete without depth limit.
    
    Args:
        start: Starting state tuple
        goal: Goal state tuple
        max_depth: Maximum depth to search
        max_nodes: Maximum nodes to expand
        max_time_ms: Maximum runtime
        action_order: Order to try actions
        trace_limit: Maximum trace rows
    
    Returns:
        SearchResult
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    timer = Timer()
    timer.__enter__()
    
    metrics = SearchMetrics()
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="DFS",
            group="Uninformed Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            nodes_expanded=0,
            nodes_generated=1,
            max_frontier_size=0,
            reached_size=1,
            trace=[],
            message="Already at goal!",
            optimal="No",
            complete="No, without depth limit"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    if not start_state.is_solvable():
        result = SearchResult(
            success=False,
            algorithm="DFS",
            group="Uninformed Search",
            message="Puzzle is not solvable",
            optimal="No",
            complete="No, without depth limit"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # DFS uses LIFO stack
    frontier = []
    start_node = Node(state=start, g=0, depth=0)
    frontier.append(start_node)
    
    reached: Dict[Tuple[int, ...], int] = {start: 0}
    
    step = 0
    
    while frontier:
        if metrics.nodes_expanded >= max_nodes:
            result = SearchResult(
                success=False,
                algorithm="DFS",
                group="Uninformed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message=f"Max nodes ({max_nodes}) exceeded",
                max_nodes_exceeded=True,
                optimal="No",
                complete="No, without depth limit"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        if timer.elapsed > max_time_ms:
            result = SearchResult(
                success=False,
                algorithm="DFS",
                group="Uninformed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message=f"Timeout ({max_time_ms}ms) exceeded",
                timeout=True,
                optimal="No",
                complete="No, without depth limit"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        # Pop from end (LIFO)
        node = frontier.pop()
        
        # Depth limit check
        if node.depth > max_depth:
            continue
            
        metrics.increment_expanded()
        
        current_state = PuzzleState(node.state)
        
        if len(trace) < trace_limit:
            trace.append(create_trace_row(
                step=step,
                algorithm="DFS",
                node_state=node.state,
                action=node.action,
                depth=node.depth,
                g=node.g,
                h=0,
                f=node.g,
                frontier=list(frontier),
                reached=reached,
                note=f"Expanded at depth {node.depth}"
            ))
        
        step += 1
        
        if node.state == goal:
            path, actions = reconstruct_path(node)
            result = SearchResult(
                success=True,
                algorithm="DFS",
                group="Uninformed Search",
                path=path,
                actions=actions,
                path_cost=node.g,
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message=f"Goal found at depth {node.depth}",
                optimal="No",
                complete="No, without depth limit"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_generated(len(neighbors))
        
        for action, neighbor_state in neighbors:
            child_depth = node.depth + 1
            if neighbor_state.state not in reached or child_depth < reached[neighbor_state.state]:
                reached[neighbor_state.state] = child_depth
                child = Node(
                    state=neighbor_state.state,
                    parent=node,
                    action=action,
                    g=node.g + 1,
                    depth=child_depth
                )
                frontier.append(child)
        
        metrics.update_frontier(len(frontier))
        metrics.update_reached(len(reached))
    
    result = SearchResult(
        success=False,
        algorithm="DFS",
        group="Uninformed Search",
        nodes_expanded=metrics.nodes_expanded,
        nodes_generated=metrics.nodes_generated,
        max_frontier_size=metrics.max_frontier_size,
        reached_size=len(reached),
        trace=trace,
        message=f"No solution found within depth {max_depth}",
        optimal="No",
        complete="No, without depth limit"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def ucs(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    max_nodes: int = 100000,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100
) -> SearchResult:
    """
    Uniform Cost Search.
    
    Uses priority queue ordered by g(n).
    Optimal for any non-negative costs.
    For unit cost, same as BFS.
    
    Args:
        start: Starting state
        goal: Goal state
        max_nodes: Maximum nodes to expand
        max_time_ms: Maximum runtime
        action_order: Action order
        trace_limit: Trace limit
    
    Returns:
        SearchResult
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    timer = Timer()
    timer.__enter__()
    
    metrics = SearchMetrics()
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="UCS",
            group="Uninformed Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            nodes_expanded=0,
            nodes_generated=1,
            message="Already at goal!",
            optimal="Yes, for non-negative costs",
            complete="Yes, with finite state space"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    if not start_state.is_solvable():
        result = SearchResult(
            success=False,
            algorithm="UCS",
            group="Uninformed Search",
            message="Puzzle is not solvable",
            optimal="Yes, for non-negative costs",
            complete="Yes, with finite state space"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # UCS uses priority queue by g
    frontier = []
    counter = 0  # Tie-breaker
    start_node = Node(state=start, g=0, depth=0)
    heapq.heappush(frontier, (0, counter, start_node))
    counter += 1
    
    reached: Dict[Tuple[int, ...], int] = {start: 0}
    
    step = 0
    
    while frontier:
        if metrics.nodes_expanded >= max_nodes:
            result = SearchResult(
                success=False,
                algorithm="UCS",
                group="Uninformed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message=f"Max nodes ({max_nodes}) exceeded",
                max_nodes_exceeded=True,
                optimal="Yes, for non-negative costs",
                complete="Yes, with finite state space"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        if timer.elapsed > max_time_ms:
            result = SearchResult(
                success=False,
                algorithm="UCS",
                group="Uninformed Search",
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message=f"Timeout ({max_time_ms}ms) exceeded",
                timeout=True,
                optimal="Yes, for non-negative costs",
                complete="Yes, with finite state space"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        _, _, node = heapq.heappop(frontier)
        metrics.increment_expanded()
        
        # Skip if we've found better path to this state
        if node.state in reached and reached[node.state] < node.g:
            continue
        
        current_state = PuzzleState(node.state)
        
        if len(trace) < trace_limit:
            trace.append(create_trace_row(
                step=step,
                algorithm="UCS",
                node_state=node.state,
                action=node.action,
                depth=node.depth,
                g=node.g,
                h=0,
                f=node.g,
                frontier=[n[2].state for n in frontier[:5]],
                reached=set(reached.keys()),
                note=f"g={node.g}"
            ))
        
        step += 1
        
        if node.state == goal:
            path, actions = reconstruct_path(node)
            result = SearchResult(
                success=True,
                algorithm="UCS",
                group="Uninformed Search",
                path=path,
                actions=actions,
                path_cost=node.g,
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=len(reached),
                trace=trace,
                message="Goal found!",
                optimal="Yes, for non-negative costs",
                complete="Yes, with finite state space"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
        
        neighbors = current_state.get_neighbors(action_order)
        metrics.increment_generated(len(neighbors))
        
        for action, neighbor_state in neighbors:
            new_g = node.g + 1  # Unit cost
            
            if neighbor_state.state not in reached or new_g < reached[neighbor_state.state]:
                reached[neighbor_state.state] = new_g
                child = Node(
                    state=neighbor_state.state,
                    parent=node,
                    action=action,
                    g=new_g,
                    depth=node.depth + 1
                )
                heapq.heappush(frontier, (new_g, counter, child))
                counter += 1
        
        metrics.update_frontier(len(frontier))
        metrics.update_reached(len(reached))
    
    result = SearchResult(
        success=False,
        algorithm="UCS",
        group="Uninformed Search",
        nodes_expanded=metrics.nodes_expanded,
        nodes_generated=metrics.nodes_generated,
        max_frontier_size=metrics.max_frontier_size,
        reached_size=len(reached),
        trace=trace,
        message="No solution found",
        optimal="Yes, for non-negative costs",
        complete="Yes, with finite state space"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def ids(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    max_depth: int = 30,
    max_nodes: int = 100000,
    max_time_ms: float = 30000,
    action_order: str = "LRUD",
    trace_limit: int = 100
) -> SearchResult:
    """
    Iterative Deepening Search.
    
    Runs DFS with increasing depth limits.
    Optimal for unit cost. Low memory.
    
    Args:
        start: Starting state
        goal: Goal state
        max_depth: Maximum depth limit
        max_nodes: Maximum nodes
        max_time_ms: Maximum runtime
        action_order: Action order
        trace_limit: Trace limit
    
    Returns:
        SearchResult
    """
    if goal is None:
        goal = PuzzleState.GOAL_STATE
    
    timer = Timer()
    timer.__enter__()
    
    metrics = SearchMetrics()
    trace = []
    
    start_state = PuzzleState(start)
    goal_state = PuzzleState(goal)
    
    if start_state.state == goal_state.state:
        result = SearchResult(
            success=True,
            algorithm="IDS",
            group="Uninformed Search",
            path=[start_state],
            actions=[],
            path_cost=0,
            nodes_expanded=0,
            nodes_generated=1,
            message="Already at goal!",
            optimal="Yes, when every step cost is 1",
            complete="Yes, up to configured depth limit"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    if not start_state.is_solvable():
        result = SearchResult(
            success=False,
            algorithm="IDS",
            group="Uninformed Search",
            message="Puzzle is not solvable",
            optimal="Yes, when every step cost is 1",
            complete="Yes, up to configured depth limit"
        )
        timer.__exit__()
        result.runtime_ms = timer.elapsed_ms
        return result
    
    # IDS: iterate depth from 0 to max_depth
    for depth_limit in range(max_depth + 1):
        if metrics.nodes_expanded >= max_nodes:
            break
        
        if timer.elapsed > max_time_ms:
            break
        
        # Run depth-limited DFS
        dls_result = _depth_limited_search(
            start=start,
            goal=goal,
            depth_limit=depth_limit,
            metrics=metrics,
            action_order=action_order
        )
        
        # Add to trace
        if len(trace) < trace_limit:
            trace.append({
                "Step": len(trace),
                "Algorithm": "IDS",
                "Node": f"Depth limit: {depth_limit}",
                "Action": "-",
                "Depth": depth_limit,
                "g": 0,
                "h": 0,
                "f": 0,
                "Frontier": 0,
                "Reached": metrics.reached_size,
                "Note": f"Starting iteration with depth limit {depth_limit}"
            })
        
        if dls_result["found"]:
            # Reconstruct path
            node = dls_result["node"]
            path, actions = reconstruct_path(node)
            
            result = SearchResult(
                success=True,
                algorithm="IDS",
                group="Uninformed Search",
                path=path,
                actions=actions,
                path_cost=node.g,
                nodes_expanded=metrics.nodes_expanded,
                nodes_generated=metrics.nodes_generated,
                max_frontier_size=metrics.max_frontier_size,
                reached_size=metrics.reached_size,
                trace=trace,
                message=f"Goal found at depth limit {depth_limit}",
                optimal="Yes, when every step cost is 1",
                complete="Yes, up to configured depth limit"
            )
            timer.__exit__()
            result.runtime_ms = timer.elapsed_ms
            return result
    
    result = SearchResult(
        success=False,
        algorithm="IDS",
        group="Uninformed Search",
        nodes_expanded=metrics.nodes_expanded,
        nodes_generated=metrics.nodes_generated,
        max_frontier_size=metrics.max_frontier_size,
        reached_size=metrics.reached_size,
        trace=trace,
        message=f"No solution found within depth limit {max_depth}",
        optimal="Yes, when every step cost is 1",
        complete="Yes, up to configured depth limit"
    )
    timer.__exit__()
    result.runtime_ms = timer.elapsed_ms
    return result


def _depth_limited_search(
    start: Tuple[int, ...],
    goal: Tuple[int, ...],
    depth_limit: int,
    metrics: SearchMetrics,
    action_order: str = "LRUD"
) -> Dict[str, Any]:
    """
    Helper: Depth-limited DFS for IDS.
    
    Returns dict with 'found' and 'node' (if found).
    """
    frontier = []
    start_node = Node(state=start, g=0, depth=0)
    frontier.append((start_node, {start}))
    
    while frontier:
        node, path_set = frontier.pop()
        
        # Increment after popping but only if we process it
        metrics.increment_expanded()
        metrics.update_frontier(len(frontier))
        
        if node.state == goal:
            return {"found": True, "node": node}
        
        if node.depth < depth_limit:
            current_state = PuzzleState(node.state)
            neighbors = current_state.get_neighbors(action_order)
            metrics.increment_generated(len(neighbors))
            
            for action, neighbor_state in neighbors:
                if neighbor_state.state not in path_set:
                    child = Node(
                        state=neighbor_state.state,
                        parent=node,
                        action=action,
                        g=node.g + 1,
                        depth=node.depth + 1
                    )
                    child_path_set = set(path_set)
                    child_path_set.add(neighbor_state.state)
                    frontier.append((child, child_path_set))
                metrics.update_frontier(len(frontier))
    
    return {"found": False, "node": None}
