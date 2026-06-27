# Squirrels AI Solver

**Squirrels AI Solver** là ứng dụng Python/Pygame mô phỏng trò chơi logic **Squirrels Go Nuts** và dùng nhiều thuật toán Trí tuệ nhân tạo để giải, trực quan hóa, so sánh quá trình tìm kiếm trong không gian trạng thái.

Project được thiết kế như một đồ án AI: có core game logic, bộ level JSON, nhiều nhóm thuật toán theo tinh thần AIMA, giao diện chơi thử, màn trình diễn thuật toán và màn báo cáo hiệu năng.

## Tổng quan nhanh

| Hạng mục | Nội dung |
|---|---|
| Ngôn ngữ | Python |
| Giao diện | Pygame |
| Bàn cờ | 4x4 |
| Dữ liệu level | `data/book_levels.json` |
| Số level hiện có | 32 level, gồm `starter`, `junior`, `expert`, `master` |
| Entry point | `main.py` |
| Solver interface | `ai/solver_interface.py` |
| Kết quả solver | `ai/search_result.py` |

## Tính năng chính

### Chơi thủ công

Người dùng có thể chọn level, click chọn một mảnh squirrel và dùng phím mũi tên hoặc `W A S D` để di chuyển. Game có reset, undo và popup chiến thắng.

### AI Solver

Người dùng chọn thuật toán từ dropdown, bấm giải AI, xem thống kê số node duyệt, số node sinh, thời gian chạy và replay từng bước lời giải.

### Algorithm Visualizer

Màn hình trình diễn thuật toán cho phép xem từng trạng thái trong log duyệt. Người dùng có thể bấm từng bước, tua lại, tự chạy và cuộn log.

### Performance Report

Màn report chạy toàn bộ thuật toán đã đăng ký trên cùng một level, hiển thị bảng kết quả, biểu đồ số node đã duyệt và hỗ trợ export CSV vào thư mục `results/`.

## Mô hình game trong project

Project mô hình hóa trò chơi thành bài toán tìm kiếm trạng thái:

| Thành phần | Cách biểu diễn |
|---|---|
| State | `GameState`: danh sách pieces, holes, filled holes |
| Piece | `Piece`: id, type, shape, anchor, nut offset, has nut, movable |
| Board | Bàn 4x4, dùng `BOARD_SIZE = 4` |
| Action | Tuple `(piece_id, direction)` |
| Direction | `UP`, `DOWN`, `LEFT`, `RIGHT` |
| Goal | Tất cả squirrel có trong level đã thả hạt |
| State key | `state.encode()` dùng cho visited/explored |

Lưu ý quan trọng về luật di chuyển: trong code hiện tại, mỗi action dịch mảnh **đúng 1 ô** theo hướng đã chọn nếu hợp lệ. Đây là mô hình được core logic và toàn bộ solver sử dụng. Vì vậy khi trình bày đồ án, nên mô tả là "di chuyển/dịch 1 ô" thay vì "trượt cho tới khi gặp vật cản".

Một nước đi hợp lệ khi:

1. Piece tồn tại và được phép di chuyển.
2. Sau khi dịch 1 ô, toàn bộ piece vẫn nằm trong bàn 4x4.
3. Piece không đè lên piece khác.
4. Nếu hạt của squirrel nằm trên một hole chưa filled, hạt rơi xuống hole.

## Thuật toán AI

Tất cả thuật toán được gọi qua `solve(algorithm_name, start_state, rules, **kwargs)` trong `ai/solver_interface.py` và trả về `SearchResult`.

| Nhóm | Thuật toán | File |
|---|---|---|
| Uninformed Search | BFS | `ai/uninformed/bfs.py` |
| Uninformed Search | DFS | `ai/uninformed/dfs.py` |
| Uninformed Search | IDS | `ai/uninformed/ids.py` |
| Informed Search | Greedy Best-First Search | `ai/informed/greedy.py` |
| Informed Search | A* | `ai/informed/astar.py` |
| Informed Search | IDA* | `ai/informed/idastar.py` |
| Heuristic | Minimum-assignment Manhattan nut-to-hole heuristic | `ai/informed/heuristics.py` |
| Local Search | Hill Climbing | `ai/local_search/hill_climbing.py` |
| Local Search | Local Beam Search | `ai/local_search/local_beam.py` |
| Local Search | Simulated Annealing | `ai/local_search/simulated_annealing.py` |
| Complex Environment | AND-OR Search | `ai/complex/and_or_search.py` |
| Complex Environment | Belief-State Search | `ai/complex/belief_state_search.py` |
| Complex Environment | Online Search / LRTA* | `ai/complex/online_search.py` |
| CSP | Backtracking | `ai/csp/backtracking.py` |
| CSP | AC-3 | `ai/csp/ac3.py` |
| CSP | Min-Conflicts | `ai/csp/min_conflicts.py` |
| Adversarial/Stochastic | Minimax | `ai/adversarial/minimax.py` |
| Adversarial/Stochastic | Alpha-Beta Pruning | `ai/adversarial/alpha_beta.py` |
| Adversarial/Stochastic | Expectimax | `ai/adversarial/expectimax.py` |

### Ghi chú học thuật

Một số nhóm thuật toán áp dụng tự nhiên vào game hơn các nhóm khác:

* BFS, DFS, IDS, Greedy, A*, IDA* là các thuật toán phù hợp trực tiếp với bài toán state-space search.
* Hill Climbing, Local Beam và Simulated Annealing dùng heuristic để minh họa local search, không đảm bảo luôn tìm được lời giải.
* CSP được mô hình hóa theo hướng action-plan CSP. Đây là phiên bản thích nghi để phục vụ học thuật.
* Minimax, Alpha-Beta và Expectimax là chế độ minh họa adversarial/stochastic, trong đó flower/blocker được xem như đối thủ hoặc chance node. Đây không phải luật gốc của puzzle.
* AND-OR và Belief-State là mô hình môi trường phức tạp giả lập, dùng để minh họa conditional plan, nondeterminism và uncertainty.

Heuristic hiện tại ghép các hạt chưa rơi với các lỗ trống riêng biệt sao cho tổng khoảng cách Manhattan là nhỏ nhất. Cách này mạnh hơn việc cho từng hạt tự chọn lỗ gần nhất độc lập, nhưng vẫn chưa được chứng minh admissible/consistent cho mọi cấu hình. Vì vậy không nên khẳng định A* luôn tối ưu tuyệt đối; A* tối ưu khi heuristic thỏa điều kiện lý thuyết và không bị giới hạn tài nguyên.

## Cấu trúc thư mục

```text
squirrels_ai_solver/
|-- main.py
|-- requirements.txt
|-- requirements-dev.txt
|-- README.md
|-- verify_core.py
|-- data/
|   |-- book_levels.json
|-- core/
|   |-- constants.py
|   |-- piece.py
|   |-- state.py
|   |-- rules.py
|   |-- level.py
|-- ai/
|   |-- solver_interface.py
|   |-- search_result.py
|   |-- limits.py
|   |-- utils.py
|   |-- uninformed/
|   |-- informed/
|   |-- local_search/
|   |-- complex/
|   |-- csp/
|   |-- adversarial/
|-- ui/
|   |-- screen_manager.py
|   |-- font.py
|   |-- components/
|   |-- renderers/
|   |-- screens/
|-- tests/
|   |-- test_algorithm_smoke.py
|   |-- test_core_rules.py
|   |-- test_heuristics.py
|   |-- test_level_validation.py
|   |-- test_solver_contracts.py
```

## Cài đặt

Yêu cầu:

* Python 3.8 trở lên.
* Pygame 2.x.

Cài dependency:

```bash
pip install -r requirements.txt
```

Nếu dùng virtual environment trên Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Nếu muốn chạy toàn bộ test bằng `pytest`:

```bash
pip install -r requirements-dev.txt
```

## Chạy ứng dụng

```bash
python main.py
```

Nếu máy dùng Python Launcher:

```bash
py main.py
```

## Cách dùng giao diện

1. Mở app bằng `python main.py`.
2. Ở menu chính, chọn một chế độ:
   * `CHƠI GAME (PLAY)`: tự chơi.
   * `AI SOLVER`: chọn thuật toán và replay lời giải.
   * `TRÌNH DIỄN THUẬT TOÁN`: xem log từng bước của solver.
   * `BÁO CÁO HIỆU NĂNG`: so sánh tất cả thuật toán.
3. Chọn nhóm level và level.
4. Với chế độ chơi thủ công:
   * Click một squirrel để chọn.
   * Dùng phím mũi tên hoặc `W A S D` để dịch mảnh 1 ô.
   * Dùng reset/undo khi cần.
5. Với chế độ AI:
   * Chọn thuật toán trong dropdown.
   * Bấm `GIẢI AI` hoặc `BẮT ĐẦU`.
   * Dùng `TRƯỚC`, `TIẾP`, `TỰ CHẠY` để replay.

## Kiểm tra project

Các lệnh nên chạy trước khi nộp hoặc demo:

```bash
python -m compileall .
python verify_core.py
python -m pytest tests
```

Nếu chưa cài `pytest`, có thể chạy smoke test trực tiếp:

```bash
python tests/test_algorithm_smoke.py
```

`verify_core.py` kiểm tra load level, sinh legal actions, apply action và chạy toàn bộ thuật toán đã đăng ký.

`tests/test_algorithm_smoke.py` chạy tất cả solver trên `starter_01` với giới hạn nhỏ, kiểm tra mỗi solver trả `SearchResult` đúng format.

Các test pytest bổ sung kiểm tra luật core, validate level, heuristic matching và contract replay path của các solver chính.

## Dữ liệu level

Level nằm trong:

```text
data/book_levels.json
```

Hiện có 4 nhóm difficulty:

| Difficulty | Số level |
|---|---:|
| starter | 8 |
| junior | 8 |
| expert | 8 |
| master | 8 |

Mỗi level khai báo:

* `id`, `name`, `difficulty`, `target_moves`.
* `holes`: danh sách tọa độ lỗ.
* `pieces`: danh sách squirrel/block với cells, nut và trạng thái hạt.

`LevelManager` tự validate dữ liệu khi load level: kiểm tra overlap, out-of-bounds, duplicate id, duplicate hole, nut không nằm trong piece và level không có squirrel. Phần còn nên bổ sung nếu muốn chặt hơn là kiểm tra solvability tự động bằng benchmark giới hạn.

## SearchResult

Mọi solver trả về object `SearchResult` gồm:

| Field | Ý nghĩa |
|---|---|
| `algorithm` | Tên thuật toán |
| `solved` | Có tìm được lời giải hợp lệ không |
| `path` | Danh sách action để replay |
| `visited_count` | Số node/state/đơn vị đã duyệt |
| `generated_count` | Số successor/candidate sinh ra |
| `elapsed_time` | Thời gian chạy |
| `steps` | Log state từng bước cho visualizer |
| `extra` | Metadata riêng của thuật toán |

Lưu ý: `visited_count` và `generated_count` giữa các nhóm thuật toán không luôn có cùng ý nghĩa tuyệt đối. Khi viết báo cáo, nên dùng chúng như chỉ số tham khảo trong từng nhóm thuật toán.

## Gợi ý demo khi thuyết trình

Nên demo theo thứ tự:

1. Chọn một level `starter`.
2. Chạy BFS để giải thích tìm kiếm mù và lời giải nông nhất với cost 1.
3. Chạy A* để so sánh informed search với BFS.
4. Mở Algorithm Visualizer để xem log từng bước.
5. Chạy Hill Climbing hoặc Simulated Annealing để nói về local search.
6. Mở Report Screen để xuất bảng so sánh.
7. Chỉ giới thiệu CSP/adversarial/complex như phần mở rộng học thuật.

## Kết luận

Squirrels AI Solver là một project phù hợp để trình bày bài toán tìm kiếm trong AI: có mô hình trạng thái rõ, nhiều thuật toán, UI trực quan và màn report so sánh. Để đạt điểm cao hơn khi bảo vệ, nên ưu tiên chạy test đầy đủ, bổ sung benchmark solvability và mô tả cẩn thận những thuật toán mang tính thích nghi.
