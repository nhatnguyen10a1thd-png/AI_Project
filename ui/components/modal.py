# ui/components/modal.py
import pygame
from core.constants import TEXT_COLOR, PANEL_COLOR, BORDER_COLOR
from ui.components.button import Button


class Modal:
    """A blocking modal dialog overlay — tự căn giữa theo kích thước màn hình thực tế."""

    def __init__(self, title, message_lines, font_title, font_body, font_btn,
                 buttons_config, screen_w=1280, screen_h=800):
        self.title = title
        self.message_lines = message_lines
        self.font_title = font_title
        self.font_body = font_body
        self.font_btn = font_btn
        self.active = False

        # Kích thước modal cố định; vị trí được tính theo screen_w/h
        self.modal_w = 480
        self.modal_h = 340
        self._screen_w = screen_w
        self._screen_h = screen_h
        self.rect = self._centered_rect()

        self._build_buttons(buttons_config)

    # ------------------------------------------------------------------
    def _centered_rect(self):
        x = (self._screen_w - self.modal_w) // 2
        y = (self._screen_h - self.modal_h) // 2
        return pygame.Rect(x, y, self.modal_w, self.modal_h)

    def reposition(self, screen_w, screen_h):
        """Gọi lại khi kích thước màn hình thay đổi để modal luôn nằm giữa."""
        self._screen_w = screen_w
        self._screen_h = screen_h
        old_y_offset = self.rect.y
        self.rect = self._centered_rect()
        dy = self.rect.y - old_y_offset
        for btn in self.buttons:
            btn.rect.y += dy

    def _build_buttons(self, buttons_config):
        btn_y = self.rect.bottom - 65
        btn_w = 130
        btn_h = 42
        num = len(buttons_config)
        gap = 16
        total_w = num * btn_w + (num - 1) * gap
        start_x = self.rect.x + (self.modal_w - total_w) // 2

        self.buttons = []
        for i, cfg in enumerate(buttons_config):
            bx = start_x + i * (btn_w + gap)
            self.buttons.append(
                Button(
                    rect=(bx, btn_y, btn_w, btn_h),
                    text=cfg["text"],
                    font=self.font_btn,
                    callback=cfg["callback"],
                    color=cfg.get("color", (79, 110, 138)),
                    border_radius=10,
                )
            )

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if not self.active:
            return False
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return True   # Chặn toàn bộ click khi modal đang hiển thị
        return True

    # ------------------------------------------------------------------
    def draw(self, surface):
        if not self.active:
            return

        W, H = surface.get_size()

        # Lớp phủ mờ toàn màn hình
        blocker = pygame.Surface((W, H), pygame.SRCALPHA)
        blocker.fill((0, 0, 0, 130))
        surface.blit(blocker, (0, 0))

        # Bóng đổ
        shadow = self.rect.move(5, 5)
        shadow_surf = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 60))
        surface.blit(shadow_surf, shadow.topleft)

        # Panel chính
        pygame.draw.rect(surface, PANEL_COLOR, self.rect, border_radius=16)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, width=2, border_radius=16)

        # Thanh màu ở đỉnh modal
        accent = pygame.Rect(self.rect.x, self.rect.y, self.modal_w, 6)
        pygame.draw.rect(surface, (46, 125, 50), accent,
                         border_radius=16)  # xanh lá — Win modal

        # Tiêu đề
        title_surf = self.font_title.render(self.title, True, (46, 125, 50))
        title_rect = title_surf.get_rect(centerx=self.rect.centerx,
                                         y=self.rect.y + 28)
        surface.blit(title_surf, title_rect)

        # Đường kẻ phân cách
        sep_y = self.rect.y + 72
        pygame.draw.line(surface, BORDER_COLOR,
                         (self.rect.x + 30, sep_y),
                         (self.rect.right - 30, sep_y), 1)

        # Nội dung
        for i, line in enumerate(self.message_lines):
            s = self.font_body.render(line, True, TEXT_COLOR)
            r = s.get_rect(centerx=self.rect.centerx, y=sep_y + 18 + i * 28)
            surface.blit(s, r)

        # Buttons
        for btn in self.buttons:
            btn.draw(surface)
