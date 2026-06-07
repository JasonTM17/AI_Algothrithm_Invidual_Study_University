"""
8-Puzzle AI Solver - Streamlit Application
Complete implementation with all 6 algorithm groups.
"""

import streamlit as st
import sys
import os
import time
import pandas as pd

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(PACKAGE_DIR)
sys.path.insert(0, PACKAGE_DIR)
sys.path.insert(0, PROJECT_DIR)

from core.puzzle import PuzzleState, scramble_state, parse_state, validate_state
from core.heuristics import misplaced_tiles, manhattan_distance, linear_conflict, heuristic_info
from core.metrics import get_algorithm_properties, generate_comparison_report
from core.utils import format_state_box, get_algorithm_theory
from algorithms import ALGORITHMS, get_algorithm, get_algorithm_group, list_algorithms

def configure_page():
    """Configure Streamlit only when the app is executed, not when imported by tests."""
    st.set_page_config(
        page_title="8-Puzzle AI Solver",
        page_icon="🧩",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
        .puzzle-cell {
            font-size: 24px;
            text-align: center;
            padding: 10px;
            border: 2px solid #333;
            background-color: #f0f0f0;
            color: #1a1a1a;
        }
        .puzzle-cell.blank {
            background-color: #fff;
            color: #1a1a1a;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            font-size: 16px;
        }
        .metric-card {
            background-color: var(--secondary-background-color, #f8f9fa);
            color: var(--text-color, #1a1a1a);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(128, 128, 128, 0.2);
        }
        .success-message {
            color: #2ecc71;
            font-weight: bold;
        }
        .error-message {
            color: #e74c3c;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)


def render_puzzle_board(state, title=""):
    """Render puzzle board as HTML table."""
    if title:
        st.markdown(f"**{title}**")
    
    # Create HTML table
    html = '<table style="border-collapse: collapse; margin: 10px auto;">'
    for i in range(3):
        html += '<tr>'
        for j in range(3):
            idx = i * 3 + j
            val = state[idx]
            if val == 0:
                html += f'<td style="width: 60px; height: 60px; border: 2px solid #333; text-align: center; font-size: 24px; background-color: #fff; color: #1a1a1a;">&nbsp;</td>'
            else:
                html += f'<td style="width: 60px; height: 60px; border: 2px solid #333; text-align: center; font-size: 24px; background-color: #e3f2fd; color: #1a1a1a;">{val}</td>'
        html += '</tr>'
    html += '</table>'
    
    st.markdown(html, unsafe_allow_html=True)


def render_puzzle_inline(state):
    """Render puzzle inline for tables."""
    return f"{state[0]} {state[1]} {state[2]}\n{state[3]} {state[4]} {state[5]}\n{state[6]} {state[7]} {state[8]}"


BASE_PARAMS = {"start", "goal", "trace_limit"}
LIMITED_SEARCH_PARAMS = BASE_PARAMS | {"max_nodes", "max_time_ms", "action_order"}
HEURISTIC_SEARCH_PARAMS = LIMITED_SEARCH_PARAMS | {"heuristic"}

ALGORITHM_PARAM_KEYS = {
    "BFS": LIMITED_SEARCH_PARAMS,
    "UCS": LIMITED_SEARCH_PARAMS,
    "DFS": LIMITED_SEARCH_PARAMS | {"max_depth"},
    "IDS": LIMITED_SEARCH_PARAMS | {"max_depth"},
    "Greedy": HEURISTIC_SEARCH_PARAMS,
    "A*": HEURISTIC_SEARCH_PARAMS,
    "IDA*": HEURISTIC_SEARCH_PARAMS | {"max_iterations"},
    "Simple Hill Climbing": BASE_PARAMS | {"heuristic", "max_steps", "max_time_ms", "action_order", "seed"},
    "Steepest-Ascent Hill Climbing": BASE_PARAMS | {"heuristic", "max_steps", "max_time_ms", "action_order"},
    "Stochastic Hill Climbing": BASE_PARAMS | {"heuristic", "max_steps", "max_time_ms", "action_order", "seed"},
    "Random-Restart Hill Climbing": BASE_PARAMS | {"heuristic", "max_restarts", "max_steps_per_restart", "max_time_ms", "action_order", "seed"},
    "Local Beam Search": BASE_PARAMS | {"heuristic", "beam_width", "max_steps", "max_time_ms", "action_order"},
    "Simulated Annealing": BASE_PARAMS | {"heuristic", "initial_temp", "cooling_rate", "min_temp", "max_steps", "max_time_ms", "action_order", "seed"},
    "AND-OR Search": BASE_PARAMS | {"heuristic", "max_depth", "nondeterministic_prob", "seed"},
    "No Observation": BASE_PARAMS | {"heuristic", "initial_belief_size", "max_steps", "seed"},
    "Partially Observable": BASE_PARAMS | {"heuristic", "max_steps", "seed"},
    "Online Search": BASE_PARAMS | {"heuristic", "max_steps", "seed"},
    "CSP Backtracking": BASE_PARAMS | {"max_time_steps", "max_nodes"},
    "Min-Conflicts": BASE_PARAMS | {"max_steps"},
    "Constraint Propagation": BASE_PARAMS,
    "Minimax": BASE_PARAMS | {"heuristic", "max_depth", "seed"},
    "Alpha-Beta Pruning": BASE_PARAMS | {"heuristic", "max_depth", "seed"},
    "Expectimax": BASE_PARAMS | {"heuristic", "max_depth", "success_prob", "seed"},
}

EDUCATIONAL_GROUPS = {"Complex Environments", "Constraint Satisfaction", "Adversarial Search"}


def run_selected_algorithm(name: str, params: dict):
    """Run a package algorithm with only the parameters its signature accepts."""
    allowed = ALGORITHM_PARAM_KEYS.get(name, BASE_PARAMS)
    filtered = {key: value for key, value in params.items() if key in allowed}
    result = get_algorithm(name)(**filtered)

    group = get_algorithm_group(name)
    if group in EDUCATIONAL_GROUPS:
        note = getattr(result, "notes", "")
        educational_note = "Educational demo: this group is not a natural 8-puzzle solver."
        result.notes = f"{note} {educational_note}".strip() if note else educational_note
    return result


def main():
    configure_page()
    st.title("🧩 8-Puzzle AI Solver")
    st.markdown("### Complete AI Search Algorithm Visualizer")
    
    # Initialize session state
    if 'start_state' not in st.session_state:
        st.session_state.start_state = (1, 2, 3, 5, 0, 6, 4, 7, 8)
    if 'goal_state' not in st.session_state:
        st.session_state.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    if 'results' not in st.session_state:
        st.session_state.results = []
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Start state input
        st.subheader("Start State")
        input_method = st.radio("Input Method", ["Default", "Manual", "Random"])
        
        if input_method == "Manual":
            state_str = st.text_input(
                "Enter 9 numbers (0-8)",
                value="1 2 3 5 0 6 4 7 8"
            )
            if st.button("Apply"):
                try:
                    parsed = parse_state(state_str)
                    is_valid, msg = validate_state(parsed)
                    if is_valid:
                        puzzle = PuzzleState(parsed)
                        if puzzle.is_solvable():
                            st.session_state.start_state = parsed
                            st.success("✅ Valid solvable state!")
                        else:
                            st.error("❌ State is not solvable!")
                    else:
                        st.error(f"❌ {msg}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        elif input_method == "Random":
            scramble_depth = st.slider("Scramble Depth", 5, 50, 20)
            seed = st.number_input("Seed", value=42)
            if st.button("Generate"):
                random_state = scramble_state(num_moves=scramble_depth, seed=seed)
                st.session_state.start_state = random_state.state
                st.success("✅ Generated random solvable state!")
        
        else:  # Default
            st.session_state.start_state = (1, 2, 3, 5, 0, 6, 4, 7, 8)
        
        st.divider()
        
        # Algorithm parameters
        st.subheader("Algorithm Parameters")
        heuristic = st.selectbox("Heuristic", ["manhattan", "misplaced", "linear_conflict"])
        max_nodes = st.slider("Max Nodes", 1000, 100000, 50000)
        max_time_ms = st.slider("Timeout (ms)", 5000, 60000, 30000)
        action_order = st.selectbox("Action Order", ["LRUD", "LDRU", "RLDU", "UDLR"])
        
        st.divider()
        
        # Display current states
        st.subheader("Current States")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Start State**")
            render_puzzle_board(st.session_state.start_state)
            puzzle = PuzzleState(st.session_state.start_state)
            st.caption(f"h = {manhattan_distance(st.session_state.start_state)}")
        
        with col2:
            st.markdown("**Goal State**")
            render_puzzle_board(st.session_state.goal_state)
    
    # Main content - Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎮 Play",
        "▶️ Run Algorithm",
        "📊 Trace Steps",
        "📈 Compare",
        "📚 Theory",
        "ℹ️ About"
    ])
    
    # Tab 1: Play
    with tab1:
        st.header("🎮 Interactive Play")
        
        current_state = st.session_state.start_state
        puzzle = PuzzleState(current_state)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Current Board")
            render_puzzle_board(current_state)
            
            st.markdown(f"**h(n) = {manhattan_distance(current_state, st.session_state.goal_state)}**")
            
            if current_state == st.session_state.goal_state:
                st.balloons()
                st.success("🎉 Congratulations! You solved the puzzle!")
        
        st.divider()
        
        # Manual moves
        st.subheader("Manual Moves")
        st.markdown("Click a button to move the blank tile:")
        
        col1, col2, col3, col4 = st.columns(4)
        
        neighbors = puzzle.get_neighbors()
        
        with col1:
            if st.button("⬅️ Left", width="stretch"):
                for action, neighbor in neighbors:
                    if action == 'L':
                        st.session_state.start_state = neighbor.state
                        st.rerun()
        
        with col2:
            if st.button("➡️ Right", width="stretch"):
                for action, neighbor in neighbors:
                    if action == 'R':
                        st.session_state.start_state = neighbor.state
                        st.rerun()
        
        with col3:
            if st.button("⬆️ Up", width="stretch"):
                for action, neighbor in neighbors:
                    if action == 'U':
                        st.session_state.start_state = neighbor.state
                        st.rerun()
        
        with col4:
            if st.button("⬇️ Down", width="stretch"):
                for action, neighbor in neighbors:
                    if action == 'D':
                        st.session_state.start_state = neighbor.state
                        st.rerun()
        
        if st.button("🔄 Reset to Default"):
            st.session_state.start_state = (1, 2, 3, 5, 0, 6, 4, 7, 8)
            st.rerun()
    
    # Tab 2: Run Algorithm
    with tab2:
        st.header("▶️ Run Algorithm")
        
        # Group selection
        groups = list_algorithms()
        selected_group = st.selectbox("Select Algorithm Group", list(groups.keys()))
        
        # Algorithm selection
        algorithms_in_group = groups[selected_group]
        selected_algorithm = st.selectbox("Select Algorithm", algorithms_in_group)
        
        # Group-specific parameters
        st.subheader("Parameters")
        
        params = {
            'start': st.session_state.start_state,
            'goal': st.session_state.goal_state,
            'heuristic': heuristic,
            'max_nodes': max_nodes,
            'max_time_ms': max_time_ms,
            'action_order': action_order,
            'trace_limit': 100
        }
        
        # Add group-specific params
        if selected_group == "Uninformed Search":
            if selected_algorithm == "DFS":
                params['max_depth'] = st.slider("Max Depth", 10, 100, 50)
            elif selected_algorithm == "IDS":
                params['max_depth'] = st.slider("Max Depth Limit", 10, 50, 30)
        
        elif selected_group == "Informed Search":
            if selected_algorithm == "IDA*":
                params['max_iterations'] = st.slider("Max Iterations", 10, 200, 100)
        
        elif selected_group == "Local Search":
            if "Hill Climbing" in selected_algorithm:
                params['max_steps'] = st.slider("Max Steps", 100, 1000, 500)
                if "Random-Restart" in selected_algorithm:
                    params['max_restarts'] = st.slider("Max Restarts", 10, 100, 50)
                    params['max_steps_per_restart'] = st.slider("Steps per Restart", 50, 500, 200)
            elif selected_algorithm == "Local Beam Search":
                params['beam_width'] = st.slider("Beam Width", 2, 10, 4)
                params['max_steps'] = st.slider("Max Steps", 100, 1000, 500)
            elif selected_algorithm == "Simulated Annealing":
                params['initial_temp'] = st.slider("Initial Temperature", 10.0, 500.0, 100.0)
                params['cooling_rate'] = st.slider("Cooling Rate", 0.9, 0.999, 0.995)
                params['min_temp'] = st.slider("Min Temperature", 0.001, 0.1, 0.01)
                params['max_steps'] = st.slider("Max Steps", 1000, 20000, 10000)
        
        elif selected_group == "Complex Environments":
            if selected_algorithm == "AND-OR Search":
                params['max_depth'] = st.slider("Max Depth", 10, 50, 20)
                params['nondeterministic_prob'] = st.slider("Nondeterministic Prob", 0.0, 0.3, 0.1)
            elif selected_algorithm == "No Observation":
                params['initial_belief_size'] = st.slider("Initial Belief Size", 2, 10, 3)
                params['max_steps'] = st.slider("Max Steps", 50, 200, 100)
            else:
                params['max_steps'] = st.slider("Max Steps", 100, 1000, 500)
        
        elif selected_group == "Constraint Satisfaction":
            if selected_algorithm == "CSP Backtracking":
                params['max_time_steps'] = st.slider("Max Time Steps", 5, 30, 10)
            else:
                params['max_steps'] = st.slider("Max Steps", 100, 2000, 1000)
        
        elif selected_group == "Adversarial Search":
            params['max_depth'] = st.slider("Search Depth", 2, 10, 4)
            if selected_algorithm == "Expectimax":
                params['success_prob'] = st.slider("Success Probability", 0.5, 1.0, 0.8)
        
        # Run button
        if st.button("🚀 Run Algorithm", type="primary"):
            with st.spinner(f"Running {selected_algorithm}..."):
                result = run_selected_algorithm(selected_algorithm, params)
                
                st.session_state.current_result = result
                st.session_state.results.append(result)
        
        # Display result
        if 'current_result' in st.session_state:
            result = st.session_state.current_result
            
            st.divider()
            st.subheader("📊 Results")
            
            # Success/failure
            if result.success:
                st.success(f"✅ {result.message}")
            else:
                st.error(f"❌ {result.message}")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Path Length", result.path_cost if result.path_cost else "N/A")
            
            with col2:
                st.metric("Nodes Expanded", result.nodes_expanded)
            
            with col3:
                st.metric("Nodes Generated", result.nodes_generated)
            
            with col4:
                st.metric("Runtime", f"{result.runtime_ms:.2f} ms")
            
            # Path visualization
            if result.success and result.path:
                st.subheader("🛤️ Solution Path")
                
                path_cols = st.columns(min(len(result.path), 10))
                
                for i, (col, state) in enumerate(zip(path_cols, result.path[:10])):
                    with col:
                        if i < len(result.actions):
                            st.markdown(f"**Step {i}**: {result.actions[i] if i > 0 else 'Start'}")
                        else:
                            st.markdown(f"**Step {i}**")
                        render_puzzle_board(state.state)
                
                if len(result.path) > 10:
                    st.info(f"... and {len(result.path) - 10} more steps")
                
                # Actions
                st.markdown(f"**Actions:** `{' → '.join(result.actions)}`")
            
            # Properties
            st.subheader("📋 Algorithm Properties")
            st.markdown(f"- **Optimal:** {result.optimal}")
            st.markdown(f"- **Complete:** {result.complete}")
            if result.notes:
                st.info(f"ℹ️ {result.notes}")
    
    # Tab 3: Trace Steps
    with tab3:
        st.header("📊 Step-by-Step Trace")
        
        if 'current_result' in st.session_state and st.session_state.current_result.trace:
            trace = st.session_state.current_result.trace
            
            st.subheader(f"Trace for {st.session_state.current_result.algorithm}")
            
            # Display trace as table
            df = pd.DataFrame(trace)
            st.dataframe(df, width="stretch", height=400)
            
            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Trace CSV",
                csv,
                f"trace_{st.session_state.current_result.algorithm}.csv",
                "text/csv"
            )
        else:
            st.info("Run an algorithm first to see the trace.")
    
    # Tab 4: Compare
    with tab4:
        st.header("📈 Algorithm Comparison")
        
        st.markdown("Run multiple algorithms and compare their performance.")
        
        # Select algorithms to compare
        all_algos = []
        for group, algos in list_algorithms().items():
            all_algos.extend(algos)
        
        selected_algos = st.multiselect(
            "Select Algorithms to Compare",
            all_algos,
            default=["BFS", "A*", "Greedy", "IDS"]
        )
        
        if st.button("🔄 Run Comparison", type="primary"):
            if not selected_algos:
                st.warning("Please select at least one algorithm.")
            else:
                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, algo_name in enumerate(selected_algos):
                    status_text.text(f"Running {algo_name}...")
                    
                    # Basic params
                    params = {
                        'start': st.session_state.start_state,
                        'goal': st.session_state.goal_state,
                        'heuristic': heuristic,
                        'max_nodes': max_nodes,
                        'max_time_ms': max_time_ms,
                        'action_order': action_order,
                        'trace_limit': 10
                    }
                    
                    try:
                        result = run_selected_algorithm(algo_name, params)
                        results.append(result)
                    except Exception as e:
                        st.warning(f"{algo_name} failed: {e}")
                    
                    progress_bar.progress((i + 1) / len(selected_algos))
                
                st.session_state.comparison_results = results
                status_text.text("Done!")
        
        # Display comparison
        if 'comparison_results' in st.session_state and st.session_state.comparison_results:
            results = st.session_state.comparison_results
            
            st.subheader("Comparison Table")
            
            comparison_data = []
            for r in results:
                comparison_data.append({
                    "Algorithm": r.algorithm,
                    "Group": r.group,
                    "Success": "✅" if r.success else "❌",
                    "Path Length": r.path_cost if r.success else "N/A",
                    "Expanded": r.nodes_expanded,
                    "Generated": r.nodes_generated,
                    "Runtime (ms)": f"{r.runtime_ms:.2f}",
                    "Optimal": r.optimal
                })
            
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, width="stretch")
            
            # Best performers
            st.subheader("🏆 Best Performers")
            
            successful = [r for r in results if r.success]
            
            if successful:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fastest = min(successful, key=lambda x: x.runtime_ms)
                    st.metric("Fastest", fastest.algorithm, f"{fastest.runtime_ms:.2f} ms")
                
                with col2:
                    shortest = min(successful, key=lambda x: x.path_cost if x.path_cost else float('inf'))
                    st.metric("Shortest Path", shortest.algorithm, f"{shortest.path_cost} moves")
                
                with col3:
                    most_efficient = min(successful, key=lambda x: x.nodes_expanded)
                    st.metric("Most Efficient", most_efficient.algorithm, f"{most_efficient.nodes_expanded} nodes")
            
            # Analysis
            st.subheader("📝 Analysis")
            
            if successful:
                st.markdown("""
                **Key Observations:**
                - **BFS/UCS**: Optimal for unit cost, but high memory usage
                - **A***: Best balance of speed and optimality with good heuristic
                - **Greedy**: Fast but not optimal
                - **IDS**: Optimal like BFS but less memory
                - **Local Search**: Fast but may not find solution
                """)
    
    # Tab 5: Theory
    with tab5:
        st.header("📚 Algorithm Theory")
        
        # Select algorithm
        groups = list_algorithms()
        all_algos = []
        for group, algos in groups.items():
            all_algos.extend(algos)
        
        selected = st.selectbox("Select Algorithm", all_algos)
        
        theory = get_algorithm_theory(selected)
        props = get_algorithm_properties().get(selected, {})
        
        # Display theory
        st.subheader(theory.get('name', selected))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Group:** {theory.get('group', props.get('group', 'Unknown'))}")
            st.markdown(f"**Description:** {theory.get('description', 'N/A')}")
            st.markdown(f"**Idea:** {theory.get('idea', 'N/A')}")
            st.markdown(f"**Data Structure:** {theory.get('data_structure', 'N/A')}")
        
        with col2:
            st.markdown(f"**Complete:** {theory.get('complete', props.get('complete', 'Unknown'))}")
            st.markdown(f"**Optimal:** {theory.get('optimal', props.get('optimal', 'Unknown'))}")
            st.markdown(f"**Time:** {theory.get('time_complexity', props.get('time_complexity', 'N/A'))}")
            st.markdown(f"**Space:** {theory.get('space_complexity', props.get('space_complexity', 'N/A'))}")
        
        st.divider()
        
        st.markdown(f"**Strengths:** {theory.get('strengths', props.get('strengths', 'N/A'))}")
        st.markdown(f"**Weaknesses:** {theory.get('weaknesses', props.get('weaknesses', 'N/A'))}")
        st.markdown(f"**When to Use:** {theory.get('when_to_use', props.get('suitable', 'N/A'))}")
        
        st.info(f"💡 **Exam Tips:** {theory.get('exam_tips', 'N/A')}")
        
        # Suitability for 8-puzzle
        st.subheader("🎯 Suitability for 8-Puzzle")
        suitable = props.get('suitable', False)
        if suitable:
            st.success(f"✅ This algorithm is suitable for 8-puzzle. {props.get('notes', '')}")
        else:
            st.warning(f"⚠️ This algorithm may not be ideal for 8-puzzle. {props.get('notes', '')}")
    
    # Tab 6: About
    with tab6:
        st.header("ℹ️ About This Project")
        
        st.markdown("""
        ### 8-Puzzle AI Solver
        
        This is a complete implementation of AI search algorithms for the 8-puzzle problem.
        
        **Features:**
        - ✅ 6 algorithm groups with 24+ algorithms
        - ✅ Step-by-step trace visualization
        - ✅ Algorithm comparison
        - ✅ Interactive play mode
        - ✅ Theory explanations
        
        **Algorithm Groups:**
        1. **Uninformed Search**: BFS, DFS, UCS, IDS
        2. **Informed Search**: Greedy, A*, IDA*
        3. **Local Search**: Hill Climbing variants, Beam, Simulated Annealing
        4. **Complex Environments**: AND-OR, No Observation, Partially Observable, Online
        5. **Constraint Satisfaction**: Backtracking, Min-Conflicts
        6. **Adversarial Search**: Minimax, Alpha-Beta, Expectimax
        
        **Heuristics:**
        - Misplaced Tiles
        - Manhattan Distance
        - Linear Conflict
        
        **Note:** Some algorithms (CSP, Adversarial) are included for educational purposes
        as 8-puzzle is not naturally a CSP or 2-player game.
        
        ---
        
        **Created for AI Education** 🎓
        """)


if __name__ == "__main__":
    main()
