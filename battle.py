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
        return i * self.n + j

    def getRowUnassigned(self, i):
        sum = 0
        for v in range(i * self.n, i * self.n + self.n):
            if not self.assigned[v]:
                sum += 1
        return sum

    def getColUnassigned(self, j):
        sum = 0
        for v in range(j, self.n * self.n - 1 + j, self.n):
            if not self.assigned[v]:
                sum += 1
        return sum
    # endregion HELPERS

    # region PREPROCESSING
    def defineVariables(self):
        self.n = len(self.squares)
        self.N = self.n ** 2

        self.variables = range(self.N)
        self.domains = [[['W', 'S', 'L', 'R', 'T', 'B', 'M'] for j in range(self.n)] for i in range(self.n)]
        self.assigned = [False] * self.N
        self.values = ['0'] * self.N

        self.rowPieceRem = list(self.rowPieceCount)
        self.colPieceRem = list(self.colPieceCount)
        self.rowPieceSum = [0] * self.n
        self.colPieceSum = [0] * self.n
        self.rowWaterSum = [0] * self.n
        self.colWaterSum = [0] * self.n

    def preprocess(self):
        for i, j in itertools.product(range(self.n), range(self.n)):
            square = self.squares[i][j]

            # water adj constraint
            if square != '0' and square != 'W':
                self.assignSquare(i, j, square, True)
                self.makeAdjWater(i, j, square)

            # edge row/column piece constraints
            # top
            if i == 0 and 'B' in self.domains[i][j]:
                self.domains[i][j].remove('B')
            # bottom
            if i == self.n - 1 and 'T' in self.domains[i][j]:
                self.domains[i][j].remove('T')
            # left
            if j == 0 and 'R' in self.domains[i][j]:
                self.domains[i][j].remove('R')
            # right
            if j == self.n - 1 and 'L' in self.domains[i][j]:
                self.domains[i][j].remove('L')

        # row max piece constraint
        for i in range(self.n):
            if self.rowPieceCount[i] == 0 or self.rowPieceSum[i] == self.rowPieceCount[i]:
                for j in range(self.n):
                    if self.squares[i][j] == '0':
                        self.assignSquare(i, j, 'W')

        # col max piece constraint
        for j in range(self.n):
            if self.colPieceCount[j] == 0 or self.colPieceSum[j] == self.colPieceCount[j]:
                for i in range(self.n):
                    if self.squares[i][j] == '0':
                        self.assignSquare(i, j, 'W')
    # endregion PREPROCESSING

    # region ASSIGNMENT
    def assignSquare(self, i, j, piece, isPreprocess = False):
        updateSums = True
        # already assigned to that piece
        if self.squares[i][j] == piece and not isPreprocess:
            updateSums = False

        v = self.getVarByIndex(i, j)

        self.squares[i][j] = piece
        self.domains[i][j] = [piece]
        self.values[v] = piece
        self.assigned[v] = True

        # TODO: add index constraints? should already be handled by preprocessing
        if piece == 'L':
            domain = self.domains[i][j+1]
            domain = [d for d in domain if d not in ['W', 'S', 'L', 'T', 'B']]
        elif piece == 'R':
            domain = self.domains[i][j - 1]
            domain = [d for d in domain if d not in ['W', 'S', 'R', 'T', 'B']]
        elif piece == 'T':
            domain = self.domains[i + 1][j]
            domain = [d for d in domain if d not in ['W', 'S', 'L', 'R', 'T']]
        elif piece == 'B':
            domain = self.domains[i - 1][j]
            domain = [d for d in domain if d not in ['W', 'S', 'L', 'R', 'B']]
        elif piece == 'M':
            if i > 0:
                domain = self.domains[i - 1][j]
                domain = [d for d in domain if d not in ['S', 'L', 'R', 'B']]
            if i < self.n - 1:
                domain = self.domains[i + 1][j]
                domain = [d for d in domain if d not in ['S', 'L', 'R', 'T']]
            if j > 0:
                domain = self.domains[i][j - 1]
                domain = [d for d in domain if d not in ['S', 'R', 'T', 'B']]
            if j < self.n - 1:
                domain = self.domains[i][j + 1]
                domain = [d for d in domain if d not in ['S', 'L', 'T', 'B']]


        if not updateSums:
            return

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

        if self.rowPieceSum[i] == self.rowPieceCount:
            for j in range(self.n):
                self.assignSquare(i, j, 'W')

        if self.colPieceSum[i] == self.colPieceCount:
            for i in range(self.n):
                self.assignSquare(i, j, 'W')

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
        # Baseline
        # for v in range(self.N):
        #     if not self.assigned[v]:
        #         return v

        # Min unassigned row/col intersection
        return self.findMinUnassigned()

        # MRV in domain
        # return self.findMinDomain()

    def findMinDomain(self):
        min = sys.maxsize
        minI, minJ = -1, -1
        for i, j in itertools.product(range(self.n), range(self.n)):
            size = len(self.domains[i][j])
            if size < min and not self.assigned[self.getVarByIndex(i, j)]:
                min = size
                minI, minJ = i, j
        return self.getVarByIndex(minI, minJ)

    def findMinUnassigned(self):
        # intersection of row and col with min total unassigned
        min = sys.maxsize
        minV = -1 # will never return -1 as solveCSP returns if False not in board.assigned

        for i in range(self.n):
            for j in range(self.n):
                rowRem = self.getRowUnassigned(i)
                colRem = self.getColUnassigned(j)
                if rowRem > 0 and colRem > 0:
                    rem = rowRem + colRem
                    v = self.getVarByIndex(i, j)
                    if rem < min and not self.assigned[v]:
                        min = rem
                        minV = v

        return minV
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
        writeBoard(board, 'solution_test.txt')
        exit()

    ogBoard = deepcopy(board)
    v = board.pickUnassignedVar()
    board.assigned[v] = True
    i, j = board.getIndexByVar(v)

    for d in board.domains[i][j]:
        board.assignSquare(i, j, d)
        board.makeAdjWater(i, j, d)
        # print('### STEP TEST ###')
        # board.print()
        constraintsSatisfied = True

        if not board.constraintsSatisfied():
            constraintsSatisfied = False

        if constraintsSatisfied:
            print('### STEP ###')
            board.print()
            solveCSP(board)

        # undo assignment
        board = deepcopy(ogBoard)
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
#
# print('### readBoard ###')
# board = readBoard(inputPath)
# board.print()
#
# print('### defineVariables ###')
# board.defineVariables()
# board.print()
#
# print('### preprocess ###')
# board.preprocess()
# board.print()
#
# print('### solveCSP ###')
# solveCSP(board)
# board.print()