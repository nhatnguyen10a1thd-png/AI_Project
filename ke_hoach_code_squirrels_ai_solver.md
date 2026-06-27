# Kế hoạch code dự án Squirrels Go Nuts AI Solver

## 0. Thông tin đã chốt

Dự án sẽ được xây dựng theo hướng **game 2D có giao diện đẹp + AI solver + mô phỏng thuật toán**.

| Hạng mục | Quyết định |
|---|---|
| Công nghệ | Python + Pygame |
| Mức độ thuật toán | Code đầy đủ tất cả thuật toán đã chọn |
| Nhóm thuật toán | Tất cả nhóm đã liệt kê: Uninformed, Informed, Local Search, CSP, Adversarial, AND-OR / Belief State |
| Giao diện | Game 2D đẹp như app thật |
| Điều khiển | Click chọn miếng + phím mũi tên |
| Level | Có màn chọn level Starter / Junior / Expert |
| Tài nguyên hình ảnh | Asset cartoon/vector |
| AI visualization | Có: hiển thị frontier, visited, current state, path và đường đi tới đích |
| File kế hoạch | Vừa phục vụ lập trình, vừa phục vụ báo cáo đồ án |
| Deadline | 1 tuần |

---

## 1. Mục tiêu tổng thể

Tên đề tài đề xuất:

> **Ứng dụng các thuật toán tìm kiếm trong Trí tuệ nhân tạo để giải trò chơi Squirrels Go Nuts**

Mục tiêu sản phẩm cuối cùng:

1. Có giao diện game 2D đẹp, dễ dùng, mượt.
2. Người chơi có thể chọn level và tự chơi bằng click + phím mũi tên.
3. Có AI Solver chạy nhiều nhóm thuật toán.
4. Sau khi AI giải, chương trình hiển thị:
   - Đường đi tới đích.
   - Từng bước di chuyển.
   - Số trạng thái đã duyệt.
   - Số trạng thái đã sinh.
   - Thời gian chạy.
   - Độ dài lời giải.
5. Có chế độ visualization để xem thuật toán hoạt động.
6. Có dữ liệu level bằng JSON để dễ thêm màn.
7. Có tài liệu báo cáo đi kèm để giải thích state, action, goal test, cost, heuristic, visited, frontier.

---

## 2. Phạm vi trò chơi

### 2.1. Bàn cờ

Bàn cờ là lưới **4×4**.

Quy ước tọa độ dùng trong code:

```text
(0,0) (0,1) (0,2) (0,3)
(1,0) (1,1) (1,2) (1,3)
(2,0) (2,1) (2,2) (2,3)
(3,0) (3,1) (3,2) (3,3)
```

Các lỗ cố định:

```python
HOLES = {(0, 2), (1, 0), (2, 1), (3, 3)}
```

### 2.2. Tài nguyên trò chơi

Các mảnh chính:

| ID | Loại | Vai trò |
|---|---|---|
| brown | Sóc nâu | Có hạt dẻ |
| black | Sóc đen | Có hạt dẻ |
| white | Sóc trắng | Có hạt dẻ |
| orange | Sóc cam | Có hạt dẻ |
| flower | Mảnh hoa đỏ | Mảnh cản, không có hạt |

Điều kiện thắng:

```text
4 hạt dẻ của 4 con sóc đều rơi xuống 4 lỗ.
```

Không cần tính mảnh hoa đỏ là hạt dẻ.

---

## 3. Mô hình hóa bài toán AI

### 3.1. State

Một trạng thái cần lưu:

1. Vị trí anchor của từng mảnh.
2. Trạng thái hạt dẻ của từng con sóc: còn hay đã rơi.
3. Không lưu hình ảnh, màu sắc, animation trong state AI.

Dạng state đề xuất:

```python
state = (
    ("brown", row, col, has_nut),
    ("black", row, col, has_nut),
    ("white", row, col, has_nut),
    ("orange", row, col, has_nut),
    ("flower", row, col)
)
```

Lý do dùng tuple:

- Hash được.
- Đưa vào `visited` được.
- So sánh trạng thái nhanh.
- Phù hợp với BFS, DFS, A*, Greedy, AND-OR, Belief Search.

### 3.2. Action

Ở 8-puzzle thường nói là di chuyển ô trống.  
Ở trò này, action sẽ là:

```text
Move(piece_id, direction)
```

Ví dụ:

```text
Move("white", "RIGHT")
Move("black", "DOWN")
Move("flower", "LEFT")
Move("brown", "UP")
```

Bốn hướng:

```python
DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}
```

### 3.3. Transition Model

Hàm chuyển trạng thái:

```python
next_state = apply_action(current_state, action)
```

Điều kiện action hợp lệ:

1. Mảnh không vượt ra ngoài bàn 4×4.
2. Mảnh không đè lên mảnh khác.
3. Mảnh trượt nguyên khối.
4. Không xoay mảnh.
5. Không nhấc mảnh.
6. Nếu hạt dẻ đi vào lỗ thì `has_nut = False`.

### 3.4. Goal Test

```python
def is_goal(state):
    return all(piece.has_nut == False for piece in squirrels)
```

Nói cách khác:

```text
Goal = brown_has_nut == False
    and black_has_nut == False
    and white_has_nut == False
    and orange_has_nut == False
```

### 3.5. Path Cost

Mỗi lần trượt một miếng tính là 1 bước.

```python
cost(action) = 1
```

Tổng chi phí:

```python
g(n) = số bước đã đi từ trạng thái đầu đến trạng thái hiện tại
```

---

## 4. Danh sách thuật toán cần code

Dự án sẽ code **tất cả nhóm đã chọn**, mỗi nhóm có ít nhất 2 thuật toán.

### 4.1. Nhóm 1: Uninformed Search

| Thuật toán | Vai trò |
|---|---|
| Breadth-First Search | Tìm lời giải ngắn nhất nếu mỗi bước có cost = 1 |
| Depth-First Search | So sánh với BFS, dễ đi sâu vào nhánh sai |

#### 4.1.1. BFS

BFS dùng queue.

Đầu vào:

```python
start_state
```

Đầu ra:

```python
solution_path
stats
```

Thống kê cần trả về:

```python
{
    "algorithm": "BFS",
    "solved": True,
    "solution_length": 14,
    "visited_count": 382,
    "generated_count": 710,
    "time": 0.04
}
```

Pseudo:

```text
BFS(start):
    frontier = queue(start)
    visited = {start}
    parent = {}

    while frontier not empty:
        current = pop_front(frontier)

        if is_goal(current):
            return reconstruct_path(parent, current)

        for action in legal_actions(current):
            next_state = apply_action(current, action)

            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = (current, action)
                push_back(frontier, next_state)

    return failure
```

#### 4.1.2. DFS

DFS dùng stack.

Cần có:

- `visited`
- `depth_limit` tùy chọn
- chống lặp trạng thái

DFS không đảm bảo tối ưu số bước nhưng dùng để so sánh.

---

### 4.2. Nhóm 2: Informed Search

| Thuật toán | Vai trò |
|---|---|
| Greedy Best-First Search | Chỉ dùng h(n), chạy nhanh nhưng không đảm bảo tối ưu |
| A* Search | Dùng f(n) = g(n) + h(n), cân bằng giữa độ ngắn và độ gần goal |

#### 4.2.1. Heuristic chung

Heuristic chính:

```text
h(n) = tổng khoảng cách Manhattan từ mỗi hạt chưa rơi đến lỗ gần nhất
```

Công thức Manhattan:

```python
def manhattan(a, b):
    return abs(a.row - b.row) + abs(a.col - b.col)
```

Heuristic:

```python
def heuristic(state):
    total = 0
    for squirrel in squirrels:
        if squirrel.has_nut:
            nut_pos = get_nut_position(squirrel)
            nearest = min(manhattan(nut_pos, hole) for hole in HOLES)
            total += nearest
    return total
```

Có thể nâng cấp thêm:

```text
h2(n) = số hạt còn chưa rơi
h3(n) = h_manhattan + penalty nếu miếng bị chặn
```

#### 4.2.2. Greedy Best-First Search

Ưu tiên node có `h(n)` nhỏ nhất.

```text
f(n) = h(n)
```

Ưu điểm:

- Dễ giải thích.
- Chạy nhanh.

Nhược điểm:

- Có thể đi sai vì chỉ nhìn gần goal trước mắt.

#### 4.2.3. A* Search

Ưu tiên node có:

```text
f(n) = g(n) + h(n)
```

Trong đó:

- `g(n)` là số bước đã đi.
- `h(n)` là ước lượng còn lại.

A* là thuật toán nên dùng làm solver chính trong giao diện.

---

### 4.3. Nhóm 3: Local Search

| Thuật toán | Vai trò |
|---|---|
| Hill Climbing | Luôn chọn trạng thái tốt hơn gần nhất |
| Simulated Annealing | Cho phép đi xấu tạm thời để thoát kẹt |

Local Search phù hợp để minh họa việc thuật toán có thể kẹt local optimum.

#### 4.3.1. Hill Climbing

Hàm đánh giá:

```text
value(state) = -heuristic(state)
```

Hoặc dùng cost:

```text
cost(state) = heuristic(state)
```

Mỗi bước:

1. Sinh các trạng thái lân cận.
2. Chọn trạng thái có heuristic nhỏ nhất.
3. Nếu không có trạng thái tốt hơn thì dừng.

Kết quả có thể:

- Thành công.
- Kẹt tại local optimum.
- Kẹt tại plateau.

#### 4.3.2. Simulated Annealing

Khác Hill Climbing ở chỗ:

- Nếu trạng thái mới tốt hơn thì nhận.
- Nếu trạng thái mới xấu hơn thì vẫn có xác suất nhận.
- Xác suất nhận giảm dần theo nhiệt độ `T`.

Công thức:

```text
P = exp((current_value - next_value) / T)
```

Lưu ý triển khai:

- Có `temperature`.
- Có `cooling_rate`.
- Có `max_iterations`.

---

### 4.4. Nhóm 4: Constraint Satisfaction Problem

Trò chơi gốc là state-space puzzle, nhưng vẫn có thể mô hình hóa CSP ở chế độ học thuật.

| Thuật toán | Vai trò |
|---|---|
| Backtracking Search | Tìm chuỗi hành động hợp lệ theo độ sâu |
| Min-Conflicts | Tối ưu chuỗi hành động bằng cách giảm vi phạm |

#### 4.4.1. Cách mô hình CSP

Biến:

```text
X1, X2, X3, ..., Xk
```

Trong đó `Xi` là hành động ở bước thứ i.

Miền giá trị:

```text
Domain(Xi) = tất cả action có dạng Move(piece, direction)
```

Ràng buộc:

1. Action phải hợp lệ tại state hiện tại.
2. State sau action không trùng state trước đó.
3. Không vượt bàn.
4. Không đè mảnh.
5. Sau k bước phải đạt goal.

#### 4.4.2. Backtracking Search

Backtracking sẽ thử từng action cho từng bước.

Nếu action gây lỗi hoặc lặp trạng thái thì quay lui.

Ứng dụng:

- Dùng để tìm lời giải trong giới hạn độ sâu `k`.
- Tương tự depth-limited search nhưng trình bày dưới dạng CSP.

#### 4.4.3. Min-Conflicts

Mô hình chuỗi hành động độ dài k.

Conflict score:

```text
conflict = số lỗi trong chuỗi hành động
         + số hạt chưa rơi
         + số lần lặp state
         + số action không hợp lệ
```

Mỗi vòng:

1. Chọn một biến/action đang gây conflict.
2. Thay bằng action khác làm giảm conflict nhiều nhất.
3. Lặp đến khi conflict = 0 hoặc hết số vòng.

---

### 4.5. Nhóm 5: Adversarial Search

Trò Squirrels Go Nuts gốc không có đối thủ, nên nhóm này sẽ được triển khai trong **Adversarial Demo Mode** để đáp ứng yêu cầu môn học.

| Thuật toán | Vai trò |
|---|---|
| Minimax | MAX cố giải nhanh, MIN cố làm chậm |
| Alpha-Beta Pruning | Tối ưu Minimax bằng cắt tỉa nhánh không cần xét |

#### 4.5.1. Cách chuyển thành game đối kháng

Tạo chế độ:

```text
Solver vs Blocker
```

- MAX: chọn nước đi giúp hạt gần lỗ hơn.
- MIN: chọn nước đi làm tăng heuristic hoặc làm chậm MAX.
- Đối tượng MIN có thể điều khiển mảnh `flower`, hoặc chọn một trong các nhiễu hợp lệ.

Cách đơn giản để code:

```text
MAX turn: chọn action cho các mảnh sóc.
MIN turn: chọn action cho flower hoặc chọn trạng thái bất lợi nhất từ các hậu quả có thể xảy ra.
```

Utility:

```text
utility(state) = -heuristic(state) - steps_penalty
```

Nếu goal:

```text
utility = +1000
```

Nếu quá depth mà chưa goal:

```text
utility = -heuristic(state)
```

#### 4.5.2. Minimax

Dùng depth giới hạn:

```python
best_action = minimax(state, depth=4, maximizing=True)
```

#### 4.5.3. Alpha-Beta

Tối ưu Minimax bằng hai biến:

```python
alpha
beta
```

Mục tiêu:

- Cho cùng kết quả với Minimax.
- Duyệt ít node hơn.
- Có số liệu so sánh trong UI.

---

### 4.6. Nhóm 6: AND-OR / Belief-State Search

Nhóm này dùng cho chế độ mở rộng **Complex Environment Mode**.

| Thuật toán | Vai trò |
|---|---|
| AND-OR Graph Search | Xử lý hành động không xác định |
| Belief-State Search | Xử lý quan sát không đầy đủ |

#### 4.6.1. AND-OR Graph Search

Tạo chế độ nondeterministic:

```text
Khi trượt một miếng, có thể:
1. Đi đúng 1 ô.
2. Trượt lệch hoặc đứng yên.
3. Trượt thêm 1 ô nếu đường trống.
```

Khi đó một action có nhiều kết quả.

Ví dụ:

```text
Move(white, RIGHT)
├── Result 1: white đi phải 1 ô
├── Result 2: white đứng yên
└── Result 3: white đi phải 2 ô nếu hợp lệ
```

- OR node: agent chọn action.
- AND node: tất cả kết quả của action đều phải có kế hoạch xử lý.

#### 4.6.2. Belief-State Search

Tạo chế độ partial observable:

```text
Người chơi/agent không biết chính xác một số mảnh đang ở đâu.
```

Belief state là tập các trạng thái có thể:

```python
belief_state = {state1, state2, state3, ...}
```

Action áp dụng lên toàn bộ belief state.

Goal:

```text
Tất cả state trong belief_state đều đạt goal.
```

Đây là phần mở rộng học thuật, không cần là solver chính của game gốc.

---

## 5. Kiến trúc thư mục dự án

Cấu trúc đề xuất:

```text
squirrels_ai_solver/
│
├── main.py
├── requirements.txt
├── README.md
│
├── assets/
│   ├── images/
│   │   ├── board/
│   │   │   ├── board_bg.png
│   │   │   ├── hole.png
│   │   │   └── cell_highlight.png
│   │   ├── pieces/
│   │   │   ├── brown_squirrel.png
│   │   │   ├── black_squirrel.png
│   │   │   ├── white_squirrel.png
│   │   │   ├── orange_squirrel.png
│   │   │   └── flower.png
│   │   ├── ui/
│   │   │   ├── button.png
│   │   │   ├── panel.png
│   │   │   └── logo.png
│   │   └── effects/
│   │       ├── acorn.png
│   │       ├── sparkle.png
│   │       └── arrow.png
│   │
│   ├── sounds/
│   │   ├── move.wav
│   │   ├── drop.wav
│   │   ├── click.wav
│   │   ├── solve.wav
│   │   └── win.wav
│   │
│   └── fonts/
│       └── README_fonts.md
│
├── data/
│   ├── levels.json
│   ├── themes.json
│   └── algorithm_config.json
│
├── core/
│   ├── __init__.py
│   ├── constants.py
│   ├── piece.py
│   ├── board.py
│   ├── state.py
│   ├── move.py
│   ├── rules.py
│   └── level.py
│
├── ai/
│   ├── __init__.py
│   ├── search_result.py
│   ├── uninformed/
│   │   ├── bfs.py
│   │   └── dfs.py
│   ├── informed/
│   │   ├── greedy.py
│   │   ├── astar.py
│   │   └── heuristics.py
│   ├── local_search/
│   │   ├── hill_climbing.py
│   │   └── simulated_annealing.py
│   ├── csp/
│   │   ├── backtracking.py
│   │   └── min_conflicts.py
│   ├── adversarial/
│   │   ├── minimax.py
│   │   └── alpha_beta.py
│   └── complex/
│       ├── and_or_search.py
│       └── belief_state_search.py
│
├── ui/
│   ├── __init__.py
│   ├── app.py
│   ├── theme.py
│   ├── screen_manager.py
│   ├── screens/
│   │   ├── main_menu.py
│   │   ├── level_select.py
│   │   ├── game_screen.py
│   │   ├── algorithm_screen.py
│   │   ├── report_screen.py
│   │   └── settings_screen.py
│   ├── components/
│   │   ├── button.py
│   │   ├── panel.py
│   │   ├── dropdown.py
│   │   ├── slider.py
│   │   ├── toast.py
│   │   └── modal.py
│   ├── renderers/
│   │   ├── board_renderer.py
│   │   ├── piece_renderer.py
│   │   ├── path_renderer.py
│   │   └── graph_renderer.py
│   └── animations/
│       ├── tween.py
│       ├── move_animation.py
│       ├── drop_animation.py
│       └── win_animation.py
│
├── utils/
│   ├── file_loader.py
│   ├── timer.py
│   ├── logger.py
│   ├── profiler.py
│   └── math_utils.py
│
└── docs/
    ├── ke_hoach_du_an.md
    ├── mo_hinh_bai_toan.md
    ├── thuat_toan.md
    ├── huong_dan_chay.md
    └── bao_cao_tom_tat.md
```

---

## 6. Thiết kế dữ liệu level JSON

File:

```text
data/levels.json
```

Mẫu:

```json
{
  "starter": [
    {
      "id": "starter_01",
      "name": "Starter 01",
      "difficulty": "Starter",
      "holes": [[0, 2], [1, 0], [2, 1], [3, 3]],
      "pieces": [
        {
          "id": "brown",
          "type": "squirrel",
          "shape": [[0, 0], [1, 0], [1, 1]],
          "anchor": [0, 0],
          "nut_offset": [1, 1],
          "has_nut": true
        },
        {
          "id": "black",
          "type": "squirrel",
          "shape": [[0, 0], [0, 1], [1, 1]],
          "anchor": [1, 2],
          "nut_offset": [0, 0],
          "has_nut": true
        },
        {
          "id": "white",
          "type": "squirrel",
          "shape": [[0, 0], [0, 1]],
          "anchor": [2, 0],
          "nut_offset": [0, 1],
          "has_nut": true
        },
        {
          "id": "orange",
          "type": "squirrel",
          "shape": [[0, 0], [1, 0]],
          "anchor": [2, 3],
          "nut_offset": [0, 0],
          "has_nut": true
        },
        {
          "id": "flower",
          "type": "block",
          "shape": [[0, 0]],
          "anchor": [0, 3]
        }
      ]
    }
  ],
  "junior": [],
  "expert": []
}
```

Mỗi level cần validate khi load:

1. Không có mảnh nào ra ngoài bàn.
2. Không có hai mảnh đè nhau.
3. Có đúng 4 hạt dẻ.
4. Có đúng 4 lỗ.
5. Các shape hợp lệ.
6. Mỗi `piece_id` là duy nhất.

---

## 7. Thiết kế UI/UX

### 7.1. Kích thước cửa sổ

Đề xuất:

```text
1280 × 720
```

Lý do:

- Phù hợp màn laptop.
- Có đủ không gian cho bàn cờ, panel thuật toán, danh sách bước.
- Dễ quay video demo.

### 7.2. Layout màn chơi

```text
+--------------------------------------------------------------+
| SQUIRRELS GO NUTS - AI SOLVER                                |
+------------------------------+-------------------------------+
|                              | Level: Starter 01             |
|                              | Algorithm: A*                 |
|                              | Status: Solved                |
|          BOARD 4×4           | Steps: 14                     |
|                              | Visited: 382                  |
|                              | Generated: 710                |
|                              | Time: 0.04s                   |
|                              |                               |
|                              | Path:                         |
|                              | 1. White RIGHT                |
|                              | 2. Flower DOWN                |
|                              | 3. Brown LEFT                 |
+------------------------------+-------------------------------+
| Reset | Undo | Hint | Solve | Next | Auto | Visualize | Menu |
+--------------------------------------------------------------+
```

### 7.3. Màn hình chính

Menu chính gồm:

```text
PLAY
AI SOLVER
ALGORITHM VISUALIZER
LEVEL SELECT
REPORT
SETTINGS
QUIT
```

### 7.4. Màn chọn level

Chia tab:

```text
Starter | Junior | Expert
```

Mỗi level hiển thị dạng card:

```text
Starter 01
Best Steps: 12
Solved by: A*
[Play]
```

### 7.5. Màn Algorithm Visualizer

Mục tiêu:

- Hiển thị thuật toán đang chạy.
- Hiển thị current state.
- Hiển thị frontier.
- Hiển thị visited.
- Hiển thị path tìm được.

Bố cục:

```text
Left: Board hiện tại
Center: Search tree / Queue / Stack
Right: Stats + pseudocode
Bottom: Step control
```

Nút điều khiển:

```text
Start
Pause
Step
Speed -
Speed +
Reset
```

### 7.6. Trạng thái nút

Mỗi nút cần có 4 trạng thái:

1. Normal
2. Hover
3. Pressed
4. Disabled

### 7.7. Feedback người dùng

Cần có:

- Âm thanh click.
- Hiệu ứng hover.
- Toast khi move sai.
- Highlight miếng đang chọn.
- Highlight ô có thể đi.
- Popup khi thắng.
- Progress spinner khi AI đang solve.

Ví dụ toast:

```text
"Move không hợp lệ: mảnh bị chặn!"
```

---

## 8. Thiết kế animation

### 8.1. Move animation

Khi miếng trượt:

```text
duration = 0.15s đến 0.25s
```

Dùng easing:

```python
def ease_out_quad(t):
    return 1 - (1 - t) * (1 - t)
```

### 8.2. Drop animation

Khi hạt rơi vào lỗ:

1. Hạt dẻ rung nhẹ.
2. Scale nhỏ dần.
3. Alpha giảm.
4. Phát âm thanh drop.
5. Lỗ sáng nhẹ.

### 8.3. Path animation

Khi AI hiển thị lời giải:

- Mũi tên chỉ hướng di chuyển.
- Miếng vừa đi được viền sáng.
- Danh sách bước tự scroll.
- Bước hiện tại được highlight.

### 8.4. Win animation

Khi giải xong:

- Popup `Solved!`
- Hiển thị số bước.
- Hiển thị thuật toán.
- Hiển thị thời gian.
- Có nút `Replay Solution`.

---

## 9. Thiết kế luồng sử dụng

### 9.1. Người chơi tự chơi

```text
Main Menu
→ Play
→ Chọn level
→ Click chọn miếng
→ Bấm phím mũi tên
→ Nếu move hợp lệ: miếng trượt
→ Nếu hạt vào lỗ: hạt rơi
→ Nếu đủ 4 hạt: win popup
```

### 9.2. AI tự giải

```text
Main Menu
→ AI Solver
→ Chọn level
→ Chọn thuật toán
→ Bấm Solve
→ Hiện loading
→ Solver trả về path
→ Hiện thống kê
→ Bấm Auto để xem AI giải
```

### 9.3. Visualization

```text
Main Menu
→ Algorithm Visualizer
→ Chọn thuật toán
→ Bấm Start
→ Mỗi lần bấm Step:
    - Hiện state đang xét
    - Cập nhật frontier
    - Cập nhật visited
    - Cập nhật pseudocode line hiện tại
```

---

## 10. Các class chính

### 10.1. Piece

```python
class Piece:
    def __init__(self, id, type, shape, anchor, nut_offset=None, has_nut=False):
        self.id = id
        self.type = type
        self.shape = shape
        self.anchor = anchor
        self.nut_offset = nut_offset
        self.has_nut = has_nut

    def occupied_cells(self):
        pass

    def nut_position(self):
        pass
```

### 10.2. GameState

```python
class GameState:
    def __init__(self, pieces, holes):
        self.pieces = pieces
        self.holes = holes

    def encode(self):
        pass

    def clone(self):
        pass

    def is_goal(self):
        pass
```

### 10.3. BoardRules

```python
class BoardRules:
    def legal_actions(self, state):
        pass

    def can_move(self, state, piece_id, direction):
        pass

    def apply_action(self, state, action):
        pass

    def check_nut_drop(self, state):
        pass
```

### 10.4. SearchResult

```python
class SearchResult:
    def __init__(
        self,
        algorithm,
        solved,
        path,
        visited_count,
        generated_count,
        elapsed_time,
        extra=None
    ):
        self.algorithm = algorithm
        self.solved = solved
        self.path = path
        self.visited_count = visited_count
        self.generated_count = generated_count
        self.elapsed_time = elapsed_time
        self.extra = extra or {}
```

### 10.5. Algorithm Interface

Tất cả thuật toán nên dùng chung interface:

```python
class Solver:
    def solve(self, start_state, rules, config=None):
        raise NotImplementedError
```

Mục tiêu:

- UI gọi thuật toán nào cũng giống nhau.
- Dễ thêm thuật toán mới.
- Dễ thống kê và so sánh.

---

## 11. Chống lỗi và chống chạy vô hạn

Bắt buộc có `visited`.

Với thuật toán dạng graph search:

```python
visited = set()
```

Mỗi state được mã hóa:

```python
key = state.encode()
```

Nếu đã gặp:

```python
if key in visited:
    continue
```

Với DFS cần thêm:

```python
depth_limit
max_nodes
timeout
```

Với local search cần thêm:

```python
max_iterations
restart_count
```

Với minimax cần thêm:

```python
depth_limit
```

Với AND-OR cần thêm:

```python
cycle_check
```

Với belief-state cần thêm:

```python
max_belief_size
```

---

## 12. So sánh thuật toán trong UI

Sau khi chạy nhiều thuật toán trên cùng level, hiển thị bảng:

| Algorithm | Solved | Steps | Visited | Generated | Time |
|---|---:|---:|---:|---:|---:|
| BFS | Yes | 14 | 382 | 710 | 0.04s |
| DFS | Yes | 31 | 95 | 180 | 0.02s |
| Greedy | Yes | 18 | 60 | 130 | 0.01s |
| A* | Yes | 14 | 96 | 210 | 0.01s |
| Hill Climbing | No | - | 22 | 44 | 0.01s |
| Simulated Annealing | Yes | 25 | 130 | 250 | 0.03s |

Có nút:

```text
Run All Algorithms
```

Mục tiêu:

- Tạo dữ liệu cho báo cáo.
- Dễ chứng minh A* hiệu quả hơn BFS.
- Dễ chứng minh DFS/Hill Climbing không ổn định.

---

## 13. Báo cáo tích hợp trong app

Màn `Report` trong app nên có:

1. Mô hình bài toán.
2. Bảng thuật toán.
3. Kết quả thực nghiệm.
4. Biểu đồ đơn giản:
   - Steps
   - Visited states
   - Time
5. Kết luận.

Có thể xuất CSV:

```text
results/algorithm_results.csv
```

Format:

```csv
level,algorithm,solved,steps,visited,generated,time
starter_01,A*,true,14,96,210,0.01
starter_01,BFS,true,14,382,710,0.04
```

---

## 14. Lộ trình 1 tuần

### Ngày 1: Core logic

Mục tiêu:

- Tạo project structure.
- Code Piece, State, BoardRules.
- Load level từ JSON.
- Sinh legal actions.
- Apply action.
- Check goal.
- Check nut drop.

Checklist:

```text
[ ] Tạo thư mục dự án
[ ] Tạo requirements.txt
[ ] Tạo levels.json mẫu
[ ] Code Piece
[ ] Code GameState
[ ] Code BoardRules
[ ] Code legal_actions()
[ ] Code apply_action()
[ ] Code is_goal()
[ ] Test bằng console
```

Kết quả cuối ngày:

```text
Chạy được logic game không cần UI.
In ra legal moves và state sau khi move.
```

---

### Ngày 2: Uninformed + Informed Search

Mục tiêu:

- Code BFS.
- Code DFS.
- Code Greedy.
- Code A*.
- Code heuristic.
- Trả về SearchResult chuẩn.

Checklist:

```text
[ ] bfs.py
[ ] dfs.py
[ ] heuristics.py
[ ] greedy.py
[ ] astar.py
[ ] reconstruct_path()
[ ] visited set
[ ] parent map
[ ] priority queue cho A*
[ ] thống kê visited/generated/time
```

Kết quả cuối ngày:

```text
Console chạy được:
python main.py --level starter_01 --algorithm astar
```

---

### Ngày 3: Các nhóm thuật toán còn lại

Mục tiêu:

- Code Hill Climbing.
- Code Simulated Annealing.
- Code CSP Backtracking.
- Code Min-Conflicts.
- Code Minimax.
- Code Alpha-Beta.
- Code khung AND-OR và Belief-State.

Checklist:

```text
[ ] hill_climbing.py
[ ] simulated_annealing.py
[ ] backtracking.py
[ ] min_conflicts.py
[ ] minimax.py
[ ] alpha_beta.py
[ ] and_or_search.py
[ ] belief_state_search.py
[ ] thống nhất SearchResult
[ ] test mỗi thuật toán ít nhất 1 level
```

Kết quả cuối ngày:

```text
Có thể chạy tất cả thuật toán bằng console và nhận bảng so sánh.
```

---

### Ngày 4: UI Pygame cơ bản

Mục tiêu:

- Tạo cửa sổ Pygame.
- Vẽ menu.
- Vẽ board.
- Vẽ mảnh.
- Click chọn miếng.
- Di chuyển bằng phím mũi tên.
- Reset và Undo.

Checklist:

```text
[ ] Pygame app loop
[ ] ScreenManager
[ ] MainMenuScreen
[ ] LevelSelectScreen
[ ] GameScreen
[ ] BoardRenderer
[ ] PieceRenderer
[ ] Button component
[ ] Click chọn piece
[ ] Arrow key movement
[ ] Reset
[ ] Undo
[ ] Win popup
```

Kết quả cuối ngày:

```text
Người chơi tự chơi được một level bằng giao diện.
```

---

### Ngày 5: Gắn AI Solver vào UI

Mục tiêu:

- Chọn thuật toán trong UI.
- Bấm Solve để AI giải.
- Hiển thị path.
- Bấm Next Step để chạy từng bước.
- Bấm Auto Play để AI tự chạy.
- Hiển thị stats.

Checklist:

```text
[ ] Algorithm dropdown
[ ] Solve button
[ ] Next Step button
[ ] Auto Play button
[ ] Path panel
[ ] Stats panel
[ ] Loading state
[ ] Run All Algorithms
[ ] Algorithm comparison table
```

Kết quả cuối ngày:

```text
App có thể chọn A*, BFS, DFS... rồi xem từng bước giải.
```

---

### Ngày 6: UI/UX đẹp và mượt

Mục tiêu:

- Thêm animation.
- Thêm hiệu ứng hover.
- Thêm âm thanh.
- Thêm highlight.
- Thêm Algorithm Visualizer.
- Làm giao diện giống app hoàn chỉnh.

Checklist:

```text
[ ] Move animation
[ ] Drop animation
[ ] Win animation
[ ] Button hover
[ ] Toast message
[ ] Highlight selected piece
[ ] Highlight legal moves
[ ] Path arrow
[ ] Frontier/visited visualization
[ ] Pseudocode panel
[ ] Speed control
[ ] Theme màu cartoon/vector
```

Kết quả cuối ngày:

```text
Giao diện mượt, dễ dùng, có trải nghiệm tốt.
```

---

### Ngày 7: Test, đóng gói, tài liệu, demo

Mục tiêu:

- Fix bug.
- Thêm nhiều level.
- Viết README.
- Viết báo cáo tóm tắt.
- Quay demo.
- Đóng gói.

Checklist:

```text
[ ] Test tất cả thuật toán
[ ] Test tất cả level
[ ] Test undo/reset/solve/autoplay
[ ] Test không lặp vô hạn
[ ] Viết README.md
[ ] Viết docs/bao_cao_tom_tat.md
[ ] Xuất CSV kết quả
[ ] Quay video demo
[ ] Đóng gói bằng PyInstaller
```

Lệnh đóng gói:

```bash
pyinstaller --onefile --windowed main.py
```

Kết quả cuối ngày:

```text
Có bản demo hoàn chỉnh để nộp và thuyết trình.
```

---

## 15. Thứ tự ưu tiên khi code

Không code UI trước. Thứ tự đúng:

```text
1. Core logic
2. BFS/A*
3. Các thuật toán còn lại
4. UI cơ bản
5. Gắn solver vào UI
6. Animation
7. Visualization
8. Báo cáo + đóng gói
```

Lý do:

- Nếu logic sai, UI đẹp cũng vô dụng.
- Solver chạy đúng thì giao diện chỉ là lớp trình bày.
- Dễ debug hơn.

---

## 16. Tiêu chí hoàn thành

### 16.1. Bắt buộc

```text
[ ] Có thể chơi bằng click + phím mũi tên
[ ] Có chọn level Starter/Junior/Expert
[ ] Có BFS
[ ] Có DFS
[ ] Có Greedy
[ ] Có A*
[ ] Có Hill Climbing
[ ] Có Simulated Annealing
[ ] Có Backtracking
[ ] Có Min-Conflicts
[ ] Có Minimax
[ ] Có Alpha-Beta
[ ] Có AND-OR Search
[ ] Có Belief-State Search
[ ] Có visited để chống lặp
[ ] Có hiển thị đường đi tới đích
[ ] Có thống kê thuật toán
[ ] Có giao diện đẹp, mượt
```

### 16.2. Nâng cao

```text
[ ] Có animation hạt rơi
[ ] Có animation miếng trượt
[ ] Có sound effect
[ ] Có bảng so sánh thuật toán
[ ] Có export CSV
[ ] Có pseudocode highlight
[ ] Có search tree/frontier visualization
[ ] Có replay solution
[ ] Có PyInstaller build
```

---

## 17. Rủi ro và cách xử lý

### Rủi ro 1: Code tất cả thuật toán trong 1 tuần bị quá tải

Cách xử lý:

- Ưu tiên solver chính: BFS, DFS, Greedy, A*.
- Các nhóm khó như AND-OR, Belief-State, Minimax có thể làm chế độ demo học thuật.
- Vẫn code đủ file và interface, nhưng visualization có thể đơn giản hơn.

### Rủi ro 2: Minimax không tự nhiên với game gốc

Cách xử lý:

- Tạo riêng `Adversarial Demo Mode`.
- Giải thích rõ trong báo cáo: game gốc là single-agent puzzle, adversarial search là phiên bản mở rộng để minh họa thuật toán.

### Rủi ro 3: CSP khó ra lời giải tối ưu

Cách xử lý:

- Dùng CSP như tìm kiếm chuỗi hành động có giới hạn độ sâu.
- Với mỗi độ sâu k, thử tìm chuỗi action hợp lệ.
- Nếu không ra thì tăng k.

### Rủi ro 4: UI làm mất nhiều thời gian

Cách xử lý:

- Ngày 4 chỉ làm UI cơ bản.
- Ngày 6 mới làm đẹp.
- Không để animation làm hỏng logic.

### Rủi ro 5: State bị encode sai

Cách xử lý:

- Viết test cho `encode()`.
- In state sau mỗi move.
- So sánh occupied cells.
- Dùng `visited` bằng tuple chuẩn hóa theo thứ tự piece_id.

---

## 18. Nội dung báo cáo nên viết

Báo cáo có thể đi theo bố cục:

```text
1. Giới thiệu đề tài
2. Giới thiệu trò chơi Squirrels Go Nuts
3. Mô hình hóa bài toán
   3.1 State
   3.2 Action
   3.3 Transition Model
   3.4 Goal Test
   3.5 Path Cost
4. Các nhóm thuật toán áp dụng
   4.1 Uninformed Search: BFS, DFS
   4.2 Informed Search: Greedy, A*
   4.3 Local Search: Hill Climbing, Simulated Annealing
   4.4 CSP: Backtracking, Min-Conflicts
   4.5 Adversarial Search: Minimax, Alpha-Beta
   4.6 Complex Environment: AND-OR, Belief-State
5. Thiết kế chương trình
6. Thiết kế giao diện
7. Kết quả thực nghiệm
8. So sánh thuật toán
9. Kết luận
```

Câu mô tả cốt lõi:

> Trò chơi Squirrels Go Nuts được mô hình hóa thành bài toán tìm kiếm trong không gian trạng thái. Mỗi trạng thái biểu diễn vị trí của các miếng ghép và tình trạng hạt dẻ. Mỗi hành động là việc chọn một miếng ghép và trượt nó theo một trong bốn hướng. Mục tiêu là đưa bốn hạt dẻ rơi vào bốn lỗ trên bàn cờ. Dự án triển khai nhiều nhóm thuật toán tìm kiếm nhằm so sánh hiệu quả giải bài toán, bao gồm BFS, DFS, Greedy Best-First Search, A*, Hill Climbing, Simulated Annealing, Backtracking, Min-Conflicts, Minimax, Alpha-Beta, AND-OR Search và Belief-State Search.

---

## 19. Kết luận hướng triển khai

Hướng triển khai cuối cùng:

```text
Python + Pygame
→ Core game logic
→ AI solver nhiều nhóm thuật toán
→ UI game đẹp, mượt
→ Visualization thuật toán
→ Level JSON
→ Báo cáo + demo
```

Điểm mạnh của đề tài:

1. Không nhàm chán như 8-puzzle.
2. Vẫn bám sát kiến thức AI search.
3. Có nhiều thuật toán để so sánh.
4. Có giao diện đẹp để thuyết trình.
5. Có thể mở rộng thêm level và chế độ chơi.
6. Có tính thực tế vì mô phỏng một board game thật.

---

## 20. Checklist nộp cuối cùng

```text
[ ] Source code đầy đủ
[ ] requirements.txt
[ ] README.md
[ ] data/levels.json
[ ] assets cartoon/vector
[ ] docs/ke_hoach_du_an.md
[ ] docs/bao_cao_tom_tat.md
[ ] Video demo
[ ] Bảng so sánh thuật toán
[ ] File chạy hoặc hướng dẫn chạy
```
