""" chess_alfa_beta.py

This module implements the IoC agent with alfa-beta algorithm.

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

    def evaluate(self) -> int:
        """Evaluate the board using heuristic function"""
        board = self.board

        # 1. Material
        PIECE_WEIGHTS = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

        # 2. Position (centre is good)
        POSITION_SQUARES = [
            0, 0, 1, 2, 2, 1, 0, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            1, 3, 5, 6, 6, 5, 3, 1,
            2, 4, 6, 8, 8, 6, 4, 2,
            2, 4, 6, 8, 8, 6, 4, 2,
            1, 3, 5, 6, 6, 5, 3, 1,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 0, 1, 2, 2, 1, 0, 0
        ]

        material_white = 0
        material_black = 0
        pos_white = 0
        pos_black = 0

        for pos, piece in self.board.piece_map().items():
            value = PIECE_WEIGHTS[piece.piece_type]

            if piece.color == chess.WHITE:
                material_white += value
                pos_white += POSITION_SQUARES[pos]
            else:
                material_black += value
                pos_black += POSITION_SQUARES[pos]

        # 3. Mobility
        current_turn = board.turn
        board.turn = chess.WHITE

        mobility_white = len(list(board.legal_moves))

        board.turn = chess.BLACK
        mobility_black = len(list(board.legal_moves))

        board.turn = current_turn

        # 4. We do not like trains
        train_white = 0
        train_black = 0

        for file in range(8):
            white_pawns = 0
            black_pawns = 0
            for square in chess.SquareSet(chess.BB_FILES[file]):
                if board.piece_at(square) == chess.Piece(chess.PAWN, chess.WHITE):
                    white_pawns += 1
                else:
                    black_pawns += 1

            train_white += white_pawns - 1
            black_pawns += white_pawns - 1

        # 5. King safety
        white_king_safety = 0
        black_king_safety = 0
        pos = board.king(chess.WHITE)

        file = chess.square_file(pos)
        rank = chess.square_rank(pos)

        if file == 0 or file == 7 or rank == 0:
            white_king_safety += 1

        pos = board.king(chess.BLACK)

        file = chess.square_file(pos)
        rank = chess.square_rank(pos)

        if file == 0 or file == 7 or rank == 7:
            white_king_safety -= 1

        # + for white
        score = (
            1.0 * (material_white - material_black)
            + 0.5 * (mobility_white - mobility_black)
            + 2.0 * (train_white - train_black)
            + 0.25 * (white_king_safety - black_king_safety)
        )

        return score if self.my_player == chess.WHITE else -score

    def minimax(
            self,
            depth: int,
            alfa: float,
            beta: float,
    ) -> int:
        """Decide which state is the best"""
        outcome = self.board.outcome()

        if outcome is not None:
            if outcome.winner is None:
                return 0

            if outcome.winner == self.my_player:
                return 10000 - depth
            else:
                return depth - 10000

        if depth == 0:
            return self.evaluate()

        is_maximizing = self.board.turn == self.my_player
        moves = self.board.legal_moves

        if is_maximizing:
            best_score = -float('inf')

            for move in moves:
                self.board.push(move)

                score = self.minimax(depth - 1, alfa, beta)

                self.board.pop()

                best_score = max(score, best_score)
                alfa = max(best_score, alfa)

                if beta <= alfa:
                    break
        else:
            best_score = float('inf')

            for move in moves:
                self.board.push(move)

                score = self.minimax(depth - 1, alfa, beta)

                self.board.pop()

                best_score = min(score, best_score)
                beta = min(best_score, beta)

                if beta <= alfa:
                    break

        return best_score

    def best_move(self, depth: int):
        """Generate best move for current state"""
        best_score = -float('inf')
        best_move = None

        moves = self.board.legal_moves
        book_moves = list(self.book_reader.find_all(self.board))

        # Play book moves like a pro
        if book_moves:
            book_move_entry: chess.polyglot.Entry = random.choice(book_moves)
            book_move = book_move_entry.move
            return book_move

        for move in moves:
            self.board.push(move)

            score = self.minimax(depth, -float('inf'), float('inf'))

            self.board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def play(self) -> bool:
        """Play random chess move"""
        move = self.best_move(2)
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
