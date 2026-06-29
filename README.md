# Squirrels AI Solver

Ứng dụng Python/Pygame mô phỏng trò chơi logic **Squirrels Go Nuts** trên bàn cờ 4×4, tích hợp **18 thuật toán AI** để tự động giải puzzle, trực quan hóa quá trình tìm kiếm và so sánh hiệu năng giữa các thuật toán.

## Mục lục

- [Tính năng](#tính-năng)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Chạy ứng dụng](#chạy-ứng-dụng)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [Mô hình bài toán](#mô-hình-bài-toán)
- [Thuật toán AI](#thuật-toán-ai)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Dữ liệu level](#dữ-liệu-level)
- [SearchResult](#searchresult)
- [Kiểm thử](#kiểm-thử)

## Tính năng

- **Chơi thủ công** — Chọn level, click chọn mảnh squirrel và di chuyển bằng phím mũi tên hoặc `W A S D`. Hỗ trợ reset và undo.
- **AI Solver** — Chọn thuật toán từ dropdown, giải tự động và replay từng bước lời giải. Hiển thị thống kê số node duyệt, số node sinh và thời gian chạy.
- **Algorithm Visualizer** — Trình diễn từng trạng thái trong log duyệt của thuật toán. Hỗ trợ bước tiến/lùi, tự chạy và cuộn log.
- **Performance Report** — Chạy toàn bộ thuật toán trên cùng một level, hiển thị bảng kết quả, biểu đồ so sánh và hỗ trợ export CSV vào thư mục `results/`.

## Yêu cầu hệ thống

- Python >= 3.8
- Pygame >= 2.0

## Cài đặt

```bash
# Clone repository
git clone https://github.com/nhatnguyen10a1thd-png/AI_Project
cd AI_Project

# (Khuyến nghị) Tạo virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# (Tùy chọn) Cài thêm dev dependencies để chạy test
pip install -r requirements-dev.txt
```

## Chạy ứng dụng

```bash
python main.py
```

## Hướng dẫn sử dụng

### Menu chính

Ứng dụng có 4 chế độ:

| Chế độ | Mô tả |
|---|---|
| **Chơi Game** | Tự chơi puzzle bằng tay |
| **AI Solver** | Chọn thuật toán và xem lời giải tự động |
| **Trình diễn thuật toán** | Xem log từng bước của quá trình tìm kiếm |
| **Báo cáo hiệu năng** | So sánh hiệu năng tất cả thuật toán trên cùng level |

### Chơi thủ công

1. Chọn nhóm level và level cụ thể.
2. Click vào một squirrel để chọn.
3. Dùng phím mũi tên hoặc `W A S D` để di chuyển mảnh 1 ô.
4. Dùng nút **Reset** / **Undo** khi cần.

### AI Solver

1. Chọn level và thuật toán từ dropdown.
2. Bấm **Giải AI**.
3. Dùng **Trước**, **Tiếp**, **Tự chạy** để replay lời giải.

## Mô hình bài toán

Project mô hình hóa trò chơi thành bài toán **tìm kiếm trong không gian trạng thái**:

| Thành phần | Biểu diễn |
|---|---|
| **State** | `GameState` — danh sách pieces, holes, filled holes |
| **Piece** | `Piece` — id, type, shape, anchor, nut offset, has\_nut, movable |
| **Board** | Bàn 4×4 (`BOARD_SIZE = 4`) |
| **Action** | Tuple `(piece_id, direction)` |
| **Direction** | `UP`, `DOWN`, `LEFT`, `RIGHT` |
| **Goal test** | Tất cả squirrel đã thả hạt xuống hole |
| **State encoding** | `state.encode()` — dùng cho tập visited/explored |

### Luật di chuyển

- Mỗi action dịch mảnh **đúng 1 ô** theo hướng đã chọn.
- Piece phải tồn tại và được phép di chuyển (`movable = True`).
- Sau khi dịch, toàn bộ cells của piece phải nằm trong bàn 4×4.
- Piece không được đè lên piece khác.
- Nếu hạt của squirrel rơi vào vị trí hole chưa filled → hạt rơi xuống hole.

## Thuật toán AI

Tất cả thuật toán được gọi thống nhất qua `solve(algorithm_name, start_state, rules, **kwargs)` trong `ai/solver_interface.py` và trả về đối tượng `SearchResult`.

### Uninformed Search

| Thuật toán | File |
|---|---|
| BFS | `ai/uninformed/bfs.py` |
| DFS | `ai/uninformed/dfs.py` |
| IDS (Iterative Deepening Search) | `ai/uninformed/ids.py` |

### Informed Search

| Thuật toán | File |
|---|---|
| Greedy Best-First Search | `ai/informed/greedy.py` |
| A* | `ai/informed/astar.py` |
| IDA* | `ai/informed/idastar.py` |

**Heuristic:** Minimum-assignment Manhattan distance — ghép các hạt chưa rơi với các hole trống sao cho tổng khoảng cách Manhattan là nhỏ nhất (`ai/informed/heuristics.py`).

### Local Search

| Thuật toán | File |
|---|---|
| Hill Climbing | `ai/local_search/hill_climbing.py` |
| Local Beam Search | `ai/local_search/local_beam.py` |
| Simulated Annealing | `ai/local_search/simulated_annealing.py` |

### Complex Environment

| Thuật toán | File |
|---|---|
| AND-OR Search | `ai/complex/and_or_search.py` |
| Belief-State Search | `ai/complex/belief_state_search.py` |
| Online Search (LRTA*) | `ai/complex/online_search.py` |

### CSP (Constraint Satisfaction Problem)

| Thuật toán | File |
|---|---|
| Backtracking | `ai/csp/backtracking.py` |
| AC-3 | `ai/csp/ac3.py` |
| Min-Conflicts | `ai/csp/min_conflicts.py` |

### Adversarial / Stochastic Search

| Thuật toán | File |
|---|---|
| Minimax | `ai/adversarial/minimax.py` |
| Alpha-Beta Pruning | `ai/adversarial/alpha_beta.py` |
| Expectimax | `ai/adversarial/expectimax.py` |

## Cấu trúc thư mục

```
AI_Project/
├── main.py                    # Entry point
├── requirements.txt
├── requirements-dev.txt
├── verify_core.py             # Script kiểm tra nhanh core logic
├── data/
│   └── book_levels.json       # 32 levels (starter, junior, expert, master)
├── core/
│   ├── constants.py           # Hằng số game (BOARD_SIZE, directions, ...)
│   ├── piece.py               # Lớp Piece
│   ├── state.py               # Lớp GameState
│   ├── rules.py               # Luật di chuyển và goal test
│   └── level.py               # Load và validate level từ JSON
├── ai/
│   ├── solver_interface.py    # Interface chung cho tất cả solver
│   ├── search_result.py       # Lớp SearchResult
│   ├── limits.py              # Giới hạn tài nguyên (node, thời gian)
│   ├── utils.py               # Utility functions
│   ├── uninformed/            # BFS, DFS, IDS
│   ├── informed/              # Greedy, A*, IDA*, heuristics
│   ├── local_search/          # Hill Climbing, Local Beam, SA
│   ├── complex/               # AND-OR, Belief-State, Online Search
│   ├── csp/                   # Backtracking, AC-3, Min-Conflicts
│   └── adversarial/           # Minimax, Alpha-Beta, Expectimax
├── ui/
│   ├── screen_manager.py      # Quản lý chuyển màn hình
│   ├── font.py                # Quản lý font
│   ├── components/            # UI components tái sử dụng
│   ├── renderers/             # Render game board, pieces
│   └── screens/               # Các màn hình (menu, play, solver, ...)
└── tests/
    ├── test_algorithm_smoke.py
    ├── test_core_rules.py
    ├── test_heuristics.py
    ├── test_level_validation.py
    └── test_solver_contracts.py
```

## Dữ liệu level

Level được lưu trong `data/book_levels.json`, gồm 32 level chia thành 4 nhóm:

| Difficulty | Số level |
|---|---:|
| Starter | 8 |
| Junior | 8 |
| Expert | 8 |
| Master | 8 |

Mỗi level bao gồm:
- `id`, `name`, `difficulty`, `target_moves`
- `holes` — danh sách tọa độ các hole trên bàn cờ
- `pieces` — danh sách squirrel/block với cells, vị trí nut và trạng thái

`LevelManager` tự động validate dữ liệu khi load: kiểm tra overlap, out-of-bounds, duplicate id, duplicate hole, nut không thuộc piece và level thiếu squirrel.

## SearchResult

Mọi solver trả về đối tượng `SearchResult` với các field:

| Field | Kiểu | Mô tả |
|---|---|---|
| `algorithm` | `str` | Tên thuật toán |
| `solved` | `bool` | Có tìm được lời giải không |
| `path` | `list` | Danh sách action để replay |
| `visited_count` | `int` | Số node/state đã duyệt |
| `generated_count` | `int` | Số successor/candidate đã sinh |
| `elapsed_time` | `float` | Thời gian chạy (giây) |
| `steps` | `list` | Log state từng bước (cho visualizer) |
| `extra` | `dict` | Metadata riêng của thuật toán |

## Kiểm thử

```bash
# Kiểm tra cú pháp toàn bộ project
python -m compileall .

# Kiểm tra nhanh core logic và tất cả solver
python verify_core.py

# Chạy toàn bộ test suite (cần pytest)
python -m pytest tests/

# Chạy smoke test riêng lẻ (không cần pytest)
python tests/test_algorithm_smoke.py
```

| Test file | Nội dung kiểm tra |
|---|---|
| `test_algorithm_smoke.py` | Chạy tất cả solver trên `starter_01`, kiểm tra format `SearchResult` |
| `test_core_rules.py` | Luật di chuyển, collision, goal test |
| `test_heuristics.py` | Heuristic matching nut-to-hole |
| `test_level_validation.py` | Validate dữ liệu level JSON |
| `test_solver_contracts.py` | Contract replay path của các solver chính |
