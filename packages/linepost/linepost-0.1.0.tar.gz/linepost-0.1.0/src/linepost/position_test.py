import chess
import pytest

from linepost.position import Game, Position


@pytest.mark.parametrize(
    "move_label,evaluation,position_remarks,move_remarks", [
        ("e4", "", set(), set()),
        ("Nc3", "?!", {"No one in the center"}, {"Why, tho?"}),
        ("b4", "!!", set(), {"Hi, lularobs!", "bishop bait!"}),
    ])
def test_move(move_label, evaluation, position_remarks, move_remarks):
    game = Game()
    pos = Position(game, chess.Board())
    next_pos = pos.make_move(move_label, evaluation, position_remarks,
                             move_remarks)
    assert len(pos.moves) == 1
    assert next_pos.remarks == position_remarks
    move = None
    for move_key in pos.moves:
        move = pos.moves[move_key]
        break
    assert move.label == move_label
    assert move.evaluation == evaluation
    assert move.remarks == move_remarks
    assert move.from_position == pos
    assert move.to_position == next_pos


@pytest.mark.parametrize("moves", [
    [],
    ["e4"],
    ["d4"],
    ["e4", "c6"],
    ["e4", "e5", "Nf3"],
    ["d4", "d5", "c4", "c6"],
    ["e4", "e5", "Nf3", "Nc6", "Bc4"],
])
def test_turn(moves):
    whites_turn = len(moves) % 2 == 0
    game = Game()
    pos = Position(game, chess.Board())
    for move in moves:
        pos = pos.make_move(move)
    assert pos.white_to_move() == whites_turn


@pytest.mark.parametrize("move", [
    ("e5"),
    ("Ke2"),
    ("O-O"),
])
def test_invalid_move(move):
    game = Game()
    pos = Position(game, chess.Board())
    with pytest.raises(ValueError):
        _ = pos.make_move(move)


def test_invalid_move_merge():
    game = Game()
    pos = Position(game, chess.Board())
    pos1 = pos.make_move("e4")
    pos2 = pos.make_move("d4")
    moves = list(pos.moves.values())
    with pytest.raises(ValueError):
        moves[0].merge(moves[1])


@pytest.mark.parametrize("moves,want", [
    (["e4"], "1: e4"),
    (["d4"], "1: d4"),
    (["e4", "c6"], "1.. c6"),
    (["e4", "e5", "Nf3"], "2: Nf3"),
    (["d4", "d5", "c4", "c6"], "2.. c6"),
    (["e4", "e5", "Nf3", "Nc6", "Bc4"], "3: Bc4"),
])
def test_move_label(moves, want):
    whites_turn = len(moves) % 2 == 0
    game = Game()
    pos = Position(game, chess.Board())
    pos_old = None
    for move in moves:
        pos_old = pos
        pos = pos.make_move(move)
    move = list(pos_old.moves.values())[0]
    assert str(move) == want
