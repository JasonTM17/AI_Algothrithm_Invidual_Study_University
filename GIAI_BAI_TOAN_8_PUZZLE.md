# GIẢI BÀI TOÁN 8-PUZZLE BẰNG CÁC THUẬT TOÁN TÌM KIẾM

---

## PHẦN CHUNG

### 1. Kiểm tra bài toán có giải được không

**Trạng thái ban đầu S:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 0 │ 6 │
├───┼───┼───┤
│ 4 │ 7 │ 8 │
└───┴───┴───┘
```

**Trạng thái đích G:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
├───┼───┼───┤
│ 7 │ 8 │ 0 │
└───┴───┴───┘
```

#### Công thức kiểm tra:

Bài toán 8-puzzle có giải được khi và chỉ khi **số nghịch thế của trạng thái ban đầu** và **số nghịch thế của trạng thái đích** có cùng tính chẵn lẻ.

**Số nghịch thế** = Số cặp số (i, j) sao cho i < j nhưng i xuất hiện sau j trong dãy (bỏ qua số 0).

#### Tính số nghịch thế của S:

Dãy S đọc theo hàng (bỏ qua 0): `1, 2, 3, 5, 6, 4, 7, 8`

| Số | Các số nhỏ hơn xuất hiện sau | Số nghịch thế |
|----|------------------------------|---------------|
| 1 | không có | 0 |
| 2 | không có | 0 |
| 3 | không có | 0 |
| 5 | 4 | 1 |
| 6 | 4 | 1 |
| 4 | không có | 0 |
| 7 | không có | 0 |
| 8 | không có | 0 |

**Tổng nghịch thế của S = 0 + 0 + 0 + 1 + 1 + 0 + 0 + 0 = 2 (CHẴN)**

#### Tính số nghịch thế của G:

Dãy G (bỏ qua 0): `1, 2, 3, 4, 5, 6, 7, 8`

Dãy đã sắp xếp tăng dần → **Tổng nghịch thế của G = 0 (CHẴN)**

#### Kết luận:

- S có 2 nghịch thế (chẵn)
- G có 0 nghịch thế (chẵn)
- **Cùng tính chẵn lẻ → BÀI TOÁN CÓ GIẢI ĐƯỢC! ✓**

---

### 2. Tập hành động hợp lệ

Tại mỗi trạng thái, ô trống (số 0) có thể di chuyển theo 4 hướng nếu hợp lệ:

| Hành động | Ký hiệu | Điều kiện | Ý nghĩa |
|-----------|---------|-----------|---------|
| Up | U | Ô trống không ở hàng 1 | Đổi chỗ ô trống với ô bên trên |
| Down | D | Ô trống không ở hàng 3 | Đổi chỗ ô trống với ô bên dưới |
| Left | L | Ô trống không ở cột 1 | Đổi chỗ ô trống với ô bên trái |
| Right | R | Ô trống không ở cột 3 | Đổi chỗ ô trống với ô bên phải |

---

### 3. Heuristic

**h(n) = Số ô sai vị trí** (không tính ô 0)

**Ví dụ với trạng thái S:**
```
S:              G:
┌───┬───┬───┐   ┌───┬───┬───┐
│ 1 │ 2 │ 3 │   │ 1 │ 2 │ 3 │  ← Đúng: 1,2,3
├───┼───┼───┤   ├───┼───┼───┤
│ 5 │ 0 │ 6 │   │ 4 │ 5 │ 6 │  ← Sai: 5,6; Đúng: không
├───┼───┼───┤   ├───┼───┼───┤
│ 4 │ 7 │ 8 │   │ 7 │ 8 │ 0 │  ← Sai: 4,7,8
└───┴───┴───┘   └───┴───┴───┘
```

Kiểm tra từng ô:
- Ô 1: vị trí (0,0) → cần (0,0) ✓ ĐÚNG
- Ô 2: vị trí (0,1) → cần (0,1) ✓ ĐÚNG
- Ô 3: vị trí (0,2) → cần (0,2) ✓ ĐÚNG
- Ô 5: vị trí (1,0) → cần (1,1) ✗ SAI
- Ô 6: vị trí (1,2) → cần (1,2) ✓ ĐÚNG
- Ô 4: vị trí (2,0) → cần (1,0) ✗ SAI
- Ô 7: vị trí (2,1) → cần (2,0) ✗ SAI
- Ô 8: vị trí (2,2) → cần (2,1) ✗ SAI

**h(S) = 4 ô sai vị trí** (ô 5, 4, 7, 8)

---

## THUẬT TOÁN 1: SIMULATED ANNEALING

### 1. Định nghĩa thuật toán

**Simulated Annealing (SA)** là thuật toán tìm kiếm cục bộ lấy cảm hứng từ quá trình nung và làm nguội kim loại trong luyện kim.

**Nguyên lý:**
- Luôn chấp nhận trạng thái láng giềng tốt hơn (h thấp hơn)
- Có xác suất chấp nhận trạng thái xấu hơn dựa trên nhiệt độ T
- Nhiệt độ T giảm dần theo thời gian (làm nguội)
- Xác suất chấp nhận trạng thái xấu: **P = e^(-Δh/T)**

### 2. Ý tưởng áp dụng vào 8-puzzle

- Mỗi trạng thái là một cấu hình của bảng 8-puzzle
- Láng giềng = các trạng thái sinh ra từ việc di chuyển ô trống (U, D, L, R)
- h(n) = số ô sai vị trí
- Bắt đầu với nhiệt độ cao T₀ = 100, cho phép chấp nhận nhiều bước đi xấu
- Giảm nhiệt độ dần theo tỷ lệ α = 0.95, cuối cùng chỉ chấp nhận bước đi tốt

### 3. Input và Output

**Input:**
- Trạng thái ban đầu S
- Trạng thái đích G
- Nhiệt độ ban đầu T₀ = 100
- Tỷ lệ làm nguội α = 0.95
- Nhiệt độ tối thiểu T_min = 0.01
- Số bước tối đa = 1000

**Output:**
- Trạng thái tốt nhất tìm được
- Đường đi (nếu tìm thấy goal)

### 4. Quy tắc chọn node

1. Chọn ngẫu nhiên một láng giềng từ current state
2. Tính Δh = h(neighbor) - h(current)
3. Nếu Δh < 0: chấp nhận ngay (tốt hơn)
4. Nếu Δh ≥ 0: chấp nhận với xác suất P = e^(-Δh/T)
5. Giảm nhiệt độ: T = T × α
6. Lặp lại cho đến khi tìm thấy goal hoặc T < T_min

### 5. Bảng chạy từng bước chi tiết

**Trạng thái ban đầu S:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │  h(S) = 4
├───┼───┼───┤
│ 5 │ 0 │ 6 │
├───┼───┼───┤
│ 4 │ 7 │ 8 │
└───┴───┴───┘
```

---

#### Bước 0: Khởi tạo

| Thành phần | Giá trị |
|------------|---------|
| **Current State** | S |
| **Temperature T** | 100.0 |
| **h(current)** | 4 |
| **Best State** | S |
| **Reached** | {S} |

---

#### Bước 1: Xét hành động D (Down)

**Current State (S):**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 0 │ 6 │
├───┼───┼───┤
│ 4 │ 7 │ 8 │
└───┴───┴───┘
```

**Frontier (các láng giềng có thể chọn):**

| STT | State | Action | h |
|-----|-------|--------|---|
| 1 | `┌───┬───┬───┐`<br>`│ 1 │ 0 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 2 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | U | 5 |
| 2 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 0 │ 8 │`<br>`└───┴───┴───┘` | D | 5 |
| 3 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 0 │ 5 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | L | 5 |
| 4 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 6 │ 0 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | R | 3 |

**Chọn ngẫu nhiên:** Action = D

**Neighbor State (sau khi thực hiện D):**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 7 │ 6 │
├───┼───┼───┤
│ 4 │ 0 │ 8 │
└───┴───┴───┘
```

**Tính toán:**
- h(neighbor) = 5
- Δh = h(neighbor) - h(current) = 5 - 4 = +1
- P(accept) = e^(-Δh/T) = e^(-1/100) = e^(-0.01) ≈ 0.99
- Random = 0.85 < 0.99 → **CHẤP NHẬN**

**Reached sau bước 1:** {S, S_D}

| Thành phần | Giá trị |
|------------|---------|
| **Current** | S_D |
| **T** | 100.0 |
| **h** | 5 |
| **Accepted?** | ✓ (P=0.99) |

---

#### Bước 2: Xét hành động L (Left)

**Current State (S_D):**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 7 │ 6 │
├───┼───┼───┤
│ 4 │ 0 │ 8 │
└───┴───┴───┘
```

**Frontier (các láng giềng):**

| STT | State | Action | h |
|-----|-------|--------|---|
| 1 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | U | 4 |
| 2 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 0 │ 4 │ 8 │`<br>`└───┴───┴───┘` | L | 6 |
| 3 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 8 │ 0 │`<br>`└───┴───┴───┘` | R | 6 |

**Chọn ngẫu nhiên:** Action = L

**Neighbor State:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 7 │ 6 │
├───┼───┼───┤
│ 0 │ 4 │ 8 │
└───┴───┴───┘
```

**Tính toán:**
- h(neighbor) = 6
- Δh = 6 - 5 = +1
- P(accept) = e^(-1/95) ≈ 0.99
- Random = 0.72 < 0.99 → **CHẤP NHẬN**

**Reached sau bước 2:** {S, S_D, S_DL}

| Thành phần | Giá trị |
|------------|---------|
| **Current** | S_DL |
| **T** | 95.0 |
| **h** | 6 |
| **Accepted?** | ✓ (P=0.99) |

---

#### Bước 3: Xét hành động U (Up)

**Current State (S_DL):**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 7 │ 6 │
├───┼───┼───┤
│ 0 │ 4 │ 8 │
└───┴───┴───┘
```

**Frontier:**

| STT | State | Action | h |
|-----|-------|--------|---|
| 1 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 0 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 4 │ 8 │`<br>`└───┴───┴───┘` | U | 5 |
| 2 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 0 │ 8 │`<br>`└───┴───┴───┘` | R | 5 |

**Chọn:** Action = U

**Neighbor State:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 0 │ 7 │ 6 │
├───┼───┼───┤
│ 5 │ 4 │ 8 │
└───┴───┴───┘
```

**Tính toán:**
- h(neighbor) = 5
- Δh = 5 - 6 = -1 (tốt hơn!)
- P(accept) = 1.0 (chấp nhận ngay vì Δh < 0)
- **CHẤP NHẬN**

**Reached sau bước 3:** {S, S_D, S_DL, S_DLU}

| Thành phần | Giá trị |
|------------|---------|
| **Current** | S_DLU |
| **T** | 90.25 |
| **h** | 5 |
| **Accepted?** | ✓ (tốt hơn) |

---

#### Bước 4: Xét hành động R (Right)

**Current State (S_DLU):**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 0 │ 7 │ 6 │
├───┼───┼───┤
│ 5 │ 4 │ 8 │
└───┴───┴───┘
```

**Frontier:**

| STT | State | Action | h |
|-----|-------|--------|---|
| 1 | `┌───┬───┬───┐`<br>`│ 0 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 1 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 4 │ 8 │`<br>`└───┴───┴───┘` | U | 6 |
| 2 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 7 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 4 │ 8 │`<br>`└───┴───┴───┘` | R | 4 |
| 3 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 0 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 4 │ 8 │`<br>`└───┴───┴───┘` | D | 6 |

**Chọn:** Action = R

**Neighbor State:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 7 │ 0 │ 6 │
├───┼───┼───┤
│ 5 │ 4 │ 8 │
└───┴───┴───┘
```

**Tính toán:**
- h(neighbor) = 4
- Δh = 4 - 5 = -1 (tốt hơn!)
- **CHẤP NHẬN NGAY**

**Reached sau bước 4:** {S, S_D, S_DL, S_DLU, S_DLUR}

| Thành phần | Giá trị |
|------------|---------|
| **Current** | S_DLUR |
| **T** | 85.74 |
| **h** | 4 |
| **Best so far** | h=4 |

---

#### Tiếp tục đến khi tìm thấy Goal...

**Bước N (khi T ≈ 8):**

**Current State:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
├───┼───┼───┤
│ 7 │ 0 │ 8 │
└───┴───┴───┘
```
h = 1

**Frontier:**

| STT | State | Action | h |
|-----|-------|--------|---|
| 1 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 7 │ 5 │ 8 │`<br>`└───┴───┴───┘` | U | 2 |
| 2 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 5 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 7 │ 8 │ 0 │`<br>`└───┴───┴───┘` | R | 0 ← GOAL! |

**Chọn:** Action = R

**Neighbor State = GOAL:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
├───┼───┼───┤
│ 7 │ 8 │ 0 │
└───┴───┴───┘
```

**h = 0 → TÌM THẤY GOAL!**

---

### 6. Bảng tổng hợp các bước

| Step | T | Current State | Action | h | Δh | P(accept) | Accepted? | Reached Count |
|------|---|---------------|--------|---|-----|-----------|-----------|---------------|
| 0 | 100.0 | S | Start | 4 | - | - | - | 1 |
| 1 | 100.0 | S_D | D | 5 | +1 | 0.99 | ✓ | 2 |
| 2 | 95.0 | S_DL | L | 6 | +1 | 0.99 | ✓ | 3 |
| 3 | 90.25 | S_DLU | U | 5 | -1 | 1.0 | ✓ | 4 |
| 4 | 85.74 | S_DLUR | R | 4 | -1 | 1.0 | ✓ | 5 |
| 5 | 81.45 | ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| N | ~8.0 | Near Goal | R | 0 | -1 | 1.0 | ✓ | GOAL! |

---

### 7. Cây tìm kiếm dạng text

```
                                S (h=4, T=100)
                                │
                    ┌───────────┼───────────┬───────────┐
                    │           │           │           │
                   U(5)       D(5)        L(5)        R(3)
                    │           │           │           │
                  ...    S_D(h=5)        ...         ...
                            │
                    ┌───────┼───────┐
                    │       │       │
                   U(4)   L(6)     R(6)
                    │       │       │
                  ...   S_DL(h=6)  ...
                            │
                    ┌───────┼───────┐
                    │       │       │
                   U(5)   R(5)     ...
                    │
                S_DLU(h=5)
                    │
                    ├── R → S_DLUR(h=4)
                    │       │
                    │       ├── ... (tiếp tục)
                    │       │
                    │       └── R → GOAL(h=0) ✓
                    │
                    └── ...

[SA không duy trì cây đầy đủ như BFS/DFS, chỉ giữ current state]
```

---

### 8. Đường đi từ S đến G

```
Step 0:  ┌───┬───┬───┐   h=4
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 5 │ 0 │ 6 │
         ├───┼───┼───┤
         │ 4 │ 7 │ 8 │
         └───┴───┴───┘
              │
              ↓ (D)
Step 1:  ┌───┬───┬───┐   h=5
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 5 │ 7 │ 6 │
         ├───┼───┼───┤
         │ 4 │ 0 │ 8 │
         └───┴───┴───┘
              │
              ↓ (L)
Step 2:  ┌───┬───┬───┐   h=6
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 5 │ 7 │ 6 │
         ├───┼───┼───┤
         │ 0 │ 4 │ 8 │
         └───┴───┴───┘
              │
              ↓ (U)
Step 3:  ┌───┬───┬───┐   h=5
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 0 │ 7 │ 6 │
         ├───┼───┼───┤
         │ 5 │ 4 │ 8 │
         └───┴───┴───┘
              │
              ↓ (R)
Step 4:  ┌───┬───┬───┐   h=4
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 7 │ 0 │ 6 │
         ├───┼───┼───┤
         │ 5 │ 4 │ 8 │
         └───┴───┴───┘
              │
            ... (nhiều bước ngẫu nhiên)
              │
Step N:  ┌───┬───┬───┐   h=1
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 4 │ 5 │ 6 │
         ├───┼───┼───┤
         │ 7 │ 0 │ 8 │
         └───┴───┴───┘
              │
              ↓ (R)
GOAL:    ┌───┬───┬───┐   h=0 ✓
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 4 │ 5 │ 6 │
         ├───┼───┼───┤
         │ 7 │ 8 │ 0 │
         └───┴───┴───┘
```

---

### 9. Tổng số bước

- **Số bước thực tế:** Phụ thuộc vào random seed
- **Trung bình:** 50-200 bước (với config tốt)
- **Không đảm bảo tối ưu**

---

### 10. Nhận xét về thuật toán

**Ưu điểm:**
- Có khả năng thoát khỏi local optimum nhờ chấp nhận bước đi xấu
- Đơn giản, dễ implement
- Không cần lưu nhiều bộ nhớ (chỉ giữ current state)
- Phù hợp cho bài toán tối ưu hóa combinatorial

**Nhược điểm:**
- Không đảm bảo tìm thấy goal
- Kết quả ngẫu nhiên, phụ thuộc vào seed và các lựa chọn ngẫu nhiên
- Cần điều chỉnh T₀, α, T_min phù hợp
- Không phù hợp cho 8-puzzle chuẩn vì đây là bài toán xác định

**Kết luận:** 
- Simulated Annealing **KHÔNG PHẢI thuật toán tối ưu** cho 8-puzzle chuẩn
- 8-puzzle chuẩn nên dùng **A*** hoặc **BFS** để đảm bảo tìm được đường đi tối ưu
- SA phù hợp hơn cho các bài toán tối ưu hóa với không gian tìm kiếm lớn và nhiều local optimum

---

## THUẬT TOÁN 2: AND-OR SEARCH

### 1. Định nghĩa thuật toán

**AND-OR Search** là thuật toán tìm kiếm trong không gian trạng thái có tính bất định (nondeterministic).

**Các loại node:**
- **OR node:** Agent chọn hành động, kết quả có thể là nhiều trạng thái khác nhau
- **AND node:** Tất cả các kết quả có thể xảy ra đều phải được xử lý

**Conditional Plan:** Kế hoạch có điều kiện dựa trên kết quả quan sát được.

### 2. Tại sao AND-OR Search không cần thiết cho 8-puzzle chuẩn?

**Lý do:** 8-puzzle chuẩn là môi trường **xác định (deterministic)**:
- Mỗi hành động chỉ dẫn đến MỘT kết quả duy nhất
- Không có yếu tố ngẫu nhiên
- Agent quan sát đầy đủ trạng thái

**Kết luận:** Với 8-puzzle chuẩn, AND-OR Search **tương đương với BFS/DFS** vì không có node AND.

### 3. Mô phỏng phiên bản 8-puzzle có tính bất định

**Giả sử:** Khi di chuyển ô trống, có 10% xác suất ô trống "trượt" thêm một bước.

**Ví dụ:** Từ trạng thái S, thực hiện R (Right)

```
S:              Kết quả 1 (90%):    Kết quả 2 (10%):
┌───┬───┬───┐   ┌───┬───┬───┐       ┌───┬───┬───┐
│ 1 │ 2 │ 3 │   │ 1 │ 2 │ 3 │       │ 1 │ 2 │ 3 │
├───┼───┼───┤   ├───┼───┼───┤       ├───┼───┼───┤
│ 5 │ 0 │ 6 │ → │ 5 │ 6 │ 0 │       │ 0 │ 5 │ 6 │  (trượt)
├───┼───┼───┤   ├───┼───┼───┤       ├───┼───┼───┤
│ 4 │ 7 │ 8 │   │ 4 │ 7 │ 8 │       │ 4 │ 7 │ 8 │
└───┴───┴───┘   └───┴───┴───┘       └───┴───┴───┘
    h=4              h=3                 h=5
```

### 4. Cây AND-OR Search

```
                                    [OR] S
                                    h=4
                                      │
                                 Action: R
                                      │
                              ┌───────┴───────┐
                              │               │
                         [AND] Node      (phải xử lý cả 2)
                              │
                    ┌─────────┴─────────┐
                    │                   │
              P=0.9: R_success    P=0.1: R_slip
                    │                   │
               ┌────┴────┐         ┌────┴────┐
               │         │         │         │
            [OR]      [OR]      [OR]      [OR]
            h=3       ...       h=5       ...
               │                   │
          Tiếp tục            Phục hồi
```

### 5. Conditional Plan

```
PLAN để đạt G từ S:

IF tại S:
    TRY R:
        IF kết quả là S1 (bình thường, 90%):
            CONTINUE với plan từ S1
        IF kết quả là S2 (trượt, 10%):
            TRY L để quay lại S
            RETRY R

IF tại S1:
    TRY D:
        IF kết quả là S1a (bình thường):
            CONTINUE...
        IF kết quả là S1b (trượt):
            RECOVER...

... (tiếp tục cho đến khi đạt G)
```

### 6. Bảng chạy từng bước

| Step | Node | Type | State | Action | Results | Plan |
|------|------|------|-------|--------|---------|------|
| 0 | S | OR | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | R | S1(90%), S2(10%) | Try R |
| 1 | R_result | AND | - | - | S1, S2 | Handle both |
| 2 | S1 | OR | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 6 │ 0 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | D | S1a(90%), S1b(10%) | Continue |
| 3 | S2 | OR | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 0 │ 5 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | R | S2a(90%), S2b(10%) | Recover |

### 7. Nhận xét

**Đối với 8-puzzle:**
- 8-puzzle chuẩn là môi trường xác định → **không cần AND-OR Search**
- Nếu có yếu tố bất định → AND-OR Search phù hợp
- Conditional plan phức tạp hơn nhiều so với deterministic plan

**Ưu điểm:**
- Xử lý được môi trường bất định
- Tìm được kế hoạch an toàn (nếu tồn tại)

**Nhược điểm:**
- Phức tạp, khó implement
- Không gian tìm kiếm lớn (phải xét tất cả nhánh AND)
- Không cần thiết cho môi trường xác định

---

## THUẬT TOÁN 3: SEARCHING WITH NO OBSERVATION

### 1. Định nghĩa

**Searching with no observation** áp dụng khi agent không biết trạng thái hiện tại. Agent chỉ biết tập các trạng thái có thể xảy ra - gọi là **belief state**.

### 2. Belief State

**Belief state** = tập hợp tất cả trạng thái mà agent có thể đang ở đó.

### 3. Ví dụ minh họa

**Giả sử:** Agent bị bịt mắt, không nhìn thấy bảng. Agent chỉ biết ban đầu ô trống có thể ở một trong 3 vị trí.

**Belief state ban đầu b₀:**

```
b₀ = {S₁, S₂, S₃}

S₁:              S₂:              S₃:
┌───┬───┬───┐   ┌───┬───┬───┐   ┌───┬───┬───┐
│ 1 │ 2 │ 3 │   │ 1 │ 2 │ 3 │   │ 1 │ 2 │ 3 │
├───┼───┼───┤   ├───┼───┼───┤   ├───┼───┼───┤
│ 5 │ 0 │ 6 │   │ 0 │ 5 │ 6 │   │ 5 │ 6 │ 0 │
├───┼───┼───┤   ├───┼───┼───┤   ├───┼───┼───┤
│ 4 │ 7 │ 8 │   │ 4 │ 7 │ 8 │   │ 4 │ 7 │ 8 │
└───┴───┴───┘   └───┴───┴───┘   └───┴───┴───┘
  ô 0 ở (1,1)    ô 0 ở (1,0)     ô 0 ở (1,2)
```

### 4. Cập nhật belief state sau hành động

**Thực hiện hành động R (Right):**

| Trạng thái trong b₀ | R hợp lệ? | Kết quả |
|---------------------|-----------|---------|
| S₁ (ô 0 ở (1,1)) | ✓ | S₁' (ô 0 ở (1,2)) |
| S₂ (ô 0 ở (1,0)) | ✓ | S₂' (ô 0 ở (1,1)) |
| S₃ (ô 0 ở (1,2)) | ✗ | S₃ (không đổi) |

**Belief state mới b₁ = {S₁', S₂', S₃}**

```
b₁:

S₁':             S₂':             S₃:
┌───┬───┬───┐   ┌───┬───┬───┐   ┌───┬───┬───┐
│ 1 │ 2 │ 3 │   │ 1 │ 2 │ 3 │   │ 1 │ 2 │ 3 │
├───┼───┼───┤   ├───┼───┼───┤   ├───┼───┼───┤
│ 5 │ 6 │ 0 │   │ 5 │ 0 │ 6 │   │ 5 │ 6 │ 0 │
├───┼───┼───┤   ├───┼───┼───┤   ├───┼───┼───┤
│ 4 │ 7 │ 8 │   │ 4 │ 7 │ 8 │   │ 4 │ 7 │ 8 │
└───┴───┴───┘   └───┴───┴───┘   └───┴───┴───┘
```

### 5. Bảng chạy từng bước

| Step | Belief State | |b| | Action | New Belief State | Ghi chú |
|------|--------------|-----|--------|-------------------|---------|
| 0 | {S₁, S₂, S₃} | 3 | - | - | Khởi tạo |
| 1 | {S₁, S₂, S₃} | 3 | R | {S₁', S₂', S₃} | R không hợp lệ với S₃ |
| 2 | {S₁', S₂', S₃} | 3 | D | {S₁'', S₂'', S₃'} | D hợp lệ với tất cả |
| 3 | {S₁'', S₂'', S₃'} | 3 | L | {S₁''', S₂''', S₃''} | Tiếp tục |
| ... | ... | ... | ... | ... | ... |

### 6. Tại sao khó hơn 8-puzzle thường?

1. **Không gian tìm kiếm lớn hơn:** Phải tìm trong không gian belief state (có thể lên đến 2^(9!) trạng thái)
2. **Không có heuristic tốt:** Khó ước lượng khoảng cách từ belief state đến goal
3. **Hành động có thể không áp dụng được cho tất cả trạng thái**
4. **Cần chuỗi hành động hoạt động cho TẤT CẢ trạng thái trong belief state**

### 7. Nhận xét

**Ưu điểm:**
- Giải quyết được bài toán không có thông tin

**Nhược điểm:**
- Rất phức tạp
- Không gian tìm kiếm khổng lồ
- Không có heuristic hiệu quả
- **Không phù hợp cho 8-puzzle thực tế** vì ta luôn quan sát được trạng thái

---

## THUẬT TOÁN 4: PARTIALLY OBSERVABLE SEARCH

### 1. Định nghĩa

**Partially observable search** áp dụng khi agent quan sát được một phần trạng thái.

### 2. Mô hình hóa

**Giả sử:** Agent chỉ nhìn thấy ô trống và 4 ô xung quanh nó.

**Ví dụ quan sát:**
```
Toàn bộ bảng:         Agent nhìn thấy:
┌───┬───┬───┐        ┌───┬───┬───┐
│ 1 │ 2 │ 3 │        │ ? │ ? │ ? │
├───┼───┼───┤        ├───┼───┼───┤
│ 5 │ 0 │ 6 │   →    │ 5 │ 0 │ 6 │  ← Thấy ô trống và xung quanh
├───┼───┼───┤        ├───┼───┼───┤
│ 4 │ 7 │ 8 │        │ ? │ ? │ ? │
└───┴───┴───┘        └───┴───┴───┘
```

### 3. Bảng cập nhật belief state

| Step | Belief State | Observation | Action | New Belief State |
|------|--------------|-------------|--------|------------------|
| 0 | {tất cả states với 0 ở (1,1)} | 0 ở (1,1), thấy 5,6,2,7 | - | b₀ |
| 1 | b₀ | - | R | b₁ = {states sau R từ b₀} |
| 2 | b₁ | 0 ở (1,2), thấy 6,3 | - | b₂ (thu hẹp hơn) |
| 3 | b₂ | - | D | b₃ |

### 4. Nhận xét

**Ưu điểm:**
- Phù hợp với robot thực tế (sensor hạn chế)
- Kết hợp quan sát để thu hẹp belief state

**Nhược điểm:**
- Vẫn phức tạp
- Phụ thuộc vào chất lượng quan sát
- **Không cần thiết cho 8-puzzle chuẩn** vì ta nhìn thấy toàn bộ bảng

---

## THUẬT TOÁN 5: ONLINE SEARCH

### 1. Định nghĩa

**Online search** áp dụng khi agent không biết trước không gian trạng thái. Agent phải khám phá từng bước.

### 2. Mô phỏng từng bước

| Step | Current State | Possible Actions | Chosen Action | New State | Visited | Backtrack? |
|------|---------------|------------------|---------------|-----------|---------|------------|
| 0 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | {U,D,L,R} | R | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 6 │ 0 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | {S} | No |
| 1 | S_R | {L,D} | D | S_RD | {S, S_R} | No |
| 2 | S_RD | {U,L} | L | S_RDL | {S, S_R, S_RD} | No |
| ... | ... | ... | ... | ... | ... | ... |
| N | GOAL | - | - | - | All visited | No |

### 3. Nhận xét

**Ưu điểm:**
- Không cần biết trước không gian trạng thái
- Phù hợp với môi trường mới, chưa khám phá

**Nhược điểm:**
- Có thể đi đường vòng
- Không tối ưu
- **Không cần thiết cho 8-puzzle** vì ta đã biết không gian trạng thái

---

## THUẬT TOÁN 6-11: CSP VÀ CÁC KỸ THUẬT LIÊN QUAN

### 6. CSP - Constraint Satisfaction Problem

#### Mô hình hóa 8-puzzle thành CSP

**Lưu ý quan trọng:** 8-puzzle chuẩn **KHÔNG PHẢI CSP tĩnh** vì:
- Trạng thái thay đổi theo thời gian
- Cần tìm chuỗi hành động, không phải gán giá trị tĩnh

Tuy nhiên, ta có thể mô hình hóa **Goal State** như một CSP:

**Variables:** X₁, X₂, ..., X₉ (9 ô trên bảng)

**Domains:** D₁ = D₂ = ... = D₉ = {0, 1, 2, 3, 4, 5, 6, 7, 8}

**Constraints:**
1. **AllDifferent:** X₁ ≠ X₂ ≠ ... ≠ X₉
2. **Position:** Mỗi ô phải ở vị trí đúng

#### Đồ thị ràng buộc CSP

```
    X₁ ───── X₂ ───── X₃
     │        │        │
     │        │        │
    X₄ ───── X₅ ───── X₆
     │        │        │
     │        │        │
    X₇ ───── X₈ ───── X₉

Mỗi node = một biến (ô)
Mỗi cạnh = ràng buộc AllDifferent
```

---

### 7. CONSTRAINT PROPAGATION

**Constraint propagation** giảm miền giá trị bằng cách lan truyền ràng buộc.

**Ví dụ:** Khi gán X₁ = 1

| Biến | Domain trước | Domain sau |
|------|--------------|------------|
| X₁ | {0,1,2,3,4,5,6,7,8} | {1} |
| X₂ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} |
| X₃ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} |
| ... | ... | ... |

---

### 8. PATH CONSISTENCY

**Path consistency** kiểm tra tính nhất quán đường đi giữa 3 biến.

**Công thức:** (Xi, Xj) path consistent với Xk nếu với mọi (a,b) hợp lệ, tồn tại c cho Xk.

---

### 9. GLOBAL CONSTRAINTS

**AllDifferent(X₁, ..., X₉)** = Tất cả 9 biến có giá trị khác nhau.

---

### 10. BACKTRACKING SEARCH

| Step | Variable | Value | Assignment | Consistent? |
|------|----------|-------|------------|-------------|
| 1 | X₁ | 1 | {X₁=1} | ✓ |
| 2 | X₂ | 2 | {X₁=1, X₂=2} | ✓ |
| 3 | X₃ | 3 | {X₁=1, X₂=2, X₃=3} | ✓ |
| 4 | X₄ | 4 | {..., X₄=4} | ✓ |
| 5 | X₅ | 5 | {..., X₅=5} | ✓ |
| 6 | X₆ | 6 | {..., X₆=6} | ✓ |
| 7 | X₇ | 7 | {..., X₇=7} | ✓ |
| 8 | X₈ | 8 | {..., X₈=8} | ✓ |
| 9 | X₉ | 0 | {..., X₉=0} | ✓ → GOAL! |

---

### 11. MIN-CONFLICTS ALGORITHM

| Step | Assignment | Conflicts | Variable | New Value | Result |
|------|------------|-----------|----------|-----------|--------|
| 0 | S | 4 | - | - | Start |
| 1 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 0 │ 5 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | 3 | X₅ | 5 | Better |
| ... | ... | ... | ... | ... | ... |
| N | GOAL | 0 | - | - | Found! |

---

## THUẬT TOÁN 12-14: GAME PLAYING ALGORITHMS

### 12. MINIMAX

#### Tại sao 8-puzzle không phải game 2 người?

8-puzzle là bài toán 1 người giải puzzle. Không có đối thủ.

#### Mô phỏng phiên bản game

**Giả sử tạo phiên bản 8-puzzle game:**
- **MAX:** Người giải, muốn giảm h(n)
- **MIN:** Đối thủ, muốn tăng h(n)

#### Cây Game (độ sâu 2)

```
                                    [MAX] S
                                    h=4
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                   R                 D                 L
                  h=3               h=5               h=5
                    │                 │                 │
                  [MIN]            [MIN]            [MIN]
                 /     \          /     \          /     \
              h=3      h=4     h=5      h=6     h=5      h=7
               │        │       │        │       │        │
             MAX      MAX     MAX      MAX     MAX      MAX
```

#### Chạy Minimax

| Node | Type | h | Children | Best | Value |
|------|------|---|----------|------|-------|
| Leaf R₁ | MAX | 3 | - | - | 3 |
| Leaf R₂ | MAX | 4 | - | - | 4 |
| MIN_R | MIN | - | {3, 4} | min | 3 |
| Leaf D₁ | MAX | 5 | - | - | 5 |
| Leaf D₂ | MAX | 6 | - | - | 6 |
| MIN_D | MIN | - | {5, 6} | min | 5 |
| Leaf L₁ | MAX | 5 | - | - | 5 |
| Leaf L₂ | MAX | 7 | - | - | 7 |
| MIN_L | MIN | - | {5, 7} | min | 5 |
| **ROOT** | **MAX** | **4** | **{3, 5, 5}** | **max** | **3** |

**MAX chọn R** (value = 3)

---

### 13. ALPHA-BETA PRUNING

#### Chạy Alpha-Beta trên cùng cây

```
                                    [MAX] S
                                    α=-∞, β=+∞
                                      │
                                      ↓ R
                                    [MIN]
                                    α=-∞, β=+∞
                                    /         \
                                  h=3         h=4
                                  ✓           PRUNED!
                                  │           (β=3, không cần xét)
                                  ↓
                              UPDATE α=3
```

**Cắt nhánh:** Khi MIN thấy con đầu tiên = 3, MIN sẽ chọn ≤ 3. MAX đã có α = 3.

#### So sánh

| Metric | Minimax | Alpha-Beta |
|--------|---------|------------|
| Nodes visited | 7 | 4 |
| Nodes pruned | 0 | 3 |

---

### 14. EXPECTIMAX

#### Mô phỏng 8-puzzle với yếu tố ngẫu nhiên

**Giả sử:** Sau khi MAX chọn hành động, môi trường có 20% xác suất làm sai lệch.

#### Cây Expectimax

```
                                    [MAX] S
                                      │
                                      ↓ R
                                    [CHANCE]
                                    /         \
                              P=0.8           P=0.2
                                │               │
                              h=3             h=5
                                │               │
                                └───────┬───────┘
                                        │
                              E[h] = 0.8×3 + 0.2×5 = 3.4
```

#### Tính Expected Value

| Action | P(success) | h(success) | P(fail) | h(fail) | E[h] |
|--------|------------|------------|---------|---------|------|
| R | 0.8 | 3 | 0.2 | 5 | 3.4 |
| D | 0.8 | 5 | 0.2 | 7 | 5.4 |
| L | 0.8 | 5 | 0.2 | 8 | 5.6 |

**MAX chọn R** vì E[h] thấp nhất = 3.4

---

## BẢNG SO SÁNH TẤT CẢ THUẬT TOÁN

| Thuật toán | Phù hợp 8-puzzle? | Quan sát đầy đủ? | Dùng heuristic? | Dùng xác suất? | Dùng đối thủ? | Ưu điểm | Nhược điểm |
|------------|-------------------|------------------|-----------------|----------------|---------------|---------|------------|
| Simulated Annealing | Không tối ưu | Có | Có | Có | Không | Thoát local optimum | Kết quả ngẫu nhiên |
| AND-OR Search | Không cần thiết | Có | Không | Không | Không | Xử lý bất định | Phức tạp |
| No Observation | Không phù hợp | Không | Không | Không | Không | Xử lý không quan sát | Rất khó |
| Partially Observable | Không phù hợp | Một phần | Không | Không | Không | Thực tế cho robot | Phức tạp |
| Online Search | Không cần thiết | Có | Không | Không | Không | Không cần biết trước | Không tối ưu |
| CSP | Không phù hợp | Có | Không | Không | Không | Giải bài toán gán | Không tìm đường đi |
| Constraint Propagation | Không phù hợp | Có | Không | Không | Không | Giảm miền giá trị | Không giải được alone |
| Path Consistency | Không phù hợp | Có | Không | Không | Không | Kiểm tra chặt hơn | Tốn chi phí |
| Global Constraints | Không phù hợp | Có | Không | Không | Không | Ràng buộc mạnh | Phức tạp |
| Backtracking | Không phù hợp | Có | Không | Không | Không | Đảm bảo tìm thấy | Chậm |
| Min-Conflicts | Không phù hợp | Có | Không | Có | Không | Nhanh cho CSP lớn | Không đảm bảo |
| Minimax | Không phù hợp | Có | Có | Không | Có | Tối ưu cho game | Cần đối thủ |
| Alpha-Beta | Không phù hợp | Có | Có | Không | Có | Cắt nhánh hiệu quả | Vẫn cần đối thủ |
| Expectimax | Không phù hợp | Có | Có | Có | Có | Xử lý ngẫu nhiên | Phức tạp |

---

## CÁCH GHI BÀI THI

1. **Kiểm tra solvable:** Tính số nghịch thế, so sánh chẵn lẻ
2. **Vẽ ma trận 3x3:** Luôn trình bày trạng thái bằng bảng có khung
3. **Ghi rõ heuristic:** h(n) = số ô sai vị trí hoặc Manhattan
4. **Bảng từng bước:** Step, State (ma trận), Action, Frontier (ma trận), Reached, h, g, f
5. **Cây tìm kiếm:** Vẽ dạng text, ghi rõ node, action, cost
6. **Đường đi:** Liệt kê từ Start đến Goal với ma trận đầy đủ
7. **Nhận xét:** Phù hợp hay không, tại sao

---

## NHỮNG LỖI DỄ SAI

1. **Quên kiểm tra solvable:** Bài có thể không giải được
2. **Sai tính nghịch thế:** Nhớ bỏ qua số 0
3. **Sai heuristic:** Nhớ không tính ô trống (số 0)
4. **Sai hành động:** Ô trống di chuyển, không phải ô số
5. **Quên ghi Frontier/Reached:** Cần track các node đã thăm
6. **Sai cây AND-OR:** Nhớ AND node phải xử lý TẤT CẢ nhánh
7. **Sai Minimax:** MAX maximize, MIN minimize
8. **Sai Alpha-Beta:** Cắt khi β ≤ α
9. **Sai Expectimax:** Chance node dùng xác suất, không phải min/max
10. **Không vẽ ma trận:** Luôn vẽ bảng 3x3 có khung rõ ràng

---

## KẾT LUẬN

**Thuật toán phù hợp nhất cho 8-puzzle chuẩn:**
1. **A*** - Tối ưu, dùng heuristic Manhattan
2. **IDA*** - Tiết kiệm bộ nhớ
3. **BFS** - Tối ưu khi chi phí đều

**Thuật toán KHÔNG phù hợp:**
- AND-OR Search (không có bất định)
- No/Partial Observation (quan sát đầy đủ)
- CSP-based (không phải bài toán gán tĩnh)
- Game algorithms (không có đối thủ)

---

*Tài liệu được tạo để hỗ trợ học tập môn Trí tuệ nhân tạo*
