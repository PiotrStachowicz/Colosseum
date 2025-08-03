# Piotr Stachowicz 337942
import sys

from backend.adapter import AgentAdapter


class Logic:
    PIECE_VALUES = {
        0: 4,
        1: 1,
        2: 2,
        3: 3,
        4: 5,
        5: 7,
        6: 8,
        7: 10
    }

    MAXIMAL_PASSIVE = 30
    DENS_DIST = 0.1
    X = 7
    Y = 9
    traps = {(2, 0), (4, 0), (3, 1), (2, 8), (4, 8), (3, 7)}
    ponds = {(x, y) for x in [1, 2, 4, 5] for y in [3, 4, 5]}
    dens = [(3, 8), (3, 0)]
    dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]

    rat, cat, dog, wolf, jaguar, tiger, lion, elephant = range(8)

    def __init__(self):
        """Board constructor"""
        self.board = self.init_board()
        self.pieces = {0: {}, 1: {}}

        for y in range(Logic.Y):
            for x in range(Logic.X):
                C: tuple = self.board[y][x]

                if C:
                    pl, pc = C
                    self.pieces[pl][pc] = (x, y)

        self.turn = 0
        self.peace_counter = 0
        self.winner = None

    def quick_copy(self):
        new_game = self.__class__.__new__(self.__class__)
        new_game.board = [row[:] for row in self.board]

        new_game.pieces = {
            0: dict(self.pieces[0]),
            1: dict(self.pieces[1])
        }

        new_game.turn = self.turn
        new_game.peace_counter = self.peace_counter
        new_game.winner = self.winner

        return new_game

    @staticmethod
    def init_board():
        """Initiate board with defined state"""
        pieces = """
        L.....T
        .D...C.
        R.J.W.E
        .......
        .......
        .......
        e.w.j.r
        .c...d.
        t.....l
        """

        B = [x.strip() for x in pieces.split() if len(x) > 0]
        T = dict(zip('rcdwjtle', range(8)))

        res = []
        for y in range(9):
            raw = 7 * [None]

            for x in range(7):
                c = B[y][x]

                if c != '.':
                    if 'A' <= c <= 'Z':
                        owner = 1
                    else:
                        owner = 0

                    raw[x] = (owner, T[c.lower()])

            res.append(raw)

        return res

    @staticmethod
    def can_beat(p1, p2, pos1, pos2):
        """Check whether p1 can beat p2"""
        if pos1 in Logic.ponds and pos2 in Logic.ponds:
            return True  # rat vs rat

        if pos1 in Logic.ponds:
            return False  # rat in pond cannot beat any piece on land

        if p1 == Logic.rat and p2 == Logic.elephant:
            return True

        if p1 == Logic.elephant and p2 == Logic.rat:
            return False

        if p1 >= p2:
            return True

        if pos2 in Logic.traps:
            return True

        return False

    def check_winner(self):
        """Check who won"""
        for i in range(7, -1, -1):
            ps = []

            for p in [0, 1]:
                if i in self.pieces[p]:
                    ps.append(p)

            if len(ps) == 1:
                return ps[0]

        return None

    def rat_is_blocking(self, pos, dx, dy):
        """Check whether rat block that move"""
        x, y = pos
        nx = x + dx

        for player in [0, 1]:
            if Logic.rat not in self.pieces[1 - player]:
                continue

            rx, ry = self.pieces[1 - player][Logic.rat]

            if (rx, ry) not in self.ponds:
                continue

            if dy != 0:
                if x == rx:
                    return True

            if dx != 0:
                if y == ry and abs(x - rx) <= 2 and abs(nx - rx) <= 2:
                    return True

        return False

    def moves(self, player):
        """Return all possible moves"""
        res = []

        for p, pos in self.pieces[player].items():
            x, y = pos

            for (dx, dy) in Logic.dirs:
                pos2 = (nx, ny) = (x + dx, y + dy)

                if 0 <= nx < Logic.X and 0 <= ny < Logic.Y:
                    if Logic.dens[player] == pos2:
                        continue

                    if pos2 in self.ponds:
                        if p not in (Logic.rat, Logic.tiger, Logic.lion):
                            continue

                        if p == Logic.tiger or p == Logic.lion:
                            if dx != 0:
                                dx *= 3
                            if dy != 0:
                                dy *= 4
                            if self.rat_is_blocking(pos, dx, dy):
                                continue

                            pos2 = (nx, ny) = (x + dx, y + dy)

                    if self.board[ny][nx] is not None:
                        pl2, piece2 = self.board[ny][nx]

                        if pl2 == player:
                            continue
                        if not self.can_beat(p, piece2, pos, pos2):
                            continue

                    res.append((pos, pos2))
        return res

    def victory(self, player):
        """Check if given player won"""
        opponent = 1 - player

        if len(self.pieces[opponent]) == 0:
            self.winner = player
            return True

        x, y = self.dens[opponent]

        if self.board[y][x]:
            self.winner = player
            return True

        # Edge case for 'peace'
        if self.peace_counter >= Logic.MAXIMAL_PASSIVE:
            r = self.check_winner()

            if r is None:
                self.winner = 1  # draw is second player's victory
            else:
                self.winner = r
            return True

        return False

    def do_move(self, move):
        """Do the desired move"""
        self.turn = 1 - self.turn

        if move is None:
            return

        pos1, pos2 = move
        x, y = pos1
        pl, pc = self.board[y][x]

        x2, y2 = pos2
        if self.board[y2][x2]:  # piece taken!
            pl2, pc2 = self.board[y2][x2]
            del self.pieces[pl2][pc2]
            self.peace_counter = 0
        else:
            self.peace_counter += 1

        self.pieces[pl][pc] = (x2, y2)
        self.board[y2][x2] = (pl, pc)
        self.board[y][x] = None


class JungleRandomAgent(AgentAdapter):
    def __init__(self):
        """Agent constructor"""
        self.game: Logic = None
        self.my_player = None
        self.reset()

    def reset(self):
        """Reset agent state"""
        self.game = Logic()
        self.my_player = 1
        self.publish('RDY')

    @staticmethod
    def publish(what):
        """Publish message to opponent"""
        sys.stdout.write(what)
        sys.stdout.write('\n')
        sys.stdout.flush()

    @staticmethod
    def sniff():
        """Sniff message from opponent"""
        line = sys.stdin.readline().split()
        return line[0], line[1:]

    @staticmethod
    def copy_game(game) -> Logic:
        return game.quick_copy()

    def evaluate(self, game: Logic):
        """Heuristic evaluation function for Jungle game"""
        if game.winner == self.my_player:
            return float('inf')
        elif game.winner == 1 - self.my_player:
            return -float('inf')

        score = 0
        opponent = 1 - self.my_player

        opp_den = Logic.dens[opponent]

        # Material balance
        material = sum(Logic.PIECE_VALUES[pc] for pc in game.pieces[self.my_player])
        material -= sum(Logic.PIECE_VALUES[pc] for pc in game.pieces[opponent])
        score += material * 10

        # Distance to enemy den
        for _, (x, y) in game.pieces[self.my_player].items():
            distance = abs(x - opp_den[0]) + abs(y - opp_den[1])
            score += (14 - distance) * 3

        return score

    def minimax(self, game, depth, alfa, beta, is_maximizing):
        if depth == 0:
            return self.evaluate(game)

        if game.victory(self.my_player) or game.victory(1 - self.my_player):
            return self.evaluate(game)

        player = self.my_player if is_maximizing else 1 - self.my_player

        best_score = -float('inf') if is_maximizing else float('inf')

        moves = game.moves(player)

        if is_maximizing:
            for move in moves:
                game_copy = self.copy_game(game)
                game_copy.do_move(move)

                score = self.minimax(game_copy, depth - 1, alfa, beta, not is_maximizing)

                best_score = max(score, best_score)
                alfa = max(alfa, best_score)

                if beta <= alfa:
                    break
        else:
            for move in moves:
                game_copy = self.copy_game(game)
                game_copy.do_move(move)

                score = self.minimax(game_copy, depth - 1, alfa, beta, not is_maximizing)

                best_score = min(score, best_score)
                alfa = min(alfa, best_score)

                if beta <= alfa:
                    break

        return best_score

    def best_move(self):
        """Simulate and evaluate game for each move"""
        best_score = -float('inf')
        best_move = None

        moves = self.game.moves(self.my_player)

        for move in moves:
            game_copy = self.copy_game(self.game)

            game_copy.do_move(move)
            score = self.minimax(game_copy, 2, -float('inf'), float('inf'), False)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def loop(self):
        """Fight for life"""
        while True:
            cmd, args = self.sniff()
            if cmd == 'HEDID':
                move = tuple((int(m) for m in args[2:]))

                if move == (-1, -1, -1, -1):
                    move = None
                else:
                    xs, ys, xd, yd = move
                    move = ((xs, ys), (xd, yd))

                self.game.do_move(move)

            elif cmd == 'ONEMORE':
                self.reset()
                continue

            elif cmd == 'BYE':
                break

            else:
                assert cmd == 'UGO'
                self.my_player = 0

            move = self.best_move()

            if move:
                self.game.do_move(move)
                move = (move[0][0], move[0][1], move[1][0], move[1][1])
            else:
                self.game.do_move(None)
                move = (-1, -1, -1, -1)

            self.publish('IDO %d %d %d %d' % move)
