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

    def defineVariables(self):
        self.N = len(self.squares)
        self.variables = range(self.N ** 2)
        self.domains = [['0', 'S', 'W', 'L', 'R', 'T', 'B', 'M'] for v in self.variables]
        self.assigned = ['0' for v in self.variables]
        self.values = ['0' for v in self.variables]

    def preprocess(self):
        for i in range(self.N):
            for j in range(self.N):
                v = i * self.N + j
                if self.rowCounts[i] == 0 or self.colCounts[j] == 0:
                    self.domains[v] = ['W']
                    self.assigned[v] = True
                    self.values[v] = 'W'
                elif self.squares[i][j] != '0':
                    self.domains[v] = [self.squares[i][j]]
                    self.assigned[v] = True
                    self.values[v] = self.squares[i][j]

    def updateSquares(self):
        for i in range(self.N):
            for j in range(self.N):
                v = i * self.N + j
                self.squares[i][j] = self.values[v]


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
board.updateSquares()
print(board)
