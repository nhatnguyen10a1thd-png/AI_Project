# ui/screens/main_menu.py
import sys
import pygame
from ui.screen_manager import ScreenBase
from ui.components.button import Button
from ui.components.titlebar import TITLEBAR_H
from core.constants import BG_COLOR, TEXT_COLOR, PANEL_COLOR

class MainMenuScreen(ScreenBase):
    """Giao diện Menu chính — nội dung bắt đầu từ bên dưới TitleBar."""
    def __init__(self, app):
        super().__init__(app)
        self.buttons = []
        self._build_buttons()

    def _build_buttons(self):
        button_font = self.app.fonts["button"]
        W = self.app.width
        H = self.app.height
        # Phần nội dung bắt đầu từ dưới TitleBar
        content_h = H - TITLEBAR_H

        choices = [
            ("CHƠI GAME (PLAY)", lambda: self.app.switch_to_screen("level_select", mode="play")),
            ("AI SOLVER",        lambda: self.app.switch_to_screen("level_select", mode="ai")),
            ("TRÌNH DIỄN THUẬT TOÁN", lambda: self.app.switch_to_screen("level_select", mode="visualizer")),
            ("BÁO CÁO HIỆU NĂNG",    lambda: self.app.switch_to_screen("level_select", mode="report")),
            ("THOÁT (QUIT)", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))),
        ]

        btn_w = max(320, min(420, int(W * 0.33)))
        btn_h = max(44, min(54, int(content_h * 0.065)))
        gap   = max(14, int(content_h * 0.022))
        # Bắt đầu vẽ từ 38% chiều cao nội dung
        start_y = TITLEBAR_H + int(content_h * 0.38)

        self.buttons = []
        for idx, (label, callback) in enumerate(choices):
            rect = (
                (W - btn_w) // 2,
                start_y + idx * (btn_h + gap),
                btn_w,
                btn_h,
            )
            color = (139, 115, 85) if idx == 0 else (79, 110, 138)
            self.buttons.append(
                Button(rect=rect, text=label, font=button_font,
                       callback=callback, color=color, border_radius=10)
            )

    def on_enter(self, **kwargs):
        self._build_buttons()

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, surface):
        W = self.app.width
        H = self.app.height
        content_top = TITLEBAR_H
        content_h   = H - TITLEBAR_H

        surface.fill(BG_COLOR)

        # Panel nền trắng
        panel_w = max(440, min(560, int(W * 0.43)))
        panel_h = int(content_h * 0.84)
        panel_rect = pygame.Rect(
            (W - panel_w) // 2,
            content_top + int(content_h * 0.07),
            panel_w, panel_h,
        )
        pygame.draw.rect(surface, PANEL_COLOR, panel_rect, border_radius=20)
        pygame.draw.rect(surface, (220, 215, 205), panel_rect, width=2, border_radius=20)

        # Tiêu đề
        title_font = self.app.fonts["title_huge"]
        sub_font   = self.app.fonts["title"]

        t1 = title_font.render("SQUIRRELS", True, (139, 115, 85))
        t1_rect = t1.get_rect(centerx=W // 2, y=content_top + int(content_h * 0.11))
        surface.blit(t1, t1_rect)

        t2 = sub_font.render("GO NUTS! AI SOLVER", True, TEXT_COLOR)
        t2_rect = t2.get_rect(centerx=W // 2, y=content_top + int(content_h * 0.23))
        surface.blit(t2, t2_rect)

        # Đường kẻ phân cách
        sep_y = content_top + int(content_h * 0.32)
        pygame.draw.line(surface, (180, 150, 110),
                         (panel_rect.left + 50, sep_y),
                         (panel_rect.right - 50, sep_y), width=2)

        # Buttons
        for btn in self.buttons:
            btn.draw(surface)

        # Credits
        credit_font = self.app.fonts["body_small"]
        credit = credit_font.render("Đồ án Trí Tuệ Nhân Tạo  -  Môn học AI Search", True, (160, 155, 145))
        surface.blit(credit, credit.get_rect(centerx=W // 2, y=H - 36))
