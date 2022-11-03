from battle import *

# inputPath = "battle_validate/input_easy1.txt"
# inputPath = "battle_validate/input_easy2.txt"
# inputPath = "battle_validate/input_medium1.txt"
inputPath = "battle_validate/input_medium2.txt"
# inputPath = "battle_validate/input_hard1.txt"
# inputPath = "battle_validate/input_hard2.txt"

print('### readBoard & defineVariables ###')
board = readBoard(inputPath)
board.defineVariables()
board.print()


print('### preprocess ###')
board.preprocess()
board.print()

print('### solveCSP ###')
solveCSP(board)
board.print()

# print('### writeBoard ###')
# writeBoard(board, 'solution_test.txt')