import sys

class Board:
    N = 0
    rowCounts = []
    colCounts = []
    ships = [] # submarines, destroyers, cruisers, battleships
    squares = []

    # numSubmarines = 0
    # numDestroyers = 0
    # numCruisers = 0
    # numBattleships = 0

    variables = None
    domains = []
    assigned = []
    values = []

    def rowConstraint(self, i):
        sum = 0
        for square in self.squares[i]:
            if square != '0' and square != 'W':
                sum += 1
        return sum <= self.rowCounts[i]

    def colConstraint(self, j):
        sum = 0
        for i in range(self.N):
            square = self.squares[i][j]
            if square != '0' and square != 'W':
                sum += 1
        return sum <= self.colCounts[j]

    def defineVariables(self):
        self.N = len(self.squares)
        self.variables = range(self.N ** 2)
        self.domains = [['S', 'W', 'L', 'R', 'T', 'B', 'M'] for v in self.variables]
        self.assigned = [False for v in self.variables]
        self.values = ['0' for v in self.variables]
        self.rowRemaining = list(self.rowCounts)
        self.colRemaining = list(self.colCounts)

    def preprocess(self):
        for i in range(self.N):
            for j in range(self.N):
                if self.rowCounts[i] == 0:
                    self.assignSquare(i, j, 'W')
                if self.colCounts[j] == 0:
                    self.assignSquare(i, j, 'W')
                elif self.squares[i][j] == 'S':
                    self.assignSquare(i, j, 'S')
                    self.makeAdjacentWater(i, j, 'S')

    def preprocess2(self):
        for i in range(self.N):
            rowR = self.rowRemaining[i]
            if rowR == 0:
                for j in range(self.N):
                    square = self.squares[i][j]
                    if square == '0':
                        self.assignSquare(i, j, 'W')

        for j in range(self.N):
            colR = self.colRemaining[j]
            if colR == 0:
                for i in range(self.N):
                    square = self.squares[i][j]
                    if square == '0':
                        self.assignSquare(i, j, 'W')


    def assignSquare(self, i, j, piece):
        v = i * self.N + j
        self.domains[v] = [piece]
        self.assigned[v] = True
        self.values[v] = piece
        self.squares[i][j] = piece
        if piece != '0' and piece != 'W':
            self.rowRemaining[i] -= 1
            self.colRemaining[j] -= 1

    def makeAdjacentWater(self, i, j, piece):
        # left
        if i > 0 and piece in ['S', 'L', 'T', 'B']:
            self.assignSquare(i - 1, j, 'W')

        # right
        if i < self.N - 1 and piece in ['S', 'R', 'T', 'B']:
            self.assignSquare(i + 1, j, 'W')

        # down
        if j > 0 and piece in ['S', 'L', 'R', 'B']:
            self.assignSquare(i, j - 1, 'W')

        # up
        if j < self.N - 1 and piece in ['S', 'L', 'R', 'T']:
            self.assignSquare(i, j + 1, 'W')

        # down-left
        if i > 0 and j > 0 :
            self.assignSquare(i - 1, j - 1, 'W')

        # up-left
        if i > 0 and j < self.N - 1:
            self.assignSquare(i - 1, j + 1, 'W')

        # down-right
        if i < self.N - 1 and j > 0:
            self.assignSquare(i + 1, j - 1, 'W')

        # up-right
        if i < self.N - 1 and j < self.N - 1:
            self.assignSquare(i + 1, j + 1, 'W')

    # def updateSquares(self):
    #     for i in range(self.N):
    #         for j in range(self.N):
    #             v = i * self.N + j
    #             self.squares[i][j] = self.values[v]

    def pickUnassignedVar(self):
        row, col = self.findMinRemaining()
        return row * self.N + col + 1

    def findMinRemaining(self):
        min = sys.maxsize
        minRow = -1
        minCol = -1

        for i in range(self.N):
            for j in range(self.N):
                rowRem = self.rowRemaining[i]
                colRem = self.colRemaining[j]
                if rowRem > 0 and colRem > 0:
                    rem = rowRem + colRem
                    if rem < min:
                        min = rem
                        minRow = i
                        minCol = j

        return minRow, minCol

    def print(self):
        for row in self.squares:
            string = ''
            for square in row:
                string += square + ' '
            print(string[:-1])

def solveCSP(board):
    if False not in board.assigned:
        return True

    v = board.pickUnassignedVar()
    board.assigned[v] = True

    ogPiece = board.values[v]
    for d in board.domains[v]:
        i = v // board.N
        j = v % board.N - 1
        board.assignSquare(i, j, d)
        satisfied = True

        for i in range(board.N):
            if not board.rowConstraint(i):
                satisfied = False
                break

        for j in range(board.N):
            if not board.colConstraint(j):
                satisfied = False
                break

        if satisfied:
            solveCSP(board)

        board.assignSquare(i, j, ogPiece)

    board.assigned[v] = False
    return False

def readInputFile():
    pass

def readBoard(inputPath):
    board = Board()
    inputFile = open(inputPath)

    board.rowCounts = [int(char) for char in inputFile.readline()[:-1]]
    board.colCounts = [int(char) for char in inputFile.readline()[:-1]]
    board.ships = [int(char) for char in inputFile.readline()[:-1]]

    lines = inputFile.read().splitlines()
    for line in lines:
        board.squares.append(list(line))

    return board

# inputPath = sys.argv[1] # Input file
# outputPath = sys.argv[2] # Output file

board = readBoard("battle_validate/input_easy1.txt")
board.defineVariables()
board.preprocess()
board.preprocess2()
print(board.findMinRemaining())
print(board)
solveCSP(board)
board.print()
