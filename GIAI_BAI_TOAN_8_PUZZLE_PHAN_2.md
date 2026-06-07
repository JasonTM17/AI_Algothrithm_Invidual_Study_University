# GIẢI BÀI TOÁN 8-PUZZLE BẰNG CÁC THUẬT TOÁN TÌM KIẾM - PHẦN 2

---

## THUẬT TOÁN 6: CSP (CONSTRAINT SATISFACTION PROBLEM)

### 1. Định nghĩa thuật toán

**CSP (Constraint Satisfaction Problem)** là bài toán tìm giá trị cho các biến sao cho thỏa mãn tất cả các ràng buộc.

**Thành phần của CSP:**
- **Variables (Biến):** Tập các biến cần gán giá trị
- **Domains (Miền giá trị):** Tập giá trị có thể gán cho mỗi biến
- **Constraints (Ràng buộc):** Các điều kiện phải thỏa mãn

### 2. Tại sao 8-puzzle KHÔNG PHẢI CSP tĩnh?

**Lý do quan trọng:**

8-puzzle chuẩn là bài toán **tìm kiếm theo trạng thái (state-space search)**, không phải CSP vì:

1. **Trạng thái thay đổi theo thời gian:** Mỗi bước di chuyển ô trống tạo ra trạng thái mới
2. **Cần tìm chuỗi hành động:** Không phải gán giá trị tĩnh một lần
3. **Có khái niệm "bước đi":** CSP không có khái niệm hành động, chi phí

**Ví dụ khác biệt:**
- **CSP:** "Tìm cách xếp 8 con hậu sao cho không ăn nhau" → Gán vị trí một lần
- **8-puzzle:** "Tìm chuỗi di chuyển từ S đến G" → Cần tìm đường đi

### 3. Mô hình hóa Goal State như một CSP

Tuy nhiên, ta có thể mô hình hóa **Goal State** như một CSP để hiểu cách CSP hoạt động:

#### Variables (Biến)

| Biến | Vị trí trên bảng | Ý nghĩa |
|------|------------------|---------|
| X₁ | (0,0) | Ô góc trái trên |
| X₂ | (0,1) | Ô hàng 1, cột 2 |
| X₃ | (0,2) | Ô góc phải trên |
| X₄ | (1,0) | Ô hàng 2, cột 1 |
| X₅ | (1,1) | Ô giữa |
| X₆ | (1,2) | Ô hàng 2, cột 3 |
| X₇ | (2,0) | Ô góc trái dưới |
| X₈ | (2,1) | Ô hàng 3, cột 2 |
| X₉ | (2,2) | Ô góc phải dưới |

#### Domains (Miền giá trị)

```
D₁ = D₂ = D₃ = D₄ = D₅ = D₆ = D₇ = D₈ = D₉ = {0, 1, 2, 3, 4, 5, 6, 7, 8}
```

Mỗi biến có thể nhận giá trị từ 0 đến 8.

#### Constraints (Ràng buộc)

**Ràng buộc 1: AllDifferent**
```
X₁ ≠ X₂ ≠ X₃ ≠ X₄ ≠ X₅ ≠ X₆ ≠ X₇ ≠ X₈ ≠ X₉
```
Mỗi số từ 0-8 xuất hiện đúng một lần.

**Ràng buộc 2: Goal Position**
```
X₁ = 1, X₂ = 2, X₃ = 3
X₄ = 4, X₅ = 5, X₆ = 6
X₇ = 7, X₈ = 8, X₉ = 0
```

### 4. Constraint Graph

```
        X₁ ───────── X₂ ───────── X₃
         │           │           │
         │           │           │
         │           │           │
        X₄ ───────── X₅ ───────── X₆
         │           │           │
         │           │           │
         │           │           │
        X₇ ───────── X₈ ───────── X₉

Chú thích:
- Mỗi node = một biến (X₁ đến X₉)
- Mỗi cạnh = ràng buộc AllDifferent giữa hai biến
- Tổng số cạnh = C(9,2) = 36 cạnh
```

### 5. Giải CSP cho Goal State

**Bước 1: Gán giá trị theo Goal**

| Step | Biến | Giá trị | Assignment | Consistent? |
|------|------|---------|------------|-------------|
| 1 | X₁ | 1 | {X₁=1} | ✓ |
| 2 | X₂ | 2 | {X₁=1, X₂=2} | ✓ (2≠1) |
| 3 | X₃ | 3 | {X₁=1, X₂=2, X₃=3} | ✓ (3≠1, 3≠2) |
| 4 | X₄ | 4 | {..., X₄=4} | ✓ |
| 5 | X₅ | 5 | {..., X₅=5} | ✓ |
| 6 | X₆ | 6 | {..., X₆=6} | ✓ |
| 7 | X₇ | 7 | {..., X₇=7} | ✓ |
| 8 | X₈ | 8 | {..., X₈=8} | ✓ |
| 9 | X₉ | 0 | {..., X₉=0} | ✓ |

**Kết quả:**
```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
├───┼───┼───┤
│ 7 │ 8 │ 0 │
└───┴───┴───┘
```

### 6. Nhận xét

**Ưu điểm của CSP:**
- Mô hình hóa rõ ràng bài toán gán giá trị
- Có nhiều thuật toán hiệu quả (backtracking, constraint propagation)
- Phù hợp cho bài toán xếp lịch, Sudoku, N-queens

**Nhược điểm cho 8-puzzle:**
- Không tìm được đường đi từ S đến G
- Chỉ giải quyết việc "Goal state là gì"
- Không áp dụng được cho bài toán tìm kiếm theo trạng thái

**Kết luận:** CSP **không phù hợp** để giải 8-puzzle vì 8-puzzle cần tìm chuỗi hành động, không phải gán giá trị tĩnh.

---

## THUẬT TOÁN 7: CONSTRAINT PROPAGATION

### 1. Định nghĩa thuật toán

**Constraint Propagation** là kỹ thuật giảm miền giá trị của biến bằng cách lan truyền ràng buộc từ biến đã gán sang biến chưa gán.

**Ý tưởng:** Nếu một biến X được gán giá trị v, thì tất cả các biến khác không thể nhận giá trị v (với ràng buộc AllDifferent).

### 2. Các phương pháp Constraint Propagation

#### 2.1. Forward Checking (Kiểm tra tiến)

**Forward Checking** giảm miền giá trị của các biến chưa gán sau khi gán một biến.

#### 2.2. Arc Consistency (AC-3)

**Arc Consistency** kiểm tra tính nhất quán giữa hai biến kết nối bởi ràng buộc.

**Định nghĩa:** Arc (Xᵢ, Xⱼ) là consistent nếu với mọi giá trị a ∈ Dᵢ, tồn tại giá trị b ∈ Dⱼ sao cho (a, b) thỏa mãn ràng buộc.

### 3. Áp dụng vào 8-puzzle CSP

**Giả sử:** Đang giải Goal State như một CSP.

#### Bước 0: Khởi tạo

| Biến | Domain ban đầu |
|------|-----------------|
| X₁ | {0, 1, 2, 3, 4, 5, 6, 7, 8} |
| X₂ | {0, 1, 2, 3, 4, 5, 6, 7, 8} |
| X₃ | {0, 1, 2, 3, 4, 5, 6, 7, 8} |
| X₄ | {0, 1, 2, 3, 4, 5, 6, 7, 8} |
| X₅ | {0, 1, 2, 3, 4, 5, 6, 7, 8} |
| X₆ | {0, 1, 2, 3, 4, 5, 6, 7, 8} |
| X₇ | {0, 1, 2, 3, 4, 5, 6, 7, 8} |
| X₈ | {0, 1, 2, 3, 4, 5, 6, 7, 8} |
| X₉ | {0, 1, 2, 3, 4, 5, 6, 7, 8} |

#### Bước 1: Gán X₁ = 1

**Forward Checking:** Loại 1 khỏi domain của tất cả biến khác.

| Biến | Domain trước | Domain sau | Giảm? |
|------|--------------|------------|-------|
| X₁ | {0,1,2,3,4,5,6,7,8} | {1} | ✓ |
| X₂ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | ✓ |
| X₃ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | ✓ |
| X₄ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | ✓ |
| X₅ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | ✓ |
| X₆ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | ✓ |
| X₇ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | ✓ |
| X₈ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | ✓ |
| X₉ | {0,1,2,3,4,5,6,7,8} | {0,2,3,4,5,6,7,8} | ✓ |

**Kích thước domain giảm:** 9 → 8 (cho các biến chưa gán)

#### Bước 2: Gán X₂ = 2

| Biến | Domain trước | Domain sau | Giảm? |
|------|--------------|------------|-------|
| X₁ | {1} | {1} | Không |
| X₂ | {0,2,3,4,5,6,7,8} | {2} | ✓ |
| X₃ | {0,2,3,4,5,6,7,8} | {0,3,4,5,6,7,8} | ✓ |
| X₄ | {0,2,3,4,5,6,7,8} | {0,3,4,5,6,7,8} | ✓ |
| X₅ | {0,2,3,4,5,6,7,8} | {0,3,4,5,6,7,8} | ✓ |
| X₆ | {0,2,3,4,5,6,7,8} | {0,3,4,5,6,7,8} | ✓ |
| X₇ | {0,2,3,4,5,6,7,8} | {0,3,4,5,6,7,8} | ✓ |
| X₈ | {0,2,3,4,5,6,7,8} | {0,3,4,5,6,7,8} | ✓ |
| X₉ | {0,2,3,4,5,6,7,8} | {0,3,4,5,6,7,8} | ✓ |

#### Bảng tổng hợp quá trình Constraint Propagation

| Step | Biến gán | Giá trị | |D₁| | |D₂| | |D₃| | |D₄| | |D₅| | |D₆| | |D₇| | |D₈| | |D₉| |
|------|----------|---------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | - | - | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 1 | X₁ | 1 | 1 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |
| 2 | X₂ | 2 | 1 | 1 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |
| 3 | X₃ | 3 | 1 | 1 | 1 | 6 | 6 | 6 | 6 | 6 | 6 |
| 4 | X₄ | 4 | 1 | 1 | 1 | 1 | 5 | 5 | 5 | 5 | 5 |
| 5 | X₅ | 5 | 1 | 1 | 1 | 1 | 1 | 4 | 4 | 4 | 4 |
| 6 | X₆ | 6 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 3 | 3 |
| 7 | X₇ | 7 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 |
| 8 | X₈ | 8 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 9 | X₉ | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

### 4. Thuật toán AC-3

```
function AC-3(csp):
    queue = tất cả các arc trong csp
    while queue không rỗng:
        (Xᵢ, Xⱼ) = queue.pop()
        if REMOVE-INCONSISTENT-VALUES(Xᵢ, Xⱼ):
            for each Xₖ neighbor của Xᵢ:
                queue.add((Xₖ, Xᵢ))
    return true

function REMOVE-INCONSISTENT-VALUES(Xᵢ, Xⱼ):
    removed = false
    for each a ∈ Dᵢ:
        if không có b ∈ Dⱼ thỏa mãn constraint(Xᵢ, Xⱼ, a, b):
            Dᵢ.remove(a)
            removed = true
    return removed
```

### 5. Nhận xét

**Ưu điểm:**
- Giảm đáng kể không gian tìm kiếm
- Phát hiện sớm các trường hợp không có lời giải
- Kết hợp tốt với backtracking

**Nhược điểm:**
- Tốn chi phí tính toán
- Với AllDifferent, cần thuật toán phức tạp hơn
- Không giải quyết được bài toán tìm đường đi

---

## THUẬT TOÁN 8: PATH CONSISTENCY

### 1. Định nghĩa thuật toán

**Path Consistency** là kỹ thuật kiểm tra tính nhất quán của đường đi giữa 3 biến.

**Định nghĩa:** (Xᵢ, Xⱼ) là path consistent với Xₖ nếu với mọi cặp giá trị (a, b) ∈ Dᵢ × Dⱼ thỏa mãn constraint(Xᵢ, Xⱼ), tồn tại giá trị c ∈ Dₖ sao cho cả (a, c) và (c, b) đều thỏa mãn các constraint tương ứng.

### 2. Công thức

```
PathConsistent(Xᵢ, Xⱼ, Xₖ) = 
    ∀a ∈ Dᵢ, ∀b ∈ Dⱼ:
        nếu (a, b) hợp lệ thì ∃c ∈ Dₖ:
            (a, c) hợp lệ VÀ (c, b) hợp lệ
```

### 3. Áp dụng vào 8-puzzle CSP

**Giả sử:** Xét 3 biến X₁, X₅, X₉ (góc trái trên, giữa, góc phải dưới)

```
        X₁ ───────── X₅ ───────── X₉
```

#### Kiểm tra Path Consistency

**Giả sử:**
- D₁ = {1, 2}
- D₅ = {5, 6}
- D₉ = {0, 8}

**Kiểm tra từng cặp:**

| (a, b) từ (X₁, X₉) | Tồn tại c ∈ D₅? | Path Consistent? |
|---------------------|-----------------|------------------|
| (1, 0) | c=5: (1≠5)✓, (5≠0)✓ | ✓ |
| (1, 8) | c=5: (1≠5)✓, (5≠8)✓ | ✓ |
| (2, 0) | c=5: (2≠5)✓, (5≠0)✓ | ✓ |
| (2, 8) | c=5: (2≠5)✓, (5≠8)✓ | ✓ |

**Kết luận:** (X₁, X₉) là path consistent với X₅.

### 4. Thuật toán PC-2

```
function PC-2(csp):
    queue = tất cả các path (Xᵢ, Xⱼ, Xₖ)
    while queue không rỗng:
        (Xᵢ, Xⱼ, Xₖ) = queue.pop()
        if REVISE-PATH(Xᵢ, Xⱼ, Xₖ):
            if Dᵢ rỗng hoặc Dⱼ rỗng:
                return false
            for each Xₗ neighbor của Xᵢ hoặc Xⱼ:
                queue.add((Xᵢ, Xₗ, Xⱼ))
                queue.add((Xⱼ, Xₗ, Xᵢ))
    return true
```

### 5. Nhận xét

**Ưu điểm:**
- Kiểm tra chặt chẽ hơn Arc Consistency
- Loại bỏ được nhiều cặp giá trị không hợp lệ

**Nhược điểm:**
- Chi phí tính toán cao hơn AC-3
- Phức tạp hơn để implement
- Vẫn không giải quyết được bài toán tìm đường đi

---

## THUẬT TOÁN 9: GLOBAL CONSTRAINTS

### 1. Định nghĩa

**Global Constraint** là ràng buộc áp dụng cho nhiều biến cùng lúc, không chỉ cặp biến.

### 2. AllDifferent Constraint

**AllDifferent(X₁, X₂, ..., Xₙ)** = Tất cả n biến phải có giá trị khác nhau.

**Ví dụ trong 8-puzzle:**
```
AllDifferent(X₁, X₂, X₃, X₄, X₅, X₆, X₇, X₈, X₉)
```

### 3. Cách implement AllDifferent

#### Phương pháp 1: Binary Decomposition

Phân rã thành n(n-1)/2 binary constraints:
```
X₁ ≠ X₂, X₁ ≠ X₃, X₁ ≠ X₄, ...
X₂ ≠ X₃, X₂ ≠ X₄, ...
...
```

**Nhược điểm:** Không hiệu quả, mất tính global.

#### Phương pháp 2: Bipartite Matching

**Ý tưởng:**
1. Tạo đồ thị bipartite: Variables ↔ Values
2. Tìm matching hoàn hảo
3. Nếu tồn tại → AllDifferent thỏa mãn

### 4. Ví dụ áp dụng

**Giả sử:**
```
D₁ = {1, 2}
D₂ = {1, 2}
D₃ = {3}
D₄ = {4}
D₅ = {5}
D₆ = {6}
D₇ = {7}
D₈ = {8}
D₉ = {0}
```

**Bipartite Graph:**
```
Variables          Values
   X₁ ──────────── 1
    │╲            │
    │ ╲           │
   X₂ ─────────── 2
   X₃ ─────────── 3
   X₄ ─────────── 4
   X₅ ─────────── 5
   X₆ ─────────── 6
   X₇ ─────────── 7
   X₈ ─────────── 8
   X₉ ─────────── 0
```

**Vấn đề:** X₁ và X₂ đều có domain {1, 2}, chỉ có thể gán một trong hai giá trị này cho một biến.

**Kết luận:** Không tồn tại matching hoàn hảo → AllDifferent không thỏa mãn với domains này.

### 5. Bảng minh họa

| Biến | Domain | Giá trị đã dùng | Giá trị khả dụng |
|------|--------|-----------------|------------------|
| X₁ | {1, 2} | {} | {1, 2} |
| X₂ | {1, 2} | {1} | {2} |
| X₃ | {3} | {1, 2} | {3} |
| X₄ | {4} | {1, 2, 3} | {4} |
| X₅ | {5} | {1, 2, 3, 4} | {5} |
| X₆ | {6} | {1, 2, 3, 4, 5} | {6} |
| X₇ | {7} | {1, 2, 3, 4, 5, 6} | {7} |
| X₈ | {8} | {1, 2, 3, 4, 5, 6, 7} | {8} |
| X₉ | {0} | {1, 2, 3, 4, 5, 6, 7, 8} | {0} |

### 6. Nhận xét

**Ưu điểm:**
- Ràng buộc mạnh, giảm nhiều không gian tìm kiếm
- Có thuật toán hiệu quả (bipartite matching)

**Nhược điểm:**
- Vẫn không giải quyết được bài toán tìm đường đi
- Phức tạp hơn binary constraints

---

## THUẬT TOÁN 10: BACKTRACKING SEARCH

### 1. Định nghĩa thuật toán

**Backtracking Search** là thuật toán tìm kiếm theo chiều sâu, thử gán giá trị cho từng biến, nếu không hợp lệ thì quay lui.

### 2. Thuật toán cơ bản

```
function BACKTRACKING-SEARCH(csp):
    return BACKTRACK({}, csp)

function BACKTRACK(assignment, csp):
    if assignment complete:
        return assignment
    
    var = SELECT-UNASSIGNED-VARIABLE(csp, assignment)
    
    for each value in ORDER-DOMAIN-VALUES(var, assignment, csp):
        if value consistent with assignment:
            assignment[var] = value
            result = BACKTRACK(assignment, csp)
            if result ≠ FAILURE:
                return result
            remove var from assignment
    
    return FAILURE
```

### 3. Các heuristic cải tiến

#### 3.1. MRV (Minimum Remaining Values)

**Chọn biến có ít giá trị khả dụng nhất.**

**Ví dụ:**
| Biến | |Domain| | Được chọn? |
|------|----------|------------|
| X₁ | 5 | |
| X₂ | 2 | ✓ (ít nhất) |
| X₃ | 4 | |
| X₄ | 3 | |

#### 3.2. Degree Heuristic

**Chọn biến có nhiều ràng buộc nhất với biến chưa gán.**

**Ví dụ:**
| Biến | Số neighbor chưa gán | Được chọn? |
|------|---------------------|------------|
| X₁ | 2 | |
| X₂ | 4 | ✓ (nhiều nhất) |
| X₃ | 3 | |

#### 3.3. Least Constraining Value

**Chọn giá trị ít hạn chế nhất các biến khác.**

**Ví dụ:**
| Giá trị | Số neighbor bị ảnh hưởng | Được chọn? |
|---------|-------------------------|------------|
| 1 | 5 | |
| 2 | 2 | ✓ (ít nhất) |
| 3 | 4 | |

### 4. Áp dụng vào 8-puzzle CSP

**Giải Goal State bằng Backtracking:**

#### Bước 0: Khởi tạo

| Biến | Domain |
|------|--------|
| X₁ | {0,1,2,3,4,5,6,7,8} |
| X₂ | {0,1,2,3,4,5,6,7,8} |
| ... | ... |

#### Bảng chạy Backtracking

| Step | Biến | Giá trị thử | Assignment | Consistent? | Action |
|------|------|-------------|------------|-------------|--------|
| 1 | X₁ | 1 | {X₁=1} | ✓ | Tiếp tục |
| 2 | X₂ | 1 | {X₁=1, X₂=1} | ✗ | Backtrack |
| 3 | X₂ | 2 | {X₁=1, X₂=2} | ✓ | Tiếp tục |
| 4 | X₃ | 1 | {X₁=1, X₂=2, X₃=1} | ✗ | Backtrack |
| 5 | X₃ | 2 | {X₁=1, X₂=2, X₃=2} | ✗ | Backtrack |
| 6 | X₃ | 3 | {X₁=1, X₂=2, X₃=3} | ✓ | Tiếp tục |
| 7 | X₄ | 1 | {..., X₄=1} | ✗ | Backtrack |
| 8 | X₄ | 2 | {..., X₄=2} | ✗ | Backtrack |
| 9 | X₄ | 3 | {..., X₄=3} | ✗ | Backtrack |
| 10 | X₄ | 4 | {..., X₄=4} | ✓ | Tiếp tục |
| 11 | X₅ | 5 | {..., X₅=5} | ✓ | Tiếp tục |
| 12 | X₆ | 6 | {..., X₆=6} | ✓ | Tiếp tục |
| 13 | X₇ | 7 | {..., X₇=7} | ✓ | Tiếp tục |
| 14 | X₈ | 8 | {..., X₈=8} | ✓ | Tiếp tục |
| 15 | X₉ | 0 | {..., X₉=0} | ✓ | SUCCESS! |

### 5. Cây Backtracking

```
                                    X₁
                                     │
                                     1
                                     │
                                    X₂
                                   / | \
                                  1  2  3 ...
                                  │   │
                                 ✗  X₃
                                    / | \
                                   1  2  3
                                   │   │  │
                                  ✗  ✗  X₄
                                         |
                                        ...
                                         |
                                        X₉
                                         │
                                         0
                                         │
                                      SUCCESS
```

### 6. Kết quả

```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
├───┼───┼───┤
│ 7 │ 8 │ 0 │
└───┴───┴───┘
```

### 7. Nhận xét

**Ưu điểm:**
- Đảm bảo tìm thấy lời giải (nếu tồn tại)
- Kết hợp được nhiều heuristic
- Dễ hiểu, dễ implement

**Nhược điểm:**
- Có thể rất chậm nếu không dùng heuristic
- Không tìm được đường đi từ S đến G
- Chỉ giải quyết việc "Goal state là gì"

**Kết luận:** Backtracking **không phù hợp** để giải 8-puzzle vì không tìm được chuỗi hành động.

---

## THUẬT TOÁN 11: MIN-CONFLICTS ALGORITHM

### 1. Định nghĩa thuật toán

**Min-Conflicts** là thuật toán local search cho CSP:
1. Bắt đầu với một assignment hoàn chỉnh (có thể không hợp lệ)
2. Lặp: chọn biến bị xung đột, đổi giá trị để giảm xung đột
3. Lặp cho đến khi không còn xung đột

### 2. Thuật toán

```
function MIN-CONFLICTS(csp, max_steps):
    current = random complete assignment
    for i = 1 to max_steps:
        if current is solution:
            return current
        var = randomly select conflicted variable
        value = value minimizing conflicts
        current[var] = value
    return FAILURE
```

### 3. Áp dụng vào 8-puzzle

**Lưu ý:** Min-Conflicts không phù hợp cho 8-puzzle vì:
- 8-puzzle không phải CSP tĩnh
- Tuy nhiên, ta có thể mô phỏng như một bài toán tối ưu hóa

### 4. Mô phỏng

**Bước 0: Khởi tạo assignment ngẫu nhiên**

```
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 5 │ 0 │ 6 │
├───┼───┼───┤
│ 4 │ 7 │ 8 │
└───┴───┴───┘
```

**Tính conflicts (số ô sai vị trí):**
- Ô 5: sai vị trí → 1 conflict
- Ô 4: sai vị trí → 1 conflict
- Ô 7: sai vị trí → 1 conflict
- Ô 8: sai vị trí → 1 conflict

**Total conflicts = 4**

### 5. Bảng chạy Min-Conflicts

| Step | Current State | Conflicts | Biến chọn | Giá trị mới | New Conflicts | Ghi chú |
|------|---------------|-----------|-----------|-------------|---------------|---------|
| 0 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 7 │ 8 │`<br>`└───┴───┴───┘` | 4 | - | - | - | Khởi tạo |
| 1 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 0 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 5 │ 7 │ 8 │`<br>`└───┴───┴───┘` | 3 | X₄, X₅ | Đổi 4↔5 | 3 | Giảm 1 |
| 2 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 5 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 7 │ 0 │ 8 │`<br>`└───┴───┴───┘` | 2 | X₅, X₈ | Đổi 0↔7 | 2 | Giảm 1 |
| 3 | `┌───┬───┬───┐`<br>`│ 1 │ 2 │ 3 │`<br>`├───┼───┼───┤`<br>`│ 4 │ 5 │ 6 │`<br>`├───┼───┼───┤`<br>`│ 7 │ 8 │ 0 │`<br>`└───┴───┴───┘` | 0 | X₈, X₉ | Đổi 0↔8 | 0 | GOAL! |

### 6. Nhận xét

**Ưu điểm:**
- Nhanh cho CSP lớn (như N-Queens với N lớn)
- Đơn giản, dễ implement
- Tốn ít bộ nhớ

**Nhược điểm:**
- Không đảm bảo tìm thấy lời giải
- Có thể kẹt ở local minimum
- **Không phù hợp cho 8-puzzle** vì đây là bài toán tìm kiếm theo trạng thái

**Tại sao không phù hợp:**
- Min-Conflicts chỉ đổi giá trị của biến, không di chuyển ô trống
- Không tìm được chuỗi hành động hợp lệ
- Kết quả có thể không đạt được từ trạng thái ban đầu

---

## THUẬT TOÁN 12: MINIMAX

### 1. Định nghĩa thuật toán

**Minimax** là thuật toán cho game 2 người, zero-sum:
- **MAX:** Muốn maximize utility
- **MIN:** Muốn minimize utility

### 2. Tại sao 8-puzzle KHÔNG PHẢI game 2 người?

**Lý do:**
- 8-puzzle là bài toán 1 người giải puzzle
- Không có đối thủ
- Không có yếu tố cạnh tranh

**Kết luận:** Minimax **không cần thiết** cho 8-puzzle chuẩn.

### 3. Mô phỏng phiên bản game

**Giả sử tạo phiên bản 8-puzzle game:**
- **MAX:** Người giải puzzle, muốn giảm h(n)
- **MIN:** Đối thủ, muốn làm trạng thái xấu hơn (tăng h(n))

**Quy tắc:**
- MAX chọn hành động để giảm h(n)
- MIN chọn hành động để tăng h(n)
- Luân phiên MAX và MIN

### 4. Cây Game (độ sâu 3)

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
              [MAX]    [MAX]      [MAX]    [MAX]       [MAX]    [MAX]
              / \      / \        / \      / \         / \      / \
            h=1  h=3  h=3  h=5  h=3  h=5  h=5  h=7   h=3  h=5  h=5  h=8
```

### 5. Chạy Minimax từng bước

#### Bước 1: Tính giá trị tại các node lá (MAX level 3)

| Node | h | Value |
|------|---|-------|
| MAX_R1 | 1 | 1 |
| MAX_R2 | 3 | 3 |
| MAX_R3 | 3 | 3 |
| MAX_R4 | 5 | 5 |
| MAX_D1 | 3 | 3 |
| MAX_D2 | 5 | 5 |
| MAX_D3 | 5 | 5 |
| MAX_D4 | 7 | 7 |
| MAX_L1 | 3 | 3 |
| MAX_L2 | 5 | 5 |
| MAX_L3 | 5 | 5 |
| MAX_L4 | 8 | 8 |

#### Bước 2: Tính giá trị tại node MIN (level 2)

| MIN Node | Children | min(children) | Value |
|----------|----------|---------------|-------|
| MIN_R | {1, 3} | min(1, 3) | 1 |
| MIN_R' | {3, 5} | min(3, 5) | 3 |
| MIN_D | {3, 5} | min(3, 5) | 3 |
| MIN_D' | {5, 7} | min(5, 7) | 5 |
| MIN_L | {3, 5} | min(3, 5) | 3 |
| MIN_L' | {5, 8} | min(5, 8) | 5 |

#### Bước 3: Tính giá trị tại node MAX (level 1)

| MAX Node | Children | max(children) | Value |
|----------|----------|---------------|-------|
| MAX_R | {1, 3} | max(1, 3) | 3 |
| MAX_D | {3, 5} | max(3, 5) | 5 |
| MAX_L | {3, 5} | max(3, 5) | 5 |

#### Bước 4: Tính giá trị tại ROOT

| ROOT | Children | max(children) | Best Action |
|------|----------|---------------|-------------|
| S | {3, 5, 5} | max(3, 5, 5) | R (value=3) |

### 6. Bảng tổng hợp

| Level | Node | Type | Children Values | Operation | Value |
|-------|------|------|-----------------|-----------|-------|
| 3 | Leaves | MAX | - | - | 1, 3, 3, 5, 3, 5, 5, 7, 3, 5, 5, 8 |
| 2 | MIN_R | MIN | {1, 3} | min | 1 |
| 2 | MIN_R' | MIN | {3, 5} | min | 3 |
| 2 | MIN_D | MIN | {3, 5} | min | 3 |
| 2 | MIN_D' | MIN | {5, 7} | min | 5 |
| 2 | MIN_L | MIN | {3, 5} | min | 3 |
| 2 | MIN_L' | MIN | {5, 8} | min | 5 |
| 1 | MAX_R | MAX | {1, 3} | max | 3 |
| 1 | MAX_D | MAX | {3, 5} | max | 5 |
| 1 | MAX_L | MAX | {3, 5} | max | 5 |
| 0 | S | MAX | {3, 5, 5} | max | 3 |

### 7. Kết quả

**MAX chọn hành động R** vì R dẫn đến value = 3 (tốt nhất).

### 8. Nhận xét

**Ưu điểm:**
- Tìm được nước đi tối ưu (nếu có đủ độ sâu)
- Phù hợp cho game 2 người

**Nhược điểm:**
- Cần đối thủ (8-puzzle không có)
- Độ phức tạp exponentially
- **Không phù hợp cho 8-puzzle chuẩn**

---

## THUẬT TOÁN 13: ALPHA-BETA PRUNING

### 1. Định nghĩa thuật toán

**Alpha-Beta Pruning** cải tiến Minimax bằng cách cắt các nhánh không cần thiết.

**Khái niệm:**
- **α (alpha):** Giá trị tốt nhất MAX có thể đạt được (lower bound)
- **β (beta):** Giá trị tốt nhất MIN có thể đạt được (upper bound)

**Quy tắc cắt:**
- Nếu β ≤ α → Cắt nhánh (prune)

### 2. Chạy Alpha-Beta trên cùng cây Minimax

#### Bắt đầu: α = -∞, β = +∞

```
                                        [MAX] S
                                        α=-∞, β=+∞
                                          │
                                          ↓
                                    Chọn R
                                          │
                                      [MIN]
                                      α=-∞, β=+∞
                                      /         \
                                    h=1         h=3
                                    ✓           ✓
                                    │           │
                                    ↓           ↓
                              UPDATE α=1    UPDATE α=3
                                    │           │
                                    └─────┬─────┘
                                          │
                                    β = min(1, 3) = 1
```

#### Tiếp tục với nhánh D:

```
                                        [MAX] S
                                        α=3, β=+∞
                                          │
                                          ↓
                                    Chọn D
                                          │
                                      [MIN]
                                      α=3, β=+∞
                                      /         \
                                    h=3         h=5
                                    ✓           PRUNED!
                                    │           (β ≤ α: 3 ≤ 3)
                                    ↓
                              UPDATE α=3
```

**Cắt nhánh:** Khi MIN thấy con đầu tiên = 3, và MAX đã có α = 3, không cần xét thêm.

#### Tiếp tục với nhánh L:

```
                                        [MAX] S
                                        α=3, β=+∞
                                          │
                                          ↓
                                    Chọn L
                                          │
                                      [MIN]
                                      α=3, β=+∞
                                      /         \
                                    h=3         h=5
                                    ✓           PRUNED!
                                    │           (β ≤ α)
                                    ↓
                              Không cải thiện α
```

### 3. Bảng chạy chi tiết

| Step | Node | Type | α | β | Value | Action |
|------|------|------|---|---|-------|--------|
| 1 | S | MAX | -∞ | +∞ | - | Bắt đầu |
| 2 | R | MIN | -∞ | +∞ | - | Khám phá |
| 3 | R₁ | MAX | -∞ | +∞ | 1 | Leaf |
| 4 | R | MIN | -∞ | +∞ | 1 | Update β=1 |
| 5 | R₂ | MAX | -∞ | 1 | 3 | Leaf |
| 6 | R | MIN | -∞ | 1 | 1 | β=min(1,3)=1 |
| 7 | S | MAX | 1 | +∞ | 1 | Update α=1 |
| 8 | D | MIN | 1 | +∞ | - | Khám phá |
| 9 | D₁ | MAX | 1 | +∞ | 3 | Leaf |
| 10 | D | MIN | 1 | +∞ | 3 | Update β=3 |
| 11 | D₂ | MAX | 1 | 3 | - | **PRUNED** (β≤α) |
| 12 | S | MAX | 3 | +∞ | 3 | α=max(1,3)=3 |
| 13 | L | MIN | 3 | +∞ | - | Khám phá |
| 14 | L₁ | MAX | 3 | +∞ | 3 | Leaf |
| 15 | L | MIN | 3 | +∞ | 3 | Update β=3 |
| 16 | L₂ | MAX | 3 | 3 | - | **PRUNED** (β≤α) |
| 17 | S | MAX | 3 | +∞ | 3 | α=max(3,3)=3 |

### 4. So sánh Minimax vs Alpha-Beta

| Metric | Minimax | Alpha-Beta | Cải thiện |
|--------|---------|------------|-----------|
| Nodes visited | 12 | 6 | 50% |
| Nodes pruned | 0 | 6 | - |
| Time complexity | O(b^d) | O(b^(d/2)) | √b times faster |

### 5. Nhận xét

**Ưu điểm:**
- Cắt giảm đáng kể số node cần duyệt
- Kết quả giống Minimax
- Hiệu quả hơn nhiều cho cây lớn

**Nhược điểm:**
- Vẫn cần đối thủ
- Hiệu quả phụ thuộc vào thứ tự node
- **Không phù hợp cho 8-puzzle chuẩn**

---

## THUẬT TOÁN 14: EXPECTIMAX

### 1. Định nghĩa thuật toán

**Expectimax** dùng cho game có yếu tố ngẫu nhiên (stochastic games).

**Các loại node:**
- **MAX node:** Chọn giá trị lớn nhất
- **MIN node:** Chọn giá trị nhỏ nhất
- **CHANCE node:** Tính expected value = Σ P(s) × V(s)

### 2. Mô phỏng 8-puzzle với yếu tố ngẫu nhiên

**Giả sử:** Sau khi MAX chọn hành động, môi trường có 20% xác suất làm sai lệch kết quả.

**Ví dụ:** MAX chọn R, nhưng có:
- 80%: Kết quả đúng (ô trống di chuyển đúng)
- 20%: Kết quả sai (ô trống trượt thêm)

### 3. Cây Expectimax

```
                                        [MAX] S
                                        h=4
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
                   R                     D                     L
                    │                     │                     │
                              [CHANCE]
                              /         \
                          P=0.8         P=0.2
                            │             │
                          h=3           h=5
                            │             │
                          [MIN]         [MIN]
                         /     \       /     \
                       h=2     h=4   h=4     h=6
```

### 4. Tính Expected Value

#### Cho hành động R:

```
E[R] = 0.8 × E[R_success] + 0.2 × E[R_fail]

E[R_success] = min(2, 4) = 2
E[R_fail] = min(4, 6) = 4

E[R] = 0.8 × 2 + 0.2 × 4 = 1.6 + 0.8 = 2.4
```

#### Cho hành động D:

```
E[D] = 0.8 × E[D_success] + 0.2 × E[D_fail]

E[D_success] = min(3, 5) = 3
E[D_fail] = min(5, 7) = 5

E[D] = 0.8 × 3 + 0.2 × 5 = 2.4 + 1.0 = 3.4
```

#### Cho hành động L:

```
E[L] = 0.8 × E[L_success] + 0.2 × E[L_fail]

E[L_success] = min(3, 5) = 3
E[L_fail] = min(5, 8) = 5

E[L] = 0.8 × 3 + 0.2 × 5 = 2.4 + 1.0 = 3.4
```

### 5. Bảng tổng hợp

| Action | P(success) | h(success) | P(fail) | h(fail) | E[h] |
|--------|------------|------------|---------|---------|------|
| R | 0.8 | 2 | 0.2 | 4 | 2.4 |
| D | 0.8 | 3 | 0.2 | 5 | 3.4 |
| L | 0.8 | 3 | 0.2 | 5 | 3.4 |

### 6. Kết quả

**MAX chọn R** vì E[h] = 2.4 (thấp nhất, tốt nhất)

### 7. So sánh Expectimax vs Minimax

| Aspect | Minimax | Expectimax |
|--------|---------|------------|
| Môi trường | Deterministic | Stochastic |
| Node types | MAX, MIN | MAX, MIN, CHANCE |
| Tính giá trị | max/min | max/min/expected |
| Phức tạp | O(b^d) | O(b^d × n) |

### 8. Nhận xét

**Ưu điểm:**
- Xử lý được yếu tố ngẫu nhiên
- Phù hợp cho game có randomness (backgammon, poker)

**Nhược điểm:**
- Phức tạp hơn Minimax
- Cần biết xác suất
- **Không phù hợp cho 8-puzzle chuẩn** (không có yếu tố ngẫu nhiên)

---

## BẢNG SO SÁNH TẤT CẢ 14 THUẬT TOÁN

| # | Thuật toán | Phù hợp 8-puzzle? | Quan sát | Heuristic | Xác suất | Đối thủ | Ưu điểm | Nhược điểm |
|---|------------|-------------------|----------|-----------|----------|---------|---------|------------|
| 1 | Simulated Annealing | Không tối ưu | Đầy đủ | Có | Có | Không | Thoát local optimum | Kết quả ngẫu nhiên |
| 2 | AND-OR Search | Không cần thiết | Đầy đủ | Không | Không | Không | Xử lý bất định | Phức tạp |
| 3 | No Observation | Không phù hợp | Không | Không | Không | Không | Xử lý không quan sát | Rất khó |
| 4 | Partially Observable | Không phù hợp | Một phần | Không | Không | Không | Thực tế | Phức tạp |
| 5 | Online Search | Không cần thiết | Đầy đủ | Không | Không | Không | Không cần biết trước | Không tối ưu |
| 6 | CSP | Không phù hợp | Đầy đủ | Không | Không | Không | Giải bài toán gán | Không tìm đường |
| 7 | Constraint Propagation | Không phù hợp | Đầy đủ | Không | Không | Không | Giảm miền giá trị | Không giải alone |
| 8 | Path Consistency | Không phù hợp | Đầy đủ | Không | Không | Không | Kiểm tra chặt | Tốn chi phí |
| 9 | Global Constraints | Không phù hợp | Đầy đủ | Không | Không | Không | Ràng buộc mạnh | Phức tạp |
| 10 | Backtracking | Không phù hợp | Đầy đủ | Không | Không | Không | Đảm bảo tìm thấy | Chậm |
| 11 | Min-Conflicts | Không phù hợp | Đầy đủ | Không | Có | Không | Nhanh cho CSP lớn | Không đảm bảo |
| 12 | Minimax | Không phù hợp | Đầy đủ | Có | Không | Có | Tối ưu cho game | Cần đối thủ |
| 13 | Alpha-Beta | Không phù hợp | Đầy đủ | Có | Không | Có | Cắt nhánh hiệu quả | Cần đối thủ |
| 14 | Expectimax | Không phù hợp | Đầy đủ | Có | Có | Có | Xử lý ngẫu nhiên | Phức tạp |

---

## KẾT LUẬN CHUNG

### Thuật toán PHÙ HỢP cho 8-puzzle:

1. **A*** - Tối ưu, dùng heuristic Manhattan
2. **IDA*** - Tiết kiệm bộ nhớ
3. **BFS** - Tối ưu khi chi phí đều
4. **UCS** - Tương tự BFS với chi phí đều
5. **Greedy** - Nhanh nhưng không tối ưu
6. **Hill Climbing** - Đơn giản nhưng dễ kẹt

### Thuật toán KHÔNG PHÙ HỢP:

- **AND-OR Search:** 8-puzzle không có bất định
- **No/Partial Observation:** 8-puzzle quan sát đầy đủ
- **CSP-based:** 8-puzzle cần tìm đường đi, không phải gán giá trị
- **Game algorithms:** 8-puzzle không có đối thủ

### Lý do chính:

1. **8-puzzle là môi trường xác định:** Mỗi hành động dẫn đến 1 kết quả duy nhất
2. **8-puzzle là môi trường quan sát đầy đủ:** Agent nhìn thấy toàn bộ trạng thái
3. **8-puzzle là bài toán 1 người:** Không có đối thủ
4. **8-puzzle cần tìm chuỗi hành động:** Không phải gán giá trị tĩnh

---

*Tài liệu hoàn chỉnh cho môn Trí tuệ nhân tạo*
