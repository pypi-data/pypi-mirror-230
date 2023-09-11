"""Repertoire holds the game graph and all ingested lines.
"""

import re
from typing import Iterable, Optional, Tuple

import chess
import graphviz

from linepost.line import Line
from linepost.position import Game
from linepost.visual import visualize

START_POS_LABEL = 'start'
START_COLOR_LABEL = 'turn'
LINE_LABEL = 'line'
LINE_START_REGEX = re.compile(
    f'^(?:@(?P<{START_POS_LABEL}>[0-9]+)(?P<{START_COLOR_LABEL}>[wb]?)\\s+)?(?P<{LINE_LABEL}>.+)$'  # noqa: E501
)


def get_line_and_start(line: str) -> Tuple[str, int]:
    """Parses a line into the line text and its starting position.

    Lines beginning with @<number>[wb] will start from that move/turn in the
    previous line. For instance, @3b means begin with Black's 3rd move in the
    previous line, and @2w means begin with White's 2nd move in the previous
    line. If the number does not have b or w after it, it will be interprted as
    being White's move.

    Args:
        line: The raw line string.
    Returns:
        The line text and starting index.
    Raises:
        ValueError if the line does not match the parsing regex.
        TODO: The .+ actually matches invalid lines, but that will be caught
        later. Determine whether this is sufficient.
    """
    match = LINE_START_REGEX.match(line)
    if match is None:
        raise ValueError(f'Line {line} does not match the expected pattern.')
    start_position_value = match.group(START_POS_LABEL)
    start_index = 0
    if start_position_value:
        start_index = 2 * (int(start_position_value) - 1)
    if match.group(START_COLOR_LABEL) == 'b':
        start_index += 1

    return match.group(LINE_LABEL), start_index


class Repertoire:
    """The game graph and all lines which constructed it.

    Attributes:
        game: The Game graph.
        lines: All Line objects which constructed the game graph.
    """

    @classmethod
    def from_lines(cls,
                   line_source: Iterable[str],
                   skip_invalid: bool = False,
                   rep: Optional['Repertoire'] = None) -> 'Repertoire':
        """From a list of lines, create a repertoire.

        Optionally, add these lines to an existing repertoire.

        Args:
            line_source: A list of lines (e.g. from a file).
            skip_invalid: Whether to skip invalid lines.
            rep: The repertoire to add the lines to. Creates one if none provided.
        Returns:
            The repertoire with the provided lines.
        Raises:
            ValueError if adding an invalid line and skip_invalid is False.
        """
        if rep is None:
            rep = Repertoire()
        for line in line_source:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    line_text, index = get_line_and_start(line)
                    if len(rep.lines) > 0:
                        if index >= len(rep.lines[-1].line):
                            raise ValueError(
                                f'Index {index} does not exist in previous line'
                            )
                        rep.add_line(
                            f'{"".join(map(lambda s: f"{s} ", rep.lines[-1].moves[:index]))}{line_text}'
                        )
                    else:
                        if index > 0:
                            raise ValueError('No previous lines to reference')
                        rep.add_line(line_text)
                except ValueError as exc:
                    if not skip_invalid:
                        raise exc
        return rep

    @classmethod
    def from_file(cls,
                  filename: str,
                  skip_invalid: bool = False,
                  rep: Optional['Repertoire'] = None) -> 'Repertoire':
        """Create a repertoire from lines in a text file.

        Optionally, add these lines to an existing repertoire.

        Args:
            filename: The name of the file with the lines.
            skip_invalid: Whether to skip invalid lines.
            rep: The repertoire to add the lines to. Creates one if none provided.
        Returns:
            The repertoire with the provided lines.
        """
        with open(filename) as file:
            return Repertoire.from_lines(file.readlines(), skip_invalid)

    def __init__(self) -> None:
        self.game = Game()
        self.lines = []

    def add_line(self,
                 line: str,
                 initial_board: Optional[chess.Board] = None) -> None:
        """Ingests a line, adding new positions and moves to the Game graph.

        Does not mutate the game state if the line is invalid.

        Args:
            line: A string representing one line in the repertoire.
            initial_board: The initial state of the chess board at the beginning
                of the line (defaults to the starting position).
        """
        # Ingest the line into a new game first in case it fails.
        _ = Line(line, Game(), initial_board)

        self.lines.append(Line(line, self.game, initial_board))

    def visualize(self) -> graphviz.Digraph:
        """Returns a graphviz graph of the game.

        Returns:
            The rendered graph.
        """
        return visualize(self.game)
