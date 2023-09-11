"""Line stores a single opening line from algebraic notation.
"""

import re
from typing import Generator, Iterable, List, Optional, Tuple

import chess

from linepost.position import Game, Move, Position

COORDINATE_PATTERN = '[a-h][1-8]'
PROMOTION_PATTERN = r'(?:\=)?[NBRQ]'
PAWN_PATTERN = f'(?:[a-h]x)?{COORDINATE_PATTERN}(?:{PROMOTION_PATTERN})?'
PIECE_PATTERN = f'(?:[NBRQK][a-h1-8]?x?{COORDINATE_PATTERN})'
CASTLES_PATTERN = '[oO](?:-[oO]){1,2}'
CHECK_PATTERN = '[+#]'
ONCE_PATTERN = '{1}'
MOVE_PATTERN = f'(?:{PAWN_PATTERN}|{PIECE_PATTERN}|{CASTLES_PATTERN}){ONCE_PATTERN}{CHECK_PATTERN}?'  # noqa: E501
EVALUATION_PATTERN = r'\?\?|\?|\?!|!\?|!|!!'
MOVE_LABEL = 'move'
EVAL_LABEL = 'eval'
MOVE_EVAL_PATTERN = f'(?P<{MOVE_LABEL}>{MOVE_PATTERN})(?P<{EVAL_LABEL}>{EVALUATION_PATTERN})?'
MOVE_REGEX = re.compile(f'^{MOVE_EVAL_PATTERN}$')

POS_PREFIX = 'pP'
MOVE_PREFIX = 'mM'
PREFIX_PATTERN = f'[{POS_PREFIX}{MOVE_PREFIX}]{ONCE_PATTERN}'
PREFIX_LABEL = 'prefix'
REMARK_LABEL = 'remark'
REMARK_PATTERN = f'(?P<{PREFIX_LABEL}>{PREFIX_PATTERN})"(?P<{REMARK_LABEL}>[^"]*?)"'
REMARK_POINTER_PATTERN = f'(?P<{PREFIX_LABEL}>{PREFIX_PATTERN})(?P<{REMARK_LABEL}>\\d+)'
REMARK_POINTER_REGEX = re.compile(f'^{REMARK_POINTER_PATTERN}$')
MOVE_REMARK = 'move'
POSITION_REMARK = 'position'


def unlabel_pattern(pattern: str) -> str:
    """Removes the named capture groups of a regex pattern.

    Args:
        pattern: The original pattern.
    Returns:
        Pattern with all named capture groups replaced by non-capturing groups.
    """
    return re.sub('P<.*?>', ':', pattern)


FULL_MOVE_PATTERN = f'{MOVE_EVAL_PATTERN}(\\s+{REMARK_PATTERN})*'
FULL_LINE_PATTERN = f'{FULL_MOVE_PATTERN}(\\s+{FULL_MOVE_PATTERN})*'
FULL_LINE_REGEX = re.compile(f'^\\s*{unlabel_pattern(FULL_LINE_PATTERN)}$')


class Token:
    """Textual representation of a chess move, evaluation, or comment.

    It can be any legal chess move, with or without evaluations (e.g. ?, !), or
    it can be part of a commentary about a move or position.
    """

    def __init__(self, s: str):
        """Initializes the token based on whether it's chess move.

        Args:
            s: The raw string.
        """
        self._raw = s
        self._match_chess = MOVE_REGEX.match(self._raw)
        self._match_remark = REMARK_POINTER_REGEX.match(self._raw)

    def is_chess_move(self) -> bool:
        """Whether this token represents a chess move.

        Returns:
            Whether this move matches the compiled MOVE_REGEX.
        """
        return self._match_chess is not None

    def get_move(self) -> Optional[str]:
        """If this is a chess move, returns the move label.

        Returns:
            The move portion of the chess token.
        """
        return self._match_chess.group(
            MOVE_LABEL) if self.is_chess_move() else None

    def get_evaluation(self) -> Optional[str]:
        """If this is a chess move, returns the evaluation portion.

        Returns:
            The evaluation portion of the chess token.
        """
        return self._match_chess.group(
            EVAL_LABEL) if self.is_chess_move() else None

    def get_remark_type(self) -> Optional[str]:
        """If this is a remark token, return the remark type.

        If this is a Position Remark, returns p or P (the first character).
        If this is a Move Remark, returns m or M (the first character).

        Returns:
            The remark type.
        """
        if self._match_remark is None:
            return None
        remark_type = self._match_remark.group(PREFIX_LABEL)
        if remark_type in POS_PREFIX:
            return POS_PREFIX[0]
        elif remark_type in MOVE_PREFIX:
            return MOVE_PREFIX[0]
        return None

    def get_remark_index(self) -> Optional[int]:
        """If this is a remark token, return the remark index.

        Returns:
            The remark index in its respective list.
        """
        if self._match_remark is None:
            return None
        return int(self._match_remark.group(REMARK_LABEL))

    def __str__(self):
        return self._raw

    def __eq__(self, other):
        if isinstance(other, Token):
            return str(self) == str(other)

        return False


START_TOKEN = Token('start')
END_TOKEN = Token('end')


def can_parse_line(line: str) -> bool:
    """Returns whether a line matches the full legal line regex.

    Args:
        line: The string representing the line.
    Returns:
        Whether the line matches the full line regex.
    """
    return FULL_LINE_REGEX.match(line) is not None


def parse_line(line: str) -> Tuple[List['Token'], List[str], List[str]]:
    """Returns the tokens and remarks represented by a line.

    The list of Token objects will represent both the Move tokens and the
    Remark tokens referencing the remarks on that move or position. The index
    of each remark token will match the index of the remark in the respective
    list of position or move remarks.

    Args:
        line: The string representing the line.
    Returns:
        The list of Tokens, position remarks, and move remarks from the line.
    """
    if not can_parse_line(line):
        raise ValueError(f'Line "{line}" cannot be parsed')

    position_remarks = []
    move_remarks = []
    for match_remark in re.finditer(REMARK_PATTERN, line):
        remark_list = move_remarks
        prefix = 'm'
        if match_remark.group(PREFIX_LABEL) in POS_PREFIX:
            prefix = 'p'
            remark_list = position_remarks
        remark_index = len(remark_list)
        remark_list.append(match_remark.group(REMARK_LABEL))
        matched = match_remark.string[match_remark.start():match_remark.end()]
        line = line.replace(matched, f'{prefix}{remark_index}', 1)

    # Return all tokens, as well as the remarks lists.
    return list(map(Token, line.split())), position_remarks, move_remarks


def generate_positions(
        tokens: Iterable[Token], position_remarks: Iterable[str],
        move_remarks: Iterable[str],
        starting_position: Position) -> Generator[Position, None, None]:
    """Generates the Position objects based on a parsed line.

    Args:
        tokens: The list of tokens. All remark indicies must reference the
            position_remarks and move_remarks lists.
        position_remarks: The list of position remarks.
        move_remarks: The list of move remarks.
        starting_position: The Position object from which this line begins.
    Returns:
        A generator yielding each Position based on this line.
    """
    last_chess_token = START_TOKEN
    position = starting_position
    current_position_remarks = []
    current_move_remarks = []
    for token in tokens + [END_TOKEN]:
        remark_type = token.get_remark_type()
        if token is END_TOKEN or token.is_chess_move():
            if last_chess_token is not START_TOKEN:
                position = position.make_move(
                    last_chess_token.get_move(),
                    last_chess_token.get_evaluation(),
                    current_position_remarks, current_move_remarks)
                yield position
            if token is not END_TOKEN:
                current_position_remarks = []
                current_move_remarks = []
                last_chess_token = token
        elif remark_type is not None:
            if remark_type in POS_PREFIX:
                current_position_remarks.append(
                    position_remarks[token.get_remark_index()])
            elif remark_type in MOVE_PREFIX:
                current_move_remarks.append(
                    move_remarks[token.get_remark_index()])
            else:
                raise ValueError(
                    f'Invalid remark type {remark_type} in token {token}')
            pass
        else:
            raise ValueError(f'Invalid token {token}')


class Line:
    """A single line (no variation) of a chess opening.

    Parses the entire line, including commentary, and stores it as a list of
    list of Position objects (with Move objects as the edges). Each
    Position will have a Move link to each subsequent position.

    Attributes:
        initial_board: The chess.Board representing the initial position.
        line: The list of Position objects in the line.
    """

    def __init__(self,
                 line: str,
                 game: Game,
                 initial_board: Optional[chess.Board] = None) -> None:
        """Initializes the line

        Args:
            line: A string representing the opening line and commentary.
            game: The Game which the Line adds to.
            initial_board: The initial state of the chess board at the beginning
                of the line (defaults to the starting position).
        Raises:
            ValueError if the line cannot be completely parsed.
        """
        self._line_raw = line
        self.game = game
        if initial_board is None:
            initial_board = chess.Board()
        self._start = game.get_position(initial_board)
        self.line = [self._start]
        tokens, position_remarks, move_remarks = parse_line(self._line_raw)
        self.line.extend([
            position for position in generate_positions(
                tokens, position_remarks, move_remarks, self._start)
        ])
        self.moves = [str(token) for token in tokens if token.is_chess_move()]
