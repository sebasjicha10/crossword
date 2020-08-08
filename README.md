# Crossword

## Built with Python - Constraint Satisfaction Problem
Program running: https://youtu.be/2QNXVw0nBwM

## How to run (example)

```
$ python generate.py data/structure1.txt data/words1.txt output.png
██████████████
███████M████R█
█INTELLIGENCE█
█N█████N████S█
█F██LOGIC███O█
█E█████M████L█
█R███SEARCH█V█
███████X████E█
██████████████

```

Given the structure of a crossword puzzle (i.e., which squares of the grid are meant to be filled in with a letter), and a list of words to use, the problem becomes one of choosing which words should go in each vertical or horizontal sequence of squares. 

This sort of problem can be modeled as a constraint satisfaction problem. 
Each sequence of squares is one variable, for which we need to decide on its value (which word in the domain of possible words will fill in that sequence). 

This program finds a satisfying assignment: a different word (from a given vocabulary list) for each variable such that all of the unary and binary constraints are met.

