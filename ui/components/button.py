# ui/components/button.py
import pygame
from core.constants import BTN_NORMAL, BTN_HOVER, BTN_PRESSED, BTN_DISABLED, BTN_TEXT_COLOR

class Button:
    """A highly reusable, styled Pygame Button with hover/click visual feedback."""
    def __init__(self, rect, text, font, callback=None, color=BTN_NORMAL, hover_color=BTN_HOVER, pressed_color=BTN_PRESSED, text_color=BTN_TEXT_COLOR, border_radius=8):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.base_color = color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.text_color = text_color
        self.border_radius = border_radius
        
        self.is_hovered = False
        self.is_pressed = False
        self.is_enabled = True

    def handle_event(self, event):
        if not self.is_enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_pressed = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                was_pressed = self.is_pressed
                self.is_pressed = False  # Always reset, even if mouse moved away
                if was_pressed and self.rect.collidepoint(event.pos) and self.callback:
                    self.callback()
                    return True
        return False

    def draw(self, surface):
        # Determine current color
        if not self.is_enabled:
            color = BTN_DISABLED
        elif self.is_pressed:
            color = self.pressed_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.base_color

        # Draw soft shadow and crisp border.
        if self.is_enabled and not self.is_pressed:
            shadow_rect = self.rect.move(0, 3)
            pygame.draw.rect(surface, (185, 183, 178), shadow_rect, border_radius=self.border_radius)

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        border = tuple(max(0, channel - 34) for channel in color)
        pygame.draw.rect(surface, border, self.rect, width=1, border_radius=self.border_radius)
        if self.is_enabled and not self.is_pressed:
            shine = pygame.Rect(self.rect.x + 4, self.rect.y + 3, self.rect.width - 8, 2)
            shine_color = tuple(min(255, channel + 55) for channel in color)
            pygame.draw.rect(surface, shine_color, shine, border_radius=2)
        
        # Render text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
