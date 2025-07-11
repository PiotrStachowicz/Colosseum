""" agent_runner.py

REST API, which plays role of IoC communicator between
Chess agent and GUI application.
"""

import chess
from fastapi import FastAPI

app = FastAPI()

@app.get("/update/{move}")
def update(move: str) -> None:
    pass

@app.get("/play")
def play() -> None:
    pass

