import cProfile
import time
import os


class MyGO():
    def __init__(self, size):
        self.size = size
        self.komi = 2.5
        self.move = 0
        self.max_move = 24
        self.dead = []

    def set_board(self, type, prev_board, board):
        # Adapted from host.py
        for i in range(self.size):
            for j in range(self.size):
                if prev_board[i][j] == type and board[i][j] != type:
                    self.dead.append((i, j))

        self.prev_board = prev_board
        self.board = board

    def detect_neighbor(self, i, j, board):
        # Adapted from host.py
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i - 1, j))
        if i < len(board) - 1: neighbors.append((i + 1, j))
        if j > 0: neighbors.append((i, j - 1))
        if j < len(board) - 1: neighbors.append((i, j + 1))
        return neighbors

    def detect_neighbor_ally(self, i, j, board):
        # Adapted from host.py
        neighbors = self.detect_neighbor(i, j, board)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j, board):
        # Adapted from host.py
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1], board)
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j, board):
        # Adapted from host.py
        ally_members = self.ally_dfs(i, j, board)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1], board)
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:

                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False

    def find_liberties(self, i, j, board):
        # Adapted from host.py
        liberties = 0
        neighbors = self.detect_neighbor(i, j, board)
        for piece in neighbors:
            # If there is empty space around a piece, it has liberty
            if board[piece[0]][piece[1]] == 0:
                liberties += 1
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return liberties

    def find_died_pieces(self, piece_type, board):
        # Adapted from host.py
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                # Check if there is a piece at this position:
                if board[i][j] == piece_type:
                    # The piece die if it has no liberty
                    if not self.find_liberty(i, j, board):
                        died_pieces.append((i, j))
        return died_pieces

    def remove_died_pieces(self, piece_type, board):
        # Adapted from host.py
        died_pieces = self.find_died_pieces(piece_type, board)
        if not died_pieces:
            return []
        for piece in died_pieces:
            board[piece[0]][piece[1]] = 0
        return died_pieces

    def place(self, i, j, piece_type, board):
        board = list(map(list, board))
        board[i][j] = piece_type
        self.remove_died_pieces(3 - piece_type, board)
        return board

    def compare_board(self, board1, board2):
        # Adapted from host.py
        for i in range(self.size):
            for j in range(self.size):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def valid_place_check(self, i, j, piece_type, board):
        # Adapted from host.py
        verbose = False

        # Check if the place is in the board range
        if not (i >= 0 and i < len(board)):
            if verbose:
                print(('Invalid placement. row should be in the range 1 to {}.').format(len(board) - 1))
            return False
        if not (j >= 0 and j < len(board)):
            if verbose:
                print(('Invalid placement. column should be in the range 1 to {}.').format(len(board) - 1))
            return False

        # Check if the place already has a piece
        if board[i][j] != 0:
            if verbose:
                print('Invalid placement. There is already a chess in this position.')
            return False

        # Copy the board for testing
        test_board = list(map(list, board))

        # Check if the place has liberty
        test_board[i][j] = piece_type

        if self.find_liberty(i, j, test_board):
            return True

        # If not, remove the died pieces of opponent and check again
        self.remove_died_pieces(3 - piece_type, test_board)

        if not self.find_liberty(i, j, test_board):
            if verbose:
                print('Invalid placement. No liberty found in this position.')
            return False

        # Check special case: repeat placement causing the repeat board state (KO rule)
        else:
            if self.dead and self.compare_board(self.prev_board, test_board):
                if verbose:
                    print('Invalid placement. A repeat move not permitted by the KO rule.')
                return False
        return True

    def is_territory(self, piece_type, i, j, board):
        isEmpty = False
        up = False
        down = False
        left = False
        right = False
        if board[i][j] == 0: isEmpty = True
        if (i > 0 and board[i - 1][j] == piece_type) or i == 0:
            up = True
        if (i < len(board) - 1 and board[i + 1][j] == piece_type) or i == len(board) - 1:
            down = True
        if (j > 0 and board[i][j - 1] == piece_type) or j == 0:
            left = True
        if (j < len(board) - 1 and board[i][j + 1] == piece_type) or j == len(board) - 1:
            right = True
        return isEmpty and up and down and left and right

    def has_neighbour(self, i, j, type, board):
        empty = 0
        for x in range(self.size):
            for y in range(self.size):
                if board[x][y] == 0:
                    empty += 1
        # print(empty)
        if empty < 14 or empty == 25:
            return True
        neighbours = self.detect_neighbor(i, j, board)
        if i > 0 and j > 0:
            neighbours.append((i - 1, j - 1))
        if i > 0 and j < len(board) - 1:
            neighbours.append((i - 1, j + 1))
        if i < len(board) - 1 and j > 0:
            neighbours.append((i + 1, j - 1))
        if i < len(board) - 1 and j < len(board) - 1:
            neighbours.append((i + 1, j + 1))
        # print(i, j, neighbours)
        for n in neighbours:
            if board[n[0]][n[1]] == 3 - type:
                return True
        return False

    def reward(self, piece_type, board):
        score = 0
        if piece_type == 1:
            for i in range(self.size):
                for j in range(self.size):
                    if board[i][j] == piece_type:
                        score += 1
                    # if self.is_territory(piece_type, i, j, board):
                    #     score += 0.5
                    if board[i][j] == 3 - piece_type:
                        score -= 1
                    # if self.is_territory(3 - piece_type, i, j, board):
                    #     score -= 0.5
        if piece_type == 2:
            for i in range(self.size):
                for j in range(self.size):
                    if board[i][j] == piece_type:
                        score += 1
                        score += 0.1 * self.find_liberties(i, j, board)
                    if self.is_territory(piece_type, i, j, board):
                        score += 0.5

        # Implement Benson's unconditional live

        # print("Score:", score, "\n")
        # go.visualize_board(board)
        return score

    def visualize_board(self, board):
        print('-' * len(board) * 2)
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    print(' ', end=' ')
                elif board[i][j] == 1:
                    print('X', end=' ')
                else:
                    print('O', end=' ')
            print()
        print('-' * len(board) * 2)


class Node:
    def __init__(self, board, type, step, next_step=None):
        self.board = board
        self.type = type
        self.step = step
        self.next_step = next_step
        self.reward = -1000
        self.best_path = []


# class TranspositionTable:

class Minimax:
    def __init__(self, go, root, depth):
        self.go = go
        self.root = root
        self.best_move = []
        self.depth = depth

    def max_value(self, depth, cur_node, alpha, beta):
        type = cur_node.type
        board = cur_node.board
        go = self.go
        cur_node.reward = -1000
        if depth == 0:
            cur_node.reward = go.reward(self.root.type, cur_node.board)
            cur_node.best_path = [cur_node.step]
            return cur_node

        # find possible placements
        psb_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, type, board) and go.has_neighbour(i, j, type, board):
                    psb_placements.append((i, j))

        # print(go.valid_place_check(3, 1, 1, board))
        # print(psb_placements)
        if not psb_placements:
            cur_node.reward = go.reward(self.root.type, cur_node.board)
            cur_node.best_path = [cur_node.step]
            return cur_node
        depth -= 1
        new_type = 3 - type
        if len(self.best_move) > 0 and self.best_move[0] in psb_placements:
            psb_placements.insert(0, psb_placements.pop(psb_placements.index(self.best_move.pop(0))))
            # print(psb_placements, cur_node.step)
        for (i, j) in psb_placements:
            new_board = go.place(i, j, type, board)
            new_child = Node(new_board, new_type, (i, j))
            new_child = self.min_value(depth, new_child, alpha, beta)
            if new_child.reward > cur_node.reward:
                cur_node.reward = new_child.reward
                cur_node.next_step = new_child.step
                # print("max", depth)
                if depth + 1 == self.depth:
                    cur_node.best_path = new_child.best_path
                else:
                    cur_node.best_path = [cur_node.step] + new_child.best_path
                # print(cur_node.best_path)
            if new_child.reward >= beta:
                return cur_node
            if new_child.reward > alpha:
                alpha = new_child.reward
        return cur_node

    def min_value(self, depth, cur_node, alpha, beta):
        type = cur_node.type
        board = cur_node.board
        go = self.go
        cur_node.reward = 1000
        if depth == 0:
            cur_node.reward = go.reward(self.root.type, cur_node.board)
            cur_node.best_path = [cur_node.step]
            return cur_node

        # find possible placements
        psb_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, type, board) and go.has_neighbour(i, j, type, board):
                    psb_placements.append((i, j))
        if not psb_placements:
            cur_node.reward = go.reward(self.root.type, cur_node.board)
            cur_node.best_path = [cur_node.step]
            return cur_node

        depth -= 1
        new_type = 3 - type
        if len(self.best_move) > 0 and self.best_move[0] in psb_placements:
            psb_placements.insert(0, psb_placements.pop(psb_placements.index(self.best_move.pop(0))))
            # print(psb_placements, cur_node.step)
        for (i, j) in psb_placements:
            new_board = go.place(i, j, type, board)
            new_child = Node(new_board, new_type, (i, j))
            new_child = self.max_value(depth, new_child, alpha, beta)
            if new_child.reward < cur_node.reward:
                cur_node.reward = new_child.reward
                cur_node.next_step = new_child.step
                # print("min", depth)
                if depth + 1 == self.depth:
                    cur_node.best_path = new_child.best_path
                else:
                    cur_node.best_path = [cur_node.step] + new_child.best_path
                # print(cur_node.best_path)
            if new_child.reward <= alpha:
                return cur_node
            if new_child.reward < beta:
                beta = new_child.reward
        return cur_node

    def iterative_deepening(self, root):
        start_time = time.time()
        depth = self.depth
        for i in range(1, depth + 1):
            self.depth = i
            root = self.max_value(i, root, -1000, 1000)
            self.best_move = root.best_path
            # print("id", self.best_move)
            elapsed_time = time.time() - start_time
            if elapsed_time >= 2000:
                break
        return root


class MyPlayer:
    def __init__(self, depth):
        self.type = 'random'
        self.depth = depth

    def get_input(self, go, piece_type, board, moves):
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if board[i][j] == 0:
                    possible_placements.append((i, j))
        if len(possible_placements) == 25:
            return (2, 2)
        root = Node(go.board, piece_type, None)
        # go.visualize_board(root.board)
        if moves < self.depth:
            self.depth = moves
        minimax = Minimax(go, root, self.depth)
        root = minimax.iterative_deepening(root)
        print(root.next_step)
        go.visualize_board(root.board)
        if not root.next_step:
            return "PASS"
        return root.next_step


# Adapted from read.py
def readInput(n, path="input.txt"):
    with open(path, 'r') as f:
        lines = f.readlines()

        piece_type = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n + 1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n + 1: 2 * n + 1]]

        return piece_type, previous_board, board


# Adapted from write.py
def writeOutput(result, path="output.txt"):
    res = ""
    if result == "PASS":
        res = "PASS"
    else:
        res += str(result[0]) + ',' + str(result[1])

    with open(path, 'w') as f:
        f.write(res)


def readMoves(piece_type, path="moves.txt"):
    if not os.path.exists(path):
        moves = 25-piece_type
        with open(path, 'w') as f:
            f.write(str(moves - 2))
            return moves
    with open(path, 'r') as g:
        moves = int(g.read())
        g.close()
    with open(path, 'w') as h:
        h.write(str(moves - 2))
        if moves - 2 <= 0:
            h.close()
            os.remove(path)
        return moves


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    moves = readMoves(piece_type)
    print(moves)
    go = MyGO(N)
    go.set_board(piece_type, previous_board, board)
    player = MyPlayer(depth=6)
    # cProfile.run("player.get_input(go, piece_type, board)")
    action = player.get_input(go, piece_type, board, moves)
    writeOutput(action)
