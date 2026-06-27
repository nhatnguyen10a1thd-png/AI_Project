# Squirrels Go Nuts! — AI Search Solver

## 🐿️ Giới thiệu dự án
**Squirrels Go Nuts! - AI Search Solver** là một ứng dụng mô phỏng và tự động giải quyết trò chơi giải đố logic "Squirrels Go Nuts" (Sóc giấu hạt dẻ) bằng các thuật toán tìm kiếm trong lĩnh vực Trí Tuệ Nhân Tạo (AI).

Dự án được xây dựng hoàn toàn bằng **Python** và sử dụng thư viện đồ họa **Pygame**, cho phép người dùng không chỉ tự tay trải nghiệm các câu đố mà còn quan sát cách AI phân tích không gian trạng thái và tìm ra con đường ngắn nhất để chiến thắng.

## ✨ Các tính năng chính
1. **Chế độ Tự Chơi (Manual Play):**
   - Người chơi có thể tự mình di chuyển các chú Sóc bằng chuột và bàn phím.
   - Cung cấp các công cụ hỗ trợ trải nghiệm như `Hoàn tác` (Undo), `Đặt lại` (Reset) và chuyển đổi level nhanh chóng.

2. **Chế độ AI Giải Đố & Trình Diễn (AI Solver & Visualizer):**
   - Ứng dụng tích hợp nhiều thuật toán tìm kiếm kinh điển và hiện đại:
     - **A*** (A-Star Search - Thuật toán tìm kiếm tối ưu bằng Heuristic)
     - **BFS** (Breadth-First Search - Tìm kiếm theo chiều rộng)
     - **IDS** (Iterative Deepening Search - Tìm kiếm sâu dần)
     - **Greedy** (Greedy Best-First Search - Tìm kiếm tham lam)
     - **Hill Climbing** và **Simulated Annealing** (Local Search)
     - **Minimax** và **Alpha-Beta** (Adversarial Search)
     - **Backtracking** và **Min-Conflicts** (CSP)
     - **AND-OR Search** và **Belief-State Search** (Complex Search)
   - Người dùng có thể xem được chi tiết từng bước mà thuật toán đã duyệt qua (Log duyệt) và nhấn `TỰ CHẠY` để AI thực hiện các bước giải trực quan trên màn hình.

3. **Báo Cáo Hiệu Năng (Performance Report):**
   - Chạy đồng loạt tất cả thuật toán để đánh giá hiệu suất trên cùng một màn chơi.
   - Hiển thị trực quan qua biểu đồ số lượng nút đã duyệt (Visited Nodes), số bước giải (Path Length) và thời gian thực thi (ms).
   - Hỗ trợ **xuất file báo cáo .csv** để lưu trữ và phân tích số liệu chuyên sâu.

## 🛠️ Yêu cầu hệ thống
- **Python 3.8** trở lên.
- Thư viện **Pygame** (Phiên bản `2.x` trở lên).

## 🚀 Hướng dẫn cài đặt và vận hành

1. **Cài đặt thư viện yêu cầu:**
   Mở Terminal hoặc Command Prompt, chạy lệnh sau để cài đặt Pygame (nếu máy tính của bạn chưa có):
   ```bash
   pip install pygame
   ```

2. **Khởi chạy ứng dụng:**
   Mở Terminal tại thư mục `squirrels_ai_solver` (thư mục chứa mã nguồn dự án) và chạy file `main.py`:
   ```bash
   python main.py
   ```

## 🎮 Cách tương tác với trò chơi

- **Tại Menu Chính:**
  - Nhấp vào `TỰ CHƠI` nếu bạn muốn tự mình giải đố.
  - Nhấp vào `TRÌNH DIỄN THUẬT TOÁN` nếu muốn xem AI tự động chạy và biểu diễn thuật toán tìm kiếm.
  - Nhấp vào `BÁO CÁO HIỆU NĂNG` để đánh giá sức mạnh của các thuật toán.

- **Luật di chuyển (áp dụng cả khi tự chơi):**
  - **Mục tiêu:** Đẩy toàn bộ các chú Sóc sao cho chúng thả được tất cả hạt dẻ xuống các lỗ trên bàn cờ.
  - **Di chuyển:** Nhấp chuột vào một chú Sóc để chọn, sau đó dùng các phím mũi tên (`Lên`, `Xuống`, `Trái`, `Phải`) hoặc `W A S D` để trượt chú Sóc.
  - **Quy tắc:** Sóc sẽ trượt thẳng theo hướng đã chọn và chỉ dừng lại khi gặp vật cản (vách bàn cờ, một mảnh khác hoặc bông hoa đỏ). Nếu sóc trượt ngang qua một cái lỗ chưa có hạt dẻ, hạt dẻ sẽ rơi xuống. Các chú Sóc có thể trượt an toàn đi ngang qua các lỗ đã bị lấp kín hạt dẻ. Bông hoa đỏ là chướng ngại vật cố định không thể dịch chuyển.

- **Sử dụng AI:**
  - Trong quá trình chơi hoặc ở màn hình trình diễn, chọn tên một thuật toán từ Dropdown (danh sách xổ xuống) ở bảng điều khiển bên phải.
  - Nhấn `BẮT ĐẦU` / `GIẢI AI` để hệ thống tính toán.
  - Dùng các nút `< TRƯỚC` hoặc `TIẾP >` để tua từng bước chạy của máy, hoặc nhấn `> TỰ CHẠY` để chương trình tự trình diễn đến bước cuối cùng.

## 📁 Cấu trúc thư mục

Để dễ dàng nắm bắt mã nguồn, dự án được chia thành các thành phần cụ thể:
- `main.py`: Điểm bắt đầu của ứng dụng, chứa vòng lặp trò chơi (game loop) và thiết lập môi trường.
- `core/`: Chứa các quy tắc vật lý cơ bản (`rules.py`), quản lý level (`level.py`) và các mô hình dữ liệu (`state.py`, `piece.py`).
- `ai/`: Trung tâm não bộ của trò chơi, bao gồm mã nguồn cho các nhóm thuật toán, đánh giá heuristic (`informed/heuristics.py`) và theo dõi kết quả tìm kiếm (`search_result.py`).
- `ui/`: Toàn bộ mã nguồn liên quan đến hình ảnh và giao diện người dùng. Được chia nhỏ thành:
  - `screens/`: Quản lý các chế độ màn hình (Menu, Game, Report, v.v.).
  - `components/`: Các thành phần tái sử dụng (Nút bấm, Danh sách, Modal, Thanh cuộn, Toast thông báo).
  - `renderers/`: Phụ trách hiển thị đồ họa chi tiết cho bàn cờ và mảnh ghép.
- `data/`: Nơi lưu trữ thông tin vị trí các màn chơi (định nghĩa cấu trúc level).

---
*Dự án Squirrels AI Solver là một công cụ trực quan và thực tế để kiểm chứng hiệu năng, đồng thời học tập, nghiên cứu về Trí Tuệ Nhân Tạo (Bài toán tìm kiếm không gian trạng thái - State Space Search).*
