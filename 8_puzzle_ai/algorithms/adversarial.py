"""
Adversarial and stochastic search demos.

The 8-puzzle is a deterministic single-player problem, so Minimax,
Alpha-Beta, and Expectimax are demonstrated on a small Caro board instead of
pretending the puzzle has an opponent.
"""

from __future__ import annotations

import math
import random
from typing import List, Optional, Tuple

try:
    from ..core.node import SearchResult
    from ..core.utils import Timer
except ImportError:
    from core.node import SearchResult
    from core.utils import Timer


CaroBoard = Tuple[str, ...]
CARO_START: CaroBoard = ("X", "O", "X", ".", "O", ".", ".", ".", ".")
CARO_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def _board_text(board: CaroBoard) -> str:
    rows = [" ".join(board[index : index + 3]) for index in range(0, 9, 3)]
    return "Caro board\n" + "\n".join(rows)


def _winner(board: CaroBoard) -> Optional[str]:
    for a, b, c in CARO_LINES:
        if board[a] != "." and board[a] == board[b] == board[c]:
            return board[a]
    if "." not in board:
        return "Draw"
    return None


def _moves(board: CaroBoard) -> List[int]:
    return [index for index, cell in enumerate(board) if cell == "."]


def _apply(board: CaroBoard, move: int, player: str) -> CaroBoard:
    cells = list(board)
    cells[move] = player
    return tuple(cells)


def _action(move: int, player: str) -> str:
    row, col = divmod(move, 3)
    return f"{player}@{row + 1},{col + 1}"


def _children(board: CaroBoard, player: str, rng: random.Random) -> List[Tuple[str, CaroBoard]]:
    children = [(_action(move, player), _apply(board, move, player)) for move in _moves(board)]
    if len(children) > 1:
        rng.shuffle(children)
    return children


def _utility(board: CaroBoard, ply: int) -> float:
    winner = _winner(board)
    if winner == "X":
        return 100.0 - ply
    if winner == "O":
        return ply - 100.0
    if winner == "Draw":
        return 0.0

    score = 0.0
    for line in CARO_LINES:
        cells = [board[index] for index in line]
        x_count = cells.count("X")
        o_count = cells.count("O")
        if x_count and o_count:
            continue
        if x_count:
            score += 1.5 * x_count
        if o_count:
            score -= 1.5 * o_count
    return score - 0.01 * ply


def _finish(
    *,
    timer: Timer,
    algorithm: str,
    trace: list,
    chosen_action: str,
    chosen_score: float,
    nodes_expanded: int,
    nodes_generated: int,
    max_frontier_size: int,
    note: str,
) -> SearchResult:
    timer.__exit__()
    return SearchResult(
        success=True,
        algorithm=algorithm,
        group="Adversarial Search",
        path=[],
        actions=[chosen_action] if chosen_action != "No move" else [],
        path_cost=1 if chosen_action != "No move" else 0,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier_size=max_frontier_size,
        reached_size=max_frontier_size + 1,
        runtime_ms=timer.elapsed_ms,
        trace=trace,
        message=f"{algorithm} selected Caro move {chosen_action} for MAX (X), value={chosen_score:.2f}.",
        optimal="For the bounded Caro game tree only",
        complete="Yes, within configured Caro depth",
        notes=note,
    )


def _trace_row(
    *,
    algorithm: str,
    node: CaroBoard,
    action: str,
    depth: int,
    score: float,
    frontier: List[str],
    reached: List[str],
    note: str,
    pruned: int = 0,
) -> dict:
    return {
        "Step": 0,
        "Algorithm": algorithm,
        "Node": _board_text(node),
        "Action": action,
        "Depth": depth,
        "g": 0,
        "h": 0,
        "f": round(score, 2),
        "Frontier": "\n---\n".join(frontier),
        "Reached": "\n---\n".join(reached),
        "Priority Rule": "Caro game tree utility; MAX is X, MIN/chance is O",
        "Selection Key": f"game=Caro; depth={depth}; utility={score:.2f}; pruned={pruned}",
        "Note": note,
    }


def _minimax_like(
    algorithm: str,
    max_depth: int,
    trace_limit: int,
    seed: Optional[int],
) -> SearchResult:
    rng = random.Random(seed)
    timer = Timer()
    timer.__enter__()
    depth_limit = max(1, min(6, max_depth))
    nodes_expanded = 0
    nodes_generated = 1
    pruned = 0

    def value(board: CaroBoard, depth: int, maximizing: bool, alpha: float, beta: float) -> float:
        nonlocal nodes_expanded, nodes_generated, pruned
        if depth == 0 or _winner(board) is not None:
            return _utility(board, depth_limit - depth)

        player = "X" if maximizing else "O"
        children = _children(board, player, rng)
        nodes_expanded += 1
        nodes_generated += len(children)

        if maximizing:
            best = -math.inf
            for index, (_child_action, child) in enumerate(children):
                best = max(best, value(child, depth - 1, False, alpha, beta))
                if algorithm == "Alpha-Beta Pruning":
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        pruned += len(children) - index - 1
                        break
            return best

        best = math.inf
        for index, (_child_action, child) in enumerate(children):
            best = min(best, value(child, depth - 1, True, alpha, beta))
            if algorithm == "Alpha-Beta Pruning":
                beta = min(beta, best)
                if beta <= alpha:
                    pruned += len(children) - index - 1
                    break
        return best

    scored = [
        (value(child, depth_limit - 1, False, -math.inf, math.inf), action, child)
        for action, child in _children(CARO_START, "X", rng)
    ]
    chosen_score, chosen_action, chosen_board = max(scored, key=lambda item: (item[0], item[1]))
    frontier = [f"{action}\n{_board_text(board)}" for _score, action, board in scored]
    trace = []
    if trace_limit > 0:
        trace.append(
            _trace_row(
                algorithm=algorithm,
                node=CARO_START,
                action=chosen_action,
                depth=depth_limit,
                score=chosen_score,
                frontier=frontier,
                reached=[_board_text(CARO_START), _board_text(chosen_board)],
                note=f"MAX chooses {chosen_action}; backed-up utility={chosen_score:.2f}; pruned branches={pruned}.",
                pruned=pruned,
            )
        )

    return _finish(
        timer=timer,
        algorithm=algorithm,
        trace=trace,
        chosen_action=chosen_action,
        chosen_score=chosen_score,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier_size=max(len(scored), 1),
        note="Educational Caro mini-game: 8-puzzle has no opponent, so this demonstrates MAX/MIN game-tree reasoning separately.",
    )


def minimax(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_depth: int = 4,
    trace_limit: int = 100,
    seed: Optional[int] = None,
) -> SearchResult:
    """Run Minimax on the educational Caro game tree."""
    return _minimax_like("Minimax", max_depth, trace_limit, seed)


def alpha_beta(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_depth: int = 6,
    trace_limit: int = 100,
    seed: Optional[int] = None,
) -> SearchResult:
    """Run Alpha-Beta Pruning on the educational Caro game tree."""
    return _minimax_like("Alpha-Beta Pruning", max_depth, trace_limit, seed)


def expectimax(
    start: Tuple[int, ...],
    goal: Tuple[int, ...] = None,
    heuristic: str = "manhattan",
    max_depth: int = 4,
    success_prob: float = 0.8,
    trace_limit: int = 100,
    seed: Optional[int] = None,
) -> SearchResult:
    """Run Expectimax where O replies are chance outcomes in the Caro game."""
    rng = random.Random(seed)
    timer = Timer()
    timer.__enter__()
    depth_limit = max(1, min(6, max_depth))
    nodes_expanded = 0
    nodes_generated = 1

    def expected_value(board: CaroBoard, depth: int, maximizing: bool) -> float:
        nonlocal nodes_expanded, nodes_generated
        if depth == 0 or _winner(board) is not None:
            return _utility(board, depth_limit - depth)

        if maximizing:
            children = _children(board, "X", rng)
            nodes_expanded += 1
            nodes_generated += len(children)
            values = [expected_value(child, depth - 1, False) for _action, child in children]
            return max(values) if values else _utility(board, depth_limit - depth)

        children = _children(board, "O", rng)
        nodes_expanded += 1
        nodes_generated += len(children)
        if not children:
            return _utility(board, depth_limit - depth)
        probability = 1.0 / len(children)
        return sum(probability * expected_value(child, depth - 1, True) for _action, child in children)

    scored = []
    for action, child in _children(CARO_START, "X", rng):
        o_children = _children(child, "O", rng)
        if not o_children:
            score = _utility(child, 1)
            outcomes = [f"No O move\n{_board_text(child)}"]
        else:
            probability = 1.0 / len(o_children)
            score = sum(probability * expected_value(outcome, depth_limit - 1, True) for _o_action, outcome in o_children)
            outcomes = [f"p={probability:.2f} {o_action}\n{_board_text(outcome)}" for o_action, outcome in o_children]
        scored.append((score, action, child, outcomes))

    chosen_score, chosen_action, chosen_board, outcomes = max(scored, key=lambda item: (item[0], item[1]))
    trace = []
    if trace_limit > 0:
        trace.append(
            _trace_row(
                algorithm="Expectimax",
                node=CARO_START,
                action=chosen_action,
                depth=depth_limit,
                score=chosen_score,
                frontier=outcomes,
                reached=[_board_text(CARO_START), _board_text(chosen_board)],
                note=f"MAX chooses {chosen_action}; expected utility={chosen_score:.2f}; chance outcomes={len(outcomes)}.",
            )
        )

    return _finish(
        timer=timer,
        algorithm="Expectimax",
        trace=trace,
        chosen_action=chosen_action,
        chosen_score=chosen_score,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier_size=max(len(scored), len(outcomes), 1),
        note="Educational Caro mini-game: Expectimax treats O replies as chance outcomes because 8-puzzle has no stochastic opponent.",
    )
