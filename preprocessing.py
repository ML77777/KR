import sys
#!/usr/bin/env python3


#----------------------------------------------------------------------------------------------

'''
#String format version, so dont save sudoku puzzles to files
#For reading Dimacs input from sudoku clauses and sudoku puzzle
def read_dimacs2(dimacs_format):

    clauses = []

    #Check first two lines for the c and p lines if they are there
    full_text = dimacs_format.splitlines()

    for line in full_text[:2]:

        if not ("p" or "c") in line:
            clause = line.split()[:-1]
            clauses.append(clause)

    for line in full_text[2:]:
        clause = line.split()[:-1]
        clauses.append(clause)

        #print(list(map(int,clause)))   #In case to convert every element to actual integer

    return clauses
'''
#---------------------------------------------------------------------------------------


def encode_dimacs(sudoku_puzzles):

    puzzles = []
    amount_clauses = 0

    for puzzle in sudoku_puzzles: #Every puzzle is a line of 81 characters
        encoded_puzzle = ""
        row = 1
        column = 1
        for element in list(puzzle)[:-1]: #Dont include "\n"
            if element != ".":
                clause_line = str(row) + str(column) + element + " 0\n"
                amount_clauses += 1
                encoded_puzzle += clause_line
            if column < 9:  #Assuming the 81 characters are indicating from left to right going down each row
                column += 1
            else:
                row += 1
                column = 1
        puzzles.append(encoded_puzzle)
        break #Testing on 1 puzzle only now

    return puzzles,amount_clauses


if __name__ == "__main__":
    #sys.argv[]

    sudoku_rules = open("./sudoku-rules.txt","r")
    rules = sudoku_rules.readlines()
    n_clauses = 0
    variables = set()
    rule_clauses = ""
    for line in rules:
        if not ("p" and "c") in line:
            n_clauses += 1
            rule_clauses += line
            for literal in line.split()[:-1]:
                if literal not in variables:
                    variables.add(literal)

    #print(len(n_variables),n_clauses)

    if len(sys.argv) > 1:
        sudoku_puzzle = open("./" + sys.argv[1], "r")
    else:
        sudoku_puzzle = open("./top95.sdk.txt", "r")

    dimacs_puzzle,n2_clauses = encode_dimacs(sudoku_puzzle)
    total_clauses = n_clauses + n2_clauses

    input_file = open("./input_file.cnf","w")
    input_file.write("p cnf " + str(len(variables)) + " " + str(total_clauses) + "\n")
    input_file.write(rule_clauses)
    input_file.write(dimacs_puzzle[0])

    #rules_clauses = read_dimacs(sudoku_rules) #File format read version

    #sudoku_rules = open("./sudoku-rules.txt","r")
    #rules = sudoku_rules.read()
    #rules_clauses = read_dimacs2(rules) #String read version

    print(dimacs_puzzle[0]) #String version