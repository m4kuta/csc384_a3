import sys
from copy import deepcopy


class Board:
    def __init__(self, rowPieceCount, colPieceCount, ships, squares):
        self.rowPieceCount = rowPieceCount
        self.colPieceCount = colPieceCount
        self.shipCounts = ships  # submarines, destroyers, cruisers, battleships
        self.squares = squares

        self.n = len(self.squares)
        self.N = self.n ** 2

        self.domains = [[['W', 'S', 'L', 'R', 'T', 'B', 'M'] for j in range(self.n)] for i in range(self.n)]
        self.assigned = [[False for j in range(self.n)] for i in range(self.n)]

        self.rowPieceSum = [0 for i in range(self.n)]
        self.colPieceSum = [0 for j in range(self.n)]

        self.rowWaterSum = [0 for i in range(self.n)]
        self.colWaterSum = [0 for j in range(self.n)]

        self.pieceMax = {}
        for i in range(len(self.shipCounts)):
            if i == 3:
                pass
            else:
                num = 1 * self.shipCounts[i]

                if i == 0: # submarine
                    pieces = ['S']
                elif i == 1: # destroyers
                    pieces = ['L', 'R', 'T', 'B']
                else: # i == 2: # cruisers
                    pieces = ['L', 'R', 'T', 'B', 'M']

                for piece in pieces:
                    if piece in self.pieceMax:
                        self.pieceMax[piece] += num
                    else:
                        self.pieceMax[piece] = num

            if i == 3: # battleships
                num = 1 * self.shipCounts[i]

                for piece in ['L', 'R', 'T', 'B']:
                    if piece in self.pieceMax:
                        self.pieceMax[piece] += num
                    else:
                        self.pieceMax[piece] = num

                num = 2 * self.shipCounts[i]
                if 'M' in self.pieceMax:
                    self.pieceMax['M'] += num
                else:
                    self.pieceMax['M'] = num

        self.pieceSum = {}

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
        return i * self.n + j

    def getRowUnassigned(self, i):
        sum = 0
        for j in range(self.n):
            if not self.assigned[i][j]:
                sum += 1
        return sum

    def getColUnassigned(self, j):
        sum = 0
        for i in range(self.n):
            if not self.assigned[i][j]:
                sum += 1
        return sum
    # endregion HELPERS

    # region PREPROCESSING
    def preprocess(self):
        for i in range(self.n):
            for j in range(self.n):
                square = self.squares[i][j]

                # water adj constraint
                if square != '0' and square != 'W':
                    self.assignSquare(i, j, square, True)
                    self.makeAdjWater(i, j, square)

                # edge row/column piece constraints
                # corner
                if 'M' in self.domains[i][j] and \
                        ((i == 0 and j == 0) or (i == 0 and j == self.n - 1) or
                         (i == self.n - 1 and j == 0) or (i == self.n - 1 and j == self.n - 1)):
                    self.domains[i][j].remove('M')
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

        # TODO: combine this with above?
        # col max piece constraint
        for j in range(self.n):
            if self.colPieceCount[j] == 0 or self.colPieceSum[j] == self.colPieceCount[j]:
                for i in range(self.n):
                    if self.squares[i][j] == '0':
                        self.assignSquare(i, j, 'W')
    # endregion PREPROCESSING

    # region ASSIGNMENT
    def assignSquare(self, i, j, piece, isPreprocess = False):
        self.squares[i][j] = piece
        self.domains[i][j] = [piece]
        self.assigned[i][j] = True

        # TODO: move constraints out of assign
        # index constraints of given piece already handled by preprocessing
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

        if piece == 'W':
            self.rowWaterSum[i] += 1
            self.colWaterSum[j] += 1
        elif piece != '0':
            self.rowPieceSum[i] += 1
            self.colPieceSum[j] += 1

            if piece in self.pieceSum:
                self.pieceSum[piece] += 1
            else:
                self.pieceSum[piece] = 1

            if self.pieceSum[piece] > self.pieceMax[piece]:
                for i in range(self.n):
                    for j in range(self.n):
                        if piece in self.domains[i][j]:
                            self.domains[i][j].remove(piece)

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
    # endregion ASSIGNMENT

    # region SELECTION
    def pickUnassignedVar(self):
        # Baseline
        # for i in range(self.n):
        #     for j in range(self.n):
        #         if not self.assigned[i][j]:
        #             return v

        # MRV in domain
        # return self.findMinDomain()

        # Min unassigned row/col intersection
        return self.findMinUnassigned()

    def findMinDomain(self):
        min = sys.maxsize
        minI, minJ = -1, -1

        for i in range(self.n):
            for j in range(self.n):
                if self.assigned[i][j]:
                    continue

                size = len(self.domains[i][j])
                if size < min:
                    min = size
                    minI, minJ = i, j

        return minI, minJ

    def findMinUnassigned(self):
        # intersection of row and col with min total unassigned
        min = sys.maxsize
        minI = -1
        minJ = -1

        for i in range(self.n):
            for j in range(self.n):
                if self.assigned[i][j]:
                    continue

                rowRem = self.getRowUnassigned(i)
                colRem = self.getColUnassigned(j)
                if rowRem <= 0 or colRem <= 0:
                    continue

                rem = rowRem + colRem
                if rem < min:
                    min = rem
                    minI = i
                    minJ = j

        return minI, minJ
    # endregion SELECTION

    # region CONSTRAINTS
    def constraintsSatisfied(self):
        return self.rowConstraint() and self.colConstraint()

    def constraintsSatisfiedTight(self, i, j):
        return self.rowConstraintTight(i, j) and self.colConstraint()

    # def rowConstraint(self):
    #     for i in range(self.n):
    #         if self.rowPieceCount[i] + self.rowWaterSum[i] > self.n or \
    #                 self.rowPieceSum[i] > self.rowPieceCount[i]:
    #             return False
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

    def rowConstraintTight(self, i, j):
        for i in range(max(i - 1, 0), min(i + 2, self.n)):
            pieceSum = 0
            waterSum = 0

            for j in range(max(j - 1, 0), min(j + 2, self.n)):
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
    #                 self.colPieceSum[j] > self.colPieceCount[j]:
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

    def colConstraintTight(self, i, j):
        for j in range(max(j - 1, 0), min(j + 2, self.n)):
            pieceSum = 0
            waterSum = 0

            for i in range(max(i - 1, 0), min(i + 2, self.n)):
                square = self.squares[i][j]
                if square != '0' and square != 'W':
                    pieceSum += 1
                elif square == 'W':
                    waterSum += 1

            if self.colPieceCount[j] + waterSum > self.n or pieceSum > self.colPieceCount[j]:
                return False
        return True

    def gacEnforce(self):
        pass
    # endregion CONSTRAINTS

    def hasUnassignedVar(self):
        for i in range(self.n):
            for j in range(self.n):
                if not self.assigned[i][j]:
                    return True
        return False

def solveCSP(board):
    if not board.hasUnassignedVar():
        writeBoard(board, outputPath)
        exit()

    ogBoard = deepcopy(board)
    i, j = board.pickUnassignedVar()
    board.assigned[i][j] = True

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

    board.assigned[i][j] = False
    return False

# region I/O
outputPath = "output.txt"

def readBoard(inputPath):
    inputFile = open(inputPath)

    rowPieceCount = [int(char) for char in inputFile.readline()[:-1]]
    colPieceCount = [int(char) for char in inputFile.readline()[:-1]]
    ships = [int(char) for char in inputFile.readline()[:-1]]

    lines = inputFile.read().splitlines()
    squares = []
    for line in lines:
        squares.append(list(line))

    return Board(rowPieceCount, colPieceCount, ships, squares)

def writeBoard(board, outputPath):
    outputFile = open(outputPath, 'w')
    for row in board.squares:
        string = ''
        for square in row:
            string += square
        outputFile.write(string + '\n') # TODO remove final blank line
# endregion I/O

# inputPath = sys.argv[1] # Input file
# outputPath = sys.argv[2] # Output file
