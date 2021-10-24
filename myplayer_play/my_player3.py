import random
import sys
from copy import deepcopy

from read import readInput
from write import writeOutput

from host import GO


class MyGO():
    def __init__(self):
        self.size = 5
        self.komi = 2.5
        self.move = 0
        self.max_move = 24
        self.dead = []

    def set_board(self, type, prev_board, board):
        # adapted from host.py
        for i in range(self.size):
            for j in range(self.size):
                if prev_board[i][j] == type and board[i][j] != type:
                    self.dead.append((i, j))

        # self.piece_type = piece_type
        self.prev_board = prev_board
        self.board = board

    def compare_board(self, board1, board2):
        for i in range(self.size):
            for j in range(self.size):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def copy_board(self):
        '''
        Copy the current board for potential testing.

        :param: None.
        :return: the copied board instance.
        '''
        return deepcopy(self)

    def detect_neighbor(self, i, j):
        '''
        Detect all the neighbors of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i - 1, j))
        if i < len(board) - 1: neighbors.append((i + 1, j))
        if j > 0: neighbors.append((i, j - 1))
        if j < len(board) - 1: neighbors.append((i, j + 1))
        return neighbors

    def detect_neighbor_ally(self, i, j, board):
        '''
        Detect the neighbor allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        # board = self.board
        neighbors = self.detect_neighbor(i, j)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j, board):
        '''
        Using DFS to search for all allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
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
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        # board = self.board

        ally_members = self.ally_dfs(i, j, board)
        if board[0][0] == 2 and board[1][0] == 1 and board[0][1] == 1:
            print(i, j)
            print(ally_members)
            go.visualize_board(board)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False

    def find_died_pieces(self, piece_type, board):
        '''
        Find the died stones that has no liberty in the board for a given piece type.

        :param piece_type: 1('X') or 2('O').
        :return: a list containing the dead pieces row and column(row, column).
        '''
        # board = self.board
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
        '''
        Remove the dead stones in the board.

        :param piece_type: 1('X') or 2('O').
        :return: locations of dead pieces.
        '''

        died_pieces = self.find_died_pieces(piece_type, board)
        if not died_pieces:
            return []
        print("died: ", died_pieces)
        for piece in died_pieces:
            board[piece[0]][piece[1]] = 0
        go.visualize_board(board)
        return died_pieces

    def remove_certain_pieces(self, positions, board):
        '''
        Remove the stones of certain locations.

        :param positions: a list containing the pieces to be removed row and column(row, column)
        :return: None.
        '''
        # board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        # self.update_board(board)

    def place_chess(self, i, j, piece_type):
        '''
        Place a chess stone in the board.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the placement is valid.
        '''

        board = self.board

        valid_place = self.valid_place_check(i, j, piece_type)
        if not valid_place:
            return False
        self.previous_board = deepcopy(board)
        board[i][j] = piece_type
        self.update_board(board)
        # Remove the following line for HW2 CS561 S2020
        # self.n_move += 1
        return True

    def place(self, i, j, piece_type, board):
        board = deepcopy(board)
        board[i][j] = piece_type
        self.remove_died_pieces(3 - piece_type, board)
        # if board[0][1] == 1 and board[1][0] == 1:
        #     print("place")
        #     go.visualize_board(board)
        return board

    def valid_place_check(self, i, j, piece_type, board):
        '''
        Check whether a placement is valid.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1(white piece) or 2(black piece).
        :param test_check: boolean if it's a test check.
        :return: boolean indicating whether the placement is valid.
        '''
        # board = self.board
        verbose = False
        # if test_check:
        #     verbose = False
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
        test_go = self.copy_board()
        test_board = test_go.board

        # Check if the place has liberty
        test_board[i][j] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(i, j, test_board):
            return True

        # If not, remove the died pieces of opponent and check again
        test_go.remove_died_pieces(3 - piece_type, board)
        if not test_go.find_liberty(i, j, test_board):
            if verbose:
                print('Invalid placement. No liberty found in this position.')
            return False

        # Check special case: repeat placement causing the repeat board state (KO rule)
        else:
            if self.died_pieces and self.compare_board(self.previous_board, test_go.board):
                if verbose:
                    print('Invalid placement. A repeat move not permitted by the KO rule.')
                return False
        return True

    def update_board(self, new_board):
        '''
        Update the board with new_board

        :param new_board: new board.
        :return: None.
        '''
        self.board = new_board

    def score(self, piece_type):
        '''
        Get score of a player by counting the number of stones.

        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the game should end.
        '''

        board = self.board
        cnt = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    cnt += 1
        return cnt

    def reward(self, piece_type, board):
        score = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    score += 1
                elif board[i][j] != 0:
                    score -= 1
        return score

    def visualize_board(self, board):
        # board = self.board

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
    def __init__(self, board, reward, type, step):
        self.board = board
        self.reward = reward
        self.parent = None
        self.step = step
        self.children = None
        self.type = type


class Minimax:
    def __init__(self, go, root):
        self.go = go
        self.root = root

    def run(self, depth, cur_node):
        # print("start: ", depth)
        type = cur_node.type
        board = cur_node.board
        go = self.go
        # find possible placements
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, type, board):
                    possible_placements.append((i, j))
        if not possible_placements:
            # print(possible_placements)
            return possible_placements
        # generate next possible states
        next_layer = []
        new_type = 3 - type
        for (i, j) in possible_placements:
            new_board = go.place(i, j, type, board)
            new_reward = go.reward(self.root.type, new_board)
            # if new_board[0][1] == 1 and new_board[1][0] == 1:
            #     print("run")
            #     go.visualize_board(new_board)
            #     print(new_reward)
            new_child = Node(new_board, new_reward, new_type, (i, j))
            new_child.parent = cur_node
            next_layer.append(new_child)
        # recursively apply until reaches maximum depth
        depth -= 1
        # print("end: ", depth)
        if depth > 0:
            for child in next_layer:
                child.children = self.run(depth, child)
        return next_layer

    def prune(self):
        return

    def update_reward(self, node):
        if node.children is None:
            return
        children = node.children
        for child in children:
            self.update_reward(child)
        if node.type != self.root.type:
            min_reward = 24
            for child in children:
                if child.reward < min_reward:
                    node.reward = child.reward
        else:
            max_reward = -24
            for child in children:
                if child.reward > max_reward:
                    node.reward = child.reward

    def select_path(self):
        for child in self.root.children:
            go.visualize_board(child.board)
            print(child.reward)
        next_node = random.choice(self.root.children)
        next_reward = -24
        for child in self.root.children:
            if child.reward > next_reward:
                next_node = child
                next_reward = child.reward
        print(next_node.step)
        return next_node.step


class MyPlayer:
    def __init__(self):
        self.type = 'random'

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, board):
                    possible_placements.append((i, j))
        if not possible_placements:
            return "Pass"

        root = Node(go.board, 0, piece_type, None)
        minimax = Minimax(go, root)
        root.children = minimax.run(3, minimax.root)
        minimax.update_reward(minimax.root)
        return minimax.select_path()


def readInput(n, path="init/input.txt"):
    with open(path, 'r') as f:
        lines = f.readlines()

        piece_type = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n + 1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n + 1: 2 * n + 1]]

        return piece_type, previous_board, board


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = MyGO()
    go.set_board(piece_type, previous_board, board)
    player = MyPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)
