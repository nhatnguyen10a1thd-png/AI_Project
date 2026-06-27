# ui/screen_manager.py

class ScreenManager:
    """Manages switching and lifecycle events of different screens."""
    def __init__(self):
        self.screens = {}
        self.current_screen = None

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def switch_to(self, name, **kwargs):
        if self.current_screen:
            self.current_screen.on_exit()
        self.current_screen = self.screens.get(name)
        if self.current_screen:
            self.current_screen.on_enter(**kwargs)

    def handle_event(self, event):
        if self.current_screen:
            self.current_screen.handle_event(event)

    def update(self, dt):
        if self.current_screen:
            self.current_screen.update(dt)

    def draw(self, surface):
        if self.current_screen:
            self.current_screen.draw(surface)
            
class ScreenBase:
    """Base class for all screens in the application."""
    def __init__(self, app):
        self.app = app # The main App instance

    def on_enter(self, **kwargs):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass
