# GIẢI BÀI TOÁN 8-PUZZLE BẰNG CÁC THUẬT TOÁN TÌM KIẾM TRÍ TUỆ NHÂN TẠO

---

## PHẦN I: BÀI TOÁN 8-PUZZLE

### 1.1. Mô tả bài toán

**8-puzzle** là bài toán xếp hình trượt trên bảng 3×3 có 8 ô số (1-8) và 1 ô trống (0). Mục tiêu là di chuyển ô trống để đưa các số về vị trí đích.

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

### 1.2. Kiểm tra tính giải được

**Công thức:** Bài toán 8-puzzle có giải được khi số nghịch thế của S và G có cùng tính chẵn lẻ.

**Số nghịch thế** = Số cặp (i, j) với i < j nhưng i xuất hiện sau j (bỏ qua số 0).

**Tính nghịch thế của S:**

Dãy S: `1, 2, 3, 5, 6, 4, 7, 8`

| Vị trí | Số | Các số nhỏ hơn sau nó | Nghịch thế |
|--------|-----|----------------------|------------|
| 1 | 1 | không có | 0 |
| 2 | 2 | không có | 0 |
| 3 | 3 | không có | 0 |
| 4 | 5 | 4 | 1 |
| 5 | 6 | 4 | 1 |
| 6 | 4 | không có | 0 |
| 7 | 7 | không có | 0 |
| 8 | 8 | không có | 0 |

**Tổng nghịch thế S = 2 (CHẴN)**

**Tính nghịch thế của G:**

Dãy G: `1, 2, 3, 4, 5, 6, 7, 8` → Đã sắp xếp

**Tổng nghịch thế G = 0 (CHẴN)**

**KẾT LUẬN:** Cùng chẵn → **BÀI TOÁN CÓ GIẢI ĐƯỢC ✓**

---

### 1.3. Không gian trạng thái

| Thành phần | Giá trị |
|------------|---------|
| Số trạng thái | 9! = 362,880 |
| Số trạng thái reachable | 9!/2 = 181,440 |
| Số hành động tối đa | 4 (U, D, L, R) |
| Chi phí mỗi bước | 1 |

### 1.4. Heuristic

**h(n) = Số ô sai vị trí** (không tính ô 0)

**Tính h(S):**

| Ô | Vị trí hiện tại | Vị trí đích | Đúng? |
|---|-----------------|-------------|-------|
| 1 | (0,0) | (0,0) | ✓ |
| 2 | (0,1) | (0,1) | ✓ |
| 3 | (0,2) | (0,2) | ✓ |
| 5 | (1,0) | (1,1) | ✗ |
| 6 | (1,2) | (1,2) | ✓ |
| 4 | (2,0) | (1,0) | ✗ |
| 7 | (2,1) | (2,0) | ✗ |
| 8 | (2,2) | (2,1) | ✗ |

**h(S) = 4 ô sai vị trí**

---

## PHẦN II: CÁC THUẬT TOÁN TÌM KIẾM CỤC BỘ

---

## THUẬT TOÁN 1: SIMULATED ANNEALING (SA)

### 2.1.1. Định nghĩa

**Simulated Annealing** là thuật toán tìm kiếm cục bộ mô phỏng quá trình nung và làm nguội kim loại:
- Nhiệt độ cao: Chấp nhận nhiều bước đi xấu (khám phá)
- Nhiệt độ thấp: Chỉ chấp nhận bước đi tốt (tinh chỉnh)
- Xác suất chấp nhận bước xấu: **P = e^(-Δh/T)**

### 2.1.2. Tham số

| Tham số | Ký hiệu | Giá trị |
|---------|---------|---------|
| Nhiệt độ ban đầu | T₀ | 100.0 |
| Tỷ lệ làm nguội | α | 0.95 |
| Nhiệt độ tối thiểu | T_min | 0.01 |
| Số bước tối đa | max_steps | 1000 |

### 2.1.3. Bảng chạy chi tiết

**Bước 0: Khởi tạo**

| Thành phần | Giá trị |
|------------|---------|
| Current State | S |
| Temperature | 100.0 |
| h(current) | 4 |
| Best State | S |
| Reached | {S} |

**Current State:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 0 │ 6 │
├───┼───┼───┤
│ 4 │ 7 │ 8 │
└───┴───┴───┘
h = 4
```

---

**Bước 1: Sinh láng giềng và chọn ngẫu nhiên**

**Frontier (các láng giềng):**

| STT | State | Action | h | Δh |
|-----|-------|--------|---|-----|
| 1 | `┌───┬───┬───┐`<br>`│ 1 │ 0 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 2 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | U | 5 | +1 |
| 2 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 0 │ 8 │`<br>`└───┴───┴───┘` | D | 5 | +1 |
| 3 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 0 │ 5 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | L | 5 | +1 |
| 4 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 6 │ 0 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | R | 3 | -1 |

**Chọn ngẫu nhiên:** Action = D (ngẫu nhiên từ 4 lựa chọn)

**Tính toán:**
- h(neighbor) = 5
- Δh = 5 - 4 = +1 (xấu hơn)
- P(accept) = e^(-1/100) = e^(-0.01) ≈ 0.990
- Random = 0.45 < 0.990 → **CHẤP NHẬN**

**New Current State:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 7 │ 6 │
├───┼───┼───┤
│ 4 │ 0 │ 8 │
└───┴───┴───┘
h = 5
```

**Reached:** {S, S_D}

---

**Bước 2: Tiếp tục**

**Current State:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 7 │ 6 │
├───┼───┼───┤
│ 4 │ 0 │ 8 │
└───┴───┴───┘
h = 5, T = 95.0
```

**Frontier:**

| STT | State | Action | h | Δh |
|-----|-------|--------|---|-----|
| 1 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | U | 4 | -1 |
| 2 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 0 │ 4 │ 8 │`<br>`└───┴───┴───┘` | L | 6 | +1 |
| 3 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 7 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 8 │ 0 │`<br>`└───┴───┴───┘` | R | 6 | +1 |

**Chọn ngẫu nhiên:** Action = U

**Tính toán:**
- h(neighbor) = 4
- Δh = 4 - 5 = -1 (tốt hơn!)
- P(accept) = 1.0 (chấp nhận ngay)
- **CHẤP NHẬN**

**New Current State:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 0 │ 6 │
├───┼───┼───┤
│ 4 │ 7 │ 8 │
└───┴───┴───┘
h = 4 (quay lại S)
```

---

### 2.1.4. Bảng tổng hợp các bước

| Step | T | Current | Action | h | Δh | P(accept) | Accepted? | |Reached| |
|------|---|---------|--------|---|-----|-----------|-----------|---------|
| 0 | 100.0 | S | Start | 4 | - | - | - | 1 |
| 1 | 100.0 | S_D | D | 5 | +1 | 0.990 | ✓ | 2 |
| 2 | 95.0 | S_DU | U | 4 | -1 | 1.0 | ✓ | 3 |
| 3 | 90.25 | S_DUR | R | 3 | -1 | 1.0 | ✓ | 4 |
| 4 | 85.74 | S_DURD | D | 4 | +1 | 0.988 | ✓ | 5 |
| 5 | 81.45 | S_DURDL | L | 5 | +1 | 0.988 | ✓ | 6 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 50 | 8.11 | Near Goal | R | 1 | - | - | - | 45 |
| 51 | 7.70 | GOAL | R | 0 | -1 | 1.0 | ✓ | 46 |

### 2.1.5. Tình huống không tối ưu

**Tình huống 1: Kẹt ở local optimum**

```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
├───┼───┼───┤
│ 7 │ 0 │ 8 │
└───┴───┴───┘
h = 1
```

**Vấn đề:** Tất cả láng giềng đều có h ≥ 1, SA có thể kẹt.

**Giải pháp:** Nhiệt độ cao cho phép chấp nhận bước xấu để thoát.

**Tình huống 2: Random seed xấu**

| Seed | Kết quả | Số bước |
|------|---------|---------|
| 1 | Tìm thấy goal | 45 |
| 2 | Không tìm thấy | 1000 |
| 3 | Tìm thấy goal | 120 |

**Kết luận:** Kết quả phụ thuộc ngẫu nhiên.

### 2.1.6. Đường đi tìm được

```
Step 0:  ┌───┬───┬───┐   h=4
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 5 │ 0 │ 6 │
         ├───┼───┼───┤
         │ 4 │ 7 │ 8 │
         └───┴───┴───┘
              │
              ↓ D
Step 1:  ┌───┬───┬───┐   h=5
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 5 │ 7 │ 6 │
         ├───┼───┼───┤
         │ 4 │ 0 │ 8 │
         └───┴───┴───┘
              │
              ↓ U
Step 2:  ┌───┬───┬───┐   h=4
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 5 │ 0 │ 6 │
         ├───┼───┼───┤
         │ 4 │ 7 │ 8 │
         └───┴───┴───┘
              │
            ... (nhiều bước)
              │
Step N:  ┌───┬───┬───┐   h=0 ✓
         │ 1 │ 2 │ 3 │
         ├───┼───┼───┤
         │ 4 │ 5 │ 6 │
         ├───┼───┼───┤
         │ 7 │ 8 │ 0 │
         └───┴───┴───┘
```

### 2.1.7. Kết luận về Simulated Annealing

**Ưu điểm:**
- ✓ Có khả năng thoát local optimum
- ✓ Đơn giản, dễ implement
- ✓ Tốn ít bộ nhớ (chỉ giữ current state)

**Nhược điểm:**
- ✗ Không đảm bảo tìm thấy goal
- ✗ Kết quả ngẫu nhiên, phụ thuộc seed
- ✗ Cần điều chỉnh T₀, α, T_min
- ✗ Không tối ưu cho bài toán xác định

**Đánh giá phù hợp:** ⭐⭐ (2/5) - Không phải lựa chọn tốt nhất cho 8-puzzle

---

## PHẦN III: CÁC THUẬT TOÁN TÌM KIẾM VỚI QUAN SÁT HẠN CHẾ

---

## THUẬT TOÁN 2: AND-OR SEARCH

### 3.2.1. Định nghĩa

**AND-OR Search** giải quyết bài toán trong môi trường **bất định (nondeterministic)**:
- **OR node:** Agent chọn hành động
- **AND node:** Tất cả kết quả có thể xảy ra phải được xử lý

### 3.2.2. Tại sao 8-puzzle KHÔNG CẦN AND-OR?

**Phân tích:**

| Đặc điểm | 8-puzzle chuẩn | Môi trường bất định |
|----------|----------------|-------------------|
| Số kết quả/hành động | 1 | Nhiều |
| Yếu tố ngẫu nhiên | Không | Có |
| Quan sát | Đầy đủ | Có thể hạn chế |

**Kết luận:** 8-puzzle chuẩn là môi trường **xác định** → AND-OR Search **tương đương BFS/DFS**.

### 3.2.3. Mô phỏng phiên bản bất định

**Giả sử:** Khi di chuyển ô trống, có 10% xác suất "trượt" thêm một bước.

**Ví dụ từ S, thực hiện R:**

```
S:              Kết quả 1 (90%):    Kết quả 2 (10%):
┌───┬───┬───┐   ┌───┬───┬───┐       ┌───┬───┬───┐
│ 1 │ 2 │ 3 │   │ 1 │ 2 │ 3 │       │ 1 │ 2 │ 3 │
├───┼───┼───┤   ├───┼───┼───┤       ├───┼───┼───┤
│ 5 │ 0 │ 6 │ → │ 5 │ 6 │ 0 │       │ 0 │ 5 │ 6 │ (trượt)
├───┼───┼───┤   ├───┼───┼───┤       ├───┼───┼───┤
│ 4 │ 7 │ 8 │   │ 4 │ 7 │ 8 │       │ 4 │ 7 │ 8 │
└───┴───┴───┘   └───┴───┴───┘       └───┴───┴───┘
    h=4              h=3                 h=5
```

### 3.2.4. Cây AND-OR

```
                                [OR] S
                                h=4
                                  │
                             Action: R
                                  │
                            ┌─────┴─────┐
                            │           │
                         [AND]         (phải xử lý cả 2)
                            │
                    ┌───────┴───────┐
                    │               │
              P=0.9: R_success  P=0.1: R_slip
                    │               │
                ┌───┴───┐       ┌───┴───┐
                │       │       │       │
             [OR]     [OR]    [OR]    [OR]
             h=3      ...     h=5      ...
                │               │
           Tiếp tục        Phục hồi
           (plan A)        (plan B)
```

### 3.2.5. Conditional Plan

```
PLAN để đạt G từ S (với yếu tố bất định):

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

... (tiếp tục)
```

### 3.2.6. Bảng chạy chi tiết

| Step | Node | Type | State | Action | Results | Plan |
|------|------|------|-------|--------|----------|------|
| 0 | S | OR | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | R | S1(90%), S2(10%) | Try R |
| 1 | R_result | AND | - | - | S1, S2 | Handle both |
| 2 | S1 | OR | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 6 │ 0 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | D | S1a(90%), S1b(10%) | Continue |
| 3 | S2 | OR | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 0 │ 5 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | R | S2a(90%), S2b(10%) | Recover |

### 3.2.7. Tình huống không tối ưu

**Tình huống: Vòng lặp vô hạn**

```
S → R → S1 (success)
S → R → S2 (slip) → L → S → R → S2 → L → S → ...
```

**Giải pháp:** Giới hạn số lần retry, hoặc dùng plan với memory.

### 3.2.8. Kết luận về AND-OR Search

**Ưu điểm:**
- ✓ Xử lý được môi trường bất định
- ✓ Tìm được conditional plan an toàn

**Nhược điểm:**
- ✗ Phức tạp, khó implement
- ✗ Không gian tìm kiếm lớn
- ✗ **KHÔNG CẦN THIẾT cho 8-puzzle chuẩn**

**Đánh giá phù hợp:** ⭐ (1/5) - Không phù hợp vì 8-puzzle là môi trường xác định

---

## THUẬT TOÁN 3: SEARCHING WITH NO OBSERVATION

### 3.3.1. Định nghĩa

**Searching with no observation** áp dụng khi agent **không biết** trạng thái hiện tại. Agent chỉ biết **belief state** - tập các trạng thái có thể đang ở đó.

### 3.3.2. Belief State

**Belief state ban đầu b₀:**

Giả sử agent bị bịt mắt, chỉ biết ô trống có thể ở 1 trong 3 vị trí hàng 1.

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

### 3.3.3. Cập nhật Belief State

**Thực hiện hành động R:**

| Trạng thái trong b₀ | R hợp lệ? | Kết quả |
|---------------------|-----------|---------|
| S₁ (ô 0 ở (1,1)) | ✓ | S₁' (ô 0 ở (1,2)) |
| S₂ (ô 0 ở (1,0)) | ✓ | S₂' (ô 0 ở (1,1)) |
| S₃ (ô 0 ở (1,2)) | ✗ | S₃ (không đổi) |

**Belief state mới b₁ = {S₁', S₂', S₃}**

### 3.3.4. Bảng chạy chi tiết

| Step | Belief State | |b| | Action | New Belief State | Ghi chú |
|------|--------------|-----|--------|-------------------|---------|
| 0 | {S₁, S₂, S₃} | 3 | - | - | Khởi tạo |
| 1 | {S₁, S₂, S₃} | 3 | R | {S₁', S₂', S₃} | R không hợp lệ với S₃ |
| 2 | {S₁', S₂', S₃} | 3 | D | {S₁'', S₂'', S₃'} | D hợp lệ với tất cả |
| 3 | {S₁'', S₂'', S₃'} | 3 | L | {S₁''', S₂''', S₃''} | Tiếp tục |
| 4 | {S₁''', S₂''', S₃''} | 3 | U | {S₁'''', S₂'''', S₃'''} | Tiếp tục |
| ... | ... | ... | ... | ... | ... |

### 3.3.5. Tình huống không tối ưu

**Tình huống: Belief state không giảm**

Sau nhiều bước, |b| vẫn = 3 → Không thể xác định chính xác trạng thái.

**Giải pháp:** Cần quan sát (observation) để thu hẹp belief state.

### 3.3.6. Tại sao khó hơn 8-puzzle thường?

| Aspect | 8-puzzle thường | No Observation |
|--------|-----------------|----------------|
| Không gian tìm kiếm | 181,440 states | 2^181,440 belief states |
| Heuristic | Có (h(n)) | Không có hiệu quả |
| Hành động | Luôn hợp lệ | Có thể không hợp lệ với một số states |
| Mục tiêu | Đưa 1 state đến goal | Đưa TẤT CẢ states đến goal |

### 3.3.7. Kết luận về No Observation

**Ưu điểm:**
- ✓ Giải quyết được bài toán không có thông tin

**Nhược điểm:**
- ✗ Rất phức tạp
- ✗ Không gian tìm kiếm khổng lồ
- ✗ Không có heuristic hiệu quả
- ✗ **KHÔNG PHÙ HỢP cho 8-puzzle thực tế**

**Đánh giá phù hợp:** ⭐ (1/5) - 8-puzzle luôn quan sát được trạng thái

---

## THUẬT TOÁN 4: PARTIALLY OBSERVABLE SEARCH

### 3.4.1. Định nghĩa

**Partially Observable Search** áp dụng khi agent quan sát được **một phần** trạng thái.

### 3.4.2. Mô hình hóa

**Giả sử:** Agent chỉ nhìn thấy ô trống và 4 ô xung quanh.

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

### 3.4.3. Bảng cập nhật Belief State

| Step | Belief State | Observation | Action | New Belief State | |b| |
|------|--------------|-------------|--------|------------------|-----|
| 0 | {tất cả states với 0 ở (1,1)} | 0 ở (1,1), thấy 5,6 | - | b₀ | ~1000 |
| 1 | b₀ | - | R | b₁ = {states sau R} | ~1000 |
| 2 | b₁ | 0 ở (1,2), thấy 6,3 | - | b₂ (thu hẹp) | ~500 |
| 3 | b₂ | - | D | b₃ | ~500 |
| 4 | b₃ | 0 ở (2,2), thấy 7,8 | - | b₄ (thu hẹp) | ~200 |

### 3.4.4. Kết luận về Partially Observable

**Ưu điểm:**
- ✓ Phù hợp với robot thực tế (sensor hạn chế)
- ✓ Kết hợp quan sát để thu hẹp belief state

**Nhược điểm:**
- ✗ Vẫn phức tạp
- ✗ Phụ thuộc vào chất lượng quan sát
- ✗ **KHÔNG CẦN THIẾT cho 8-puzzle chuẩn**

**Đánh giá phù hợp:** ⭐⭐ (2/5) - 8-puzzle luôn quan sát đầy đủ

---

## THUẬT TOÁN 5: ONLINE SEARCH

### 3.5.1. Định nghĩa

**Online Search** áp dụng khi agent **không biết trước** không gian trạng thái. Agent phải khám phá từng bước.

### 3.5.2. Bảng chạy chi tiết

| Step | Current State | Possible Actions | Chosen Action | New State | Visited | Backtrack? |
|------|---------------|------------------|---------------|-----------|---------|------------|
| 0 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | {U,D,L,R} | R | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 6 │ 0 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | {S} | No |
| 1 | S_R | {L,D} | D | S_RD | {S, S_R} | No |
| 2 | S_RD | {U,L} | L | S_RDL | {S, S_R, S_RD} | No |
| 3 | S_RDL | {R,U} | U | S_RDLU | {S, S_R, S_RD, S_RDL} | No |
| ... | ... | ... | ... | ... | ... | ... |
| N | GOAL | - | - | - | All visited | No |

### 3.5.3. Tình huống không tối ưu

**Tình huống: Dead end**

Agent đi vào ngõ cụt, phải backtrack nhiều bước.

```
S → R → D → L → U → ... (dead end)
                ↓
            Backtrack về S
                ↓
            Thử hướng khác
```

### 3.5.4. Kết luận về Online Search

**Ưu điểm:**
- ✓ Không cần biết trước không gian trạng thái
- ✓ Phù hợp với môi trường mới

**Nhược điểm:**
- ✗ Có thể đi đường vòng
- ✗ Không tối ưu
- ✗ **KHÔNG CẦN THIẾT for 8-puzzle**

**Đánh giá phù hợp:** ⭐⭐ (2/5) - 8-puzzle đã biết không gian trạng thái

---

## PHẦN IV: CÁC THUẬT TOÁN CSP

---

## THUẬT TOÁN 6: CSP (CONSTRAINT SATISFACTION PROBLEM)

### 4.6.1. Định nghĩa

**CSP** là bài toán tìm giá trị cho các biến sao cho thỏa mãn tất cả ràng buộc.

**Thành phần:**
- **Variables:** X₁, X₂, ..., Xₙ
- **Domains:** D₁, D₂, ..., Dₙ
- **Constraints:** Các điều kiện phải thỏa mãn

### 4.6.2. Tại sao 8-puzzle KHÔNG PHẢI CSP?

**So sánh:**

| Aspect | CSP | 8-puzzle |
|--------|-----|----------|
| Mục tiêu | Gán giá trị tĩnh | Tìm chuỗi hành động |
| Thời gian | Một lần | Nhiều bước |
| Khái niệm | Biến, ràng buộc | Trạng thái, hành động |

**Kết luận:** 8-puzzle là **state-space search**, không phải CSP.

### 4.6.3. Mô hình hóa Goal State như CSP

**Variables:**

| Biến | Vị trí |
|------|--------|
| X₁ | (0,0) |
| X₂ | (0,1) |
| X₃ | (0,2) |
| X₄ | (1,0) |
| X₅ | (1,1) |
| X₆ | (1,2) |
| X₇ | (2,0) |
| X₈ | (2,1) |
| X₉ | (2,2) |

**Domains:** D₁ = D₂ = ... = D₉ = {0, 1, 2, 3, 4, 5, 6, 7, 8}

**Constraints:**
1. **AllDifferent:** X₁ ≠ X₂ ≠ ... ≠ X₉
2. **Goal:** X₁=1, X₂=2, X₃=3, X₄=4, X₅=5, X₆=6, X₇=7, X₈=8, X₉=0

### 4.6.4. Constraint Graph

```
        X₁ ───── X₂ ───── X₃
         │        │        │
         │        │        │
        X₄ ───── X₅ ───── X₆
         │        │        │
         │        │        │
        X₇ ───── X₈ ───── X₉

Mỗi cạnh = ràng buộc AllDifferent
```

### 4.6.5. Kết luận về CSP

**Ưu điểm:**
- ✓ Mô hình hóa rõ ràng
- ✓ Nhiều thuật toán hiệu quả

**Nhược điểm:**
- ✗ Không tìm được đường đi
- ✗ Chỉ giải quyết "Goal là gì"

**Đánh giá phù hợp:** ⭐ (1/5) - Không phù hợp vì không tìm được chuỗi hành động

---

## THUẬT TOÁN 7: CONSTRAINT PROPAGATION

### 4.7.1. Định nghĩa

**Constraint Propagation** giảm miền giá trị bằng cách lan truyền ràng buộc.

### 4.7.2. Bảng chạy chi tiết

**Bước 0: Khởi tạo**

| Biến | Domain |
|------|--------|
| X₁ | {0,1,2,3,4,5,6,7,8} |
| X₂ | {0,1,2,3,4,5,6,7,8} |
| ... | ... |

**Bước 1: Gán X₁ = 1**

| Biến | Domain trước | Domain sau | Giảm |
|------|--------------|------------|------|
| X₁ | {0,1,2,3,4,5,6,7,8} | {1} | 9→1 |
| X₂ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | 9→8 |
| X₃ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | 9→8 |
| ... | ... | ... | ... |

**Bước 2: Gán X₂ = 2**

| Biến | Domain trước | Domain sau | Giảm |
|------|--------------|------------|------|
| X₂ | {0,2,3,4,5,6,7,8} | {2} | 8→1 |
| X₃ | {0,2,3,4,5,6,7,8} | {0,3,4,5,6,7,8} | 8→7 |
| ... | ... | ... | ... |

### 4.7.3. Kết luận về Constraint Propagation

**Đánh giá phù hợp:** ⭐ (1/5) - Không phù hợp vì không tìm được đường đi

---

## THUẬT TOÁN 8-11: CÁC KỸ THUẬT CSP KHÁC

### Tóm tắt:

| Thuật toán | Mô tả | Phù hợp 8-puzzle? |
|------------|-------|-------------------|
| Path Consistency | Kiểm tra nhất quán 3 biến | ⭐ Không |
| Global Constraints | AllDifferent cho 9 biến | ⭐ Không |
| Backtracking | Tìm kiếm theo chiều sâu | ⭐ Không |
| Min-Conflicts | Local search cho CSP | ⭐ Không |

**Lý do không phù hợp:** Tất cả đều giải quyết bài toán gán giá trị tĩnh, không tìm chuỗi hành động.

---

## PHẦN V: CÁC THUẬT TOÁN GAME

---

## THUẬT TOÁN 12: MINIMAX

### 5.12.1. Định nghĩa

**Minimax** là thuật toán cho game 2 người:
- **MAX:** Muốn maximize utility
- **MIN:** Muốn minimize utility

### 5.12.2. Tại sao 8-puzzle KHÔNG PHẢI game?

**Lý do:**
- 8-puzzle là bài toán 1 người
- Không có đối thủ
- Không có yếu tố cạnh tranh

### 5.12.3. Mô phỏng phiên bản game

**Giả sử tạo phiên bản game:**
- **MAX:** Người giải, muốn giảm h(n)
- **MIN:** Đối thủ, muốn tăng h(n)

### 5.12.4. Cây Game (độ sâu 2)

```
                                [MAX] S
                                h=4
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
           R                     D                     L
          h=3                   h=5                   h=5
            │                     │                     │
          [MIN]                [MIN]                [MIN]
         /     \              /     \              /     \
      h=2      h=4         h=4      h=6         h=4      h=7
        │        │           │        │           │        │
      MAX      MAX         MAX      MAX         MAX      MAX
```

### 5.12.5. Bảng chạy Minimax

| Level | Node | Type | Children | Operation | Value |
|-------|------|------|----------|-----------|-------|
| 2 | Leaf nodes | MAX | - | - | 2, 4, 4, 6, 4, 7 |
| 1 | MIN_R | MIN | {2, 4} | min | 2 |
| 1 | MIN_D | MIN | {4, 6} | min | 4 |
| 1 | MIN_L | MIN | {4, 7} | min | 4 |
| 0 | ROOT | MAX | {2, 4, 4} | max | 4 |

**MAX chọn R** (value = 2, nhưng sau khi MIN chơi, value = 2)

### 5.12.6. Kết luận về Minimax

**Ưu điểm:**
- ✓ Tối ưu cho game 2 người

**Nhược điểm:**
- ✗ Cần đối thủ
- ✗ **KHÔNG PHÙ HỢP cho 8-puzzle**

**Đánh giá phù hợp:** ⭐ (1/5) - 8-puzzle không có đối thủ

---

## THUẬT TOÁN 13: ALPHA-BETA PRUNING

### 5.13.1. Định nghĩa

**Alpha-Beta Pruning** cải tiến Minimax bằng cách cắt nhánh không cần thiết.

### 5.13.2. Bảng chạy Alpha-Beta

| Step | Node | Type | α | β | Value | Action |
|------|------|------|---|---|-------|--------|
| 1 | S | MAX | -∞ | +∞ | - | Bắt đầu |
| 2 | R | MIN | -∞ | +∞ | - | Khám phá |
| 3 | R₁ | MAX | -∞ | +∞ | 2 | Leaf |
| 4 | R | MIN | -∞ | +∞ | 2 | Update β=2 |
| 5 | R₂ | MAX | -∞ | 2 | 4 | Leaf |
| 6 | R | MIN | -∞ | +∞ | 2 | β=min(2,4)=2 |
| 7 | S | MAX | 2 | +∞ | 2 | Update α=2 |
| 8 | D | MIN | 2 | +∞ | - | Khám phá |
| 9 | D₁ | MAX | 2 | +∞ | 4 | Leaf |
| 10 | D | MIN | 2 | +∞ | 4 | Update β=4 |
| 11 | D₂ | MAX | 2 | 4 | - | **PRUNED** (β≤α: 4≤2? No) |
| 12 | S | MAX | 4 | +∞ | 4 | α=max(2,4)=4 |

### 5.13.3. So sánh Minimax vs Alpha-Beta

| Metric | Minimax | Alpha-Beta | Cải thiện |
|--------|---------|------------|-----------|
| Nodes visited | 6 | 4 | 33% |
| Nodes pruned | 0 | 2 | - |

### 5.13.4. Kết luận về Alpha-Beta

**Đánh giá phù hợp:** ⭐ (1/5) - Cần đối thủ, 8-puzzle không có

---

## THUẬT TOÁN 14: EXPECTIMAX

### 5.14.1. Định nghĩa

**Expectimax** dùng cho game có yếu tố ngẫu nhiên với **Chance node**.

### 5.14.2. Cây Expectimax

```
                                [MAX] S
                                h=4
                                  │
                                 R
                                  │
                            ┌─────┴─────┐
                            │           │
                        [CHANCE]        
                        P=0.8       P=0.2
                          │           │
                        h=3         h=5
                          │           │
                        [MIN]       [MIN]
                       /     \     /     \
                     h=2     h=4 h=4     h=6
```

### 5.14.3. Tính Expected Value

| Action | P(success) | h(success) | P(fail) | h(fail) | E[h] |
|--------|------------|------------|---------|---------|------|
| R | 0.8 | 2 | 0.2 | 4 | 0.8×2 + 0.2×4 = 2.4 |
| D | 0.8 | 4 | 0.2 | 6 | 0.8×4 + 0.2×6 = 4.4 |
| L | 0.8 | 4 | 0.2 | 7 | 0.8×4 + 0.2×7 = 4.6 |

**MAX chọn R** vì E[h] = 2.4 (thấp nhất)

### 5.14.4. Kết luận về Expectimax

**Đánh giá phù hợp:** ⭐ (1/5) - 8-puzzle không có yếu tố ngẫu nhiên

---

## PHẦN VI: BẢNG TỔNG HỢP VÀ KẾT LUẬN

---

### BẢNG SO SÁNH TẤT CẢ 14 THUẬT TOÁN

| # | Thuật toán | Phù hợp? | Quan sát | Heuristic | Xác suất | Đối thủ | Đánh giá |
|---|------------|----------|----------|-----------|----------|---------|----------|
| 1 | Simulated Annealing | Không tối ưu | Đầy đủ | Có | Có | Không | ⭐⭐ |
| 2 | AND-OR Search | Không cần | Đầy đủ | Không | Không | Không | ⭐ |
| 3 | No Observation | Không phù hợp | Không | Không | Không | Không | ⭐ |
| 4 | Partially Observable | Không phù hợp | Một phần | Không | Không | Không | ⭐⭐ |
| 5 | Online Search | Không cần | Đầy đủ | Không | Không | Không | ⭐⭐ |
| 6 | CSP | Không phù hợp | Đầy đủ | Không | Không | Không | ⭐ |
| 7 | Constraint Propagation | Không phù hợp | Đầy đủ | Không | Không | Không | ⭐ |
| 8 | Path Consistency | Không phù hợp | Đầy đủ | Không | Không | Không | ⭐ |
| 9 | Global Constraints | Không phù hợp | Đầy đủ | Không | Không | Không | ⭐ |
| 10 | Backtracking | Không phù hợp | Đầy đủ | Không | Không | Không | ⭐ |
| 11 | Min-Conflicts | Không phù hợp | Đầy đủ | Không | Có | Không | ⭐ |
| 12 | Minimax | Không phù hợp | Đầy đủ | Có | Không | Có | ⭐ |
| 13 | Alpha-Beta | Không phù hợp | Đầy đủ | Có | Không | Có | ⭐ |
| 14 | Expectimax | Không phù hợp | Đầy đủ | Có | Có | Có | ⭐ |

---

### KẾT LUẬN CHUNG

#### Thuật toán PHÙ HỢP cho 8-puzzle:

| Thuật toán | Lý do phù hợp | Đánh giá |
|------------|---------------|----------|
| **A*** | Tối ưu, dùng heuristic Manhattan | ⭐⭐⭐⭐⭐ |
| **IDA*** | Tiết kiệm bộ nhớ, tối ưu | ⭐⭐⭐⭐⭐ |
| **BFS** | Tối ưu khi chi phí đều | ⭐⭐⭐⭐ |
| **UCS** | Tương tự BFS | ⭐⭐⭐⭐ |
| **Greedy** | Nhanh (nhưng không tối ưu) | ⭐⭐⭐ |

#### Thuật toán KHÔNG PHÙ HỢP:

| Nhóm | Thuật toán | Lý do không phù hợp |
|------|------------|---------------------|
| **Môi trường bất định** | AND-OR, No Observation, Partially Observable | 8-puzzle là môi trường xác định |
| **Không biết trước** | Online Search | 8-puzzle đã biết không gian trạng thái |
| **CSP** | CSP, Constraint Propagation, Backtracking, Min-Conflicts | 8-puzzle cần tìm chuỗi hành động, không phải gán giá trị |
| **Game** | Minimax, Alpha-Beta, Expectimax | 8-puzzle không có đối thủ |

---

### NGUYÊN TẮC CHỌN THUẬT TOÁN CHO 8-PUZZLE

```
                    ┌─────────────────────────┐
                    │   BÀI TOÁN 8-PUZZLE     │
                    └───────────┬─────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────┴───────┐       ┌───────┴───────┐
            │ Cần tối ưu?  │       │ Giới hạn bộ nhớ?│
            └───────┬───────┘       └───────┬───────┘
                    │                       │
               ┌────┴────┐             ┌────┴────┐
               │         │             │         │
              Có        Không          Có       Không
               │         │             │         │
               ↓         ↓             ↓         ↓
              A*       Greedy        IDA*       BFS
            (Manhattan)  (nhanh)    (iterative) (đơn giản)
```

---

### LỖI THƯỜNG GẶP KHI GIẢI 8-PUZZLE

| Lỗi | Mô tả | Cách tránh |
|-----|-------|------------|
| Quên kiểm tra solvable | Bài có thể không giải được | Luôn tính nghịch thế trước |
| Sai tính nghịch thế | Quên bỏ qua số 0 | Chỉ xét các số 1-8 |
| Sai heuristic | Tính cả ô trống | Không tính ô 0 |
| Chọn sai thuật toán | Dùng CSP/Game algorithms | Hiểu rõ đặc điểm bài toán |
| Không vẽ ma trận | Ghi dãy số khó đọc | Luôn vẽ bảng 3×3 |

---

## PHẦN VII: APP DEMO VÀ TƯƠNG TÁC NHƯ TRÒ CHƠI

### 7.1. Mục tiêu của app

App desktop `8PuzzleSearchLab.exe` được thiết kế để giảng viên có thể mở trực tiếp và quan sát cả hai mặt của bài:

1. **Người chơi tự giải:** click ô nằm cạnh `0` để di chuyển giống trò chơi 8-puzzle.
2. **AI giải bài toán:** chọn thuật toán, heuristic, chạy solver và xem trace `Node / Frontier / Reached`.
3. **Học thuật:** xem PEAS, certificate, heuristic breakdown, experiment và báo cáo Markdown.

### 7.2. Chế độ chơi trực tiếp

| Chức năng | Ý nghĩa học thuật |
|-----------|-------------------|
| Click ô cạnh `0` | Mô phỏng actuator: di chuyển ô trống theo hành động hợp lệ |
| Số nước chơi | Tương ứng với `g(n)` khi mỗi bước có cost = 1 |
| Reset ván | Khôi phục Start state ban đầu của preset/shuffle |
| Gợi ý A* | Dùng `f(n)=g(n)+h(n)` với Manhattan để đề xuất nước đi |
| Đi 1 bước tối ưu | Cho AI áp dụng một action từ nghiệm A* hiện tại |
| Auto-solve | Trình diễn toàn bộ đường đi lời giải từng bước |

### 7.3. Máy hút bụi cho thuật toán tô màu / CSP

Một số thuật toán CSP như **graph coloring / tô màu đồ thị** không phù hợp để
giải trực tiếp 8-puzzle, vì 8-puzzle cần tìm chuỗi hành động trong không gian
trạng thái. Do đó app tách riêng một tab **Vacuum Game** để minh họa graph
coloring đúng bản chất hơn.

**Mô hình Vacuum Cleaner Agent:**

| PEAS | Xác định |
|------|----------|
| Performance | Làm sạch toàn bộ phòng với ít hành động |
| Environment | Lưới phòng 2×3, mỗi phòng sạch/bẩn, deterministic, fully observable |
| Actuators | Up, Down, Left, Right, Suck |
| Sensors | Vị trí hiện tại và trạng thái sạch/bẩn của từng phòng |

**Áp dụng tô màu đồ thị:**

| Thành phần CSP | Trong Vacuum Game |
|----------------|-------------------|
| Biến | Các phòng đang bẩn |
| Miền giá trị | Slot/batch dọn: 1, 2, 3, ... |
| Ràng buộc | Hai phòng kề nhau không được dùng cùng slot |
| Kết quả | Lịch dọn theo batch màu, không phải đường đi 8-puzzle |

Nhờ vậy khi thuyết trình có thể nói rõ:

- 8-puzzle chuẩn dùng BFS/UCS/A*/IDA* để tìm đường đi.
- Graph coloring là CSP, nên demo bằng bài toán lập lịch dọn phòng của agent máy hút bụi.
- Cả hai đều thuộc AI nhưng khác dạng bài toán: state-space search và constraint satisfaction.

### 7.4. Giá trị khi thuyết trình

Khi demo, có thể cho giảng viên thấy cùng một trạng thái được xử lý theo ba tầng:

1. **Tầng game:** người dùng tự click tile để cảm nhận state/action.
2. **Tầng thuật toán:** bấm Run để xem thuật toán chọn node, cập nhật frontier và reached.
3. **Tầng báo cáo:** xuất report/certificate để chứng minh lời giải hợp lệ và thuật toán có/không có bảo đảm tối ưu.

---

**TÀI LIỆU HOÀN CHỈNH - MÔN TRÍ TUỆ NHÂN TẠO**
