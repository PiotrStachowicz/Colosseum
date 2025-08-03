# Piotr Stachowicz 337942
import sys

class Logic:
    def __init__(self):
        """Board constructor"""
        self.board = self.init_board()
        self.free_fields = set()
        self.move_list = []
        self.history = []

        for i in range(8):
            for j in range(8):
                if self.board[i][j] is None:
                    self.free_fields.add((j, i))

    @staticmethod
    def init_board():
        """Initiate board with defined state"""
        board = [[None] * 8 for _ in range(8)]

        board[3][3] = 1
        board[4][4] = 1
        board[3][4] = 0
        board[4][3] = 0

        return board

    def moves(self, turn):
        """Return all possible fields that can move"""
        directions = [
            (0, 1),
            (1, 0),
            (-1, 0),
            (0, -1),
            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1)
        ]

        res = []

        for (x, y) in self.free_fields:
            for direction in directions:
                if self.can_beat(x, y, direction, turn):
                    res.append((x, y))
                    break

        return res

    def can_beat(self, x, y, d, turn):
        """Return true if this move overthrows enemy's fields"""
        dx, dy = d

        x += dx
        y += dy

        cnt = 0

        while self.get(x, y) == 1 - turn:
            x += dx
            y += dy
            cnt += 1

        return cnt > 0 and self.get(x, y) == turn

    def get(self, x, y):
        """Return value of (x, y) tile"""
        if 0 <= x < 8 and 0 <= y < 8:
            return self.board[y][x]

        return None

    def do_move(self, move, turn):
        """Apply the move"""
        directions = [
            (0, 1),
            (1, 0),
            (-1, 0),
            (0, -1),
            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1)
        ]

        self.history.append([x[:] for x in self.board])
        self.move_list.append(move)

        if move is None:
            return

        x, y = move
        x0, y0 = move

        self.board[y][x] = turn
        self.free_fields -= {move}

        for dx, dy in directions:
            x, y = x0, y0

            to_beat = []

            x += dx
            y += dy

            while self.get(x, y) == 1 - turn:
                to_beat.append((x, y))
                x += dx
                y += dy

            if self.get(x, y) == turn:
                for (nx, ny) in to_beat:
                    self.board[ny][nx] = turn

    def undo_move(self):
        """Undo the move"""
        prev_board = self.history.pop()
        move = self.move_list.pop()

        if move is not None:
            self.free_fields.add(move)

        self.board = prev_board

    def result(self):
        """Check which site is winning"""
        res = 0

        for y in range(8):
            for x in range(8):
                b = self.board[y][x]

                if b == 0:
                    res -= 1
                elif b == 1:
                    res += 1

        return res

    def terminal(self):
        if not self.free_fields:
            return True

        if len(self.move_list) < 2:
            return False

        return self.move_list[-1] is None and self.move_list[-2] is None


class ReversiAlfaAgent(object):
    def __init__(self):
        """Reset agent"""
        self.game: Logic = None
        self.my_player = None
        self.reset()

    def reset(self):
        """Reset agent"""
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

    def evaluate(self):
        """
        Improved heuristic evaluation of the board.
        Combines positional weights, mobility, piece count, and corner strategy.
        """
        player = self.my_player
        opponent = 1 - player
        board = self.game.board

        if self.game.terminal():
            game_res = self.game.result()
            if player == 1:
                return game_res * 10000
            else:
                return -game_res * 10000

        CORNER_C_X = {
            (0, 0): {'C': [(0, 1), (1, 0)], 'X': [(1, 1)]},
            (0, 7): {'C': [(0, 6), (1, 7)], 'X': [(1, 6)]},
            (7, 0): {'C': [(6, 0), (7, 1)], 'X': [(6, 1)]},
            (7, 7): {'C': [(6, 7), (7, 6)], 'X': [(6, 6)]},
        }

        my_vul = enemy_vul = 0

        for r in range(8):
            for c in range(8):
                tile = board[r][c]

                if tile is None:
                    continue

                is_frontier = False

                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue

                        nr, nc = r + dr, c + dc

                        if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] is None:
                            is_frontier = True
                            break

                    if is_frontier:
                        break

                if tile == player:
                    if is_frontier:
                        my_vul += 1

                else:
                    if is_frontier:
                        enemy_vul += 1

        corner_related_score = 0

        for r_corn, c_corn in CORNER_C_X.keys():
            corner_owner = board[r_corn][c_corn]

            if corner_owner == player:
                corner_related_score += 50

            elif corner_owner == opponent:
                corner_related_score -= 50

            else:
                for c_sq_r, c_sq_c in CORNER_C_X[(r_corn, c_corn)]['C']:
                    if board[c_sq_r][c_sq_c] == player:
                        corner_related_score -= 35
                    elif board[c_sq_r][c_sq_c] == opponent:
                        corner_related_score += 35

                for x_sq_r, x_sq_c in CORNER_C_X[(r_corn, c_corn)]['X']:
                    if board[x_sq_r][x_sq_c] == player:
                        corner_related_score -= 45
                    elif board[x_sq_r][x_sq_c] == opponent:
                        corner_related_score += 45

        frontier_score = -8 * (my_vul - enemy_vul)

        final_score = (corner_related_score +
                       frontier_score)

        return final_score

    def minimax(self, depth, alfa, beta, is_maximizing):
        """Alfa beta pruning algorithm"""
        if depth == 0 or self.game.terminal():
            return self.evaluate()

        player = self.my_player if is_maximizing else 1 - self.my_player
        moves = self.game.moves(player)

        if not moves:
            self.game.do_move(None, player)
            if self.game.terminal():
                score = self.evaluate()
                self.game.undo_move()
                return score

            score = self.minimax(depth - 1, alfa, beta, not is_maximizing)
            self.game.undo_move()

            return score

        if is_maximizing:
            best_score = -float('inf')

            for move in moves:
                self.game.do_move(move, player)

                score = self.minimax(depth - 1, alfa, beta, not is_maximizing)

                self.game.undo_move()

                best_score = max(score, best_score)
                alfa = max(alfa, best_score)

                if beta <= alfa:
                    break

            return best_score

        else:
            worst_score = float('inf')

            for move in moves:
                self.game.do_move(move, player)

                score = self.minimax(depth - 1, alfa, beta, not is_maximizing)

                self.game.undo_move()

                worst_score = min(score, worst_score)
                beta = min(beta, worst_score)

                if beta <= alfa:
                    break

            return worst_score

    def best_move(self, moves):
        """Pick the best possible move"""
        best_score = -float('inf')
        best_move = None

        for move in moves:
            self.game.do_move(move, self.my_player)
            score = self.minimax(2, -float('inf'), float('inf'), False)
            self.game.undo_move()

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def loop(self):
        """Fight for life"""
        CORNERS = {(0, 0), (0, 7), (7, 0), (7, 7)}

        while True:
            cmd, args = self.sniff()
            if cmd == 'HEDID':
                move = tuple((int(m) for m in args[2:]))

                if move == (-1, -1):
                    move = None

                self.game.do_move(move, 1 - self.my_player)

            elif cmd == 'ONEMORE':
                self.reset()
                continue

            elif cmd == 'BYE':
                break

            else:
                assert cmd == 'UGO'
                # assert not self.game.move_list
                self.my_player = 0

            moves = self.game.moves(self.my_player)
            better_moves = list(set(moves) & CORNERS)

            if better_moves:
                move = self.best_move(better_moves)
                self.game.do_move(move, self.my_player)
            elif moves:
                move = self.best_move(moves)
                self.game.do_move(move, self.my_player)
            else:
                self.game.do_move(None, self.my_player)
                move = (-1, -1)

            self.publish('IDO %d %d' % move)
