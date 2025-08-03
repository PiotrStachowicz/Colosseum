# Piotr Stachowicz 337942
import sys
import math
import random

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


    def quick_copy(self) -> "Logic":
        new = self.__class__.__new__(self.__class__)
        new.board = [row.copy() for row in self.board]
        new.free_fields = set(self.free_fields)
        new.move_list = list(self.move_list)
        new.history = list(self.history)
        return new


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
        """Check if state is terminal"""
        if not self.free_fields:
            return True

        if len(self.move_list) < 2:
            return False

        return self.move_list[-1] is None and self.move_list[-2] is None

class Node:
    def __init__(self, state: Logic, player: int, parent=None):
        """Node constructor"""
        self.state = state
        self.player = player
        self.parent = parent
        self.visits = 0
        self.wins = 0
        self.moves = self.init_moves()
        self.children = {}

    def init_moves(self):
        """Initiate untried states"""
        return self.state.moves(self.player)

    def expand(self):
        """Expand the node"""
        not_touched = [move for move in self.moves if move not in self.children]

        if not not_touched:
            return None

        move: Logic = random.choice(not_touched)

        new_state = self.state.quick_copy()
        new_state.do_move(move, self.player)

        child = Node(new_state, 1 - self.player, self)

        self.children[move] = child

        return child

    def is_expanded(self):
        """Check if node is fully expanded"""
        return len(self.children) == len(self.moves)

    def uct_score(self, c=1.414):
        """UCT SCORE"""
        if self.visits == 0:
            return float('inf')

        return self.wins / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)


    def best_child(self, c=1.414):
        """Pick best child"""
        _, best_node = max(self.children.items(), key=lambda item: item[1].uct_score(c))
        return best_node

class MCTS:
    @staticmethod
    def run(root: Node, rounds=1000):
        """Run MCTS rounds"""
        for _ in range(rounds):
            node = root

            # Selection phase
            while node.is_expanded() and node.children:
                node = node.best_child()

            # Expansion phase
            if not node.state.terminal():
                node = node.expand() or node

            # Simulation phase
            rollout_state: Logic = node.state.quick_copy()
            player = node.player

            while not rollout_state.terminal():
                moves = rollout_state.moves(player)

                if moves:
                    move = random.choice(moves)
                else:
                    move = None

                rollout_state.do_move(move, player)
                player = 1 - player

            res = rollout_state.result()

            is_win = (root.player == 1 and res > 0) or (root.player == 0 and res < 0)

            # Backpropagation phase
            while node:
                node.visits += 1

                if is_win:
                    node.wins += 1

                node = node.parent

        best_move, _ = max(root.children.items(), key=lambda item: item[1].visits)
        return best_move

    @staticmethod
    def best_move(state: Logic, player):
        """Pick best move for current state"""
        root = Node(state, player)

        return MCTS.run(root, 2000)

class ReversiMCTSAgent(object):
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

    def best_move(self):
        """Pick the best possible move"""
        return MCTS.best_move(self.game.quick_copy(), self.my_player)

    def loop(self):
        """Fight for life"""
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

            if moves:
                move = self.best_move()
                self.game.do_move(move, self.my_player)

            else:
                self.game.do_move(None, self.my_player)
                move = (-1, -1)

            self.publish('IDO %d %d' % move)
