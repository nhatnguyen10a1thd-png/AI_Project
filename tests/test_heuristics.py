import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai.informed.heuristics import squirrel_heuristic
from core.piece import Piece
from core.state import GameState


def test_heuristic_uses_distinct_hole_assignment():
    state = GameState(
        pieces={
            "orange": Piece("orange", "squirrel", [(0, 0)], (0, 0), (0, 0), True),
            "white": Piece("white", "squirrel", [(0, 0)], (0, 1), (0, 0), True),
        },
        holes={(0, 0), (3, 3)},
    )

    assert squirrel_heuristic(state) == 5


def test_heuristic_is_zero_when_no_active_nuts():
    state = GameState(
        pieces={
            "orange": Piece("orange", "squirrel", [(0, 0)], (0, 0), (0, 0), False),
        },
        holes={(0, 0)},
    )

    assert squirrel_heuristic(state) == 0
