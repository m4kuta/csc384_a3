import copy
import random
import time
import queue
import sys
import os

# Validation script for CSC384 A3 : battle.py
# Change input_easy1.txt, output_easy1.txt and solution_easy1.txt to run
#    other test inputs.

if __name__ == '__main__':
  # Invoke the shell command to test the checkers solver
  print("Input file: input_easy1.txt, output file: output_easy1.txt")
  os.system("python3 battle.py input_easy1.txt output_easy1.txt")

  output_read = open("output_easy1.txt", "r")
  solution_read = open("solution_easy1.txt", "r")

  output_lines = output_read.readlines()
  solution_lines = solution_read.readlines()
  passed = True

  for index in range(1, len(output_lines)):
    if output_lines[index].strip() != solution_lines[index].strip():
      print(f"Line {index + 1}: "
                             f"Expected <{output_lines[index].strip()}> "
                             f"Encountered <{solution_lines[index].strip()}>\n")
      passed = False
      break

  print("Battleship output matches solution file.")
