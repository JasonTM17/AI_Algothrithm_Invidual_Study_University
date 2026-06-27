# Kịch bản demo nộp bài 8-Puzzle Search Lab

## 1. Mở app chính

```powershell
python -m streamlit run .\streamlit_eight_puzzle_app.py
```

App chính gồm core `eight_puzzle_search_app.py` và UI `streamlit_eight_puzzle_app.py`.
Package `8_puzzle_ai/` là phần phụ để tham khảo/educational.

## 2. Demo thuật toán solver chuẩn

1. Chọn preset `easy_2`.
2. Chọn nhóm `Informed Search`.
3. Chọn thuật toán `A*`.
4. Chọn heuristic `manhattan`.
5. Bấm `Chạy thuật toán đã chọn`.

Điểm cần nói:
- A* chọn node theo `f(n)=g(n)+h(n)`.
- Với Manhattan admissible, A* tối ưu trên 8-puzzle chuẩn.
- Tab `Trace` giải thích Node, Frontier, Reached và “Why This Node?”.

## 3. So sánh BFS, UCS, A*

1. Giữ preset `easy_2` hoặc `medium_10`.
2. Bấm `So sánh tất cả thuật toán`.
3. Quan sát BFS, UCS, A* có cùng path cost khi giới hạn đủ.

Điểm cần nói:
- BFS tối ưu vì chi phí mỗi bước bằng 1.
- UCS tối ưu vì chọn min `g(n)`.
- A* tối ưu vì chọn min `g(n)+h(n)` với heuristic admissible.

## 4. Demo unsolvable

1. Chọn preset `unsolvable_demo`.
2. Chạy `A*` + `manhattan`.
3. Quan sát app dừng sớm, `Expanded = 0`.

Điểm cần nói:
- 8-puzzle 3x3 kiểm tra solvability bằng inversion parity.
- Nếu state không solvable, không mở rộng node để tránh tìm kiếm vô hạn.

## 5. Demo Goal biết một phần

1. Chọn nhóm `Complex Environments`.
2. Chọn `Partially Observable Search`.
3. Nhập `Goal biết một phần`, ví dụ:

```text
1 2 ? ? ? ? ? ? ?
```

hoặc bấm `Random Goal một phần`.

Điểm cần nói:
- Đây là dạng partial knowledge, không phải solver chuẩn fully observable.
- Agent dùng thông tin quan sát một phần để đánh giá state.
- Bạn có thể nhập pattern bất kỳ gồm số `0..8` và `?` để demo phần quan sát một phần.

## 6. Demo CSP

1. Chọn nhóm `Constraint Satisfaction Problems`.
2. Chọn `CSP Definition`, `Constraint Propagation`, hoặc `CSP Backtracking`.

Điểm cần nói:
- CSP diễn đạt bài toán bằng biến, miền giá trị và ràng buộc.
- Với 8-puzzle, CSP được dùng như mô hình lập kế hoạch theo horizon.
- Đây là demo học thuật, không quảng bá là solver chuẩn nhanh nhất.

## 7. Demo Run/Compare trên Start đã chọn

Trong app Streamlit chính:

```powershell
python -m streamlit run .\streamlit_eight_puzzle_app.py
```

Mở chế độ `8-Puzzle Search` trong sidebar.

1. Chọn preset, nhập Start thủ công hoặc bấm `Tự trộn ma trận`.
2. Chọn nhóm thuật toán và thuật toán cần chạy.
3. Bấm `Chạy thuật toán đã chọn`; xác nhận Start không đổi.
4. Trong Path playback và Trace Player, dùng Bước trước/Bước sau/Về đầu, Play/Pause, tốc độ và slider.
5. Bấm `So sánh nhóm đang chọn` để chạy toàn bộ nhóm trên cùng Start và cấu hình.

Điểm cần nói:
- Chỉ nút `Tự trộn ma trận` tạo Start solvable mới; Run/Compare không thay đổi bài đang trình bày.
- Compare dùng cùng Start, heuristic, seed, giới hạn và successor order để kết quả công bằng, tái lập được.
- Mỗi thuật toán vẫn có trace riêng để kiểm tra logic chọn node.
- Certificate phân biệt path hợp lệ, đạt Goal, lý do kết thúc và chứng minh tối ưu.

## 8. Demo đối kháng/xác suất

1. Chọn nhóm `Adversarial / Stochastic Search`.
2. Chọn `Minimax`, `Alpha-Beta Pruning`, hoặc `Expectimax`.

Điểm cần nói:
- 8-puzzle chuẩn không có đối thủ/chance node.
- Vì vậy nhóm này dùng Caro mini-game:
  - MAX là quân `X`, chọn nước đi tốt nhất.
  - MIN là quân `O` trong Minimax/Alpha-Beta.
  - Expectimax xem phản hồi của `O` như chance/random outcome.
- Mục tiêu là chứng minh hiểu đúng tên và dạng bài toán của thuật toán.

## 9. Xuất báo cáo

1. Sau khi chạy thuật toán, mở tab `Report`.
2. Tải Markdown hoặc tạo Submission Pack.
3. Các file có thể tải: Markdown, DOCX, PDF, HTML, CSV benchmark.

Báo cáo nên có:
- Start/Goal.
- Thuật toán và công thức chọn node.
- PEAS.
- Certificate.
- Trace preview.
- Heuristic inspector.
- Benchmark/experiment.
- Kết luận complete/optimal/failure mode.

## 10. Checklist trước khi nộp

- [ ] Chạy được Streamlit app chính.
- [ ] Chạy được A* Manhattan và xem được trace.
- [ ] Chứng minh BFS/UCS/A* cùng optimal cost trên state nông.
- [ ] Có PEAS cho thuật toán đang demo.
- [ ] Có Node / Frontier / Reached rõ trong trace.
- [ ] Có giải thích `misplaced` và `manhattan`.
- [ ] Có demo unsolvable dừng sớm.
- [ ] Run/Compare giữ nguyên Start đã chọn và có bảng số bước/thời gian.
- [ ] Có báo cáo tải xuống.
- [ ] Toàn bộ test local pass.

## 11. Checklist UI/UX trước khi demo trực tiếp

- [ ] First viewport nhìn rõ Start, Goal, Preset, Nhóm thuật toán, Thuật toán, Heuristic và nút `Chạy thuật toán đã chọn`.
- [ ] Header và subtitle không bị chìm trên dark mode.
- [ ] Ô trống hiển thị bằng số `0` gạch chân, không phải ô đen rỗng.
- [ ] `h(n)` trong UI chỉ có `misplaced` và `manhattan`.
- [ ] Thuật toán không dùng heuristic có ghi chú rõ h(n) chỉ để giải thích/certificate.
- [ ] Thuật toán Complex/CSP/Adversarial có chip hoặc ghi chú `mô phỏng học thuật`.
- [ ] Tab `Trace` có Trace Player, Frontier/Reached sau mở rộng, và vẫn còn bảng trace gốc.
- [ ] Path/Trace playback có Bước trước, Bước sau, Về đầu, Play, Pause và tốc độ phát.
- [ ] Mobile `390x844` không có horizontal scroll.
- [ ] Report Pack hiện đủ Markdown/DOCX/PDF/HTML/CSV.
