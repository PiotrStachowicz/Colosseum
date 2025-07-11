""" agent_alfa_beta.py

This module implements the IoC agent with alfa-beta algorithm.

"""
from backend.agents.logic.logic_v0 import Logic
import chess


class Agent(object):
    def __init__(self) -> None:
        self.logic: Logic = Logic()

    def evaluate(self) -> float:
        pass

    def alfa_beta(
            self,
            depth: int,
            alfa: float,
            beta: float,
            is_maximizing: bool
    ) -> float:
        if depth == 0 or self.logic.end():
            return self.evaluate()

        if is_maximizing:
            best_score = -float('inf')

            for move in self.logic.get_moves():
                self.logic.execute_move(move)

                score = self.alfa_beta(depth - 1, alfa, beta, False)

                self.logic.undo_move()

                best_score = max(best_score, score)

                if alfa >= beta:
                    return best_score
        else:
            best_score = float('inf')

            for move in self.logic.get_moves():
                self.logic.execute_move(move)

                score = self.alfa_beta(depth - 1, alfa, beta, True)

                self.logic.undo_move()

                best_score = min(best_score, score)

                if alfa >= beta:
                    return best_score

        return best_score

    def play(self, depth: int) -> chess.Move:
        best_score = -float('inf')
        best_move = None

        for move in self.logic.get_moves():
            self.logic.execute_move(move)

            score = self.alfa_beta(depth - 1, -float('inf'), float('inf'), False)

            self.logic.undo_move()

            if score > best_score:
                best_score = score
                best_move = move

        return best_move
