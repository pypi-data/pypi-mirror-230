"""Displays the game graph.
"""

import graphviz

from linepost.position import Game


def visualize(game: Game, format: str = 'png') -> graphviz.Digraph:
    """Returns a graphviz graph of the game.

    Args:
        game: The game to render.
        format: The graph format.
    Returns:
        The rendered graph.
    """
    graphviz.set_jupyter_format(format)
    graph = graphviz.Digraph(name='test', graph_attr={'rankdir': 'LR'})
    positions = set()
    moves = set()

    for position in game.fens.values():
        graph.node(position.board.fen(),
                   label=str(position),
                   color="black" if position.white_to_move() else "gray")
        moves = moves.union(position.moves.values())

    for move in moves:
        label = str(move)
        if move.remarks:
            label = '\n'.join([label] + list(move.remarks))
        graph.edge(move.from_position.board.fen(),
                   move.to_position.board.fen(),
                   label=label)

    return graph
