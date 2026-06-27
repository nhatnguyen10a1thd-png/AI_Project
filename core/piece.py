# core/piece.py

class Piece:
    """Represents a sliding puzzle piece (squirrel or flower block)."""
    def __init__(self, piece_id, piece_type, shape, anchor, nut_offset=None, has_nut=False, movable=True):
        self.id = piece_id          # e.g., "brown", "black", "flower"
        self.type = piece_type      # "squirrel" or "block"
        self.shape = [tuple(cell) for cell in shape]  # List of (dr, dc) offsets relative to anchor
        self.anchor = tuple(anchor) # (row, col) coordinates of anchor
        self.nut_offset = tuple(nut_offset) if nut_offset is not None else None # (dr, dc) offset for nut
        self.has_nut = has_nut      # True if it's a squirrel and still has its acorn
        self.movable = movable      # Whether the piece is allowed to slide

    def occupied_cells(self, anchor=None):
        """Returns the absolute cells occupied by this piece on the board given an anchor."""
        base = tuple(anchor) if anchor is not None else self.anchor
        return {(base[0] + dr, base[1] + dc) for (dr, dc) in self.shape}

    def nut_position(self, anchor=None):
        """Returns the absolute position of the nut if the piece has a nut."""
        if not self.has_nut or self.nut_offset is None:
            return None
        base = tuple(anchor) if anchor is not None else self.anchor
        return (base[0] + self.nut_offset[0], base[1] + self.nut_offset[1])

    def clone(self):
        """Creates a deep copy of the piece."""
        return Piece(
            piece_id=self.id,
            piece_type=self.type,
            shape=self.shape,
            anchor=self.anchor,
            nut_offset=self.nut_offset,
            has_nut=self.has_nut,
            movable=self.movable
        )

    def __repr__(self):
        return f"Piece({self.id}, type={self.type}, anchor={self.anchor}, has_nut={self.has_nut})"
