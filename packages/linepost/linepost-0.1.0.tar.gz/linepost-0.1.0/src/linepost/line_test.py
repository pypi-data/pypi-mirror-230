import pytest

from linepost.line import (REMARK_POINTER_PATTERN, Line, Token, can_parse_line,
                           parse_line, unlabel_pattern)
from linepost.position import Game


@pytest.mark.parametrize("pattern,unlabeled_pattern", [
    ("asdf", "asdf"),
    ("(?P<label>NBRQK)", "(?:NBRQK)"),
])
def test_unlabel_pattern(pattern, unlabeled_pattern):
    assert unlabel_pattern(pattern) == unlabeled_pattern


# TODO: Generate these for more complete coverage
@pytest.mark.parametrize("string,want_bool", [
    ('e4', True),
    ('c6', True),
    ('e0', False),
    ('e9', False),
    ('cxd5', True),
    ('cxd9', False),
    ('cx6', False),
    ('hxg5', True),
    ('hxi5', False),
    ('ixh5', False),
    ('e1=N', True),
    ('f8=B+', True),
    ('gxh8=R', True),
    ('axb1=Q+', True),
    ('b8N', True),
    ('cxd8B', True),
    ('d8R', True),
    ('e8Q', True),
    ('a8=K', False),
    ('a1K', False),
    ('+', False),
    ('#', False),
    ('a1+', True),
    ('a8#', True),
    ('Ne7', True),
    ('Bf4', True),
    ('Re1', True),
    ('Qh5', True),
    ('Ke2', True),
    ('Jh5', False),
    ('Qe0', False),
    ('Rj5', False),
    ('B4', False),
    ('Nbd2', True),
    ('N4d2', True),
    ('Nc4d2', False),
    ('N4cd2', False),
    ('Rxb1', True),
    ('Raxb1', True),
    ('R3xb2', True),
    ('Rb3xb2', False),
    ('Raxb1=Q', False),
    ('Raxb1#', True),
    ('Ke2?', True),
    ('Ke2!', True),
    ('Ke2!!', True),
    ('Bf4??', True),
    ('a4?!', True),
    ('a4!?', True),
    ('!', False),
    ('?', False),
    ('o', False),
    ('o-o', True),
    ('o-o-o', True),
    ('o-o#', True),
    ('o-o-o??', True),
    ('o-o-o-o', False),
    ('O', False),
    ('O-O', True),
    ('O-O-O', True),
    ('O-O+', True),
    ('O-O-O!!', True),
    ('O-O-O-O', False),
    ('chess move', False),
    ('p17', False),
    ('P17', False),
    ('m17', False),
    ('M17', False),
])
def test_is_chess_move(string, want_bool):
    token = Token(string)
    got_bool = token.is_chess_move()
    assert want_bool == got_bool


@pytest.mark.parametrize("string,want_move,want_eval", [
    ('great move', None, None),
    ('Nf3', 'Nf3', None),
    ('Nf3!!', 'Nf3', '!!'),
])
def test_chess_tokens(string, want_move, want_eval):
    token = Token(string)
    assert want_move == token.get_move()
    assert want_eval == token.get_evaluation()


@pytest.mark.parametrize("string,want_remark_type,want_remark_index", [
    ('great move', None, None),
    ('Nf3', None, None),
    ('Nf3!!', None, None),
    ('p2', 'p', 2),
    ('P3', 'p', 3),
    ('m4', 'm', 4),
    ('M5', 'm', 5),
])
def test_remark_tokens(string, want_remark_type, want_remark_index):
    token = Token(string)
    assert want_remark_type == token.get_remark_type()
    assert want_remark_index == token.get_remark_index()


@pytest.mark.parametrize(
    "string,want_bool",
    [
        ('q4', False),
        ('e4 c"comment"', False),
        ('e4 d5 k"die"', False),
        ('e4 p"Best by test" p"Black has many responses"', True),
        ('d4 m"I better not see another London" d5 Bf4?! m"really?!" m"goddammit" p"I am rooting for Black now"',
         True),  # noqa: E501
        ('d4 m"I better not see another London" d5 Bf4?! c"really?!" m"goddammit" p"I am rooting for Black now"',
         False),  # noqa: E501
    ])
def test_can_parse_line(string, want_bool):
    assert want_bool == can_parse_line(string)


@pytest.mark.parametrize(
    "line,want_tokens,want_position_remarks,want_move_remarks", [
        ('c4? e5!', ['c4?', 'e5!'], [], []),
        ('c4?        e5!', ['c4?', 'e5!'], [], []),
        ('e4 m"Be bold!" p"Best by test" p"Black has many responses"', [
            'e4', 'm0', 'p0', 'p1'
        ], ['Best by test', 'Black has many responses'], ['Be bold!']),
    ])
def test_parse_line(line, want_tokens, want_position_remarks,
                    want_move_remarks):
    tokens, position_remarks, move_remarks = parse_line(line)
    assert want_tokens == list(map(str, tokens))
    assert want_position_remarks == position_remarks
    assert want_move_remarks == move_remarks


@pytest.mark.parametrize("line", [
    '',
    '     ',
    'Q7',
    'e4 e5 j7',
    'this probably does not work',
    'p"this also should not work"',
    'm"nor this"',
])
def test_parse_line_invalid(line):
    with pytest.raises(ValueError):
        _ = parse_line(line)


@pytest.mark.parametrize(
    "string,want_labels,want_evals_by_index,want_pos_remarks_by_index,want_move_remarks_by_index",  # noqa: E501
    [
        ('e4 e5 Nf3', ['e4', 'e5', 'Nf3'], {}, {}, {}),
        ('e4   e5   Nf3', ['e4', 'e5', 'Nf3'], {}, {}, {}),
        ('  e4 e5 Nf3', ['e4', 'e5', 'Nf3'], {}, {}, {}),
        ('e4 e5 Nf3 Nc6', ['e4', 'e5', 'Nf3', 'Nc6'], {}, {}, {}),
        ('e4', ['e4'], {}, {}, {}),
        ('e4 p"Best by test" p"Black has many responses"', ['e4'], {}, {
            1: {'Black has many responses', 'Best by test'},
        }, {}),
        ('e4    p"Best by test"   p"Black has many responses"', ['e4'], {}, {
            1: {'Black has many responses', 'Best by test'},
        }, {}),
        ('    e4    p"Best by test"   p"Black has many responses"', ['e4'], {},
         {
             1: {'Black has many responses', 'Best by test'},
         }, {}),
        (
            'd4 m"I better not see another London" d5 Bf4?! m"really?!" m"goddammit" p"I am rooting for Black now"',  # noqa: E501
            ['d4', 'd5', 'Bf4'],
            {
                3: '?!'
            },
            {
                3: {'I am rooting for Black now'},
            },
            {
                1: {'I better not see another London'},
                3: {'really?!', 'goddammit'}
            }),
    ])
def test_lines(string, want_labels, want_evals_by_index,
               want_pos_remarks_by_index, want_move_remarks_by_index):
    game = Game()
    line = Line(string, game)
    assert len(want_labels) + 1 == len(line.line)
    for i, position in enumerate(line.line):
        if i < len(line.line) - 1:
            assert position.remarks == want_pos_remarks_by_index.get(i, set())
            move = None
            for move_key in position.moves:
                move = position.moves[move_key]
                break
            assert move.label == want_labels[i]
            assert move.evaluation == want_evals_by_index.get(i + 1, '')
            assert move.remarks == want_move_remarks_by_index.get(i + 1, set())
        else:
            assert len(position.moves) == 0


@pytest.mark.parametrize("string", [
    "",
    "   ",
    "e5",
    "e4 Bc5",
    "e4 e5 O-O O-O",
])
def test_invalid_lines(string):
    game = Game()
    with pytest.raises(ValueError):
        _ = Line(string, game)


@pytest.mark.parametrize("string", [
    'e4 c"comment"',
    'e4 d5 k"die"',
])
def test_invalid_comments(string):
    game = Game()
    with pytest.raises(ValueError):
        _ = Line(string, game)
