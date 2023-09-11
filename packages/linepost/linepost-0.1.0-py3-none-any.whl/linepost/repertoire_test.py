import pytest

from linepost.repertoire import Repertoire, get_line_and_start


@pytest.mark.parametrize("line, want_text, want_index", [
    ('e4 e5', 'e4 e5', 0),
    ('e4 d5?', 'e4 d5?', 0),
    ('@2b c6', 'c6', 3),
    ('@2w d4', 'd4', 2),
    ('@2 d4', 'd4', 2),
    ('@4w d4', 'd4', 6),
])
def test_line_with_ref(line, want_text, want_index):
    got_text, got_index = get_line_and_start(line)
    assert want_text == got_text
    assert want_index == got_index


def test_add_invalid_no_change():
    rep = Repertoire()
    rep.add_line('e4 e5 Ke2')
    with pytest.raises(ValueError):
        rep.add_line('d4 d4')
    assert len(rep.lines) == 1
    assert len(rep.lines[0].line) == 4
    assert len(rep.game.fens) == 4
    with pytest.raises(ValueError):
        rep.add_line('c4 Be5')
    assert len(rep.lines) == 1
    assert len(rep.lines[0].line) == 4
    assert len(rep.game.fens) == 4


@pytest.mark.parametrize("lines", [
    [
        'e4 e5 Nf3',
        'e4 c5 Nf3',
    ],
    [
        'e4 e5 Nf3',
        '',
        'e4 c5 Nf3',
    ],
    [
        'e4 e5 Nf3',
        '    ',
        'e4 c5 Nf3',
    ],
    [
        'e4 e5 Nf3',
        '# Some people hate it, but you can play the Alapin if you want',
        'e4 c5 c3',
    ],
    [
        'e4 e5 Nf3\n',
        'e4 c5 Nf3\n',
    ],
    [
        'e4 e5 Nf3\n',
        '\n',
        'e4 c5 Nf3\n',
    ],
    [
        'e4 e5 Nf3\n',
        '    \n',
        'e4 c5 Nf3\n',
    ],
    [
        'e4 e5 Nf3\n',
        '# Some people hate it, but you can play the Alapin if you want\n',
        'e4 c5 c3\n',
    ],
])
def test_lines(lines):
    _ = Repertoire.from_lines(lines)


def test_invalid_lines():
    lines = [
        "e4 e5 Nf3 Nc6 Bc4 Bc5 b4",
        "e4 e5 Nf6",
        "e4 e5 Nf3 Nc6 Bc4 Nf6 d4",
        "e4 e5 Nf3 d6 e3",
        "e4 c5 c3",
    ]
    with pytest.raises(ValueError):
        _ = Repertoire.from_lines(lines)


def test_skip_invalid():
    valid_lines = [
        "e4 e5 Nf3 Nc6 Bc4 Bc5 b4",
        "e4 e5 Nf3 Nc6 Bc4 Nf6 d4",
        "e4 c5 c3",
    ]
    invalid_lines = [
        "e4 e5 Nf3 Nc6 Bc4 Bc5 b4",
        "e4 e5 Nf6",
        "e4 e5 Nf3 Nc6 Bc4 Nf6 d4",
        "e4 e5 Nf3 d6 e3",
        "e4 c5 c3",
    ]

    valid_rep = Repertoire.from_lines(valid_lines)
    invalid_rep = Repertoire.from_lines(invalid_lines, skip_invalid=True)
    assert len(valid_rep.lines) == len(invalid_rep.lines)
    assert len(valid_rep.game.fens) == len(invalid_rep.game.fens)


@pytest.mark.parametrize("lines", [
    [
        '@1b e5',
    ],
    [
        'e4 e5',
        '@2b d4',
    ],
])
def test_invalid_reference(lines):
    with pytest.raises(ValueError):
        _ = Repertoire.from_lines(lines)


def test_reference_equivalence():
    lines = [
        'e4 e5 Nf3 Nc6',
        'e4 e5 Nf3 Nf6',
        'e4 e5 f4 d5',
    ]
    lines_with_ref = [
        'e4 e5 Nf3 Nc6',
        '@2b Nf6',
        '@2 f4 d5',
    ]
    rep = Repertoire.from_lines(lines)
    rep_with_ref = Repertoire.from_lines(lines_with_ref)
    assert len(rep.lines) == len(rep_with_ref.lines)
    assert len(rep.game.fens) == len(rep_with_ref.game.fens)
