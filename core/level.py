# core/level.py
import json
import os
from core.constants import BOARD_SIZE
from core.piece import Piece
from core.state import GameState


class LevelValidationError(ValueError):
    """Raised when level JSON contains invalid board data."""


class LevelManager:
    """Manages loading and validating levels from JSON configuration."""
    def __init__(self, file_path=None):
        if file_path is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(current_dir, "data", "book_levels.json")
        
        self.file_path = file_path
        self.levels_data = {}
        self.load_all_levels()

    def load_all_levels(self):
        """Loads levels from the JSON file."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Levels file not found: {self.file_path}")
        
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.levels_data = json.load(f)
        self.validate_all_levels()

    def get_difficulties(self):
        """Returns the list of available difficulties."""
        return list(self.levels_data.keys())

    def get_levels_by_difficulty(self, difficulty):
        """Returns the list of levels for a specific difficulty."""
        return self.levels_data.get(difficulty.lower(), [])

    @staticmethod
    def _coord(value):
        if (
            isinstance(value, (list, tuple))
            and len(value) == 2
            and all(isinstance(v, int) for v in value)
        ):
            return tuple(value)
        return None

    @staticmethod
    def _in_bounds(coord):
        row, col = coord
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def validate_all_levels(self):
        """Validate every level and raise a grouped error if anything is invalid."""
        errors = []
        if not isinstance(self.levels_data, dict):
            raise LevelValidationError("Level file root must be an object keyed by difficulty.")

        seen_level_ids = set()
        for difficulty, levels in self.levels_data.items():
            if not isinstance(levels, list):
                errors.append(f"{difficulty}: difficulty value must be a list of levels")
                continue
            for level in levels:
                errors.extend(self.validate_level(level, difficulty, seen_level_ids))

        if errors:
            formatted = "\n- ".join(errors)
            raise LevelValidationError(f"Invalid level data:\n- {formatted}")

    def validate_level(self, level_dict, difficulty=None, seen_level_ids=None):
        """Return a list of validation errors for one level dictionary."""
        errors = []
        if not isinstance(level_dict, dict):
            return [f"{difficulty or '<unknown>'}: level must be an object"]

        level_id = level_dict.get("id", "<missing id>")
        label = f"{difficulty or level_dict.get('difficulty', '<unknown>')}/{level_id}"

        def add_error(message):
            errors.append(f"{label}: {message}")

        if not isinstance(level_dict.get("id"), str) or not level_dict["id"]:
            add_error("missing or invalid string id")
        elif seen_level_ids is not None:
            if level_dict["id"] in seen_level_ids:
                add_error(f"duplicate level id '{level_dict['id']}'")
            seen_level_ids.add(level_dict["id"])

        if not isinstance(level_dict.get("name"), str) or not level_dict["name"]:
            add_error("missing or invalid level name")

        target_moves = level_dict.get("target_moves")
        if target_moves is not None and (
            not isinstance(target_moves, int) or target_moves <= 0
        ):
            add_error("target_moves must be a positive integer when present")

        raw_holes = level_dict.get("holes")
        holes = set()
        if not isinstance(raw_holes, list) or not raw_holes:
            add_error("holes must be a non-empty list")
        else:
            for index, raw_hole in enumerate(raw_holes):
                hole = self._coord(raw_hole)
                if hole is None:
                    add_error(f"hole[{index}] must be a [row, col] integer pair")
                    continue
                if not self._in_bounds(hole):
                    add_error(f"hole[{index}] {hole} is out of bounds")
                if hole in holes:
                    add_error(f"duplicate hole {hole}")
                holes.add(hole)

        raw_pieces = level_dict.get("pieces")
        if not isinstance(raw_pieces, list) or not raw_pieces:
            add_error("pieces must be a non-empty list")
            return errors

        piece_ids = set()
        occupied_by = {}
        squirrel_count = 0

        for piece_index, piece_data in enumerate(raw_pieces):
            if not isinstance(piece_data, dict):
                add_error(f"pieces[{piece_index}] must be an object")
                continue

            piece_id = piece_data.get("id")
            if not isinstance(piece_id, str) or not piece_id:
                add_error(f"pieces[{piece_index}] has missing or invalid id")
                piece_id = f"<piece {piece_index}>"
            elif piece_id in piece_ids:
                add_error(f"duplicate piece id '{piece_id}'")
            piece_ids.add(piece_id)

            piece_type = piece_data.get("type")
            if piece_type not in {"squirrel", "block"}:
                add_error(f"piece '{piece_id}' has invalid type '{piece_type}'")
            if piece_type == "squirrel":
                squirrel_count += 1

            cells = []
            anchor = None
            if "cells" in piece_data:
                raw_cells = piece_data["cells"]
                if not isinstance(raw_cells, list) or not raw_cells:
                    add_error(f"piece '{piece_id}' cells must be a non-empty list")
                else:
                    for cell_index, raw_cell in enumerate(raw_cells):
                        cell = self._coord(raw_cell)
                        if cell is None:
                            add_error(
                                f"piece '{piece_id}' cell[{cell_index}] must be a [row, col] integer pair"
                            )
                            continue
                        if not self._in_bounds(cell):
                            add_error(f"piece '{piece_id}' cell {cell} is out of bounds")
                        cells.append(cell)
                    if cells:
                        anchor = (min(row for row, _ in cells), min(col for _, col in cells))
            elif "shape" in piece_data and "anchor" in piece_data:
                anchor = self._coord(piece_data["anchor"])
                if anchor is None:
                    add_error(f"piece '{piece_id}' anchor must be a [row, col] integer pair")
                shape = piece_data.get("shape")
                if not isinstance(shape, list) or not shape:
                    add_error(f"piece '{piece_id}' shape must be a non-empty list")
                elif anchor is not None:
                    for shape_index, raw_offset in enumerate(shape):
                        offset = self._coord(raw_offset)
                        if offset is None:
                            add_error(
                                f"piece '{piece_id}' shape[{shape_index}] must be a [dr, dc] integer pair"
                            )
                            continue
                        cell = (anchor[0] + offset[0], anchor[1] + offset[1])
                        if not self._in_bounds(cell):
                            add_error(f"piece '{piece_id}' cell {cell} is out of bounds")
                        cells.append(cell)
            else:
                add_error(f"piece '{piece_id}' must define either cells or shape+anchor")

            seen_cells = set()
            for cell in cells:
                if cell in seen_cells:
                    add_error(f"piece '{piece_id}' repeats cell {cell}")
                seen_cells.add(cell)
                previous = occupied_by.get(cell)
                if previous is not None:
                    add_error(f"piece '{piece_id}' overlaps piece '{previous}' at {cell}")
                else:
                    occupied_by[cell] = piece_id

            has_nut = piece_data.get("has_nut", False)
            if not isinstance(has_nut, bool):
                add_error(f"piece '{piece_id}' has_nut must be a boolean")
            if piece_type != "squirrel" and has_nut:
                add_error(f"non-squirrel piece '{piece_id}' cannot have a nut")

            nut_position = None
            if "nut" in piece_data:
                nut_position = self._coord(piece_data["nut"])
                if nut_position is None:
                    add_error(f"piece '{piece_id}' nut must be a [row, col] integer pair")
                elif not self._in_bounds(nut_position):
                    add_error(f"piece '{piece_id}' nut {nut_position} is out of bounds")
            elif "nut_offset" in piece_data:
                nut_offset = self._coord(piece_data["nut_offset"])
                if nut_offset is None:
                    add_error(f"piece '{piece_id}' nut_offset must be a [dr, dc] integer pair")
                elif anchor is not None:
                    nut_position = (anchor[0] + nut_offset[0], anchor[1] + nut_offset[1])
                    if not self._in_bounds(nut_position):
                        add_error(f"piece '{piece_id}' nut {nut_position} is out of bounds")

            if piece_type == "squirrel" and has_nut:
                if nut_position is None:
                    add_error(f"squirrel '{piece_id}' has_nut=True but has no nut position")
                elif nut_position not in set(cells):
                    add_error(f"squirrel '{piece_id}' nut {nut_position} is not on the piece")

        if squirrel_count == 0:
            add_error("level must contain at least one squirrel")

        return errors

    def create_game_state(self, level_dict):
        """Creates a GameState object from the level dictionary config."""
        pieces = {}
        holes = {tuple(h) for h in level_dict["holes"]}
        
        for p_data in level_dict["pieces"]:
            pid = p_data["id"]
            ptype = p_data["type"]
            if "cells" in p_data:
                cells = [tuple(cell) for cell in p_data["cells"]]
                anchor = [min(r for r, _ in cells), min(c for _, c in cells)]
                shape = [[r - anchor[0], c - anchor[1]] for r, c in cells]
                nut = p_data.get("nut")
                nut_offset = [nut[0] - anchor[0], nut[1] - anchor[1]] if nut else None
            else:
                shape = p_data["shape"]
                anchor = p_data["anchor"]
                nut_offset = p_data.get("nut_offset")
            has_nut = p_data.get("has_nut", False)
            
            # The red flower (or blocks with ID "flower") is stationary by default
            movable = p_data.get("movable", pid != "flower")
            
            pieces[pid] = Piece(
                piece_id=pid,
                piece_type=ptype,
                shape=shape,
                anchor=anchor,
                nut_offset=nut_offset,
                has_nut=has_nut,
                movable=movable
            )
            
        return GameState(pieces, holes)

    def load_level(self, difficulty, level_id):
        """Loads a specific level by ID and returns (metadata, initial_state)."""
        levels = self.get_levels_by_difficulty(difficulty)
        for lvl in levels:
            if lvl["id"] == level_id:
                state = self.create_game_state(lvl)
                return lvl, state
        raise ValueError(f"Level not found: {level_id} in {difficulty}")
