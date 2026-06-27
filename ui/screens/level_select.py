# ui/screens/level_select.py
import pygame
from ui.screen_manager import ScreenBase
from ui.components.button import Button
from ui.components.titlebar import TITLEBAR_H
from core.constants import BG_COLOR, TEXT_COLOR, PANEL_COLOR, BORDER_COLOR


class LevelSelectScreen(ScreenBase):
    """Màn hình chọn Level — nội dung tránh TitleBar."""
    def __init__(self, app):
        super().__init__(app)
        self.mode = "play"
        self.selected_difficulty = "starter"
        self.back_button = None
        self.tab_buttons = {}
        self.level_buttons = []
        self.setup_ui()

    # ------------------------------------------------------------------ layout constants
    @property
    def _top(self):
        """Y bắt đầu của nội dung (bên dưới TitleBar)."""
        return TITLEBAR_H + 8

    def setup_ui(self):
        font_btn  = self.app.fonts["button"]
        W, H = self.app.width, self.app.height
        top = self._top

        self.tab_buttons = {}

        # Nút quay lại
        self.back_button = Button(
            rect=(30, top + 10, 155, 40),
            text="< QUAY LẠI",
            font=self.app.fonts["body_bold"],
            callback=lambda: self.app.switch_to_screen("main_menu"),
            color=(120, 115, 105),
        )

        # Tab chọn cấp độ
        diffs = [
            (d.upper(), d)
            for d in self.app.level_manager.get_difficulties()
        ]
        tab_w   = min(160, max(110, (W - 140) // max(1, len(diffs))))
        tab_h   = 42
        gap     = 18
        start_x = (W - (tab_w * len(diffs) + gap * (len(diffs) - 1))) // 2
        tab_y   = top + 70

        for idx, (label, diff_key) in enumerate(diffs):
            tx = start_x + idx * (tab_w + gap)
            self.tab_buttons[diff_key] = Button(
                rect=(tx, tab_y, tab_w, tab_h),
                text=label,
                font=font_btn,
                callback=lambda k=diff_key: self.select_difficulty(k),
                color=(79, 110, 138),
            )

    def on_enter(self, **kwargs):
        self.mode = kwargs.get("mode", "play")
        self.setup_ui()
        self.select_difficulty(self.selected_difficulty)

    def select_difficulty(self, diff_key):
        self.selected_difficulty = diff_key
        for key, btn in self.tab_buttons.items():
            if key == diff_key:
                btn.base_color  = (139, 115, 85)
                btn.hover_color = (139, 115, 85)
            else:
                btn.base_color  = (79, 110, 138)
                btn.hover_color = (98, 132, 161)

        self.level_buttons = []
        levels = self.app.level_manager.get_levels_by_difficulty(diff_key)
        W, H  = self.app.width, self.app.height
        top   = self._top

        card_w    = min(260, (W - 100) // 4)
        card_h    = 180
        margin_x  = 30
        margin_y  = 30
        grid_cols = 4
        total_w   = card_w * grid_cols + margin_x * (grid_cols - 1)
        if total_w > W - 80:
            grid_cols = 3
            total_w   = card_w * grid_cols + margin_x * (grid_cols - 1)
        start_x = (W - total_w) // 2
        start_y = top + 135   # bên dưới header + tabs

        for idx, lvl in enumerate(levels):
            row = idx // grid_cols
            col = idx % grid_cols
            bx  = start_x + col * (card_w + margin_x)
            by  = start_y + row * (card_h + margin_y)

            btn_text = {
                "play":       "VÀO CHƠI",
                "ai":         "GIẢI AI",
                "visualizer": "MÔ PHỎNG",
                "report":     "BÁO CÁO",
            }.get(self.mode, "MỞ")

            self.level_buttons.append({
                "lvl_data":  lvl,
                "card_rect": pygame.Rect(bx, by, card_w, card_h),
                "button": Button(
                    rect=(bx + 20, by + card_h - 58, card_w - 40, 40),
                    text=btn_text,
                    font=self.app.fonts["body_bold"],
                    callback=lambda lid=lvl["id"]: self.select_level(lid),
                    color=(46, 125, 50) if self.mode == "play" else (139, 115, 85),
                ),
            })

    def select_level(self, level_id):
        if self.mode == "play":
            self.app.switch_to_screen("game", difficulty=self.selected_difficulty, level_id=level_id, mode="play")
        elif self.mode == "ai":
            self.app.switch_to_screen("game", difficulty=self.selected_difficulty, level_id=level_id, mode="ai")
        elif self.mode == "visualizer":
            self.app.switch_to_screen("algorithm", difficulty=self.selected_difficulty, level_id=level_id)
        elif self.mode == "report":
            self.app.switch_to_screen("report", difficulty=self.selected_difficulty, level_id=level_id)

    def handle_event(self, event):
        self.back_button.handle_event(event)
        for btn in self.tab_buttons.values():
            btn.handle_event(event)
        for card in self.level_buttons:
            card["button"].handle_event(event)

    def draw(self, surface):
        W, H = self.app.width, self.app.height
        top  = self._top
        surface.fill(BG_COLOR)

        # Header
        header_font = self.app.fonts["title"]
        mode_str = {
            "play":       "TỰ CHƠI GAME",
            "ai":         "AI SOLVER",
            "visualizer": "TRÌNH DIỄN THUẬT TOÁN",
            "report":     "BÁO CÁO HIỆU NĂNG",
        }.get(self.mode, self.mode.upper())
        header_surf = header_font.render(f"CHỌN LEVEL  -  CHẾ ĐỘ: {mode_str}", True, TEXT_COLOR)
        header_rect = header_surf.get_rect(centerx=W // 2, y=top + 18)
        surface.blit(header_surf, header_rect)

        # Back + tabs
        self.back_button.draw(surface)
        for btn in self.tab_buttons.values():
            btn.draw(surface)

        # Level cards
        body_font = self.app.fonts["body"]
        body_bold = self.app.fonts["body_bold"]

        for card in self.level_buttons:
            rect = card["card_rect"]
            lvl  = card["lvl_data"]

            pygame.draw.rect(surface, PANEL_COLOR, rect, border_radius=12)
            pygame.draw.rect(surface, BORDER_COLOR, rect, width=2, border_radius=12)

            title_s = body_bold.render(lvl["name"], True, TEXT_COLOR)
            surface.blit(title_s, title_s.get_rect(centerx=rect.centerx, y=rect.y + 18))

            sq   = sum(1 for p in lvl["pieces"] if p["type"] == "squirrel")
            blk  = sum(1 for p in lvl["pieces"] if p["type"] == "block")
            det  = body_font.render(f"Số Sóc: {sq}  |  Ô cản: {blk}", True, (120, 115, 105))
            surface.blit(det, det.get_rect(centerx=rect.centerx, y=rect.y + 52))

            tm = lvl.get("target_moves")
            if tm:
                ts = body_bold.render(f"Số bước chuẩn: {tm}", True, (139, 115, 85))
                surface.blit(ts, ts.get_rect(centerx=rect.centerx, y=rect.y + 80))

            card["button"].draw(surface)

        if not self.level_buttons:
            empty = body_font.render("Chưa có level nào trong nhóm này.", True, (120, 115, 105))
            surface.blit(empty, empty.get_rect(centerx=W // 2, y=top + 180))
