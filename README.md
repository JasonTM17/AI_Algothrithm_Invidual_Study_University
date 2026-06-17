# Dự án trực quan hóa thuật toán tìm kiếm cho trò chơi 8-Puzzle

## 0. Chạy nhanh cho giảng viên

App chính của bài nộp là:

- Core thuật toán: `eight_puzzle_search_app.py`
- Giao diện web (Streamlit): `streamlit_eight_puzzle_app.py`
- Giao diện desktop (Tkinter, song ngữ VI/EN): `eight_puzzle_tk_app.py`
  + package `eight_puzzle_tk/`
- Package phụ/educational: `8_puzzle_ai/`

Chạy giao diện web:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run .\streamlit_eight_puzzle_app.py
```

Chạy giao diện desktop (Tkinter, **không cần pip install** — chỉ Python stdlib):

```powershell
python .\eight_puzzle_tk_app.py
```

Build file `.exe` cho giảng viên mở trực tiếp:

```powershell
.\build_desktop_exe.ps1 -Python "C:\Users\Admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
.\dist\8PuzzleSearchLab.exe
```

Giao diện desktop giữ cùng luồng học thuật với bản web: Start/Goal board, preset,
nhóm thuật toán, heuristic `misplaced`/`manhattan`, trace `Node / Frontier / Reached`,
certificate, experiment và report. Riêng Start board có thể tương tác như trò chơi:
click ô nằm cạnh `0` để di chuyển trước khi chạy thuật toán.

Chế độ trò chơi trong desktop app:

- `Reset ván`: đưa Start board về trạng thái lúc nạp preset/shuffle.
- `Gợi ý A*`: dùng A* + Manhattan để đề xuất nước đi tiếp theo.
- `Đi 1 bước tối ưu`: cho AI áp dụng đúng một bước từ nghiệm A* hiện tại.
- `Auto-solve`: tự động phát nghiệm A* từng bước để demo trực quan.
- Bộ đếm `Số nước chơi` và trạng thái thắng giúp phân biệt người chơi tự giải với
  đường đi do thuật toán sinh ra.

Chạy kiểm thử desktop (headless smoke test cho cả package Tkinter):

```powershell
python .\eight_puzzle_tk_app.py --self-test
```

Chạy kiểm thử core:

```powershell
python .\eight_puzzle_search_app.py --self-test
python .\tests\test_search_behavior.py
python .\8_puzzle_ai\tests\test_puzzle.py
python -m py_compile .\eight_puzzle_search_app.py .\streamlit_eight_puzzle_app.py .\8_puzzle_ai\app.py
```

Phạm vi heuristic `h(n)` của app chính được cố ý giữ đúng hai hàm cơ bản trong môn học:

- `misplaced`: số ô sai vị trí so với Goal.
- `manhattan`: tổng khoảng cách Manhattan của từng ô tới Goal.

Các nhóm `Complex Environments`, `Constraint Satisfaction Problems` và
`Adversarial / Stochastic Search` được gắn nhãn là mô hình học thuật/educational.
Chúng giúp chứng minh hiểu đúng dạng bài toán, PEAS, biến/ràng buộc, belief state,
đối thủ hoặc chance node; không được trình bày như solver chuẩn thay thế BFS/UCS/A*.

Checklist nộp bài:

- [ ] App chính chạy được bằng Streamlit.
- [ ] Có đủ 6 nhóm thuật toán trong UI.
- [ ] Mỗi thuật toán có PEAS và dạng bài toán tương ứng.
- [ ] Trace thể hiện rõ `Node`, `Frontier`, `Reached`, `Priority Rule`, `Selection Key`.
- [ ] Heuristic trong UI chỉ có `misplaced` và `manhattan`.
- [ ] A* + Manhattan giải được preset demo và có certificate hợp lệ.
- [ ] Unsolvable state dừng sớm, không mở rộng node.
- [ ] Có thể xuất Markdown/DOCX/PDF/HTML/CSV trong tab `Report`.
- [ ] Tất cả lệnh kiểm thử phía trên pass trước khi nộp.

Kịch bản demo chi tiết nằm ở `docs/demo_script.md`.

## 1. Thông tin dự án

**Tên dự án:** Trực quan hóa và so sánh các thuật toán tìm kiếm trên bài toán 8-Puzzle  
**Lĩnh vực:** Trí tuệ nhân tạo, tìm kiếm trong không gian trạng thái, heuristic search  
**Ngôn ngữ lập trình:** Python  
**Giao diện:** Streamlit, có hỗ trợ Tiếng Việt và English  
**Ngày tạo dự án:** 04/06/2026  

### Người thực hiện

| Vai trò | Thông tin |
|---|---|
| Người làm báo cáo/dự án | `[Điền tên sinh viên hoặc nhóm tại đây]` |
| Lớp / môn học | `[Điền lớp, học phần hoặc giảng viên tại đây]` |
| Hỗ trợ xây dựng mã nguồn và tài liệu | Codex, theo yêu cầu của người dùng |
| Môi trường phát triển | `D:\Trí tuệ nhân tạo` |

> Ghi chú: phần tên sinh viên, lớp và giảng viên nên được thay bằng thông tin thật trước khi nộp báo cáo.

## 2. Mục tiêu của dự án

Dự án này xây dựng một chương trình mô phỏng trò chơi **8-Puzzle** nhằm minh họa cách các thuật toán tìm kiếm hoạt động trong trí tuệ nhân tạo.

Chương trình tập trung vào ba mục tiêu chính:

1. **Trực quan hóa quá trình tìm kiếm:** hiển thị trạng thái hiện tại, frontier, reached và các bước mở rộng node.
2. **So sánh thuật toán:** so sánh số bước lời giải, số node mở rộng, số node sinh ra, kích thước frontier, thời gian chạy và tính tối ưu.
3. **Phục vụ học thuật:** giải thích mô hình bài toán, hàm đánh giá `g(n)`, `h(n)`, `f(n)`, tính đầy đủ, tính tối ưu và hạn chế của từng thuật toán.

## 3. Bài toán 8-Puzzle

8-Puzzle là một bài toán kinh điển trong trí tuệ nhân tạo. Bàn cờ gồm 9 ô dạng ma trận `3 x 3`, trong đó có 8 ô số từ `1` đến `8` và một ô trống được ký hiệu là `0`.

Ví dụ trạng thái bắt đầu:

```text
1 2 3
4 5 6
0 7 8
```

Trạng thái đích mặc định:

```text
1 2 3
4 5 6
7 8 0
```

Mục tiêu là tìm một chuỗi hành động hợp lệ để biến trạng thái bắt đầu thành trạng thái đích.

### 3.1. Biểu diễn trạng thái

Trong mã nguồn, mỗi trạng thái được biểu diễn bằng tuple gồm 9 số:

```python
(1, 2, 3, 4, 5, 6, 7, 8, 0)
```

Ma trận tương ứng:

```text
1 2 3
4 5 6
7 8 0
```

### 3.2. Tập hành động

Ô trống `0` có thể di chuyển theo bốn hướng nếu hợp lệ:

| Hành động | Ý nghĩa |
|---|---|
| `Up` | Di chuyển ô trống lên trên |
| `Down` | Di chuyển ô trống xuống dưới |
| `Left` | Di chuyển ô trống sang trái |
| `Right` | Di chuyển ô trống sang phải |

Mỗi hành động có chi phí bằng `1`, vì vậy chi phí đường đi `g(n)` chính là số bước từ trạng thái bắt đầu đến node hiện tại.

### 3.3. Điều kiện solvable

Không phải mọi hoán vị của 8-Puzzle đều có lời giải. Với bàn `3 x 3`, trạng thái có thể giải được nếu số inversion có cùng parity với trạng thái đích.

Trong chương trình:

- `generate_random_state()` tạo trạng thái bằng cách đi ngẫu nhiên từ goal, nên luôn solvable.
- Nếu nhập một trạng thái không solvable, thuật toán sẽ dừng sớm và báo lỗi thay vì tìm kiếm vô hạn.

### 3.4. PEAS cho 8-Puzzle Agent

| Thành phần | Xác định trong dự án |
|---|---|
| Performance | Đạt Goal, tối thiểu hóa số bước/cost, giảm node expanded/generated, chạy trong giới hạn thời gian/bộ nhớ, có trace và certificate hợp lệ. |
| Environment | Bảng 3x3 deterministic, fully observable, một ô trống `0`, hành động hợp lệ `Up/Down/Left/Right`, cost mỗi bước bằng `1`, solvability theo inversion parity. |
| Actuators | Di chuyển ô trống theo `Up`, `Down`, `Left`, `Right` nếu hợp lệ. |
| Sensors | Quan sát toàn bộ ma trận 3x3, vị trí ô trống, tập hành động hợp lệ và kiểm tra Goal. |

## 4. Cấu trúc dự án

### 4.0. Đường chạy chính

Phiên bản chính cần chạy và demo là:

- Core thuật toán: `eight_puzzle_search_app.py`
- Giao diện Streamlit chính: `streamlit_eight_puzzle_app.py`
- Lệnh chạy khuyến nghị: `python -m streamlit run .\streamlit_eight_puzzle_app.py`

Thư mục `8_puzzle_ai/` là package phụ phục vụ tham khảo và minh họa thêm. Các nhóm `Complex Environments`, `Constraint Satisfaction` và `Adversarial Search` trong package này là demo học thuật, không phải solver tự nhiên của bài toán 8-Puzzle chuẩn.

```text
D:\Trí tuệ nhân tạo
├── eight_puzzle_search_app.py
├── streamlit_eight_puzzle_app.py
├── README.md
└── plans/
    ├── plan.md
    ├── phase-01-research.md
    ├── phase-02-implement.md
    └── phase-03-test.md
```

### 4.1. `eight_puzzle_search_app.py`

File lõi chứa:

- Biểu diễn trạng thái 8-Puzzle.
- Sinh trạng thái random solvable.
- Kiểm tra solvability.
- Các heuristic.
- Các thuật toán tìm kiếm.
- Thu thập trace `Node / Frontier / Reached` kèm `Priority Rule`, `Selection Key`, số child sinh ra và số state bị bỏ qua.
- Kiểm chứng kết quả bằng `validate_result()`.
- Giải thích heuristic bằng `explain_heuristic()`: hai h(n) chính của bài là `misplaced` và `manhattan`, kèm đóng góp từng ô.
- Giải thích từng bước trace bằng `build_trace_story()`, giúp trả lời câu hỏi “vì sao node này được chọn?”.
- Chạy benchmark coursework bằng `run_experiment_suite()` và xuất bảng bằng `export_experiment_markdown()`.
- Xuất báo cáo Markdown/DOCX/PDF/HTML/CSV bằng submission pack, có PEAS, certificate, heuristic inspector, trace story và experiment summary nếu đã chạy.
- Hàm so sánh thuật toán.
- Self-test.
- Hàm `launch_jupyter_app()` cho môi trường Jupyter nếu có `ipywidgets`.

### 4.2. `streamlit_eight_puzzle_app.py`

File giao diện web Streamlit chứa:

- Giao diện song ngữ Tiếng Việt / English.
- Ma trận Start và Goal dạng lưới 3x3 xếp dọc, không có header cột, dễ quan sát và không bị chồng lấn.
- Nút tự trộn ma trận.
- Chọn thuật toán, heuristic và các giới hạn chạy.
- Chọn nhóm thuật toán theo 6 nhóm học thuật rồi chọn thuật toán trong nhóm.
- Chọn preset demo cố định: `easy_2`, `medium_10`, `hard_20`, `unsolvable_demo`.
- Phần cơ sở học thuật, bao gồm PEAS cho 8-Puzzle agent.
- Bảng tổng kết.
- Algorithm Certificate cho mỗi lần chạy.
- Bảng lời giải.
- Bảng trace `Node / Frontier / Reached`.
- Bảng so sánh thuật toán.
- Tab `Heuristics` để xem h(n) theo `misplaced` và `manhattan`, kèm đóng góp từng ô.
- Tab `Experiment` để chạy benchmark deterministic trên preset cố định.
- Tab `Report` để tải báo cáo Markdown phục vụ nộp bài.

### 4.3. `plans/`

Thư mục kế hoạch ClaudeKit dùng để theo dõi quá trình triển khai:

- `phase-01-research.md`: khảo sát môi trường.
- `phase-02-implement.md`: triển khai mã nguồn.
- `phase-03-test.md`: kiểm thử.
- `plan.md`: tổng hợp trạng thái kế hoạch.

## 5. Cách chạy chương trình

### 5.1. Chạy giao diện Streamlit

```powershell
python -m streamlit run .\streamlit_eight_puzzle_app.py
```

Sau khi chạy, mở:

```text
http://127.0.0.1:8501
```

### 5.2. Chạy demo bằng terminal

```powershell
python .\eight_puzzle_search_app.py --demo
```

### 5.3. Chạy self-test

```powershell
python .\eight_puzzle_search_app.py --self-test
```

Nếu thành công, chương trình in:

```text
Self-test passed.
```

### 5.4. Dùng trong Jupyter

```python
from eight_puzzle_search_app import launch_jupyter_app
launch_jupyter_app()
```

Nếu môi trường thiếu `ipywidgets`, chương trình sẽ tự fallback sang demo dạng text.

## 6. Các khái niệm học thuật trong chương trình

### 6.1. Node

`Node` là trạng thái đang được thuật toán chọn để xét tại vòng lặp hiện tại.

Một node thường chứa:

- `state`: trạng thái ma trận.
- `parent`: node cha.
- `action`: hành động tạo ra node.
- `g(n)`: chi phí từ start đến node.
- `h(n)`: heuristic ước lượng từ node đến goal.
- `f(n)`: hàm đánh giá dùng để ưu tiên node.
- `depth`: độ sâu trong cây tìm kiếm.

### 6.2. Frontier

`Frontier` là tập các node đã được sinh ra nhưng chưa được mở rộng.

Tùy thuật toán, frontier có thể là:

| Thuật toán | Frontier |
|---|---|
| BFS | Hàng đợi FIFO |
| DFS | Stack LIFO |
| UCS | Priority queue theo `g(n)` |
| Greedy | Priority queue theo `h(n)` |
| A* | Priority queue theo `f(n)=g(n)+h(n)` |
| IDS | Stack trong từng lần depth-limited search |
| IDA* | Đường DFS hiện tại với ngưỡng `f` |
| Hill Climbing | Danh sách láng giềng |
| Local Beam Search | Tập beam/candidate |

### 6.3. Reached

`Reached` là tập các trạng thái đã được ghi nhận để:

- tránh lặp vô hạn;
- không mở lại trạng thái kém hơn;
- theo dõi toàn bộ vùng không gian trạng thái đã đi qua.

### 6.4. Expanded

`Expanded` là số node đã được lấy ra khỏi frontier để kiểm tra và sinh successor.

### 6.5. Generated

`Generated` là số node successor được tạo ra trong quá trình chạy thuật toán.

### 6.6. Complete

Một thuật toán gọi là **complete** nếu nó đảm bảo tìm được nghiệm khi nghiệm tồn tại.

### 6.7. Optimal

Một thuật toán gọi là **optimal** nếu nó đảm bảo trả về nghiệm có chi phí nhỏ nhất.

Với 8-Puzzle trong dự án này, chi phí mỗi bước bằng `1`, nên nghiệm tối ưu là nghiệm có số bước ít nhất.

### 6.8. Thuật toán dựa trên `g(n)`, `h(n)` hay `f(n)`

Để nhìn theo đúng góc độ học thuật, mỗi thuật toán trong dự án được phân loại theo thành phần mà nó dùng để ưu tiên node.

Ý nghĩa các hàm:

| Ký hiệu | Ý nghĩa |
|---|---|
| `g(n)` | Chi phí thật từ trạng thái bắt đầu đến node `n` |
| `h(n)` | Chi phí ước lượng từ node `n` đến goal |
| `f(n)` | Hàm đánh giá tổng hợp để xếp ưu tiên node |

Với A* và IDA*:

```text
f(n) = g(n) + h(n)
```

Bảng phân loại thuật toán theo hàm đánh giá:

| Thuật toán | Dựa chính trên | Dùng `g(n)` | Dùng `h(n)` | Dùng `f(n)` | Diễn giải học thuật |
|---|---|---:|---:|---:|---|
| BFS | Độ sâu / số tầng | Gián tiếp | Không | Không | Với cost mỗi bước bằng 1, độ sâu tương đương `g(n)`, nhưng BFS không tính priority bằng `g(n)` |
| DFS | Stack LIFO / độ sâu nhánh | Không | Không | Không | DFS chọn node mới nhất trong stack, không dựa vào cost hay heuristic |
| UCS | `g(n)` | Có | Không | Gián tiếp | UCS chọn node có chi phí đường đi nhỏ nhất; có thể xem `f(n)=g(n)` |
| IDS | Depth limit | Gián tiếp | Không | Không | IDS kiểm soát độ sâu theo từng vòng lặp; depth tương đương `g(n)` khi cost=1 |
| Greedy | `h(n)` | Không | Có | Gián tiếp | Greedy chỉ nhìn khoảng cách ước lượng tới goal; có thể xem `f(n)=h(n)` |
| A* | `f(n)=g(n)+h(n)` | Có | Có | Có | A* cân bằng chi phí đã đi và chi phí ước lượng còn lại |
| IDA* | `f(n)=g(n)+h(n)` với threshold | Có | Có | Có | IDA* dùng `f(n)` để cắt nhánh theo ngưỡng tăng dần |
| Simple Hill Climbing | `h(n)` | Không | Có | Không | Chọn neighbor đầu tiên làm giảm heuristic |
| Steepest-Ascent Hill Climbing | `h(n)` | Không | Có | Không | Chọn neighbor có heuristic tốt nhất |
| Stochastic Hill Climbing | `h(n)` + ngẫu nhiên | Không | Có | Không | Chọn ngẫu nhiên trong các neighbor có cải thiện heuristic |
| Random-Restart Hill Climbing | `h(n)` qua nhiều restart | Không | Có | Không | Chạy nhiều lần leo đồi để giảm nguy cơ kẹt local optimum |
| Local Beam Search | `h(n)` trên beam | Không | Có | Không | Giữ `k` trạng thái có heuristic tốt nhất ở mỗi vòng |

Trong giao diện Streamlit, phần **Hồ sơ thuật toán đang chọn / Selected algorithm profile** cũng hiển thị bảng riêng:

```text
Component | Có dùng? | Ý nghĩa trong thuật toán đang chọn
g(n)      | ...      | ...
h(n)      | ...      | ...
f(n)      | ...      | ...
```

Nhờ vậy người xem có thể xác định ngay thuật toán đang chạy thuộc kiểu:

- tìm kiếm không heuristic;
- tìm kiếm theo chi phí `g(n)`;
- tìm kiếm heuristic `h(n)`;
- tìm kiếm tổng hợp `f(n)=g(n)+h(n)`;
- hoặc tìm kiếm cục bộ tối thiểu hóa `h(n)`.

## 7. Heuristic sử dụng trong dự án

### 7.1. Manhattan Distance

Manhattan Distance tính tổng khoảng cách hàng và cột của từng ô so với vị trí goal.

Công thức:

```text
h(s) = Σ |row_s(t) - row_g(t)| + |col_s(t) - col_g(t)|
```

Trong đó `t` chạy từ `1` đến `8`, không tính ô trống `0`.

Ví dụ:

- Nếu một ô lệch 1 hàng và 2 cột, đóng góp heuristic là `3`.
- Tổng của tất cả ô là `h(s)`.

Manhattan là heuristic **admissible** cho 8-Puzzle vì nó không bao giờ ước lượng vượt quá số bước thật cần thiết.

### 7.2. Misplaced Tiles

Misplaced Tiles đếm số ô đang không nằm đúng vị trí goal.

Công thức:

```text
h(s) = số ô t sao cho position_s(t) != position_goal(t)
```

Không tính ô trống `0`.

Heuristic này đơn giản hơn Manhattan nhưng thường kém chính xác hơn.

### 7.3. Quan hệ giữa hai heuristic chính

Trong bản nộp này, dropdown `h(n)` của app chính chỉ dùng đúng hai heuristic cơ bản:

1. `misplaced`: số ô sai vị trí, không tính ô trống `0`.
2. `manhattan`: tổng khoảng cách Manhattan của từng ô số tới vị trí goal.

Quan hệ cần nhớ:

```text
manhattan >= misplaced
```

Cả hai đều admissible cho 8-Puzzle chuẩn. `manhattan` thường tốt hơn vì không chỉ biết ô nào sai mà còn biết ô đó đang cách goal bao xa.

## 8. Danh sách thuật toán đã cài đặt

Dự án cài đặt đủ 27 thuật toán/biến thể theo 6 nhóm học thuật:

| Nhóm | Thuật toán |
|---|---|
| Uninformed Search | BFS, DFS, UCS, IDS |
| Informed Search | Greedy, A*, IDA* |
| Local Search | Simple Hill Climbing, Steepest-Ascent Hill Climbing, Stochastic Hill Climbing, Random-Restart Hill Climbing, Local Beam Search, Simulated Annealing |
| Complex Environments | AND-OR Search, No Observation Search, Partially Observable Search, Online Search |
| Constraint Satisfaction Problems | CSP Definition, Constraint Propagation, Path Consistency, Global Constraints, CSP Backtracking, Min-Conflicts, Constraint Graph |
| Adversarial / Stochastic Search | Minimax, Alpha-Beta Pruning, Expectimax |

Lưu ý học thuật: nhóm `Complex Environments`, `CSP` và `Adversarial / Stochastic Search` không phải solver tự nhiên của 8-Puzzle deterministic/fully observable. App vẫn chạy phiên bản mô phỏng có giới hạn trên state hiện tại và ghi rõ trace, message, guarantee/failure mode để phục vụ báo cáo môn AI.

## 9. Giải thích chi tiết từng thuật toán

### 9.1. BFS - Breadth-First Search

BFS là thuật toán tìm kiếm theo chiều rộng. Thuật toán mở rộng các node theo từng tầng.

Nguyên tắc:

```text
Luôn mở node nông nhất trước.
```

Frontier của BFS là hàng đợi FIFO.

Pseudo-code:

```text
frontier <- FIFO(start)
reached <- {start}

while frontier not empty:
    node <- pop_front(frontier)
    if node is goal:
        return solution
    for child in successors(node):
        if child not in reached:
            add child to frontier
            add child to reached
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Có, nếu không gian trạng thái hữu hạn |
| Optimal | Có, nếu mọi bước có chi phí bằng nhau |
| Ưu điểm | Tìm nghiệm ngắn nhất theo số bước |
| Nhược điểm | Tốn bộ nhớ vì frontier tăng rất nhanh |
| Phù hợp với 8-Puzzle | Tốt cho bài nhỏ hoặc trạng thái gần goal |

### 9.2. DFS - Depth-First Search

DFS là thuật toán tìm kiếm theo chiều sâu. Thuật toán đi sâu vào một nhánh trước khi quay lui.

Nguyên tắc:

```text
Luôn mở node sâu nhất trước.
```

Frontier của DFS là stack LIFO.

Pseudo-code:

```text
frontier <- Stack(start)
reached <- {start}

while frontier not empty:
    node <- pop(frontier)
    if node is goal:
        return solution
    if depth(node) < depth_limit:
        push successors(node)
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Không đảm bảo nếu không giới hạn hoặc có vòng lặp |
| Optimal | Không |
| Ưu điểm | Dùng ít bộ nhớ hơn BFS |
| Nhược điểm | Có thể đi sâu vào nhánh xấu |
| Trong app | Có giới hạn `dfs_depth_limit` để tránh chạy quá sâu |

### 9.3. UCS - Uniform Cost Search

UCS mở rộng node có chi phí đường đi `g(n)` nhỏ nhất.

Nguyên tắc:

```text
Luôn chọn node có g(n) nhỏ nhất.
```

Với 8-Puzzle trong dự án này, mỗi bước có chi phí bằng `1`, vì vậy UCS thường cho độ dài nghiệm giống BFS.

Pseudo-code:

```text
frontier <- PriorityQueue(start, priority=g)
best_g[start] <- 0

while frontier not empty:
    node <- pop_lowest_g(frontier)
    if node is goal:
        return solution
    for child in successors(node):
        if g(child) is better:
            update child in frontier
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Có, nếu chi phí không âm |
| Optimal | Có |
| Ưu điểm | Tổng quát hơn BFS khi chi phí bước khác nhau |
| Nhược điểm | Không dùng heuristic nên có thể mở nhiều node |
| Phù hợp với 8-Puzzle | Có ý nghĩa học thuật để so sánh với BFS |

### 9.4. IDS - Iterative Deepening Search

IDS kết hợp ưu điểm của BFS và DFS. Thuật toán chạy Depth-Limited Search nhiều lần với giới hạn tăng dần.

Nguyên tắc:

```text
Chạy DFS với limit = 0, 1, 2, 3, ...
```

Pseudo-code:

```text
for limit in 0..max_depth:
    result <- depth_limited_search(start, limit)
    if result found:
        return result
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Có nếu giới hạn đủ lớn |
| Optimal | Có với chi phí bước bằng nhau |
| Ưu điểm | Ít tốn bộ nhớ hơn BFS |
| Nhược điểm | Mở lại các node nông nhiều lần |
| Phù hợp với 8-Puzzle | Tốt để minh họa trade-off thời gian và bộ nhớ |

### 9.5. Greedy Best-First Search

Greedy chọn node có heuristic `h(n)` nhỏ nhất, tức là node có vẻ gần goal nhất.

Nguyên tắc:

```text
Luôn chọn node có h(n) nhỏ nhất.
```

Pseudo-code:

```text
frontier <- PriorityQueue(start, priority=h)

while frontier not empty:
    node <- pop_lowest_h(frontier)
    if node is goal:
        return solution
    expand node
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Không đảm bảo trong mọi trường hợp nếu không kiểm soát lặp |
| Optimal | Không |
| Ưu điểm | Thường chạy nhanh |
| Nhược điểm | Dễ bị heuristic dẫn sai |
| Phù hợp với 8-Puzzle | Dùng để thấy heuristic giúp giảm expanded node nhưng có rủi ro không tối ưu |

### 9.6. A*

A* là thuật toán tìm kiếm có thông tin, kết hợp chi phí đã đi và ước lượng chi phí còn lại.

Hàm đánh giá:

```text
f(n) = g(n) + h(n)
```

Trong đó:

- `g(n)`: chi phí từ start đến node `n`.
- `h(n)`: ước lượng chi phí từ node `n` đến goal.
- `f(n)`: tổng chi phí ước lượng của lời giải đi qua node `n`.

Pseudo-code:

```text
frontier <- PriorityQueue(start, priority=g+h)
best_g[start] <- 0

while frontier not empty:
    node <- pop_lowest_f(frontier)
    if node is goal:
        return solution
    for child in successors(node):
        if g(child) is better:
            update child in frontier
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Có với không gian hữu hạn |
| Optimal | Có nếu heuristic admissible |
| Ưu điểm | Thường mở ít node hơn BFS/UCS |
| Nhược điểm | Có thể tốn bộ nhớ |
| Phù hợp với 8-Puzzle | Rất phù hợp, đặc biệt với Manhattan Distance |

### 9.7. IDA* - Iterative Deepening A*

IDA* kết hợp ý tưởng của IDS và A*. Thuật toán dùng DFS nhưng giới hạn bởi ngưỡng `f(n)`.

Nguyên tắc:

```text
Chỉ đi sâu nếu f(n) <= threshold.
```

Pseudo-code:

```text
threshold <- h(start)

repeat:
    result, next_threshold <- DFS_bounded_by_f(start, threshold)
    if result found:
        return result
    threshold <- next_threshold
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Có nếu không bị giới hạn vòng lặp |
| Optimal | Có với heuristic admissible |
| Ưu điểm | Tiết kiệm bộ nhớ hơn A* |
| Nhược điểm | Có thể mở lại node nhiều lần |
| Phù hợp với 8-Puzzle | Rất có giá trị học thuật vì thể hiện trade-off giữa A* và IDS |

### 9.8. Simple Hill Climbing

Simple Hill Climbing là thuật toán tìm kiếm cục bộ. Thuật toán chỉ quan tâm trạng thái hiện tại và các láng giềng.

Nguyên tắc:

```text
Chọn láng giềng đầu tiên có h(n) tốt hơn hiện tại.
```

Pseudo-code:

```text
current <- start

while exists improving neighbor:
    current <- first improving neighbor

return current
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Không |
| Optimal | Không |
| Ưu điểm | Đơn giản, ít bộ nhớ |
| Nhược điểm | Dễ kẹt local optimum hoặc plateau |
| Phù hợp với 8-Puzzle | Dùng để minh họa hạn chế của local search |

### 9.9. Steepest-Ascent Hill Climbing

Biến thể này xét toàn bộ láng giềng và chọn láng giềng tốt nhất.

Nguyên tắc:

```text
Chọn neighbor có h(n) nhỏ nhất trong tất cả neighbor.
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Không |
| Optimal | Không |
| Ưu điểm | Quyết định tốt hơn Simple Hill Climbing |
| Nhược điểm | Vẫn kẹt local optimum |
| Phù hợp với 8-Puzzle | Dùng để so sánh với Simple Hill Climbing |

### 9.10. Stochastic Hill Climbing

Stochastic Hill Climbing chọn ngẫu nhiên một láng giềng có cải thiện.

Nguyên tắc:

```text
Nếu có nhiều neighbor tốt hơn, chọn ngẫu nhiên một neighbor.
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Không |
| Optimal | Không |
| Ưu điểm | Có tính ngẫu nhiên, đôi khi tránh được một số đường xấu |
| Nhược điểm | Kết quả phụ thuộc seed |
| Phù hợp với 8-Puzzle | Dùng để minh họa vai trò của randomness trong local search |

### 9.11. Random-Restart Hill Climbing

Random-Restart Hill Climbing chạy hill climbing nhiều lần từ các điểm khởi động khác nhau.

Trong app, các điểm restart được tạo bằng random-walk từ start để lời giải vẫn có quan hệ với trạng thái bắt đầu.

Nguyên tắc:

```text
Chạy hill climbing nhiều lần và giữ nghiệm tốt nhất.
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Không tuyệt đối |
| Optimal | Không |
| Ưu điểm | Giảm nguy cơ kẹt local optimum |
| Nhược điểm | Tốn thời gian hơn hill climbing thường |
| Phù hợp với 8-Puzzle | Tốt để minh họa cách restart cải thiện local search |

### 9.12. Local Beam Search

Local Beam Search duy trì nhiều trạng thái cùng lúc. Ở mỗi vòng, thuật toán sinh successor từ tất cả trạng thái trong beam và giữ lại `k` trạng thái tốt nhất.

Nguyên tắc:

```text
Giữ k trạng thái tốt nhất theo h(n).
```

Pseudo-code:

```text
beam <- {start}

while step limit not reached:
    candidates <- successors of all states in beam
    beam <- k best candidates by h
    if goal in beam:
        return solution
```

Đặc điểm:

| Tiêu chí | Nhận xét |
|---|---|
| Complete | Không |
| Optimal | Không |
| Ưu điểm | Khám phá nhiều hướng hơn hill climbing |
| Nhược điểm | Beam nhỏ có thể bỏ mất nhánh tốt |
| Phù hợp với 8-Puzzle | Dùng để so sánh local search đơn trạng thái và đa trạng thái |

## 10. Bảng so sánh tổng quát

| Thuật toán | Nhóm | Dùng heuristic | Complete | Optimal | Bộ nhớ |
|---|---|---:|---:|---:|---|
| BFS | Uninformed | Không | Có | Có, nếu cost=1 | Cao |
| DFS | Uninformed | Không | Không đảm bảo | Không | Thấp |
| UCS | Uninformed / Cost-based | Không | Có | Có | Cao |
| IDS | Uninformed | Không | Có nếu depth đủ | Có, nếu cost=1 | Thấp |
| Greedy | Informed | Có | Không đảm bảo | Không | Trung bình |
| A* | Informed | Có | Có | Có nếu h admissible | Cao |
| IDA* | Informed | Có | Có nếu không bị limit | Có nếu h admissible | Thấp hơn A* |
| Simple Hill Climbing | Local Search | Có | Không | Không | Rất thấp |
| Steepest-Ascent Hill Climbing | Local Search | Có | Không | Không | Rất thấp |
| Stochastic Hill Climbing | Local Search | Có | Không | Không | Rất thấp |
| Random-Restart Hill Climbing | Local Search | Có | Không tuyệt đối | Không | Thấp |
| Local Beam Search | Local Search | Có | Không | Không | Tùy beam width |

## 11. Ý nghĩa bảng trace Node / Frontier / Reached

Mỗi dòng trace biểu diễn một vòng lặp chính của thuật toán. Với BFS, DFS, UCS, Greedy, A* và Local Beam Search, `Frontier` và `Reached` được ghi theo snapshot **sau khi node hiện tại đã được expand**. Với node goal hoặc node bị prune bởi threshold/limit, `Generated Children = 0` để thể hiện rằng thuật toán không sinh successor từ node đó.

| Cột | Ý nghĩa |
|---|---|
| `Step` | Số thứ tự vòng lặp |
| `Algorithm` | Thuật toán đang chạy |
| `Node` | Node hiện tại được chọn để xét |
| `Action` | Hành động sinh ra node hiện tại |
| `Depth` | Độ sâu node |
| `g` | Chi phí từ start đến node |
| `h` | Heuristic từ node đến goal |
| `f` | Hàm đánh giá ưu tiên |
| `Priority Rule` | Quy tắc thuật toán dùng để chọn node tiếp theo |
| `Selection Key` | Giá trị cụ thể dùng ở vòng lặp hiện tại, ví dụ `g`, `h`, `f`, threshold hoặc temperature |
| `Generated Children` | Số successor hợp lệ được sinh ra |
| `Skipped States` | Số state bị bỏ qua do đã reached, nằm trên path hiện tại hoặc bị giới hạn depth |
| `Frontier` | Các node đang chờ mở rộng |
| `Reached` | Các trạng thái đã được ghi nhận |
| `Decision/Note` | Ghi chú quyết định của thuật toán |

## 12. Cách dùng giao diện

### 12.1. Chọn ngôn ngữ

Ở sidebar bên trái, chọn:

- `Tiếng Việt`
- `English`

### 12.2. Chú thích khi hover

Giao diện có các chú thích pop-up để người học hiểu nhanh từng thành phần.

Cách sử dụng:

- Di chuột vào biểu tượng trợ giúp cạnh nhãn như `Thuật toán`, `Heuristic`, `Seed`, `Số bước tự trộn`, `Giới hạn mở rộng node`.
- Di chuột vào các nút như `Tự trộn ma trận`, `Chạy thuật toán đã chọn`, `So sánh tất cả thuật toán` để biết thao tác đó dùng làm gì.
- Di chuột vào từng ô trong ma trận Start hoặc Goal để xem ô đó đang ở hàng, cột nào; ô `0` được chú thích là ô trống có thể di chuyển.
- Sau khi chạy thuật toán, di chuột vào các chỉ số `g(n)`, `h(n)`, `f(n)` trong khu vực theo dõi từng bước để xem ý nghĩa học thuật của từng hàm.

Mục đích của phần hover này là giúp giao diện dùng được như một công cụ học tập: người xem không cần nhớ trước toàn bộ thuật ngữ mà vẫn hiểu được từng control, từng ma trận và từng đại lượng đánh giá.

### 12.3. Tự trộn ma trận

Bấm:

```text
Tự trộn ma trận / Shuffle matrix
```

Chương trình sẽ tạo một start state solvable bằng cách đi ngẫu nhiên từ goal.

### 12.4. Chọn thuật toán

Chọn một thuật toán trong danh sách:

```text
BFS, DFS, UCS, IDS, Greedy, A*, IDA*, Simple Hill Climbing,
Steepest-Ascent Hill Climbing, Stochastic Hill Climbing,
Random-Restart Hill Climbing, Local Beam Search
```

### 12.5. Chạy thuật toán

Bấm:

```text
Chạy thuật toán đã chọn / Run selected algorithm
```

App sẽ hiển thị:

- bảng tổng kết;
- ma trận goal và final state;
- từng bước lời giải;
- bảng trace Node / Frontier / Reached.

### 12.5.1. Theo dõi đường đi từng bước

Sau khi thuật toán tìm được nghiệm, app hiển thị khu vực:

```text
Theo dõi đường đi từng bước / Step-by-step path viewer
```

Khu vực này dùng để quan sát thuật toán đi từ Start đến Goal theo từng hành động.

Các thành phần chính:

| Thành phần | Ý nghĩa |
|---|---|
| `Bước trước / Previous step` | Quay lại trạng thái trước đó trong lời giải |
| `Bước sau / Next step` | Đi tới trạng thái kế tiếp trong lời giải |
| Slider chọn bước | Nhảy trực tiếp tới một bước bất kỳ |
| `Trạng thái trước bước đi` | Ma trận ở bước trước |
| `Trạng thái hiện tại` | Ma trận sau khi áp dụng hành động |
| `Hành động vừa thực hiện` | Nước đi tạo ra trạng thái hiện tại |
| `Hành động tiếp theo` | Nước đi kế tiếp nếu chưa đến Goal |
| `g(n)` | Số bước đã đi từ Start đến trạng thái hiện tại |
| `h(n)` | Heuristic của trạng thái hiện tại |
| `f(n)` | Tổng `g(n) + h(n)` |
| `Chuỗi hành động` | Toàn bộ đường đi từ Start đến Goal |
| `Bảng đường đi đầy đủ` | Bảng liệt kê từng bước, hành động, `g`, `h`, `f` và ma trận |

Ví dụ nếu app hiển thị:

```text
Hành động vừa thực hiện: Phải
```

nghĩa là từ trạng thái trước đó, ô trống `0` đã di chuyển sang phải để tạo ra trạng thái hiện tại.

Tính năng này giúp người học không chỉ biết kết quả cuối cùng mà còn theo dõi được toàn bộ quá trình lời giải di chuyển qua từng trạng thái.

### 12.6. So sánh toàn bộ thuật toán

Bấm:

```text
So sánh tất cả thuật toán / Compare all algorithms
```

App sẽ chạy toàn bộ thuật toán trên cùng một start state và trả về bảng so sánh.

### 12.7. Algorithm Certificate và Report

Sau khi chạy một thuật toán, vùng kết quả được chia thành các tab:

- `Summary`: metric cards, Algorithm Certificate dạng status chip, kết luận học thuật và Path playback.
- `Trace`: bảng trace mở rộng, Trace Story “Why This Node?”, glossary và hồ sơ thuật toán.
- `Heuristics`: Heuristic Inspector với hai h(n) chính `misplaced`, `manhattan` và đóng góp từng ô.
- `Experiment`: benchmark deterministic trên `easy_2`, `medium_10`, `hard_20`, `unsolvable_demo`, kèm `Optimal Gap`.
- `Report`: tải Coursework Report Markdown và tạo Submission Pack gồm Markdown, DOCX, PDF, HTML, CSV benchmark; báo cáo có PEAS, setup, metrics, certificate, heuristic inspector, path, trace preview, trace story và experiment summary nếu đã chạy.

Algorithm Certificate kiểm tra:

- path có bắt đầu từ Start và đi qua các action hợp lệ không;
- path cost có khớp số action không;
- terminal state có đúng Goal không;
- unsolvable input có bị dừng sớm trước khi mở rộng node không;
- heuristic có trả giá trị hợp lệ không.

Experiment Lab mặc định tắt trace (`max_trace_rows=0`) để benchmark không chậm khi demo. Các thuật toán tối ưu như BFS, UCS, A* và IDA* được dùng làm baseline cost khi điều kiện giới hạn đủ lớn; Greedy và local search được xem là kết quả thực nghiệm, không phải bảo đảm tối ưu.

## 13. Các giới hạn để tránh treo chương trình

Vì một số thuật toán có thể mở rất nhiều trạng thái, app có các giới hạn:

| Tham số | Ý nghĩa |
|---|---|
| `max_expansions` | Giới hạn số node mở rộng |
| `max_trace_rows` | Giới hạn số dòng trace hiển thị |
| `frontier_preview` | Số trạng thái frontier hiển thị trước |
| `reached_preview` | Số trạng thái reached hiển thị trước |
| `ids_max_depth` | Độ sâu tối đa của IDS |
| `ida_max_iterations` | Số vòng threshold tối đa của IDA* |
| `local_max_steps` | Số bước tối đa cho local search |
| `random_restarts` | Số lần restart cho Random-Restart Hill Climbing |
| `beam_width` | Số trạng thái giữ lại trong Local Beam Search |

## 14. Kiểm thử đã thực hiện

Các kiểm thử chính:

1. Goal state trả về nghiệm 0 bước.
2. Puzzle dễ trong 2 bước cho BFS, UCS, IDS và A* cùng độ dài nghiệm.
3. Random start luôn solvable.
4. Unsolvable state bị phát hiện sớm.
5. Trace table luôn có `Node`, `Frontier`, `Reached`, `Priority Rule`, `Selection Key`, `Generated Children`, `Skipped States`.
6. Local Beam Search giải được puzzle một bước.
7. `manhattan >= misplaced` trên các state gần goal và không vượt true distance trong vùng test nông.
8. `validate_result()` pass với lời giải hợp lệ và fail rõ với path bị sửa sai.
9. `explain_heuristic()` trả đúng totals cho `misplaced`, `manhattan` và đóng góp từng ô.
10. `build_trace_story()` giải thích đúng selection rule cho A*, IDA* và Simulated Annealing.
11. Trace semantics khớp mô hình học thuật: frontier/reached post-expansion, IDA* prune không sinh child, Local Beam đếm successor đúng, Simulated Annealing ghi node trước accept/reject.
12. `run_experiment_suite()` deterministic ở các trường thuật toán quan trọng và xử lý unsolvable preset đúng.
13. `export_run_markdown()` tạo được báo cáo có metrics, certificate, heuristic inspector, path, trace preview và trace story.
14. Streamlit app chạy được tại `http://127.0.0.1:8501`.
15. Giao diện song ngữ hoạt động.
16. Ma trận Start/Goal hiển thị dạng 3x3 không có header cột, xếp dọc để tránh tràn layout.
17. Phần học thuật hiển thị đúng trong cả Tiếng Việt và English.

Lệnh kiểm thử:

```powershell
python .\eight_puzzle_search_app.py --self-test
python .\tests\test_search_behavior.py
python .\8_puzzle_ai\tests\test_puzzle.py
python -m py_compile .\eight_puzzle_search_app.py .\streamlit_eight_puzzle_app.py .\8_puzzle_ai\app.py
```

## 15. Nhận xét học thuật

Qua chương trình có thể rút ra một số nhận xét:

- BFS và UCS thường tìm nghiệm tối ưu nhưng có thể mở nhiều node.
- DFS dùng ít bộ nhớ hơn nhưng không đảm bảo tối ưu.
- IDS cân bằng giữa BFS và DFS: tối ưu theo số bước nhưng lặp lại mở node.
- Greedy thường nhanh nhưng không chắc tối ưu.
- A* là thuật toán mạnh cho 8-Puzzle khi dùng Manhattan Distance.
- IDA* tiết kiệm bộ nhớ hơn A* nhưng có thể mở lại node nhiều lần.
- Hill Climbing đơn giản và ít bộ nhớ nhưng dễ kẹt local optimum.
- Random-Restart Hill Climbing giúp giảm rủi ro kẹt nhưng không đảm bảo tối ưu.
- Local Beam Search khám phá nhiều hướng hơn hill climbing nhưng phụ thuộc `beam_width`.

## 16. Hướng phát triển

Có thể mở rộng dự án theo các hướng:

1. Thêm thuật toán Bidirectional Search.
2. Thêm RBFS hoặc SMA*.
3. Cho phép người dùng chọn goal tùy ý.
4. Xuất trace ra CSV hoặc Excel.
5. Vẽ cây tìm kiếm bằng graph.
6. Thêm animation từng bước di chuyển.
7. Tạo báo cáo PDF tự động sau mỗi lần chạy.
8. Thêm thống kê trung bình trên nhiều random start.
9. Hỗ trợ 15-Puzzle.

## 17. Kết luận

Dự án cung cấp một môi trường học tập trực quan cho bài toán 8-Puzzle. Thay vì chỉ in kết quả cuối cùng, chương trình cho thấy cách thuật toán chọn node, quản lý frontier, cập nhật reached và tìm đường đi đến goal.

Điểm mạnh của dự án là kết hợp giữa:

- mô phỏng thuật toán;
- bảng trace chi tiết;
- so sánh thực nghiệm;
- giải thích học thuật;
- giao diện song ngữ;
- khả năng chạy bằng Streamlit, terminal hoặc Jupyter.

Do đó, dự án phù hợp để dùng trong báo cáo môn Trí tuệ nhân tạo, bài thực hành về search algorithms hoặc demo lớp học về 8-Puzzle.
