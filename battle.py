import itertools
import sys


class Board:
    rowPieceCount = []
    colPieceCount = []
    ships = []  # submarines, destroyers, cruisers, battleships
    squares = []

    n = 0
    N = 0

    rowPieceRem = []
    colPieceRem = []
    rowPieceSum = []
    colPieceSum = []

    rowWaterSum = []
    colWaterSum = []

    sMax = 0
    lMax = 0
    rMax = 0
    tMax = 0
    bMax = 0
    mMax = 0

    sSum = 0
    lSum = 0
    rSum = 0
    tSum = 0
    bSum = 0
    mSum = 0

    variables = None
    domains = []
    values = []
    assigned = []


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
        if i > 0 and piece != 'B':
            self.assignSquare(i - 1, j, 'W')

        # down
        if i < self.n - 1 and piece != 'T':
            self.assignSquare(i + 1, j, 'W')

        # left
        if j > 0 and piece != 'R':
            self.assignSquare(i, j - 1, 'W')

        # right
        if j < self.n - 1 and piece != 'L':
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
    def checkConstraints(self):
        return self.rowConstraint() and self.colConstraint()

    def rowConstraint(self):
        for i in range(self.n):
            if self.rowPieceSum[i] + self.rowWaterSum[i] > self.n:
                return False
        return True

    def colConstraint(self):
        for j in range(self.n):
            if self.colPieceSum[j] + self.colWaterSum[j] > self.n:
                return False
        return True

    def subConstraint(self):
        pass
    # endregion CONSTRAINTS


def solveCSP(board):
    if False not in board.assigned:
        return True

    v = board.pickUnassignedVar()
    board.assigned[v] = True

    ogPiece = board.values[v]
    i, j = board.getIndexByVar(v)

    for d in board.domains[v]:
        board.assignSquare(i, j, d)
        constraintsSatisfied = True

        for i in range(board.n):
            if not board.rowConstraint(i):
                constraintsSatisfied = False
                break

        for j in range(board.n):
            if not board.colConstraint(j):
                constraintsSatisfied = False
                break

        if constraintsSatisfied:
            print('### STEP ###')
            board.print()
            solveCSP(board)

        # undo assignment
        board.assignSquare(i, j, ogPiece)

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
