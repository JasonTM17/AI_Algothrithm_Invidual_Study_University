"""
Metrics and comparison utilities for search algorithms.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class SearchMetrics:
    """Metrics collected during search."""
    
    nodes_expanded: int = 0
    nodes_generated: int = 0
    max_frontier_size: int = 0
    reached_size: int = 0
    runtime_ms: float = 0.0
    memory_estimate_kb: float = 0.0
    
    def update_frontier(self, frontier_size: int):
        """Update max frontier size."""
        self.max_frontier_size = max(self.max_frontier_size, frontier_size)
    
    def increment_expanded(self):
        """Increment expanded counter."""
        self.nodes_expanded += 1
    
    def increment_generated(self, count: int = 1):
        """Increment generated counter."""
        self.nodes_generated += count
    
    def update_reached(self, reached_size: int):
        """Update reached size."""
        self.reached_size = reached_size


def compare_results(results: List[Any]) -> Dict[str, Any]:
    """
    Compare multiple search results.
    
    Args:
        results: List of SearchResult objects
    
    Returns:
        Dictionary with comparison data
    """
    if not results:
        return {}
    
    # Filter successful results
    successful = [r for r in results if r.success]
    
    comparison = {
        "total_algorithms": len(results),
        "successful": len(successful),
        "failed": len(results) - len(successful),
        "fastest": None,
        "shortest_path": None,
        "most_efficient": None,
        "least_memory": None,
        "summary_table": []
    }
    
    # Build summary table
    for r in results:
        row = {
            "Algorithm": r.algorithm,
            "Group": r.group,
            "Success": "✓" if r.success else "✗",
            "Path Length": r.path_cost if r.success else "N/A",
            "Nodes Expanded": r.nodes_expanded,
            "Runtime (ms)": f"{r.runtime_ms:.2f}",
            "Optimal": r.optimal
        }
        comparison["summary_table"].append(row)
    
    if successful:
        # Find fastest
        fastest = min(successful, key=lambda x: x.runtime_ms)
        comparison["fastest"] = {
            "algorithm": fastest.algorithm,
            "runtime_ms": fastest.runtime_ms
        }
        
        # Find shortest path
        shortest = min(successful, key=lambda x: x.path_cost if x.path_cost else float('inf'))
        comparison["shortest_path"] = {
            "algorithm": shortest.algorithm,
            "path_cost": shortest.path_cost
        }
        
        # Find most efficient (fewest expanded)
        most_efficient = min(successful, key=lambda x: x.nodes_expanded)
        comparison["most_efficient"] = {
            "algorithm": most_efficient.algorithm,
            "nodes_expanded": most_efficient.nodes_expanded
        }
        
        # Find least memory (smallest max frontier)
        least_memory = min(successful, key=lambda x: x.max_frontier_size)
        comparison["least_memory"] = {
            "algorithm": least_memory.algorithm,
            "max_frontier": least_memory.max_frontier_size
        }
    
    return comparison


def generate_comparison_report(results: List[Any]) -> str:
    """
    Generate text comparison report.
    
    Args:
        results: List of SearchResult objects
    
    Returns:
        Formatted report string
    """
    comparison = compare_results(results)
    
    lines = []
    lines.append("=" * 60)
    lines.append("ALGORITHM COMPARISON REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    lines.append(f"Total algorithms tested: {comparison['total_algorithms']}")
    lines.append(f"Successful: {comparison['successful']}")
    lines.append(f"Failed: {comparison['failed']}")
    lines.append("")
    
    if comparison['fastest']:
        lines.append("FASTEST ALGORITHM:")
        lines.append(f"  {comparison['fastest']['algorithm']} ({comparison['fastest']['runtime_ms']:.2f} ms)")
        lines.append("")
    
    if comparison['shortest_path']:
        lines.append("SHORTEST PATH:")
        lines.append(f"  {comparison['shortest_path']['algorithm']} ({comparison['shortest_path']['path_cost']} moves)")
        lines.append("")
    
    if comparison['most_efficient']:
        lines.append("MOST EFFICIENT (fewest nodes expanded):")
        lines.append(f"  {comparison['most_efficient']['algorithm']} ({comparison['most_efficient']['nodes_expanded']} nodes)")
        lines.append("")
    
    if comparison['least_memory']:
        lines.append("LEAST MEMORY (smallest max frontier):")
        lines.append(f"  {comparison['least_memory']['algorithm']} ({comparison['least_memory']['max_frontier']} nodes)")
        lines.append("")
    
    lines.append("-" * 60)
    lines.append("SUMMARY TABLE:")
    lines.append("-" * 60)
    
    # Table header
    header = f"{'Algorithm':<25} {'Success':<8} {'Path':<8} {'Expanded':<10} {'Runtime':<10}"
    lines.append(header)
    lines.append("-" * 60)
    
    for row in comparison['summary_table']:
        line = f"{row['Algorithm']:<25} {row['Success']:<8} {str(row['Path Length']):<8} {row['Nodes Expanded']:<10} {row['Runtime (ms)']:<10}"
        lines.append(line)
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


def get_algorithm_properties() -> Dict[str, Dict[str, Any]]:
    """
    Return properties of each algorithm.
    
    Returns:
        Dictionary with algorithm properties
    """
    return {
        # Uninformed
        "BFS": {
            "group": "Uninformed Search",
            "complete": True,
            "optimal": True,
            "time_complexity": "O(b^d)",
            "space_complexity": "O(b^d)",
            "uses_heuristic": False,
            "suitable": True,
            "notes": "Optimal for unit cost. High memory usage."
        },
        "DFS": {
            "group": "Uninformed Search",
            "complete": False,
            "optimal": False,
            "time_complexity": "O(b^m)",
            "space_complexity": "O(bm)",
            "uses_heuristic": False,
            "suitable": False,
            "notes": "May not find solution. Not optimal. Low memory."
        },
        "UCS": {
            "group": "Uninformed Search",
            "complete": True,
            "optimal": True,
            "time_complexity": "O(b^(C*/ε))",
            "space_complexity": "O(b^(C*/ε))",
            "uses_heuristic": False,
            "suitable": True,
            "notes": "Same as BFS for unit cost."
        },
        "IDS": {
            "group": "Uninformed Search",
            "complete": True,
            "optimal": True,
            "time_complexity": "O(b^d)",
            "space_complexity": "O(bd)",
            "uses_heuristic": False,
            "suitable": True,
            "notes": "Optimal like BFS but less memory. Re-expands nodes."
        },
        # Informed
        "Greedy": {
            "group": "Informed Search",
            "complete": False,
            "optimal": False,
            "time_complexity": "O(b^m)",
            "space_complexity": "O(b^m)",
            "uses_heuristic": True,
            "suitable": True,
            "notes": "Fast but not optimal. Can get stuck."
        },
        "A*": {
            "group": "Informed Search",
            "complete": True,
            "optimal": True,
            "time_complexity": "O(b^d)",
            "space_complexity": "O(b^d)",
            "uses_heuristic": True,
            "suitable": True,
            "notes": "Optimal with admissible heuristic. Best for 8-puzzle."
        },
        "IDA*": {
            "group": "Informed Search",
            "complete": True,
            "optimal": True,
            "time_complexity": "O(b^d)",
            "space_complexity": "O(bd)",
            "uses_heuristic": True,
            "suitable": True,
            "notes": "Optimal like A* but less memory. Re-expands nodes."
        },
        # Local Search
        "Simple Hill Climbing": {
            "group": "Local Search",
            "complete": False,
            "optimal": False,
            "time_complexity": "O(1)",
            "space_complexity": "O(1)",
            "uses_heuristic": True,
            "suitable": False,
            "notes": "Can get stuck at local optimum."
        },
        "Steepest-Ascent Hill Climbing": {
            "group": "Local Search",
            "complete": False,
            "optimal": False,
            "time_complexity": "O(b)",
            "space_complexity": "O(1)",
            "uses_heuristic": True,
            "suitable": False,
            "notes": "Better than simple but still can get stuck."
        },
        "Stochastic Hill Climbing": {
            "group": "Local Search",
            "complete": False,
            "optimal": False,
            "time_complexity": "O(b)",
            "space_complexity": "O(1)",
            "uses_heuristic": True,
            "suitable": False,
            "notes": "Random neighbor selection. Can escape some local optima."
        },
        "Random-Restart Hill Climbing": {
            "group": "Local Search",
            "complete": True,
            "optimal": False,
            "time_complexity": "O(?)",
            "space_complexity": "O(1)",
            "uses_heuristic": True,
            "suitable": False,
            "notes": "Complete with enough restarts. Not optimal."
        },
        "Local Beam Search": {
            "group": "Local Search",
            "complete": False,
            "optimal": False,
            "time_complexity": "O(kb)",
            "space_complexity": "O(k)",
            "uses_heuristic": True,
            "suitable": False,
            "notes": "Keeps k best states. Better than single hill climbing."
        },
        "Simulated Annealing": {
            "group": "Local Search",
            "complete": True,
            "optimal": False,
            "time_complexity": "O(?)",
            "space_complexity": "O(1)",
            "uses_heuristic": True,
            "suitable": False,
            "notes": "Can escape local optima. Not optimal. Random results."
        },
        # Complex Environments
        "AND-OR Search": {
            "group": "Complex Environments",
            "complete": True,
            "optimal": False,
            "time_complexity": "O(b^d)",
            "space_complexity": "O(bd)",
            "uses_heuristic": False,
            "suitable": False,
            "notes": "For nondeterministic environments. Not needed for standard 8-puzzle."
        },
        "No Observation": {
            "group": "Complex Environments",
            "complete": True,
            "optimal": False,
            "time_complexity": "O(2^N)",
            "space_complexity": "O(2^N)",
            "uses_heuristic": False,
            "suitable": False,
            "notes": "Uses belief states. Not needed for fully observable 8-puzzle."
        },
        "Partially Observable": {
            "group": "Complex Environments",
            "complete": True,
            "optimal": False,
            "time_complexity": "O(2^N)",
            "space_complexity": "O(2^N)",
            "uses_heuristic": False,
            "suitable": False,
            "notes": "Uses belief states with observations. Not needed for 8-puzzle."
        },
        "Online Search": {
            "group": "Complex Environments",
            "complete": True,
            "optimal": False,
            "time_complexity": "O(?)",
            "space_complexity": "O(N)",
            "uses_heuristic": False,
            "suitable": False,
            "notes": "For unknown environments. Not needed for 8-puzzle."
        },
        # CSP
        "Backtracking CSP": {
            "group": "Constraint Satisfaction",
            "complete": True,
            "optimal": False,
            "time_complexity": "O(d^n)",
            "space_complexity": "O(n)",
            "uses_heuristic": False,
            "suitable": False,
            "notes": "8-puzzle is not a static CSP. Cannot find action sequence."
        },
        "Min-Conflicts": {
            "group": "Constraint Satisfaction",
            "complete": False,
            "optimal": False,
            "time_complexity": "O(?)",
            "space_complexity": "O(n)",
            "uses_heuristic": False,
            "suitable": False,
            "notes": "For CSP repair. Not suitable for 8-puzzle path finding."
        },
        # Adversarial
        "Minimax": {
            "group": "Adversarial Search",
            "complete": True,
            "optimal": True,
            "time_complexity": "O(b^m)",
            "space_complexity": "O(bm)",
            "uses_heuristic": True,
            "suitable": False,
            "notes": "For 2-player games. 8-puzzle is single-player."
        },
        "Alpha-Beta Pruning": {
            "group": "Adversarial Search",
            "complete": True,
            "optimal": True,
            "time_complexity": "O(b^(m/2))",
            "space_complexity": "O(bm)",
            "uses_heuristic": True,
            "suitable": False,
            "notes": "Optimized Minimax. Still needs opponent."
        },
        "Expectimax": {
            "group": "Adversarial Search",
            "complete": True,
            "optimal": False,
            "time_complexity": "O(b^m)",
            "space_complexity": "O(bm)",
            "uses_heuristic": True,
            "suitable": False,
            "notes": "For stochastic games. 8-puzzle is deterministic."
        }
    }
