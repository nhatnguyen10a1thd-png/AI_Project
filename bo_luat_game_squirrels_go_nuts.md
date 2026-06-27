# Bộ luật game Squirrels Go Nuts

## 1. Bàn cờ

Game sử dụng bàn cờ dạng lưới **4×4**.

Quy ước tọa độ trong code:

```text
(0,0) (0,1) (0,2) (0,3)
(1,0) (1,1) (1,2) (1,3)
(2,0) (2,1) (2,2) (2,3)
(3,0) (3,1) (3,2) (3,3)
```

Bàn cờ có **4 lỗ cố định**:

```python
HOLES = {
    (0, 2),
    (1, 0),
    (2, 1),
    (3, 3)
}
```

Các lỗ **không chặn đường đi**. Mảnh ghép vẫn có thể trượt qua hoặc đứng trên ô có lỗ.

---

## 2. Các mảnh trong game

Game có 5 mảnh chính:

| Mảnh | Loại | Có hạt dẻ không | Vai trò |
|---|---|---:|---|
| Sóc nâu | Squirrel piece | Có | Đưa hạt dẻ vào lỗ |
| Sóc đen | Squirrel piece | Có | Đưa hạt dẻ vào lỗ |
| Sóc trắng | Squirrel piece | Có | Đưa hạt dẻ vào lỗ |
| Sóc cam | Squirrel piece | Có | Đưa hạt dẻ vào lỗ |
| Hoa đỏ | Block piece | Không | Mảnh cản |

Mỗi con sóc ban đầu giữ **1 hạt dẻ**.

Mảnh hoa đỏ chỉ là **mảnh cản**, không cần đưa vào lỗ.

---

## 3. Luật di chuyển

Mỗi lượt, người chơi hoặc AI được chọn **1 mảnh** và trượt 1 ô mảnh đó theo **1 trong 4 hướng**:

```text
UP
DOWN
LEFT
RIGHT
```

Action trong code nên viết dạng:

```text
Move(piece_id, direction)
```

Ví dụ:

```text
Move("white", "RIGHT")
Move("black", "DOWN")
Move("flower", "LEFT")
```

Một nước đi hợp lệ khi thỏa mãn tất cả điều kiện sau:

```text
1. Mảnh di chuyển đúng 1 ô mỗi lần.
2. Mảnh chỉ được đi ngang hoặc dọc.
3. Mảnh không được đi chéo.
4. Mảnh không được xoay.
5. Mảnh không được nhấc lên.
6. Sau khi di chuyển, toàn bộ mảnh vẫn nằm trong bàn cờ 4×4.
7. Sau khi di chuyển, mảnh không đè lên mảnh khác.
```

---

## 4. Luật va chạm

Mỗi mảnh chiếm một hoặc nhiều ô trên bàn cờ.

Một nước đi bị xem là **không hợp lệ** nếu sau khi di chuyển:

```text
- Có ô của mảnh nằm ngoài bàn cờ.
- Có ô của mảnh trùng với ô đang bị mảnh khác chiếm.
```

Ví dụ:

```text
Nếu Sóc trắng chiếm (2,1), (2,2)
và Sóc cam đang chiếm (2,3)

thì Move("white", "RIGHT") là sai
vì Sóc trắng sẽ đè lên ô (2,3).
```

---

## 5. Luật hạt dẻ rơi vào lỗ

Mỗi con sóc có một vị trí hạt dẻ tương đối trên mảnh, gọi là:

```text
nut_offset
```

Vị trí thật của hạt dẻ:

```text
nut_position = piece_anchor + nut_offset
```

Sau mỗi lần di chuyển hợp lệ, chương trình kiểm tra:

```text
Nếu nut_position nằm đúng trên một ô lỗ
→ hạt dẻ rơi xuống lỗ
→ has_nut = False
```

Ví dụ:

```text
Sóc trắng còn hạt.
Hạt của Sóc trắng đang ở ô (2,1).
Mà (2,1) là lỗ.
=> Hạt rơi.
=> white.has_nut = False.
```

Sau khi hạt đã rơi:

```text
- Con sóc vẫn tiếp tục tồn tại trên bàn cờ.
- Con sóc vẫn có thể di chuyển bình thường.
- Con sóc không còn hạt để rơi lần nữa.
```

---

## 6. Luật thắng

Người chơi thắng khi **4 hạt dẻ của 4 con sóc đều đã rơi vào lỗ**.

Điều kiện goal:

```python
brown.has_nut == False
black.has_nut == False
white.has_nut == False
orange.has_nut == False
```

Có thể viết trong code:

```python
def is_goal(state):
    for piece in state.pieces:
        if piece.type == "squirrel" and piece.has_nut:
            return False
    return True
```

Mảnh hoa đỏ không ảnh hưởng đến điều kiện thắng.

---

## 7. Luật thua hoặc thất bại

Game gốc không có trạng thái thua trực tiếp.

Nhưng trong thuật toán AI, có thể xem là thất bại nếu:

```text
1. Không còn trạng thái nào để xét.
2. Frontier rỗng.
3. Thuật toán vượt quá giới hạn thời gian.
4. Thuật toán vượt quá giới hạn số node.
5. Local Search bị kẹt và không tìm được goal.
```

---

## 8. Luật chống lặp trạng thái

Để tránh việc AI chạy vô hạn, mỗi trạng thái đã xét phải được lưu vào `visited`.

Ví dụ vòng lặp nguy hiểm:

```text
Move("white", "RIGHT")
Move("white", "LEFT")
Move("white", "RIGHT")
Move("white", "LEFT")
...
```

Cách xử lý:

```python
if next_state in visited:
    # bỏ qua
    pass
else:
    visited.add(next_state)
    frontier.append(next_state)
```

Bắt buộc áp dụng cho:

```text
BFS
DFS
Greedy
A*
Backtracking
AND-OR Search
Belief-State Search
```

---

## 9. Bộ luật formal để đưa vào báo cáo

> Trò chơi Squirrels Go Nuts được mô hình hóa trên bàn cờ 4×4 gồm các mảnh ghép có hình dạng cố định. Mỗi lượt, người chơi chọn một mảnh và trượt mảnh đó theo một trong bốn hướng: lên, xuống, trái hoặc phải. Một nước đi hợp lệ khi mảnh không vượt ra ngoài bàn cờ, không va chạm với mảnh khác và không thay đổi hình dạng. Bốn con sóc ban đầu giữ bốn hạt dẻ. Sau mỗi nước đi, nếu vị trí hạt dẻ của một con sóc trùng với vị trí lỗ trên bàn cờ, hạt dẻ sẽ rơi xuống và được xem là hoàn thành. Trò chơi kết thúc khi toàn bộ bốn hạt dẻ đã rơi vào bốn lỗ. Mảnh hoa đỏ chỉ đóng vai trò vật cản và không phải là mục tiêu của trò chơi.

---

## 10. Bộ luật dạng code-ready

```python
BOARD_SIZE = 4

HOLES = {
    (0, 2),
    (1, 0),
    (2, 1),
    (3, 3)
}

DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}

RULES = {
    "can_move_diagonal": False,
    "can_rotate_piece": False,
    "can_lift_piece": False,
    "move_step": 1,
    "holes_block_movement": False,
    "flower_is_goal": False,
    "squirrel_can_move_after_drop": True,
    "goal": "all_4_acorns_dropped"
}
```

---

## 11. Tóm tắt ngắn gọn

```text
1. Bàn cờ 4×4.
2. Có 4 lỗ cố định.
3. Có 4 con sóc, mỗi con giữ 1 hạt.
4. Có 1 mảnh hoa đỏ làm vật cản.
5. Mỗi lượt chọn 1 mảnh và trượt lên/xuống/trái/phải.
6. Không được xoay, nhấc, đi chéo.
7. Không được ra ngoài bàn.
8. Không được đè lên mảnh khác.
9. Nếu hạt dẻ nằm đúng trên lỗ thì hạt rơi.
10. Thắng khi cả 4 hạt đều rơi vào lỗ.
```

---

## 12. Gợi ý tên file code liên quan

Bộ luật này nên được triển khai trong file:

```text
core/rules.py
```

Các hàm quan trọng nên có:

```python
def legal_actions(state):
    pass

def can_move(state, piece_id, direction):
    pass

def apply_action(state, action):
    pass

def check_nut_drop(state):
    pass

def is_goal(state):
    pass
```
