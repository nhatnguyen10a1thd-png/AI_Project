# core/level.py
import json
import os
from core.piece import Piece
from core.state import GameState

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

    def get_difficulties(self):
        """Returns the list of available difficulties."""
        return list(self.levels_data.keys())

    def get_levels_by_difficulty(self, difficulty):
        """Returns the list of levels for a specific difficulty."""
        return self.levels_data.get(difficulty.lower(), [])

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
