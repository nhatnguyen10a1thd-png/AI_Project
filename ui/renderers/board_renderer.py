import math

import pygame

from core.constants import (
    BOARD_BG_COLOR, CELL_BG_COLOR, HIGHLIGHT_COLOR, HOLE_BORDER_COLOR,
    HOLE_COLOR, NUT_BORDER, NUT_COLOR, NUT_SLOT_COLOR, PIECE_COLORS,
    SELECT_BORDER,
)


# Default CELL_SIZE is used for icon/acorn rendering outside of draw_board.
# The actual cell size during board rendering is computed dynamically.
CELL_SIZE = 90
AA_SCALE = 3
ICON_CANVAS_SIZE = 90


def get_cell_size(board_rect):
    """Compute the best square cell size to fit a 4x4 grid inside board_rect."""
    max_cell_w = board_rect.width // 4
    max_cell_h = board_rect.height // 4
    return min(max_cell_w, max_cell_h, 130)  # cap at 130 px for very large monitors


def get_cell_pos(row, col, board_rect):
    cell = get_cell_size(board_rect)
    offset_x = board_rect.x + (board_rect.width - 4 * cell) // 2
    offset_y = board_rect.y + (board_rect.height - 4 * cell) // 2
    return offset_x + col * cell, offset_y + row * cell


def _shade(color, amount):
    return tuple(max(0, min(255, channel + amount)) for channel in color)


def _blit_aa(surface, center, size, painter, angle=0):
    # Painters use a stable 90x90 coordinate system. Render the complete icon
    # first, then scale it down so small icons never get clipped.
    large_size = ICON_CANVAS_SIZE * AA_SCALE
    canvas = pygame.Surface((large_size, large_size), pygame.SRCALPHA)
    painter(canvas, AA_SCALE)
    if angle:
        canvas = pygame.transform.rotate(canvas, angle)
    icon = pygame.transform.smoothscale(canvas, (size, size))
    surface.blit(icon, icon.get_rect(center=center))


def _paint_squirrel(canvas, scale, color):
    def rect(x, y, w, h):
        return pygame.Rect(x * scale, y * scale, w * scale, h * scale)

    outline = _shade(color, -75)
    highlight = _shade(color, 55)
    dark = _shade(color, -35)

    # Soft shadow, large curled tail, body, head, ears and face.
    pygame.draw.ellipse(canvas, (20, 20, 20, 65), rect(17, 43, 56, 24))
    pygame.draw.ellipse(canvas, outline, rect(7, 21, 39, 48))
    pygame.draw.ellipse(canvas, dark, rect(11, 24, 31, 40))
    pygame.draw.ellipse(canvas, highlight, rect(18, 29, 16, 24))
    pygame.draw.ellipse(canvas, outline, rect(36, 29, 34, 34))
    pygame.draw.ellipse(canvas, color, rect(39, 31, 29, 29))
    pygame.draw.circle(canvas, outline, (67 * scale, 38 * scale), 15 * scale)
    pygame.draw.circle(canvas, color, (66 * scale, 38 * scale), 12 * scale)
    pygame.draw.polygon(canvas, outline, [(58 * scale, 26 * scale), (61 * scale, 12 * scale), (68 * scale, 27 * scale)])
    pygame.draw.polygon(canvas, outline, [(68 * scale, 27 * scale), (75 * scale, 15 * scale), (76 * scale, 32 * scale)])
    pygame.draw.circle(canvas, (250, 250, 245), (70 * scale, 36 * scale), 3 * scale)
    pygame.draw.circle(canvas, (25, 25, 25), (71 * scale, 36 * scale), 2 * scale)
    pygame.draw.circle(canvas, (35, 25, 20), (79 * scale, 42 * scale), 2 * scale)
    pygame.draw.arc(canvas, outline, rect(60, 39, 16, 12), 0.2, 2.7, 2 * scale)
    pygame.draw.arc(canvas, outline, rect(44, 38, 18, 17), 3.4, 5.9, 2 * scale)


def draw_squirrel(surface, center, color, direction="RIGHT"):
    # The direction belongs to the piece layout, not to its latest movement.
    angle = {"RIGHT": 0, "UP": 90, "LEFT": 180, "DOWN": -90}.get(direction, 0)
    _blit_aa(surface, center, 82, lambda canvas, scale: _paint_squirrel(canvas, scale, color), angle)


def _paint_flower(canvas, scale):
    center = 45 * scale
    for index in range(8):
        angle = index * math.pi / 4
        x = center + int(math.cos(angle) * 20 * scale)
        y = center + int(math.sin(angle) * 20 * scale)
        pygame.draw.circle(canvas, (145, 25, 35), (x, y), 13 * scale)
        pygame.draw.circle(canvas, (235, 64, 76), (x, y), 10 * scale)
    pygame.draw.circle(canvas, (122, 67, 20), (center, center), 12 * scale)
    pygame.draw.circle(canvas, (255, 205, 45), (center, center), 9 * scale)
    pygame.draw.circle(canvas, (255, 238, 130), (42 * scale, 42 * scale), 3 * scale)


def draw_flower(surface, center):
    _blit_aa(surface, center, 76, _paint_flower)


def _paint_acorn(canvas, scale, dropped):
    center = (45 * scale, 45 * scale)
    outer = (95, 68, 28) if dropped else NUT_BORDER
    body = (184, 132, 36) if dropped else NUT_COLOR
    pygame.draw.circle(canvas, (20, 15, 10, 55), (47 * scale, 49 * scale), 25 * scale)
    pygame.draw.circle(canvas, outer, center, 25 * scale)
    pygame.draw.circle(canvas, body, center, 21 * scale)
    pygame.draw.circle(canvas, _shade(body, 42), (39 * scale, 37 * scale), 7 * scale)
    pygame.draw.circle(canvas, _shade(body, -32), center, 21 * scale, 2 * scale)


def draw_acorn(surface, center, scale=0.8, is_dropped=False):
    size = max(34, int(64 * scale))
    _blit_aa(surface, center, size, lambda canvas, aa: _paint_acorn(canvas, aa, is_dropped))


def _squirrel_layout(piece):
    """Return a stable icon offset and direction based only on the piece layout."""
    shape = sorted(piece.shape)
    if not shape:
        return (0, 0), "RIGHT"
    if piece.nut_offset is None:
        return shape[0], "RIGHT"

    # Deterministic tie-breaking prevents the icon hopping between equal cells
    # while the piece is animated using floating-point coordinates.
    icon_offset = max(
        shape,
        key=lambda cell: (
            abs(cell[0] - piece.nut_offset[0]) + abs(cell[1] - piece.nut_offset[1]),
            -cell[0],
            -cell[1],
        ),
    )
    dr = piece.nut_offset[0] - icon_offset[0]
    dc = piece.nut_offset[1] - icon_offset[1]
    if abs(dc) >= abs(dr):
        direction = "RIGHT" if dc >= 0 else "LEFT"
    else:
        direction = "DOWN" if dr >= 0 else "UP"
    return icon_offset, direction


def draw_board(surface, state, board_rect, selected_piece_id=None, legal_moves=None, animations=None):
    animations = animations or {}
    cell_sz = get_cell_size(board_rect)  # dynamic cell size based on actual board area

    pygame.draw.rect(surface, (66, 48, 34), board_rect.move(0, 7), border_radius=22)
    pygame.draw.rect(surface, BOARD_BG_COLOR, board_rect, border_radius=20)
    pygame.draw.rect(surface, (92, 68, 48), board_rect, width=5, border_radius=20)
    pygame.draw.line(surface, _shade(BOARD_BG_COLOR, 34), (board_rect.x + 24, board_rect.y + 13),
                     (board_rect.right - 24, board_rect.y + 13), 3)

    for r in range(4):
        for c in range(4):
            x, y = get_cell_pos(r, c, board_rect)
            cell = pygame.Rect(x, y, cell_sz, cell_sz).inflate(-7, -7)
            pygame.draw.rect(surface, _shade(CELL_BG_COLOR, -18), cell.move(0, 3), border_radius=10)
            pygame.draw.rect(surface, CELL_BG_COLOR, cell, border_radius=10)
            pygame.draw.line(surface, _shade(CELL_BG_COLOR, 18), (cell.x + 10, cell.y + 8), (cell.right - 10, cell.y + 8), 2)
            pygame.draw.line(surface, _shade(CELL_BG_COLOR, -10), (cell.x + 12, cell.bottom - 9),
                             (cell.right - 12, cell.bottom - 9), 1)
            pygame.draw.rect(surface, _shade(CELL_BG_COLOR, -28), cell, width=2, border_radius=10)

    for row, col in state.holes:
        x, y = get_cell_pos(row, col, board_rect)
        center = (x + cell_sz // 2, y + cell_sz // 2)
        pygame.draw.circle(surface, (70, 53, 38), (center[0], center[1] + 4), cell_sz // 3 + 2)
        pygame.draw.circle(surface, HOLE_BORDER_COLOR, center, cell_sz // 3 + 1)
        pygame.draw.circle(surface, HOLE_COLOR, center, cell_sz // 3 - 3)
        pygame.draw.circle(surface, (80, 70, 58), (center[0] - 8, center[1] - 9), 8)
        if (row, col) in state.filled_holes:
            draw_acorn(surface, center, scale=0.58, is_dropped=True)

    if selected_piece_id and legal_moves:
        piece = state.pieces[selected_piece_id]
        from core.constants import DIRECTIONS
        for piece_id, direction in legal_moves:
            if piece_id != selected_piece_id:
                continue
            dr, dc = DIRECTIONS[direction]
            x, y = get_cell_pos(piece.anchor[0] + dr, piece.anchor[1] + dc, board_rect)
            target = pygame.Rect(x, y, cell_sz, cell_sz).inflate(-12, -12)
            pygame.draw.rect(surface, _shade(HIGHLIGHT_COLOR, -35), target, width=5, border_radius=14)
            pygame.draw.circle(surface, HIGHLIGHT_COLOR, target.center, 8)

    for piece_id, piece in state.pieces.items():
        if piece_id in animations:
            progress, start, end = animations[piece_id]
            ease = 1.0 - (1.0 - progress) ** 2
            anchor = (start[0] + (end[0] - start[0]) * ease, start[1] + (end[1] - start[1]) * ease)
        else:
            anchor = piece.anchor

        color = PIECE_COLORS.get(piece.id, (120, 175, 86))
        cells = piece.occupied_cells(anchor)
        for row, col in cells:
            x, y = get_cell_pos(row, col, board_rect)
            rect = pygame.Rect(x, y, cell_sz, cell_sz).inflate(-11, -11)
            pygame.draw.rect(surface, _shade(color, -55), rect.move(0, 3), border_radius=14)
            pygame.draw.rect(surface, color, rect, border_radius=14)
            pygame.draw.line(surface, _shade(color, 50), (rect.x + 10, rect.y + 7), (rect.right - 10, rect.y + 7), 2)
            pygame.draw.rect(surface, _shade(color, -42), rect, width=2, border_radius=14)
            if piece_id == selected_piece_id:
                pygame.draw.rect(surface, SELECT_BORDER, rect.inflate(4, 4), width=4, border_radius=16)

        cell_list = list(cells)
        for first in cell_list:
            for second in cell_list:
                if abs(first[0] - second[0]) + abs(first[1] - second[1]) != 1:
                    continue
                x1, y1 = get_cell_pos(first[0], first[1], board_rect)
                x2, y2 = get_cell_pos(second[0], second[1], board_rect)
                bridge = pygame.Rect(min(x1, x2) + 18, min(y1, y2) + 18,
                                     abs(x1 - x2) + cell_sz - 36, abs(y1 - y2) + cell_sz - 36)
                pygame.draw.rect(surface, color, bridge, border_radius=8)

        if piece.type == "squirrel":
            nut_position = None
            if piece.nut_offset is not None:
                nut_position = (anchor[0] + piece.nut_offset[0], anchor[1] + piece.nut_offset[1])
            icon_offset, direction = _squirrel_layout(piece)
            icon_cell = (anchor[0] + icon_offset[0], anchor[1] + icon_offset[1])
            icon_x, icon_y = get_cell_pos(icon_cell[0], icon_cell[1], board_rect)
            draw_squirrel(surface, (icon_x + cell_sz // 2, icon_y + cell_sz // 2), color, direction)
            if nut_position:
                nut_x, nut_y = get_cell_pos(nut_position[0], nut_position[1], board_rect)
                center = (nut_x + cell_sz // 2, nut_y + cell_sz // 2)
                pygame.draw.circle(surface, (55, 42, 31), (center[0], center[1] + 2), cell_sz // 4 + 2)
                pygame.draw.circle(surface, NUT_SLOT_COLOR, center, cell_sz // 4 - 2)
                pygame.draw.circle(surface, _shade(NUT_SLOT_COLOR, 24), center, cell_sz // 4 - 2, 2)
                if piece.has_nut:
                    draw_acorn(surface, center, scale=0.72)
        elif piece.id == "flower":
            x, y = get_cell_pos(anchor[0], anchor[1], board_rect)
            draw_flower(surface, (x + cell_sz // 2, y + cell_sz // 2))


def make_app_icon():
    icon = pygame.Surface((128, 128), pygame.SRCALPHA)
    pygame.draw.circle(icon, (244, 241, 234), (64, 64), 61)
    pygame.draw.circle(icon, (139, 115, 85), (64, 64), 59, 6)
    draw_squirrel(icon, (58, 67), PIECE_COLORS["orange"], "RIGHT")
    draw_acorn(icon, (92, 79), scale=0.55)
    return icon
