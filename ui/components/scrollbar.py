import pygame


class Scrollbar:
    """Scrollbar with track click and thumb dragging."""

    def __init__(self, rect, on_change, min_thumb_height=28, orientation="vertical"):
        self.rect = pygame.Rect(rect)
        self.on_change = on_change
        self.min_thumb_height = min_thumb_height
        self.orientation = orientation
        self.total_items = 0
        self.visible_items = 0
        self.offset = 0
        self.dragging = False
        self.drag_offset_y = 0
        self.drag_offset_x = 0

    @property
    def max_offset(self):
        return max(0, self.total_items - self.visible_items)

    def configure(self, total_items, visible_items, offset):
        self.total_items = max(0, total_items)
        self.visible_items = max(1, visible_items)
        self.offset = max(0, min(offset, self.max_offset))

    def thumb_rect(self):
        if self.total_items <= self.visible_items:
            return pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)

        ratio = self.visible_items / self.total_items
        if self.orientation == "horizontal":
            thumb_w = max(self.min_thumb_height, int(self.rect.width * ratio))
            travel = self.rect.width - thumb_w
            thumb_x = self.rect.x + int(travel * self.offset / self.max_offset)
            return pygame.Rect(thumb_x, self.rect.y, thumb_w, self.rect.height)

        thumb_h = max(self.min_thumb_height, int(self.rect.height * ratio))
        travel = self.rect.height - thumb_h
        thumb_y = self.rect.y + int(travel * self.offset / self.max_offset)
        return pygame.Rect(self.rect.x, thumb_y, self.rect.width, thumb_h)

    def set_offset(self, offset):
        offset = max(0, min(int(offset), self.max_offset))
        if offset != self.offset:
            self.offset = offset
            self.on_change(offset)

    def scroll(self, delta):
        self.set_offset(self.offset + delta)

    def handle_event(self, event):
        if self.total_items <= self.visible_items:
            self.dragging = False
            return False

        thumb = self.thumb_rect()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if thumb.collidepoint(event.pos):
                self.dragging = True
                if self.orientation == "horizontal":
                    self.drag_offset_x = event.pos[0] - thumb.x
                else:
                    self.drag_offset_y = event.pos[1] - thumb.y
                return True
            if self.rect.collidepoint(event.pos):
                page = max(1, self.visible_items - 1)
                if self.orientation == "horizontal":
                    self.scroll(-page if event.pos[0] < thumb.x else page)
                else:
                    self.scroll(-page if event.pos[1] < thumb.y else page)
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_dragging = self.dragging
            self.dragging = False
            return was_dragging

        if event.type == pygame.MOUSEMOTION and self.dragging:
            if self.orientation == "horizontal":
                thumb_w = thumb.width
                travel = max(1, self.rect.width - thumb_w)
                x = max(self.rect.x, min(event.pos[0] - self.drag_offset_x, self.rect.right - thumb_w))
                ratio = (x - self.rect.x) / travel
            else:
                thumb_h = thumb.height
                travel = max(1, self.rect.height - thumb_h)
                y = max(self.rect.y, min(event.pos[1] - self.drag_offset_y, self.rect.bottom - thumb_h))
                ratio = (y - self.rect.y) / travel
            self.set_offset(round(ratio * self.max_offset))
            return True

        return False

    def draw(self, surface):
        pygame.draw.rect(surface, (232, 230, 225), self.rect, border_radius=6)
        if self.total_items > self.visible_items:
            color = (105, 125, 145) if self.dragging else (145, 155, 165)
            pygame.draw.rect(surface, color, self.thumb_rect(), border_radius=6)
