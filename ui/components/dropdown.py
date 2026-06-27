# ui/components/dropdown.py
import pygame
from core.constants import BORDER_COLOR, PANEL_COLOR, TEXT_COLOR

class Dropdown:
    """A custom Pygame Dropdown menu selector component."""
    def __init__(self, rect, options, font, default_index=0, callback=None):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.font = font
        self.selected_index = default_index
        self.callback = callback
        
        self.is_open = False
        self.hovered_index = -1
        self.is_hovered_main = False
        
        # Style variables
        self.bg_color = PANEL_COLOR
        self.text_color = TEXT_COLOR
        self.border_color = BORDER_COLOR
        self.highlight_color = (235, 240, 245) # Soft selection light blue

    def get_selected(self):
        return self.options[self.selected_index]

    def set_selected(self, option_name):
        if option_name in self.options:
            self.selected_index = self.options.index(option_name)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Check hover over main box
            self.is_hovered_main = self.rect.collidepoint(event.pos)
            
            # Check hover over options
            if self.is_open:
                self.hovered_index = -1
                for i in range(len(self.options)):
                    opt_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                    if opt_rect.collidepoint(event.pos):
                        self.hovered_index = i
                        break
                        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.is_open = not self.is_open
                    return True
                elif self.is_open:
                    # Check if click is inside an option
                    for i in range(len(self.options)):
                        opt_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                        if opt_rect.collidepoint(event.pos):
                            self.selected_index = i
                            self.is_open = False
                            if self.callback:
                                self.callback(self.options[i])
                            return True
                    # Clicked outside when open — close and BLOCK event propagation
                    self.is_open = False
                    return True  # Consume the event to prevent other buttons from firing
        return False

    def draw(self, surface):
        # Draw main box
        pygame.draw.rect(surface, (205, 202, 196), self.rect.move(0, 2), border_radius=7)
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=6)
        border = (79, 110, 138) if self.is_open or self.is_hovered_main else self.border_color
        pygame.draw.rect(surface, border, self.rect, width=2 if self.is_open else 1, border_radius=6)
        
        # Render selected text
        text_surf = self.font.render(self.options[self.selected_index], True, self.text_color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Render arrow indicator (▼ or ▲)
        arrow_char = "▲" if self.is_open else "▼"
        arrow_surf = self.font.render(arrow_char, True, self.text_color)
        arrow_rect = arrow_surf.get_rect(midright=(self.rect.right - 10, self.rect.centery))
        surface.blit(arrow_surf, arrow_rect)
        
        # Draw options if open
        if self.is_open:
            # We want to draw options over other elements, so we draw it
            height = self.rect.height
            for i, opt in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * height, self.rect.width, height)
                
                # Check option bg
                bg = self.highlight_color if self.hovered_index == i else self.bg_color
                
                pygame.draw.rect(surface, bg, opt_rect)
                pygame.draw.rect(surface, self.border_color, opt_rect, width=1)
                
                opt_surf = self.font.render(opt, True, self.text_color)
                opt_surf_rect = opt_surf.get_rect(midleft=(opt_rect.x + 10, opt_rect.centery))
                surface.blit(opt_surf, opt_surf_rect)
