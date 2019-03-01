#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import preprocessing
import random
import SAT
import csv

#### Runtime toevoegen?


def experiment(number_of_sudokus, repetitions_per_sudoku, heuristic, output_file):
    with open(output_file + '.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        csvwriter.writerow(["Sudoku #", "Seed", "Number of splits", "Number of backtracks",
                                     "Number of negative assignments", "Number of positive assignments",
                                     "Number of clauses learned"])  
    
        file = open("./top95.sdk.txt", "r")
        puzzles, list_number_clauses = preprocessing.encode_dimacs(file)
        
        ## Loop over sudokus to be solved
        for i in range(number_of_sudokus):    
            puzzle = puzzles[i]
            number_clauses = list_number_clauses[i]
            preprocessing.write_puzzle(puzzle, number_clauses)
            
            ## Loop over number of seeds
            for j in range(repetitions_per_sudoku):
                random.seed(j+1)
                        
                ## Run the SAT solver on the sudoku
                file = open("./sudoku.cnf","r")
                solution = SAT.run_dp(file, heuristic)
                
                ## Write global variables 
                csvwriter.writerow([i, j, SAT.amount_of_splits, SAT.amount_of_backtracks,
                                     SAT.n_negative_assign, SAT.n_positive_assign,
                                     SAT.clauses_learned])       
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