# ui/components/toast.py
"""
Toast thông báo nổi — luôn hiển thị chính giữa màn hình theo kích thước surface thực tế.
"""
import pygame


class Toast:
    """Hiển thị thông báo tạm thời ở chính giữa màn hình, tự động mờ dần."""

    def __init__(self, font):
        self.font       = font
        self.message    = ""
        self.duration   = 2.5
        self.timer      = 0.0
        self.active     = False
        self.bg_color   = (30, 30, 28)
        self.text_color = (255, 255, 255)

    # ------------------------------------------------------------------
    def show(self, message, duration=2.5):
        self.message  = message
        self.duration = duration
        self.timer    = duration
        self.active   = True

    def update(self, dt):
        if not self.active:
            return
        self.timer -= dt
        if self.timer <= 0:
            self.active = False

    # ------------------------------------------------------------------
    def draw(self, surface):
        if not self.active:
            return

        SW, SH = surface.get_size()   # kích thước màn hình thực tế

        # Alpha fade-out trong 0.5s cuối
        alpha = 255
        if self.timer < 0.5:
            alpha = max(0, int(self.timer / 0.5 * 255))

        # Render text
        text_surf = self.font.render(self.message, True, self.text_color)
        tw, th    = text_surf.get_size()

        px, py    = 24, 14
        bw        = tw + px * 2
        bh        = th + py * 2

        # Vị trí: chính giữa màn hình theo chiều ngang, 60% chiều cao
        bx = (SW - bw) // 2
        by = int(SH * 0.60)

        # Bề mặt với alpha
        toast = pygame.Surface((bw, bh), pygame.SRCALPHA)

        # Nền tối bo góc
        bg_a = int(220 * alpha / 255)
        pygame.draw.rect(toast, (*self.bg_color, bg_a), (0, 0, bw, bh), border_radius=10)
        # Viền nhẹ
        border_a = int(80 * alpha / 255)
        pygame.draw.rect(toast, (255, 255, 255, border_a), (0, 0, bw, bh),
                         width=1, border_radius=10)

        # Chữ
        text_a = self.font.render(self.message, True,
                                  (*self.text_color, alpha))
        toast.blit(text_a, text_a.get_rect(center=(bw // 2, bh // 2)))

        surface.blit(toast, (bx, by))
