from battle import *

# inputPath = "battle_validate/input_easy1.txt"
inputPath = "battle_validate/input_easy2.txt"

print('### readBoard ###')
board = readBoard(inputPath)
board.print()

print('### defineVariables ###')
board.defineVariables()
board.print()

print('### preprocess ###')
board.preprocess()
board.print()

print('### solveCSP ###')
# solveCSP(board)
board.print()
