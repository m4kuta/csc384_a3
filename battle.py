import itertools
import sys


def readBoard(inputPath):
    board = Board()
    inputFile = open(inputPath)

    board.rowMaxes = [int(char) for char in inputFile.readline()[:-1]]
    board.colMaxes = [int(char) for char in inputFile.readline()[:-1]]
    board.ships = [int(char) for char in inputFile.readline()[:-1]]

    lines = inputFile.read().splitlines()
    for line in lines:
        board.squares.append(list(line))

    return board


class Board:
    rowMaxes = []
    colMaxes = []
    ships = []  # submarines, destroyers, cruisers, battleships
    squares = []

    n = 0
    N = 0
    variables = None
    domains = []
    assigned = []
    values = []
    rowRem = []
    colRem = []
    rowSum = []
    colSum = []

    # region HELPERS
    def print(self):
        for row in self.squares:
            string = ''
            for square in row:
                string += square + ' '
            print(string[:-1])
        print()

    def getIndexByVar(self, v):
        i = v // self.n
        j = v % self.n - 1
        return i, j

    def getVarByIndex(self, i, j):
        return i * self.n + j + 1

    # endregion HELPERS

    # region PREPROCESSING
    def defineVariables(self):
        self.n = len(self.squares)
        self.N = self.n ** 2
        self.variables = range(self.n ** 2)
        self.domains = [['S', 'W', 'L', 'R', 'T', 'B', 'M'] for v in self.variables]
        self.assigned = [False for v in self.variables]
        self.values = ['0' for v in self.variables]
        self.rowRem = list(self.rowMaxes)
        self.colRem = list(self.colMaxes)
        self.rowSum = [0] * self.n
        self.colSum = [0] * self.n

    # def rowColMaxPreprocess(self):
    #     for i in range(self.n):
    #         if self.rowMaxes[i] == 0:
    #             for j in range(self.n):
    #                 self.assignSquare(i, j, 'W')
    #         if self.colMaxes[i] == 0:
    #             for j in range(self.n):
    #                 self.assignSquare(j, i, 'W')

    def preprocess(self):
        for i, j in itertools.product(range(self.n), range(self.n)):
            square = self.squares[i][j]

            # water adj constraint
            if square != '0' and square != 'W':
                self.assignSquare(i, j, square)
                self.makeAdjWater(i, j, square)

            # row max piece constraint
            if self.rowMaxes[i] == 0 or (self.rowSum[i] == self.rowMaxes[i] and square == '0'):
                self.assignSquare(i, j, 'W')

            # col max piece constraint
            if self.colMaxes[j] == 0 or (self.colSum[j] == self.colMaxes[j] and square == '0'):
                self.assignSquare(i, j, 'W')

    # def preprocess2(self):
    #     for i in range(self.n):
    #         rowR = self.rowRem[i]
    #         if rowR == 0:
    #             for j in range(self.n):
    #                 square = self.squares[i][j]
    #                 if square == '0':
    #                     self.assignSquare(i, j, 'W')
    #
    #     for j in range(self.n):
    #         colR = self.colRem[j]
    #         if colR == 0:
    #             for i in range(self.n):
    #                 square = self.squares[i][j]
    #                 if square == '0':
    #                     self.assignSquare(i, j, 'W')
    # endregion PREPROCESSING

    # region ASSIGNMENT
    def assignSquare(self, i, j, piece):
        v = i * self.n + j
        self.domains[v] = [piece]
        self.assigned[v] = True
        self.values[v] = piece
        self.squares[i][j] = piece
        if piece != '0' and piece != 'W':
            self.rowRem[i] -= 1
            self.colRem[j] -= 1
            self.rowSum[i] += 1
            self.colSum[j] += 1

    def makeAdjWater(self, i, j, piece):
        # left
        if i > 0 and piece in ['S', 'L', 'T', 'B']:
            self.assignSquare(i - 1, j, 'W')

        # right
        if i < self.n - 1 and piece in ['S', 'R', 'T', 'B']:
            self.assignSquare(i + 1, j, 'W')

        # down
        if j > 0 and piece in ['S', 'L', 'R', 'B']:
            self.assignSquare(i, j - 1, 'W')

        # up
        if j < self.n - 1 and piece in ['S', 'L', 'R', 'T']:
            self.assignSquare(i, j + 1, 'W')

        # down-left
        if i > 0 and j > 0:
            self.assignSquare(i - 1, j - 1, 'W')

        # up-left
        if i > 0 and j < self.n - 1:
            self.assignSquare(i - 1, j + 1, 'W')

        # down-right
        if i < self.n - 1 and j > 0:
            self.assignSquare(i + 1, j - 1, 'W')

        # up-right
        if i < self.n - 1 and j < self.n - 1:
            self.assignSquare(i + 1, j + 1, 'W')
    # endregion ASSIGNMENT

    # region SELECTION
    def pickUnassignedVar(self):
        row, col = self.findMinRemaining()
        return row * self.n + col + 1

    def findMinRemaining(self):
        min = sys.maxsize
        minRow = -1
        minCol = -1

        for i in range(self.n):
            for j in range(self.n):
                rowRem = self.rowRem[i]
                colRem = self.colRem[j]
                if rowRem > 0 and colRem > 0:
                    rem = rowRem + colRem
                    if rem < min:
                        min = rem
                        minRow = i
                        minCol = j

        return minRow, minCol
    # endregion SELECTION

    # region CONSTRAINTS
    def rowConstraint(self, i):
        sum = 0
        for square in self.squares[i]:
            if square != '0' and square != 'W':
                sum += 1
        return sum <= self.rowMaxes[i]

    def colConstraint(self, j):
        sum = 0
        for i in range(self.n):
            square = self.squares[i][j]
            if square != '0' and square != 'W':
                sum += 1
        return sum <= self.colMaxes[j]

    def subConstraint(self):
        pass
    # endregion CONSTRAINTS


def solveCSP(board):
    if False not in board.assigned:
        return True

    v = board.pickUnassignedVar()
    board.assigned[v] = True

    ogPiece = board.values[v]
    for d in board.domains[v]:
        i = v // board.n
        j = v % board.n - 1
        board.assignSquare(i, j, d)
        satisfied = True

        for i in range(board.n):
            if not board.rowConstraint(i):
                satisfied = False
                break

        for j in range(board.n):
            if not board.colConstraint(j):
                satisfied = False
                break

        if satisfied:
            solveCSP(board)

        board.assignSquare(i, j, ogPiece)

    board.assigned[v] = False
    return False

# inputPath = sys.argv[1] # Input file
# outputPath = sys.argv[2] # Output file
