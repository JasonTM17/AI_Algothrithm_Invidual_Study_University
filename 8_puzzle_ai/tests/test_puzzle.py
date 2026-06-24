"""
Tests for 8-puzzle core functionality.
"""

import sys
import os

try:
    from ..core.puzzle import PuzzleState, validate_state, parse_state, scramble_state
    from ..core.heuristics import misplaced_tiles, manhattan_distance, linear_conflict
    from ..algorithms import get_algorithm
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from core.puzzle import PuzzleState, validate_state, parse_state, scramble_state
    from core.heuristics import misplaced_tiles, manhattan_distance, linear_conflict
    from algorithms import get_algorithm


def test_is_solvable():
    """Test solvability check."""
    # Goal state is solvable
    goal = PuzzleState((1, 2, 3, 4, 5, 6, 7, 8, 0))
    assert goal.is_solvable() == True, "Goal should be solvable"
    
    # Swap 7 and 8 - should be unsolvable
    unsolvable = PuzzleState((1, 2, 3, 4, 5, 6, 8, 7, 0))
    assert unsolvable.is_solvable() == False, "Swapped 7,8 should be unsolvable"
    
    print("[PASS] test_is_solvable passed")


def test_get_neighbors():
    """Test neighbor generation."""
    # Goal state - blank at (2,2)
    goal = PuzzleState((1, 2, 3, 4, 5, 6, 7, 8, 0))
    neighbors = goal.get_neighbors()
    
    # Should have 2 neighbors: Left and Up
    assert len(neighbors) == 2, f"Goal should have 2 neighbors, got {len(neighbors)}"
    
    actions = [a for a, _ in neighbors]
    assert 'L' in actions, "Should have Left action"
    assert 'U' in actions, "Should have Up action"
    
    print("[PASS] test_get_neighbors passed")


def test_heuristics():
    """Test heuristic functions."""
    goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    
    # h(goal) should be 0
    assert misplaced_tiles(goal, goal) == 0, "Misplaced tiles of goal should be 0"
    assert manhattan_distance(goal, goal) == 0, "Manhattan of goal should be 0"
    assert linear_conflict(goal, goal) == 0, "Linear conflict of goal should be 0"
    
    # Test a non-goal state
    state = (1, 2, 3, 5, 0, 6, 4, 7, 8)
    h_misplaced = misplaced_tiles(state, goal)
    h_manhattan = manhattan_distance(state, goal)
    
    assert h_misplaced > 0, "Non-goal should have h > 0"
    assert h_manhattan > 0, "Non-goal should have h > 0"
    assert h_manhattan >= h_misplaced, "Manhattan should be >= misplaced tiles"
    
    print("[PASS] test_heuristics passed")


def test_validate_state():
    """Test state validation."""
    # Valid state
    is_valid, msg = validate_state((1, 2, 3, 4, 5, 6, 7, 8, 0))
    assert is_valid == True, "Valid state should pass"
    
    # Wrong length
    is_valid, msg = validate_state((1, 2, 3, 4, 5, 6, 7, 8))
    assert is_valid == False, "Wrong length should fail"
    
    # Duplicate
    is_valid, msg = validate_state((1, 1, 2, 3, 4, 5, 6, 7, 8))
    assert is_valid == False, "Duplicate should fail"
    
    print("[PASS] test_validate_state passed")


def test_parse_state():
    """Test state parsing."""
    # Space separated
    state = parse_state("1 2 3 4 5 6 7 8 0")
    assert state == (1, 2, 3, 4, 5, 6, 7, 8, 0)
    
    # Comma separated
    state = parse_state("1,2,3,4,5,6,7,8,0")
    assert state == (1, 2, 3, 4, 5, 6, 7, 8, 0)
    
    # No separator
    state = parse_state("123456780")
    assert state == (1, 2, 3, 4, 5, 6, 7, 8, 0)
    
    print("[PASS] test_parse_state passed")


def test_scramble():
    """Test scramble generation."""
    state = scramble_state(num_moves=20, seed=42)
    
    assert state.is_solvable() == True, "Scrambled state should be solvable"
    assert state.state != PuzzleState.GOAL_STATE, "Scrambled should not be goal"
    
    print("[PASS] test_scramble passed")


def test_adversarial_algorithms_use_caro_demo():
    """Adversarial algorithms should run on Caro, not simulated 8-puzzle."""
    start = (1, 2, 3, 5, 0, 6, 4, 7, 8)
    for algorithm in ["Minimax", "Alpha-Beta Pruning", "Expectimax"]:
        result = get_algorithm(algorithm)(
            start=start,
            max_depth=3,
            trace_limit=5,
            seed=7,
        )
        trace_text = "\n".join(str(row) for row in result.trace)
        assert result.success is True, f"{algorithm} should complete the Caro demo"
        assert "Caro" in result.message, f"{algorithm} message should mention Caro"
        assert "Caro board" in trace_text, f"{algorithm} trace should render a Caro board"
        assert result.actions and result.actions[0].startswith("X@"), f"{algorithm} should choose a MAX move"

    print("[PASS] test_adversarial_algorithms_use_caro_demo passed")


def run_all_tests():
    """Run all tests."""
    print("Running tests...\n")
    
    test_is_solvable()
    test_get_neighbors()
    test_heuristics()
    test_validate_state()
    test_parse_state()
    test_scramble()
    test_adversarial_algorithms_use_caro_demo()
    
    print("\n[SUCCESS] All tests passed!")


if __name__ == "__main__":
    run_all_tests()
