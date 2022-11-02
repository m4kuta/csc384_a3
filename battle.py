import itertools
import sys
from copy import deepcopy


class Board:
    def __init__(self):
        self.rowPieceCount = []
        self.colPieceCount = []
        self.ships = []  # submarines, destroyers, cruisers, battleships
        self.squares = []

        self.n = 0
        self.N = 0

        self.rowPieceRem = []
        self.colPieceRem = []
        self.rowPieceSum = []
        self.colPieceSum = []

        self.rowWaterSum = []
        self.colWaterSum = []

        self.sMax = 0
        self.lMax = 0
        self.rMax = 0
        self.tMax = 0
        self.bMax = 0
        self.mMax = 0

        self.sSum = 0
        self.lSum = 0
        self.rSum = 0
        self.tSum = 0
        self.bSum = 0
        self.mSum = 0

        self.variables = None
        self.domains = []
        self.values = []
        self.assigned = []


    # region HELPERS
    def print(self):
        print('    ' + ' '.join(str(max) for max in self.colPieceCount))
        print()

        for i, row in enumerate(self.squares):
            string = str(self.rowPieceCount[i]) + '   '
            for square in row:
                string += square + ' '
            print(string[:-1])
        print()

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result

    def getIndexByVar(self, v):
        i = v // self.n
        j = v % self.n
        return i, j

    def getVarByIndex(self, i, j):
        return i * self.n + j + 1
    # endregion HELPERS

    # region PREPROCESSING
    def defineVariables(self):
        self.n = len(self.squares)
        self.N = self.n ** 2

        self.variables = range(self.N)
        self.domains = [['W', 'S', 'L', 'R', 'T', 'B', 'M']] * self.N
        self.assigned = [False] * self.N
        self.values = ['0'] * self.N

        self.rowPieceRem = list(self.rowPieceCount)
        self.colPieceRem = list(self.colPieceCount)
        self.rowPieceSum = [0] * self.n
        self.colPieceSum = [0] * self.n
        self.rowWaterSum = [0] * self.n
        self.colWaterSum = [0] * self.n

    def preprocess(self):
        # water adj constraint
        for i, j in itertools.product(range(self.n), range(self.n)):
            square = self.squares[i][j]

            if square != '0' and square != 'W':
                self.assignSquare(i, j, square)
                self.makeAdjWater(i, j, square)

        # row max piece constraint
        for i in range(self.n):
            if self.rowPieceCount[i] == 0 or self.rowPieceRem[i] == 0:
                for j in range(self.n):
                    if self.squares[i][j] == '0':
                        self.assignSquare(i, j, 'W')

        # col max piece constraint
        for j in range(self.n):
            if self.colPieceCount[j] == 0 or self.colPieceRem[j] == 0:
                for i in range(self.n):
                    if self.squares[i][j] == '0':
                        self.assignSquare(i, j, 'W')
    # endregion PREPROCESSING

    # region ASSIGNMENT
    def assignSquare(self, i, j, piece):
        # already assigned to that piece
        if self.squares[i][j] == piece:
            return

        v = i * self.n + j

        self.squares[i][j] = piece
        self.domains[v] = [piece]
        self.values[v] = piece
        self.assigned[v] = True

        if piece != '0' and piece != 'W':
            self.rowPieceRem[i] -= 1
            self.colPieceRem[j] -= 1
            self.rowPieceSum[i] += 1
            self.colPieceSum[j] += 1

        if piece == 'W':
            self.rowWaterSum[i] += 1
            self.colWaterSum[j] += 1
        elif piece == 'S':
            self.sSum += 1
        elif piece == 'L':
            self.lSum += 1
        elif piece == 'R':
            self.rSum += 1
        elif piece == 'T':
            self.tSum += 1
        elif piece == 'B':
            self.bSum += 1
        elif piece == 'M':
            self.mSum += 1

    def makeAdjWater(self, i, j, piece):
        # ['0', 'W', 'S', 'L', 'R', 'T', 'B', 'M']
        # row up: -1
        # row down: +1
        if piece == 'W' or piece == '0':
            return

        # up
        if i > 0 and piece != 'B' and piece != 'M':
            self.assignSquare(i - 1, j, 'W')

        # down
        if i < self.n - 1 and piece != 'T' and piece != 'M':
            self.assignSquare(i + 1, j, 'W')

        # left
        if j > 0 and piece != 'R' and piece != 'M':
            self.assignSquare(i, j - 1, 'W')

        # right
        if j < self.n - 1 and piece != 'L' and piece != 'M':
            self.assignSquare(i, j + 1, 'W')

        # up-left
        if i > 0 and j > 0:
            self.assignSquare(i - 1, j - 1, 'W')

        # up-right
        if i > 0 and j < self.n - 1:
            self.assignSquare(i - 1, j + 1, 'W')

        # down-left
        if i < self.n - 1 and j > 0:
            self.assignSquare(i + 1, j - 1, 'W')

        # down-right
        if i < self.n - 1 and j < self.n - 1:
            self.assignSquare(i + 1, j + 1, 'W')

    def testAssignSquare(self, i, j, piece):
        # already assigned to that piece
        if self.squares[i][j] == piece:
            return

        v = i * self.n + j

        self.squares[i][j] = piece

    def testMakeAdjWater(self, i, j, piece):
        # ['0', 'W', 'S', 'L', 'R', 'T', 'B', 'M']
        # row up: -1
        # row down: +1
        if piece == 'W' or piece == '0':
            return

        # up
        if i > 0 and piece != 'B' and piece != 'M':
            self.testAssignSquare(i - 1, j, 'W')

        # down
        if i < self.n - 1 and piece != 'T' and piece != 'M':
            self.testAssignSquare(i + 1, j, 'W')

        # left
        if j > 0 and piece != 'R' and piece != 'M':
            self.testAssignSquare(i, j - 1, 'W')

        # right
        if j < self.n - 1 and piece != 'L' and piece != 'M':
            self.testAssignSquare(i, j + 1, 'W')

        # up-left
        if i > 0 and j > 0:
            self.testAssignSquare(i - 1, j - 1, 'W')

        # up-right
        if i > 0 and j < self.n - 1:
            self.testAssignSquare(i - 1, j + 1, 'W')

        # down-left
        if i < self.n - 1 and j > 0:
            self.testAssignSquare(i + 1, j - 1, 'W')

        # down-right
        if i < self.n - 1 and j < self.n - 1:
            self.testAssignSquare(i + 1, j + 1, 'W')
    # endregion ASSIGNMENT

    # region SELECTION
    def pickUnassignedVar(self):
        # row, col = self.findMinRemaining()
        # return row * self.n + col + 1

        for v in range(self.N):
            if not self.assigned[v]:
                return v


    def findMinRemaining(self):
        min = sys.maxsize
        minRow = -1
        minCol = -1

        for i in range(self.n):
            for j in range(self.n):
                rowRem = self.rowPieceRem[i]
                colRem = self.colPieceRem[j]
                if rowRem > 0 and colRem > 0:
                    rem = rowRem + colRem
                    if rem < min:
                        min = rem
                        minRow = i
                        minCol = j

        return minRow, minCol
    # endregion SELECTION

    # region CONSTRAINTS
    def constraintsSatisfied(self):
        return self.rowConstraint() and self.colConstraint()

    # def rowConstraint(self):
    #     for i in range(self.n):
    #         if self.rowPieceCount[i] + self.rowWaterSum[i] > self.n or \
    #     #                 self.rowPieceSum > self.rowPieceCount:
    #     return True

    def rowConstraint(self):
        for i in range(self.n):
            pieceSum = 0
            waterSum = 0

            for j in range(self.n):
                square = self.squares[i][j]
                if square != '0' and square != 'W':
                    pieceSum += 1
                elif square == 'W':
                    waterSum += 1

            if self.rowPieceCount[i] + waterSum > self.n or pieceSum > self.rowPieceCount[i]:
                return False

        return True

    # def colConstraint(self):
    #     for j in range(self.n):
    #         if self.colPieceCount[j] + self.colWaterSum[j] > self.n or \
    #                 self.colPieceSum > self.colPieceCount:
    #             return False
    #     return True

    def colConstraint(self):
        for j in range(self.n):
            pieceSum = 0
            waterSum = 0

            for i in range(self.n):
                square = self.squares[i][j]
                if square != '0' and square != 'W':
                    pieceSum += 1
                elif square == 'W':
                    waterSum += 1

            if self.colPieceCount[j] + waterSum > self.n or pieceSum > self.colPieceCount[j]:
                return False
        return True

    def subConstraint(self):
        pass
    # endregion CONSTRAINTS


def solveCSP(board):
    if False not in board.assigned:
        return True

    ogSquares = deepcopy(list(board.squares))
    v = board.pickUnassignedVar()
    board.assigned[v] = True
    i, j = board.getIndexByVar(v)

    for d in board.domains[v]:
        board.testAssignSquare(i, j, d)
        board.testMakeAdjWater(i, j, d)
        # print('### STEP TEST ###')
        # board.print()
        constraintsSatisfied = True

        if not board.constraintsSatisfied():
            constraintsSatisfied = False

        if constraintsSatisfied:
            print('### STEP ###')
            board.assignSquare(i, j, d)
            board.makeAdjWater(i, j, d)
            board.print()
            solveCSP(board)

        # undo assignment
        board.squares = deepcopy(ogSquares)
        # print('### UNDO ###')
        # board.print()

    board.assigned[v] = False
    return False

def readBoard(inputPath):
    board = Board()
    inputFile = open(inputPath)

    board.rowPieceCount = [int(char) for char in inputFile.readline()[:-1]]
    board.colPieceCount = [int(char) for char in inputFile.readline()[:-1]]
    board.ships = [int(char) for char in inputFile.readline()[:-1]]

    lines = inputFile.read().splitlines()
    for line in lines:
        board.squares.append(list(line))

    return board


def writeBoard(board, outputPath):
    outputFile = open(outputPath, 'w')
    for row in board.squares:
        string = ''
        for square in row:
            string += square
        outputFile.write(string + '\n')

# inputPath = sys.argv[1] # Input file
# outputPath = sys.argv[2] # Output file
