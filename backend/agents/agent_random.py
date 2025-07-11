""" agent_alfa_beta.py

This module implements simplest (test) random agent.

"""
from backend.agents.logic.logic_v0 import Logic
import random
import chess


class Agent(object):
    def __init__(self, colour: chess.Color) -> None:
        """Initiate agent's parameters."""
        self.logic: Logic = Logic()
        self.my_color = colour

    def play(self, depth: int = 0) -> chess.Move:
        """Make random move"""
        return random.choice(self.logic.get_moves())
