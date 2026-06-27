import json
import os
import sys

import pytest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.level import LevelManager, LevelValidationError


def _write_levels(tmp_path, payload):
    path = tmp_path / "levels.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def test_book_levels_pass_validation():
    manager = LevelManager()

    assert manager.get_difficulties()
    assert sum(len(manager.get_levels_by_difficulty(diff)) for diff in manager.get_difficulties()) == 32


def test_validation_rejects_overlapping_pieces(tmp_path):
    level_path = _write_levels(
        tmp_path,
        {
            "starter": [
                {
                    "id": "bad_overlap",
                    "name": "Bad Overlap",
                    "difficulty": "Starter",
                    "target_moves": 1,
                    "holes": [[0, 0]],
                    "pieces": [
                        {
                            "id": "orange",
                            "type": "squirrel",
                            "cells": [[1, 1]],
                            "nut": [1, 1],
                            "has_nut": True,
                        },
                        {
                            "id": "flower",
                            "type": "block",
                            "cells": [[1, 1]],
                        },
                    ],
                }
            ]
        },
    )

    with pytest.raises(LevelValidationError, match="overlaps"):
        LevelManager(level_path)


def test_validation_rejects_nut_outside_piece(tmp_path):
    level_path = _write_levels(
        tmp_path,
        {
            "starter": [
                {
                    "id": "bad_nut",
                    "name": "Bad Nut",
                    "difficulty": "Starter",
                    "target_moves": 1,
                    "holes": [[0, 0]],
                    "pieces": [
                        {
                            "id": "orange",
                            "type": "squirrel",
                            "cells": [[1, 1]],
                            "nut": [1, 2],
                            "has_nut": True,
                        }
                    ],
                }
            ]
        },
    )

    with pytest.raises(LevelValidationError, match="not on the piece"):
        LevelManager(level_path)
