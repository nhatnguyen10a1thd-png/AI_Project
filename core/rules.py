# core/rules.py
from core.constants import BOARD_SIZE, DIRECTIONS

class BoardRules:
    """Handles rules of the game: generating legal moves, checking collision, and applying state transitions."""
    
    @staticmethod
    def get_all_occupied(state, exclude_id=None):
        """Returns the set of all occupied cells on the board by all pieces except the specified one."""
        occupied = set()
        for pid, p in state.pieces.items():
            if pid == exclude_id:
                continue
            occupied.update(p.occupied_cells())
        return occupied

    @staticmethod
    def is_in_bounds(cells):
        """Checks if all cells in the set are within the 4x4 board boundaries."""
        for r, c in cells:
            if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                return False
        return True

    def can_move(self, state, piece_id, direction):
        """Checks if a piece can move in a given direction."""
        piece = state.pieces.get(piece_id)
        if not piece or not piece.movable:
            return False

        dr, dc = DIRECTIONS[direction]
        new_anchor = (piece.anchor[0] + dr, piece.anchor[1] + dc)
        new_cells = piece.occupied_cells(new_anchor)

        # Rule 1: Must remain inside the board
        if not self.is_in_bounds(new_cells):
            return False

        # Rule 2: Must not overlap with other pieces
        other_occupied = self.get_all_occupied(state, exclude_id=piece_id)
        if new_cells.intersection(other_occupied):
            return False

        return True

    def legal_actions(self, state):
        """
        Returns a list of all valid actions in the current state.
        Each action is represented as a tuple: (piece_id, direction)
        """
        actions = []
        for pid, p in state.pieces.items():
            if not p.movable:
                continue
            for direction in DIRECTIONS.keys():
                if self.can_move(state, pid, direction):
                    actions.append((pid, direction))
        return actions

    def apply_action(self, state, action):
        """
        Applies an action to the state and returns a new GameState.
        action: tuple (piece_id, direction)
        """
        piece_id, direction = action
        next_state = state.clone()
        
        piece = next_state.pieces[piece_id]
        dr, dc = DIRECTIONS[direction]
        piece.anchor = (piece.anchor[0] + dr, piece.anchor[1] + dc)
        
        # Check if the moved piece dropped its acorn
        if piece.type == "squirrel" and piece.has_nut:
            nut_pos = piece.nut_position()
            if nut_pos in next_state.holes and nut_pos not in next_state.filled_holes:
                # The nut drops into the hole!
                piece.has_nut = False
                next_state.filled_holes.add(nut_pos)

        return next_state
