"""Detailed 8-puzzle search visualizer for Python and Jupyter.

The module is intentionally self-contained:
- Core algorithms work in plain Python.
- Tables use pandas when available, otherwise lists of dictionaries.
- Jupyter widgets are optional; `launch_jupyter_app()` falls back gracefully.
"""

from __future__ import annotations

import argparse
import heapq
import html
import io
import math
import random
import time
import zipfile
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from xml.sax.saxutils import escape as xml_escape


State = Tuple[int, ...]
GOAL_STATE: State = (1, 2, 3, 4, 5, 6, 7, 8, 0)
BOARD_SIZE = 3
TRACE_COLUMNS = [
    "Step",
    "Algorithm",
    "Node",
    "Action",
    "Depth",
    "g",
    "h",
    "f",
    "Priority Rule",
    "Selection Key",
    "Generated Children",
    "Skipped States",
    "Frontier",
    "Reached",
    "Decision/Note",
]
DEFAULT_HEURISTICS = ["misplaced", "manhattan"]


@dataclass
class TraceConfig:
    """Runtime limits for search and table output."""

    max_expansions: int = 5000
    max_trace_rows: int = 300
    frontier_preview: int = 5
    reached_preview: int = 5
    dfs_depth_limit: int = 50
    ids_max_depth: int = 30
    ida_max_iterations: int = 80
    local_max_steps: int = 200
    random_restarts: int = 20
    beam_width: int = 4
    seed: Optional[int] = None
    sa_initial_temp: float = 100.0
    sa_cooling_rate: float = 0.995
    sa_min_temp: float = 0.01
    sa_max_steps: int = 5000
    partial_goal_pattern: Optional[Tuple[Optional[int], ...]] = None


@dataclass
class SearchNode:
    state: State
    parent: Optional["SearchNode"] = None
    action: str = "Start"
    g: int = 0
    depth: int = 0
    h: int = 0

    @property
    def f(self) -> int:
        return self.g + self.h


@dataclass
class SearchResult:
    algorithm: str
    start: State
    goal: State
    found: bool
    path: List[State] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    path_cost: Optional[int] = None
    expanded: int = 0
    generated: int = 0
    max_frontier: int = 0
    reached_count: int = 0
    runtime_ms: float = 0.0
    memory_estimate_kb: float = 0.0
    trace_rows: List[Dict[str, Any]] = field(default_factory=list)
    message: str = ""
    optimal: str = "No"
    complete: str = "No"
    notes: str = ""

    def summary_row(self) -> Dict[str, Any]:
        return {
            "Algorithm": self.algorithm,
            "Found": self.found,
            "Path Length": self.path_cost if self.path_cost is not None else "",
            "Expanded": self.expanded,
            "Generated": self.generated,
            "Max Frontier": self.max_frontier,
            "Reached": self.reached_count,
            "Runtime ms": round(self.runtime_ms, 3),
            "Optimal": self.optimal,
            "Complete": self.complete,
            "Memory": f"{self.memory_estimate_kb:.1f} KB",
            "Message": self.message,
        }


ALGORITHM_INFO: Dict[str, Dict[str, str]] = {
    "BFS": {
        "group": "Uninformed Search",
        "optimal": "Yes, when every step cost is 1",
        "complete": "Yes, with finite state space",
        "suitable": "Yes, canonical deterministic 8-puzzle solver",
    },
    "DFS": {
        "group": "Uninformed Search",
        "optimal": "No",
        "complete": "Limited by max expansions/depth",
        "suitable": "Yes, but not optimal and must be depth-limited",
    },
    "UCS": {
        "group": "Uninformed Search",
        "optimal": "Yes, for non-negative costs",
        "complete": "Yes, with finite state space",
        "suitable": "Yes, equivalent to BFS behavior when every move costs 1",
    },
    "IDS": {
        "group": "Uninformed Search",
        "optimal": "Yes, when every step cost is 1 and depth limit is enough",
        "complete": "Up to configured depth limit",
        "suitable": "Yes, memory-light canonical solver with repeated expansions",
    },
    "Greedy": {
        "group": "Informed Search",
        "optimal": "No",
        "complete": "Limited by max expansions",
        "suitable": "Yes, heuristic solver but not optimal",
    },
    "A*": {
        "group": "Informed Search",
        "optimal": "Yes, with admissible heuristic",
        "complete": "Yes, with finite state space and admissible heuristic",
        "suitable": "Yes, canonical optimal heuristic solver",
    },
    "IDA*": {
        "group": "Informed Search",
        "optimal": "Yes, with admissible heuristic and enough iterations",
        "complete": "Up to configured iteration/expansion limits",
        "suitable": "Yes, memory-light heuristic solver",
    },
    "Simple Hill Climbing": {
        "group": "Local Search",
        "optimal": "No",
        "complete": "No",
        "suitable": "Demonstration solver; can get stuck on local optima",
    },
    "Steepest-Ascent Hill Climbing": {
        "group": "Local Search",
        "optimal": "No",
        "complete": "No",
        "suitable": "Demonstration solver; stronger local choice but still incomplete",
    },
    "Stochastic Hill Climbing": {
        "group": "Local Search",
        "optimal": "No",
        "complete": "No",
        "suitable": "Randomized demonstration solver; seed-dependent",
    },
    "Random-Restart Hill Climbing": {
        "group": "Local Search",
        "optimal": "No",
        "complete": "No, but restarts reduce local-minimum risk",
        "suitable": "Randomized demonstration solver; improves chance but not guarantee",
    },
    "Local Beam Search": {
        "group": "Local Search",
        "optimal": "No",
        "complete": "No",
        "suitable": "Population-style local demonstration solver",
    },
    "Simulated Annealing": {
        "group": "Local Search",
        "optimal": "No",
        "complete": "No, but probability of finding solution increases with time",
        "suitable": "Stochastic local demonstration solver",
    },
    "AND-OR Search": {
        "group": "Complex Environments",
        "optimal": "No, returns a bounded conditional-plan demonstration",
        "complete": "Bounded by max expansions and simulation depth",
        "suitable": "Educational extension for nondeterministic actions, not a canonical 8-puzzle solver",
    },
    "No Observation Search": {
        "group": "Complex Environments",
        "optimal": "No, belief-state demonstration",
        "complete": "Bounded by max expansions and belief update depth",
        "suitable": "Educational extension for belief states with no observations",
    },
    "Partially Observable Search": {
        "group": "Complex Environments",
        "optimal": "No, belief-update demonstration",
        "complete": "Bounded by max expansions and simulation depth",
        "suitable": "Educational extension where observations reveal blank position and adjacent tiles",
    },
    "Online Search": {
        "group": "Complex Environments",
        "optimal": "No",
        "complete": "Bounded LRTA* demonstration",
        "suitable": "Educational online/LRTA* extension; learns while moving",
    },
    "CSP Definition": {
        "group": "Constraint Satisfaction Problems",
        "optimal": "Not applicable; model description",
        "complete": "Not applicable; no state-space solving",
        "suitable": "Educational modeling of 8-puzzle as a time-indexed planning CSP",
    },
    "Constraint Propagation": {
        "group": "Constraint Satisfaction Problems",
        "optimal": "Not applicable; inference demonstration",
        "complete": "Not a complete solver by itself",
        "suitable": "Educational domain-reduction demonstration",
    },
    "Path Consistency": {
        "group": "Constraint Satisfaction Problems",
        "optimal": "Not applicable; consistency demonstration",
        "complete": "Not a complete solver by itself",
        "suitable": "Educational ternary consistency demonstration over planning variables",
    },
    "Global Constraints": {
        "group": "Constraint Satisfaction Problems",
        "optimal": "Not applicable; constraint demonstration",
        "complete": "Not a complete solver by itself",
        "suitable": "Educational AllDifferent/global-constraint demonstration",
    },
    "CSP Backtracking": {
        "group": "Constraint Satisfaction Problems",
        "optimal": "Yes only when depth bound equals the optimal solution depth and search is exhaustive",
        "complete": "Complete up to configured planning horizon",
        "suitable": "Educational bounded planning-CSP solver for shallow starts",
    },
    "Min-Conflicts": {
        "group": "Constraint Satisfaction Problems",
        "optimal": "No",
        "complete": "No",
        "suitable": "Educational local-repair CSP demonstration; better suited to large static CSPs",
    },
    "Constraint Graph": {
        "group": "Constraint Satisfaction Problems",
        "optimal": "Not applicable; graph representation",
        "complete": "Not applicable; no state-space solving",
        "suitable": "Educational constraint graph/hyperedge preview",
    },
    "Minimax": {
        "group": "Adversarial / Stochastic Search",
        "optimal": "Optimal only for the bounded adversarial game model, not for standard 8-puzzle",
        "complete": "Complete within configured game-tree depth",
        "suitable": "Educational two-player extension: MAX reduces h, MIN increases h",
    },
    "Alpha-Beta Pruning": {
        "group": "Adversarial / Stochastic Search",
        "optimal": "Same bounded-game value as Minimax when depth/order match",
        "complete": "Complete within configured game-tree depth",
        "suitable": "Educational pruning extension of Minimax",
    },
    "Expectimax": {
        "group": "Adversarial / Stochastic Search",
        "optimal": "Optimal expected action only for the configured stochastic model",
        "complete": "Complete within configured chance-tree depth",
        "suitable": "Educational stochastic extension with chance outcomes",
    },
}

PRIORITY_RULES: Dict[str, str] = {
    "BFS": "FIFO queue; expand the shallowest discovered node.",
    "DFS": "LIFO stack; expand the deepest discovered node.",
    "UCS": "Priority queue ordered by minimum g(n).",
    "IDS": "Depth-limited DFS with increasing depth limit.",
    "Greedy": "Priority queue ordered by minimum h(n).",
    "A*": "Priority queue ordered by minimum f(n)=g(n)+h(n); ties keep insertion order after h(n).",
    "IDA*": "DFS pruned by the current f(n)=g(n)+h(n) threshold.",
    "Simple Hill Climbing": "Move to the first neighbor that improves h(n).",
    "Steepest-Ascent Hill Climbing": "Move to the neighbor with the best h(n) improvement.",
    "Stochastic Hill Climbing": "Randomly choose among neighbors that improve h(n).",
    "Random-Restart Hill Climbing": "Run hill climbing from deterministic random-walk restarts and keep the best h(n).",
    "Local Beam Search": "Keep the top-k frontier states with the smallest h(n).",
    "Simulated Annealing": "Accept better moves and sometimes worse moves using exp(-delta_h/T).",
    "AND-OR Search": "OR node chooses an action; AND node records all possible nondeterministic outcomes.",
    "No Observation Search": "Choose one action for a belief state and update every possible state together.",
    "Partially Observable Search": "Update the belief state using action outcomes plus a partial observation.",
    "Online Search": "LRTA*: update H(s), then move to the neighbor minimizing c(s,a,s')+H(s').",
    "CSP Definition": "Define variables, domains, and constraints for a time-indexed planning CSP.",
    "Constraint Propagation": "Apply constraints to shrink variable domains before search.",
    "Path Consistency": "Check whether every pairwise assignment has support through a third variable.",
    "Global Constraints": "Apply AllDifferent and transition constraints across whole state snapshots.",
    "CSP Backtracking": "Depth-bounded backtracking over legal action assignments with forward checking.",
    "Min-Conflicts": "Iteratively change the conflicted variable/action that most reduces conflicts.",
    "Constraint Graph": "Represent CSP variables as nodes and constraints as edges or hyperedges.",
    "Minimax": "MAX chooses moves that maximize utility while MIN chooses moves that minimize it.",
    "Alpha-Beta Pruning": "Minimax with alpha/beta bounds to skip provably irrelevant branches.",
    "Expectimax": "MAX chooses the action with best expected value over stochastic chance outcomes.",
}

ALGORITHM_GROUP_ORDER = [
    "Uninformed Search",
    "Informed Search",
    "Local Search",
    "Complex Environments",
    "Constraint Satisfaction Problems",
    "Adversarial / Stochastic Search",
]

ALGORITHM_ALIASES: Dict[str, str] = {
    "bfs": "BFS",
    "breadthfirst": "BFS",
    "breadthfirstsearch": "BFS",
    "dfs": "DFS",
    "depthfirst": "DFS",
    "depthfirstsearch": "DFS",
    "ucs": "UCS",
    "uniformcost": "UCS",
    "uniformcostsearch": "UCS",
    "ids": "IDS",
    "iterativedeepening": "IDS",
    "iterativedeepeningsearch": "IDS",
    "greedy": "Greedy",
    "greedybestfirst": "Greedy",
    "greedybestfirstsearch": "Greedy",
    "astar": "A*",
    "a": "A*",
    "a_star": "A*",
    "a*": "A*",
    "ida": "IDA*",
    "idastar": "IDA*",
    "ida_star": "IDA*",
    "ida*": "IDA*",
    "idsa": "IDA*",
    "idsastar": "IDA*",
    "simplehillclimbing": "Simple Hill Climbing",
    "simplehill": "Simple Hill Climbing",
    "hillclimbing": "Steepest-Ascent Hill Climbing",
    "steepestascent": "Steepest-Ascent Hill Climbing",
    "steepesthillclimbing": "Steepest-Ascent Hill Climbing",
    "steepestascenthillclimbing": "Steepest-Ascent Hill Climbing",
    "stochastic": "Stochastic Hill Climbing",
    "stochastichillclimbing": "Stochastic Hill Climbing",
    "randomrestart": "Random-Restart Hill Climbing",
    "randomrestarthillclimbing": "Random-Restart Hill Climbing",
    "localbeam": "Local Beam Search",
    "localbeamsearch": "Local Beam Search",
    "simulatedannealing": "Simulated Annealing",
    "sa": "Simulated Annealing",
    "simulated": "Simulated Annealing",
    "annealing": "Simulated Annealing",
    "andor": "AND-OR Search",
    "andorsearch": "AND-OR Search",
    "and-or": "AND-OR Search",
    "and-orsearch": "AND-OR Search",
    "noobservation": "No Observation Search",
    "noobservationsearch": "No Observation Search",
    "searchingwithnoobservation": "No Observation Search",
    "partiallyobservable": "Partially Observable Search",
    "partiallyobservablesearch": "Partially Observable Search",
    "searchingforpartiallyobservableproblems": "Partially Observable Search",
    "online": "Online Search",
    "onlinesearch": "Online Search",
    "lrta": "Online Search",
    "lrtastar": "Online Search",
    "cspdefinition": "CSP Definition",
    "definitionofcsp": "CSP Definition",
    "constraintpropagation": "Constraint Propagation",
    "pathconsistency": "Path Consistency",
    "globalconstraints": "Global Constraints",
    "cspbacktracking": "CSP Backtracking",
    "backtrackingsearch": "CSP Backtracking",
    "minconflicts": "Min-Conflicts",
    "min-conflicts": "Min-Conflicts",
    "constraintgraph": "Constraint Graph",
    "constraintgraphs": "Constraint Graph",
    "minimax": "Minimax",
    "alphabeta": "Alpha-Beta Pruning",
    "alphabetapruning": "Alpha-Beta Pruning",
    "alpha-beta": "Alpha-Beta Pruning",
    "alpha-betapruning": "Alpha-Beta Pruning",
    "expectimax": "Expectimax",
}

DEFAULT_ALGORITHMS = list(ALGORITHM_INFO.keys())


def algorithm_groups() -> List[str]:
    """Return academic algorithm groups in coursework order."""

    available = {info["group"] for info in ALGORITHM_INFO.values()}
    ordered = [group for group in ALGORITHM_GROUP_ORDER if group in available]
    return ordered + sorted(available - set(ordered))


def algorithms_by_group() -> Dict[str, List[str]]:
    """Return algorithms grouped by their academic family."""

    grouped: Dict[str, List[str]] = {group: [] for group in algorithm_groups()}
    for name, info in ALGORITHM_INFO.items():
        grouped.setdefault(info["group"], []).append(name)
    return grouped


def normalize_algorithm(name: str) -> str:
    key = "".join(ch for ch in name.lower() if ch.isalnum() or ch in "*_")
    key = key.replace("_", "")
    if key in ALGORITHM_ALIASES:
        return ALGORITHM_ALIASES[key]
    raise ValueError(f"Unknown algorithm: {name}. Options: {', '.join(DEFAULT_ALGORITHMS)}")


def parse_state(value: str | Sequence[int] | State) -> State:
    if isinstance(value, tuple):
        state = value
    elif isinstance(value, str):
        cleaned = value.replace(",", " ").replace("/", " ").replace("|", " ")
        state = tuple(int(part) for part in cleaned.split())
    else:
        state = tuple(int(part) for part in value)
    validate_state(state)
    return state


def validate_state(state: State) -> None:
    if len(state) != 9:
        raise ValueError("An 8-puzzle state must contain exactly 9 numbers.")
    if set(state) != set(range(9)):
        raise ValueError("An 8-puzzle state must contain each number from 0 to 8 exactly once.")


def inversion_count(state: State) -> int:
    values = [x for x in state if x != 0]
    return sum(1 for i in range(len(values)) for j in range(i + 1, len(values)) if values[i] > values[j])


def is_solvable(state: State, goal: State = GOAL_STATE) -> bool:
    validate_state(state)
    validate_state(goal)
    return inversion_count(state) % 2 == inversion_count(goal) % 2


def board_rows(state: State) -> List[List[int]]:
    validate_state(state)
    return [list(state[i : i + BOARD_SIZE]) for i in range(0, 9, BOARD_SIZE)]


def board_string(state: State) -> str:
    return "\n".join(" ".join(str(cell) for cell in row) for row in board_rows(state))


def compact_state(state: State) -> str:
    return "/".join("".join(str(cell) for cell in row) for row in board_rows(state))


def render_board(state: State) -> Any:
    """Return a 3x3 board table. Uses pandas DataFrame when available."""

    rows = board_rows(state)
    try:
        import pandas as pd  # type: ignore

        return pd.DataFrame(rows, columns=["c1", "c2", "c3"])
    except Exception:
        return rows


def manhattan_distance(state: State, goal: State = GOAL_STATE) -> int:
    goal_positions = {tile: index for index, tile in enumerate(goal)}
    total = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        goal_index = goal_positions[tile]
        row, col = divmod(index, BOARD_SIZE)
        goal_row, goal_col = divmod(goal_index, BOARD_SIZE)
        total += abs(row - goal_row) + abs(col - goal_col)
    return total


def misplaced_tiles(state: State, goal: State = GOAL_STATE) -> int:
    return sum(1 for tile, goal_tile in zip(state, goal) if tile != 0 and tile != goal_tile)


def linear_conflict(state: State, goal: State = GOAL_STATE) -> int:
    """Manhattan distance plus two moves for each row/column linear conflict."""

    goal_positions = {tile: index for index, tile in enumerate(goal)}
    h = manhattan_distance(state, goal)

    for row in range(BOARD_SIZE):
        row_tiles: List[Tuple[int, int]] = []
        for col in range(BOARD_SIZE):
            tile = state[row * BOARD_SIZE + col]
            if tile == 0:
                continue
            goal_row, goal_col = divmod(goal_positions[tile], BOARD_SIZE)
            if goal_row == row:
                row_tiles.append((col, goal_col))
        for index, (_, goal_col) in enumerate(row_tiles):
            for _, other_goal_col in row_tiles[index + 1 :]:
                if goal_col > other_goal_col:
                    h += 2

    for col in range(BOARD_SIZE):
        col_tiles: List[Tuple[int, int]] = []
        for row in range(BOARD_SIZE):
            tile = state[row * BOARD_SIZE + col]
            if tile == 0:
                continue
            goal_row, goal_col = divmod(goal_positions[tile], BOARD_SIZE)
            if goal_col == col:
                col_tiles.append((row, goal_row))
        for index, (_, goal_row) in enumerate(col_tiles):
            for _, other_goal_row in col_tiles[index + 1 :]:
                if goal_row > other_goal_row:
                    h += 2

    return h


def get_heuristic(name: str, goal: State = GOAL_STATE) -> Callable[[State], int]:
    normalized = name.lower().replace("-", "_").replace(" ", "_")
    if normalized in {"manhattan", "manhattan_distance", "md"}:
        return lambda state: manhattan_distance(state, goal)
    if normalized in {"misplaced", "misplaced_tiles", "hamming"}:
        return lambda state: misplaced_tiles(state, goal)
    if normalized in {"linear_conflict", "linearconflict", "lc"}:
        return lambda state: linear_conflict(state, goal)
    raise ValueError("Unknown heuristic. Use 'misplaced' or 'manhattan'.")


def neighbors(state: State) -> List[Tuple[str, State]]:
    blank = state.index(0)
    row, col = divmod(blank, BOARD_SIZE)
    candidates: List[Tuple[str, int]] = []
    if row > 0:
        candidates.append(("Up", blank - BOARD_SIZE))
    if row < BOARD_SIZE - 1:
        candidates.append(("Down", blank + BOARD_SIZE))
    if col > 0:
        candidates.append(("Left", blank - 1))
    if col < BOARD_SIZE - 1:
        candidates.append(("Right", blank + 1))

    result: List[Tuple[str, State]] = []
    for action, swap_index in candidates:
        next_state = list(state)
        next_state[blank], next_state[swap_index] = next_state[swap_index], next_state[blank]
        result.append((action, tuple(next_state)))
    return result


def generate_random_state(scramble_moves: int = 20, seed: Optional[int] = None) -> State:
    """Generate a solvable start by walking from the goal through legal moves."""

    rng = random.Random(seed)
    state = GOAL_STATE
    previous: Optional[State] = None
    for _ in range(max(0, scramble_moves)):
        options = [(action, nxt) for action, nxt in neighbors(state) if nxt != previous]
        if not options:
            options = neighbors(state)
        previous = state
        state = rng.choice(options)[1]
    return state


DEMO_PRESETS: Dict[str, State] = {
    "easy_2": (1, 2, 3, 4, 5, 6, 0, 7, 8),
    "medium_10": generate_random_state(10, seed=7),
    "hard_20": generate_random_state(20, seed=1),
    "unsolvable_demo": (1, 2, 3, 4, 5, 6, 8, 7, 0),
}
DEFAULT_EXPERIMENT_PRESETS = ["easy_2", "medium_10", "hard_20", "unsolvable_demo"]
DEFAULT_EXPERIMENT_ALGORITHMS = ["BFS", "UCS", "A*", "Greedy", "IDA*"]
OPTIMAL_BASELINE_ALGORITHMS = {"BFS", "UCS", "A*", "IDA*"}
PARTIAL_GOAL_PATTERN: Tuple[Optional[int], ...] = (1, 2, None, None, None, None, None, None, None)


def parse_partial_goal(value: str | Sequence[Optional[int]]) -> Tuple[Optional[int], ...]:
    """Parse a partial goal pattern such as '1 2 ? ? ? ? ? ? ?'."""

    if isinstance(value, str):
        tokens = value.replace(",", " ").replace("/", " ").replace("|", " ").split()
        pattern: List[Optional[int]] = []
        for token in tokens:
            normalized = token.strip().lower()
            if normalized in {"?", "*", "x", "_", "-"}:
                pattern.append(None)
            else:
                pattern.append(int(normalized))
    else:
        pattern = [None if item is None else int(item) for item in value]
    if len(pattern) != 9:
        raise ValueError("Partial goal pattern must contain exactly 9 entries.")
    known = [item for item in pattern if item is not None]
    if any(item < 0 or item > 8 for item in known):
        raise ValueError("Known partial goal values must be in range 0..8.")
    if len(set(known)) != len(known):
        raise ValueError("Known partial goal values must not be duplicated.")
    return tuple(pattern)


def random_partial_goal_pattern(
    goal: State = GOAL_STATE,
    reveal_count: int = 2,
    seed: Optional[int] = None,
) -> Tuple[Optional[int], ...]:
    """Reveal a deterministic random subset of goal positions for partial-observation demos."""

    rng = random.Random(seed)
    count = max(1, min(8, reveal_count))
    positions = rng.sample(range(9), count)
    return tuple(goal[index] if index in positions else None for index in range(9))


def partial_goal_string(pattern: Optional[Tuple[Optional[int], ...]] = None) -> str:
    pattern = pattern or PARTIAL_GOAL_PATTERN
    rows = []
    for start in range(0, 9, BOARD_SIZE):
        rows.append(" ".join("?" if value is None else str(value) for value in pattern[start : start + BOARD_SIZE]))
    return "\n".join(rows)


def partial_goal_mismatch(state: State, pattern: Tuple[Optional[int], ...] = PARTIAL_GOAL_PATTERN) -> int:
    return sum(1 for index, value in enumerate(pattern) if value is not None and state[index] != value)


def algorithm_problem_model(
    algorithm: str,
    lang: str = "en",
    partial_goal_pattern: Optional[Tuple[Optional[int], ...]] = None,
) -> List[Dict[str, str]]:
    """Return the academic problem formulation that matches the selected algorithm name."""

    canonical = normalize_algorithm(algorithm)
    partial_goal = partial_goal_string(partial_goal_pattern)
    if lang == "vi":
        models = {
            "AND-OR Search": [
                ("Dạng bài toán", "Môi trường không xác định kết quả hành động: agent chọn action ở OR node, môi trường sinh nhiều outcome ở AND node."),
                ("Agent biết gì", "Biết Start, Goal đầy đủ và action model có thể lệch outcome."),
                ("Goal/Quan sát", f"Goal đầy đủ:\n{board_string(GOAL_STATE)}"),
                ("Cách giải", "Tạo conditional plan: IF outcome này THEN tiếp tục nhánh tương ứng. Không phải path đơn như BFS/A*."),
            ],
            "No Observation Search": [
                ("Dạng bài toán", "Không quan sát: agent không biết state thật sau khi hành động, chỉ cập nhật một belief state."),
                ("Agent biết gì", "Biết Goal đầy đủ và một tập Start có thể xảy ra; không nhận percept sau mỗi bước."),
                ("Goal/Quan sát", f"Goal đầy đủ nhưng state hiện tại bị ẩn:\n{board_string(GOAL_STATE)}"),
                ("Cách giải", "Dùng ý tưởng các thuật toán nhóm trước trên belief frontier: chọn action làm giảm tổng h(n) của toàn bộ belief state."),
            ],
            "Partially Observable Search": [
                ("Dạng bài toán", "Biết một phần: agent chỉ quan sát một phần trạng thái hoặc một phần mục tiêu."),
                ("Agent biết gì", "Biết Start đại diện, observation gồm vị trí ô trống/các ô kề và một mẫu goal một phần."),
                ("Goal/Quan sát", f"Goal quan sát được:\n{partial_goal}"),
                ("Cách giải", "Lọc belief theo observation rồi dùng h(n) của nhóm informed search để chọn representative action."),
            ],
            "Online Search": [
                ("Dạng bài toán", "Online search: agent biết state hiện tại qua sensor nhưng chưa duyệt/biết toàn bộ không gian trước khi đi."),
                ("Agent biết gì", "Biết Start hiện tại, Goal đầy đủ, action hợp lệ tại state đang đứng và học H(s) trong lúc di chuyển."),
                ("Goal/Quan sát", f"Goal đầy đủ:\n{board_string(GOAL_STATE)}"),
                ("Cách giải", "LRTA*: cập nhật H(current), rồi chọn neighbor có 1 + H(neighbor) nhỏ nhất."),
            ],
        }
        default_rows = [
            ("Dạng bài toán", f"{canonical} trên 8-Puzzle chuẩn."),
            ("Agent biết gì", "Biết Start, Goal, action model, cost và trạng thái quan sát được."),
            ("Goal/Quan sát", f"Goal đầy đủ:\n{board_string(GOAL_STATE)}"),
            ("Cách giải", PRIORITY_RULES.get(canonical, "")),
        ]
        selected = models.get(canonical, default_rows)
        return [{"Mục": key, "Định nghĩa": value} for key, value in selected]

    models_en = {
        "AND-OR Search": [
            ("Problem type", "Nondeterministic actions: the agent chooses at OR nodes and the environment returns multiple AND outcomes."),
            ("Known information", "Full Start, full Goal, and an action model with possible slipped outcomes."),
            ("Goal/Observation", f"Full goal:\n{board_string(GOAL_STATE)}"),
            ("How it solves", "Build a conditional plan: IF this outcome occurs THEN continue with the matching branch."),
        ],
        "No Observation Search": [
            ("Problem type", "No observation: the true current board is hidden after actions; the agent updates a belief state."),
            ("Known information", "Full Goal and a set of possible starts; no percept is received after each action."),
            ("Goal/Observation", f"Full goal is known, current state is hidden:\n{board_string(GOAL_STATE)}"),
            ("How it solves", "Apply earlier search ideas over a belief frontier by choosing the action that lowers total h(n)."),
        ],
        "Partially Observable Search": [
            ("Problem type", "Partial knowledge: the agent observes only part of the state or part of the goal."),
            ("Known information", "A representative Start, blank/adjacent-tile observations, and a partial goal template."),
            ("Goal/Observation", f"Observed goal template:\n{partial_goal}"),
            ("How it solves", "Filter the belief state by observation, then use informed-search h(n) to select a representative action."),
        ],
        "Online Search": [
            ("Problem type", "Online search: the agent senses only the current state and learns while moving."),
            ("Known information", "Current Start, full Goal, legal actions at the current state, and learned H(s)."),
            ("Goal/Observation", f"Full goal:\n{board_string(GOAL_STATE)}"),
            ("How it solves", "LRTA*: update H(current), then move to the neighbor minimizing 1 + H(neighbor)."),
        ],
    }
    selected_en = models_en.get(
        canonical,
        [
            ("Problem type", f"{canonical} on the standard 8-puzzle."),
            ("Known information", "Start, Goal, action model, step cost, and observable current board."),
            ("Goal/Observation", f"Full goal:\n{board_string(GOAL_STATE)}"),
            ("How it solves", PRIORITY_RULES.get(canonical, "")),
        ],
    )
    return [{"Item": key, "Definition": value} for key, value in selected_en]


def peas_model(algorithm: Optional[str] = None, lang: str = "en") -> List[Dict[str, str]]:
    """Return the PEAS formulation for the 8-puzzle agent or a selected algorithm."""

    canonical = normalize_algorithm(algorithm) if algorithm else "8-Puzzle Agent"
    info = ALGORITHM_INFO.get(canonical, {})
    group = info.get("group", "Standard 8-Puzzle")
    if lang == "vi":
        group_environment = {
            "Uninformed Search": "Môi trường 8-Puzzle chuẩn: deterministic, fully observable, bảng 3x3, cost mỗi bước bằng 1.",
            "Informed Search": "Môi trường 8-Puzzle chuẩn kèm hàm heuristic h(n) để ước lượng khoảng cách tới Goal.",
            "Local Search": "Không gian trạng thái 8-Puzzle nhìn như landscape theo h(n); thuật toán chỉ giữ một hoặc vài trạng thái ứng viên.",
            "Complex Environments": "Mô hình mở rộng học thuật: có belief state, quan sát thiếu, online learning hoặc hành động không xác định.",
            "Constraint Satisfaction Problems": "Mô hình CSP planning theo thời gian với biến X[t][p], A[t] và ràng buộc Initial/Goal/AllDifferent/Transition.",
            "Adversarial / Stochastic Search": "Mô hình game/stochastic mở rộng: MAX, MIN hoặc Chance node; không phải môi trường chuẩn của 8-Puzzle.",
        }
        return [
            {
                "Algorithm": canonical,
                "PEAS": "Performance (Hiệu suất)",
                "Definition": (
                    f"{canonical}: đạt Goal nếu thuật toán là solver phù hợp; giảm cost/path length, expanded/generated, "
                    f"runtime và memory. Complete: {info.get('complete', 'N/A')}. Optimal: {info.get('optimal', 'N/A')}."
                ),
            },
            {
                "Algorithm": canonical,
                "PEAS": "Environment (Môi trường)",
                "Definition": group_environment.get(group, "Môi trường 8-Puzzle 3x3 với trạng thái tuple 9 phần tử và goal cố định."),
            },
            {
                "Algorithm": canonical,
                "PEAS": "Actuators (Bộ chấp hành)",
                "Definition": (
                    "Với solver chuẩn: di chuyển ô trống Up/Down/Left/Right nếu hợp lệ. "
                    "Với mô phỏng học thuật: chọn action, cập nhật belief/constraint/utility theo mô hình của thuật toán."
                ),
            },
            {
                "Algorithm": canonical,
                "PEAS": "Sensors (Cảm biến)",
                "Definition": (
                    "Quan sát board 3x3, vị trí ô trống, action hợp lệ, Goal test, g(n), h(n), f(n) nếu có; "
                    "riêng nhóm belief/game/CSP quan sát thêm belief, constraints, utility hoặc probability."
                ),
            },
        ]

    group_environment = {
        "Uninformed Search": "The standard deterministic, fully observable 3x3 8-puzzle with unit step cost.",
        "Informed Search": "The standard 8-puzzle plus h(n), an admissible estimate of remaining cost.",
        "Local Search": "The 8-puzzle state space viewed as an h(n) landscape; only one or a small population of candidates is kept.",
        "Complex Environments": "An educational extension with belief states, partial/no observation, online learning, or nondeterministic actions.",
        "Constraint Satisfaction Problems": "A time-indexed planning CSP with X[t][p], A[t], Initial, Goal, AllDifferent, and Transition constraints.",
        "Adversarial / Stochastic Search": "An educational game/stochastic extension with MAX, MIN, or Chance nodes, not the standard puzzle environment.",
    }
    return [
        {
            "Algorithm": canonical,
            "PEAS": "Performance",
            "Definition": (
                f"{canonical}: reach the goal when the algorithm is a suitable solver; minimize path cost, expanded/generated nodes, "
                f"runtime, and memory. Complete: {info.get('complete', 'N/A')}. Optimal: {info.get('optimal', 'N/A')}."
            ),
        },
        {
            "Algorithm": canonical,
            "PEAS": "Environment",
            "Definition": group_environment.get(group, "A 3x3 8-puzzle state represented as a 9-tuple with a fixed goal."),
        },
        {
            "Algorithm": canonical,
            "PEAS": "Actuators",
            "Definition": (
                "For standard solvers, move the blank tile Up/Down/Left/Right when legal. "
                "For educational simulations, choose/update actions, beliefs, constraints, utilities, or probabilities."
            ),
        },
        {
            "Algorithm": canonical,
            "PEAS": "Sensors",
            "Definition": (
                "Observe the board, blank position, legal actions, goal test, and g(n), h(n), f(n) when relevant; "
                "belief/game/CSP demos also observe beliefs, constraints, utilities, or probabilities."
            ),
        },
    ]


def reconstruct_node_path(node: SearchNode) -> Tuple[List[State], List[str]]:
    nodes: List[SearchNode] = []
    current: Optional[SearchNode] = node
    while current is not None:
        nodes.append(current)
        current = current.parent
    nodes.reverse()
    path = [item.state for item in nodes]
    actions = [item.action for item in nodes[1:]]
    return path, actions


def _states_from_items(items: Iterable[Any]) -> List[State]:
    states: List[State] = []
    for item in items:
        if isinstance(item, SearchNode):
            states.append(item.state)
        elif isinstance(item, tuple) and len(item) == 9 and set(item) == set(range(9)):
            states.append(item)
        elif isinstance(item, tuple) and item and isinstance(item[-1], SearchNode):
            states.append(item[-1].state)
    return states


def summarize_states(items: Iterable[Any], limit: int = 5) -> str:
    states = _states_from_items(items)
    if not states:
        return ""
    shown = states[:limit]
    text = "\n---\n".join(board_string(state) for state in shown)
    if len(states) > limit:
        text += f"\n... (+{len(states) - limit} more)"
    return text


def _trace_value(value: Optional[Any]) -> Any:
    return "" if value is None else value


def add_trace(
    trace_rows: List[Dict[str, Any]],
    config: TraceConfig,
    step: int,
    algorithm: str,
    node: Any,
    action: str,
    depth: Any,
    g: Optional[int],
    h: Optional[int],
    f: Optional[int],
    frontier: Iterable[Any],
    reached: Iterable[Any],
    note: str,
    priority_rule: str = "",
    selection_key: Any = "",
    generated_children: Optional[int] = None,
    skipped_states: Optional[int] = None,
) -> None:
    if len(trace_rows) >= config.max_trace_rows:
        return
    if isinstance(node, SearchNode):
        node_text = board_string(node.state)
    elif isinstance(node, tuple) and len(node) == 9 and set(node) == set(range(9)):
        node_text = board_string(node)
    else:
        node_text = str(node)
    trace_rows.append(
        {
            "Step": step,
            "Algorithm": algorithm,
            "Node": node_text,
            "Action": action,
            "Depth": depth,
            "g": _trace_value(g),
            "h": _trace_value(h),
            "f": _trace_value(f),
            "Priority Rule": priority_rule or PRIORITY_RULES.get(algorithm, ""),
            "Selection Key": _trace_value(selection_key),
            "Generated Children": _trace_value(generated_children),
            "Skipped States": _trace_value(skipped_states),
            "Frontier": summarize_states(frontier, config.frontier_preview),
            "Reached": summarize_states(reached, config.reached_preview),
            "Decision/Note": note,
        }
    )


def _memory_estimate_kb(reached_count: int, max_frontier: int) -> float:
    return ((reached_count + max_frontier) * 9 * 28) / 1024


def _finish_result(
    *,
    algorithm: str,
    start: State,
    goal: State,
    found: bool,
    terminal_node: Optional[SearchNode],
    expanded: int,
    generated: int,
    max_frontier: int,
    reached_count: int,
    trace_rows: List[Dict[str, Any]],
    started_at: float,
    message: str,
) -> SearchResult:
    path: List[State] = []
    actions: List[str] = []
    path_cost: Optional[int] = None
    if found and terminal_node is not None:
        path, actions = reconstruct_node_path(terminal_node)
        path_cost = len(actions)
    info = ALGORITHM_INFO[algorithm]
    return SearchResult(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=found,
        path=path,
        actions=actions,
        path_cost=path_cost,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        reached_count=reached_count,
        runtime_ms=(time.perf_counter() - started_at) * 1000,
        memory_estimate_kb=_memory_estimate_kb(reached_count, max_frontier),
        trace_rows=trace_rows,
        message=message,
        optimal=info["optimal"],
        complete=info["complete"],
        notes=f"Group: {info['group']}",
    )


def _unsolvable_result(algorithm: str, start: State, goal: State, started_at: float) -> SearchResult:
    return SearchResult(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=False,
        runtime_ms=(time.perf_counter() - started_at) * 1000,
        message="Start state is not solvable relative to the goal.",
        optimal=ALGORITHM_INFO[algorithm]["optimal"],
        complete=ALGORITHM_INFO[algorithm]["complete"],
        notes=f"Group: {ALGORITHM_INFO[algorithm]['group']}",
    )


def _bfs(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "BFS"
    started_at = time.perf_counter()
    root = SearchNode(start, h=heuristic(start))
    frontier: Deque[SearchNode] = deque([root])
    reached: Dict[State, int] = {start: 0}
    reached_order = [start]
    expanded = 0
    generated = 1
    max_frontier = 1
    step = 0
    trace_rows: List[Dict[str, Any]] = []

    while frontier and expanded < config.max_expansions:
        node = frontier.popleft()
        step += 1
        is_goal = node.state == goal
        new_children: List[SearchNode] = []
        skipped = 0
        if not is_goal:
            for action, next_state in neighbors(node.state):
                if next_state in reached:
                    skipped += 1
                    continue
                new_children.append(SearchNode(next_state, node, action, node.g + 1, node.depth + 1, heuristic(next_state)))
        if node.state == goal:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                node.depth,
                node.g,
                node.h,
                None,
                frontier,
                reached_order,
                "Pop shallowest node from FIFO frontier; goal test succeeds.",
                selection_key=f"depth={node.depth}; fifo_pop={step}",
                generated_children=0,
                skipped_states=0,
            )
            return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=node, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message="Goal found.")
        expanded += 1
        for child in new_children:
            frontier.append(child)
            reached[child.state] = child.g
            reached_order.append(child.state)
            generated += 1
        max_frontier = max(max_frontier, len(frontier))
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            node,
            node.action,
            node.depth,
            node.g,
            node.h,
            None,
            frontier,
            reached_order,
            "Pop shallowest node, expand it, then append unseen children to the FIFO frontier.",
            selection_key=f"depth={node.depth}; fifo_pop={step}",
            generated_children=len(new_children),
            skipped_states=skipped,
        )

    message = "Stopped by expansion limit." if frontier else "Frontier exhausted."
    return _finish_result(algorithm=algorithm, start=start, goal=goal, found=False, terminal_node=None, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message=message)


def _dfs(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "DFS"
    started_at = time.perf_counter()
    root = SearchNode(start, h=heuristic(start))
    frontier: List[SearchNode] = [root]
    reached: Dict[State, int] = {start: 0}
    reached_order = [start]
    expanded = 0
    generated = 1
    max_frontier = 1
    step = 0
    trace_rows: List[Dict[str, Any]] = []

    while frontier and expanded < config.max_expansions:
        node = frontier.pop()
        step += 1
        is_goal = node.state == goal
        new_children: List[SearchNode] = []
        skipped = 0
        if not is_goal and node.depth < config.dfs_depth_limit:
            for action, next_state in reversed(neighbors(node.state)):
                if next_state in reached:
                    skipped += 1
                    continue
                new_children.append(SearchNode(next_state, node, action, node.g + 1, node.depth + 1, heuristic(next_state)))
        elif not is_goal:
            skipped = len(neighbors(node.state))
        if node.state == goal:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                node.depth,
                node.g,
                node.h,
                None,
                frontier,
                reached_order,
                "Pop deepest node from LIFO frontier; goal test succeeds.",
                selection_key=f"depth={node.depth}; lifo_pop={step}",
                generated_children=0,
                skipped_states=0,
            )
            return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=node, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message="Goal found.")
        expanded += 1
        if node.depth >= config.dfs_depth_limit:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                node.depth,
                node.g,
                node.h,
                None,
                frontier,
                reached_order,
                "Pop deepest node; depth limit prevents expansion.",
                selection_key=f"depth={node.depth}; lifo_pop={step}",
                generated_children=0,
                skipped_states=skipped,
            )
            continue
        for child in new_children:
            frontier.append(child)
            reached[child.state] = child.g
            reached_order.append(child.state)
            generated += 1
        max_frontier = max(max_frontier, len(frontier))
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            node,
            node.action,
            node.depth,
            node.g,
            node.h,
            None,
            frontier,
            reached_order,
            "Pop deepest node, expand it, then push unseen children onto the LIFO frontier.",
            selection_key=f"depth={node.depth}; lifo_pop={step}",
            generated_children=len(new_children),
            skipped_states=skipped,
        )

    message = "Stopped by expansion/depth limit." if frontier else "Frontier exhausted."
    return _finish_result(algorithm=algorithm, start=start, goal=goal, found=False, terminal_node=None, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message=message)


def _priority_search(
    algorithm: str,
    start: State,
    goal: State,
    heuristic: Callable[[State], int],
    config: TraceConfig,
) -> SearchResult:
    started_at = time.perf_counter()
    root = SearchNode(start, h=heuristic(start))
    counter = 0

    def priority_tuple(node: SearchNode) -> Tuple[int, int, int, SearchNode]:
        if algorithm == "UCS":
            return (node.g, node.h, next_counter(), node)
        if algorithm == "Greedy":
            return (node.h, node.g, next_counter(), node)
        return (node.f, node.h, next_counter(), node)

    def next_counter() -> int:
        nonlocal counter
        counter += 1
        return counter

    frontier: List[Tuple[int, int, int, SearchNode]] = [priority_tuple(root)]
    best_g: Dict[State, int] = {start: 0}
    reached_order = [start]
    expanded = 0
    generated = 1
    max_frontier = 1
    step = 0
    trace_rows: List[Dict[str, Any]] = []

    while frontier and expanded < config.max_expansions:
        _, _, _, node = heapq.heappop(frontier)
        if node.g != best_g.get(node.state):
            continue
        step += 1
        f_value = node.g if algorithm == "UCS" else node.h if algorithm == "Greedy" else node.f
        is_goal = node.state == goal
        new_children: List[SearchNode] = []
        skipped = 0
        if not is_goal:
            for action, next_state in neighbors(node.state):
                next_g = node.g + 1
                if next_g >= best_g.get(next_state, math.inf):
                    skipped += 1
                    continue
                new_children.append(SearchNode(next_state, node, action, next_g, node.depth + 1, heuristic(next_state)))
        if algorithm == "UCS":
            selection_key = f"g={node.g}; h={node.h}"
        elif algorithm == "Greedy":
            selection_key = f"h={node.h}; g={node.g}"
        else:
            selection_key = f"f={node.f}; g={node.g}; h={node.h}"
        if node.state == goal:
            frontier_nodes: Iterable[Any] = ()
            if len(trace_rows) < config.max_trace_rows:
                frontier_nodes = [entry[-1] for entry in sorted(frontier)]
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                node.depth,
                node.g,
                node.h,
                f_value,
                frontier_nodes,
                reached_order,
                f"Pop best priority node for {algorithm}; goal test succeeds.",
                selection_key=selection_key,
                generated_children=0,
                skipped_states=0,
            )
            return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=node, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(best_g), trace_rows=trace_rows, started_at=started_at, message="Goal found.")
        expanded += 1
        for child in new_children:
            best_g[child.state] = child.g
            reached_order.append(child.state)
            heapq.heappush(frontier, priority_tuple(child))
            generated += 1
        max_frontier = max(max_frontier, len(frontier))
        frontier_nodes = ()
        if len(trace_rows) < config.max_trace_rows:
            frontier_nodes = [entry[-1] for entry in sorted(frontier)]
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            node,
            node.action,
            node.depth,
            node.g,
            node.h,
            f_value,
            frontier_nodes,
            reached_order,
            f"Pop best priority node for {algorithm}, expand it, then push improved children.",
            selection_key=selection_key,
            generated_children=len(new_children),
            skipped_states=skipped,
        )

    message = "Stopped by expansion limit." if frontier else "Frontier exhausted."
    return _finish_result(algorithm=algorithm, start=start, goal=goal, found=False, terminal_node=None, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(best_g), trace_rows=trace_rows, started_at=started_at, message=message)


def _ids(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "IDS"
    started_at = time.perf_counter()
    expanded = 0
    generated = 0
    max_frontier = 0
    total_reached: Set[State] = set()
    trace_rows: List[Dict[str, Any]] = []
    step = 0

    for limit in range(config.ids_max_depth + 1):
        root = SearchNode(start, h=heuristic(start))
        frontier: List[Tuple[SearchNode, Set[State]]] = [(root, {start})]
        generated += 1
        iteration_reached: List[State] = [start]
        total_reached.add(start)
        max_frontier = max(max_frontier, len(frontier))
        while frontier and expanded < config.max_expansions:
            node, path_set = frontier.pop()
            step += 1
            is_goal = node.state == goal
            new_children: List[SearchNode] = []
            skipped = 0
            if not is_goal and node.depth < limit:
                for action, next_state in reversed(neighbors(node.state)):
                    if next_state in path_set:
                        skipped += 1
                        continue
                    new_children.append(SearchNode(next_state, node, action, node.g + 1, node.depth + 1, heuristic(next_state)))
            elif not is_goal:
                skipped = len(neighbors(node.state))
            if node.state == goal:
                add_trace(
                    trace_rows,
                    config,
                    step,
                    algorithm,
                    node,
                    node.action,
                    f"{node.depth}/{limit}",
                    node.g,
                    node.h,
                    None,
                    [item[0] for item in frontier],
                    iteration_reached,
                    f"Depth-limited DFS at limit {limit}; goal test succeeds.",
                    selection_key=f"depth={node.depth}; limit={limit}",
                    generated_children=0,
                    skipped_states=0,
                )
                return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=node, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(total_reached), trace_rows=trace_rows, started_at=started_at, message=f"Goal found at depth limit {limit}.")
            if node.depth >= limit:
                add_trace(
                    trace_rows,
                    config,
                    step,
                    algorithm,
                    node,
                    node.action,
                    f"{node.depth}/{limit}",
                    node.g,
                    node.h,
                    None,
                    [item[0] for item in frontier],
                    iteration_reached,
                    f"Depth-limited DFS at limit {limit}; depth limit prevents expansion.",
                    selection_key=f"depth={node.depth}; limit={limit}",
                    generated_children=0,
                    skipped_states=skipped,
                )
                continue
            expanded += 1
            for child in new_children:
                child_path = set(path_set)
                child_path.add(child.state)
                frontier.append((child, child_path))
                iteration_reached.append(child.state)
                total_reached.add(child.state)
                generated += 1
            max_frontier = max(max_frontier, len(frontier))
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                f"{node.depth}/{limit}",
                node.g,
                node.h,
                None,
                [item[0] for item in frontier],
                iteration_reached,
                f"Depth-limited DFS at limit {limit}; expanded and pushed children.",
                selection_key=f"depth={node.depth}; limit={limit}",
                generated_children=len(new_children),
                skipped_states=skipped,
            )
        if expanded >= config.max_expansions:
            break

    message = "Stopped by expansion limit." if expanded >= config.max_expansions else f"No solution within IDS depth {config.ids_max_depth}."
    return _finish_result(algorithm=algorithm, start=start, goal=goal, found=False, terminal_node=None, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(total_reached), trace_rows=trace_rows, started_at=started_at, message=message)


def _ida_star(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "IDA*"
    started_at = time.perf_counter()
    threshold = heuristic(start)
    expanded = 0
    generated = 1
    max_frontier = 1
    reached: Set[State] = {start}
    reached_order = [start]
    trace_rows: List[Dict[str, Any]] = []
    step = 0
    stopped = False

    def dfs(node: SearchNode, bound: int, path_set: Set[State]) -> Tuple[Optional[SearchNode], float]:
        nonlocal expanded, generated, max_frontier, step, stopped
        node_f = node.f
        step += 1
        if node_f > bound:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                node.depth,
                node.g,
                node.h,
                node_f,
                (),
                reached_order,
                f"Prune before expansion because f(n)={node_f} exceeds threshold {bound}.",
                selection_key=f"f={node_f}; threshold={bound}; pruned=True",
                generated_children=0,
                skipped_states=0,
            )
            return None, node_f
        if node.state == goal:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                node.depth,
                node.g,
                node.h,
                node_f,
                (),
                reached_order,
                f"IDA* threshold {bound}; goal test succeeds.",
                selection_key=f"f={node_f}; threshold={bound}",
                generated_children=0,
                skipped_states=0,
            )
            return node, node_f
        if expanded >= config.max_expansions:
            stopped = True
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                node.depth,
                node.g,
                node.h,
                node_f,
                (),
                reached_order,
                f"IDA* threshold {bound}; expansion limit prevents child generation.",
                selection_key=f"f={node_f}; threshold={bound}; stopped=True",
                generated_children=0,
                skipped_states=0,
            )
            return None, math.inf
        neighbor_items = neighbors(node.state)
        candidate_nodes = [
            SearchNode(next_state, node, action, node.g + 1, node.depth + 1, heuristic(next_state))
            for action, next_state in neighbor_items
            if next_state not in path_set
        ]
        candidate_nodes.sort(key=lambda item: (item.f, item.h))
        skipped = len(neighbor_items) - len(candidate_nodes)
        generated += len(candidate_nodes)
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            node,
            node.action,
            node.depth,
            node.g,
            node.h,
            node_f,
            candidate_nodes,
            reached_order,
            f"IDA* threshold {bound}; expanded node and ordered children by f(n).",
            selection_key=f"f={node_f}; threshold={bound}",
            generated_children=len(candidate_nodes),
            skipped_states=skipped,
        )
        expanded += 1
        min_overrun = math.inf
        max_frontier = max(max_frontier, len(path_set) + len(candidate_nodes))
        for child in candidate_nodes:
            reached.add(child.state)
            reached_order.append(child.state)
            path_set.add(child.state)
            found_node, next_bound = dfs(child, bound, path_set)
            path_set.remove(child.state)
            if found_node is not None:
                return found_node, next_bound
            min_overrun = min(min_overrun, next_bound)
            if stopped:
                return None, math.inf
        return None, min_overrun

    for _ in range(config.ida_max_iterations):
        root = SearchNode(start, h=heuristic(start))
        found, next_threshold = dfs(root, threshold, {start})
        if found is not None:
            return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=found, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message=f"Goal found with threshold {threshold}.")
        if stopped or next_threshold == math.inf:
            break
        threshold = int(next_threshold)

    message = "Stopped by expansion/iteration limit." if stopped else "No solution within IDA* thresholds."
    return _finish_result(algorithm=algorithm, start=start, goal=goal, found=False, terminal_node=None, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message=message)


def _hill_climbing(
    algorithm: str,
    start: State,
    goal: State,
    heuristic: Callable[[State], int],
    config: TraceConfig,
) -> SearchResult:
    started_at = time.perf_counter()
    rng = random.Random(config.seed)
    expanded = 0
    generated = 1
    max_frontier = 1
    reached: Set[State] = {start}
    reached_order = [start]
    trace_rows: List[Dict[str, Any]] = []
    step = 0
    best_terminal = SearchNode(start, h=heuristic(start))

    def choose_next(current: SearchNode, candidate_nodes: List[SearchNode]) -> Optional[SearchNode]:
        improving = [item for item in candidate_nodes if item.h < current.h]
        if not improving:
            return None
        if algorithm == "Simple Hill Climbing":
            return improving[0]
        if algorithm == "Stochastic Hill Climbing":
            return rng.choice(improving)
        return min(improving, key=lambda item: (item.h, item.g))

    restart_count = config.random_restarts if algorithm == "Random-Restart Hill Climbing" else 0

    def restart_node(restart_index: int) -> SearchNode:
        nonlocal generated
        current = SearchNode(start, h=heuristic(start))
        if restart_index == 0:
            return current
        previous: Optional[State] = None
        walk_length = min(30, 4 + restart_index)
        for _ in range(walk_length):
            options = [(action, nxt) for action, nxt in neighbors(current.state) if nxt != previous]
            if not options:
                options = neighbors(current.state)
            action, next_state = rng.choice(options)
            previous = current.state
            current = SearchNode(
                next_state,
                current,
                f"Restart walk: {action}",
                current.g + 1,
                current.depth + 1,
                heuristic(next_state),
            )
            generated += 1
        return current

    for restart_index in range(restart_count + 1):
        current = restart_node(restart_index)
        local_path_seen: Set[State] = set(reconstruct_node_path(current)[0])
        if current.h < best_terminal.h:
            best_terminal = current
        for local_step in range(config.local_max_steps):
            step += 1
            reached.add(current.state)
            reached_order.append(current.state)
            if current.state == goal:
                return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=current, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message=f"Goal found after restart {restart_index}.")
            neighbor_items = neighbors(current.state)
            candidate_nodes = [
                SearchNode(next_state, current, action, current.g + 1, current.depth + 1, heuristic(next_state))
                for action, next_state in neighbor_items
                if next_state not in local_path_seen
            ]
            skipped = len(neighbor_items) - len(candidate_nodes)
            generated += len(candidate_nodes)
            expanded += 1
            max_frontier = max(max_frontier, len(candidate_nodes))
            selected = choose_next(current, candidate_nodes)
            if selected is None:
                add_trace(
                    trace_rows,
                    config,
                    step,
                    algorithm,
                    current,
                    current.action,
                    current.depth,
                    current.g,
                    current.h,
                    current.h,
                    candidate_nodes,
                    reached_order,
                    f"Restart {restart_index}: no improving neighbor; local optimum or plateau.",
                    selection_key=f"current_h={current.h}; selected=None",
                    generated_children=len(candidate_nodes),
                    skipped_states=skipped,
                )
                break
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                current,
                current.action,
                current.depth,
                current.g,
                current.h,
                selected.h,
                candidate_nodes,
                reached_order,
                f"Restart {restart_index}: move to {selected.action} with h={selected.h}.",
                selection_key=f"current_h={current.h}; selected_h={selected.h}; restart={restart_index}",
                generated_children=len(candidate_nodes),
                skipped_states=skipped,
            )
            current = selected
            local_path_seen.add(current.state)
            reached.add(current.state)
            if current.h < best_terminal.h:
                best_terminal = current
            if expanded >= config.max_expansions:
                break
        if expanded >= config.max_expansions:
            break

    return _finish_result(algorithm=algorithm, start=start, goal=goal, found=False, terminal_node=best_terminal, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message=f"Stopped without reaching goal. Best h={best_terminal.h}.")


def _local_beam_search(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "Local Beam Search"
    started_at = time.perf_counter()
    root = SearchNode(start, h=heuristic(start))
    beams = [root]
    reached: Set[State] = {start}
    reached_order = [start]
    expanded = 0
    generated = len(beams)
    max_frontier = len(beams)
    trace_rows: List[Dict[str, Any]] = []

    for step in range(1, config.local_max_steps + 1):
        best = min(beams, key=lambda item: (item.h, item.g))
        for node in beams:
            if node.state == goal:
                add_trace(
                    trace_rows,
                    config,
                    step,
                    algorithm,
                    node,
                    f"Beam step {step}",
                    step - 1,
                    node.g,
                    node.h,
                    node.h,
                    beams,
                    reached_order,
                    f"Current beam already contains the goal; best h={best.h}.",
                    selection_key=f"top_k={config.beam_width}; best_h={best.h}; beam_size={len(beams)}",
                    generated_children=0,
                    skipped_states=0,
                )
                return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=node, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message="Goal found in current beam.")
        if expanded >= config.max_expansions:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                best,
                f"Beam step {step}",
                step - 1,
                best.g,
                best.h,
                best.h,
                beams,
                reached_order,
                f"Expansion limit prevents expanding current beam; best h={best.h}.",
                selection_key=f"top_k={config.beam_width}; best_h={best.h}; beam_size={len(beams)}",
                generated_children=0,
                skipped_states=0,
            )
            break
        candidates: Dict[State, SearchNode] = {}
        duplicate_skips = 0
        for node in beams:
            expanded += 1
            for action, next_state in neighbors(node.state):
                child = SearchNode(next_state, node, action, node.g + 1, node.depth + 1, heuristic(next_state))
                old = candidates.get(next_state)
                if old is None or (child.h, child.g) < (old.h, old.g):
                    candidates[next_state] = child
                    if old is not None:
                        duplicate_skips += 1
                else:
                    duplicate_skips += 1
                reached.add(next_state)
                reached_order.append(next_state)
        if not candidates:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                best,
                f"Beam step {step}",
                step - 1,
                best.g,
                best.h,
                best.h,
                (),
                reached_order,
                f"Expanded current beam but produced no candidates; best h={best.h}.",
                selection_key=f"top_k={config.beam_width}; best_h={best.h}; beam_size={len(beams)}",
                generated_children=0,
                skipped_states=duplicate_skips,
            )
            break
        generated += len(candidates)
        sorted_candidates = sorted(candidates.values(), key=lambda item: (item.h, item.g))
        next_beams = sorted_candidates[: max(1, config.beam_width)]
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            best,
            f"Beam step {step}",
            step - 1,
            best.g,
            best.h,
            best.h,
            next_beams,
            reached_order,
            f"Expanded current beam, generated {len(candidates)} unique candidates, and kept top-{config.beam_width}.",
            selection_key=f"top_k={config.beam_width}; best_h={best.h}; beam_size={len(beams)}",
            generated_children=len(candidates),
            skipped_states=duplicate_skips,
        )
        for child in sorted_candidates:
            if child.state == goal:
                beams = next_beams
                max_frontier = max(max_frontier, len(sorted_candidates), len(beams))
                return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=child, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message="Goal found among beam candidates.")
        beams = next_beams
        max_frontier = max(max_frontier, len(sorted_candidates), len(beams))

    best = min(beams, key=lambda item: (item.h, item.g))
    return _finish_result(algorithm=algorithm, start=start, goal=goal, found=False, terminal_node=best, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message=f"Stopped without reaching goal. Best h={best.h}.")


def _simulated_annealing(
    start: State,
    goal: State,
    heuristic: Callable[[State], int],
    config: TraceConfig,
) -> SearchResult:
    """Simulated Annealing search with temperature-based acceptance.
    
    Trace structure:
    - Node: current state being evaluated
    - Frontier: candidate neighbors (all possible moves)
    - Reached: all visited states
    - Decision/Note: temperature, acceptance probability, move decision
    """
    algorithm = "Simulated Annealing"
    started_at = time.perf_counter()
    rng = random.Random(config.seed)
    
    current = SearchNode(start, h=heuristic(start))
    best_node = current
    
    reached: Set[State] = {start}
    reached_order: List[State] = [start]
    trace_rows: List[Dict[str, Any]] = []
    
    expanded = 0
    generated = 0
    max_frontier = 0
    
    temperature = config.sa_initial_temp
    step = 0
    
    while temperature > config.sa_min_temp and step < config.sa_max_steps:
        step += 1
        
        if current.state == goal:
            return _finish_result(
                algorithm=algorithm,
                start=start,
                goal=goal,
                found=True,
                terminal_node=current,
                expanded=expanded,
                generated=generated,
                max_frontier=max_frontier,
                reached_count=len(reached),
                trace_rows=trace_rows,
                started_at=started_at,
                message=f"Goal found at step {step}, temperature {temperature:.4f}."
            )
        
        neighbor_list = neighbors(current.state)
        candidate_nodes = [
            SearchNode(next_state, current, action, current.g + 1, current.depth + 1, heuristic(next_state))
            for action, next_state in neighbor_list
        ]
        generated += len(candidate_nodes)
        max_frontier = max(max_frontier, len(candidate_nodes))
        
        if not candidate_nodes:
            break
            
        current_before = current
        next_node = rng.choice(candidate_nodes)
        expanded += 1
        
        delta_h = next_node.h - current_before.h
        accept_prob = 1.0 if delta_h < 0 else math.exp(-delta_h / max(temperature, 1e-10))
        accepted = delta_h < 0 or rng.random() < accept_prob
        
        reached.add(next_node.state)
        reached_order.append(next_node.state)
        
        if accepted:
            if delta_h < 0:
                decision = f"T={temperature:.2f}: accept better move (delta_h={delta_h})"
            else:
                decision = f"T={temperature:.2f}: accept worse move with p={accept_prob:.4f} (delta_h={delta_h})"
            current = next_node
            if current.h < best_node.h:
                best_node = current
        else:
            decision = f"T={temperature:.2f}: reject worse move (delta_h={delta_h}, p={accept_prob:.4f})"
        
        add_trace(
            trace_rows, config, step, algorithm, current_before,
            next_node.action, current_before.depth, current_before.g, current_before.h,
            current_before.h, candidate_nodes, reached_order, decision,
            selection_key=f"candidate_h={next_node.h}; delta_h={delta_h}; T={temperature:.4f}; p={accept_prob:.4f}; accepted={accepted}",
            generated_children=len(candidate_nodes),
            skipped_states=0,
        )
        
        temperature *= config.sa_cooling_rate
    
    message = f"Stopped at T={temperature:.4f}. Best h={best_node.h}."
    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=best_node.state == goal,
        terminal_node=best_node,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        reached_count=len(reached),
        trace_rows=trace_rows,
        started_at=started_at,
        message=message
    )


def _preview_node_for_state(state: State, parent: Optional[SearchNode], action: str, heuristic: Callable[[State], int]) -> SearchNode:
    g = 0 if parent is None else parent.g + 1
    depth = 0 if parent is None else parent.depth + 1
    return SearchNode(state, parent, action, g, depth, heuristic(state))


def _educational_limit(config: TraceConfig, default: int = 30) -> int:
    return max(1, min(default, config.local_max_steps, config.max_expansions))


def _partial_observation(state: State) -> Tuple[int, Tuple[int, ...]]:
    blank = state.index(0)
    adjacent = tuple(sorted(next_state[blank] for _, next_state in neighbors(state)))
    return blank, adjacent


def _apply_action_or_stay(state: State, action: str) -> State:
    return dict(neighbors(state)).get(action, state)


def _complex_environment_search(
    algorithm: str,
    start: State,
    goal: State,
    heuristic: Callable[[State], int],
    config: TraceConfig,
) -> SearchResult:
    if algorithm == "Online Search":
        return _online_lrta_star(start, goal, heuristic, config)
    if algorithm == "No Observation Search":
        return _no_observation_search(start, goal, heuristic, config)
    if algorithm == "Partially Observable Search":
        return _partially_observable_search(start, goal, heuristic, config)
    return _and_or_search(start, goal, heuristic, config)


def _and_or_search(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "AND-OR Search"
    started_at = time.perf_counter()
    current = SearchNode(start, h=heuristic(start))
    reached: Set[State] = {start}
    reached_order = [start]
    trace_rows: List[Dict[str, Any]] = []
    expanded = 0
    generated = 1
    max_frontier = 1
    limit = _educational_limit(config, default=18)

    for step in range(1, limit + 1):
        if current.state == goal:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                current,
                current.action,
                current.depth,
                current.g,
                current.h,
                current.f,
                (),
                reached_order,
                "Representative branch reached the goal; conditional plan succeeds for this observed branch.",
                selection_key=f"or_choice={current.action}; h={current.h}",
                generated_children=0,
                skipped_states=0,
            )
            return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=current, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message="Educational AND-OR representative branch reached the goal.")

        child_nodes = [
            SearchNode(next_state, current, action, current.g + 1, current.depth + 1, heuristic(next_state))
            for action, next_state in neighbors(current.state)
        ]
        child_nodes.sort(key=lambda item: (item.h, item.action))
        if not child_nodes:
            break
        chosen = child_nodes[0]
        outcomes = child_nodes[: min(3, len(child_nodes))]
        generated += len(outcomes)
        expanded += 1
        for outcome in outcomes:
            if outcome.state not in reached:
                reached.add(outcome.state)
                reached_order.append(outcome.state)
        max_frontier = max(max_frontier, len(outcomes))
        outcome_text = "; ".join(f"{item.action}->h={item.h}" for item in outcomes)
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            current,
            f"OR choose {chosen.action}",
            current.depth,
            current.g,
            current.h,
            current.f,
            outcomes,
            reached_order,
            (
                "Nondeterministic problem: Start and Goal are known, but each action can produce several outcomes. "
                "OR node selects the lowest-h action for the representative branch; "
                f"AND node records possible environment outcomes: {outcome_text}."
            ),
            selection_key=f"OR=min_h={chosen.h}; AND_outcomes={len(outcomes)}",
            generated_children=len(outcomes),
            skipped_states=max(0, len(child_nodes) - len(outcomes)),
        )
        current = chosen

    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=False,
        terminal_node=None,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        reached_count=len(reached),
        trace_rows=trace_rows,
        started_at=started_at,
        message="Educational nondeterministic AND-OR demo stopped within the configured bound; output is a conditional-plan trace, not a canonical single-path proof.",
    )


def _belief_seed_states(start: State) -> List[State]:
    seeds = [start]
    for depth, seed in [(2, 3), (4, 5), (6, 7), (8, 11)]:
        candidate = generate_random_state(depth, seed=seed)
        if candidate not in seeds:
            seeds.append(candidate)
    return seeds[:5]


def _no_observation_search(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "No Observation Search"
    started_at = time.perf_counter()
    belief: Set[State] = set(_belief_seed_states(start))
    representative = SearchNode(start, h=heuristic(start))
    trace_rows: List[Dict[str, Any]] = []
    reached_order = list(belief)
    expanded = 0
    generated = len(belief)
    max_frontier = len(belief)
    actions = ["Up", "Down", "Left", "Right"]
    limit = _educational_limit(config, default=12)

    for step in range(1, limit + 1):
        if all(state == goal for state in belief):
            return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=representative, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(set(reached_order)), trace_rows=trace_rows, started_at=started_at, message="All states in the belief set reached the goal.")
        scored_actions: List[Tuple[int, str, Set[State]]] = []
        for action in actions:
            next_belief = {_apply_action_or_stay(state, action) for state in belief}
            score = sum(heuristic(state) for state in next_belief)
            scored_actions.append((score, action, next_belief))
        score, chosen_action, next_belief = min(scored_actions, key=lambda item: (item[0], item[1]))
        before_size = len(belief)
        belief = next_belief
        rep_next_state = _apply_action_or_stay(representative.state, chosen_action)
        if rep_next_state != representative.state:
            representative = SearchNode(rep_next_state, representative, chosen_action, representative.g + 1, representative.depth + 1, heuristic(rep_next_state))
        expanded += before_size
        generated += len(belief)
        max_frontier = max(max_frontier, len(belief))
        reached_order.extend(state for state in belief if state not in reached_order)
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            f"Belief state with {before_size} possible worlds",
            chosen_action,
            step,
            representative.g,
            representative.h,
            score,
            belief,
            reached_order,
            (
                "No observation: the agent knows the full Goal but not the true current board after actions; "
                "one action must be applied to every possible state in the belief frontier. "
                f"Chose {chosen_action} because it minimizes total belief h to {score}."
            ),
            selection_key=f"belief_size={before_size}; action={chosen_action}; total_h={score}",
            generated_children=len(belief),
            skipped_states=0,
        )

    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=False,
        terminal_node=None,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        reached_count=len(set(reached_order)),
        trace_rows=trace_rows,
        started_at=started_at,
        message="Educational no-observation belief search stopped before every possible state reached the goal.",
    )


def _partially_observable_search(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "Partially Observable Search"
    started_at = time.perf_counter()
    pattern = config.partial_goal_pattern or PARTIAL_GOAL_PATTERN
    current = SearchNode(start, h=heuristic(start))
    belief: Set[State] = set(_belief_seed_states(start))
    reached_order = list(belief)
    trace_rows: List[Dict[str, Any]] = []
    expanded = 0
    generated = len(belief)
    max_frontier = len(belief)
    limit = _educational_limit(config, default=18)

    for step in range(1, limit + 1):
        if current.state == goal:
            return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=current, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(set(reached_order)), trace_rows=trace_rows, started_at=started_at, message="Representative actual state reached the goal under partial observation.")
        child_nodes = [
            SearchNode(next_state, current, action, current.g + 1, current.depth + 1, heuristic(next_state))
            for action, next_state in neighbors(current.state)
        ]
        child_nodes.sort(key=lambda item: (partial_goal_mismatch(item.state, pattern), item.h, item.action))
        chosen = child_nodes[0]
        observation = _partial_observation(chosen.state)
        predicted = {_apply_action_or_stay(state, chosen.action) for state in belief}
        filtered = {state for state in predicted if _partial_observation(state) == observation}
        if not filtered:
            filtered = {chosen.state}
        before_size = len(belief)
        belief = filtered
        reached_order.extend(state for state in belief if state not in reached_order)
        expanded += 1
        generated += len(predicted)
        max_frontier = max(max_frontier, len(belief), len(predicted))
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            current,
            chosen.action,
            current.depth,
            current.g,
            current.h,
            chosen.h,
            belief,
            reached_order,
            (
                f"Partial observation uses visible goal template {partial_goal_string(pattern).replace(chr(10), ' / ')}. "
                "Belief keeps states matching blank position and adjacent tiles. "
                f"Observation={observation}; partial_goal_mismatch={partial_goal_mismatch(chosen.state, pattern)}; belief {before_size}->{len(belief)}."
            ),
            selection_key=f"partial_goal_mismatch={partial_goal_mismatch(chosen.state, pattern)}; chosen_h={chosen.h}; observation_blank={observation[0]}; belief_after={len(belief)}",
            generated_children=len(predicted),
            skipped_states=max(0, len(predicted) - len(belief)),
        )
        current = chosen

    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=False,
        terminal_node=None,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        reached_count=len(set(reached_order)),
        trace_rows=trace_rows,
        started_at=started_at,
        message="Educational partially observable search stopped within the configured bound.",
    )


def _online_lrta_star(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "Online Search"
    started_at = time.perf_counter()
    current = SearchNode(start, h=heuristic(start))
    learned_h: Dict[State, float] = {start: float(current.h)}
    visits: Dict[State, int] = {start: 1}
    reached: Set[State] = {start}
    reached_order = [start]
    trace_rows: List[Dict[str, Any]] = []
    expanded = 0
    generated = 1
    max_frontier = 1
    limit = _educational_limit(config, default=80)

    for step in range(1, limit + 1):
        if current.state == goal:
            return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=current, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message="LRTA* reached the goal while learning online.")
        child_nodes = [
            SearchNode(next_state, current, action, current.g + 1, current.depth + 1, heuristic(next_state))
            for action, next_state in neighbors(current.state)
        ]
        for child in child_nodes:
            learned_h.setdefault(child.state, float(child.h))
        generated += len(child_nodes)
        expanded += 1
        max_frontier = max(max_frontier, len(child_nodes))
        old_h = learned_h[current.state]
        best_estimate = min(1.0 + learned_h[child.state] for child in child_nodes)
        learned_h[current.state] = best_estimate
        chosen = min(
            child_nodes,
            key=lambda child: (1.0 + learned_h[child.state], visits.get(child.state, 0), child.h, child.action),
        )
        reached.add(chosen.state)
        reached_order.append(chosen.state)
        visits[chosen.state] = visits.get(chosen.state, 0) + 1
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            current,
            chosen.action,
            current.depth,
            current.g,
            current.h,
            int(best_estimate),
            child_nodes,
            reached_order,
            (
                "Online problem: the agent senses only the current state and learns the map while moving. "
                f"LRTA* updated H(current) from {old_h:.1f} to {best_estimate:.1f}, "
                f"then moved to {chosen.action} with estimated cost {1 + learned_h[chosen.state]:.1f}."
            ),
            selection_key=f"updated_H={best_estimate:.1f}; chosen={chosen.action}; est={1 + learned_h[chosen.state]:.1f}",
            generated_children=len(child_nodes),
            skipped_states=0,
        )
        current = chosen

    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=False,
        terminal_node=None,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        reached_count=len(reached),
        trace_rows=trace_rows,
        started_at=started_at,
        message="Bounded LRTA* online demo stopped before reaching the goal.",
    )


def _csp_search(
    algorithm: str,
    start: State,
    goal: State,
    heuristic: Callable[[State], int],
    config: TraceConfig,
) -> SearchResult:
    if algorithm == "CSP Backtracking":
        return _csp_backtracking(start, goal, heuristic, config)
    if algorithm == "Min-Conflicts":
        return _min_conflicts(start, goal, heuristic, config)
    return _csp_static_demo(algorithm, start, goal, heuristic, config)


def _csp_static_demo(
    algorithm: str,
    start: State,
    goal: State,
    heuristic: Callable[[State], int],
    config: TraceConfig,
) -> SearchResult:
    started_at = time.perf_counter()
    root = SearchNode(start, h=heuristic(start))
    trace_rows: List[Dict[str, Any]] = []
    all_different_ok = len(set(start)) == 9 and len(set(goal)) == 9
    demo_rows = {
        "CSP Definition": [
            ("Variables", "X[t][p] for tile at position p and A[t] for action at time t."),
            ("Domains", "X[t][p] in {0..8}; A[t] in legal blank moves."),
            ("Constraints", "Initial, Goal, AllDifferent, LegalMove, and Transition constraints."),
        ],
        "Constraint Propagation": [
            ("Initial constraint", f"X[0] is fixed to {compact_state(start)}."),
            ("Goal constraint", f"X[T] is fixed to {compact_state(goal)}."),
            ("AllDifferent", "Each tile assignment removes that value from the other eight positions."),
        ],
        "Path Consistency": [
            ("Triple check", "For (X[t], A[t], X[t+1]), every state/action pair needs a supported successor."),
            ("Legal move support", "An action value is removed if no transition can realize it from the blank position."),
            ("Goal support", "A predecessor value is removed if it cannot lead to the goal horizon."),
        ],
        "Global Constraints": [
            ("AllDifferent(start)", f"valid={all_different_ok}"),
            ("AllDifferent(goal)", "valid=True"),
            ("Transition global", "Exactly two positions change between consecutive states: blank and swapped tile."),
        ],
        "Constraint Graph": [
            ("Nodes", "X[0][0..8], A[0], X[1][0..8]"),
            ("Edges", "Initial fixes X[0]; LegalMove connects X[0] to A[0]; Transition connects X[0], A[0], X[1]."),
            ("Hyperedge", "AllDifferent(X[t][0..8]) can be represented as one global hyperedge or a clique."),
        ],
    }[algorithm]
    for step, (label, note) in enumerate(demo_rows, start=1):
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            f"CSP {label}",
            "Model",
            step - 1,
            0,
            root.h,
            root.h,
            [start, goal],
            [start],
            note,
            selection_key=f"{label}; h(start)={root.h}",
            generated_children=0,
            skipped_states=0,
        )
    found = start == goal
    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=found,
        terminal_node=root if found else None,
        expanded=len(demo_rows),
        generated=len(demo_rows),
        max_frontier=2,
        reached_count=1,
        trace_rows=trace_rows,
        started_at=started_at,
        message=f"{algorithm} is an educational CSP-planning demonstration; use CSP Backtracking for a bounded solver demo.",
    )


def _csp_backtracking(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "CSP Backtracking"
    started_at = time.perf_counter()
    trace_rows: List[Dict[str, Any]] = []
    expanded = 0
    generated = 1
    max_frontier = 1
    reached: Set[State] = {start}
    reached_order = [start]
    step = 0
    horizon = max(0, min(config.ids_max_depth, 12))

    def backtrack(node: SearchNode, path_set: Set[State]) -> Optional[SearchNode]:
        nonlocal expanded, generated, max_frontier, step
        step += 1
        if node.state == goal:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                f"{node.depth}/{horizon}",
                node.g,
                node.h,
                node.f,
                (),
                reached_order,
                "CSP planning assignment satisfies the goal constraint.",
                selection_key=f"T={horizon}; depth={node.depth}; goal=True",
                generated_children=0,
                skipped_states=0,
            )
            return node
        if node.depth >= horizon or expanded >= config.max_expansions:
            add_trace(
                trace_rows,
                config,
                step,
                algorithm,
                node,
                node.action,
                f"{node.depth}/{horizon}",
                node.g,
                node.h,
                node.f,
                (),
                reached_order,
                "Backtracking stops this branch because horizon or expansion limit is reached.",
                selection_key=f"T={horizon}; depth={node.depth}; cutoff=True",
                generated_children=0,
                skipped_states=len(neighbors(node.state)),
            )
            return None
        child_nodes = [
            SearchNode(next_state, node, action, node.g + 1, node.depth + 1, heuristic(next_state))
            for action, next_state in neighbors(node.state)
            if next_state not in path_set
        ]
        child_nodes.sort(key=lambda item: (item.h, item.action))
        skipped = len(neighbors(node.state)) - len(child_nodes)
        expanded += 1
        generated += len(child_nodes)
        max_frontier = max(max_frontier, len(child_nodes), len(path_set) + len(child_nodes))
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            node,
            node.action,
            f"{node.depth}/{horizon}",
            node.g,
            node.h,
            node.f,
            child_nodes,
            reached_order,
            "Assign A[t] using legal-move and transition constraints; forward checking removes path repeats.",
            selection_key=f"T={horizon}; MRV=next_action; LCV=lowest_h",
            generated_children=len(child_nodes),
            skipped_states=skipped,
        )
        for child in child_nodes:
            reached.add(child.state)
            reached_order.append(child.state)
            path_set.add(child.state)
            result = backtrack(child, path_set)
            path_set.remove(child.state)
            if result is not None:
                return result
        return None

    root = SearchNode(start, h=heuristic(start))
    terminal = backtrack(root, {start})
    found = terminal is not None
    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=found,
        terminal_node=terminal,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        reached_count=len(reached),
        trace_rows=trace_rows,
        started_at=started_at,
        message=f"Bounded CSP backtracking {'found a planning assignment' if found else f'found no assignment within horizon {horizon}'}.",
    )


def _min_conflicts(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "Min-Conflicts"
    started_at = time.perf_counter()
    rng = random.Random(config.seed)
    current = SearchNode(start, h=heuristic(start))
    best = current
    reached: Set[State] = {start}
    reached_order = [start]
    trace_rows: List[Dict[str, Any]] = []
    expanded = 0
    generated = 1
    max_frontier = 1
    limit = _educational_limit(config, default=120)

    for step in range(1, limit + 1):
        if current.state == goal:
            return _finish_result(algorithm=algorithm, start=start, goal=goal, found=True, terminal_node=current, expanded=expanded, generated=generated, max_frontier=max_frontier, reached_count=len(reached), trace_rows=trace_rows, started_at=started_at, message="Min-Conflicts local repair reached the goal assignment.")
        child_nodes = [
            SearchNode(next_state, current, action, current.g + 1, current.depth + 1, heuristic(next_state))
            for action, next_state in neighbors(current.state)
        ]
        generated += len(child_nodes)
        expanded += 1
        max_frontier = max(max_frontier, len(child_nodes))
        min_conflict = min(child.h for child in child_nodes)
        best_children = [child for child in child_nodes if child.h == min_conflict]
        chosen = rng.choice(best_children)
        old_conflicts = current.h
        new_conflicts = chosen.h
        reached.add(chosen.state)
        reached_order.append(chosen.state)
        if chosen.h < best.h:
            best = chosen
        add_trace(
            trace_rows,
            config,
            step,
            algorithm,
            current,
            chosen.action,
            current.depth,
            current.g,
            current.h,
            chosen.h,
            child_nodes,
            reached_order,
            (
                f"Select a conflicted transition variable and repair it with action {chosen.action}: "
                f"conflicts {old_conflicts}->{new_conflicts}."
            ),
            selection_key=f"old_conflicts={old_conflicts}; new_conflicts={new_conflicts}; candidates={len(best_children)}",
            generated_children=len(child_nodes),
            skipped_states=0,
        )
        current = chosen

    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=False,
        terminal_node=None,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        reached_count=len(reached),
        trace_rows=trace_rows,
        started_at=started_at,
        message=f"Educational Min-Conflicts stopped before satisfying the goal. Best conflict score h={best.h}.",
    )


def _utility(state: State, goal: State, heuristic: Callable[[State], int], depth: int) -> float:
    if state == goal:
        return 1000.0 - depth
    return -float(heuristic(state)) - 0.01 * depth


def _adversarial_search(
    algorithm: str,
    start: State,
    goal: State,
    heuristic: Callable[[State], int],
    config: TraceConfig,
) -> SearchResult:
    if algorithm == "Expectimax":
        return _expectimax_search(start, goal, heuristic, config)
    return _minimax_like_search(algorithm, start, goal, heuristic, config)


def _minimax_like_search(
    algorithm: str,
    start: State,
    goal: State,
    heuristic: Callable[[State], int],
    config: TraceConfig,
) -> SearchResult:
    started_at = time.perf_counter()
    depth_limit = max(1, min(3, config.dfs_depth_limit, config.ids_max_depth))
    expanded = 0
    generated = 1
    pruned = 0

    def value(state: State, depth: int, maximizing: bool, alpha: float, beta: float) -> float:
        nonlocal expanded, generated, pruned
        if depth == 0 or state == goal or expanded >= config.max_expansions:
            return _utility(state, goal, heuristic, depth_limit - depth)
        child_states = [next_state for _, next_state in neighbors(state)]
        generated += len(child_states)
        expanded += 1
        if maximizing:
            best = -math.inf
            for child in child_states:
                best = max(best, value(child, depth - 1, False, alpha, beta))
                if algorithm == "Alpha-Beta Pruning":
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        pruned += 1
                        break
            return best
        best = math.inf
        for child in child_states:
            best = min(best, value(child, depth - 1, True, alpha, beta))
            if algorithm == "Alpha-Beta Pruning":
                beta = min(beta, best)
                if beta <= alpha:
                    pruned += 1
                    break
        return best

    root = SearchNode(start, h=heuristic(start))
    child_nodes = [
        SearchNode(next_state, root, action, 1, 1, heuristic(next_state))
        for action, next_state in neighbors(start)
    ]
    scored: List[Tuple[float, SearchNode]] = []
    for child in child_nodes:
        scored.append((value(child.state, depth_limit - 1, False, -math.inf, math.inf), child))
    chosen_score, chosen = max(scored, key=lambda item: (item[0], -item[1].h, item[1].action)) if scored else (_utility(start, goal, heuristic, 0), root)
    trace_rows: List[Dict[str, Any]] = []
    add_trace(
        trace_rows,
        config,
        1,
        algorithm,
        root,
        chosen.action,
        0,
        0,
        root.h,
        int(chosen_score),
        child_nodes,
        [start],
        (
            f"{algorithm} evaluates a depth-{depth_limit} game tree where MAX reduces h and MIN increases h. "
            f"Chosen action={chosen.action}, utility={chosen_score:.2f}, pruned_branches={pruned}."
        ),
        selection_key=f"depth={depth_limit}; utility={chosen_score:.2f}; alpha_beta_pruned={pruned}",
        generated_children=len(child_nodes),
        skipped_states=pruned,
    )
    found = chosen.state == goal
    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=found,
        terminal_node=chosen if found else None,
        expanded=expanded,
        generated=generated,
        max_frontier=max(len(child_nodes), 1),
        reached_count=1 + len(child_nodes),
        trace_rows=trace_rows,
        started_at=started_at,
        message=f"{algorithm} selected action {chosen.action} for the bounded adversarial 8-puzzle extension; this is not a standard single-agent solver.",
    )


def _chance_outcomes(state: State, intended_action: str) -> List[Tuple[float, State, str]]:
    legal = neighbors(state)
    legal_map = dict(legal)
    intended = legal_map.get(intended_action, state)
    alternatives = [(action, next_state) for action, next_state in legal if action != intended_action]
    if not alternatives:
        return [(1.0, intended, intended_action)]
    first_alt = alternatives[0]
    second_alt = alternatives[1] if len(alternatives) > 1 else alternatives[0]
    outcomes = [(0.8, intended, intended_action), (0.1, first_alt[1], first_alt[0]), (0.1, second_alt[1], second_alt[0])]
    total = sum(prob for prob, _, _ in outcomes)
    return [(prob / total, state_value, label) for prob, state_value, label in outcomes]


def _expectimax_search(start: State, goal: State, heuristic: Callable[[State], int], config: TraceConfig) -> SearchResult:
    algorithm = "Expectimax"
    started_at = time.perf_counter()
    depth_limit = max(1, min(3, config.dfs_depth_limit, config.ids_max_depth))
    expanded = 0
    generated = 1

    def exp_value(state: State, depth: int) -> float:
        nonlocal expanded, generated
        if depth == 0 or state == goal or expanded >= config.max_expansions:
            return _utility(state, goal, heuristic, depth_limit - depth)
        action_values = []
        for action, next_state in neighbors(state):
            generated += 1
            expected = 0.0
            for prob, outcome, _label in _chance_outcomes(state, action):
                expected += prob * exp_value(outcome if outcome != state else next_state, depth - 1)
            action_values.append(expected)
        expanded += 1
        return max(action_values) if action_values else _utility(state, goal, heuristic, depth_limit - depth)

    root = SearchNode(start, h=heuristic(start))
    child_nodes = [
        SearchNode(next_state, root, action, 1, 1, heuristic(next_state))
        for action, next_state in neighbors(start)
    ]
    scored: List[Tuple[float, SearchNode, List[Tuple[float, State, str]]]] = []
    for child in child_nodes:
        outcomes = _chance_outcomes(start, child.action)
        expected = sum(prob * exp_value(outcome, depth_limit - 1) for prob, outcome, _label in outcomes)
        scored.append((expected, child, outcomes))
    chosen_score, chosen, outcomes = max(scored, key=lambda item: (item[0], -item[1].h, item[1].action)) if scored else (_utility(start, goal, heuristic, 0), root, [])
    trace_rows: List[Dict[str, Any]] = []
    outcome_note = "; ".join(f"p={prob:.1f}:{label}->h={heuristic(state)}" for prob, state, label in outcomes)
    add_trace(
        trace_rows,
        config,
        1,
        algorithm,
        root,
        chosen.action,
        0,
        0,
        root.h,
        int(chosen_score),
        [SearchNode(state, root, label, 1, 1, heuristic(state)) for prob, state, label in outcomes],
        [start],
        (
            f"Expectimax evaluates MAX action followed by chance outcomes. "
            f"Chosen action={chosen.action}, expected value={chosen_score:.2f}. Outcomes: {outcome_note}."
        ),
        selection_key=f"depth={depth_limit}; expected_value={chosen_score:.2f}; chance_outcomes={len(outcomes)}",
        generated_children=len(outcomes),
        skipped_states=0,
    )
    found = chosen.state == goal
    return _finish_result(
        algorithm=algorithm,
        start=start,
        goal=goal,
        found=found,
        terminal_node=chosen if found else None,
        expanded=expanded,
        generated=generated,
        max_frontier=max(len(child_nodes), len(outcomes), 1),
        reached_count=1 + len(child_nodes),
        trace_rows=trace_rows,
        started_at=started_at,
        message="Expectimax selected the best expected action for a stochastic 8-puzzle extension; this is not a standard deterministic solver.",
    )


def run_algorithm(
    start: State | Sequence[int] | str,
    algorithm: str,
    heuristic: str = "manhattan",
    config: Optional[TraceConfig] = None,
    goal: State = GOAL_STATE,
) -> SearchResult:
    """Run one algorithm and return detailed trace/statistics."""

    config = config or TraceConfig()
    start_state = parse_state(start)
    goal_state = parse_state(goal)
    canonical = normalize_algorithm(algorithm)
    started_at = time.perf_counter()
    if not is_solvable(start_state, goal_state):
        return _unsolvable_result(canonical, start_state, goal_state, started_at)
    h = get_heuristic(heuristic, goal_state)
    if canonical == "BFS":
        return _bfs(start_state, goal_state, h, config)
    if canonical == "DFS":
        return _dfs(start_state, goal_state, h, config)
    if canonical in {"UCS", "Greedy", "A*"}:
        return _priority_search(canonical, start_state, goal_state, h, config)
    if canonical == "IDS":
        return _ids(start_state, goal_state, h, config)
    if canonical == "IDA*":
        return _ida_star(start_state, goal_state, h, config)
    if canonical in {
        "Simple Hill Climbing",
        "Steepest-Ascent Hill Climbing",
        "Stochastic Hill Climbing",
        "Random-Restart Hill Climbing",
    }:
        return _hill_climbing(canonical, start_state, goal_state, h, config)
    if canonical == "Local Beam Search":
        return _local_beam_search(start_state, goal_state, h, config)
    if canonical == "Simulated Annealing":
        return _simulated_annealing(start_state, goal_state, h, config)
    if ALGORITHM_INFO[canonical]["group"] == "Complex Environments":
        return _complex_environment_search(canonical, start_state, goal_state, h, config)
    if ALGORITHM_INFO[canonical]["group"] == "Constraint Satisfaction Problems":
        return _csp_search(canonical, start_state, goal_state, h, config)
    if ALGORITHM_INFO[canonical]["group"] == "Adversarial / Stochastic Search":
        return _adversarial_search(canonical, start_state, goal_state, h, config)
    raise AssertionError(f"Unhandled algorithm: {canonical}")


def _to_table(rows: List[Dict[str, Any]]) -> Any:
    try:
        import pandas as pd  # type: ignore

        return pd.DataFrame(rows)
    except Exception:
        return rows


def render_trace_table(result: SearchResult, limit: Optional[int] = None) -> Any:
    rows = result.trace_rows if limit is None else result.trace_rows[:limit]
    for row in rows:
        for column in TRACE_COLUMNS:
            row.setdefault(column, "")
    return _to_table([{column: row.get(column, "") for column in TRACE_COLUMNS} for row in rows])


def render_solution_path(result: SearchResult) -> Any:
    rows = []
    for index, state in enumerate(result.path):
        rows.append(
            {
                "Step": index,
                "Action": "Start" if index == 0 else result.actions[index - 1],
                "Board": board_string(state),
                "Compact": compact_state(state),
            }
        )
    return _to_table(rows)


def _linear_conflict_pairs(state: State, goal: State = GOAL_STATE) -> List[Dict[str, Any]]:
    goal_positions = {tile: index for index, tile in enumerate(goal)}
    conflicts: List[Dict[str, Any]] = []

    for row in range(BOARD_SIZE):
        row_tiles: List[Tuple[int, int, int]] = []
        for col in range(BOARD_SIZE):
            tile = state[row * BOARD_SIZE + col]
            if tile == 0:
                continue
            goal_row, goal_col = divmod(goal_positions[tile], BOARD_SIZE)
            if goal_row == row:
                row_tiles.append((tile, col, goal_col))
        for index, (tile, col, goal_col) in enumerate(row_tiles):
            for other_tile, other_col, other_goal_col in row_tiles[index + 1 :]:
                if goal_col > other_goal_col:
                    conflicts.append(
                        {
                            "Direction": "row",
                            "Line": row + 1,
                            "Tile A": tile,
                            "Tile B": other_tile,
                            "Current Order": f"{tile}@c{col + 1} before {other_tile}@c{other_col + 1}",
                            "Goal Order": f"{other_tile}@c{other_goal_col + 1} before {tile}@c{goal_col + 1}",
                            "Penalty": 2,
                        }
                    )

    for col in range(BOARD_SIZE):
        col_tiles: List[Tuple[int, int, int]] = []
        for row in range(BOARD_SIZE):
            tile = state[row * BOARD_SIZE + col]
            if tile == 0:
                continue
            goal_row, goal_col = divmod(goal_positions[tile], BOARD_SIZE)
            if goal_col == col:
                col_tiles.append((tile, row, goal_row))
        for index, (tile, row, goal_row) in enumerate(col_tiles):
            for other_tile, other_row, other_goal_row in col_tiles[index + 1 :]:
                if goal_row > other_goal_row:
                    conflicts.append(
                        {
                            "Direction": "column",
                            "Line": col + 1,
                            "Tile A": tile,
                            "Tile B": other_tile,
                            "Current Order": f"{tile}@r{row + 1} before {other_tile}@r{other_row + 1}",
                            "Goal Order": f"{other_tile}@r{other_goal_row + 1} before {tile}@r{goal_row + 1}",
                            "Penalty": 2,
                        }
                    )

    return conflicts


def explain_heuristic(state: State | Sequence[int] | str, heuristic_name: str, goal: State = GOAL_STATE) -> Dict[str, Any]:
    """Return tile-level heuristic evidence for coursework explanation."""

    parsed_state = parse_state(state)
    parsed_goal = parse_state(goal)
    selected_name = heuristic_name.lower().replace("-", "_").replace(" ", "_")
    selected_value = get_heuristic(heuristic_name, parsed_goal)(parsed_state)
    goal_positions = {tile: index for index, tile in enumerate(parsed_goal)}

    tile_rows: List[Dict[str, Any]] = []
    for tile in range(1, BOARD_SIZE * BOARD_SIZE):
        current_index = parsed_state.index(tile)
        goal_index = goal_positions[tile]
        current_row, current_col = divmod(current_index, BOARD_SIZE)
        goal_row, goal_col = divmod(goal_index, BOARD_SIZE)
        manhattan = abs(current_row - goal_row) + abs(current_col - goal_col)
        tile_rows.append(
            {
                "Tile": tile,
                "Current": f"r{current_row + 1}c{current_col + 1}",
                "Goal": f"r{goal_row + 1}c{goal_col + 1}",
                "Misplaced": int(current_index != goal_index),
                "Manhattan": manhattan,
                "In Goal Row": current_row == goal_row,
                "In Goal Column": current_col == goal_col,
            }
        )

    conflicts = _linear_conflict_pairs(parsed_state, parsed_goal)
    misplaced = misplaced_tiles(parsed_state, parsed_goal)
    manhattan = manhattan_distance(parsed_state, parsed_goal)
    linear = manhattan + sum(row["Penalty"] for row in conflicts)
    totals = {
        "misplaced": misplaced,
        "manhattan": manhattan,
        "selected": selected_value,
    }
    if selected_name in {"linear_conflict", "linearconflict", "lc"}:
        totals.update(
            {
                "linear_conflict_pairs": len(conflicts),
                "linear_conflict_penalty": 2 * len(conflicts),
                "linear_conflict": linear,
            }
        )
    return {
        "state": parsed_state,
        "goal": parsed_goal,
        "heuristic": selected_name,
        "selected_value": selected_value,
        "totals": totals,
        "tile_rows": tile_rows,
        "linear_conflicts": conflicts,
        "ordering_valid": linear >= manhattan >= misplaced,
        "admissibility_note": (
            "Course h(n) uses two core admissible heuristics: misplaced counts wrong tiles, "
            "and Manhattan sums the minimum grid moves for each numbered tile."
        ),
    }


def build_trace_story(result: SearchResult, heuristic_name: str) -> List[Dict[str, Any]]:
    """Convert trace rows into compact 'why this node was selected' explanations."""

    templates = {
        "BFS": "FIFO selected the shallowest frontier node.",
        "DFS": "LIFO selected the most recently pushed deep node.",
        "UCS": "The priority queue selected the node with minimum g(n).",
        "IDS": "Depth-limited DFS selected a node within the current limit.",
        "Greedy": "The priority queue selected the node with minimum h(n).",
        "A*": "A* selected the node with minimum f(n)=g(n)+h(n); insertion order breaks ties.",
        "IDA*": "IDA* continued because the node stayed within the current f-threshold.",
        "Simple Hill Climbing": "Hill climbing moved only when a neighbor improved h(n).",
        "Steepest-Ascent Hill Climbing": "Steepest ascent selected the best improving neighbor by h(n).",
        "Stochastic Hill Climbing": "Stochastic hill climbing sampled from improving neighbors.",
        "Random-Restart Hill Climbing": "The restart run kept the best observed h(n) state.",
        "Local Beam Search": "Local beam kept the top-k states with the smallest h(n).",
        "Simulated Annealing": "Simulated annealing used delta_h, temperature, and acceptance probability.",
    }
    story_rows: List[Dict[str, Any]] = []
    for row in result.trace_rows:
        algorithm = str(row.get("Algorithm") or result.algorithm)
        selection_key = row.get("Selection Key", "")
        note = row.get("Decision/Note", "")
        explanation = templates.get(algorithm, "The algorithm applied its configured priority rule.")
        if selection_key:
            explanation += f" Selection key: {selection_key}."
        if note:
            explanation += f" Decision: {note}"
        story_rows.append(
            {
                "Step": row.get("Step", ""),
                "Algorithm": algorithm,
                "Heuristic": heuristic_name,
                "Priority Rule": row.get("Priority Rule") or PRIORITY_RULES.get(algorithm, ""),
                "Selection Key": selection_key,
                "Generated Children": row.get("Generated Children", ""),
                "Skipped States": row.get("Skipped States", ""),
                "Why This Node": explanation,
            }
        )
    return story_rows


def _valid_transition(state: State, action: str, next_state: State) -> bool:
    return dict(neighbors(state)).get(action) == next_state


def validate_result(result: SearchResult, heuristic_name: str, goal: State = GOAL_STATE) -> Dict[str, Any]:
    """Return a deterministic academic certificate for one search result."""

    certificate: Dict[str, Any] = {
        "path_valid": True,
        "cost_matches_actions": True,
        "terminal_matches_goal": False,
        "solvability_checked": True,
        "heuristic_values_valid": True,
        "error": "",
    }
    errors: List[str] = []
    expected_goal = parse_state(goal)
    solvable = is_solvable(result.start, expected_goal)

    if not solvable:
        certificate["solvability_checked"] = (not result.found) and result.expanded == 0
        certificate["terminal_matches_goal"] = not result.found
        if result.found or result.expanded != 0:
            errors.append("Unsolvable state should be rejected before expansion.")
    elif result.found:
        if not result.path:
            certificate["path_valid"] = False
            errors.append("Found result has no path.")
        else:
            if result.path[0] != result.start:
                certificate["path_valid"] = False
                errors.append("Path does not start at the start state.")
            if len(result.path) != len(result.actions) + 1:
                certificate["path_valid"] = False
                errors.append("Path length does not match action count.")
            for index, action in enumerate(result.actions):
                if index + 1 >= len(result.path) or not _valid_transition(result.path[index], action, result.path[index + 1]):
                    certificate["path_valid"] = False
                    errors.append(f"Invalid transition at action index {index}.")
                    break
            certificate["terminal_matches_goal"] = result.path[-1] == expected_goal
            if not certificate["terminal_matches_goal"]:
                errors.append("Terminal state does not match goal.")
    else:
        certificate["terminal_matches_goal"] = False

    expected_cost = len(result.actions) if result.found else None
    certificate["cost_matches_actions"] = result.path_cost == expected_cost
    if not certificate["cost_matches_actions"]:
        errors.append("Path cost does not match number of actions.")

    try:
        h_func = get_heuristic(heuristic_name, expected_goal)
        states_to_check = result.path or [result.start]
        certificate["heuristic_values_valid"] = all(h_func(state) >= 0 for state in states_to_check)
    except Exception as exc:
        certificate["heuristic_values_valid"] = False
        errors.append(f"Heuristic validation failed: {exc}")

    certificate["error"] = "; ".join(errors)
    return certificate


def _markdown_table(rows: List[Dict[str, Any]], columns: Sequence[str]) -> str:
    if not rows:
        return "_No rows._"
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        values = []
        for column in columns:
            value = str(row.get(column, "")).replace("\n", "<br>").replace("|", "\\|")
            values.append(value)
        body.append("| " + " | ".join(values) + " |")
    return "\n".join([header, separator, *body])


def academic_conclusion(result: SearchResult) -> str:
    if not is_solvable(result.start, result.goal):
        return "The input is unsolvable relative to the goal, so the solver correctly rejects it before search expansion."
    if result.found:
        return f"{result.algorithm} found a path of cost {result.path_cost}. Optimality condition: {result.optimal}. Completeness condition: {result.complete}."
    return f"{result.algorithm} did not reach the goal within the configured limits. This outcome should be interpreted using its completeness limit: {result.complete}."


def _experiment_config_summary(config: TraceConfig) -> Dict[str, Any]:
    return {
        "max_expansions": config.max_expansions,
        "max_trace_rows": config.max_trace_rows,
        "ids_max_depth": config.ids_max_depth,
        "ida_max_iterations": config.ida_max_iterations,
        "local_max_steps": config.local_max_steps,
        "random_restarts": config.random_restarts,
        "beam_width": config.beam_width,
        "seed": config.seed,
    }


def _experiment_default_config() -> TraceConfig:
    return TraceConfig(
        max_expansions=8000,
        max_trace_rows=0,
        ids_max_depth=35,
        ida_max_iterations=80,
        local_max_steps=250,
        random_restarts=10,
        beam_width=4,
        seed=7,
        sa_max_steps=1500,
    )


def run_experiment_suite(
    presets: Optional[Sequence[str]] = None,
    algorithms: Optional[Sequence[str]] = None,
    heuristic_name: str = "manhattan",
    config: Optional[TraceConfig] = None,
    goal: State = GOAL_STATE,
) -> Dict[str, Any]:
    """Run a bounded deterministic coursework benchmark over demo presets."""

    selected_presets = list(presets or DEFAULT_EXPERIMENT_PRESETS)
    selected_algorithms = [normalize_algorithm(name) for name in (algorithms or DEFAULT_EXPERIMENT_ALGORITHMS)]
    run_config = config or _experiment_default_config()
    goal_state = parse_state(goal)

    raw_results: Dict[Tuple[str, str], SearchResult] = {}
    for preset_name in selected_presets:
        if preset_name not in DEMO_PRESETS:
            raise ValueError(f"Unknown experiment preset: {preset_name}. Options: {', '.join(DEMO_PRESETS)}")
        state = DEMO_PRESETS[preset_name]
        for algorithm in selected_algorithms:
            raw_results[(preset_name, algorithm)] = run_algorithm(
                state,
                algorithm,
                heuristic=heuristic_name,
                config=run_config,
                goal=goal_state,
            )

    baselines: Dict[str, Optional[int]] = {}
    for preset_name in selected_presets:
        costs = [
            result.path_cost
            for (row_preset, algorithm), result in raw_results.items()
            if row_preset == preset_name
            and algorithm in OPTIMAL_BASELINE_ALGORITHMS
            and result.found
            and result.path_cost is not None
        ]
        baselines[preset_name] = min(costs) if costs else None

    rows: List[Dict[str, Any]] = []
    for preset_name in selected_presets:
        for algorithm in selected_algorithms:
            result = raw_results[(preset_name, algorithm)]
            baseline = baselines[preset_name]
            if baseline is not None and result.found and result.path_cost is not None:
                optimal_gap: Any = result.path_cost - baseline
            else:
                optimal_gap = ""
            rows.append(
                {
                    "Preset": preset_name,
                    "Group": ALGORITHM_INFO[result.algorithm]["group"],
                    "Algorithm": result.algorithm,
                    "Found": result.found,
                    "Path Cost": result.path_cost if result.path_cost is not None else "",
                    "Expanded": result.expanded,
                    "Generated": result.generated,
                    "Runtime ms": round(result.runtime_ms, 3),
                    "Memory": f"{result.memory_estimate_kb:.1f} KB",
                    "Complete": result.complete,
                    "Optimal": result.optimal,
                    "Optimal Gap": optimal_gap,
                    "Message": result.message,
                }
            )

    return {
        "heuristic": heuristic_name,
        "goal": goal_state,
        "presets": selected_presets,
        "algorithms": selected_algorithms,
        "config": _experiment_config_summary(run_config),
        "baselines": baselines,
        "rows": rows,
        "conclusion": (
            "Optimal algorithms should match the baseline cost when limits are sufficient; "
            "Greedy and local search rows are empirical and may trade optimality for speed."
        ),
    }


def export_experiment_markdown(experiment_result: Dict[str, Any]) -> str:
    rows = list(experiment_result.get("rows", []))
    columns = [
        "Preset",
        "Algorithm",
        "Found",
        "Path Cost",
        "Expanded",
        "Generated",
        "Runtime ms",
        "Memory",
        "Complete",
        "Optimal",
        "Optimal Gap",
    ]
    baseline_rows = [
        {"Preset": preset, "Baseline Cost": cost if cost is not None else ""}
        for preset, cost in experiment_result.get("baselines", {}).items()
    ]
    return "\n".join(
        [
            "# 8-Puzzle Experiment Lab",
            "",
            "## Setup",
            f"- Heuristic: `{experiment_result.get('heuristic', '')}`",
            f"- Presets: `{', '.join(experiment_result.get('presets', []))}`",
            f"- Algorithms: `{', '.join(experiment_result.get('algorithms', []))}`",
            f"- Config: `{experiment_result.get('config', {})}`",
            "",
            "## Optimal Baselines",
            _markdown_table(baseline_rows, ["Preset", "Baseline Cost"]),
            "",
            "## Comparison Table",
            _markdown_table(rows, columns),
            "",
            "## Academic Conclusion",
            str(experiment_result.get("conclusion", "")),
            "",
        ]
    )


def export_run_markdown(
    result: SearchResult,
    heuristic_name: str,
    validation: Dict[str, Any],
    experiment_result: Optional[Dict[str, Any]] = None,
) -> str:
    """Build a submission-ready Markdown report for one algorithm run."""

    summary_rows = [result.summary_row()]
    certificate_rows = [{"Check": key, "Value": value} for key, value in validation.items()]
    heuristic_explanation = explain_heuristic(result.start, heuristic_name, result.goal)
    heuristic_totals = [{"Metric": key, "Value": value} for key, value in heuristic_explanation["totals"].items()]
    conflict_rows = heuristic_explanation["linear_conflicts"]
    peas_rows = peas_model(result.algorithm)
    trace_story = build_trace_story(result, heuristic_name)[: min(8, len(result.trace_rows))]
    path_rows = [
        {
            "Step": index,
            "Action": "Start" if index == 0 else result.actions[index - 1],
            "State": compact_state(state),
        }
        for index, state in enumerate(result.path)
    ]
    trace_rows = result.trace_rows[: min(12, len(result.trace_rows))]
    return "\n".join(
        [
            f"# 8-Puzzle Search Report - {result.algorithm}",
            "",
            "## Run Setup",
            f"- Algorithm: `{result.algorithm}`",
            f"- Heuristic: `{heuristic_name}`",
            f"- Priority rule: {PRIORITY_RULES.get(result.algorithm, '')}",
            f"- Found: `{result.found}`",
            "",
            "## Start State",
            "```text",
            board_string(result.start),
            "```",
            "",
            "## Goal State",
            "```text",
            board_string(result.goal),
            "```",
            "",
            "## PEAS Model",
            _markdown_table(peas_rows, ["Algorithm", "PEAS", "Definition"]),
            "",
            "## Metrics",
            _markdown_table(summary_rows, list(summary_rows[0].keys())),
            "",
            "## Algorithm Certificate",
            _markdown_table(certificate_rows, ["Check", "Value"]),
            "",
            "## Submission Grading Checklist",
            _markdown_table(coursework_grading_checklist(), ["Item", "Status", "Evidence", "Why it matters"]),
            "",
            "## Heuristic Inspector",
            _markdown_table(heuristic_totals, ["Metric", "Value"]),
            "",
            "### Tile Contributions",
            _markdown_table(
                heuristic_explanation["tile_rows"],
                ["Tile", "Current", "Goal", "Misplaced", "Manhattan", "In Goal Row", "In Goal Column"],
            ),
            "",
            *(
                [
                    "### Linear Conflict Pairs",
                    _markdown_table(conflict_rows, ["Direction", "Line", "Tile A", "Tile B", "Current Order", "Goal Order", "Penalty"]),
                    "",
                ]
                if heuristic_name.lower().replace("-", "_").replace(" ", "_") in {"linear_conflict", "linearconflict", "lc"}
                else []
            ),
            "## Solution Path",
            _markdown_table(path_rows, ["Step", "Action", "State"]),
            "",
            "## Trace Preview",
            _markdown_table(trace_rows, TRACE_COLUMNS),
            "",
            "## Why This Node? Preview",
            _markdown_table(
                trace_story,
                ["Step", "Algorithm", "Selection Key", "Generated Children", "Skipped States", "Why This Node"],
            ),
            "",
            *(
                [
                    "## Experiment Summary",
                    _markdown_table(
                        list(experiment_result.get("rows", [])),
                        [
                            "Preset",
                            "Algorithm",
                            "Found",
                            "Path Cost",
                            "Expanded",
                            "Generated",
                            "Runtime ms",
                            "Memory",
                            "Complete",
                            "Optimal",
                            "Optimal Gap",
                        ],
                    ),
                    "",
                ]
                if experiment_result
                else []
            ),
            "## Academic Conclusion",
            academic_conclusion(result),
            "",
        ]
    )


def algorithm_guarantee_matrix() -> List[Dict[str, Any]]:
    """Return a compact theory matrix for all registered coursework algorithms."""

    heuristic_algorithms = {
        "Greedy",
        "A*",
        "IDA*",
        "Simple Hill Climbing",
        "Steepest-Ascent Hill Climbing",
        "Stochastic Hill Climbing",
        "Random-Restart Hill Climbing",
        "Local Beam Search",
        "Simulated Annealing",
        "AND-OR Search",
        "Partially Observable Search",
        "Online Search",
        "Min-Conflicts",
    }
    random_algorithms = {"Stochastic Hill Climbing", "Random-Restart Hill Climbing", "Simulated Annealing", "Min-Conflicts"}
    adversarial_algorithms = {"Minimax", "Alpha-Beta Pruning"}
    probability_algorithms = {"Simulated Annealing", "Expectimax"}
    rows: List[Dict[str, Any]] = []
    for algorithm, info in ALGORITHM_INFO.items():
        rule = PRIORITY_RULES.get(algorithm, "")
        rows.append(
            {
                "Group": info["group"],
                "Algorithm": algorithm,
                "Complete": info["complete"],
                "Optimal": info["optimal"],
                "Uses g": "Yes" if algorithm in {"UCS", "A*", "IDA*", "BFS", "IDS"} else "Implicit" if "Backtracking" in algorithm else "No",
                "Uses h": "Yes" if algorithm in heuristic_algorithms else "No",
                "Uses f": "Yes" if algorithm in {"A*", "IDA*"} else "No",
                "Uses randomness": "Yes" if algorithm in random_algorithms else "No",
                "Uses adversary": "Yes" if algorithm in adversarial_algorithms else "No",
                "Uses probability": "Yes" if algorithm in probability_algorithms else "No",
                "Suitable for standard 8-puzzle": info.get("suitable", ""),
                "Frontier type": rule,
                "Failure mode": academic_failure_mode(algorithm),
            }
        )
    return rows


def coursework_grading_checklist(lang: str = "en") -> List[Dict[str, Any]]:
    """Return a compact checklist for lecturer-facing submission readiness."""

    if lang == "vi":
        return [
            {
                "Item": "App chính",
                "Status": "Sẵn sàng",
                "Evidence": "Chạy `python -m streamlit run .\\streamlit_eight_puzzle_app.py`.",
                "Why it matters": "Giảng viên mở đúng codepath chính, không nhầm package phụ.",
            },
            {
                "Item": "Đủ nhóm thuật toán",
                "Status": "Sẵn sàng",
                "Evidence": "UI chia 6 nhóm: Uninformed, Informed, Local, Complex, CSP, Adversarial/Stochastic.",
                "Why it matters": "Phủ đúng yêu cầu học phần AI thay vì chỉ có BFS/A*.",
            },
            {
                "Item": "PEAS",
                "Status": "Sẵn sàng",
                "Evidence": "Mỗi thuật toán có PEAS và dạng bài toán riêng trong panel học thuật.",
                "Why it matters": "Thể hiện agent, môi trường, hành động và cảm biến rõ ràng.",
            },
            {
                "Item": "Node / Frontier / Reached",
                "Status": "Sẵn sàng",
                "Evidence": "Trace có Node, Frontier, Reached, Priority Rule, Selection Key.",
                "Why it matters": "Chứng minh thuật toán mở rộng node đúng theo mô hình tìm kiếm.",
            },
            {
                "Item": "Heuristic h(n)",
                "Status": "Sẵn sàng",
                "Evidence": "UI chính chỉ dùng `misplaced` và `manhattan`.",
                "Why it matters": "Tránh nhầm heuristic ngoài phạm vi bài nộp.",
            },
            {
                "Item": "Certificate",
                "Status": "Sẵn sàng",
                "Evidence": "`validate_result()` kiểm path, cost, terminal goal, solvability và heuristic.",
                "Why it matters": "Kết quả chạy có kiểm chứng thay vì chỉ hiển thị đường đi.",
            },
            {
                "Item": "Báo cáo",
                "Status": "Sẵn sàng",
                "Evidence": "Tab Report xuất Markdown, DOCX, PDF, HTML, CSV benchmark.",
                "Why it matters": "Dễ nộp bài và lưu minh chứng thực nghiệm.",
            },
            {
                "Item": "Kiểm thử",
                "Status": "Sẵn sàng",
                "Evidence": "Self-test, behavior tests, package tests và py_compile.",
                "Why it matters": "Giảm rủi ro lỗi thuật toán hoặc UI adapter trước khi demo.",
            },
        ]
    return [
        {
            "Item": "Canonical app",
            "Status": "Ready",
            "Evidence": "Run `python -m streamlit run .\\streamlit_eight_puzzle_app.py`.",
            "Why it matters": "The lecturer opens the intended app path, not the supporting package.",
        },
        {
            "Item": "Algorithm coverage",
            "Status": "Ready",
            "Evidence": "The UI exposes six groups: Uninformed, Informed, Local, Complex, CSP, Adversarial/Stochastic.",
            "Why it matters": "The submission covers the AI coursework taxonomy, not only BFS/A*.",
        },
        {
            "Item": "PEAS",
            "Status": "Ready",
            "Evidence": "Every algorithm has PEAS and an algorithm-specific problem formulation panel.",
            "Why it matters": "The agent, environment, actuators, and sensors are explicit.",
        },
        {
            "Item": "Node / Frontier / Reached",
            "Status": "Ready",
            "Evidence": "Trace includes Node, Frontier, Reached, Priority Rule, and Selection Key.",
            "Why it matters": "The search process is auditable step by step.",
        },
        {
            "Item": "Heuristic h(n)",
            "Status": "Ready",
            "Evidence": "The main UI uses only `misplaced` and `manhattan`.",
            "Why it matters": "The report stays within the requested coursework heuristic scope.",
        },
        {
            "Item": "Certificate",
            "Status": "Ready",
            "Evidence": "`validate_result()` checks path, cost, terminal goal, solvability, and heuristic values.",
            "Why it matters": "Run results are certified instead of only displayed.",
        },
        {
            "Item": "Report export",
            "Status": "Ready",
            "Evidence": "The Report tab exports Markdown, DOCX, PDF, HTML, and CSV benchmark.",
            "Why it matters": "The submission can be attached and reviewed offline.",
        },
        {
            "Item": "Verification",
            "Status": "Ready",
            "Evidence": "Self-test, behavior tests, package tests, and py_compile.",
            "Why it matters": "Reduces algorithm and UI-adapter regression risk before demo.",
        },
    ]


def academic_failure_mode(algorithm: str) -> str:
    group = ALGORITHM_INFO[algorithm]["group"]
    if algorithm == "DFS":
        return "Can follow a deep poor branch and miss shallow optimum before limits."
    if algorithm in {"Greedy"}:
        return "Can be misled by h(n) because it ignores g(n)."
    if algorithm in {"Simple Hill Climbing", "Steepest-Ascent Hill Climbing", "Stochastic Hill Climbing"}:
        return "Can stop at a local optimum or plateau."
    if algorithm == "Simulated Annealing":
        return "Cooling schedule can freeze before reaching the goal."
    if group == "Complex Environments":
        return "Standard 8-puzzle is fully observable/deterministic, so this is a bounded educational extension."
    if group == "Constraint Satisfaction Problems":
        return "Planning-CSP horizon can be too small, or inference alone may not solve."
    if group == "Adversarial / Stochastic Search":
        return "Standard 8-puzzle has no opponent/chance node, so this is a bounded educational game model."
    return "Can stop by configured expansion, depth, or iteration limits."


def build_trace_replay(result: SearchResult, heuristic_name: str, limit: int = 80) -> List[Dict[str, Any]]:
    """Return replay rows that preserve Node / Frontier / Reached semantics."""

    replay: List[Dict[str, Any]] = []
    for row in result.trace_rows[: max(0, limit)]:
        replay.append(
            {
                "Step": row.get("Step", ""),
                "Algorithm": row.get("Algorithm", result.algorithm),
                "Heuristic": heuristic_name,
                "Node": row.get("Node", ""),
                "Action": row.get("Action", ""),
                "Depth": row.get("Depth", ""),
                "g": row.get("g", ""),
                "h": row.get("h", ""),
                "f": row.get("f", ""),
                "Priority Rule": row.get("Priority Rule", PRIORITY_RULES.get(result.algorithm, "")),
                "Selection Key": row.get("Selection Key", ""),
                "Frontier After Expansion": row.get("Frontier", ""),
                "Reached After Expansion": row.get("Reached", ""),
                "Generated Children": row.get("Generated Children", ""),
                "Skipped States": row.get("Skipped States", ""),
                "Decision/Note": row.get("Decision/Note", ""),
            }
        )
    return replay


def build_search_tree_preview(
    start: State | Sequence[int] | str,
    heuristic_name: str,
    max_depth: int = 2,
    max_nodes: int = 25,
    goal: State = GOAL_STATE,
) -> Dict[str, Any]:
    """Build a bounded search-tree preview for coursework visualization."""

    start_state = parse_state(start)
    goal_state = parse_state(goal)
    heuristic = get_heuristic(heuristic_name, goal_state)
    rows: List[Dict[str, Any]] = []
    frontier: Deque[Tuple[int, Optional[int], SearchNode]] = deque([(0, None, SearchNode(start_state, h=heuristic(start_state)))])
    next_id = 1
    while frontier and len(rows) < max_nodes:
        node_id, parent_id, node = frontier.popleft()
        rows.append(
            {
                "id": node_id,
                "parent": "" if parent_id is None else parent_id,
                "depth": node.depth,
                "action": node.action,
                "g": node.g,
                "h": node.h,
                "f": node.f,
                "state": compact_state(node.state),
                "is_start": node_id == 0,
                "is_goal": node.state == goal_state,
            }
        )
        if node.depth >= max_depth:
            continue
        for action, next_state in neighbors(node.state):
            if len(rows) + len(frontier) >= max_nodes:
                break
            child = SearchNode(next_state, node, action, node.g + 1, node.depth + 1, heuristic(next_state))
            frontier.append((next_id, node_id, child))
            next_id += 1
    return {
        "start": start_state,
        "goal": goal_state,
        "heuristic": heuristic_name,
        "max_depth": max_depth,
        "max_nodes": max_nodes,
        "nodes": rows,
        "truncated": bool(frontier),
    }


COURSEWORK_DEPTH_PRESETS: Dict[str, State] = {
    "depth_2": DEMO_PRESETS["easy_2"],
    "depth_6": generate_random_state(6, seed=13),
    "depth_10": DEMO_PRESETS["medium_10"],
    "depth_20": DEMO_PRESETS["hard_20"],
}


def depth_preset_rows(config: Optional[TraceConfig] = None) -> List[Dict[str, Any]]:
    """Return deterministic depth presets with true cost verified by A* Manhattan."""

    run_config = config or TraceConfig(max_expansions=50_000, max_trace_rows=0, ida_max_iterations=80)
    rows: List[Dict[str, Any]] = []
    for name, state in COURSEWORK_DEPTH_PRESETS.items():
        result = run_algorithm(state, "A*", "manhattan", run_config)
        rows.append(
            {
                "Preset": name,
                "State": compact_state(state),
                "True Cost": result.path_cost if result.found else "",
                "Verified": result.found,
            }
        )
    return rows


def run_heuristic_dominance_demo(
    state: State | Sequence[int] | str,
    algorithms: Optional[Sequence[str]] = None,
    heuristics: Optional[Sequence[str]] = None,
    config: Optional[TraceConfig] = None,
    goal: State = GOAL_STATE,
) -> Dict[str, Any]:
    """Compare the two course h(n) choices on the same board."""

    start_state = parse_state(state)
    selected_algorithms = [normalize_algorithm(name) for name in (algorithms or ["A*"])]
    selected_heuristics = list(heuristics or DEFAULT_HEURISTICS)
    run_config = config or TraceConfig(max_expansions=20_000, max_trace_rows=0, seed=7)
    rows: List[Dict[str, Any]] = []
    for heuristic_name in selected_heuristics:
        h_start = get_heuristic(heuristic_name, goal)(start_state)
        for algorithm in selected_algorithms:
            result = run_algorithm(start_state, algorithm, heuristic_name, run_config, goal)
            rows.append(
                {
                    "Algorithm": algorithm,
                    "Heuristic": heuristic_name,
                    "h(start)": h_start,
                    "Found": result.found,
                    "Cost": result.path_cost if result.path_cost is not None else "",
                    "Expanded": result.expanded,
                    "Generated": result.generated,
                    "Runtime ms": round(result.runtime_ms, 3),
                }
            )
    return {
        "state": start_state,
        "goal": goal,
        "heuristics": selected_heuristics,
        "algorithms": selected_algorithms,
        "rows": rows,
        "conclusion": (
            "Misplaced Tiles counts only wrong positions, while Manhattan sums tile distances. "
            "Manhattan is usually more informed because it preserves distance magnitude, and both are admissible."
        ),
    }


def _rows_to_csv(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO()
    columns = list(rows[0].keys())
    import csv

    writer = csv.DictWriter(buffer, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def export_coursework_html(pack: Dict[str, Any]) -> str:
    markdown = str(pack.get("markdown", ""))
    title = html.escape(str(pack.get("title", "8-Puzzle Coursework Report")))
    return "\n".join(
        [
            "<!doctype html>",
            "<html><head><meta charset=\"utf-8\">",
            f"<title>{title}</title>",
            "<style>body{font-family:Arial,sans-serif;line-height:1.5;max-width:980px;margin:40px auto;padding:0 20px;color:#17211b;}pre{white-space:pre-wrap;background:#f5f7f6;padding:16px;border:1px solid #d9e2df;border-radius:8px;}h1,h2{color:#0f766e;}table{border-collapse:collapse;width:100%;}td,th{border:1px solid #d9e2df;padding:6px;vertical-align:top;}</style>",
            "</head><body>",
            f"<h1>{title}</h1>",
            "<pre>",
            html.escape(markdown),
            "</pre>",
            "</body></html>",
        ]
    )


def export_coursework_docx(pack: Dict[str, Any]) -> bytes:
    markdown = str(pack.get("markdown", "8-Puzzle Coursework Report"))
    paragraphs = [line if line.strip() else " " for line in markdown.splitlines()]
    document_body = "".join(f"<w:p><w:r><w:t>{xml_escape(line)}</w:t></w:r></w:p>" for line in paragraphs)
    document_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        f"<w:body>{document_body}<w:sectPr/></w:body></w:document>"
    )
    content_types = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
        "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
        "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
        "<Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>"
        "</Types>"
    )
    rels = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>"
        "</Relationships>"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/document.xml", document_xml)
    return buffer.getvalue()


def _pdf_escape_text(value: str) -> str:
    ascii_value = "".join(ch if 32 <= ord(ch) <= 126 else "?" for ch in value)
    return ascii_value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def export_coursework_pdf(pack: Dict[str, Any]) -> bytes:
    title = str(pack.get("title", "8-Puzzle Coursework Report"))
    lines = [title, "", *str(pack.get("markdown", "")).splitlines()]
    lines = lines[:110]
    stream_lines = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
    for line in lines:
        stream_lines.append(f"({_pdf_escape_text(line[:100])}) Tj")
        stream_lines.append("T*")
    stream_lines.append("ET")
    content = "\n".join(stream_lines).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream",
    ]
    output = io.BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode("ascii"))
        output.write(obj)
        output.write(b"\nendobj\n")
    xref_offset = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return output.getvalue()


def build_submission_pack(
    result: SearchResult,
    heuristic_name: str,
    validation: Dict[str, Any],
    experiment_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build all report artifacts for a coursework submission."""

    experiment = experiment_result or run_experiment_suite(heuristic_name=heuristic_name)
    dominance = run_heuristic_dominance_demo(result.start, config=TraceConfig(max_trace_rows=0, max_expansions=20_000))
    markdown = export_run_markdown(result, heuristic_name, validation, experiment)
    markdown += "\n## Algorithm Guarantee Matrix\n"
    markdown += _markdown_table(
        algorithm_guarantee_matrix(),
        [
            "Group",
            "Algorithm",
            "Complete",
            "Optimal",
            "Uses g",
            "Uses h",
            "Uses f",
            "Uses randomness",
            "Uses adversary",
            "Uses probability",
            "Suitable for standard 8-puzzle",
        ],
    )
    markdown += "\n\n## Heuristic Dominance Demo\n"
    markdown += _markdown_table(dominance["rows"], ["Algorithm", "Heuristic", "h(start)", "Found", "Cost", "Expanded", "Generated", "Runtime ms"])
    markdown += f"\n\n{dominance['conclusion']}\n"
    markdown += "\n## Depth Presets\n"
    markdown += _markdown_table(depth_preset_rows(), ["Preset", "State", "True Cost", "Verified"])
    pack: Dict[str, Any] = {
        "title": f"8-Puzzle Coursework Report - {result.algorithm}",
        "markdown": markdown,
        "experiment": experiment,
        "heuristic_dominance": dominance,
        "benchmark_csv": _rows_to_csv(list(experiment.get("rows", []))),
    }
    pack["html"] = export_coursework_html(pack)
    pack["docx"] = export_coursework_docx(pack)
    pack["pdf"] = export_coursework_pdf(pack)
    return pack


def compare_algorithms(
    start: State | Sequence[int] | str,
    algorithms: Optional[Sequence[str]] = None,
    heuristic: str = "manhattan",
    config: Optional[TraceConfig] = None,
    goal: State = GOAL_STATE,
    return_results: bool = False,
) -> Any:
    """Run several algorithms and return a comparison table.

    Set `return_results=True` to receive `(table, results)`.
    """

    selected = list(algorithms or DEFAULT_ALGORITHMS)
    results = [
        run_algorithm(start, algorithm, heuristic=heuristic, config=config or TraceConfig(), goal=goal)
        for algorithm in selected
    ]
    rows = []
    for result in results:
        row = {"Group": ALGORITHM_INFO[result.algorithm]["group"]}
        row.update(result.summary_row())
        rows.append(row)
    table = _to_table(rows)
    return (table, results) if return_results else table


def print_result(result: SearchResult, trace_limit: int = 20) -> None:
    print(f"Algorithm: {result.algorithm}")
    print(f"Found: {result.found}")
    print(f"Message: {result.message}")
    print(f"Path length: {result.path_cost}")
    print(f"Expanded: {result.expanded}, Generated: {result.generated}, Max frontier: {result.max_frontier}")
    print("\nStart:")
    print(board_string(result.start))
    if result.path:
        print("\nSolution path:")
        for index, state in enumerate(result.path):
            action = "Start" if index == 0 else result.actions[index - 1]
            print(f"\nStep {index}: {action}")
            print(board_string(state))
    print("\nTrace preview:")
    table = render_trace_table(result, trace_limit)
    print(table.to_string(index=False) if hasattr(table, "to_string") else table)


def comparison_notes() -> str:
    return (
        "UCS uses step cost 1, so it usually matches BFS solution length. "
        "A* with Manhattan is optimal because Manhattan is admissible for 8-puzzle. "
        "Greedy can be fast but is not optimal. "
        "Hill climbing and local beam search can stop at local optima or plateaus."
    )


def run_demo() -> None:
    start = generate_random_state(scramble_moves=8, seed=7)
    config = TraceConfig(max_expansions=2000, max_trace_rows=60, seed=7, ids_max_depth=20)
    print("Demo start state:")
    print(board_string(start))
    print("\nComparison:")
    table, _results = compare_algorithms(
        start,
        algorithms=["BFS", "UCS", "IDS", "Greedy", "A*", "IDA*", "Steepest-Ascent Hill Climbing", "Local Beam Search"],
        config=config,
        return_results=True,
    )
    print(table.to_string(index=False) if hasattr(table, "to_string") else table)
    print("\nNotes:")
    print(comparison_notes())


def launch_jupyter_app() -> Any:
    """Launch an optional ipywidgets UI. Falls back to demo output when unavailable."""

    try:
        import ipywidgets as widgets  # type: ignore
        from IPython.display import HTML, clear_output, display  # type: ignore
    except Exception:
        print("ipywidgets/IPython display is not available. Running text demo instead.")
        run_demo()
        return None

    state_holder = {"state": generate_random_state(scramble_moves=20, seed=1)}
    algorithm_widget = widgets.Dropdown(options=DEFAULT_ALGORITHMS, value="A*", description="Algorithm")
    heuristic_widget = widgets.Dropdown(options=DEFAULT_HEURISTICS, value="manhattan", description="Heuristic")
    scramble_widget = widgets.IntSlider(value=20, min=0, max=80, step=1, description="Scramble")
    seed_widget = widgets.IntText(value=1, description="Seed")
    max_exp_widget = widgets.IntText(value=5000, description="Max expand")
    trace_widget = widgets.IntText(value=120, description="Trace rows")
    beam_widget = widgets.IntSlider(value=4, min=1, max=12, step=1, description="Beam")
    random_button = widgets.Button(description="Random Start", button_style="info")
    run_button = widgets.Button(description="Run Algorithm", button_style="success")
    compare_button = widgets.Button(description="Compare All", button_style="warning")
    output = widgets.Output()

    def build_config() -> TraceConfig:
        return TraceConfig(
            max_expansions=max(1, int(max_exp_widget.value)),
            max_trace_rows=max(1, int(trace_widget.value)),
            beam_width=max(1, int(beam_widget.value)),
            seed=int(seed_widget.value),
        )

    def display_state() -> None:
        display(HTML("<h3>Current 8-puzzle state</h3>"))
        display(render_board(state_holder["state"]))

    def on_random(_button: Any) -> None:
        state_holder["state"] = generate_random_state(int(scramble_widget.value), int(seed_widget.value))
        with output:
            clear_output()
            display_state()

    def on_run(_button: Any) -> None:
        with output:
            clear_output()
            display_state()
            result = run_algorithm(
                state_holder["state"],
                algorithm_widget.value,
                heuristic_widget.value,
                build_config(),
            )
            display(HTML("<h3>Summary</h3>"))
            display(_to_table([result.summary_row()]))
            display(HTML("<h3>Solution path</h3>"))
            display(render_solution_path(result))
            display(HTML("<h3>Node / Frontier / Reached trace</h3>"))
            display(render_trace_table(result))

    def on_compare(_button: Any) -> None:
        with output:
            clear_output()
            display_state()
            display(HTML("<h3>Algorithm comparison</h3>"))
            display(compare_algorithms(state_holder["state"], heuristic=heuristic_widget.value, config=build_config()))
            display(HTML(f"<p>{comparison_notes()}</p>"))

    random_button.on_click(on_random)
    run_button.on_click(on_run)
    compare_button.on_click(on_compare)
    controls = widgets.VBox(
        [
            widgets.HBox([algorithm_widget, heuristic_widget]),
            widgets.HBox([scramble_widget, seed_widget, max_exp_widget, trace_widget, beam_widget]),
            widgets.HBox([random_button, run_button, compare_button]),
        ]
    )
    display(controls, output)
    with output:
        display_state()
    return controls


def self_test() -> None:
    config = TraceConfig(max_expansions=2000, max_trace_rows=50, ids_max_depth=10, seed=11)
    goal_result = run_algorithm(GOAL_STATE, "BFS", config=config)
    assert goal_result.found and goal_result.path_cost == 0, "Goal state must solve in 0 moves."

    easy = (1, 2, 3, 4, 5, 6, 0, 7, 8)
    expected_lengths = {}
    for algorithm in ["BFS", "UCS", "IDS", "A*"]:
        result = run_algorithm(easy, algorithm, config=config)
        assert result.found, f"{algorithm} should solve the easy puzzle."
        expected_lengths[algorithm] = result.path_cost
    assert len(set(expected_lengths.values())) == 1 and expected_lengths["BFS"] == 2, expected_lengths

    random_state = generate_random_state(scramble_moves=25, seed=123)
    assert is_solvable(random_state), "Random states generated from the goal must be solvable."

    unsolvable = (1, 2, 3, 4, 5, 6, 8, 7, 0)
    unsolvable_result = run_algorithm(unsolvable, "A*", config=config)
    assert not unsolvable_result.found and unsolvable_result.expanded == 0, "Unsolvable state must be rejected early."

    trace_result = run_algorithm(easy, "BFS", config=config)
    trace_table = render_trace_table(trace_result)
    columns = list(trace_table.columns) if hasattr(trace_table, "columns") else list(trace_table[0].keys())
    for column in ["Node", "Frontier", "Reached", "Priority Rule", "Selection Key", "Generated Children", "Skipped States"]:
        assert column in columns, f"Trace table missing {column}."

    misplaced_result = run_algorithm(easy, "A*", heuristic="misplaced", config=config)
    assert misplaced_result.found and misplaced_result.path_cost == 2, "A* with Misplaced should solve the easy puzzle optimally."

    local_result = run_algorithm((1, 2, 3, 4, 5, 6, 7, 0, 8), "Local Beam Search", config=config)
    assert local_result.found, "Local Beam should solve a one-move puzzle."
    print("Self-test passed.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="8-puzzle search visualizer for Python/Jupyter.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in correctness checks.")
    parser.add_argument("--demo", action="store_true", help="Run a text demo comparison.")
    parser.add_argument("--algorithm", default="A*", help="Algorithm to run for non-demo CLI mode.")
    parser.add_argument("--heuristic", default="manhattan", choices=DEFAULT_HEURISTICS, help="Heuristic for informed/local search.")
    parser.add_argument("--scramble", type=int, default=12, help="Random scramble moves when --start is omitted.")
    parser.add_argument("--seed", type=int, default=1, help="Random seed.")
    parser.add_argument("--max-expansions", type=int, default=5000, help="Search expansion limit.")
    parser.add_argument("--start", default="", help="Optional state, e.g. '1 2 3 4 5 6 7 8 0'.")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        return 0
    if args.demo:
        run_demo()
        return 0

    start = parse_state(args.start) if args.start else generate_random_state(args.scramble, args.seed)
    config = TraceConfig(max_expansions=args.max_expansions, seed=args.seed)
    result = run_algorithm(start, args.algorithm, heuristic=args.heuristic, config=config)
    print_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
