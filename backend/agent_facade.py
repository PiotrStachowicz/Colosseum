""" agent_facade.py

REST API, which plays role of IoC communicator between
Chess agent and GUI application.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from backend.adapter import Player, AgentAdapter
from backend.agents.chess.chess_random import ChessRandomAgent
from backend.agents.jungle.jungle_random import JungleRandomAgent
from backend.agents.reversi.reversi_random import ReversiRandomAgent


class AgentFacade:
    def __init__(self):
        """Initiate facade for agents"""
        self.app = FastAPI()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.agent: AgentAdapter = AgentAdapter()

    def register_routes(self):
        """Register REST API routes"""
        @self.app.get("/chess/start/{player}")
        def chess_start(player: Player) -> Response:
            """Start the Chess agent"""
            self.agent = ChessRandomAgent()
            self.agent.reset(player)

            return Response(status_code=204)

        @self.app.get("/reversi/start/{player}")
        def reversi_start(player: Player) -> Response:
            """Start the Reversi agent"""
            self.agent = ReversiRandomAgent()
            self.agent.reset(player)

            return Response(status_code=204)

        @self.app.get("/jungle/start/{player}")
        def jungle_start(player: Player) -> Response:
            """Start the Jungle agent"""
            self.agent = JungleRandomAgent()
            self.agent.reset(player)

            return Response(status_code=204)

        @self.app.get("/register/{move}")
        def register(move: str) -> JSONResponse:
            """Register user's move"""
            response = self.agent.register(move)
            winner = "HUMAN" if response else None

            return JSONResponse({"end": response, "winner": winner})

        @self.app.get("/play")
        def play() -> JSONResponse:
            """Play agent's move"""
            response = self.agent.play()
            winner = "COMPUTER" if response else None

            return JSONResponse({"end": response, "winner": winner})

        @self.app.get("/reset/{player}")
        def reset(player: Player) -> Response:
            """Reset agent"""
            self.agent.reset(player)

            return Response(status_code=204)

# Expose REST API
facade = AgentFacade()
facade.register_routes()
app = facade.app
