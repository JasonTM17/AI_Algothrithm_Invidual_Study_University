"""Behavioral regression tests for the canonical 8-puzzle engine and package UI adapter."""

from __future__ import annotations

import importlib.util
import sys
from collections import deque
from dataclasses import replace
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "8_puzzle_ai"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACKAGE_ROOT))

import eight_puzzle_search_app as puzzle


def assert_valid_path(start: puzzle.State, actions: Iterable[str], goal: puzzle.State = puzzle.GOAL_STATE) -> None:
    state = start
    for action in actions:
        transitions = dict(puzzle.neighbors(state))
        assert action in transitions, f"Invalid action {action!r} from {state}"
        state = transitions[action]
    assert state == goal, f"Path ended at {state}, expected {goal}"


def shallow_distances(max_depth: int) -> dict[puzzle.State, int]:
    distances = {puzzle.GOAL_STATE: 0}
    frontier = deque([puzzle.GOAL_STATE])
    while frontier:
        state = frontier.popleft()
        depth = distances[state]
        if depth >= max_depth:
            continue
        for _, next_state in puzzle.neighbors(state):
            if next_state not in distances:
                distances[next_state] = depth + 1
                frontier.append(next_state)
    return distances


def load_package_app():
    spec = importlib.util.spec_from_file_location("package_streamlit_app", PACKAGE_ROOT / "app.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_optimal_algorithms_and_path_validity() -> None:
    start = (1, 2, 3, 4, 5, 6, 0, 7, 8)
    config = puzzle.TraceConfig(max_expansions=10_000, max_trace_rows=0, ids_max_depth=10, ida_max_iterations=20)

    results = {
        name: puzzle.run_algorithm(start, name, "manhattan", config)
        for name in ["BFS", "UCS", "A*", "IDA*", "Greedy"]
    }

    for name, result in results.items():
        assert result.found, f"{name} should solve the easy state: {result.message}"
        assert_valid_path(start, result.actions)

    assert results["BFS"].path_cost == 2
    assert results["UCS"].path_cost == results["BFS"].path_cost
    assert results["A*"].path_cost == results["BFS"].path_cost
    assert results["IDA*"].path_cost == results["BFS"].path_cost


def test_a_star_matches_true_distance_on_shallow_states() -> None:
    config = puzzle.TraceConfig(max_expansions=10_000, max_trace_rows=0, ida_max_iterations=50)
    distances = shallow_distances(6)
    for state, true_distance in distances.items():
        result = puzzle.run_algorithm(state, "A*", "manhattan", config)
        assert result.found
        assert result.path_cost == true_distance
        assert_valid_path(state, result.actions)


def test_heuristics_are_ordered_and_admissible_near_goal() -> None:
    for state, true_distance in shallow_distances(6).items():
        manhattan = puzzle.manhattan_distance(state)
        misplaced = puzzle.misplaced_tiles(state)
        assert manhattan >= misplaced
        assert manhattan <= true_distance
    assert puzzle.DEFAULT_HEURISTICS == ["misplaced", "manhattan"]


def test_unsolvable_state_stops_before_expansion() -> None:
    result = puzzle.run_algorithm((1, 2, 3, 4, 5, 6, 8, 7, 0), "A*")
    assert not result.found
    assert result.expanded == 0
    assert "not solvable" in result.message
    certificate = puzzle.validate_result(result, "manhattan")
    assert certificate["solvability_checked"]
    assert not certificate["error"]


def test_trace_disabled_does_not_crash_priority_search() -> None:
    config = puzzle.TraceConfig(max_expansions=10_000, max_trace_rows=0)
    result = puzzle.run_algorithm(puzzle.generate_random_state(20, seed=1), "A*", "manhattan", config)
    assert result.found
    assert result.trace_rows == []
    assert_valid_path(result.start, result.actions)


def test_academic_trace_contract_for_all_algorithms() -> None:
    start = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    config = puzzle.TraceConfig(
        max_expansions=200,
        max_trace_rows=20,
        ids_max_depth=5,
        ida_max_iterations=10,
        local_max_steps=8,
        random_restarts=1,
        sa_max_steps=8,
        seed=4,
    )
    expected_columns = {"Priority Rule", "Selection Key", "Generated Children", "Skipped States", "Decision/Note"}
    for algorithm in puzzle.DEFAULT_ALGORITHMS:
        result = puzzle.run_algorithm(start, algorithm, "manhattan", config)
        assert result.trace_rows, f"{algorithm} should emit trace rows"
        assert expected_columns <= set(result.trace_rows[0]), algorithm

    priority_expectations = {"UCS": "g=", "Greedy": "h=", "A*": "f="}
    for algorithm, marker in priority_expectations.items():
        result = puzzle.run_algorithm(start, algorithm, "manhattan", config)
        assert marker in result.trace_rows[0]["Selection Key"]

    ida = puzzle.run_algorithm(start, "IDA*", "manhattan", config)
    assert "threshold=" in ida.trace_rows[0]["Selection Key"]
    sa = puzzle.run_algorithm(start, "Simulated Annealing", "manhattan", config)
    assert "T=" in sa.trace_rows[0]["Selection Key"]


def test_result_certificate_and_markdown_export() -> None:
    start = (1, 2, 3, 4, 5, 6, 0, 7, 8)
    result = puzzle.run_algorithm(start, "A*", "manhattan", puzzle.TraceConfig(max_trace_rows=10))
    certificate = puzzle.validate_result(result, "manhattan")
    assert certificate["path_valid"]
    assert certificate["cost_matches_actions"]
    assert certificate["terminal_matches_goal"]
    assert certificate["heuristic_values_valid"]
    assert not certificate["error"]

    bad_path = list(result.path)
    bad_path[1] = bad_path[0]
    bad_result = replace(result, path=bad_path)
    bad_certificate = puzzle.validate_result(bad_result, "manhattan")
    assert not bad_certificate["path_valid"]
    assert "Invalid transition" in bad_certificate["error"]

    report = puzzle.export_run_markdown(result, "manhattan", certificate)
    assert "# 8-Puzzle Search Report" in report
    assert "Algorithm Certificate" in report
    assert "Submission Grading Checklist" in report
    assert "Heuristic Inspector" in report
    assert "Trace Preview" in report
    assert "Why This Node? Preview" in report

    checklist = puzzle.coursework_grading_checklist("vi")
    assert len(checklist) >= 8
    assert any(row["Item"] == "Heuristic h(n)" for row in checklist)


def test_heuristic_explainer_reports_two_course_heuristics() -> None:
    state = (2, 1, 3, 4, 5, 6, 7, 8, 0)
    explanation = puzzle.explain_heuristic(state, "manhattan")

    assert explanation["totals"]["misplaced"] == 2
    assert explanation["totals"]["manhattan"] == 2
    assert "linear_conflict" not in explanation["totals"]
    assert explanation["selected_value"] == 2
    assert explanation["ordering_valid"]
    assert len(explanation["tile_rows"]) == 8


def test_trace_story_explains_selection_rules() -> None:
    start = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    config = puzzle.TraceConfig(max_expansions=200, max_trace_rows=10, ida_max_iterations=10, sa_max_steps=5, seed=4)

    a_star = puzzle.run_algorithm(start, "A*", "manhattan", config)
    a_story = puzzle.build_trace_story(a_star, "manhattan")
    assert a_story
    assert "minimum f(n)=g(n)+h(n)" in a_story[0]["Why This Node"]

    ida = puzzle.run_algorithm(start, "IDA*", "manhattan", config)
    ida_story = puzzle.build_trace_story(ida, "manhattan")
    assert "f-threshold" in ida_story[0]["Why This Node"]

    sa = puzzle.run_algorithm(start, "Simulated Annealing", "manhattan", config)
    sa_story = puzzle.build_trace_story(sa, "manhattan")
    assert "temperature" in sa_story[0]["Why This Node"]


def test_trace_semantics_match_academic_node_frontier_reached_model() -> None:
    start = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    config = puzzle.TraceConfig(max_expansions=200, max_trace_rows=20, local_max_steps=3, sa_max_steps=3, seed=1)

    bfs = puzzle.run_algorithm(start, "BFS", "manhattan", config)
    first_bfs = bfs.trace_rows[0]
    assert first_bfs["Generated Children"] == 3
    assert "7 8 0" in first_bfs["Frontier"], "BFS frontier should show children after expanding the start node"
    assert "7 8 0" in first_bfs["Reached"], "BFS reached should include newly discovered children"

    a_star = puzzle.run_algorithm(start, "A*", "manhattan", config)
    first_a_star = a_star.trace_rows[0]
    assert first_a_star["Generated Children"] == 3
    assert "7 8 0" in first_a_star["Frontier"], "A* frontier should show priority-queued children after expansion"

    ida_config = puzzle.TraceConfig(max_expansions=200, max_trace_rows=120, ida_max_iterations=10)
    ida_start = puzzle.generate_random_state(8, seed=3)
    ida = puzzle.run_algorithm(ida_start, "IDA*", "misplaced", ida_config)
    pruned_rows = [row for row in ida.trace_rows if "pruned=True" in str(row["Selection Key"])]
    assert pruned_rows, "IDA* should expose threshold-pruned rows on this shallow misplaced-heuristic case"
    assert all(row["Generated Children"] == 0 and row["Frontier"] == "" for row in pruned_rows)

    beam = puzzle.run_algorithm(start, "Local Beam Search", "manhattan", config)
    first_beam = beam.trace_rows[0]
    assert first_beam["Generated Children"] == 3
    assert "7 8 0" in first_beam["Frontier"], "Local Beam frontier should be the next top-k beam, not the old beam"

    sa = puzzle.run_algorithm(start, "Simulated Annealing", "manhattan", config)
    first_sa = sa.trace_rows[0]
    assert first_sa["Node"] == puzzle.board_string(start)
    assert "candidate_h=" in first_sa["Selection Key"]


def test_experiment_suite_is_deterministic_and_exportable() -> None:
    config = puzzle.TraceConfig(max_expansions=10_000, max_trace_rows=0, ida_max_iterations=30, seed=7)
    experiment_a = puzzle.run_experiment_suite(
        presets=["easy_2", "unsolvable_demo"],
        algorithms=["BFS", "A*", "Greedy"],
        heuristic_name="manhattan",
        config=config,
    )
    experiment_b = puzzle.run_experiment_suite(
        presets=["easy_2", "unsolvable_demo"],
        algorithms=["BFS", "A*", "Greedy"],
        heuristic_name="manhattan",
        config=config,
    )

    stable_keys = ["Preset", "Algorithm", "Found", "Path Cost", "Expanded", "Generated", "Complete", "Optimal", "Optimal Gap"]
    stable_a = [{key: row[key] for key in stable_keys} for row in experiment_a["rows"]]
    stable_b = [{key: row[key] for key in stable_keys} for row in experiment_b["rows"]]
    assert stable_a == stable_b
    assert len(experiment_a["rows"]) == 6
    assert experiment_a["baselines"]["easy_2"] == 2
    easy_rows = [row for row in experiment_a["rows"] if row["Preset"] == "easy_2"]
    assert all(row["Optimal Gap"] == 0 for row in easy_rows if row["Found"] and row["Algorithm"] in {"BFS", "A*"})
    unsolvable_rows = [row for row in experiment_a["rows"] if row["Preset"] == "unsolvable_demo"]
    assert all(not row["Found"] and row["Expanded"] == 0 for row in unsolvable_rows)

    markdown = puzzle.export_experiment_markdown(experiment_a)
    assert "# 8-Puzzle Experiment Lab" in markdown
    assert "Optimal Baselines" in markdown
    assert "unsolvable_demo" in markdown


def test_six_group_registry_covers_coursework_spec() -> None:
    expected_algorithms = {
        "BFS",
        "DFS",
        "UCS",
        "IDS",
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
        "No Observation Search",
        "Partially Observable Search",
        "Online Search",
        "CSP Definition",
        "Constraint Propagation",
        "Path Consistency",
        "Global Constraints",
        "CSP Backtracking",
        "Min-Conflicts",
        "Constraint Graph",
        "Minimax",
        "Alpha-Beta Pruning",
        "Expectimax",
    }
    assert set(puzzle.DEFAULT_ALGORITHMS) == expected_algorithms
    assert len(puzzle.DEFAULT_ALGORITHMS) == 27
    assert puzzle.algorithm_groups() == [
        "Uninformed Search",
        "Informed Search",
        "Local Search",
        "Complex Environments",
        "Constraint Satisfaction Problems",
        "Adversarial / Stochastic Search",
    ]


def test_educational_algorithms_return_canonical_results() -> None:
    start = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    config = puzzle.TraceConfig(
        max_expansions=300,
        max_trace_rows=5,
        ids_max_depth=5,
        dfs_depth_limit=3,
        local_max_steps=5,
        random_restarts=1,
        sa_max_steps=5,
        seed=2,
    )
    educational = [
        algorithm
        for algorithm in puzzle.DEFAULT_ALGORITHMS
        if puzzle.ALGORITHM_INFO[algorithm]["group"]
        in {"Complex Environments", "Constraint Satisfaction Problems", "Adversarial / Stochastic Search"}
    ]
    for algorithm in educational:
        result = puzzle.run_algorithm(start, algorithm, "manhattan", config)
        assert result.algorithm == algorithm
        assert isinstance(result.found, bool)
        assert result.message
        assert result.notes.startswith("Group:")
        assert result.trace_rows, algorithm
        assert {"Node", "Frontier", "Reached", "Decision/Note"} <= set(result.trace_rows[0])


def test_peas_trace_preview_and_submission_pack_exports() -> None:
    peas = puzzle.peas_model()
    assert [row["PEAS"] for row in peas] == ["Performance", "Environment", "Actuators", "Sensors"]
    a_star_peas_vi = puzzle.peas_model("A*", lang="vi")
    assert all(row["Algorithm"] == "A*" for row in a_star_peas_vi)
    assert "đạt Goal" in a_star_peas_vi[0]["Definition"]

    start = (1, 2, 3, 4, 5, 6, 0, 7, 8)
    result = puzzle.run_algorithm(start, "A*", "manhattan", puzzle.TraceConfig(max_trace_rows=10))
    validation = puzzle.validate_result(result, "manhattan")
    replay = puzzle.build_trace_replay(result, "manhattan")
    tree = puzzle.build_search_tree_preview(start, "manhattan", max_depth=2, max_nodes=10)
    dominance = puzzle.run_heuristic_dominance_demo(start)
    pack = puzzle.build_submission_pack(result, "manhattan", validation)

    assert replay and "Frontier After Expansion" in replay[0]
    assert tree["nodes"][0]["is_start"]
    assert {row["Heuristic"] for row in dominance["rows"]} == {"misplaced", "manhattan"}
    assert "PEAS Model" in pack["markdown"]
    assert pack["docx"].startswith(b"PK")
    assert pack["pdf"].startswith(b"%PDF")
    assert "8-Puzzle Coursework Report" in pack["html"]
    assert "Preset,Group,Algorithm" in pack["benchmark_csv"]


def test_complex_environment_problem_formulations_match_algorithm_names() -> None:
    partial_model = puzzle.algorithm_problem_model("Partially Observable Search", lang="vi")
    assert any("1 2 ?" in row["Định nghĩa"] for row in partial_model)
    custom_pattern = puzzle.parse_partial_goal("? ? ? 4 5 ? ? ? 0")
    custom_model = puzzle.algorithm_problem_model("Partially Observable Search", lang="vi", partial_goal_pattern=custom_pattern)
    assert any("4 5 ?" in row["Định nghĩa"] and "? ? 0" in row["Định nghĩa"] for row in custom_model)
    random_pattern = puzzle.random_partial_goal_pattern(seed=10, reveal_count=3)
    assert len(random_pattern) == 9
    assert sum(value is not None for value in random_pattern) == 3
    no_obs_model = puzzle.algorithm_problem_model("No Observation Search", lang="vi")
    assert any("belief state" in row["Định nghĩa"] or "belief" in row["Định nghĩa"] for row in no_obs_model)

    start = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    config = puzzle.TraceConfig(max_expansions=100, max_trace_rows=5, local_max_steps=3, seed=2, partial_goal_pattern=custom_pattern)
    result = puzzle.run_algorithm(start, "Partially Observable Search", "manhattan", config)
    assert result.trace_rows
    assert "partial_goal_mismatch" in result.trace_rows[0]["Selection Key"]
    assert "4 5 ?" in result.trace_rows[0]["Decision/Note"]


def test_package_app_adapter_filters_algorithm_params() -> None:
    package_app = load_package_app()
    base_params = {
        "start": (1, 2, 3, 4, 5, 6, 0, 7, 8),
        "goal": puzzle.GOAL_STATE,
        "heuristic": "manhattan",
        "max_nodes": 1_000,
        "max_time_ms": 30_000,
        "action_order": "LRUD",
        "trace_limit": 10,
        "max_depth": 6,
        "max_steps": 20,
        "beam_width": 3,
        "seed": 7,
    }

    for algorithm in ["BFS", "A*", "IDS", "Local Beam Search", "Minimax"]:
        result = package_app.run_selected_algorithm(algorithm, dict(base_params))
        assert getattr(result, "algorithm", ""), algorithm
        assert hasattr(result, "success")


def run_all_tests() -> None:
    tests = [
        test_optimal_algorithms_and_path_validity,
        test_a_star_matches_true_distance_on_shallow_states,
        test_heuristics_are_ordered_and_admissible_near_goal,
        test_unsolvable_state_stops_before_expansion,
        test_trace_disabled_does_not_crash_priority_search,
        test_academic_trace_contract_for_all_algorithms,
        test_result_certificate_and_markdown_export,
        test_heuristic_explainer_reports_two_course_heuristics,
        test_trace_story_explains_selection_rules,
        test_trace_semantics_match_academic_node_frontier_reached_model,
        test_experiment_suite_is_deterministic_and_exportable,
        test_six_group_registry_covers_coursework_spec,
        test_educational_algorithms_return_canonical_results,
        test_peas_trace_preview_and_submission_pack_exports,
        test_complex_environment_problem_formulations_match_algorithm_names,
        test_package_app_adapter_filters_algorithm_params,
    ]
    for test in tests:
        test()
        print(f"[PASS] {test.__name__}")


if __name__ == "__main__":
    run_all_tests()
