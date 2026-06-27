# ui/screens/game_screen.py
import pygame
import time
from ui.screen_manager import ScreenBase
from ui.components.button import Button
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast
from ui.components.modal import Modal
from ui.components.titlebar import TITLEBAR_H
from ui.renderers.board_renderer import draw_board, get_cell_size
from core.rules import BoardRules
from core.constants import BG_COLOR, PANEL_COLOR, TEXT_COLOR, TEXT_MUTED, BORDER_COLOR
from ai.solver_interface import ALGORITHMS, solve

ADVERSARIAL_ALGORITHMS = {"Minimax", "Alpha-Beta"}

class GameScreen(ScreenBase):
    """Màn hình chơi game chính hỗ trợ cả chế độ tự chơi và chế độ chạy AI."""
    def __init__(self, app):
        super().__init__(app)
        self.mode = "play"  # "play" or "ai"
        self.difficulty = "starter"
        self.level_id = "starter_01"
        self.level_meta = None
        self.initial_state = None
        self.current_state = None
        
        self.rules = BoardRules()
        self.selected_piece_id = None
        self.history = []  # Stack of GameState copies for Undo
        
        # Animations dictionary: {piece_id: (progress, start_anchor, end_anchor)}
        self.active_animation = {}
        self.anim_duration = 0.18 # seconds
        self.anim_timer = 0.0
        self.animating_action = None # Keep track of action being animated
        
        # AI playback variables
        self.ai_result = None
        self.ai_path = []
        self.ai_start_state = None
        self.ai_step_idx = 0
        self.is_playing_ai = False
        self.ai_play_timer = 0.0
        self.ai_play_speed = 0.6 # seconds per step
        
        # UI components
        self.buttons = []
        self.right_panel_buttons = []
        self.algo_dropdown = None
        self.toast = Toast(self.app.fonts["body"])
        self.win_modal = None
        
        self.setup_ui()

    def setup_ui(self):
        font_btn  = self.app.fonts["button"]
        font_body = self.app.fonts["body_bold"]
        W = self.app.width
        H = self.app.height
        top    = TITLEBAR_H          # nội dung bắt đầu từ đây
        btn_y  = H - 65              # bottom controls
        hdr_y  = top + 10            # header text y
        sub_y  = top + 42            # subtitle y
        # Right panel AI controls bắt đầu từ dưới header
        ai_ctrl_y = top + 92

        # Bottom controls (general)
        self.btn_menu = Button(
            rect=(30, btn_y, 150, 45),
            text="< MENU",
            font=font_body,
            callback=lambda: self.app.switch_to_screen("main_menu"),
            color=(120, 115, 105)
        )
        self.btn_levels = Button(
            rect=(195, btn_y, 150, 45),
            text="CHỌN LEVEL",
            font=font_body,
            callback=lambda: self.app.switch_to_screen("level_select", mode=self.mode),
            color=(79, 110, 138)
        )
        self.btn_reset = Button(
            rect=(360, btn_y, 130, 45),
            text="ĐẶT LẠI",
            font=font_body,
            callback=self.reset_level,
            color=(211, 47, 47)
        )
        self.btn_undo = Button(
            rect=(505, btn_y, 130, 45),
            text="HOÀN TÁC",
            font=font_body,
            callback=self.undo_move,
            color=(245, 124, 0)
        )

        # Right panel for AI Mode
        rp_x = int(W * 0.56)
        self.algo_dropdown = Dropdown(
            rect=(rp_x, ai_ctrl_y, 260, 40),
            options=list(ALGORITHMS.keys()),
            font=self.app.fonts["body_bold"],
            default_index=2
        )
        self.btn_solve = Button(
            rect=(rp_x + 275, ai_ctrl_y, 120, 40),
            text="GIẢI AI",
            font=font_btn,
            callback=self.run_ai_solver,
            color=(46, 125, 50)
        )
        self.btn_ai_prev = Button(
            rect=(rp_x, btn_y, 100, 45),
            text="< TRƯỚC",
            font=font_body,
            callback=self.ai_prev_step,
            color=(120, 115, 105)
        )
        self.btn_ai_next = Button(
            rect=(rp_x + 115, btn_y, 100, 45),
            text="TIẾP >",
            font=font_body,
            callback=self.ai_next_step,
            color=(79, 110, 138)
        )
        self.btn_ai_play = Button(
            rect=(rp_x + 230, btn_y, 130, 45),
            text="> TỰ CHẠY",
            font=font_body,
            callback=self.ai_toggle_play,
            color=(46, 125, 50)
        )
        # Lưu các y cơ sở để draw() dùng lại
        self._hdr_y      = hdr_y
        self._sub_y      = sub_y
        self._ai_ctrl_y  = ai_ctrl_y
        self._top        = top

    def update_layout(self):
        W = self.app.width
        H = self.app.height
        btn_y  = H - 65
        rp_x   = int(W * 0.56)

        self.btn_menu.rect.y = btn_y
        self.btn_levels.rect.y = btn_y
        self.btn_reset.rect.y = btn_y
        self.btn_undo.rect.y = btn_y
        
        self.algo_dropdown.rect.x = rp_x
        self.btn_solve.rect.x = rp_x + 275
        
        self.btn_ai_prev.rect.x = rp_x
        self.btn_ai_prev.rect.y = btn_y
        self.btn_ai_next.rect.x = rp_x + 115
        self.btn_ai_next.rect.y = btn_y
        self.btn_ai_play.rect.x = rp_x + 230
        self.btn_ai_play.rect.y = btn_y

    def on_enter(self, **kwargs):
        self.difficulty = kwargs.get("difficulty", "starter")
        self.level_id = kwargs.get("level_id", "starter_01")
        self.mode = kwargs.get("mode", "play")
        
        # Load Level Data
        self.level_meta, self.initial_state = self.app.level_manager.load_level(self.difficulty, self.level_id)
        self.current_state = self.initial_state.clone()
        
        # Reset gameplay states
        self.selected_piece_id = None
        self.history = []
        self.active_animation = {}
        self.animating_action = None
        self.ai_result = None
        self.ai_path = []
        self.ai_start_state = None
        self.ai_step_idx = 0
        self.is_playing_ai = False
        self.ai_play_timer = 0.0
        
        # Rebuild UI to fit current window size
        self.setup_ui()
        
        # Adjust buttons visibility based on mode
        self.btn_undo.is_enabled = (self.mode == "play")
        
        # Setup Win Modal - căn giữa theo kích thước màn hình thực tế
        win_buttons = [
            {"text": "MENU CHÍNH", "callback": lambda: self.app.switch_to_screen("main_menu"), "color": (120, 115, 105)},
            {"text": "LEVEL TIẾP", "callback": self.next_level_button, "color": (46, 125, 50)},
            {"text": "CHƠI LẠI",  "callback": self.reset_level,        "color": (139, 115, 85)},
        ]
        self.win_modal = Modal(
            title="CHIẾN THẮNG!",
            message_lines=["Xin chúc mừng!", "Bạn đã đưa được tất cả hạt dẻ", "vào các lỗ cờ thành công."],
            font_title=self.app.fonts["title"],
            font_body=self.app.fonts["body"],
            font_btn=self.app.fonts["body_bold"],
            buttons_config=win_buttons,
            screen_w=self.app.width,
            screen_h=self.app.height,
        )

    def reset_level(self):
        self.current_state = self.initial_state.clone()
        self.selected_piece_id = None
        self.history = []
        self.active_animation = {}
        self.animating_action = None
        self.ai_step_idx = 0
        self.ai_play_timer = 0.0
        self.set_ai_playing(False)
        if self.win_modal:
            self.win_modal.active = False
        self.toast.show("Đã đặt lại màn chơi.")

    def next_level_button(self):
        self.win_modal.active = False
        # Find next level index
        levels = self.app.level_manager.get_levels_by_difficulty(self.difficulty)
        curr_idx = next(i for i, l in enumerate(levels) if l["id"] == self.level_id)
        if curr_idx + 1 < len(levels):
            next_lvl = levels[curr_idx + 1]
            self.app.switch_to_screen("game", difficulty=self.difficulty, level_id=next_lvl["id"], mode=self.mode)
        else:
            self.toast.show("Bạn đã hoàn thành level cuối cùng trong nhóm này!")
            self.app.switch_to_screen("level_select", mode=self.mode)

    def undo_move(self):
        if not self.history:
            self.toast.show("Không còn nước đi nào để hoàn tác.")
            return
        self.current_state = self.history.pop()
        self.selected_piece_id = None
        self.active_animation = {}
        self.animating_action = None
        self.toast.show("Đã hoàn tác.")

    def run_ai_solver(self):
        algo = self.algo_dropdown.get_selected()
        self.toast.show(f"Đang giải bằng {algo}...")
        
        # Run solver
        self.ai_start_state = self.current_state.clone()
        self.ai_result = solve(algo, self.ai_start_state, self.rules)
        has_adversarial_playout = algo in ADVERSARIAL_ALGORITHMS and bool(self.ai_result.path)
        if self.ai_result.solved or has_adversarial_playout:
            self.ai_path = self.ai_result.path
            self.ai_step_idx = 0
            self.ai_play_timer = 0.0
            self.current_state = self.ai_start_state.clone()
            self.selected_piece_id = None
            self.active_animation = {}
            self.animating_action = None
            self.set_ai_playing(has_adversarial_playout)
            if self.ai_result.solved:
                self.toast.show(f"Đã giải thành công, có {len(self.ai_path)} bước.")
            else:
                self.toast.show(f"Chưa thắng goal, có {len(self.ai_path)} nước mô phỏng đối kháng.")
            return

        self.ai_path = []
        self.ai_play_timer = 0.0
        self.set_ai_playing(False)
        reason = self.ai_result.extra.get("reason") if self.ai_result else None
        if self.ai_result and self.ai_result.extra.get("invalid_solution_path"):
            reason = "invalid_solution_path"
        suffix = f" ({reason})" if reason else ""
        self.toast.show(f"Thuật toán {algo} không tìm được lời giải{suffix}.")
        return

    def ai_next_step(self):
        if not self.ai_path or self.ai_step_idx >= len(self.ai_path):
            self.toast.show("Không còn bước nào tiếp theo.")
            return
        
        act = self.ai_path[self.ai_step_idx]
        self.trigger_piece_animation(act)
        self.ai_step_idx += 1

    def ai_prev_step(self):
        if self.ai_step_idx <= 0:
            self.toast.show("Đang ở trạng thái bắt đầu giải.")
            return
            
        self.ai_step_idx -= 1
        # To go back, we reset to starting state and fast forward to current index
        temp_state = (self.ai_start_state or self.initial_state).clone()
        for i in range(self.ai_step_idx):
            temp_state = self.rules.apply_action(temp_state, self.ai_path[i])
        self.current_state = temp_state
        self.selected_piece_id = None
        self.active_animation = {}
        self.toast.show(f"Trở lại bước {self.ai_step_idx}")

    def ai_toggle_play(self):
        if not self.ai_path:
            self.toast.show("Vui lòng chạy giải AI trước.")
            return
        self.set_ai_playing(not self.is_playing_ai)

    def set_ai_playing(self, is_playing):
        self.is_playing_ai = is_playing
        self.btn_ai_play.text = "|| DỪNG" if is_playing else "> TỰ CHẠY"
        self.btn_ai_play.base_color = (245, 124, 0) if is_playing else (46, 125, 50)

    def trigger_piece_animation(self, action):
        pid, direction = action
        piece = self.current_state.pieces[pid]
        
        # Store history for undo
        self.history.append(self.current_state.clone())
        
        # Calculate target anchor
        from core.constants import DIRECTIONS
        dr, dc = DIRECTIONS[direction]
        target_anchor = (piece.anchor[0] + dr, piece.anchor[1] + dc)
        
        # Start animation
        self.active_animation = {
            pid: (0.0, piece.anchor, target_anchor)
        }
        self.anim_timer = self.anim_duration
        self.animating_action = action

    def handle_event(self, event):
        # 1. Handle Modal events first if active
        if self.win_modal.active:
            self.win_modal.handle_event(event)
            return

        # 2. General controls
        self.btn_menu.handle_event(event)
        self.btn_levels.handle_event(event)
        self.btn_reset.handle_event(event)
        
        if self.mode == "play":
            self.btn_undo.handle_event(event)
            
        # 3. AI Mode Controls
        if self.mode == "ai":
            if self.algo_dropdown.handle_event(event):
                return
            self.btn_solve.handle_event(event)
            self.btn_ai_prev.handle_event(event)
            self.btn_ai_next.handle_event(event)
            self.btn_ai_play.handle_event(event)

        # 4. Handle grid clicks for piece selection (Only when not animating)
        if not self.active_animation and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check click on board cells - use responsive layout (khớp với draw())
            W = self.app.width
            H = self.app.height
            board_top = self._top + 72
            board_w   = int(W * 0.52)
            board_h   = H - board_top - 74
            bx        = 30
            board_rect = pygame.Rect(bx, board_top, board_w, board_h)

            # Map mouse coord to board cell using dynamic cell size
            cell_sz  = get_cell_size(board_rect)
            mpos     = event.pos
            offset_x = board_rect.x + (board_rect.width  - 4 * cell_sz) // 2
            offset_y = board_rect.y + (board_rect.height - 4 * cell_sz) // 2

            grid_c = int((mpos[0] - offset_x) // cell_sz)
            grid_r = int((mpos[1] - offset_y) // cell_sz)

            
            if 0 <= grid_r < 4 and 0 <= grid_c < 4:
                # Find if any piece occupies this cell
                hit_pid = None
                for pid, p in self.current_state.pieces.items():
                    if (grid_r, grid_c) in p.occupied_cells():
                        hit_pid = pid
                        break
                        
                if hit_pid:
                    p = self.current_state.pieces[hit_pid]
                    if p.movable:
                        self.selected_piece_id = hit_pid
                    else:
                        self.selected_piece_id = None
                        self.toast.show(f"Mảnh {hit_pid} là chướng ngại vật cố định!")
                else:
                    self.selected_piece_id = None

        # 5. Handle Keyboard inputs for sliding selected piece
        if not self.active_animation and self.selected_piece_id and event.type == pygame.KEYDOWN:
            key_dir = None
            if event.key in (pygame.K_UP, pygame.K_w):
                key_dir = "UP"
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                key_dir = "DOWN"
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                key_dir = "LEFT"
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                key_dir = "RIGHT"
                
            if key_dir:
                if self.rules.can_move(self.current_state, self.selected_piece_id, key_dir):
                    self.trigger_piece_animation((self.selected_piece_id, key_dir))
                else:
                    self.toast.show("Nước đi bị cản, không hợp lệ!")

    def update(self, dt):
        # Update toast overlays
        self.toast.update(dt)
        
        # 1. Update active piece sliding animation
        if self.active_animation:
            pid = list(self.active_animation.keys())[0]
            progress, start, end = self.active_animation[pid]
            
            # Progress rate
            new_prog = progress + (dt / self.anim_duration)
            if new_prog >= 1.0:
                # Animation finished, apply action physically in core logic
                self.current_state = self.rules.apply_action(self.current_state, self.animating_action)
                self.active_animation = {}
                self.animating_action = None
                
                # Check Win
                if self.current_state.is_goal() and not self.win_modal.active:
                    self.win_modal.active = True
                    self.set_ai_playing(False)
            else:
                self.active_animation[pid] = (new_prog, start, end)
                
        # 2. Update AI Solver auto playback
        elif self.is_playing_ai and self.ai_path:
            self.ai_play_timer += dt
            if self.ai_play_timer >= self.ai_play_speed:
                self.ai_play_timer = 0.0
                if self.ai_step_idx < len(self.ai_path):
                    act = self.ai_path[self.ai_step_idx]
                    self.trigger_piece_animation(act)
                    self.ai_step_idx += 1
                else:
                    self.set_ai_playing(False)
                    self.toast.show("Đã hoàn tất lời giải AI.")

    def draw(self, surface):
        surface.fill(BG_COLOR)

        top    = self._top
        hdr_y  = self._hdr_y
        sub_y  = self._sub_y
        ctrl_y = self._ai_ctrl_y

        # 1. Header
        title_font = self.app.fonts["title"]
        body_font  = self.app.fonts["body"]
        body_bold  = self.app.fonts["body_bold"]

        title_surf = title_font.render(f"MÀN CHƠI: {self.level_meta['name']}", True, TEXT_COLOR)
        surface.blit(title_surf, (30, hdr_y))

        diff_surf = body_font.render(
            f"Cấp độ: {self.difficulty.capitalize()}  |  "
            f"Chế độ: {'Tự chơi' if self.mode == 'play' else 'AI Solver'}",
            True, TEXT_MUTED,
        )
        surface.blit(diff_surf, (30, sub_y))

        # 2. Board (Left Side) - bắt đầu từ dưới header, lấp đầy chiều cao
        W = self.app.width
        H = self.app.height
        board_top  = top + 72
        board_h    = H - board_top - 74  # 74px = khoảng cách trên nút bottom
        bx         = 30
        board_w    = int(W * 0.52)
        board_rect = pygame.Rect(bx, board_top, board_w, board_h)

        legal_acts = []
        if self.selected_piece_id:
            legal_acts = self.rules.legal_actions(self.current_state)

        draw_board(
            surface=surface,
            state=self.current_state,
            board_rect=board_rect,
            selected_piece_id=self.selected_piece_id,
            legal_moves=legal_acts,
            animations=self.active_animation,
        )

        # 3. Side Panel (Right Side)
        rp_x = bx + board_w + 20
        rp_w = W - rp_x - 20
        panel_rect = pygame.Rect(rp_x - 10, top + 4, rp_w + 10, H - top - 74)
        pygame.draw.rect(surface, PANEL_COLOR, panel_rect, border_radius=15)
        pygame.draw.rect(surface, BORDER_COLOR, panel_rect, width=2, border_radius=15)

        panel_title_y = top + 18

        if self.mode == "play":
            lbl_title = title_font.render("BẢNG ĐIỀU KHIỂN", True, TEXT_COLOR)
            surface.blit(lbl_title, (rp_x, panel_title_y))

            instructions = [
                "Luật chơi đơn giản:",
                "1. Click chọn sóc nâu / đen / trắng / cam.",
                "2. Dùng phím mũi tên hoặc WASD để dịch sóc 1 ô.",
                "3. Nếu hạt nằm trên lỗ sau nước đi, hạt sẽ rơi.",
                "4. Thắng khi tất cả sóc trong level đã thả hạt.",
                "5. Các lỗ đã lấp không chặn đường đi.",
                "6. Mảnh hoa đỏ là vật cản cố định.",
            ]
            instr_y = panel_title_y + 44
            for idx, line in enumerate(instructions):
                color = (46, 125, 50) if idx == 0 else TEXT_COLOR
                surface.blit(body_font.render(line, True, color), (rp_x, instr_y + idx * 34))



        elif self.mode == "ai":
            lbl_title = title_font.render("AI SOLVER PANEL", True, TEXT_COLOR)
            surface.blit(lbl_title, (rp_x, panel_title_y))

            lbl_algo = body_font.render("Chọn Thuật toán:", True, TEXT_MUTED)
            surface.blit(lbl_algo, (rp_x, ctrl_y - 22))

            stats_y = ctrl_y + 55
            pygame.draw.line(surface, BORDER_COLOR, (rp_x - 5, stats_y), (W - 25, stats_y), width=1)

            if self.ai_result:
                stats_lines = [
                    f"Trạng thái giải: {'Thành công' if self.ai_result.solved else 'Thất bại'}",
                    f"Số bước giải: {len(self.ai_path)}  (Bước hiện tại: {self.ai_step_idx})",
                    f"Nút đã duyệt  (Visited):   {self.ai_result.visited_count:,}",
                    f"Nút đã sinh   (Generated): {self.ai_result.generated_count:,}",
                    f"Thời gian chạy:  {self.ai_result.elapsed_time * 1000:.2f} ms",
                ]
                reason = self.ai_result.extra.get("reason")
                if self.ai_result.extra.get("invalid_solution_path"):
                    reason = "invalid_solution_path"
                if reason:
                    stats_lines.append(f"Lý do dừng: {reason}")
                if (
                    self.ai_result.algorithm in ADVERSARIAL_ALGORITHMS
                    and self.ai_path
                    and not self.ai_result.solved
                ):
                    stats_lines[0] = "Trạng thái: Mô phỏng đối kháng chưa thắng goal"
                for idx, line in enumerate(stats_lines):
                    surface.blit(body_font.render(line, True, TEXT_COLOR), (rp_x, stats_y + 14 + idx * 30))
            else:
                surface.blit(body_font.render("Chưa có kết quả tìm kiếm thuật toán.", True, TEXT_MUTED), (rp_x, stats_y + 18))



            path_y = stats_y + 208
            pygame.draw.line(surface, BORDER_COLOR, (rp_x - 5, path_y), (W - 25, path_y), width=1)
            lbl_path = body_bold.render("Các bước di chuyển:", True, TEXT_COLOR)
            surface.blit(lbl_path, (rp_x, path_y + 10))

            if self.ai_path:
                box_rect = pygame.Rect(rp_x, path_y + 35, rp_w, 100)
                pygame.draw.rect(surface, BG_COLOR, box_rect, border_radius=6)
                pygame.draw.rect(surface, BORDER_COLOR, box_rect, width=1, border_radius=6)
                start_i = max(0, self.ai_step_idx - 1)
                end_i   = min(len(self.ai_path), start_i + 3)
                for idx in range(start_i, end_i):
                    act       = self.ai_path[idx]
                    highlight = (idx == self.ai_step_idx)
                    marker    = "> " if highlight else "  "
                    text      = f"{marker}Bước {idx+1}: {act[0].upper()} dịch {act[1]}"
                    color     = (46, 125, 50) if highlight else TEXT_COLOR
                    step_surf = (body_bold if highlight else body_font).render(text, True, color)
                    surface.blit(step_surf, (rp_x + 10, path_y + 45 + (idx - start_i) * 27))
            else:
                surface.blit(
                    body_font.render("Chọn thuật toán và bấm GIẢI AI.", True, TEXT_MUTED),
                    (rp_x + 10, path_y + 45),
                )

            self.btn_ai_prev.draw(surface)
            self.btn_ai_next.draw(surface)
            self.btn_ai_play.draw(surface)
            self.btn_solve.draw(surface)
            self.algo_dropdown.draw(surface)

        # 4. Bottom buttons
        self.btn_menu.draw(surface)
        self.btn_levels.draw(surface)
        self.btn_reset.draw(surface)
        if self.mode == "play":
            self.btn_undo.draw(surface)

        # Toast & Modal
        self.toast.draw(surface)
        self.win_modal.draw(surface)
