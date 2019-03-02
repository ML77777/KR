#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import preprocessing
import random
import SAT
import csv
import time

#### Runtime toevoegen?
def h_name(heuristic):
    if heuristic == 1:
        name = str(heuristic) + "_ Random"
    elif heuristic == 2:
        name = str(heuristic) + "_ JW one sided"
    elif heuristic == 3:
        name = str(heuristic) + "_ VSIDS"
    elif heuristic == 4:
        name = str(heuristic) + "_ JW two sided"
    elif heuristic == 5:
        name = str(heuristic) + "_ Our min len JW one sided"
    elif heuristic == 6:
        name = str(heuristic) + "_ Our min len JW two sided"
    elif heuristic == 7:
        name = str(heuristic) + "_ Our min len probabilistic JW one sided"
    elif heuristic == 8:
        name = str(heuristic) + "_ Our min len probabilistic JW two sided"
    else:
        name = str(heuristc) + "_Unknown heuristic number"
    return name

def experiment(number_of_sudokus, repetitions_per_sudoku, heuristic, output_file,sudoku_file):
    with open(output_file + '.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        csvwriter.writerow(["Heuristic","Sudoku #", "Seed","Solution Found", "Runtime","# Splits", "# Backtracks",
                                     "# Positive assignments", "# Negative assignments","Positive to negative assignments ratio",
                                     "# Clauses learned","# Clauses at start", "# Variables at start","# Initial filled",
                                    "# Clauses before loop ", "# Variables before loop", "# Variables assigned before loop"])
    
        file = open(sudoku_file, "r")
        puzzles, list_number_clauses = preprocessing.encode_dimacs(file)
        if number_of_sudokus == -1:
            number_of_sudokus = len(puzzles)

        ## Loop over sudokus to be solved
        for i in range(number_of_sudokus):    
            puzzle = puzzles[i]
            number_clauses = list_number_clauses[i]
            preprocessing.write_puzzle(puzzle, number_clauses)
            
            ## Loop over number of seeds
            for j in range(repetitions_per_sudoku):
                random.seed(j+1)

                t1 = time.time()
                ## Run the SAT solver on the sudoku
                file = open("./sudoku.cnf","r")
                solution = SAT.run_dp(file, heuristic)
                t2 = time.time()
                if solution:
                    solution_answer = "Yes"
                else: solution_answer = "No"

                heuristic_name = h_name(heuristic)
                ## Write global variables 
                csvwriter.writerow([heuristic_name,i+1, j+1,solution_answer,str((t2 - t1)), SAT.amount_of_splits, SAT.amount_of_backtracks,
                                    SAT.n_positive_assign, SAT.n_negative_assign, SAT.n_positive_assign/SAT.n_negative_assign,
                                     SAT.clauses_learned, SAT.original_info[0],SAT.original_info[1],SAT.original_info[2],
                                    SAT.info_before_loop[0],SAT.info_before_loop[1],SAT.info_before_loop[2]])
                ## Reset global variables
                reset_values()
            
            print(str(((i+1)*100)/number_of_sudokus) + '%')

            
def reset_values():
    SAT.n_positive_assign = 0
    SAT.n_negative_assign = 0
    SAT.amount_of_splits = 0
    SAT.amount_of_backtracks = 0 
    SAT.clauses_learned = 0
    SAT.final_assignment_dictionary = {}
    SAT.original_info = []
    SAT.info_before_loop = []
    
    return

if __name__ == "__main__":
    #sudoku_file = "./top95.sdk.txt"
    #sudoku_file = "./damnhard.sdk.txt"
    sudoku_file = "./top2365.sdk.txt"
    n_sudokus = -1 #-1 for max
    n_seeds = 5
    heuristic = 8
    output_file_name = "./Results/"+ "Results_" + sudoku_file[2:-8] + "_" + str(n_seeds) + "_h" + str(heuristic)
    experiment(n_sudokus,n_seeds,heuristic,output_file_name,sudoku_file)