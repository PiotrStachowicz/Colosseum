""" chess_random.py

Random chess agent.
"""
import random
import chess
from chess import polyglot
from backend.adapter import AgentAdapter, Player


class ChessRandomAgent(AgentAdapter):
    def __init__(self):
        """Agent constructor"""
        self.board: chess.Board = chess.Board()
        self.my_player: chess.Color = chess.WHITE
        self.reset()
        self.book_reader = polyglot.open_reader('../data/Cerebellum3Merge.bin')

    def play(self) -> bool:
        """Play random chess move"""
        move = random.choice(self.board.move_stack)
        self.board.push(move)

        return self.board.is_game_over()

    def register(self, uci: str) -> None:
        """Register user's move"""
        move = chess.Move.from_uci(uci)
        self.board.push(move)

    def reset(self, player: Player=Player.FIRST) -> None:
        """Reset the agent"""
        self.board = chess.Board()

        if player == Player.FIRST:
            self.my_player = chess.WHITE
        else:
            self.my_player = chess.BLACK
