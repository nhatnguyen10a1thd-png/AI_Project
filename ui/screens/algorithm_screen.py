import pygame

from ai.solver_interface import ALGORITHMS, solve
from core.constants import BG_COLOR, BORDER_COLOR, PANEL_COLOR, TEXT_COLOR, TEXT_MUTED
from core.rules import BoardRules
from ui.components.button import Button
from ui.components.dropdown import Dropdown
from ui.components.scrollbar import Scrollbar
from ui.components.titlebar import TITLEBAR_H
from ui.renderers.board_renderer import draw_board
from ui.screen_manager import ScreenBase

# Màu hint khi chưa chạy
_HINT_COLOR = (140, 135, 125)


def _safe_log_text(text):
    """Replace symbols that some pygame fonts render as square boxes."""
    replacements = {
        "\u2192": "->",
        "\u2190": "<-",
        "\u21d2": "=>",
        "\u279c": "->",
        "\u2794": "->",
        "\u2013": "-",
        "\u2014": "-",
        "\u2705": "[OK]",
        "\u274c": "[X]",
        "\U0001f3b2": "[Random]",
        "\u2026": "...",
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return text


class AlgorithmScreen(ScreenBase):
    """Trình diễn thuật toán với nhật ký duyệt đầy đủ và có thể tương tác."""

    def __init__(self, app):
        super().__init__(app)
        self.difficulty    = "starter"
        self.level_id      = "starter_01"
        self.level_meta    = None
        self.initial_state = None
        self.current_state = None
        self.rules         = BoardRules()

        self.result        = None       # None = chưa chạy
        self.solver_steps  = []
        self.step_idx      = 0
        self.current_algo  = "A*" if "A*" in ALGORITHMS else next(iter(ALGORITHMS))
        self.is_playing    = False
        self.play_timer    = 0.0
        self.play_speed    = 0.55

        self.log_scroll_offset = 0
        self.log_x_offset      = 0
        self.log_content_width = 0
        self.log_row_h         = 25
        self.log_visible_rows  = 1
        self.log_area_rect     = pygame.Rect(0, 0, 0, 0)
        self.log_view_rect     = pygame.Rect(0, 0, 0, 0)
        self.log_scrollbar     = Scrollbar((0, 0, 12, 100), self._set_log_offset)
        self.log_h_scrollbar   = Scrollbar((0, 0, 100, 12), self._set_log_x_offset, orientation="horizontal")
        self.setup_ui()

    # ------------------------------------------------------------------
    def setup_ui(self):
        font_btn  = self.app.fonts["button"]
        font_body = self.app.fonts["body_bold"]
        top       = TITLEBAR_H
        bottom_y  = self.app.height - 62
        right_x   = int(self.app.width * 0.54)
        ctrl_y    = top + 36

        self.btn_menu = Button(
            (25, bottom_y, 135, 42), "< MENU", font_body,
            lambda: self.app.switch_to_screen("main_menu"), color=(120, 115, 105)
        )
        self.btn_levels = Button(
            (175, bottom_y, 145, 42), "CHỌN LEVEL", font_body,
            lambda: self.app.switch_to_screen("level_select", mode="visualizer"),
            color=(79, 110, 138)
        )
        self.btn_reset = Button(
            (335, bottom_y, 125, 42), "ĐẶT LẠI", font_body,
            self.reset_visualizer, color=(211, 47, 47)
        )

        self.algo_dropdown = Dropdown(
            (right_x, ctrl_y, 255, 38), list(ALGORITHMS.keys()),
            self.app.fonts["body_bold"], default_index=list(ALGORITHMS.keys()).index(self.current_algo)
        )
        self.btn_start = Button(
            (right_x + 270, ctrl_y, 110, 38), "BẮT ĐẦU", font_btn,
            self.start_visualization, color=(46, 125, 50)
        )
        self.btn_prev = Button(
            (right_x, bottom_y, 105, 42), "< TRƯỚC", font_body,
            self.prev_step, color=(120, 115, 105)
        )
        self.btn_next = Button(
            (right_x + 120, bottom_y, 105, 42), "TIẾP >", font_body,
            self.next_step, color=(79, 110, 138)
        )
        self.btn_play = Button(
            (right_x + 240, bottom_y, 125, 42), "> TỰ CHẠY", font_body,
            self.toggle_play, color=(46, 125, 50)
        )
        self._top     = top
        self._ctrl_y  = ctrl_y
        self._right_x = right_x

    def update_layout(self):
        bottom_y  = self.app.height - 62
        right_x   = int(self.app.width * 0.54)
        
        self.btn_menu.rect.y = bottom_y
        self.btn_levels.rect.y = bottom_y
        self.btn_reset.rect.y = bottom_y
        
        self.algo_dropdown.rect.x = right_x
        self.btn_start.rect.x = right_x + 270
        
        self.btn_prev.rect.x = right_x
        self.btn_prev.rect.y = bottom_y
        self.btn_next.rect.x = right_x + 120
        self.btn_next.rect.y = bottom_y
        self.btn_play.rect.x = right_x + 240
        self.btn_play.rect.y = bottom_y
        
        self._right_x = right_x

    # ------------------------------------------------------------------
    def on_enter(self, **kwargs):
        self.difficulty = kwargs.get("difficulty", "starter")
        self.level_id   = kwargs.get("level_id",   "starter_01")
        self.level_meta, self.initial_state = self.app.level_manager.load_level(
            self.difficulty, self.level_id
        )
        # Hiển thị trạng thái ban đầu nhưng KHÔNG tự chạy thuật toán
        self.current_state     = self.initial_state.clone()
        self.result            = None
        self.solver_steps      = []
        self.step_idx          = 0
        self.log_scroll_offset = 0
        self.log_x_offset      = 0
        self.log_content_width = 0
        self.is_playing        = False
        self.play_timer        = 0.0
        self.setup_ui()

    # ------------------------------------------------------------------
    def reset_visualizer(self):
        if self.initial_state is None:
            return
        self.current_state     = self.initial_state.clone()
        self.result            = None
        self.solver_steps      = []
        self.step_idx          = 0
        self.log_scroll_offset = 0
        self.log_x_offset      = 0
        self.log_content_width = 0
        self.play_timer        = 0.0
        self.set_playing(False)

    def start_visualization(self):
        if self.initial_state is None:
            return
        self.current_algo  = self.algo_dropdown.get_selected()
        self.result        = solve(self.current_algo, self.initial_state, self.rules)
        self.solver_steps  = self.result.steps or [(0, "Trạng thái ban đầu", self.initial_state)]
        self.step_idx      = 0
        self.play_timer    = 0.0
        self.set_playing(False)
        self.log_scroll_offset = 0
        self.log_x_offset      = 0
        self._refresh_log_content_width()
        self.current_state = self.solver_steps[0][2]

    def next_step(self):
        if not self.solver_steps or self.step_idx >= len(self.solver_steps) - 1:
            self.set_playing(False)
            return
        self.step_idx += 1
        self.current_state = self.solver_steps[self.step_idx][2]
        self._auto_scroll_log()

    def prev_step(self):
        if not self.solver_steps or self.step_idx <= 0:
            return
        self.step_idx -= 1
        self.current_state = self.solver_steps[self.step_idx][2]
        self._auto_scroll_log()

    def toggle_play(self):
        if self.solver_steps and len(self.solver_steps) > 1:
            self.set_playing(not self.is_playing)

    def set_playing(self, is_playing):
        self.is_playing = is_playing
        self.btn_play.text       = "|| DỪNG"  if is_playing else "> TỰ CHẠY"
        self.btn_play.base_color = (245, 124, 0) if is_playing else (46, 125, 50)

    # ------------------------------------------------------------------
    def _set_log_offset(self, offset):
        self.log_scroll_offset = offset

    def _set_log_x_offset(self, offset):
        self.log_x_offset = offset

    def _refresh_log_content_width(self):
        mono = self.app.fonts["mono"]
        self.log_content_width = 0
        for step_num, description, _ in self.solver_steps:
            text = f"  [{step_num:04d}] {_safe_log_text(description)}"
            self.log_content_width = max(self.log_content_width, mono.size(text)[0])

    def _sync_scrollbar(self):
        pad = 4
        bar_size = 10
        gap = 4
        self.log_view_rect = pygame.Rect(
            self.log_area_rect.x + pad,
            self.log_area_rect.y + pad,
            max(1, self.log_area_rect.width - pad * 2 - bar_size - gap),
            max(1, self.log_area_rect.height - pad * 2 - bar_size - gap),
        )
        self.log_visible_rows = max(1, self.log_view_rect.height // self.log_row_h)
        self.log_scrollbar.rect = pygame.Rect(
            self.log_area_rect.right - pad - bar_size, self.log_view_rect.y,
            bar_size, self.log_view_rect.height
        )
        self.log_scrollbar.configure(
            len(self.solver_steps), self.log_visible_rows, self.log_scroll_offset
        )
        self.log_scroll_offset = self.log_scrollbar.offset
        self.log_h_scrollbar.rect = pygame.Rect(
            self.log_view_rect.x, self.log_area_rect.bottom - pad - bar_size,
            self.log_view_rect.width, bar_size
        )
        self.log_h_scrollbar.configure(
            max(self.log_view_rect.width, self.log_content_width + 8),
            self.log_view_rect.width,
            self.log_x_offset,
        )
        self.log_x_offset = self.log_h_scrollbar.offset

    def _auto_scroll_log(self):
        max_offset = max(0, len(self.solver_steps) - self.log_visible_rows)
        if self.step_idx < self.log_scroll_offset:
            self.log_scroll_offset = self.step_idx
        elif self.step_idx >= self.log_scroll_offset + self.log_visible_rows:
            self.log_scroll_offset = self.step_idx - self.log_visible_rows + 1
        self.log_scroll_offset = min(max_offset, self.log_scroll_offset)

    # ------------------------------------------------------------------
    def handle_event(self, event):
        for button in (
            self.btn_menu, self.btn_levels, self.btn_reset,
            self.btn_start, self.btn_prev, self.btn_next, self.btn_play
        ):
            button.handle_event(event)

        if self.algo_dropdown.handle_event(event):
            return

        self._sync_scrollbar()
        if self.log_h_scrollbar.handle_event(event):
            return

        if self.log_scrollbar.handle_event(event):
            return

        if event.type == pygame.MOUSEWHEEL and self.log_view_rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.log_h_scrollbar.scroll(-event.y * 40)
            else:
                self.log_scrollbar.scroll(-event.y * 3)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.log_view_rect.collidepoint(event.pos) and self.solver_steps:
                row   = (event.pos[1] - self.log_view_rect.y) // self.log_row_h
                index = self.log_scroll_offset + row
                if 0 <= index < len(self.solver_steps):
                    self.step_idx      = index
                    self.current_state = self.solver_steps[index][2]
                    self.set_playing(False)

    def update(self, dt):
        if self.is_playing:
            self.play_timer += dt
            if self.play_timer >= self.play_speed:
                self.play_timer = 0.0
                self.next_step()

    # ------------------------------------------------------------------
    def draw(self, surface):
        width, height = self.app.width, self.app.height
        top     = self._top
        ctrl_y  = self._ctrl_y
        right_x = self._right_x
        surface.fill(BG_COLOR)

        title_font = self.app.fonts["title"]
        body       = self.app.fonts["body"]
        body_bold  = self.app.fonts["body_bold"]
        body_small = self.app.fonts["body_small"]
        mono       = self.app.fonts["mono"]

        # Tieu de trai
        surface.blit(title_font.render("TRÌNH DIỄN THUẬT TOÁN", True, TEXT_COLOR), (25, top + 8))
        level_name = self.level_meta["name"] if self.level_meta else "-"
        algo_name  = self.current_algo if self.result else "Chưa chạy"
        subtitle   = f"Màn: {level_name}  |  Thuật toán: {algo_name}"
        surface.blit(body.render(subtitle, True, TEXT_MUTED), (25, top + 38))

        # Bang game ben trai
        board_rect = pygame.Rect(25, top + 82, int(width * 0.50), height - top - 160)
        if self.current_state:
            draw_board(surface, self.current_state, board_rect)
        else:
            # Placeholder khi chưa load level
            pygame.draw.rect(surface, PANEL_COLOR, board_rect, border_radius=14)
            pygame.draw.rect(surface, BORDER_COLOR, board_rect, width=2, border_radius=14)

        # Panel ben phai
        right_w  = width - right_x - 20
        # Panel chiếm hết từ dưới TitleBar đến trên nút bottom
        panel_h  = height - top - 82
        panel    = pygame.Rect(right_x - 10, top + 4, right_w + 10, panel_h)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=14)
        pygame.draw.rect(surface, BORDER_COLOR, panel, width=2, border_radius=14)

        # Nhãn dropdown
        surface.blit(body.render("Chọn thuật toán:", True, TEXT_MUTED), (right_x, ctrl_y - 20))

        # Ket qua / trang thai
        status_y = ctrl_y + 52
        if self.result is None:
            # Chua chay
            hint_lines = [
                "Chọn thuật toán ở dropdown",
                "rồi bấm  BẮT ĐẦU  để xem kết quả.",
            ]
            for i, ln in enumerate(hint_lines):
                surface.blit(body.render(ln, True, _HINT_COLOR), (right_x, status_y + i * 26))
        else:
            solved       = self.result.solved
            status_str   = "ĐÃ TÌM THẤY LỜI GIẢI" if solved else "KHÔNG TÌM THẤY LỜI GIẢI"
            status_color = (46, 125, 50) if solved else (190, 55, 55)
            surface.blit(body_bold.render(status_str, True, status_color), (right_x, status_y))
            summary = (
                f"Log: {len(self.solver_steps):,} | Hiện tại: {self.step_idx + 1:,} | "
                f"Visited: {self.result.visited_count:,} | {self.result.elapsed_time * 1000:.1f} ms"
            )
            surface.blit(body.render(summary, True, TEXT_MUTED), (right_x, status_y + 27))

        # Nhat ky duyet
        log_title_y = status_y + 65
        surface.blit(
            body_bold.render("NHẬT KÝ DUYỆT - click dòng để xem trạng thái", True, TEXT_COLOR),
            (right_x, log_title_y)
        )

        # log_area kết thúc 112px trước bottom (chỗ nút + chú thích)
        log_area_h = height - log_title_y - 130
        self.log_area_rect = pygame.Rect(right_x, log_title_y + 28, right_w, max(60, log_area_h))
        pygame.draw.rect(surface, (248, 248, 246), self.log_area_rect, border_radius=8)
        pygame.draw.rect(surface, BORDER_COLOR,    self.log_area_rect, width=1, border_radius=8)
        self._sync_scrollbar()

        if not self.solver_steps:
            # Placeholder text khi chưa chạy
            ph = body.render("Chưa có nhật ký - bấm BẮT ĐẦU để chạy thuật toán.", True, _HINT_COLOR)
            surface.blit(ph, ph.get_rect(centerx=self.log_view_rect.centerx,
                                          y=self.log_view_rect.y + 8))
        else:
            clip       = surface.subsurface(self.log_view_rect)
            view_width = self.log_view_rect.width
            for row in range(self.log_visible_rows):
                index = self.log_scroll_offset + row
                if index >= len(self.solver_steps):
                    break
                step_num, description, _ = self.solver_steps[index]
                y      = 4 + row * self.log_row_h
                active = (index == self.step_idx)
                if active:
                    pygame.draw.rect(clip, (220, 239, 224),
                                     (0, y, view_width, self.log_row_h - 1), border_radius=4)
                prefix = ">" if active else " "
                text   = f"{prefix} [{step_num:04d}] {_safe_log_text(description)}"
                color = (30, 115, 55) if active else TEXT_COLOR
                clip.blit(mono.render(text, True, color), (4 - self.log_x_offset, y + 3))

        self.log_scrollbar.draw(surface)
        self.log_h_scrollbar.draw(surface)



        # Dropdown + buttons
        self.algo_dropdown.draw(surface)
        for button in (
            self.btn_start, self.btn_menu, self.btn_levels, self.btn_reset,
            self.btn_prev, self.btn_next, self.btn_play
        ):
            button.draw(surface)
