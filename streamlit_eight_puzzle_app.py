"""Bilingual Streamlit UI for the 8-puzzle search visualizer."""

from __future__ import annotations

from html import escape
from typing import Any, Dict

import streamlit as st

import eight_puzzle_search_app as puzzle


TEXT: Dict[str, Dict[str, str]] = {
    "vi": {
        "page_title": "8-Puzzle Search Lab",
        "page_subtitle": "Trực quan hóa BFS, UCS, A*, IDA* và các thuật toán tìm kiếm cục bộ trên cùng một ma trận.",
        "advanced_settings": "Thiết lập nâng cao",
        "result_details": "Bảng kết quả chi tiết",
        "summary_tab": "Summary",
        "academic_trace_tab": "Trace",
        "heuristics_tab": "Heuristics",
        "experiment_tab": "Experiment",
        "path_player_tab": "Path Player",
        "report_tab": "Report",
        "controls": "Điều khiển",
        "language": "Ngôn ngữ / Language",
        "algorithm": "Thuật toán",
        "algorithm_group": "Nhóm thuật toán",
        "heuristic": "Heuristic",
        "seed": "Seed",
        "scramble_moves": "Số bước tự trộn",
        "shuffle": "Tự trộn ma trận",
        "max_expansions": "Giới hạn mở rộng node",
        "max_trace_rows": "Số dòng trace tối đa",
        "frontier_preview": "Số frontier xem trước",
        "reached_preview": "Số reached xem trước",
        "ids_depth": "Độ sâu IDS tối đa",
        "ida_iterations": "Số vòng IDA*",
        "local_steps": "Số bước local tối đa",
        "random_restarts": "Số lần random restart",
        "beam_width": "Độ rộng beam",
        "board_panel": "Ma trận 8-puzzle",
        "initial_shuffle": "Trạng thái bắt đầu hiện tại được tự trộn 20 bước từ Goal.",
        "shuffle_note": "Đã tự trộn ma trận {moves} bước từ Goal (seed={seed}, lần {count}).",
        "demo_preset": "Preset demo",
        "load_preset": "Dùng preset",
        "preset_note": "Đang dùng preset demo: {name}.",
        "start_state": "Trạng thái bắt đầu",
        "goal_state": "Trạng thái đích",
        "goal_caption": "Đích cố định: đưa ô trống 0 về góc dưới bên phải.",
        "goal_and_input": "Goal và nhập tay",
        "custom_start": "Nhập ma trận bắt đầu",
        "custom_help": "Nhập 9 số từ 0 đến 8, ví dụ: 1 2 3 4 5 6 0 7 8",
        "use_custom": "Dùng ma trận này",
        "run": "Chạy thuật toán",
        "run_selected": "Chạy thuật toán đã chọn",
        "compare_all": "So sánh tất cả thuật toán",
        "notes": (
            "UCS dùng chi phí mỗi bước bằng 1 nên thường cho độ dài nghiệm giống BFS. "
            "A* với Manhattan tối ưu vì Manhattan admissible cho 8-puzzle. "
            "Greedy có thể nhanh nhưng không đảm bảo tối ưu. "
            "Leo đồi và Local Beam Search có thể kẹt ở cực trị cục bộ hoặc plateau."
        ),
        "choose_action": "Chọn một thao tác trong vùng chạy thuật toán.",
        "run_summary": "Bảng tổng kết",
        "final_state": "Trạng thái cuối",
        "best_final_state": "Trạng thái tốt nhất / cuối hiện tại",
        "solution_path": "Các bước lời giải",
        "step": "Bước",
        "start": "Bắt đầu",
        "trace": "Bảng Node / Frontier / Reached",
        "algorithm_certificate": "Algorithm Certificate",
        "certificate_status": "Trạng thái kiểm chứng",
        "certificate_pass": "PASS",
        "certificate_fail": "FAIL",
        "heuristic_inspector": "Heuristic Inspector",
        "heuristic_totals": "Tổng hợp heuristic",
        "tile_contributions": "Đóng góp từng ô",
        "linear_conflicts": "Các cặp Linear Conflict",
        "no_linear_conflicts": "Không có cặp Linear Conflict trong trạng thái này.",
        "trace_story": "Why This Node?",
        "experiment_lab": "Experiment Lab",
        "run_experiment": "Chạy Experiment Lab",
        "download_experiment": "Tải báo cáo experiment",
        "path_playback": "Path playback",
        "coursework_report": "Coursework report",
        "download_report": "Tải báo cáo Markdown",
        "report_preview": "Nội dung báo cáo",
        "benchmark": "Benchmark demo nhỏ",
        "run_benchmark": "Chạy benchmark preset",
        "benchmark_caption": "Benchmark dùng preset cố định và tắt trace để đo nhanh, phù hợp đưa vào báo cáo.",
        "comparison": "Bảng so sánh thuật toán",
        "academic_panel": "Cơ sở học thuật",
        "grading_checklist": "Checklist nộp bài",
        "heuristic_usage": "Cách dùng h(n)",
        "peas_model": "PEAS",
        "problem_variant": "Dạng bài toán theo thuật toán",
        "problem_definition": "Mô hình bài toán",
        "algorithm_profile": "Hồ sơ thuật toán đang chọn",
        "evaluation_criteria": "Tiêu chí đánh giá",
        "trace_glossary": "Ý nghĩa Node / Frontier / Reached",
        "objective": "Mục tiêu",
        "state_space": "Không gian trạng thái",
        "transition_model": "Mô hình chuyển trạng thái",
        "heuristic_formula": "Công thức heuristic",
        "priority_basis": "Cơ sở ưu tiên g(n), h(n), f(n)",
        "primary_basis": "Dựa chính trên",
        "priority_rule": "Quy tắc ưu tiên",
        "uses_component": "Có dùng?",
        "component_meaning": "Ý nghĩa trong thuật toán đang chọn",
        "yes": "Có",
        "no": "Không",
        "implicit": "Gián tiếp",
        "path_player": "Theo dõi đường đi từng bước",
        "previous_step": "Bước trước",
        "next_step": "Bước sau",
        "step_slider": "Chọn bước cần quan sát",
        "before_move": "Trạng thái trước bước đi",
        "after_move": "Trạng thái hiện tại",
        "current_action": "Hành động vừa thực hiện",
        "next_action": "Hành động tiếp theo",
        "route_sequence": "Chuỗi hành động",
        "route_table": "Bảng đường đi đầy đủ",
        "no_solution_path": "Thuật toán chưa tìm được đường đi tới Goal nên không có bước để phát lại.",
        "total_steps": "Tổng số bước",
        "sa_initial_temp": "Nhiệt độ ban đầu SA",
        "sa_cooling_rate": "Tỷ lệ làm nguội",
        "sa_min_temp": "Nhiệt độ tối thiểu",
        "sa_max_steps": "Số bước SA tối đa",
    },
    "en": {
        "page_title": "8-Puzzle Search Lab",
        "page_subtitle": "Visualize BFS, UCS, A*, IDA*, and local search algorithms on the same board.",
        "advanced_settings": "Advanced settings",
        "result_details": "Detailed result table",
        "summary_tab": "Summary",
        "academic_trace_tab": "Trace",
        "heuristics_tab": "Heuristics",
        "experiment_tab": "Experiment",
        "path_player_tab": "Path Player",
        "report_tab": "Report",
        "controls": "Controls",
        "language": "Language / Ngôn ngữ",
        "algorithm": "Algorithm",
        "algorithm_group": "Algorithm group",
        "heuristic": "Heuristic",
        "seed": "Seed",
        "scramble_moves": "Random scramble moves",
        "shuffle": "Shuffle matrix",
        "max_expansions": "Max expansions",
        "max_trace_rows": "Max trace rows",
        "frontier_preview": "Frontier preview",
        "reached_preview": "Reached preview",
        "ids_depth": "IDS max depth",
        "ida_iterations": "IDA* iterations",
        "local_steps": "Local max steps",
        "random_restarts": "Random restarts",
        "beam_width": "Beam width",
        "board_panel": "8-puzzle matrix",
        "initial_shuffle": "The current start state was shuffled 20 moves from Goal.",
        "shuffle_note": "Shuffled the matrix {moves} moves from Goal (seed={seed}, run {count}).",
        "demo_preset": "Demo preset",
        "load_preset": "Use preset",
        "preset_note": "Using demo preset: {name}.",
        "start_state": "Start state",
        "goal_state": "Goal state",
        "goal_caption": "Fixed target: move blank tile 0 to the bottom-right corner.",
        "goal_and_input": "Goal and custom input",
        "custom_start": "Custom start state",
        "custom_help": "Enter 9 numbers from 0 to 8, for example: 1 2 3 4 5 6 0 7 8",
        "use_custom": "Use custom state",
        "run": "Run",
        "run_selected": "Run selected algorithm",
        "compare_all": "Compare all algorithms",
        "notes": puzzle.comparison_notes(),
        "choose_action": "Choose an action from the run panel.",
        "run_summary": "Run summary",
        "final_state": "Final state",
        "best_final_state": "Best / current final state",
        "solution_path": "Solution path",
        "step": "Step",
        "start": "Start",
        "trace": "Node / Frontier / Reached trace",
        "algorithm_certificate": "Algorithm Certificate",
        "certificate_status": "Certificate status",
        "certificate_pass": "PASS",
        "certificate_fail": "FAIL",
        "heuristic_inspector": "Heuristic Inspector",
        "heuristic_totals": "Heuristic totals",
        "tile_contributions": "Tile contributions",
        "linear_conflicts": "Linear Conflict pairs",
        "no_linear_conflicts": "No Linear Conflict pairs in this state.",
        "trace_story": "Why This Node?",
        "experiment_lab": "Experiment Lab",
        "run_experiment": "Run Experiment Lab",
        "download_experiment": "Download experiment report",
        "path_playback": "Path playback",
        "coursework_report": "Coursework report",
        "download_report": "Download Markdown report",
        "report_preview": "Report content",
        "benchmark": "Small demo benchmark",
        "run_benchmark": "Run preset benchmark",
        "benchmark_caption": "Benchmark uses fixed presets and disables trace for quick report-ready measurements.",
        "comparison": "Algorithm comparison",
        "academic_panel": "Academic foundation",
        "grading_checklist": "Submission checklist",
        "heuristic_usage": "How h(n) is used",
        "peas_model": "PEAS",
        "problem_variant": "Problem formulation by algorithm",
        "problem_definition": "Problem model",
        "algorithm_profile": "Selected algorithm profile",
        "evaluation_criteria": "Evaluation criteria",
        "trace_glossary": "Meaning of Node / Frontier / Reached",
        "objective": "Objective",
        "state_space": "State space",
        "transition_model": "Transition model",
        "heuristic_formula": "Heuristic formula",
        "priority_basis": "Priority basis: g(n), h(n), f(n)",
        "primary_basis": "Primary basis",
        "priority_rule": "Priority rule",
        "uses_component": "Used?",
        "component_meaning": "Meaning in the selected algorithm",
        "yes": "Yes",
        "no": "No",
        "implicit": "Implicit",
        "path_player": "Step-by-step path viewer",
        "previous_step": "Previous step",
        "next_step": "Next step",
        "step_slider": "Select step to inspect",
        "before_move": "State before the move",
        "after_move": "Current state",
        "current_action": "Action just applied",
        "next_action": "Next action",
        "route_sequence": "Action sequence",
        "route_table": "Full route table",
        "no_solution_path": "The algorithm has not found a route to the Goal, so there are no steps to replay.",
        "total_steps": "Total steps",
        "sa_initial_temp": "SA initial temperature",
        "sa_cooling_rate": "SA cooling rate",
        "sa_min_temp": "SA minimum temperature",
        "sa_max_steps": "SA max steps",
    },
}

HELP: Dict[str, Dict[str, str]] = {
    "vi": {
        "language": "Đổi toàn bộ nhãn và giải thích trong app giữa Tiếng Việt và English.",
        "algorithm": "Chọn thuật toán tìm kiếm để chạy trên cùng trạng thái Start hiện tại.",
        "heuristic": "Chọn hàm h(n): Misplaced Tiles (số ô sai vị trí) hoặc Manhattan Distance (tổng khoảng cách từng ô).",
        "seed": "Seed điều khiển tính ngẫu nhiên. Cùng seed và cùng số bước trộn sẽ tái tạo được ma trận.",
        "scramble_moves": "Số bước đi ngẫu nhiên từ Goal để tạo Start. Số lớn hơn thường làm bài khó hơn.",
        "shuffle": "Tạo Start mới bằng cách đi ngẫu nhiên từ Goal, nên trạng thái luôn solvable.",
        "max_expansions": "Giới hạn số node được mở rộng để tránh thuật toán chạy quá lâu hoặc treo app.",
        "max_trace_rows": "Giới hạn số dòng bảng Node / Frontier / Reached hiển thị trong app.",
        "frontier_preview": "Số trạng thái frontier được xem trước trong mỗi dòng trace.",
        "reached_preview": "Số trạng thái reached được xem trước trong mỗi dòng trace.",
        "ids_depth": "Độ sâu tối đa cho IDS. Nếu nghiệm sâu hơn giới hạn này, IDS có thể không tìm thấy.",
        "ida_iterations": "Số lần tăng threshold tối đa của IDA*.",
        "local_steps": "Giới hạn số bước cho các thuật toán tìm kiếm cục bộ như hill climbing và beam search.",
        "random_restarts": "Số lần khởi động lại của Random-Restart Hill Climbing để giảm kẹt local optimum.",
        "beam_width": "Số trạng thái tốt nhất được giữ lại ở mỗi vòng của Local Beam Search.",
        "custom_start": "Nhập 9 số từ 0 đến 8. Ví dụ: 1 2 3 4 5 6 0 7 8.",
        "use_custom": "Áp dụng ma trận bạn nhập làm Start state hiện tại.",
        "run_selected": "Chạy thuật toán đang chọn và hiển thị lời giải, trace, g(n), h(n), f(n).",
        "compare_all": "Chạy tất cả thuật toán trên cùng Start để so sánh Expanded, Generated, Runtime và Optimal.",
        "previous_step": "Lùi lại một bước trong đường đi lời giải.",
        "next_step": "Tiến tới một bước trong đường đi lời giải.",
        "step_slider": "Kéo để nhảy tới bước bất kỳ trong lời giải.",
        "metric_step": "Chỉ số bước hiện tại trên tổng số bước của lời giải.",
        "metric_g": "g(n): chi phí thật từ Start đến trạng thái hiện tại, ở đây bằng số bước đã đi.",
        "metric_h": "h(n): heuristic ước lượng số bước còn lại từ trạng thái hiện tại đến Goal.",
        "metric_f": "f(n)=g(n)+h(n), dùng làm priority trong A* và threshold trong IDA*.",
        "metric_total_steps": "Tổng số hành động trong đường đi lời giải tìm được.",
        "board_tile": "Ô {value} tại hàng {row}, cột {col}.",
        "blank_tile": "Ô trống 0 tại hàng {row}, cột {col}; đây là ô được di chuyển trong 8-Puzzle.",
        "start_board": "Ma trận ban đầu mà thuật toán cần biến đổi thành Goal.",
        "goal_board": "Ma trận đích cố định. Thuật toán thành công khi Start biến thành ma trận này.",
        "sa_initial_temp": "Nhiệt độ ban đầu cao cho phép chấp nhận nhiều bước đi xấu hơn ban đầu.",
        "sa_cooling_rate": "Tỷ lệ giảm nhiệt độ mỗi bước. Gần 1 = làm nguội chậm, khám phá nhiều hơn.",
        "sa_min_temp": "Dừng khi nhiệt độ xuống dưới giá trị này.",
        "sa_max_steps": "Giới hạn số bước để tránh chạy vô hạn.",
    },
    "en": {
        "language": "Switch all labels and explanations between Vietnamese and English.",
        "algorithm": "Choose the search algorithm to run on the current Start state.",
        "heuristic": "Choose h(n): Misplaced Tiles (number of wrong tiles) or Manhattan Distance (sum of tile grid distances).",
        "seed": "Controls randomness. The same seed and scramble depth reproduce the same matrix.",
        "scramble_moves": "Number of random legal moves from Goal used to create Start. Larger values are usually harder.",
        "shuffle": "Creates a new Start by walking randomly from Goal, so the state is always solvable.",
        "max_expansions": "Limits expanded nodes to prevent very long runs or UI hangs.",
        "max_trace_rows": "Limits rows shown in the Node / Frontier / Reached trace table.",
        "frontier_preview": "Number of frontier states previewed in each trace row.",
        "reached_preview": "Number of reached states previewed in each trace row.",
        "ids_depth": "Maximum depth for IDS. If the solution is deeper, IDS may not find it.",
        "ida_iterations": "Maximum number of threshold increases for IDA*.",
        "local_steps": "Step limit for local search algorithms such as hill climbing and beam search.",
        "random_restarts": "Number of restarts for Random-Restart Hill Climbing to reduce local optimum risk.",
        "beam_width": "Number of best states retained at each Local Beam Search iteration.",
        "custom_start": "Enter 9 numbers from 0 to 8. Example: 1 2 3 4 5 6 0 7 8.",
        "use_custom": "Apply the entered matrix as the current Start state.",
        "run_selected": "Run the selected algorithm and show solution path, trace, g(n), h(n), f(n).",
        "compare_all": "Run all algorithms on the same Start to compare Expanded, Generated, Runtime, and Optimality.",
        "previous_step": "Move one step backward in the solution path.",
        "next_step": "Move one step forward in the solution path.",
        "step_slider": "Drag to jump to any solution step.",
        "metric_step": "Current step index over total solution steps.",
        "metric_g": "g(n): actual path cost from Start to the current state; here it equals moves made.",
        "metric_h": "h(n): heuristic estimate of remaining moves from the current state to Goal.",
        "metric_f": "f(n)=g(n)+h(n), used as priority in A* and threshold in IDA*.",
        "metric_total_steps": "Total number of actions in the found solution path.",
        "board_tile": "Tile {value} at row {row}, column {col}.",
        "blank_tile": "Blank tile 0 at row {row}, column {col}; this is the movable 8-Puzzle tile.",
        "start_board": "Initial matrix that the algorithm must transform into Goal.",
        "goal_board": "Fixed target matrix. The algorithm succeeds when Start becomes this matrix.",
        "sa_initial_temp": "High initial temperature allows accepting more bad moves early.",
        "sa_cooling_rate": "Temperature decay per step. Closer to 1 = slower cooling, more exploration.",
        "sa_min_temp": "Stop when temperature drops below this threshold.",
        "sa_max_steps": "Maximum iterations to prevent infinite runs.",
    },
}

TABLE_COLUMNS: Dict[str, Dict[str, str]] = {
    "vi": {
        "Group": "Nhóm",
        "Algorithm": "Thuật toán",
        "Found": "Tìm thấy",
        "Path Length": "Độ dài đường đi",
        "Expanded": "Node đã mở rộng",
        "Generated": "Node đã sinh",
        "Max Frontier": "Frontier lớn nhất",
        "Reached": "Reached",
        "Runtime ms": "Thời gian ms",
        "Optimal": "Tối ưu",
        "Complete": "Đầy đủ",
        "Memory": "Bộ nhớ",
        "Message": "Ghi chú",
        "Path Cost": "Chi phí đường đi",
        "Optimal Gap": "Độ lệch tối ưu",
        "Metric": "Chỉ số",
        "Baseline Cost": "Chi phí chuẩn",
        "Step": "Bước",
        "Action": "Hành động",
        "Depth": "Độ sâu",
        "Priority Rule": "Quy tắc ưu tiên",
        "Selection Key": "Khóa chọn node",
        "Generated Children": "Child sinh ra",
        "Skipped States": "State bỏ qua",
        "Decision/Note": "Quyết định / Ghi chú",
        "State": "Trạng thái",
        "Check": "Kiểm chứng",
        "Value": "Giá trị",
        "Preset": "Preset",
        "Component": "Thành phần",
        "Criterion": "Tiêu chí",
        "Academic meaning": "Ý nghĩa học thuật",
        "Trace column": "Cột trace",
        "Definition": "Định nghĩa",
        "Tile": "Ô",
        "Current": "Vị trí hiện tại",
        "Goal": "Vị trí đích",
        "Misplaced": "Sai vị trí",
        "Manhattan": "Manhattan",
        "In Goal Row": "Đúng hàng đích",
        "In Goal Column": "Đúng cột đích",
        "Direction": "Hướng",
        "Line": "Dòng/cột",
        "Tile A": "Ô A",
        "Tile B": "Ô B",
        "Current Order": "Thứ tự hiện tại",
        "Goal Order": "Thứ tự ở goal",
        "Penalty": "Phạt",
        "Why This Node": "Vì sao chọn node này",
        "Heuristic": "Heuristic",
        "Family": "Nhóm",
        "Selection rule": "Quy tắc chọn node",
        "Evaluation function": "Hàm đánh giá",
        "Guarantee": "Đảm bảo",
        "Main limitation": "Hạn chế chính",
        "Item": "Mục",
        "Status": "Trạng thái",
        "Evidence": "Minh chứng",
        "Why it matters": "Ý nghĩa học thuật",
    },
    "en": {},
}

ACTION_LABELS: Dict[str, Dict[str, str]] = {
    "vi": {
        "Start": "Bắt đầu",
        "Up": "Lên",
        "Down": "Xuống",
        "Left": "Trái",
        "Right": "Phải",
    },
    "en": {},
}

ALGORITHM_PROFILES: Dict[str, Dict[str, Dict[str, str]]] = {
    "vi": {
        "BFS": {
            "Family": "Tìm kiếm mù / không dùng heuristic",
            "Selection rule": "Luôn mở node nông nhất trong hàng đợi FIFO.",
            "Evaluation function": "f(n) = depth(n)",
            "Guarantee": "Đầy đủ và tối ưu khi mọi bước có chi phí bằng nhau.",
            "Main limitation": "Tốn bộ nhớ vì phải giữ toàn bộ frontier theo từng tầng.",
            "pseudo": "frontier <- FIFO(start)\nwhile frontier not empty:\n    node <- pop_front(frontier)\n    if node is goal: return solution\n    expand node and append unseen children",
        },
        "DFS": {
            "Family": "Tìm kiếm mù / không dùng heuristic",
            "Selection rule": "Luôn mở node sâu nhất trong stack LIFO.",
            "Evaluation function": "f(n) = depth-first order",
            "Guarantee": "Không tối ưu; trong app được chặn bởi giới hạn độ sâu/mở rộng.",
            "Main limitation": "Có thể đi sâu vào nhánh kém và bỏ lỡ nghiệm nông.",
            "pseudo": "frontier <- Stack(start)\nwhile frontier not empty:\n    node <- pop(frontier)\n    if node is goal: return solution\n    if depth limit not reached: push children",
        },
        "UCS": {
            "Family": "Tìm kiếm theo chi phí đường đi",
            "Selection rule": "Mở node có g(n) nhỏ nhất trong priority queue.",
            "Evaluation function": "f(n) = g(n)",
            "Guarantee": "Đầy đủ và tối ưu với chi phí không âm; với 8-puzzle c=1 nên gần BFS.",
            "Main limitation": "Không dùng tri thức đích nên có thể mở nhiều node.",
            "pseudo": "frontier <- PriorityQueue(start, priority=g)\nwhile frontier not empty:\n    node <- pop_lowest_g(frontier)\n    if node is goal: return solution\n    relax children by path cost",
        },
        "IDS": {
            "Family": "Tìm kiếm lặp sâu dần",
            "Selection rule": "Chạy Depth-Limited Search với giới hạn 0,1,2,...",
            "Evaluation function": "f(n) = depth limit iteration",
            "Guarantee": "Tối ưu theo số bước nếu giới hạn đủ lớn và chi phí bước bằng nhau.",
            "Main limitation": "Lặp lại việc mở node ở các tầng nông.",
            "pseudo": "for limit in 0..L:\n    result <- depth_limited_search(start, limit)\n    if result found: return result",
        },
        "Greedy": {
            "Family": "Tìm kiếm có thông tin",
            "Selection rule": "Mở node có h(n) nhỏ nhất.",
            "Evaluation function": "f(n) = h(n)",
            "Guarantee": "Không đảm bảo tối ưu.",
            "Main limitation": "Dễ bị heuristic dẫn vào đường ngắn hạn nhưng không tốt toàn cục.",
            "pseudo": "frontier <- PriorityQueue(start, priority=h)\nwhile frontier not empty:\n    node <- pop_lowest_h(frontier)\n    if node is goal: return solution\n    expand and rank children by h",
        },
        "A*": {
            "Family": "Tìm kiếm có thông tin, tối ưu theo heuristic admissible",
            "Selection rule": "Mở node có g(n)+h(n) nhỏ nhất.",
            "Evaluation function": "f(n) = g(n) + h(n)",
            "Guarantee": "Tối ưu nếu h admissible; Manhattan admissible cho 8-puzzle.",
            "Main limitation": "Có thể tốn bộ nhớ vì vẫn giữ frontier và best-g.",
            "pseudo": "frontier <- PriorityQueue(start, priority=g+h)\nwhile frontier not empty:\n    node <- pop_lowest_f(frontier)\n    if node is goal: return solution\n    relax children if a lower g is found",
        },
        "IDA*": {
            "Family": "A* lặp sâu theo ngưỡng f",
            "Selection rule": "DFS nhưng cắt nhánh khi f(n) vượt threshold.",
            "Evaluation function": "f(n) = g(n) + h(n), threshold tăng dần",
            "Guarantee": "Tối ưu với heuristic admissible nếu không bị giới hạn vòng lặp.",
            "Main limitation": "Có thể mở lại node nhiều lần qua các ngưỡng.",
            "pseudo": "threshold <- h(start)\nrepeat:\n    run DFS bounded by f <= threshold\n    if goal found: return solution\n    threshold <- smallest f that exceeded threshold",
        },
        "Simple Hill Climbing": {
            "Family": "Tìm kiếm cục bộ",
            "Selection rule": "Chọn láng giềng cải thiện đầu tiên.",
            "Evaluation function": "minimize h(n)",
            "Guarantee": "Không đầy đủ, không tối ưu.",
            "Main limitation": "Dễ kẹt local optimum hoặc plateau.",
            "pseudo": "current <- start\nwhile improvement exists:\n    move to first neighbor with lower h\nreturn current",
        },
        "Steepest-Ascent Hill Climbing": {
            "Family": "Tìm kiếm cục bộ",
            "Selection rule": "Chọn láng giềng có h(n) nhỏ nhất trong toàn bộ neighbors.",
            "Evaluation function": "minimize h(n)",
            "Guarantee": "Không đầy đủ, không tối ưu.",
            "Main limitation": "Vẫn kẹt local optimum dù xét toàn bộ láng giềng.",
            "pseudo": "current <- start\nwhile best neighbor has lower h:\n    current <- best neighbor\nreturn current",
        },
        "Stochastic Hill Climbing": {
            "Family": "Tìm kiếm cục bộ ngẫu nhiên",
            "Selection rule": "Chọn ngẫu nhiên một láng giềng có cải thiện.",
            "Evaluation function": "minimize h(n)",
            "Guarantee": "Không đầy đủ, không tối ưu.",
            "Main limitation": "Kết quả phụ thuộc seed và vẫn có thể kẹt.",
            "pseudo": "current <- start\nwhile improving neighbors exist:\n    current <- random improving neighbor\nreturn current",
        },
        "Random-Restart Hill Climbing": {
            "Family": "Tìm kiếm cục bộ với khởi động lại",
            "Selection rule": "Chạy hill climbing nhiều lần từ các trạng thái random-walk xuất phát từ start.",
            "Evaluation function": "minimize h(n)",
            "Guarantee": "Tăng xác suất tìm nghiệm nhưng không đảm bảo tối ưu.",
            "Main limitation": "Cần nhiều restart nếu landscape khó.",
            "pseudo": "best <- start\nfor each restart:\n    run hill climbing\n    keep best state found\nreturn goal if any run reaches it",
        },
        "Local Beam Search": {
            "Family": "Tìm kiếm cục bộ theo chùm trạng thái",
            "Selection rule": "Giữ k trạng thái tốt nhất theo h(n) ở mỗi vòng.",
            "Evaluation function": "minimize h(n) over beam",
            "Guarantee": "Không đầy đủ, không tối ưu.",
            "Main limitation": "Beam hẹp dễ mất nhánh tốt; beam rộng tốn tính toán hơn.",
            "pseudo": "beam <- {start}\nwhile step limit not reached:\n    generate successors of every beam state\n    beam <- k best successors by h\n    if goal in beam: return solution",
        },
        "Simulated Annealing": {
            "Family": "Tìm kiếm cục bộ ngẫu nhiên với giảm nhiệt độ",
            "Selection rule": "Chấp nhận láng giềng tốt ngay; láng giềng xấu với xác suất e^(-Δh/T).",
            "Evaluation function": "minimize h(n) với xác suất chấp nhận giảm theo nhiệt độ",
            "Guarantee": "Không đảm bảo tối ưu, nhưng xác suất tìm nghiệm tăng theo thời gian.",
            "Main limitation": "Cần điều chỉnh T₀, cooling rate, min_T phù hợp với bài toán.",
            "pseudo": "current <- start, T <- T₀\nwhile T > T_min:\n    neighbor <- random(successors(current))\n    Δh <- h(neighbor) - h(current)\n    if Δh < 0 or random() < exp(-Δh/T):\n        current <- neighbor\n    T <- T × cooling_rate\nreturn best found",
        },
    },
    "en": {},
}

ALGORITHM_PROFILES["en"] = {
    "BFS": {
        "Family": "Uninformed search",
        "Selection rule": "Always expands the shallowest node from a FIFO queue.",
        "Evaluation function": "f(n) = depth(n)",
        "Guarantee": "Complete and optimal when every step has equal cost.",
        "Main limitation": "High memory use because it stores the frontier layer by layer.",
        "pseudo": "frontier <- FIFO(start)\nwhile frontier not empty:\n    node <- pop_front(frontier)\n    if node is goal: return solution\n    expand node and append unseen children",
    },
    "DFS": {
        "Family": "Uninformed search",
        "Selection rule": "Always expands the deepest node from a LIFO stack.",
        "Evaluation function": "f(n) = depth-first order",
        "Guarantee": "Not optimal; bounded here by depth and expansion limits.",
        "Main limitation": "Can follow poor deep branches before shallow solutions.",
        "pseudo": "frontier <- Stack(start)\nwhile frontier not empty:\n    node <- pop(frontier)\n    if node is goal: return solution\n    if depth limit not reached: push children",
    },
    "UCS": {
        "Family": "Path-cost search",
        "Selection rule": "Expands the node with minimum g(n).",
        "Evaluation function": "f(n) = g(n)",
        "Guarantee": "Complete and optimal for non-negative costs; with 8-puzzle c=1 it resembles BFS.",
        "Main limitation": "Does not use goal-directed heuristic knowledge.",
        "pseudo": "frontier <- PriorityQueue(start, priority=g)\nwhile frontier not empty:\n    node <- pop_lowest_g(frontier)\n    if node is goal: return solution\n    relax children by path cost",
    },
    "IDS": {
        "Family": "Iterative deepening search",
        "Selection rule": "Runs depth-limited search with limits 0,1,2,...",
        "Evaluation function": "f(n) = depth limit iteration",
        "Guarantee": "Optimal in number of moves when the limit is sufficient and step costs are equal.",
        "Main limitation": "Re-expands shallow nodes across iterations.",
        "pseudo": "for limit in 0..L:\n    result <- depth_limited_search(start, limit)\n    if result found: return result",
    },
    "Greedy": {
        "Family": "Informed search",
        "Selection rule": "Expands the node with minimum h(n).",
        "Evaluation function": "f(n) = h(n)",
        "Guarantee": "Not optimal.",
        "Main limitation": "Can be misled by short-term heuristic progress.",
        "pseudo": "frontier <- PriorityQueue(start, priority=h)\nwhile frontier not empty:\n    node <- pop_lowest_h(frontier)\n    if node is goal: return solution\n    expand and rank children by h",
    },
    "A*": {
        "Family": "Informed optimal search with admissible heuristic",
        "Selection rule": "Expands the node with minimum g(n)+h(n).",
        "Evaluation function": "f(n) = g(n) + h(n)",
        "Guarantee": "Optimal when h is admissible; Manhattan is admissible for 8-puzzle.",
        "Main limitation": "Can consume substantial memory for frontier and best-g records.",
        "pseudo": "frontier <- PriorityQueue(start, priority=g+h)\nwhile frontier not empty:\n    node <- pop_lowest_f(frontier)\n    if node is goal: return solution\n    relax children if a lower g is found",
    },
    "IDA*": {
        "Family": "A* with iterative f-threshold deepening",
        "Selection rule": "DFS pruned by an increasing f-threshold.",
        "Evaluation function": "f(n) = g(n) + h(n), increasing threshold",
        "Guarantee": "Optimal with admissible h if not stopped by iteration limits.",
        "Main limitation": "Can re-expand nodes across thresholds.",
        "pseudo": "threshold <- h(start)\nrepeat:\n    run DFS bounded by f <= threshold\n    if goal found: return solution\n    threshold <- smallest f that exceeded threshold",
    },
    "Simple Hill Climbing": {
        "Family": "Local search",
        "Selection rule": "Moves to the first improving neighbor.",
        "Evaluation function": "minimize h(n)",
        "Guarantee": "Not complete and not optimal.",
        "Main limitation": "Can stop at local optima or plateaus.",
        "pseudo": "current <- start\nwhile improvement exists:\n    move to first neighbor with lower h\nreturn current",
    },
    "Steepest-Ascent Hill Climbing": {
        "Family": "Local search",
        "Selection rule": "Moves to the best neighbor among all neighbors.",
        "Evaluation function": "minimize h(n)",
        "Guarantee": "Not complete and not optimal.",
        "Main limitation": "Still vulnerable to local optima.",
        "pseudo": "current <- start\nwhile best neighbor has lower h:\n    current <- best neighbor\nreturn current",
    },
    "Stochastic Hill Climbing": {
        "Family": "Randomized local search",
        "Selection rule": "Randomly selects an improving neighbor.",
        "Evaluation function": "minimize h(n)",
        "Guarantee": "Not complete and not optimal.",
        "Main limitation": "Seed-dependent and can still get stuck.",
        "pseudo": "current <- start\nwhile improving neighbors exist:\n    current <- random improving neighbor\nreturn current",
    },
    "Random-Restart Hill Climbing": {
        "Family": "Local search with restarts",
        "Selection rule": "Runs hill climbing from several random-walk descendants of start.",
        "Evaluation function": "minimize h(n)",
        "Guarantee": "Improves success probability but does not guarantee optimality.",
        "Main limitation": "Needs many restarts on difficult landscapes.",
        "pseudo": "best <- start\nfor each restart:\n    run hill climbing\n    keep best state found\nreturn goal if any run reaches it",
    },
    "Local Beam Search": {
        "Family": "Population-based local search",
        "Selection rule": "Keeps the k best states by h(n) at each iteration.",
        "Evaluation function": "minimize h(n) over beam",
        "Guarantee": "Not complete and not optimal.",
        "Main limitation": "Narrow beams can discard useful branches; wide beams cost more.",
        "pseudo": "beam <- {start}\nwhile step limit not reached:\n    generate successors of every beam state\n    beam <- k best successors by h\n    if goal in beam: return solution",
    },
    "Simulated Annealing": {
        "Family": "Stochastic local search with temperature schedule",
        "Selection rule": "Accept better neighbors immediately; worse neighbors with probability e^(-Δh/T).",
        "Evaluation function": "minimize h(n) with temperature-dependent acceptance",
        "Guarantee": "Not optimal, but probability of finding solution increases with time.",
        "Main limitation": "Requires tuning T₀, cooling rate, and min_T for the problem.",
        "pseudo": "current <- start, T <- T₀\nwhile T > T_min:\n    neighbor <- random(successors(current))\n    Δh <- h(neighbor) - h(current)\n    if Δh < 0 or random() < exp(-Δh/T):\n        current <- neighbor\n    T <- T × cooling_rate\nreturn best found",
    },
}

ALGORITHM_BASIS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "vi": {
        "BFS": {
            "primary": "Độ sâu / số tầng; tương đương g(n) khi chi phí mỗi bước = 1",
            "rule": "Ưu tiên node nông nhất trước, không dùng heuristic.",
            "g": ("implicit", "Không tính priority bằng g(n), nhưng depth = g(n) vì mỗi bước có cost 1."),
            "h": ("no", "Không dùng ước lượng đến goal."),
            "f": ("no", "Không dùng hàm tổng hợp f(n)."),
        },
        "DFS": {
            "primary": "Thứ tự LIFO / độ sâu nhánh hiện tại",
            "rule": "Ưu tiên node được đưa vào stack gần nhất, không dựa trên chi phí hay heuristic.",
            "g": ("no", "Không chọn node theo chi phí đường đi."),
            "h": ("no", "Không dùng heuristic."),
            "f": ("no", "Không dùng hàm đánh giá f(n)."),
        },
        "UCS": {
            "primary": "g(n)",
            "rule": "Ưu tiên node có chi phí đường đi nhỏ nhất từ start.",
            "g": ("yes", "Thành phần quyết định priority: g(n) càng nhỏ càng được mở trước."),
            "h": ("no", "Không dùng tri thức ước lượng khoảng cách tới goal."),
            "f": ("implicit", "Có thể xem f(n)=g(n) trong UCS."),
        },
        "IDS": {
            "primary": "Độ sâu giới hạn; tương đương kiểm soát g(n) theo từng limit",
            "rule": "Lặp DFS với depth limit tăng dần 0,1,2,...",
            "g": ("implicit", "Depth của node tương ứng số bước đã đi, tức g(n) khi cost=1."),
            "h": ("no", "Không dùng heuristic."),
            "f": ("no", "Không dùng f(n) để xếp priority."),
        },
        "Greedy": {
            "primary": "h(n)",
            "rule": "Ưu tiên node có heuristic nhỏ nhất, tức có vẻ gần goal nhất.",
            "g": ("no", "Không xét chi phí đã đi, nên có thể chọn đường dài."),
            "h": ("yes", "Thành phần quyết định priority: h(n) càng nhỏ càng được mở trước."),
            "f": ("implicit", "Có thể xem f(n)=h(n) trong Greedy."),
        },
        "A*": {
            "primary": "f(n)=g(n)+h(n)",
            "rule": "Cân bằng chi phí đã đi và ước lượng chi phí còn lại.",
            "g": ("yes", "Giữ chi phí thật từ start đến node."),
            "h": ("yes", "Ước lượng chi phí còn lại tới goal."),
            "f": ("yes", "Priority chính: f(n)=g(n)+h(n)."),
        },
        "IDA*": {
            "primary": "f(n)=g(n)+h(n) với ngưỡng tăng dần",
            "rule": "DFS chỉ đi tiếp nếu f(n) không vượt threshold hiện tại.",
            "g": ("yes", "Tính chi phí đã đi trong nhánh DFS hiện tại."),
            "h": ("yes", "Ước lượng chi phí còn lại."),
            "f": ("yes", "Dùng f(n) để cắt nhánh theo threshold."),
        },
        "Simple Hill Climbing": {
            "primary": "h(n)",
            "rule": "Chuyển sang láng giềng đầu tiên có h(n) nhỏ hơn hiện tại.",
            "g": ("no", "Không quan tâm chi phí đường đi đã đi."),
            "h": ("yes", "Dùng h(n) để đánh giá trạng thái tốt hơn."),
            "f": ("no", "Không dùng f(n)=g(n)+h(n)."),
        },
        "Steepest-Ascent Hill Climbing": {
            "primary": "h(n)",
            "rule": "Chọn láng giềng có h(n) nhỏ nhất trong toàn bộ neighbors.",
            "g": ("no", "Không xét chi phí đã đi."),
            "h": ("yes", "Dùng h(n) làm tiêu chí tối ưu cục bộ."),
            "f": ("no", "Không dùng f(n)."),
        },
        "Stochastic Hill Climbing": {
            "primary": "h(n) + chọn ngẫu nhiên trong nhóm cải thiện",
            "rule": "Lọc các neighbor có h(n) tốt hơn rồi chọn ngẫu nhiên một trạng thái.",
            "g": ("no", "Không xét chi phí đường đi."),
            "h": ("yes", "Dùng h(n) để xác định neighbor cải thiện."),
            "f": ("no", "Không dùng f(n)."),
        },
        "Random-Restart Hill Climbing": {
            "primary": "h(n) qua nhiều lần restart",
            "rule": "Mỗi lần restart chạy hill climbing để giảm h(n), rồi giữ kết quả tốt nhất.",
            "g": ("no", "Không ưu tiên node theo path cost."),
            "h": ("yes", "Dùng h(n) để đánh giá tốt/xấu trong từng lần leo đồi."),
            "f": ("no", "Không dùng f(n)."),
        },
        "Local Beam Search": {
            "primary": "h(n) trên tập beam",
            "rule": "Mỗi vòng giữ k trạng thái có h(n) nhỏ nhất.",
            "g": ("no", "Không chọn theo chi phí đã đi."),
            "h": ("yes", "Dùng h(n) để xếp hạng candidates trong beam."),
            "f": ("no", "Không dùng f(n)=g(n)+h(n)."),
        },
        "Simulated Annealing": {
            "primary": "h(n) với xác suất chấp nhận giảm theo T",
            "rule": "Luôn chấp nhận láng giềng tốt hơn; láng giềng xấu hơn với xác suất e^(-Δh/T).",
            "g": ("no", "Không xét chi phí đường đi đã đi."),
            "h": ("yes", "Dùng h(n) để đánh giá độ tốt của trạng thái."),
            "f": ("no", "Không dùng f(n)=g(n)+h(n)."),
        },
    },
    "en": {
        "BFS": {
            "primary": "Depth/level order; equivalent to g(n) when every step cost is 1",
            "rule": "Prioritizes the shallowest node first and does not use a heuristic.",
            "g": ("implicit", "Priority is not computed from g(n), but depth = g(n) because every move costs 1."),
            "h": ("no", "No goal-distance estimate is used."),
            "f": ("no", "No combined evaluation function is used."),
        },
        "DFS": {
            "primary": "LIFO order / current branch depth",
            "rule": "Prioritizes the most recently pushed stack node, not cost or heuristic value.",
            "g": ("no", "Does not choose nodes by path cost."),
            "h": ("no", "Does not use a heuristic."),
            "f": ("no", "Does not use f(n)."),
        },
        "UCS": {
            "primary": "g(n)",
            "rule": "Prioritizes the node with the smallest path cost from start.",
            "g": ("yes", "Main priority component: lower g(n) is expanded first."),
            "h": ("no", "No estimated distance to the goal is used."),
            "f": ("implicit", "UCS can be viewed as f(n)=g(n)."),
        },
        "IDS": {
            "primary": "Depth limit; indirectly controls g(n) at each iteration",
            "rule": "Repeats DFS with increasing depth limits 0,1,2,...",
            "g": ("implicit", "Node depth equals number of moves, so depth = g(n) when cost=1."),
            "h": ("no", "Does not use a heuristic."),
            "f": ("no", "Does not rank nodes by f(n)."),
        },
        "Greedy": {
            "primary": "h(n)",
            "rule": "Prioritizes the node with the smallest heuristic value.",
            "g": ("no", "Ignores accumulated path cost, so it may choose long routes."),
            "h": ("yes", "Main priority component: lower h(n) is expanded first."),
            "f": ("implicit", "Greedy can be viewed as f(n)=h(n)."),
        },
        "A*": {
            "primary": "f(n)=g(n)+h(n)",
            "rule": "Balances actual path cost and estimated remaining cost.",
            "g": ("yes", "Tracks the real cost from start to the node."),
            "h": ("yes", "Estimates the remaining cost to the goal."),
            "f": ("yes", "Main priority: f(n)=g(n)+h(n)."),
        },
        "IDA*": {
            "primary": "f(n)=g(n)+h(n) with increasing threshold",
            "rule": "DFS continues only while f(n) is within the current threshold.",
            "g": ("yes", "Tracks cost along the current DFS branch."),
            "h": ("yes", "Estimates the remaining cost."),
            "f": ("yes", "Uses f(n) to prune nodes by threshold."),
        },
        "Simple Hill Climbing": {
            "primary": "h(n)",
            "rule": "Moves to the first neighbor with lower h(n).",
            "g": ("no", "Does not consider accumulated path cost."),
            "h": ("yes", "Uses h(n) to decide whether a neighbor is better."),
            "f": ("no", "Does not use f(n)=g(n)+h(n)."),
        },
        "Steepest-Ascent Hill Climbing": {
            "primary": "h(n)",
            "rule": "Chooses the neighbor with the lowest h(n) among all neighbors.",
            "g": ("no", "Does not consider path cost."),
            "h": ("yes", "Uses h(n) as the local improvement criterion."),
            "f": ("no", "Does not use f(n)."),
        },
        "Stochastic Hill Climbing": {
            "primary": "h(n) + random choice among improving neighbors",
            "rule": "Filters neighbors with better h(n), then randomly chooses one.",
            "g": ("no", "Does not consider path cost."),
            "h": ("yes", "Uses h(n) to identify improving neighbors."),
            "f": ("no", "Does not use f(n)."),
        },
        "Random-Restart Hill Climbing": {
            "primary": "h(n) across multiple restarts",
            "rule": "Each restart runs hill climbing to reduce h(n), then keeps the best outcome.",
            "g": ("no", "Does not prioritize by path cost."),
            "h": ("yes", "Uses h(n) to judge state quality in each climb."),
            "f": ("no", "Does not use f(n)."),
        },
        "Local Beam Search": {
            "primary": "h(n) across the beam",
            "rule": "Keeps the k states with the smallest h(n) at each iteration.",
            "g": ("no", "Does not select by accumulated path cost."),
            "h": ("yes", "Uses h(n) to rank beam candidates."),
            "f": ("no", "Does not use f(n)=g(n)+h(n)."),
        },
        "Simulated Annealing": {
            "primary": "h(n) with temperature-dependent acceptance",
            "rule": "Always accept better neighbors; worse neighbors with probability e^(-Δh/T).",
            "g": ("no", "Does not consider accumulated path cost."),
            "h": ("yes", "Uses h(n) to evaluate state quality."),
            "f": ("no", "Does not use f(n)=g(n)+h(n)."),
        },
    },
}


def text(lang: str, key: str, **kwargs: Any) -> str:
    value = TEXT[lang][key]
    return value.format(**kwargs) if kwargs else value


def help_text(lang: str, key: str, **kwargs: Any) -> str:
    value = HELP[lang][key]
    return value.format(**kwargs) if kwargs else value


def localize_action(action: str, lang: str) -> str:
    if lang == "en":
        return action
    for english, vietnamese in ACTION_LABELS["vi"].items():
        action = action.replace(english, vietnamese)
    return action


def localize_table(table: Any, lang: str) -> Any:
    mapping = TABLE_COLUMNS.get(lang, {})
    if not mapping:
        return table
    if hasattr(table, "rename"):
        return table.rename(columns=mapping)
    if isinstance(table, list):
        return [{mapping.get(key, key): value for key, value in row.items()} for row in table]
    return table


def apply_theme() -> None:
    st.markdown(
        """
        <style>
          :root {
            --surface: #f7f8f5;
            --panel: #ffffff;
            --ink: #17211b;
            --muted: rgba(23, 33, 27, 0.76);
            --line: rgba(23, 33, 27, 0.14);
            --accent: #0f766e;
            --accent-strong: #0f766e;
            --accent-soft: rgba(15, 118, 110, 0.1);
            --amber: #b7791f;
            --tile-shadow: inset 0 -2px 0 rgba(128, 128, 128, 0.1), 0 1px 2px rgba(0, 0, 0, 0.1);
          }
          @media (prefers-color-scheme: dark) {
            :root {
              --surface: #0e1117;
              --panel: #171b22;
              --ink: #f4fbf8;
              --muted: rgba(244, 251, 248, 0.76);
              --line: rgba(244, 251, 248, 0.16);
              --accent: #2dd4bf;
              --accent-strong: #5eead4;
              --accent-soft: rgba(45, 212, 191, 0.14);
              --amber: #f8c36a;
              --tile-shadow: inset 0 -2px 0 rgba(255, 255, 255, 0.06), 0 1px 2px rgba(0, 0, 0, 0.32);
            }
          }
          .stApp {
            background: var(--surface);
          }
          .block-container {
            padding-top: 2.6rem;
            padding-bottom: 3rem;
            max-width: 1160px;
          }
          .app-hero {
            border-bottom: 1px solid var(--line);
            margin-bottom: 1.35rem;
            padding-bottom: 1rem;
          }
          .app-kicker {
            color: var(--accent-strong);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
          }
          .app-hero h1 {
            color: var(--ink);
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 780;
            line-height: 1.05;
            letter-spacing: 0;
            margin: 0.25rem 0 0.45rem;
          }
          .app-hero p {
            color: var(--muted);
            opacity: 1;
            font-size: 1.02rem;
            line-height: 1.55;
            max-width: 760px;
            margin: 0;
          }
          div[data-testid="stVerticalBlock"] > div:has(> .metric-grid) {
            width: 100%;
          }
          .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(118px, 1fr));
            gap: 0.7rem;
            margin: 0.45rem 0 1rem;
          }
          .metric-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            padding: 0.8rem 0.9rem;
            min-height: 74px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
          }
          .metric-card span {
            display: block;
            color: var(--ink);
            opacity: 0.7;
            font-size: 0.78rem;
            line-height: 1.2;
          }
          .metric-card strong {
            display: block;
            color: var(--ink);
            font-size: 1.28rem;
            line-height: 1.25;
            margin-top: 0.25rem;
            font-variant-numeric: tabular-nums;
          }
          .lab-panel {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            padding: 0.95rem 1rem;
            margin: 0.65rem 0 1rem;
          }
          .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0.55rem;
            margin: 0.45rem 0 0.85rem;
          }
          .status-chip {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            padding: 0.55rem 0.65rem;
            min-height: 52px;
          }
          .status-chip span {
            display: block;
            color: var(--ink);
            opacity: 0.7;
            font-size: 0.75rem;
            line-height: 1.2;
          }
          .status-chip strong {
            display: block;
            margin-top: 0.18rem;
            color: var(--ink);
            font-size: 0.95rem;
          }
          .status-chip.pass {
            border-color: rgba(46, 117, 89, 0.4);
            background: rgba(46, 117, 89, 0.1);
          }
          .status-chip.fail {
            border-color: rgba(217, 83, 79, 0.4);
            background: rgba(217, 83, 79, 0.1);
          }
          .status-chip.pass strong {
            color: #2ecc71;
          }
          .status-chip.fail strong {
            color: #e74c3c;
          }
          .section-note {
            color: var(--ink);
            opacity: 0.8;
            line-height: 1.5;
            margin: 0.1rem 0 0.75rem;
          }
          .puzzle-board {
            display: grid;
            grid-template-columns: repeat(3, clamp(48px, 7vw, 72px));
            gap: 8px;
            width: fit-content;
            max-width: 100%;
            margin: 0.45rem auto 1.25rem;
          }
          .puzzle-board .tile {
            aspect-ratio: 1 / 1;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            color: var(--ink);
            font-size: clamp(1.18rem, 3vw, 1.55rem);
            font-weight: 750;
            line-height: 1;
            box-shadow: var(--tile-shadow);
          }
          .puzzle-board .blank {
            background: var(--accent-soft);
            color: var(--accent-strong);
            opacity: 1;
            border: 1px dashed var(--accent-strong);
            box-shadow: none;
            text-decoration: underline;
            text-underline-offset: 0.14em;
          }
          div.stButton > button {
            border-radius: 8px;
            min-height: 2.5rem;
          }
          @media (max-width: 760px) {
            .block-container {
              padding-top: 1rem;
              padding-left: 1rem;
              padding-right: 1rem;
            }
            .app-hero {
              margin-bottom: 0.85rem;
              padding-bottom: 0.75rem;
            }
            .app-hero h1 {
              font-size: 2rem;
              margin-bottom: 0;
            }
            .app-hero p {
              display: none;
            }
            .metric-grid {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .puzzle-board {
              grid-template-columns: repeat(3, minmax(52px, 17vw));
              gap: 7px;
            }
            .status-grid {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_page_header(lang: str) -> None:
    st.markdown(
        f"""
        <div class="app-hero">
          <span class="app-kicker">AI Search Visualizer</span>
          <h1>{escape(text(lang, "page_title"))}</h1>
          <p>{escape(text(lang, "page_subtitle"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_cards_html(result: puzzle.SearchResult, lang: str) -> str:
    labels = {
        "vi": ["Độ dài đường đi", "Expanded", "Generated", "Runtime", "Memory"],
        "en": ["Path length", "Expanded", "Generated", "Runtime", "Memory"],
    }[lang]
    values = [
        result.path_cost if result.path_cost is not None else "N/A",
        result.expanded,
        result.generated,
        f"{result.runtime_ms:.2f} ms",
        f"{result.memory_estimate_kb:.1f} KB",
    ]
    cards = "".join(
        f'<div class="metric-card"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'
        for label, value in zip(labels, values)
    )
    return f'<div class="metric-grid">{cards}</div>'


def board_matrix_html(state: puzzle.State, lang: str) -> str:
    cells = []
    for index, value in enumerate(state):
        row, col = divmod(index, 3)
        tooltip = help_text(
            lang,
            "blank_tile" if value == 0 else "board_tile",
            value=value,
            row=row + 1,
            col=col + 1,
        )
        classes = "tile blank" if value == 0 else "tile"
        cells.append(f'<div class="{classes}" title="{escape(tooltip)}">{value}</div>')
    return f"""<div class="puzzle-board" role="grid">{''.join(cells)}</div>"""


def show_board(title: str, state: puzzle.State, lang: str, help_key: str | None = None) -> None:
    tooltip = f' title="{escape(help_text(lang, help_key))}"' if help_key else ""
    st.markdown(f"<strong{tooltip}>{escape(title)}</strong>", unsafe_allow_html=True)
    st.markdown(board_matrix_html(state, lang), unsafe_allow_html=True)


def show_goal_panel(lang: str) -> None:
    st.markdown(
        f"<strong title=\"{escape(help_text(lang, 'goal_board'))}\">{escape(text(lang, 'goal_state'))}</strong>",
        unsafe_allow_html=True,
    )
    st.caption(text(lang, "goal_caption"))
    st.markdown(board_matrix_html(puzzle.GOAL_STATE, lang), unsafe_allow_html=True)


def heuristic_formula(lang: str, heuristic: str) -> str:
    if heuristic == "manhattan":
        if lang == "vi":
            return (
                "Manhattan:  "
                r"$h(s)=\sum_{t=1}^{8}(|row_s(t)-row_g(t)|+|col_s(t)-col_g(t)|)$"
            )
        return (
            "Manhattan distance:  "
            r"$h(s)=\sum_{t=1}^{8}(|row_s(t)-row_g(t)|+|col_s(t)-col_g(t)|)$"
        )
    if heuristic == "linear_conflict":
        if lang == "vi":
            return (
                "Linear Conflict:  "
                r"$h(s)=h_{Manhattan}(s)+2\times conflicts(s)$; "
                "vẫn admissible và thường informed hơn Manhattan."
            )
        return (
            "Linear Conflict:  "
            r"$h(s)=h_{Manhattan}(s)+2\times conflicts(s)$; "
            "still admissible and usually more informed than Manhattan."
        )
    if lang == "vi":
        return "Misplaced tiles:  " r"$h(s)=|\{t \in \{1..8\}: position_s(t) \ne position_g(t)\}|$"
    return "Misplaced tiles:  " r"$h(s)=|\{t \in \{1..8\}: position_s(t) \ne position_g(t)\}|$"


def academic_problem_markdown(lang: str, heuristic: str) -> str:
    if lang == "vi":
        return f"""
**{text(lang, "objective")}.** Tìm chuỗi hành động ngắn hoặc tốt nhất biến trạng thái bắt đầu `s0`
thành trạng thái đích `sg = (1,2,3,4,5,6,7,8,0)`.

**{text(lang, "state_space")}.** Mỗi trạng thái là một hoán vị của 9 ô `(0..8)`;
ô `0` biểu diễn ô trống. Trạng thái chỉ được xét nếu parity inversion tương thích với goal.

**{text(lang, "transition_model")}.** Tập hành động `A(s) = {{Up, Down, Left, Right}}`
gồm các phép di chuyển hợp lệ của ô trống. Trong bài này chi phí mỗi bước là `c(s,a,s') = 1`,
vì vậy `g(n)` chính là số bước từ start đến node `n`.

**{text(lang, "heuristic_formula")}.** {heuristic_formula(lang, heuristic)}
"""
    return f"""
**{text(lang, "objective")}.** Find a shortest or best action sequence that transforms the start state `s0`
into the goal state `sg = (1,2,3,4,5,6,7,8,0)`.

**{text(lang, "state_space")}.** Each state is a permutation of the 9 tiles `(0..8)`;
tile `0` denotes the blank. A state is searched only when its inversion parity is compatible with the goal.

**{text(lang, "transition_model")}.** The action set `A(s) = {{Up, Down, Left, Right}}`
contains all legal blank-tile moves. In this app every step has cost `c(s,a,s') = 1`,
so `g(n)` is the number of moves from the start node to node `n`.

**{text(lang, "heuristic_formula")}.** {heuristic_formula(lang, heuristic)}
"""


def evaluation_rows(lang: str) -> Any:
    if lang == "vi":
        rows = [
            {"Criterion": "Complete", "Academic meaning": "Thuật toán có đảm bảo tìm nghiệm nếu nghiệm tồn tại hay không."},
            {"Criterion": "Optimal", "Academic meaning": "Thuật toán có đảm bảo trả về nghiệm có chi phí nhỏ nhất hay không."},
            {"Criterion": "Expanded", "Academic meaning": "Số node đã được lấy ra để kiểm tra và sinh successor."},
            {"Criterion": "Generated", "Academic meaning": "Số node successor đã được tạo trong quá trình tìm kiếm."},
            {"Criterion": "Max Frontier", "Academic meaning": "Kích thước frontier lớn nhất, phản ánh áp lực bộ nhớ."},
            {"Criterion": "Runtime ms", "Academic meaning": "Thời gian thực nghiệm trên cấu hình hiện tại."},
        ]
    else:
        rows = [
            {"Criterion": "Complete", "Academic meaning": "Whether the algorithm is guaranteed to find a solution if one exists."},
            {"Criterion": "Optimal", "Academic meaning": "Whether the returned solution is guaranteed to have minimum path cost."},
            {"Criterion": "Expanded", "Academic meaning": "Number of nodes removed for testing and successor generation."},
            {"Criterion": "Generated", "Academic meaning": "Number of successor nodes produced during search."},
            {"Criterion": "Max Frontier", "Academic meaning": "Largest frontier size, used as a memory-pressure proxy."},
            {"Criterion": "Runtime ms", "Academic meaning": "Empirical runtime under the current configuration."},
        ]
    return localize_table(puzzle._to_table(rows), lang)


def trace_glossary_rows(lang: str) -> Any:
    if lang == "vi":
        rows = [
            {"Trace column": "Node", "Definition": "Trạng thái đang được chọn để xét ở vòng lặp hiện tại."},
            {"Trace column": "Frontier", "Definition": "Tập biên: các node đã sinh nhưng chưa mở rộng."},
            {"Trace column": "Reached", "Definition": "Các trạng thái đã được ghi nhận để tránh lặp hoặc so sánh chi phí tốt hơn."},
            {"Trace column": "g", "Definition": "Chi phí đường đi từ start đến node hiện tại."},
            {"Trace column": "h", "Definition": "Ước lượng chi phí còn lại từ node hiện tại đến goal."},
            {"Trace column": "f", "Definition": "Hàm đánh giá dùng để ưu tiên node, ví dụ A*: f=g+h."},
            {"Trace column": "Priority Rule", "Definition": "Quy tắc học thuật mà thuật toán dùng để chọn node tiếp theo."},
            {"Trace column": "Selection Key", "Definition": "Giá trị cụ thể tại vòng lặp hiện tại, ví dụ g, h, f, threshold hoặc temperature."},
            {"Trace column": "Generated Children", "Definition": "Số successor hợp lệ được sinh ra từ node/current state trong vòng lặp."},
            {"Trace column": "Skipped States", "Definition": "Số state bị bỏ qua do đã reached, nằm trên path hiện tại, hoặc bị giới hạn depth."},
        ]
    else:
        rows = [
            {"Trace column": "Node", "Definition": "The state selected for examination in the current iteration."},
            {"Trace column": "Frontier", "Definition": "The boundary set: generated nodes not yet expanded."},
            {"Trace column": "Reached", "Definition": "States recorded to prevent repetition or compare better path costs."},
            {"Trace column": "g", "Definition": "Path cost from the start state to the current node."},
            {"Trace column": "h", "Definition": "Estimated remaining cost from the current node to the goal."},
            {"Trace column": "f", "Definition": "Priority/evaluation value, for example A*: f=g+h."},
            {"Trace column": "Priority Rule", "Definition": "The academic rule the algorithm uses to select the next node."},
            {"Trace column": "Selection Key", "Definition": "The concrete value for this iteration, such as g, h, f, threshold, or temperature."},
            {"Trace column": "Generated Children", "Definition": "Number of valid successors generated from the node/current state."},
            {"Trace column": "Skipped States", "Definition": "States skipped because they were reached, on the current path, or blocked by depth limits."},
        ]
    return localize_table(puzzle._to_table(rows), lang)


def status_label(lang: str, status: str) -> str:
    if status == "yes":
        return text(lang, "yes")
    if status == "no":
        return text(lang, "no")
    return text(lang, "implicit")


def fallback_priority_basis(lang: str, algorithm: str) -> Dict[str, Any]:
    info = puzzle.ALGORITHM_INFO[algorithm]
    group = info["group"]
    rule = puzzle.PRIORITY_RULES.get(algorithm, "")
    if group == "Uninformed Search":
        primary = "g(n)/depth" if lang == "en" else "g(n)/độ sâu"
        g_status, h_status, f_status = "implicit", "no", "no"
    elif group == "Informed Search":
        primary = "h(n) or f(n)=g(n)+h(n)"
        g_status, h_status, f_status = "implicit", "yes", "implicit"
    elif group == "Local Search":
        primary = "h(n)"
        g_status, h_status, f_status = "no", "yes", "no"
    elif group == "Complex Environments":
        primary = "belief/conditional/online state estimate" if lang == "en" else "belief state / quan sát một phần / ước lượng online"
        g_status, h_status, f_status = "implicit", "yes", "implicit"
    elif group == "Constraint Satisfaction Problems":
        primary = "constraints/conflicts/horizon" if lang == "en" else "ràng buộc / xung đột / planning horizon"
        g_status, h_status, f_status = "implicit", "implicit", "no"
    else:
        primary = "utility / expected value" if lang == "en" else "utility / giá trị kỳ vọng"
        g_status, h_status, f_status = "no", "implicit", "no"
    if lang == "vi":
        meaning = {
            "Uninformed Search": "Chi phí/độ sâu chỉ dùng khi đường đi có ý nghĩa; h(n) không quyết định thứ tự mở node.",
            "Informed Search": "Heuristic là tri thức định hướng; A*/IDA* kết hợp thêm g(n) để giữ tối ưu.",
            "Local Search": "h(n) đo chất lượng trạng thái hiện tại; thuật toán không duy trì đường đi tối ưu toàn cục.",
            "Complex Environments": "h(n) chỉ là ước lượng chất lượng trong belief/online/partial model, không biến mô hình này thành solver chuẩn.",
            "Constraint Satisfaction Problems": "Trọng tâm là biến, miền và ràng buộc; h(n) chỉ hỗ trợ đo xung đột/trạng thái khi cần.",
            "Adversarial / Stochastic Search": "Trọng tâm là utility, đối thủ hoặc chance node; h(n) chỉ hỗ trợ xây utility trong demo.",
        }.get(group, "Thành phần này phụ thuộc mô hình học thuật của thuật toán.")
    else:
        meaning = "Path cost/depth is tracked when a path is meaningful."
    return {
        "primary": primary,
        "rule": rule,
        "g": (g_status, meaning),
        "h": (h_status, "Heuristic là ước lượng chất lượng/khoảng cách khi mô hình cần." if lang == "vi" else "Heuristic is used when the educational model needs a state-quality estimate."),
        "f": (f_status, "f(n)=g(n)+h(n) chỉ là priority chính của A*/IDA*." if lang == "vi" else "Combined f(n) is used only by A*/IDA* style algorithms."),
    }


def fallback_algorithm_profile(lang: str, algorithm: str) -> Dict[str, str]:
    info = puzzle.ALGORITHM_INFO[algorithm]
    group = info["group"]
    suitable = info.get("suitable", "")
    if lang == "vi":
        group_notes = {
            "Complex Environments": "Mô hình môi trường mở rộng: belief state, quan sát một phần, online update hoặc nondeterministic outcome.",
            "Constraint Satisfaction Problems": "Mô hình hóa bài toán bằng biến, miền giá trị và ràng buộc theo planning horizon.",
            "Adversarial / Stochastic Search": "Mô hình mở rộng có đối thủ hoặc chance node để minh họa Minimax/Expectimax.",
        }
        return {
            "Family": group,
            "Selection rule": puzzle.PRIORITY_RULES.get(algorithm, ""),
            "Evaluation function": "Xem `Selection Key` và `Decision/Note` trong trace.",
            "Guarantee": f"Complete: {info['complete']}. Optimal: {info['optimal']}.",
            "Main limitation": group_notes.get(group, suitable),
            "pseudo": (
                "khởi tạo mô hình học thuật từ ma trận hiện tại\n"
                "for mỗi bước trong giới hạn:\n"
                "    chọn/cập nhật theo quy tắc của thuật toán\n"
                "    ghi Node / Frontier / Reached / Decision vào trace\n"
                "trả SearchResult kèm ghi chú giới hạn mô hình"
            ),
        }
    return {
        "Family": group,
        "Selection rule": puzzle.PRIORITY_RULES.get(algorithm, ""),
        "Evaluation function": "See trace Selection Key and Decision/Note",
        "Guarantee": f"Complete: {info['complete']}. Optimal: {info['optimal']}.",
        "Main limitation": suitable,
        "pseudo": (
            "initialize educational model from current board\n"
            "for each bounded step:\n"
            "    choose/update according to the algorithm rule\n"
            "    emit Node / Frontier / Reached / Decision trace\n"
            "return SearchResult with explicit limitation note"
        ),
    }


def priority_basis_rows(lang: str, algorithm: str) -> Any:
    basis = ALGORITHM_BASIS.get(lang, {}).get(algorithm) or fallback_priority_basis(lang, algorithm)
    rows = []
    for component in ["g", "h", "f"]:
        status, meaning = basis[component]
        rows.append(
            {
                "Component": f"{component}(n)",
                text(lang, "uses_component"): status_label(lang, status),
                text(lang, "component_meaning"): meaning,
            }
        )
    return puzzle._to_table(rows)


def show_priority_basis(lang: str, algorithm: str) -> None:
    basis = ALGORITHM_BASIS.get(lang, {}).get(algorithm) or fallback_priority_basis(lang, algorithm)
    st.markdown(f"**{text(lang, 'primary_basis')}:** `{basis['primary']}`")
    st.markdown(f"**{text(lang, 'priority_rule')}:** {basis['rule']}")
    st.dataframe(priority_basis_rows(lang, algorithm), width="stretch", hide_index=True)


def show_algorithm_profile(lang: str, algorithm: str) -> None:
    profile = ALGORITHM_PROFILES.get(lang, {}).get(algorithm) or fallback_algorithm_profile(lang, algorithm)
    st.markdown(f"#### {text(lang, 'priority_basis')}")
    show_priority_basis(lang, algorithm)
    st.markdown(
        f"""
**{TABLE_COLUMNS[lang].get("Family", "Family")}:** {profile["Family"]}

**{TABLE_COLUMNS[lang].get("Selection rule", "Selection rule")}:** {profile["Selection rule"]}

**{TABLE_COLUMNS[lang].get("Evaluation function", "Evaluation function")}:** `{profile["Evaluation function"]}`

**{TABLE_COLUMNS[lang].get("Guarantee", "Guarantee")}:** {profile["Guarantee"]}

**{TABLE_COLUMNS[lang].get("Main limitation", "Main limitation")}:** {profile["Main limitation"]}
"""
    )
    st.code(profile["pseudo"], language="text")


def heuristic_usage_note(lang: str, algorithm: str) -> str:
    group = puzzle.ALGORITHM_INFO[algorithm]["group"]
    priority_algorithms = {
        "Greedy",
        "A*",
        "IDA*",
        "Simple Hill Climbing",
        "Steepest-Ascent Hill Climbing",
        "Stochastic Hill Climbing",
        "Random-Restart Hill Climbing",
        "Local Beam Search",
        "Simulated Annealing",
    }
    if algorithm in {"BFS", "DFS", "UCS", "IDS"}:
        return (
            "Thuật toán này không dùng h(n) để chọn node; h(n) chỉ dùng cho bảng giải thích/certificate."
            if lang == "vi"
            else "This algorithm does not use h(n) for node selection; h(n) is shown only for explanation/certification."
        )
    if algorithm in priority_algorithms:
        return (
            "Thuật toán này dùng h(n) trực tiếp trong priority hoặc đánh giá trạng thái."
            if lang == "vi"
            else "This algorithm directly uses h(n) in priority or state evaluation."
        )
    if group == "Constraint Satisfaction Problems":
        return (
            "CSP ưu tiên biến/ràng buộc; h(n) chỉ hỗ trợ đo trạng thái/xung đột trong demo."
            if lang == "vi"
            else "CSP focuses on variables/constraints; h(n) only supports state/conflict scoring in the demo."
        )
    if group == "Adversarial / Stochastic Search":
        return (
            "Nhóm này dùng utility/expected value; h(n) chỉ hỗ trợ xây hàm utility trong mô hình demo."
            if lang == "vi"
            else "This group uses utility/expected value; h(n) only helps build the demo utility function."
        )
    return (
        "Mô hình môi trường mở rộng có thể dùng h(n) như ước lượng chất lượng, không phải priority chuẩn của solver 8-puzzle."
        if lang == "vi"
        else "The extended-environment model may use h(n) as a quality estimate, not as a standard 8-puzzle solver priority."
    )


def show_grading_checklist(lang: str) -> None:
    st.subheader(text(lang, "grading_checklist"))
    st.dataframe(
        localize_table(puzzle._to_table(puzzle.coursework_grading_checklist(lang)), lang),
        width="stretch",
        hide_index=True,
    )


def show_peas_model(lang: str, algorithm: str) -> None:
    rows = puzzle.peas_model(algorithm, lang=lang)
    for row in rows:
        st.markdown(
            f"""
            <div class="lab-panel">
              <strong>{escape(row["PEAS"])}</strong><br>
              <span class="section-note">{escape(row["Definition"])}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_problem_variant(lang: str, algorithm: str) -> None:
    rows = puzzle.algorithm_problem_model(algorithm, lang=lang, partial_goal_pattern=current_partial_goal_pattern())
    key_name = "Mục" if lang == "vi" else "Item"
    definition_name = "Định nghĩa" if lang == "vi" else "Definition"
    for row in rows:
        st.markdown(
            f"""
            <div class="lab-panel">
              <strong>{escape(row[key_name])}</strong>
              <pre style="white-space: pre-wrap; margin: 0.45rem 0 0; background: transparent; border: 0; padding: 0; color: var(--muted); font: inherit;">{escape(row[definition_name])}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )


def current_partial_goal_pattern() -> Any:
    text_value = st.session_state.get("partial_goal_pattern_text", "1 2 ? ? ? ? ? ? ?")
    try:
        return puzzle.parse_partial_goal(text_value)
    except Exception:
        return puzzle.PARTIAL_GOAL_PATTERN


def partial_goal_controls(lang: str, algorithm: str) -> None:
    if algorithm != "Partially Observable Search":
        return
    label = "Partial goal pattern" if lang == "en" else "Goal biết một phần"
    help_text_value = (
        "Use 9 entries. Digits 0..8 are known cells, ? means unknown. Example: 1 2 ? ? ? ? ? ? ?."
        if lang == "en"
        else "Nhập 9 ô. Số 0..8 là ô biết trước, ? là ô chưa biết. Ví dụ: 1 2 ? ? ? ? ? ? ?."
    )
    st.text_input(label, key="partial_goal_pattern_text", help=help_text_value)
    try:
        pattern = puzzle.parse_partial_goal(st.session_state.partial_goal_pattern_text)
        st.caption(puzzle.partial_goal_string(pattern).replace("\n", " / "))
    except Exception as exc:
        st.error(str(exc))
    button_label = "Random partial goal" if lang == "en" else "Random Goal một phần"
    if st.button(button_label, width="stretch", key="random_partial_goal"):
        pattern = puzzle.random_partial_goal_pattern(seed=st.session_state.seed + st.session_state.shuffle_count, reveal_count=2)
        st.session_state.partial_goal_pattern_text = " ".join("?" if value is None else str(value) for value in pattern)
        st.rerun()


def show_academic_context(lang: str, algorithm: str, heuristic: str) -> None:
    st.subheader(text(lang, "academic_panel"))
    with st.expander(text(lang, "grading_checklist"), expanded=False):
        show_grading_checklist(lang)
    with st.expander(text(lang, "peas_model"), expanded=False):
        show_peas_model(lang, algorithm)
    with st.expander(text(lang, "problem_variant"), expanded=False):
        show_problem_variant(lang, algorithm)
    with st.expander(text(lang, "problem_definition"), expanded=False):
        st.markdown(academic_problem_markdown(lang, heuristic))
    with st.expander(text(lang, "algorithm_profile"), expanded=False):
        show_algorithm_profile(lang, algorithm)
    with st.expander(text(lang, "evaluation_criteria"), expanded=False):
        st.dataframe(evaluation_rows(lang), width="stretch", hide_index=True)
    with st.expander(text(lang, "trace_glossary"), expanded=False):
        st.dataframe(trace_glossary_rows(lang), width="stretch", hide_index=True)


def route_rows(result: puzzle.SearchResult, lang: str, heuristic: str) -> Any:
    rows = []
    h_func = puzzle.get_heuristic(heuristic)
    for index, state in enumerate(result.path):
        action = text(lang, "start") if index == 0 else localize_action(result.actions[index - 1], lang)
        rows.append(
            {
                "Step": index,
                "Action": action,
                "g": index,
                "h": h_func(state),
                "f": index + h_func(state),
                "State": puzzle.board_string(state),
            }
        )
    return localize_table(puzzle._to_table(rows), lang)


def localized_action_sequence(result: puzzle.SearchResult, lang: str) -> str:
    if not result.actions:
        return text(lang, "start")
    return " -> ".join(localize_action(action, lang) for action in result.actions)


def show_path_player(result: puzzle.SearchResult, lang: str, heuristic: str) -> None:
    st.subheader(text(lang, "path_player"))
    if not result.path:
        st.info(text(lang, "no_solution_path"))
        return

    max_step = len(result.path) - 1
    st.session_state.playback_step = min(st.session_state.playback_step, max_step)
    current_step = st.session_state.playback_step

    prev_col, slider_col, next_col = st.columns([1, 3, 1])
    with prev_col:
        if st.button(text(lang, "previous_step"), disabled=current_step <= 0, width="stretch", help=help_text(lang, "previous_step")):
            st.session_state.playback_step = max(0, current_step - 1)
            st.rerun()
    with slider_col:
        selected_step = st.slider(
            text(lang, "step_slider"),
            min_value=0,
            max_value=max_step,
            value=current_step,
            help=help_text(lang, "step_slider"),
        )
        if selected_step != current_step:
            st.session_state.playback_step = selected_step
            current_step = selected_step
    with next_col:
        if st.button(text(lang, "next_step"), disabled=current_step >= max_step, width="stretch", help=help_text(lang, "next_step")):
            st.session_state.playback_step = min(max_step, current_step + 1)
            st.rerun()

    current_state = result.path[current_step]
    previous_state = result.path[current_step - 1] if current_step > 0 else result.path[0]
    current_action = text(lang, "start") if current_step == 0 else localize_action(result.actions[current_step - 1], lang)
    next_action = (
        localize_action(result.actions[current_step], lang)
        if current_step < len(result.actions)
        else "-"
    )
    h_func = puzzle.get_heuristic(heuristic)
    h_value = h_func(current_state)

    metric_cols = st.columns(5)
    metric_cols[0].metric(text(lang, "step"), f"{current_step}/{max_step}", help=help_text(lang, "metric_step"))
    metric_cols[1].metric("g(n)", current_step, help=help_text(lang, "metric_g"))
    metric_cols[2].metric("h(n)", h_value, help=help_text(lang, "metric_h"))
    metric_cols[3].metric("f(n)", current_step + h_value, help=help_text(lang, "metric_f"))
    metric_cols[4].metric(text(lang, "total_steps"), max_step, help=help_text(lang, "metric_total_steps"))

    st.caption(f"{text(lang, 'current_action')}: {current_action} | {text(lang, 'next_action')}: {next_action}")
    before_col, after_col = st.columns(2)
    with before_col:
        show_board(text(lang, "before_move"), previous_state, lang)
    with after_col:
        show_board(text(lang, "after_move"), current_state, lang)

    st.markdown(f"**{text(lang, 'route_sequence')}:** `{localized_action_sequence(result, lang)}`")
    with st.expander(text(lang, "route_table"), expanded=False):
        st.dataframe(route_rows(result, lang, heuristic), width="stretch", hide_index=True)


def certificate_rows(validation: Dict[str, Any], lang: str) -> Any:
    labels = {
        "path_valid": "Path hợp lệ" if lang == "vi" else "Valid path",
        "cost_matches_actions": "Cost khớp action" if lang == "vi" else "Cost matches actions",
        "terminal_matches_goal": "Terminal khớp Goal" if lang == "vi" else "Terminal matches goal",
        "solvability_checked": "Đã kiểm tra solvability" if lang == "vi" else "Solvability checked",
        "heuristic_values_valid": "Heuristic hợp lệ" if lang == "vi" else "Valid heuristic values",
        "error": "Lỗi" if lang == "vi" else "Error",
    }
    rows = []
    for key in ["path_valid", "cost_matches_actions", "terminal_matches_goal", "solvability_checked", "heuristic_values_valid"]:
        value = validation.get(key)
        rows.append({"Check": labels[key], "Value": "PASS" if value else "FAIL"})
    rows.append({"Check": labels["error"], "Value": validation.get("error") or "-"})
    return localize_table(puzzle._to_table(rows), lang)


def certificate_chips_html(validation: Dict[str, Any], lang: str) -> str:
    labels = {
        "path_valid": "Path hợp lệ" if lang == "vi" else "Valid path",
        "cost_matches_actions": "Cost khớp action" if lang == "vi" else "Cost matches actions",
        "terminal_matches_goal": "Terminal khớp Goal" if lang == "vi" else "Terminal matches goal",
        "solvability_checked": "Đã kiểm tra solvability" if lang == "vi" else "Solvability checked",
        "heuristic_values_valid": "Heuristic hợp lệ" if lang == "vi" else "Valid heuristic values",
    }
    cards = []
    for key, label in labels.items():
        passed = bool(validation.get(key))
        status = text(lang, "certificate_pass") if passed else text(lang, "certificate_fail")
        css_class = "pass" if passed else "fail"
        cards.append(
            f'<div class="status-chip {css_class}"><span>{escape(label)}</span><strong>{escape(status)}</strong></div>'
        )
    return f'<div class="status-grid">{"".join(cards)}</div>'


def show_certificate(result: puzzle.SearchResult, lang: str, heuristic: str) -> Dict[str, Any]:
    validation = puzzle.validate_result(result, heuristic)
    st.subheader(text(lang, "algorithm_certificate"))
    st.markdown(certificate_chips_html(validation, lang), unsafe_allow_html=True)
    st.dataframe(certificate_rows(validation, lang), width="stretch", hide_index=True)
    return validation


def show_trace_story(result: puzzle.SearchResult, lang: str, heuristic: str) -> None:
    st.subheader(text(lang, "trace_story"))
    story_rows = puzzle.build_trace_story(result, heuristic)
    if not story_rows:
        st.info("Trace story is empty because trace capture is disabled." if lang == "en" else "Trace story đang trống vì trace đang bị tắt.")
        return
    st.dataframe(localize_table(puzzle._to_table(story_rows[:20]), lang), width="stretch", hide_index=True)


def show_heuristic_inspector(state: puzzle.State, lang: str, heuristic: str) -> None:
    explanation = puzzle.explain_heuristic(state, heuristic)
    st.subheader(text(lang, "heuristic_inspector"))
    st.markdown(f'<p class="section-note">{escape(explanation["admissibility_note"])}</p>', unsafe_allow_html=True)

    total_rows = [{"Metric": key, "Value": value} for key, value in explanation["totals"].items()]
    st.markdown(f"**{text(lang, 'heuristic_totals')}**")
    st.dataframe(localize_table(puzzle._to_table(total_rows), lang), width="stretch", hide_index=True)

    st.markdown(f"**{text(lang, 'tile_contributions')}**")
    st.dataframe(localize_table(puzzle._to_table(explanation["tile_rows"]), lang), width="stretch", hide_index=True)

    if heuristic == "linear_conflict":
        st.markdown(f"**{text(lang, 'linear_conflicts')}**")
        if explanation["linear_conflicts"]:
            st.dataframe(localize_table(puzzle._to_table(explanation["linear_conflicts"]), lang), width="stretch", hide_index=True)
        else:
            st.info(text(lang, "no_linear_conflicts"))


def show_experiment_lab(lang: str, heuristic: str) -> None:
    st.subheader(text(lang, "experiment_lab"))
    st.caption(text(lang, "benchmark_caption"))
    if st.button(text(lang, "run_experiment"), width="stretch", key="run_experiment_lab"):
        st.session_state.last_experiment = puzzle.run_experiment_suite(heuristic_name=heuristic)
        st.session_state.last_experiment_heuristic = heuristic

    experiment = st.session_state.get("last_experiment")
    if experiment is not None and experiment.get("heuristic") != heuristic:
        experiment = None
    if experiment is None:
        st.info("Run the experiment to produce a deterministic comparison table." if lang == "en" else "Chạy experiment để tạo bảng so sánh deterministic.")
        return

    st.caption(f"{text(lang, 'heuristic')}: {experiment['heuristic']}")
    st.dataframe(localize_table(puzzle._to_table(experiment["rows"]), lang), width="stretch", hide_index=True)
    experiment_markdown = puzzle.export_experiment_markdown(experiment)
    st.download_button(
        text(lang, "download_experiment"),
        data=experiment_markdown,
        file_name="8_puzzle_experiment_lab.md",
        mime="text/markdown",
        width="stretch",
    )
    st.markdown("**Heuristic dominance: misplaced vs manhattan**")
    dominance = puzzle.run_heuristic_dominance_demo(st.session_state.start_state)
    st.dataframe(localize_table(puzzle._to_table(dominance["rows"]), lang), width="stretch", hide_index=True)
    st.caption(dominance["conclusion"])


def run_demo_benchmark(heuristic: str, lang: str) -> Any:
    rows = []
    config = puzzle.TraceConfig(max_expansions=8000, max_trace_rows=0, ids_max_depth=35, ida_max_iterations=80, seed=7)
    algorithms = ["BFS", "UCS", "A*", "Greedy", "IDA*"]
    for preset_name in ["easy_2", "medium_10", "hard_20"]:
        state = puzzle.DEMO_PRESETS[preset_name]
        for algorithm in algorithms:
            result = puzzle.run_algorithm(state, algorithm, heuristic=heuristic, config=config)
            row = {"Preset": preset_name, "Group": puzzle.ALGORITHM_INFO[result.algorithm]["group"]}
            row.update(result.summary_row())
            rows.append(row)
    return localize_table(puzzle._to_table(rows), lang)


def current_shuffle_note(lang: str) -> str:
    preset_name = st.session_state.get("last_preset_name")
    if preset_name:
        return text(lang, "preset_note", name=preset_name)
    count = st.session_state.shuffle_count
    if count == 0:
        return text(lang, "initial_shuffle")
    return text(
        lang,
        "shuffle_note",
        moves=st.session_state.last_shuffle_moves,
        seed=st.session_state.last_shuffle_seed,
        count=count,
    )


def shuffle_start_state(scramble_moves: int) -> None:
    st.session_state.shuffle_count += 1
    effective_seed = st.session_state.seed + st.session_state.shuffle_count
    st.session_state.start_state = puzzle.generate_random_state(scramble_moves, effective_seed)
    st.session_state.last_shuffle_moves = scramble_moves
    st.session_state.last_shuffle_seed = effective_seed
    st.session_state.last_result = None
    st.session_state.last_comparison = None
    st.session_state.last_benchmark = None
    st.session_state.last_preset_name = ""
    st.session_state.playback_step = 0


def load_demo_preset(preset_name: str) -> None:
    st.session_state.start_state = puzzle.DEMO_PRESETS[preset_name]
    st.session_state.last_preset_name = preset_name
    st.session_state.last_result = None
    st.session_state.last_comparison = None
    st.session_state.last_benchmark = None
    st.session_state.playback_step = 0


def show_result(result: puzzle.SearchResult, lang: str, heuristic: str) -> None:
    validation = puzzle.validate_result(result, heuristic)
    summary_tab, trace_tab, heuristics_tab, experiment_tab, report_tab = st.tabs(
        [
            text(lang, "summary_tab"),
            text(lang, "academic_trace_tab"),
            text(lang, "heuristics_tab"),
            text(lang, "experiment_tab"),
            text(lang, "report_tab"),
        ]
    )

    with summary_tab:
        st.subheader(text(lang, "run_summary"))
        st.markdown(metric_cards_html(result, lang), unsafe_allow_html=True)
        st.subheader(text(lang, "algorithm_certificate"))
        st.markdown(certificate_chips_html(validation, lang), unsafe_allow_html=True)
        with st.expander(text(lang, "grading_checklist"), expanded=False):
            show_grading_checklist(lang)
        with st.expander(text(lang, "result_details"), expanded=False):
            st.dataframe(certificate_rows(validation, lang), width="stretch", hide_index=True)
            st.dataframe(localize_table(puzzle._to_table([result.summary_row()]), lang), width="stretch")

        st.markdown(f"**{text(lang, 'coursework_report')}**")
        st.caption(puzzle.academic_conclusion(result))

        goal_col, final_col = st.columns(2)
        with goal_col:
            show_goal_panel(lang)
        with final_col:
            if result.path:
                show_board(text(lang, "final_state"), result.path[-1], lang, "goal_board")
            else:
                show_board(text(lang, "best_final_state"), result.start, lang)

        with st.expander(text(lang, "path_playback"), expanded=bool(result.found and len(result.path) <= 8)):
            show_path_player(result, lang, heuristic)

    with trace_tab:
        show_trace_story(result, lang, heuristic)
        replay_rows = puzzle.build_trace_replay(result, heuristic, limit=80)
        if replay_rows:
            st.subheader("Trace Player")
            replay_index = st.slider("Trace replay row", min_value=0, max_value=len(replay_rows) - 1, value=0)
            st.json(replay_rows[replay_index], expanded=False)
        st.subheader("Search Tree Preview")
        tree = puzzle.build_search_tree_preview(result.start, heuristic, max_depth=2, max_nodes=25)
        st.dataframe(localize_table(puzzle._to_table(tree["nodes"]), lang), width="stretch", hide_index=True)
        st.subheader(text(lang, "trace"))
        st.dataframe(localize_table(puzzle.render_trace_table(result), lang), width="stretch")
        with st.expander(text(lang, "trace_glossary"), expanded=False):
            st.dataframe(trace_glossary_rows(lang), width="stretch", hide_index=True)
        with st.expander(text(lang, "algorithm_profile"), expanded=False):
            show_algorithm_profile(lang, result.algorithm)

    with heuristics_tab:
        show_heuristic_inspector(result.start, lang, heuristic)
        if result.path:
            with st.expander(text(lang, "final_state"), expanded=False):
                show_heuristic_inspector(result.path[-1], lang, heuristic)

    with experiment_tab:
        show_experiment_lab(lang, heuristic)

    with report_tab:
        experiment = st.session_state.get("last_experiment")
        if experiment is not None and experiment.get("heuristic") != heuristic:
            experiment = None
        report_markdown = puzzle.export_run_markdown(result, heuristic, validation, experiment)
        st.download_button(
            text(lang, "download_report"),
            data=report_markdown,
            file_name=f"8_puzzle_{result.algorithm.replace('*', 'star').replace(' ', '_')}.md",
            mime="text/markdown",
            width="stretch",
        )
        pack_key = f"{result.algorithm}|{heuristic}|{result.start}|{result.path_cost}"
        if st.button("Generate Submission Pack", width="stretch", key="generate_submission_pack"):
            st.session_state.last_submission_pack = puzzle.build_submission_pack(result, heuristic, validation, experiment)
            st.session_state.last_submission_pack_key = pack_key
        pack = st.session_state.get("last_submission_pack")
        if pack is not None and st.session_state.get("last_submission_pack_key") == pack_key:
            st.download_button("Download DOCX", data=pack["docx"], file_name="8_puzzle_coursework_report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width="stretch")
            st.download_button("Download PDF", data=pack["pdf"], file_name="8_puzzle_coursework_report.pdf", mime="application/pdf", width="stretch")
            st.download_button("Download HTML", data=pack["html"], file_name="8_puzzle_coursework_report.html", mime="text/html", width="stretch")
            st.download_button("Download Benchmark CSV", data=pack["benchmark_csv"], file_name="8_puzzle_benchmark.csv", mime="text/csv", width="stretch")
        with st.expander(text(lang, "grading_checklist"), expanded=False):
            show_grading_checklist(lang)
        st.text_area(text(lang, "report_preview"), value=report_markdown, height=420)

def build_config() -> puzzle.TraceConfig:
    return puzzle.TraceConfig(
        max_expansions=st.session_state.max_expansions,
        max_trace_rows=st.session_state.max_trace_rows,
        frontier_preview=st.session_state.frontier_preview,
        reached_preview=st.session_state.reached_preview,
        ids_max_depth=st.session_state.ids_depth,
        ida_max_iterations=st.session_state.ida_iterations,
        local_max_steps=st.session_state.local_steps,
        random_restarts=st.session_state.random_restarts,
        beam_width=st.session_state.beam_width,
        seed=st.session_state.seed,
        sa_initial_temp=st.session_state.sa_initial_temp,
        sa_cooling_rate=st.session_state.sa_cooling_rate,
        sa_min_temp=st.session_state.sa_min_temp,
        sa_max_steps=st.session_state.sa_max_steps,
        partial_goal_pattern=current_partial_goal_pattern(),
    )


def initialize_state() -> None:
    if "start_state" not in st.session_state:
        st.session_state.start_state = puzzle.generate_random_state(20, seed=1)
    if "shuffle_count" not in st.session_state:
        st.session_state.shuffle_count = 0
    if "last_shuffle_moves" not in st.session_state:
        st.session_state.last_shuffle_moves = 20
    if "last_shuffle_seed" not in st.session_state:
        st.session_state.last_shuffle_seed = 1
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_result_heuristic" not in st.session_state:
        st.session_state.last_result_heuristic = "manhattan"
    if "last_comparison" not in st.session_state:
        st.session_state.last_comparison = None
    if "last_benchmark" not in st.session_state:
        st.session_state.last_benchmark = None
    if "last_experiment" not in st.session_state:
        st.session_state.last_experiment = None
    if "last_experiment_heuristic" not in st.session_state:
        st.session_state.last_experiment_heuristic = "manhattan"
    if "last_preset_name" not in st.session_state:
        st.session_state.last_preset_name = ""
    if "playback_step" not in st.session_state:
        st.session_state.playback_step = 0
    if "last_submission_pack" not in st.session_state:
        st.session_state.last_submission_pack = None
    if "last_submission_pack_key" not in st.session_state:
        st.session_state.last_submission_pack_key = ""
    if "partial_goal_pattern_text" not in st.session_state:
        st.session_state.partial_goal_pattern_text = "1 2 ? ? ? ? ? ? ?"


def main() -> None:
    st.set_page_config(page_title="8-Puzzle Search", layout="wide")
    apply_theme()
    initialize_state()

    with st.sidebar:
        language_choice = st.selectbox(
            "Ngôn ngữ / Language",
            ["Tiếng Việt", "English"],
            index=0,
            key="language_choice",
            help=HELP["vi"]["language"],
        )
        lang = "vi" if language_choice == "Tiếng Việt" else "en"
        st.header(text(lang, "controls"))
        grouped_algorithms = puzzle.algorithms_by_group()
        groups = puzzle.algorithm_groups()
        default_group = puzzle.ALGORITHM_INFO["A*"]["group"]
        algorithm_group = st.selectbox(
            text(lang, "algorithm_group"),
            groups,
            index=groups.index(default_group) if default_group in groups else 0,
            help=help_text(lang, "algorithm"),
        )
        group_algorithms = grouped_algorithms[algorithm_group]
        algorithm = st.selectbox(
            text(lang, "algorithm"),
            group_algorithms,
            index=group_algorithms.index("A*") if "A*" in group_algorithms else 0,
            help=help_text(lang, "algorithm"),
        )
        heuristic = st.selectbox(
            text(lang, "heuristic"),
            puzzle.DEFAULT_HEURISTICS,
            index=puzzle.DEFAULT_HEURISTICS.index("manhattan"),
            help=help_text(lang, "heuristic"),
        )
        st.caption(f"{text(lang, 'heuristic_usage')}: {heuristic_usage_note(lang, algorithm)}")
        partial_goal_controls(lang, algorithm)
        preset_name = st.selectbox(text(lang, "demo_preset"), list(puzzle.DEMO_PRESETS.keys()))
        if st.button(text(lang, "load_preset"), width="stretch", key="sidebar_load_preset"):
            load_demo_preset(preset_name)
            st.rerun()
        st.number_input(text(lang, "seed"), min_value=0, max_value=1_000_000, value=1, key="seed", help=help_text(lang, "seed"))
        scramble = st.slider(text(lang, "scramble_moves"), min_value=0, max_value=80, value=20, help=help_text(lang, "scramble_moves"))

        if st.button(text(lang, "shuffle"), width="stretch", key="sidebar_shuffle", help=help_text(lang, "shuffle")):
            shuffle_start_state(scramble)

        st.divider()
        st.number_input(text(lang, "max_expansions"), min_value=1, max_value=200000, value=5000, key="max_expansions", help=help_text(lang, "max_expansions"))
        with st.expander(text(lang, "advanced_settings"), expanded=False):
            st.number_input(text(lang, "max_trace_rows"), min_value=0, max_value=5000, value=300, key="max_trace_rows", help=help_text(lang, "max_trace_rows"))
            st.number_input(text(lang, "frontier_preview"), min_value=1, max_value=30, value=5, key="frontier_preview", help=help_text(lang, "frontier_preview"))
            st.number_input(text(lang, "reached_preview"), min_value=1, max_value=30, value=5, key="reached_preview", help=help_text(lang, "reached_preview"))
            st.number_input(text(lang, "ids_depth"), min_value=1, max_value=80, value=30, key="ids_depth", help=help_text(lang, "ids_depth"))
            st.number_input(text(lang, "ida_iterations"), min_value=1, max_value=200, value=80, key="ida_iterations", help=help_text(lang, "ida_iterations"))
            st.number_input(text(lang, "local_steps"), min_value=1, max_value=5000, value=200, key="local_steps", help=help_text(lang, "local_steps"))
            st.number_input(text(lang, "random_restarts"), min_value=0, max_value=200, value=20, key="random_restarts", help=help_text(lang, "random_restarts"))
            st.number_input(text(lang, "beam_width"), min_value=1, max_value=50, value=4, key="beam_width", help=help_text(lang, "beam_width"))
            st.divider()
            st.number_input(text(lang, "sa_initial_temp"), min_value=1.0, max_value=1000.0, value=100.0, key="sa_initial_temp", help=help_text(lang, "sa_initial_temp"))
            st.number_input(text(lang, "sa_cooling_rate"), min_value=0.9, max_value=0.9999, value=0.995, step=0.001, key="sa_cooling_rate", help=help_text(lang, "sa_cooling_rate"))
            st.number_input(text(lang, "sa_min_temp"), min_value=0.001, max_value=1.0, value=0.01, key="sa_min_temp", help=help_text(lang, "sa_min_temp"))
            st.number_input(text(lang, "sa_max_steps"), min_value=100, max_value=50000, value=5000, key="sa_max_steps", help=help_text(lang, "sa_max_steps"))

    show_page_header(lang)

    col_left, col_right = st.columns([1, 1.45], gap="large")
    with col_left:
        st.subheader(text(lang, "board_panel"))
        if st.button(text(lang, "shuffle"), type="primary", width="stretch", key="main_shuffle", help=help_text(lang, "shuffle")):
            shuffle_start_state(scramble)
        st.caption(current_shuffle_note(lang))

        show_board(text(lang, "start_state"), st.session_state.start_state, lang, "start_board")
        show_goal_panel(lang)
        manual_label = "Nhập Start thủ công" if lang == "vi" else "Manual Start input"
        with st.expander(manual_label, expanded=False):
            state_text = st.text_input(
                text(lang, "custom_start"),
                value=" ".join(str(x) for x in st.session_state.start_state),
                help=help_text(lang, "custom_start"),
            )
            if st.button(text(lang, "use_custom"), help=help_text(lang, "use_custom")):
                try:
                    st.session_state.start_state = puzzle.parse_state(state_text)
                    st.session_state.last_result = None
                    st.session_state.last_comparison = None
                    st.session_state.last_benchmark = None
                    st.session_state.last_preset_name = ""
                    st.session_state.playback_step = 0
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    with col_right:
        st.subheader(text(lang, "run"))
        st.caption(f"{text(lang, 'algorithm')}: {algorithm} | {text(lang, 'heuristic')}: {heuristic}")
        action_cols = st.columns(2)
        with action_cols[0]:
            run_clicked = st.button(text(lang, "run_selected"), type="primary", width="stretch", help=help_text(lang, "run_selected"))
        with action_cols[1]:
            compare_clicked = st.button(text(lang, "compare_all"), width="stretch", help=help_text(lang, "compare_all"))
        st.caption(text(lang, "notes"))

        config = build_config()
        if run_clicked:
            st.session_state.last_result = puzzle.run_algorithm(st.session_state.start_state, algorithm, heuristic, config)
            st.session_state.last_result_heuristic = heuristic
            st.session_state.last_comparison = None
            st.session_state.playback_step = 0
        elif compare_clicked:
            st.session_state.last_comparison = puzzle.compare_algorithms(
                st.session_state.start_state,
                heuristic=heuristic,
                config=config,
            )
            st.session_state.last_result = None
            st.session_state.playback_step = 0

        if st.session_state.last_result is not None:
            show_result(st.session_state.last_result, lang, st.session_state.last_result_heuristic)
        elif st.session_state.last_comparison is not None:
            st.subheader(text(lang, "comparison"))
            st.dataframe(localize_table(st.session_state.last_comparison, lang), width="stretch")
        else:
            st.info(text(lang, "choose_action"))

        st.divider()
        show_academic_context(lang, algorithm, heuristic)


if __name__ == "__main__":
    main()
