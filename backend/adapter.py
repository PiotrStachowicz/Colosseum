"""adapter.py

This module defines adapter abstract methods
that agents should provide.
"""
from enum import Enum
from abc import abstractmethod


class Player(Enum):
    """Enumeration for player differentiation"""
    FIRST = 0
    SECOND = 1


class AgentAdapter(object):
    @abstractmethod
    def play(self) -> bool:
        """Play computer's move"""
        pass

    @abstractmethod
    def register(self, move: str) -> None:
        """Register user's move"""
        pass

    @abstractmethod
    def reset(self, player: Player=Player.FIRST) -> None:
        """Reset agent"""
        pass
