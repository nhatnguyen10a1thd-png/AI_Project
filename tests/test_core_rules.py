import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.piece import Piece
from core.rules import BoardRules
from core.state import GameState


def test_apply_action_returns_new_state_and_drops_nut():
    state = GameState(
        pieces={
            "orange": Piece(
                piece_id="orange",
                piece_type="squirrel",
                shape=[(0, 0), (0, 1)],
                anchor=(1, 1),
                nut_offset=(0, 0),
                has_nut=True,
            )
        },
        holes={(1, 0)},
    )
    rules = BoardRules()

    assert rules.can_move(state, "orange", "LEFT")
    next_state = rules.apply_action(state, ("orange", "LEFT"))

    assert state.pieces["orange"].anchor == (1, 1)
    assert state.pieces["orange"].has_nut is True
    assert state.filled_holes == set()

    assert next_state.pieces["orange"].anchor == (1, 0)
    assert next_state.pieces["orange"].has_nut is False
    assert next_state.filled_holes == {(1, 0)}
    assert next_state.is_goal()


def test_can_move_rejects_overlap_and_out_of_bounds():
    rules = BoardRules()
    overlap_state = GameState(
        pieces={
            "orange": Piece("orange", "squirrel", [(0, 0)], (1, 1), (0, 0), True),
            "flower": Piece("flower", "block", [(0, 0)], (1, 0), movable=False),
        },
        holes={(0, 0)},
    )
    edge_state = GameState(
        pieces={
            "orange": Piece("orange", "squirrel", [(0, 0)], (0, 0), (0, 0), True),
        },
        holes={(0, 0)},
    )

    assert not rules.can_move(overlap_state, "orange", "LEFT")
    assert not rules.can_move(edge_state, "orange", "UP")


def test_encode_tracks_anchor_and_filled_holes():
    state = GameState(
        pieces={
            "orange": Piece("orange", "squirrel", [(0, 0)], (0, 1), (0, 0), True),
        },
        holes={(0, 0)},
    )
    next_state = BoardRules().apply_action(state, ("orange", "LEFT"))

    assert state.encode() != next_state.encode()
    assert ((0, 0),) == next_state.encode()[1]
