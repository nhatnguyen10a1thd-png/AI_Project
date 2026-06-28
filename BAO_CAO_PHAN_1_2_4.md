# PHẦN I. BÀI TOÁN ĐẶT RA

## 1.1. Bài toán gì?

Squirrels AI Solver là project Python/Pygame mô phỏng logic của trò chơi Squirrels Go Nuts và dùng các thuật toán Trí tuệ nhân tạo để tìm lời giải cho từng level. Mục tiêu của bài toán là tìm một chuỗi hành động đưa tất cả hạt của các con sóc xuất hiện trong level vào các lỗ trên bàn cờ. Trong source code hiện tại, bài toán được mô hình hóa thành bài toán tìm kiếm trong không gian trạng thái: mỗi trạng thái là một cấu hình bàn cờ gồm vị trí các mảnh, trạng thái còn hay đã rơi của hạt, tập lỗ trên bàn và tập lỗ đã được lấp.

Mỗi hành động trong project là chọn một quân và di chuyển quân đó đúng một ô theo một hướng hợp lệ trong bốn hướng `UP`, `DOWN`, `LEFT`, `RIGHT`. Đây là điểm cần trình bày thống nhất: project rời rạc hóa hành động thành từng bước một ô để thuận tiện cho mô hình tìm kiếm, thay vì mô phỏng luật trượt liên tục tới vật cản. Mô hình chuyển trạng thái clone trạng thái hiện tại, cập nhật anchor của quân được chọn và nếu hạt của sóc nằm đúng trên một lỗ chưa được lấp thì cập nhật `has_nut = False` và thêm tọa độ đó vào `filled_holes`. Goal test là tất cả piece có `type == "squirrel"` trong level đều không còn hạt. Lời giải là chuỗi action từ trạng thái ban đầu tới trạng thái mục tiêu; chi phí mỗi bước có thể xem là 1.

**Bảng 1. Mô hình hóa bài toán Squirrels AI Solver**

| Thành phần | Mô tả trong project |
|---|---|
| State | Object `GameState` gồm `pieces`, `holes`, `filled_holes`; mỗi piece có `id`, `type`, `shape`, `anchor`, `nut_offset`, `has_nut`, `movable`. |
| Initial state | Trạng thái được `LevelManager.create_game_state()` tạo từ `data/book_levels.json`; ví dụ `starter_01` có `orange`, `white`, `flower` và bốn lỗ cố định. |
| Action | Tuple `(piece_id, direction)`, trong đó `direction` thuộc `UP`, `DOWN`, `LEFT`, `RIGHT`; mỗi action dịch một quân đúng một ô nếu hợp lệ. |
| Transition model | `BoardRules.apply_action()` clone state, dịch anchor của piece, kiểm tra hạt rơi vào hole chưa filled và trả về `GameState` mới. |
| Goal test | `GameState.is_goal()` trả `True` khi mọi squirrel trong level đều có `has_nut == False`. |
| Path solution | Danh sách action có thể replay được trên UI, ví dụ `[("orange", "LEFT"), ("white", "UP"), ("white", "UP")]`. |
| Step cost | Mỗi action có cost bằng 1; do đó độ dài path chính là tổng chi phí trong các solver state-space chính. |

## 1.2. PEAS của bài toán

**Bảng 2. PEAS của agent giải Squirrels AI Solver**

| Thành phần | Nội dung |
|---|---|
| Performance Measure | Tìm được goal, số bước lời giải ít, thời gian chạy thấp, số node/state sinh và duyệt hợp lý, path replay được bằng luật deterministic của project. |
| Environment | Bàn cờ 4x4, các mảnh squirrel/block, holes, filled holes; trạng thái chính là fully observable, deterministic, sequential, discrete và static. |
| Actuators | Sinh và thực thi action `(piece_id, direction)` để dịch một quân một ô theo hướng hợp lệ. |
| Sensors | Đọc toàn bộ `GameState`: vị trí anchor, occupied cells, hạt còn hay đã rơi, lỗ nào đã filled, danh sách legal actions qua `BoardRules.legal_actions()`. |

Môi trường chính của project là fully observable vì agent biết toàn bộ cấu hình bàn cờ; deterministic vì một action hợp lệ tạo ra một successor xác định; sequential vì hành động sau phụ thuộc trạng thái trước; discrete vì state, action và time step đều rời rạc; static vì bàn cờ không tự thay đổi trong lúc agent suy nghĩ. Với AND-OR, Belief-State và Expectimax, project mở rộng mô hình để minh họa môi trường không xác định, thiếu quan sát hoặc ngẫu nhiên. Khi đánh giá agent, project ưu tiên khả năng tìm lời giải, độ dài path, thời gian chạy, số trạng thái duyệt/sinh và tính hợp lệ khi replay.

# PHẦN II. THUẬT TOÁN ÁP DỤNG

Dự án triển khai nhiều nhóm thuật toán AI. Trong báo cáo này, nhóm chọn 6 thuật toán đại diện: BFS cho tìm kiếm mù, A* cho tìm kiếm có thông tin, Hill Climbing cho tìm kiếm cục bộ, AND-OR Search cho môi trường phức tạp, AC-3 cho CSP/inference và Alpha-Beta Pruning cho tìm kiếm đối kháng. Bộ thuật toán này cho phép nhìn cùng một puzzle từ nhiều mô hình khác nhau, đồng thời phân biệt rõ solver áp dụng tự nhiên và solver mang tính minh họa học thuật.

## 2.1. Breadth-First Search (BFS)

### 2.1.1. Ý tưởng thuật toán

Breadth-First Search là thuật toán tìm kiếm mù, không dùng heuristic để đánh giá trạng thái. BFS dùng hàng đợi FIFO và mở rộng các node theo từng lớp độ sâu: tất cả node ở độ sâu `d` được xét trước khi chuyển sang độ sâu `d + 1`. Trong không gian trạng thái hữu hạn, BFS complete nếu không bị giới hạn tài nguyên. Khi chi phí mỗi bước bằng nhau, BFS optimal theo số bước vì lời giải đầu tiên ở độ sâu nhỏ nhất là lời giải nông nhất. Hạn chế lớn nhất là tiêu tốn bộ nhớ do phải lưu frontier theo lớp.

### 2.1.2. Ánh xạ vào bài toán

Trong project, BFS nằm ở `ai/uninformed/bfs.py`. Node của BFS là `SearchNode` chứa một `GameState`, action là tuple `(piece_id, direction)`, successor sinh bằng `rules.legal_actions()` và `safe_apply_action()`. BFS dùng `state.encode()` để lưu `explored` và `frontier_encoded`, tránh xét lại trạng thái đã duyệt hoặc đã nằm trong frontier. Thuật toán trả về `SearchResult` gồm `solved`, `path`, `visited_count`, `generated_count`, `elapsed_time`, `steps` và `extra`.

### 2.1.3. Trạng thái ban đầu và mục tiêu

Level mẫu dùng trong báo cáo là `starter_01` trong `data/book_levels.json`. Level này có hai squirrel là `orange`, `white`, một block `flower`, bốn holes và `target_moves = 3`.

**Bảng 3. Trạng thái ban đầu và mục tiêu cho BFS**

| Thành phần | Trạng thái ban đầu | Trạng thái mục tiêu |
|---|---|---|
| Board | Bàn 4x4, holes: `(0,2)`, `(1,0)`, `(2,1)`, `(3,3)`. | Bàn 4x4 giữ nguyên holes. |
| Squirrel `orange` | Cells `(1,1)`, `(1,2)`, nut tại `(1,1)`, `has_nut=True`. | `has_nut=False`, nut đã rơi vào một hole hợp lệ. |
| Squirrel `white` | Cells `(2,2)`, `(3,2)`, nut tại `(2,2)`, `has_nut=True`. | `has_nut=False`, nut đã rơi vào một hole hợp lệ. |
| Block `flower` | Cell `(2,1)`, mặc định không movable. | Không phải goal, chỉ đóng vai trò vật cản. |
| Goal | Chưa đạt vì còn squirrel giữ hạt. | Tất cả squirrel trong level đã thả hạt; với path thực nghiệm, filled holes là `(1,0)` và `(0,2)`. |

### 2.1.4. Các bước tìm solution

Trong lần chạy thực nghiệm trên `starter_01`, BFS tìm được path 3 bước: `orange LEFT`, `white UP`, `white UP`. Số liệu ghi nhận: solved `True`, visited `12`, generated `49`, time khoảng `0.001132s`.

**Bảng 4. Minh họa các bước BFS**

| Bước | Node/trạng thái đang xét | Action | Giá trị đánh giá | Kết quả |
|---:|---|---|---|---|
| 0 | State ban đầu `starter_01` | Khởi tạo | FIFO queue, cost mỗi action = 1 | Frontier có start node. |
| 1 | Pop node depth 0 | Xét legal actions | 4 action hợp lệ | Sinh các child từ `orange UP`, `orange LEFT`, `orange RIGHT`, `white RIGHT`. |
| 2 | Child sau `orange LEFT` | Enqueue | depth = 1, g = 1 | Hạt `orange` rơi vào hole `(1,0)`, state tiến gần goal. |
| 3 | Node ở depth 1 | Xét successors | Bỏ qua state lặp bằng `encode()` | Tiếp tục mở rộng theo lớp. |
| 4 | Child sau `white UP` | Enqueue | depth = 2, g = 2 | `white` tiến gần hole `(0,2)`. |
| 5 | Child sau `white UP` lần hai | Goal check | depth = 3, g = 3 | Tìm goal, reconstruct path 3 bước. |

### 2.1.5. Nhận xét

BFS phù hợp tự nhiên với Squirrels AI Solver vì state/action/goal rõ ràng và step cost bằng 1. Ưu điểm là dễ giải thích, complete trong không gian hữu hạn và tìm lời giải nông nhất nếu không bị giới hạn. Hạn chế là bộ nhớ tăng nhanh khi level khó, do frontier có thể chứa nhiều trạng thái cùng độ sâu.

---

## 2.2. A* Search

### 2.2.1. Ý tưởng thuật toán

A* là thuật toán tìm kiếm có thông tin. Thuật toán dùng hàm đánh giá `f(n)=g(n)+h(n)`, trong đó `g(n)` là chi phí từ start đến node hiện tại, còn `h(n)` là ước lượng chi phí từ node hiện tại đến goal. A* ưu tiên node có `f` nhỏ nhất trong priority queue. Về lý thuyết, A* có tính tối ưu khi heuristic thỏa điều kiện admissible/consistent và thuật toán không bị giới hạn tài nguyên.

### 2.2.2. Ánh xạ vào bài toán

Trong project, A* nằm ở `ai/informed/astar.py`. `g` là số bước đã đi, `h` là `squirrel_heuristic()` trong `ai/informed/heuristics.py`, và `f = g + h`. Heuristic hiện tại trong source code là `min_assignment_manhattan_nuts_to_empty_holes`: ghép các hạt chưa rơi với các lỗ trống riêng biệt sao cho tổng khoảng cách Manhattan là nhỏ nhất. Cách này mạnh hơn việc mỗi hạt độc lập chọn lỗ gần nhất, nhưng vẫn bỏ qua vật cản và hình dạng mảnh, nên chưa được chứng minh admissible/consistent cho mọi cấu hình.

Implementation dùng `heapq`, `g_score`, `closed_g` và hỗ trợ reopen state khi tìm được đường có `g` tốt hơn. Kết quả trả về vẫn là `SearchResult` chuẩn. Vì heuristic chưa có chứng minh hình thức, báo cáo không khẳng định A* luôn tối ưu tuyệt đối; chỉ nói A* tối ưu khi điều kiện heuristic và tài nguyên được thỏa mãn.

### 2.2.3. Trạng thái ban đầu và mục tiêu

**Bảng 5. Trạng thái ban đầu và mục tiêu cho A***

| Thành phần | Trạng thái ban đầu | Trạng thái mục tiêu |
|---|---|---|
| Level | `starter_01`, `target_moves = 3`. | Goal đạt sau path replay hợp lệ. |
| State | `orange` và `white` còn hạt; `flower` cố định tại `(2,1)`. | `orange.has_nut=False`, `white.has_nut=False`. |
| Heuristic ban đầu | `h(start)=2` theo minimum-assignment Manhattan. | `h(goal)=0`. |
| Goal | Chưa đạt vì còn hai hạt. | Tất cả squirrel trong level đã thả hạt. |

### 2.2.4. Các bước tìm solution

Trong lần chạy thực nghiệm, A* tìm cùng path 3 bước với BFS: `orange LEFT`, `white UP`, `white UP`. Số liệu ghi nhận: solved `True`, visited `11`, generated `42`, time khoảng `0.001644s`.

**Bảng 6. Minh họa các bước A***

| Bước | Node/trạng thái đang xét | Action | g | h | f | Kết quả |
|---:|---|---|---:|---:|---:|---|
| 0 | State ban đầu | Khởi tạo | 0 | 2 | 2 | Push start vào priority queue. |
| 1 | Pop node có `f` nhỏ nhất | Mở rộng start | 0 | 2 | 2 | Có 4 action hợp lệ. |
| 2 | Successor `orange UP` | Push frontier | 1 | 2 | 3 | Chưa cải thiện heuristic. |
| 3 | Successor `orange LEFT` | Push frontier | 1 | 1 | 2 | Hạt `orange` rơi, được ưu tiên vì `f` nhỏ. |
| 4 | Pop state sau `orange LEFT` | Mở rộng | 1 | 1 | 2 | Tiếp tục xét các action của `white`. |
| 5 | Sau `white UP`, rồi `white UP` | Goal check | 3 | 0 | 3 | Tìm goal và reconstruct path 3 bước. |

### 2.2.5. Nhận xét

A* phù hợp nhất cho hướng solver chính vì tận dụng được cả chi phí đã đi và ước lượng còn lại. Trên `starter_01`, A* duyệt ít node hơn BFS trong lần chạy thực nghiệm. Tuy nhiên, do heuristic hiện tại chưa được chứng minh admissible/consistent cho mọi level và code có giới hạn tài nguyên, không nên kết luận A* luôn tối ưu tuyệt đối trong mọi trường hợp.

---

## 2.3. Hill Climbing

### 2.3.1. Ý tưởng thuật toán

Hill Climbing là thuật toán tìm kiếm cục bộ. Thuật toán không lưu toàn bộ frontier như BFS/A*, mà chỉ xét trạng thái hiện tại và các neighbor. Tại mỗi bước, thuật toán chọn neighbor có giá trị tốt hơn hiện tại. Trong project này, giá trị được định nghĩa là `value(state) = -h(state)`, nên `h` càng nhỏ thì value càng cao. Hill Climbing có thể kẹt ở local optimum, plateau hoặc ridge; vì vậy thuật toán không complete và không optimal.

### 2.3.2. Ánh xạ vào bài toán

File code là `ai/local_search/hill_climbing.py`. Neighbor của một state là các state sinh từ legal actions. Thuật toán dùng `squirrel_heuristic(state)`, đặt `value = -h`, rồi nhận first strictly better neighbor. Nếu đạt goal thì thành công; nếu không còn neighbor nào tốt hơn thì dừng với reason `local_optimum`. Kết quả vẫn được đóng gói trong `SearchResult`, nhưng khi fail thì path rỗng.

### 2.3.3. Trạng thái ban đầu và mục tiêu

**Bảng 7. Trạng thái ban đầu và mục tiêu cho Hill Climbing**

| Thành phần | Trạng thái ban đầu | Trạng thái mục tiêu |
|---|---|---|
| State | `starter_01`, hai squirrel còn hạt, h ban đầu bằng 2. | Mọi squirrel trong level đã thả hạt, h bằng 0. |
| Neighbor | Các state từ legal actions của state hiện tại. | Neighbor đạt goal nếu action cuối làm hạt còn lại rơi vào hole. |
| Value | `value = -2` ở start. | `value = 0` nếu goal. |

### 2.3.4. Các bước tìm solution

Trong lần chạy thực nghiệm trên `starter_01`, Hill Climbing không tìm được solution. Thuật toán đi từ h = 2 xuống h = 1 bằng `orange LEFT`, sau đó không tìm thấy neighbor có value cao hơn, nên dừng ở local optimum. Số liệu ghi nhận: solved `False`, visited `2`, generated `7`, time khoảng `0.000199s`, reason `local_optimum`.

**Bảng 8. Minh họa các bước Hill Climbing**

| Bước | Trạng thái hiện tại | Neighbor/action xét | h | Value=-h | Kết quả |
|---:|---|---|---:|---:|---|
| 0 | Start `starter_01` | Khởi tạo | 2 | -2 | Bắt đầu local search. |
| 1 | Start | `orange UP` | 2 | -2 | Không tốt hơn current. |
| 2 | Start | `orange LEFT` | 1 | -1 | Tốt hơn, chọn neighbor này. |
| 3 | Sau `orange LEFT` | `orange UP` | 1 | -1 | Không tốt hơn current. |
| 4 | Sau `orange LEFT` | Các neighbor còn lại | >= 1 | <= -1 | Không có neighbor strictly better. |
| 5 | Sau `orange LEFT` | Dừng | 1 | -1 | Fail với `local_optimum`. |

### 2.3.5. Nhận xét

Hill Climbing rất phù hợp để minh họa local search và hiện tượng kẹt cực trị cục bộ. Tuy nhiên, thuật toán không nên là solver chính nếu yêu cầu đảm bảo tìm lời giải, vì việc chỉ chấp nhận bước tốt hơn có thể làm nó bỏ qua những đường cần đi ngang hoặc đi tạm thời xấu hơn.

---

## 2.4. AND-OR Search

### 2.4.1. Ý tưởng thuật toán

AND-OR Search dùng cho môi trường không xác định. OR node là điểm agent chọn action; AND node là điểm môi trường có thể trả về nhiều outcome. Một action chỉ được chấp nhận nếu mọi outcome của action đó đều có plan tiếp theo dẫn tới goal. Kết quả lý tưởng của AND-OR Search không chỉ là một path tuyến tính, mà là conditional plan: nếu outcome này xảy ra thì làm nhánh này, nếu outcome khác xảy ra thì làm nhánh khác.

### 2.4.2. Ánh xạ vào bài toán

File code là `ai/complex/and_or_search.py`. Project dùng mô hình mở rộng có tên Slippery Mode để minh họa nondeterminism: một action có thể đi một ô hoặc nếu vẫn hợp lệ thì trượt thêm một ô cùng hướng. Đây là phiên bản thích nghi, không phải luật chính của game deterministic. Hàm `get_outcomes()` sinh tập outcome không mutate state. `or_search()` thử các action của agent, còn `and_search()` yêu cầu mọi outcome đều có subplan. `extra["plan_tree"]` lưu conditional plan ở dạng chuỗi, còn `path` chỉ là sample path tuyến tính chọn outcome đầu tiên để UI có thể replay.

### 2.4.3. Trạng thái ban đầu và mục tiêu

**Bảng 9. Trạng thái ban đầu và mục tiêu cho AND-OR Search**

| Thành phần | Trạng thái ban đầu | Trạng thái mục tiêu |
|---|---|---|
| State | `starter_01` deterministic được dùng làm start state. | Mọi outcome theo conditional plan đều có nhánh dẫn tới goal trong giới hạn depth. |
| Môi trường | Mở rộng bằng Slippery Mode: action có thể tạo một hoặc hai outcome. | Không còn squirrel giữ hạt ở các nhánh thành công. |
| Plan | Chưa có plan. | `plan_tree` chứa conditional plan; `path` chỉ là sample path tuyến tính cho UI. |

### 2.4.4. Các bước tìm solution

Trong lần chạy thực nghiệm, AND-OR Search tìm được plan với sample path 7 bước: `orange UP`, `orange LEFT`, `orange DOWN`, `orange UP`, `white UP`, `orange DOWN`, `white UP`. Số liệu ghi nhận: solved `True`, visited `105`, generated `121`, time khoảng `0.003467s`, reason `goal_plan_found`.

**Bảng 10. Minh họa các bước AND-OR Search**

| Bước | Loại node | Action/outcome | Điều kiện kiểm tra | Kết quả |
|---:|---|---|---|---|
| 0 | OR | Khởi tạo | Agent chọn action, môi trường trả outcomes. | Bắt đầu từ state `starter_01`. |
| 1 | OR | Xét legal actions | Không vượt `max_depth`, không lặp path. | Có 4 action hợp lệ ở depth 0. |
| 2 | AND | Outcome của `orange UP` | Mỗi outcome phải có plan. | Gọi OR cho từng outcome. |
| 3 | OR | Mở rộng outcome | Kiểm tra goal, depth, cycle. | Tiếp tục thử action kế tiếp. |
| 4 | AND | Các outcome của action được chọn | Nếu một outcome fail thì action bị loại. | Chỉ giữ action khi tất cả outcome thành công. |
| 5 | OR/AND | Plan hoàn chỉnh | Mọi nhánh có đường tới goal. | Trả về `plan_tree`, sample path dùng cho demo. |

### 2.4.5. Nhận xét

AND-OR Search phù hợp để minh họa môi trường không xác định và conditional plan. Với game chính của project, môi trường deterministic nên AND-OR không phải solver chính. Khi trình bày, cần nói rõ đây là mô hình mở rộng học thuật, không phải luật gốc của Squirrels Go Nuts trong project.

---

## 2.5. AC-3

### 2.5.1. Ý tưởng thuật toán

AC-3 là thuật toán inference trong CSP, không phải search thông thường. Mục tiêu của AC-3 là làm các cung trong CSP trở nên arc-consistent. Một giá trị trong domain của biến `X_i` bị loại nếu không có giá trị hỗ trợ tương ứng trong domain của biến lân cận `X_j`. Nếu domain của một biến rỗng, CSP thất bại.

### 2.5.2. Ánh xạ vào bài toán

File code là `ai/csp/ac3.py`. Project ánh xạ bài toán thành các biến trạng thái `S_0, S_1, ..., S_d`. Domain của `S_i` là các state đạt được sau đúng `i` bước. Ràng buộc giữa `S_i` và `S_{i+1}` là phải tồn tại action hợp lệ chuyển từ state ở lớp trước sang state ở lớp sau. Domain cuối được lọc chỉ giữ goal states. Sau khi propagation, thuật toán reconstruct path qua các transition còn support; heuristic chỉ dùng làm tie-break khi có nhiều lựa chọn hợp lệ, không phải phần cốt lõi của AC-3.

### 2.5.3. Trạng thái ban đầu và mục tiêu

**Bảng 11. Trạng thái ban đầu và mục tiêu cho AC-3**

| Thành phần | Trạng thái ban đầu | Trạng thái mục tiêu |
|---|---|---|
| Biến | `S_0` chứa duy nhất state `starter_01`. | `S_d` chứa goal states trong depth tìm được. |
| Domain | Domain được sinh theo từng layer reachable. | Domain sau propagation chỉ giữ các state có support hai chiều. |
| Ràng buộc | Transition hợp lệ giữa `S_i` và `S_{i+1}`. | Có đường reconstruct từ `S_0` tới goal ở `S_d`. |

### 2.5.4. Các bước tìm solution

Trong lần chạy thực nghiệm, AC-3 tìm goal ở depth 3 và reconstruct path `orange LEFT`, `white UP`, `white UP`. Số liệu ghi nhận: solved `True`, visited `53`, generated `30`, time khoảng `0.001719s`, `arc_checks = 37`, `pruned_values = 31`, reason `goal_found`.

**Bảng 12. Minh họa các bước AC-3**

| Bước | Biến/cung đang xét | Domain size | Giá trị bị loại | Lý do | Kết quả |
|---:|---|---:|---:|---|---|
| 0 | `S_0..S_15` | 1 ở `S_0` | 0 | Khởi tạo domain theo lớp. | Bắt đầu sinh reachable states. |
| 1 | Sinh `S_1` từ `S_0` | 4 | 0 | Có 4 successor khác nhau. | Domain `S_1` có 4 state. |
| 2 | Sinh `S_2` từ `S_1` | 11 | 0 | Mở rộng layer tiếp theo. | Domain `S_2` có 11 state. |
| 3 | Sinh `S_3` từ `S_2` | 19 | 0 | Phát hiện goal trong `S_3`. | Chọn `goal_depth = 3`. |
| 4 | Ràng buộc goal trên `S_3` | 19 | Một số state non-goal | Domain cuối chỉ giữ goal states. | Bắt đầu AC-3 revise arcs. |
| 5 | Revise các arc `S_i -> S_j` | Theo từng lớp | Tổng 31 | Loại state không có support ở lớp lân cận. | Reconstruct được path 3 bước. |

### 2.5.5. Nhận xét

AC-3 là cách nhìn bài toán dưới dạng CSP/inference. Nó không tự nhiên bằng BFS/A* cho solver chính, nhưng rất hữu ích để minh họa constraint propagation: thay vì chỉ đi từng nhánh, thuật toán xây domain theo lớp và loại các state không còn support theo ràng buộc transition.

---

## 2.6. Alpha-Beta Pruning

### 2.6.1. Ý tưởng thuật toán

Alpha-Beta Pruning dựa trên Minimax. MAX chọn hành động để tối đa hóa utility, còn MIN chọn hành động để tối thiểu hóa utility của MAX. `alpha` là giá trị tốt nhất mà MAX đã đảm bảo trên đường đi hiện tại; `beta` là giá trị tốt nhất mà MIN đã đảm bảo. Khi `beta <= alpha`, nhánh còn lại không thể ảnh hưởng tới quyết định cuối cùng nên có thể cắt tỉa. Nếu cùng depth, utility và thứ tự xét action, Alpha-Beta cho cùng quyết định như Minimax nhưng duyệt ít nhánh hơn.

### 2.6.2. Ánh xạ vào bài toán

File code là `ai/adversarial/alpha_beta.py`. Vì Squirrels Go Nuts là puzzle một người chơi, Alpha-Beta trong project là adversarial demo mode. MAX điều khiển các squirrel, còn MIN điều khiển flower/blocker trong mô hình minh họa. Utility được định nghĩa: goal có giá trị `1000`, trạng thái non-terminal dùng `-squirrel_heuristic(state)`. Flower được tạm thời đặt movable trong lượt MIN rồi trả về không movable sau khi áp dụng action. Đây là phiên bản thích nghi để minh họa tìm kiếm đối kháng, không phải luật gốc của game.

### 2.6.3. Trạng thái ban đầu và mục tiêu

**Bảng 13. Trạng thái ban đầu và mục tiêu cho Alpha-Beta**

| Thành phần | Trạng thái ban đầu | Trạng thái mục tiêu |
|---|---|---|
| MAX | Các action của squirrel có thể di chuyển hợp lệ. | Chọn được chuỗi MAX action đưa mọi hạt vào hole. |
| MIN | Flower/blocker được xem như đối thủ trong demo. | MIN cố chọn action làm giảm utility của MAX. |
| Utility | `goal = 1000`, non-terminal = `-squirrel_heuristic(state)`. | Utility cao khi goal đạt; cutoff dùng heuristic. |
| Lưu ý | Game gốc không có đối thủ. | Đây là mô hình minh họa, không phải solver chính. |

### 2.6.4. Các bước tìm solution

Trong lần chạy thực nghiệm trên `starter_01`, Alpha-Beta không tìm được path replay goal dưới thiết lập mặc định. Số liệu ghi nhận: solved `False`, visited `530`, generated `510`, time khoảng `0.018775s`, reason `max_moves`, `pruned_count = 122`, `max_depth = 3`.

**Bảng 14. Minh họa các bước Alpha-Beta**

| Bước | Node | Action | Alpha | Beta | Utility/Value | Kết quả |
|---:|---|---|---:|---:|---:|---|
| 0 | Root MAX | Khởi tạo | `-inf` | `inf` | - | Bắt đầu depth-limited Alpha-Beta. |
| 1 | MAX | Xét 4 action squirrel | `-inf` | `inf` | - | Chọn action ứng viên cho MAX. |
| 2 | MIN | Xét action flower | `-inf` | `inf` | - | MIN mô phỏng blocker. |
| 3 | MAX cutoff | Ví dụ `orange LEFT` | -2 | `inf` | -2.0 | Cập nhật alpha. |
| 4 | MAX cutoff | Ví dụ `orange RIGHT` | -1 | `inf` | -1.0 | Cập nhật best value tốt hơn. |
| 5 | MAX/MIN | Khi `beta <= alpha` | Theo nhánh | Theo nhánh | Theo heuristic | Cắt một số nhánh, nhưng không tìm goal replay được. |

### 2.6.5. Nhận xét

Alpha-Beta phù hợp để minh họa tìm kiếm đối kháng và kỹ thuật cắt nhánh của Minimax. Tuy nhiên, do puzzle gốc không có đối thủ, thuật toán này không phải hướng giải chính cho Squirrels AI Solver. Khi đưa vào báo cáo, cần gọi rõ đây là adversarial demo mode.

## 2.7. Các thuật toán còn lại trong project

Ngoài 6 thuật toán đại diện đã phân tích sâu, project còn đăng ký thêm 12 thuật toán trong `ai/solver_interface.py`. Các thuật toán này đều đi qua hàm `solve(algorithm_name, start_state, rules, **kwargs)` và đều trả về `SearchResult`, nên UI có thể hiển thị cùng một kiểu thống kê: trạng thái solved/fail, số bước, số node đã duyệt, số node đã sinh, thời gian chạy và metadata trong `extra`. Phần này giúp người đọc hiểu đầy đủ hệ thuật toán của project, không chỉ nhìn vào 6 thuật toán chính.

### 2.7.1. Depth-First Search (DFS)

DFS nằm trong `ai/uninformed/dfs.py`, thuộc nhóm tìm kiếm mù giống BFS nhưng dùng stack thay vì queue. Thuật toán ưu tiên đi sâu theo một nhánh trước khi quay lại xét nhánh khác. Trong project, DFS là depth-limited graph DFS: mỗi node vẫn là `GameState`, action vẫn là `(piece_id, direction)`, successor sinh bằng `rules.legal_actions()` và `safe_apply_action()`. DFS dùng cycle checking theo path hiện tại thay vì global explored set để tránh cắt bỏ quá mạnh các đường đi khác nhau tới cùng một state.

Ưu điểm của DFS là bộ nhớ thường thấp hơn BFS vì không cần giữ toàn bộ frontier theo lớp. Nhược điểm là DFS không đảm bảo tìm lời giải ngắn nhất; thuật toán có thể đi rất sâu vào nhánh không tốt trước khi quay lại. Trong project, DFS có `max_depth`, `max_nodes`, `max_seconds`; vì vậy nếu fail thì không thể kết luận level vô nghiệm, chỉ có thể nói thuật toán không tìm được lời giải trong giới hạn đã đặt.

### 2.7.2. Iterative Deepening Search (IDS)

IDS nằm trong `ai/uninformed/ids.py`. Thuật toán chạy nhiều lần depth-limited search với giới hạn độ sâu tăng dần từ 0 tới `max_depth`. Ý tưởng là kết hợp ưu điểm của BFS và DFS: giống BFS ở chỗ tìm lời giải nông nhất với unit cost, nhưng dùng bộ nhớ gần với DFS vì mỗi vòng chỉ đi sâu trong một giới hạn.

Trong Squirrels AI Solver, IDS dùng path-based cycle checking ở mỗi vòng lặp và không giữ global explored set qua các iteration. `extra["iterations"]` lưu thống kê từng depth limit, giúp visualizer giải thích vì sao IDS có thể duyệt lặp lại nhiều node. IDS phù hợp để so sánh với BFS: nếu cần lời giải nông nhưng muốn giảm bộ nhớ, IDS là lựa chọn hợp lý; đổi lại, thời gian có thể tăng vì các lớp nông bị duyệt lại nhiều lần.

### 2.7.3. Greedy Best-First Search

Greedy nằm trong `ai/informed/greedy.py`, thuộc nhóm tìm kiếm có thông tin. Khác A*, Greedy chỉ ưu tiên `h(n)` mà không cộng thêm `g(n)`. Trong project, `h(n)` là `squirrel_heuristic`, tức minimum-assignment Manhattan từ các hạt chưa rơi tới các lỗ trống riêng biệt. Priority queue của Greedy luôn pop node có heuristic nhỏ nhất.

Greedy thường chạy nhanh và trên level dễ có thể tìm lời giải rất ít node, nhưng nó không đảm bảo tối ưu vì không quan tâm đã đi bao xa. Một state có vẻ gần goal theo heuristic chưa chắc nằm trên đường ngắn nhất. Vì vậy Greedy phù hợp để minh họa vai trò của heuristic và để so sánh với A*: A* cân bằng `g+h`, còn Greedy chỉ nhìn phần ước lượng còn lại.

### 2.7.4. Iterative Deepening A* (IDA*)

IDA* nằm trong `ai/informed/idastar.py`. Đây là phiên bản kết hợp giữa A* và iterative deepening. Thay vì giữ priority queue lớn như A*, IDA* chạy DFS nhiều lần với ngưỡng `f = g + h`. Ban đầu threshold bằng `h(start)`, sau mỗi vòng nếu chưa tìm được goal thì nâng threshold lên giá trị `f` nhỏ nhất đã vượt ngưỡng.

Trong project, IDA* dùng `squirrel_heuristic`, path-based cycle checking và sắp xếp successor theo `(f, h, action_text)` để quá trình duyệt ổn định hơn. IDA* tiết kiệm bộ nhớ hơn A*, nhưng có thể tốn thời gian vì lặp lại tìm kiếm theo threshold. Tính tối ưu của IDA* cũng phụ thuộc vào điều kiện heuristic giống A*: không nên khẳng định tối ưu tuyệt đối khi heuristic chưa được chứng minh admissible/consistent.

### 2.7.5. Local Beam Search

Local Beam nằm trong `ai/local_search/local_beam.py`, thuộc nhóm local search. Thuật toán giữ lại `k` candidate tốt nhất ở mỗi iteration thay vì chỉ giữ một state như Hill Climbing. Trong project, bản cài đặt bắt đầu từ một `start_state` cố định rồi sinh successor, chọn top-k theo heuristic nhỏ nhất và tiếp tục mở rộng các state trong beam.

Đây là phiên bản beam-style thích nghi cho puzzle có một trạng thái ban đầu rõ ràng. So với Hill Climbing, Local Beam có cơ hội thoát một số lựa chọn cục bộ xấu vì giữ nhiều candidate cùng lúc. Tuy nhiên, thuật toán vẫn không complete và không optimal: nếu beam width nhỏ, một nhánh tốt nhưng tạm thời có heuristic cao có thể bị loại sớm.

### 2.7.6. Simulated Annealing

Simulated Annealing nằm trong `ai/local_search/simulated_annealing.py`. Thuật toán cũng dùng `value = -h`, nhưng khác Hill Climbing ở chỗ có thể chấp nhận một neighbor xấu hơn với xác suất `P = exp(delta_E / T)`. Nhiệt độ `T` giảm dần theo `cooling_rate`; khi nhiệt độ cao, thuật toán dễ chấp nhận bước xấu để khám phá, còn khi nhiệt độ thấp, thuật toán ngày càng bảo thủ.

Trong project, thuật toán chọn random một legal action ở mỗi vòng. Vì có yếu tố ngẫu nhiên, kết quả giữa các lần chạy có thể khác nhau nếu không cố định `seed`. Khi báo cáo số liệu, cần ghi rõ đây là kết quả của một lần chạy thực nghiệm cụ thể. Nếu Simulated Annealing fail với reason `temperature_zero` hoặc `max_iterations`, điều đó không chứng minh level không có lời giải; nó chỉ cho thấy lịch làm nguội hoặc số vòng hiện tại chưa tìm được goal.

### 2.7.7. Backtracking Search

Backtracking nằm trong `ai/csp/backtracking.py`. Project mô hình hóa thuật toán này theo hướng action-plan CSP. Biến `A_i` là action ở bước thứ `i`; domain của biến là các legal actions tại state hiện tại; ràng buộc gồm action phải hợp lệ, state chuyển tiếp đúng theo luật, path không tạo cycle và một state trong path phải đạt goal.

Về hành vi, Backtracking gần với depth-limited search, nhưng cách trình bày dưới dạng CSP giúp giải thích bài toán theo biến, miền giá trị và ràng buộc. Khi một action gây state lặp hoặc đi vào nhánh không đạt goal trong `max_depth`, thuật toán quay lui để thử action khác. Đây là thuật toán thích hợp để minh họa rằng cùng một puzzle có thể được nhìn như bài toán gán chuỗi hành động có ràng buộc.

### 2.7.8. Min-Conflicts

Min-Conflicts nằm trong `ai/csp/min_conflicts.py`, cũng thuộc nhóm CSP nhưng dùng local search trên một chuỗi action độ dài `k`. Thuật toán tạo một kế hoạch ban đầu ngẫu nhiên, sau đó đánh giá conflict score. Các conflict trong project gồm action illegal khi replay, state bị lặp/cycle và số hạt còn chưa rơi sau `k` bước.

Ở mỗi vòng, thuật toán chọn một biến/action đang gây xung đột rồi thử các giá trị trong domain để tìm giá trị làm giảm conflict nhiều nhất. Đây là cách minh họa Min-Conflicts theo tinh thần CSP, nhưng kết quả phụ thuộc vào `k`, `max_steps` và random seed. Ngoài ra, `solver_interface.solve()` còn replay path trước khi trả cho UI; nếu path do Min-Conflicts báo solved nhưng không replay hợp lệ dưới luật deterministic, kết quả sẽ bị đánh dấu `invalid_solution_path`.

### 2.7.9. Minimax

Minimax nằm trong `ai/adversarial/minimax.py`. Vì game gốc là puzzle một người chơi, Minimax trong project là adversarial demo mode. MAX điều khiển các squirrel để làm giảm heuristic hoặc đạt goal, còn MIN điều khiển flower/blocker để làm utility của MAX kém đi. Terminal goal có utility `1000`, còn cutoff non-terminal dùng `-squirrel_heuristic(state)`.

Thuật toán dùng depth limit và mô phỏng luân phiên lượt MAX/MIN. Điểm quan trọng khi viết báo cáo là không được nói đây là luật gốc của Squirrels Go Nuts. Đây là mô hình mở rộng để minh họa tìm kiếm đối kháng. Nếu Minimax fail ở `max_moves`, nghĩa là trong mô phỏng giới hạn hiện tại thuật toán chưa tạo được path replay goal cho UI, không phải level deterministic không giải được.

### 2.7.10. Expectimax

Expectimax nằm trong `ai/adversarial/expectimax.py`. Thuật toán giống Minimax ở lượt MAX, nhưng thay MIN bằng CHANCE node. Trong project, CHANCE mô hình hóa flower/blocker ngẫu nhiên: flower có thể đứng yên với xác suất 0.5 hoặc di chuyển một hướng hợp lệ với phần xác suất còn lại chia đều. Nếu không có flower action, chance outcome là đứng yên với xác suất 1.

Expectimax phù hợp để minh họa môi trường stochastic, nơi agent không giả định đối thủ luôn chọn nước bất lợi nhất mà tính expected utility theo xác suất. Đây cũng là mô hình mở rộng, không phải luật chính của puzzle. Khi UI replay, project chọn một outcome cụ thể để tạo path tuyến tính, nên cần phân biệt giữa expected-value planning và replay deterministic.

### 2.7.11. Belief-State Search

Belief-State nằm trong `ai/complex/belief_state_search.py`. Thuật toán dùng conformant belief-state BFS: thay vì một state duy nhất, agent giữ một tập các state có thể là trạng thái thật. Project tạo initial belief bằng cách cho flower/blocker có thể ở một vài vị trí lân cận, rồi tìm một chuỗi action hoạt động cho mọi state trong belief.

Mô hình này dùng để minh họa môi trường thiếu quan sát hoặc không chắc chắn. Một action chỉ được xét nếu hợp lệ trong tất cả possible states. Goal của belief-state là mọi state trong belief đều đạt goal. Đây là cách mở rộng tốt để giải thích khái niệm belief state, nhưng không phải solver chính của game deterministic, vì trong game chính agent biết toàn bộ bàn cờ.

### 2.7.12. Online Search / LRTA*

Online Search nằm trong `ai/complex/online_search.py`, được cài theo phong cách LRTA*. Khác A* lập plan offline trước khi hành động, online search quan sát successor của state hiện tại, cập nhật `learned_h[current] = min(1 + learned_h[next])`, rồi di chuyển sang successor có estimated cost nhỏ nhất. Thuật toán vừa học vừa đi.

Trong project, online search có `safety_cutoff` để tránh lặp vô hạn khi agent cứ quay lại cùng state. Kết quả có thể là path dài hơn BFS/A* vì agent không nhìn toàn bộ không gian trước khi đi. Thuật toán này phù hợp để minh họa agent online trong môi trường mà thông tin chỉ được biết dần, dù với puzzle deterministic nhỏ thì BFS/A* vẫn tự nhiên hơn.

## 2.8. Cách đọc kết quả thuật toán trong UI

Tất cả thuật toán trả về `SearchResult`. Trường `solved` cho biết solver có path hợp lệ sau khi qua kiểm tra replay hay không. Trường `path` là danh sách action UI có thể chạy lại; nếu `solved=False`, số bước nên ghi là `N/A` hoặc 0 tùy bảng, không nên tự suy diễn từ log nội bộ. `visited_count` và `generated_count` là chỉ số thật do từng solver trả về, nhưng ý nghĩa có thể khác nhau giữa nhóm thuật toán: BFS/A* đếm state/node, AC-3 có thêm arc checks, Minimax/Alpha-Beta đếm node trong game tree, còn local search đếm neighbor/candidate. Vì vậy khi so sánh, nên dùng các chỉ số này như bằng chứng thực nghiệm trong cùng ngữ cảnh, không nên xem chúng là thước đo tuyệt đối giống hệt nhau cho mọi nhóm.

# PHẦN IV. ĐÁNH GIÁ VÀ THẢO LUẬN

## 4.1. So sánh các thuật toán trong cùng nhóm

**Bảng 15. So sánh nhóm tìm kiếm mù**

| Thuật toán | Ưu điểm | Hạn chế | Complete | Optimal | Phù hợp với game | Vai trò |
|---|---|---|---|---|---|---|
| BFS | Dễ hiểu, tìm lời giải nông nhất với unit cost, dùng `encode()` chống lặp. | Tốn bộ nhớ khi frontier lớn. | Có nếu state-space hữu hạn và không bị limit. | Có với step cost bằng nhau và không bị limit. | Rất phù hợp. | Đại diện chính trong báo cáo. |
| DFS | Bộ nhớ thấp hơn BFS, đi sâu nhanh. | Không tối ưu, dễ đi nhánh dài. | Chỉ trong `max_depth` và resource limit. | Không. | Phù hợp để so sánh. | Thuật toán phụ trong nhóm mù. |
| IDS | Kết hợp ưu điểm tìm nông của BFS với bộ nhớ DFS. | Lặp lại nhiều node qua các depth. | Có trong `max_depth` và resource limit. | Có với unit cost trong giới hạn. | Khá phù hợp. | Lựa chọn thay thế khi muốn giảm bộ nhớ. |

Nhóm tìm kiếm mù áp dụng tự nhiên nhất vào puzzle deterministic. BFS là thuật toán dễ bảo vệ nhất vì state, action, goal và cost đều rõ ràng; IDS là lựa chọn cân bằng hơn về bộ nhớ; DFS chủ yếu dùng để so sánh hạn chế.

**Bảng 16. So sánh nhóm tìm kiếm có thông tin**

| Thuật toán | Ưu điểm | Hạn chế | Complete | Optimal | Phù hợp với game | Vai trò |
|---|---|---|---|---|---|---|
| Greedy | Nhanh, ưu tiên state có heuristic nhỏ. | Bỏ qua `g(n)`, dễ chọn đường không tối ưu. | Không đảm bảo trong giới hạn hữu hạn. | Không. | Phù hợp để demo heuristic. | So sánh với A*. |
| A* | Kết hợp `g+h`, có `g_score` và reopen state. | Phụ thuộc heuristic và resource limit. | Có điều kiện. | Có nếu heuristic admissible/consistent và không bị limit. | Rất phù hợp. | Đại diện chính trong báo cáo. |
| IDA* | Dùng ngưỡng `f`, tiết kiệm bộ nhớ hơn A*. | Có thể tốn thời gian do DFS lặp và threshold. | Có điều kiện trong depth/threshold/resource. | Có điều kiện heuristic. | Khá phù hợp. | Lựa chọn informed khi muốn giảm memory. |

Nhóm informed search là hướng mạnh cho solver chính. A* nổi bật nhất vì cân bằng số bước đã đi và ước lượng còn lại, nhưng heuristic của project là heuristic thực dụng, chưa có chứng minh đầy đủ.

**Bảng 17. So sánh nhóm tìm kiếm cục bộ**

| Thuật toán | Ưu điểm | Hạn chế | Complete | Optimal | Phù hợp với game | Vai trò |
|---|---|---|---|---|---|---|
| Hill Climbing | Đơn giản, log rõ hiện tượng cải thiện heuristic. | Dễ kẹt local optimum/plateau. | Không. | Không. | Phù hợp để minh họa, không nên làm solver chính. | Đại diện chính trong báo cáo. |
| Local Beam | Giữ nhiều candidate hơn Hill Climbing. | Prune mạnh, vẫn có thể bỏ mất lời giải. | Không. | Không. | Phù hợp demo. | So sánh local search. |
| Simulated Annealing | Có thể nhận bước xấu để thoát kẹt. | Kết quả stochastic, phụ thuộc seed/nhiệt độ. | Không. | Không. | Phù hợp demo local stochastic search. | Minh họa mở rộng. |

Nhóm local search hữu ích về mặt học thuật vì cho thấy không phải thuật toán nào dùng heuristic cũng đảm bảo tìm được lời giải. Trên `starter_01`, Hill Climbing đã kẹt ở `local_optimum`, đúng với đặc trưng lý thuyết.

**Bảng 18. So sánh nhóm môi trường phức tạp**

| Thuật toán | Ưu điểm | Hạn chế | Complete | Optimal | Phù hợp với game | Vai trò |
|---|---|---|---|---|---|---|
| AND-OR Search | Tạo conditional plan cho nhiều outcome. | Game chính deterministic, path UI chỉ là sample path. | Có trong depth/resource nếu không gian hữu hạn. | Không tối ưu cost. | Phù hợp khi mở rộng nondeterministic. | Đại diện chính trong báo cáo. |
| Belief-State | Mô hình tập state có thể xảy ra, phù hợp thiếu quan sát. | Initial belief trong project là demo quanh flower/blocker. | Có trong giới hạn `max_states`. | Không tối ưu tuyệt đối. | Phù hợp minh họa uncertainty. | So sánh trong nhóm phức tạp. |
| Online Search | Agent học và cập nhật khi đang di chuyển. | Dễ lặp, có safety cutoff. | Không đảm bảo trong demo limit. | Không. | Phù hợp minh họa LRTA*. | Demo online agent. |

Nhóm môi trường phức tạp không phải solver tự nhiên nhất cho game gốc, nhưng giúp báo cáo thể hiện các mô hình AI ngoài môi trường deterministic fully observable.

**Bảng 19. So sánh nhóm CSP**

| Thuật toán | Ưu điểm | Hạn chế | Complete | Optimal | Phù hợp với game | Vai trò |
|---|---|---|---|---|---|---|
| Backtracking | Dễ ánh xạ action-plan CSP, thử gán action theo bước. | Hành vi gần depth-limited search, phụ thuộc max depth. | Có trong depth/resource. | Không đảm bảo. | Phù hợp minh họa CSP-style search. | So sánh với AC-3. |
| AC-3 | Thể hiện constraint propagation và arc consistency. | Không phải search thông thường; cần sinh domain theo layer. | Không theo nghĩa search path cổ điển. | Không tối ưu cost. | Phù hợp minh họa inference. | Đại diện chính trong báo cáo. |
| Min-Conflicts | Tối ưu xung đột của chuỗi action. | Stochastic, có thể fail dù tồn tại lời giải. | Không. | Không. | Phù hợp demo local CSP. | So sánh trong CSP. |

AC-3 là thuật toán đáng trình bày nhất trong nhóm CSP vì nó khác rõ BFS/A*: trọng tâm không phải mở rộng frontier mà là loại bỏ giá trị domain không có support.

**Bảng 20. So sánh nhóm đối kháng/ngẫu nhiên**

| Thuật toán | Ưu điểm | Hạn chế | Complete | Optimal | Phù hợp với game | Vai trò |
|---|---|---|---|---|---|---|
| Minimax | Dễ giải thích MAX/MIN và utility. | Game gốc không có đối thủ, phải demo flower như MIN. | Trong depth game tree hữu hạn. | Tối ưu theo depth/eval giới hạn. | Chỉ phù hợp demo. | Nền tảng cho Alpha-Beta. |
| Alpha-Beta | Cắt nhánh, giữ quyết định như Minimax với cùng điều kiện. | Vẫn là adversarial demo, không phải luật game chính. | Trong depth game tree hữu hạn. | Như Minimax cùng depth/eval/order. | Chỉ phù hợp demo. | Đại diện chính trong báo cáo. |
| Expectimax | Minh họa chance node và expected utility. | Mô hình xác suất là giả lập, không phải game gốc. | Trong depth hữu hạn. | Tối ưu kỳ vọng theo model xác suất đã đặt. | Phù hợp demo stochastic. | So sánh với đối kháng. |

Nhóm adversarial/stochastic cần được gắn nhãn rõ. Đây là phần mở rộng để minh họa lý thuyết AIMA, không nên trình bày như luật gốc của Squirrels Go Nuts.

## 4.2. So sánh giữa 6 nhóm thuật toán

**Bảng 21. So sánh tổng quan 6 nhóm thuật toán**

| Nhóm thuật toán | Đại diện phân tích | Mức độ phù hợp | Tốc độ dự kiến | Bộ nhớ | Khả năng tìm lời giải | Khả năng demo | Nhận xét |
|---|---|---|---|---|---|---|---|
| Tìm kiếm mù | BFS | Rất cao | Trung bình, giảm khi state-space lớn | Cao | Tốt nếu không bị limit | Rất rõ | Solver nền tảng, dễ bảo vệ lý thuyết. |
| Tìm kiếm có thông tin | A* | Rất cao | Thường tốt hơn BFS nếu heuristic hữu ích | Trung bình đến cao | Tốt có điều kiện heuristic/resource | Rất rõ | Phù hợp nhất làm solver chính, nhưng cần nói rõ điều kiện tối ưu. |
| Tìm kiếm cục bộ | Hill Climbing | Trung bình | Nhanh | Thấp | Không đảm bảo | Rất tốt để minh họa kẹt | Hữu ích cho thảo luận local optimum. |
| Môi trường phức tạp | AND-OR Search | Trung bình trong model mở rộng | Phụ thuộc số outcome/depth | Cao theo cây plan | Tốt nếu mọi outcome có plan trong depth | Rất tốt | Minh họa nondeterminism và conditional plan. |
| CSP | AC-3 | Trung bình, thiên về học thuật | Phụ thuộc domain theo layer | Trung bình đến cao | Hỗ trợ tìm path sau propagation | Tốt | Minh họa inference/constraint propagation. |
| Đối kháng/ngẫu nhiên | Alpha-Beta | Thấp cho game gốc, cao cho demo | Tốt hơn Minimax nhờ pruning | Theo game tree depth | Chỉ theo model adversarial demo | Tốt | Không phải solver chính vì game gốc là single-agent puzzle. |

BFS và A* phù hợp nhất cho solver chính của Squirrels AI Solver vì bài toán gốc là deterministic state-space puzzle. Hill Climbing phù hợp để minh họa local search và giới hạn của heuristic cục bộ. AND-OR phù hợp khi mở rộng sang môi trường không xác định. AC-3 phù hợp để minh họa CSP/inference bằng cách lọc domain trạng thái theo ràng buộc transition. Alpha-Beta phù hợp để minh họa đối kháng và cắt nhánh, nhưng không phải luật gốc của game.

## 4.3. Kết quả thực nghiệm

Các lệnh kiểm tra đã thử trong môi trường hiện tại:

```bash
python -m compileall .
python verify_core.py
python -m pytest tests
python tests\test_algorithm_smoke.py
```

`python -m compileall .` không hoàn tất vì lỗi môi trường OneDrive/Windows khi rename file `.pyc` trong `__pycache__`: `PermissionError: [WinError 5] Access is denied`. Lỗi này thuộc môi trường ghi file bytecode, không phải lỗi cú pháp được chỉ ra trong source. `python -m pytest tests` không chạy được vì môi trường chưa cài `pytest`: `No module named pytest`. Tuy nhiên, `python verify_core.py` chạy thành công và fallback `python tests\test_algorithm_smoke.py` chạy thành công cho đủ 18 thuật toán đã đăng ký.

Bảng dưới đây dùng số liệu thực nghiệm lấy bằng đúng cấu hình của màn UI Report trong `ui/screens/report_screen.py`: mỗi thuật toán được gọi qua `solve(name, initial_state, rules, max_nodes=20000, max_seconds=2.0)` trên level `starter_01`. Đây là số liệu thật của một lần chạy cụ thể, không phải số liệu tự đặt. Thời gian chạy có thể dao động nhẹ giữa các máy hoặc giữa các lần chạy, nhất là với thuật toán stochastic như Simulated Annealing và Min-Conflicts.

**Bảng 22. Kết quả thực nghiệm toàn bộ thuật toán trên level `starter_01`**

| Thuật toán | Status | Solved | Số bước | Visited | Generated | Time | Reason/Details |
|---|---|---|---:|---:|---:|---:|---|
| BFS | done | Yes | 3 | 12 | 49 | 0.001200s | goal_found |
| DFS | done | Yes | 13 | 14 | 54 | 0.001540s | goal_found |
| IDS | done | Yes | 3 | 57 | 63 | 0.001439s | goal_found |
| A* | done | Yes | 3 | 11 | 42 | 0.001359s | goal_found |
| IDA* | done | Yes | 3 | 25 | 33 | 0.001242s | goal_found |
| Greedy | done | Yes | 3 | 6 | 21 | 0.000674s | goal_found |
| Hill Climbing | done | No | N/A | 2 | 7 | 0.000226s | local_optimum |
| Local Beam | done | No | N/A | 26 | 104 | 0.005369s | no_candidate |
| Simulated Annealing | done | No | N/A | 193 | 226 | 0.013057s | temperature_zero |
| Minimax | done | No | N/A | 885 | 865 | 0.036823s | max_moves |
| Alpha-Beta | done | No | N/A | 530 | 510 | 0.018898s | max_moves |
| Expectimax | done | Yes | 3 | 240 | 237 | 0.009730s | goal_found |
| AC-3 | done | Yes | 3 | 53 | 30 | 0.002683s | goal_found |
| Backtracking | done | Yes | 13 | 14 | 21 | 0.001143s | goal_found |
| Min-Conflicts | done | No | N/A | 6 | 40 | 0.009387s | invalid_solution_path |
| AND-OR Search | done | Yes | 7 | 105 | 121 | 0.005099s | goal_plan_found |
| Belief-State | done | Yes | 3 | 28 | 46 | 0.007796s | goal_belief_found |
| Online Search | done | Yes | 18 | 18 | 76 | 0.002135s | goal_found |

Các thuật toán state-space chính như BFS, IDS, A*, IDA* và Greedy đều tìm được lời giải 3 bước trên `starter_01`: `orange LEFT`, `white UP`, `white UP`, đúng với `target_moves = 3`. DFS và Backtracking cũng tìm được lời giải nhưng dài hơn vì cách duyệt ưu tiên đi sâu. Hill Climbing fail do local optimum, Local Beam fail do hết candidate mới trong cấu hình hiện tại, còn Simulated Annealing fail do nhiệt độ giảm tới ngưỡng dừng trước khi đạt goal trong lần chạy này. Nhóm adversarial như Minimax và Alpha-Beta fail với `max_moves` vì đây là mô hình demo đối kháng có depth/move limit, không phải solver deterministic chính của game. Min-Conflicts bị `invalid_solution_path` do path không vượt qua bước kiểm tra replay hợp lệ trong `solver_interface.solve()`. AND-OR, Belief-State và Expectimax solved trong mô hình mở rộng tương ứng, nhưng cần ghi rõ chúng không phải luật chính của game gốc.

Trong UI, màn `BÁO CÁO HIỆU NĂNG` không dùng số liệu khống: khi bấm `CHẠY TẤT CẢ`, chương trình chạy trực tiếp từng solver đã đăng ký và hiển thị kết quả từ `SearchResult`. Các chỉ số `Visited`, `Generated`, `Time` và `Reason/Details` phải được hiểu là số đo runtime của lần chạy hiện tại. Khi xuất CSV, file `results/algorithm_results.csv` cũng ghi lại các trường này để người chấm có thể đối chiếu.

Các biểu đồ nên dùng trong báo cáo trực quan là biểu đồ cột so sánh thời gian chạy, biểu đồ cột số node visited, biểu đồ cột số node generated và biểu đồ solved/fail. Khi vẽ biểu đồ, cần ghi chú rằng `visited` và `generated` giữa các nhóm thuật toán không luôn có cùng ý nghĩa tuyệt đối.

## 4.4. Ý kiến của nhóm

Việc áp dụng 6 nhóm thuật toán giúp bài toán Squirrels AI Solver được nhìn từ nhiều góc độ. Tìm kiếm mù và tìm kiếm có thông tin phù hợp nhất với puzzle deterministic vì chúng làm việc trực tiếp trên `GameState`, legal action và goal test. Trong đó, A* hoặc BFS/IDS là lựa chọn hợp lý cho solver chính tùy yêu cầu về tối ưu và tài nguyên. Tìm kiếm cục bộ hữu ích để minh họa cách heuristic dẫn đường nhưng cũng cho thấy nguy cơ kẹt. Các nhóm môi trường phức tạp, CSP và đối kháng là những mô hình mở rộng giúp liên hệ lý thuyết AI rộng hơn, nhưng cần trình bày là phiên bản thích nghi hoặc demo, không phải toàn bộ luật gốc của trò chơi.

## 4.5. Hạn chế

Heuristic hiện tại tuy mạnh hơn nearest-hole độc lập vì dùng minimum assignment giữa hạt và lỗ trống, nhưng chưa được chứng minh admissible/consistent cho mọi cấu hình. Một số thuật toán là phiên bản thích nghi, đặc biệt là AND-OR, Belief-State, Minimax, Alpha-Beta và Expectimax. Benchmark hiện mới minh họa trên `starter_01`; cần bổ sung nhiều level hơn để kết luận chắc chắn. UI hiện chạy solver đồng bộ nên thuật toán nặng có thể làm app đứng tạm thời. Log nhiều có thể làm chương trình nặng vì solver vẫn tạo log dài trước khi `SearchResult` cắt bớt để visualizer hiển thị. `LevelManager` đã validate cấu trúc level, nhưng vẫn cần benchmark solvability tự động. Ngoài ra, tài liệu cần tiếp tục thống nhất thuật ngữ: action trong code là dịch một ô, không phải trượt tới vật cản.

## 4.6. Đề xuất cải thiện

Project nên bổ sung benchmark nhiều level và tự động xuất biểu đồ trong report để kết quả thực nghiệm thuyết phục hơn. Level validation nên có thêm bước kiểm tra solvability bằng BFS/A* giới hạn hợp lý. UI có thể cải thiện bằng thread hoặc loading/cancel khi chạy thuật toán nặng. Về AI, có thể phát triển heuristic nâng cao có chứng minh rõ hơn hoặc tách riêng heuristic admissible và heuristic thực dụng. README và báo cáo nên chuẩn hóa cách phân loại "solver chính" và "thuật toán minh họa", đặc biệt với CSP, adversarial và complex environment. Cuối cùng, nên cài `pytest` trong môi trường demo để chạy đầy đủ `python -m pytest tests` trước khi nộp.
