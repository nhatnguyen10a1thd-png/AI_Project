# main.py
import os
import sys
import pygame

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.constants import FPS, BG_COLOR
from core.level import LevelManager
from ui.screen_manager import ScreenManager
from ui.screens.main_menu import MainMenuScreen
from ui.screens.level_select import LevelSelectScreen
from ui.screens.game_screen import GameScreen
from ui.screens.algorithm_screen import AlgorithmScreen
from ui.screens.report_screen import ReportScreen
from ui.font import Font
from ui.renderers.board_renderer import make_app_icon


class App:
    """The main Pygame Application manager class."""
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

        # --- Cửa sổ thông thường: phóng to tối đa, có thanh OS ---
        # Lấy kích thước màn hình để tạo cửa sổ vừa khớp (trừ taskbar)
        info = pygame.display.Info()
        W    = info.current_w
        H    = info.current_h

        self.screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        self.width  = self.screen.get_width()
        self.height = self.screen.get_height()

        pygame.display.set_caption("Squirrels Go Nuts! - AI Search Solver")
        pygame.display.set_icon(make_app_icon())

        # Maximize cửa sổ về trạng thái maximize OS (Windows)
        try:
            import ctypes
            hwnd = pygame.display.get_wm_info().get("window", 0)
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE = 3
                # Cập nhật lại kích thước thực sau maximize
                import time; time.sleep(0.05)
                pygame.event.pump()
                self.width  = self.screen.get_width()
                self.height = self.screen.get_height()
        except Exception:
            pass

        self.clock       = pygame.time.Clock()
        self.running     = True
        self.project_dir = os.path.dirname(os.path.abspath(__file__))

        # Load assets and managers
        self.level_manager = LevelManager()

        # Load fonts robustly with system fallbacks
        self.load_fonts()

        # Initialize screen manager
        self.screen_manager = ScreenManager()
        self.setup_screens()

        # Start at main menu
        self.screen_manager.switch_to("main_menu")

    def load_fonts(self):
        """Loads system fonts, scaled relative to window height (baseline 800px)."""
        pygame.font.init()

        title_font_candidates = ["Segoe UI", "Arial"]
        body_font_candidates  = ["Segoe UI", "Arial"]
        mono_font_candidates  = ["Cascadia Mono", "Consolas", "Courier New"]

        scale = self.height / 800

        def fs(base):
            return max(10, round(base * scale))

        self.fonts = {
            "title_huge": Font(pygame.font.SysFont(title_font_candidates, fs(54), bold=True)),
            "title":      Font(pygame.font.SysFont(title_font_candidates, fs(28), bold=True)),
            "button":     Font(pygame.font.SysFont(body_font_candidates,  fs(16), bold=True)),
            "body_bold":  Font(pygame.font.SysFont(body_font_candidates,  fs(16), bold=True)),
            "body":       Font(pygame.font.SysFont(body_font_candidates,  fs(16))),
            "body_small": Font(pygame.font.SysFont(body_font_candidates,  fs(13))),
            "mono":       Font(pygame.font.SysFont(mono_font_candidates,  fs(14))),
        }

    def setup_screens(self):
        """Registers all screens with the ScreenManager."""
        self.screen_manager.add_screen("main_menu",    MainMenuScreen(self))
        self.screen_manager.add_screen("level_select", LevelSelectScreen(self))
        self.screen_manager.add_screen("game",         GameScreen(self))
        self.screen_manager.add_screen("algorithm",    AlgorithmScreen(self))
        self.screen_manager.add_screen("report",       ReportScreen(self))

    def switch_to_screen(self, screen_name, **kwargs):
        self.screen_manager.switch_to(screen_name, **kwargs)

    def run(self):
        """Main application game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Cập nhật kích thước khi người dùng thay đổi cửa sổ
                    self.width  = event.w
                    self.height = event.h
                    if hasattr(self.screen_manager.current_screen, 'update_layout'):
                        self.screen_manager.current_screen.update_layout()
                else:
                    self.screen_manager.handle_event(event)

            self.screen_manager.update(dt)

            self.screen.fill(BG_COLOR)
            self.screen_manager.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = App()
    app.run()
