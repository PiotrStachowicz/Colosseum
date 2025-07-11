""" logic_v0.py

This module implements simplest board backend logic for agents.
"""
import chess


class Logic(object):
    def __init__(self) -> None:
        """Initiate chess board logic component."""
        self.board = chess.Board()

    def get_moves(self) -> list[chess.Move]:
        return list(self.board.generate_legal_moves())

    def end(self) -> bool:
        """Check if current game has ended."""
        return self.board.is_game_over()

    def execute_move(self, move: chess.Move) -> None:
        """Execute desired move on the board."""
        self.board.push(move)

    def undo_move(self) -> None:
        """Undo last move."""
        self.board.pop()
