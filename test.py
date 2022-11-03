from battle import *

# inputPath = "battle_validate/input_easy1.txt"
# inputPath = "battle_validate/input_easy2.txt"
# inputPath = "battle_validate/input_medium1.txt"
# inputPath = "battle_validate/input_medium2.txt"
inputPath = "battle_validate/input_hard1.txt"
# inputPath = "battle_validate/input_hard2.txt"

print('### readBoard ###')
board = readBoard(inputPath)
board.print()


print('### preprocess ###')
board.preprocess()
board.print()

print('### solveCSP ###')
solveCSP(board)

# print('### writeBoard ###')
# writeBoard(board, 'solution_test.txt')

# output_read = open(outputPath, "r")
# solution_read = open("solution" + inputPath[inputPath.find('_'):], "r")
#
# output_lines = output_read.readlines()
# solution_lines = solution_read.readlines()
# passed = True
#
# for index in range(1, len(output_lines)):
#     if output_lines[index].strip() != solution_lines[index].strip():
#         print(f"Line {index + 1}: "
#               f"Expected <{output_lines[index].strip()}> "
#               f"Encountered <{solution_lines[index].strip()}>\n")
#         passed = False
#         break
#
# if passed:
#     print("Battleship output matches solution file.")