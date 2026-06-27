# core/state.py

class GameState:
    """Represents a specific state of the board and pieces, which is hashable for search algorithms."""
    def __init__(self, pieces, holes, filled_holes=None):
        # pieces: dict of piece_id -> Piece object
        self.pieces = {pid: p.clone() for pid, p in pieces.items()}
        # holes: set of (row, col) coordinates of all holes on the board
        self.holes = set(holes)
        # filled_holes: set of (row, col) coordinates of holes already containing dropped acorns
        self.filled_holes = set(filled_holes) if filled_holes is not None else set()

    def clone(self):
        """Creates a copy of the GameState."""
        return GameState(self.pieces, self.holes, self.filled_holes)

    def encode(self):
        """
        Returns a hashable tuple representation of the state.
        Format: ( ( (piece_id, anchor_r, anchor_c, has_nut), ... ), ( (filled_h_r, filled_h_c), ... ) )
        The piece tuples are sorted by piece_id to ensure a unique representation.
        """
        pieces_list = []
        for pid in sorted(self.pieces.keys()):
            p = self.pieces[pid]
            pieces_list.append((pid, p.anchor[0], p.anchor[1], p.has_nut))
        
        filled_holes_list = sorted(list(self.filled_holes))
        
        return (tuple(pieces_list), tuple(filled_holes_list))

    def is_goal(self):
        """Returns True if all squirrels have dropped their nuts into holes."""
        for p in self.pieces.values():
            if p.type == "squirrel" and p.has_nut:
                return False
        return True

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return self.encode() == other.encode()

    def __hash__(self):
        return hash(self.encode())

    def __repr__(self):
        return f"GameState(pieces={list(self.pieces.values())}, filled_holes={self.filled_holes})"
