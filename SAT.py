#File format version
#For reading Dimacs input from sudoku clauses and sudoku puzzle
import sys

def read_dimacs(dimacs_file):

    clauses = []
    n_clauses = 0
    n_variables = 0

    #Check first two lines for the c and p lines if they are there
    #lines = dimacs_file.readlines()
    for line in dimacs_file:

        if "p" in line:
            splitted_line = line.split()
            n_clauses = splitted_line[-1]
            n_variables = splitted_line[-2]
        elif not "c" in line:
            clause = line.split()[:-1]
            clauses.append(clause)

        #print(list(map(int,clause)))   #In case to convert every element to actual integer

    print(n_variables,n_clauses,clauses)
    return n_variables,n_clauses,clauses


def store_clauses(initial_clauses):#,n_variables,n_clauses):
    clauses_dict = {}
    literal_dict = {}
    id = 1

    assignments = {}
    #assignments["counter"] =  0
    counter = 0
    #assignments["order"] = []
    order = []

    for clause in initial_clauses:
        if len(clause) == 1: #Found unit clause
            unit_clause = clause[0]
            if "-" in unit_clause:
                unit_clause = unit_clause[1:]
                assignments[unit_clause] = 0 #If negative like -112 then take 112 and say it is false with 0
            else:
                assignments[unit_clause] = 1 # If positive literal, assign it a 1 for true
            #assignments["counter"] += 1
            counter += 1
            #assignments["order"] = assignments["order"].append(clause)
            order.append(unit_clause)
            continue

        clauses_dict[id] = clause #A clause has an ID, except for pure literal clauses that already have a forced move
        for literal in clause:

            if literal in literal_dict:
                id_list = literal_dict[literal]
                for index,list_id in enumerate(id_list):
                    if id > list_id:
                        id_list.insert(index+1,id)
                        break
            else: id_list = [id]
            literal_dict[literal] = id_list

        id += 1

    assignments["counter"] = counter
    assignments["order"] = order
    print(counter)
    print(order)

    return clauses_dict,literal_dict,assignments

#def try_simplify(clauses_dict,literal_dict,assignments): #Check for tautology, pure literal and unit clause
    #Run through dictionaries of literal/variables, to see if there is a pure literal and to check for tautology.
    #Or to check for all three, just go over all clauses once and check with the dictionaries. Might be more logical

def run_dp(dimacs_file):
    n_variables, n_clauses, set_clauses = read_dimacs(dimacs_file)
    clauses_dict, literal_dict, assignments = store_clauses(set_clauses)#,n_variables,n_clauses) #Can check for unit clauses to prevent double checking
    #process_assignments(clauses_dict,literal_dict,assignments)

    #Algorithm loop starts here
    no_answer = True
    while no_answer:
        #try_simplify(clauses_dict,literal_dict,assignments)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        file = open("./input_file.txt","r") #For testing
        run_dp(file)#For testing

        print("Error: No arguments were given")
        sys.exit(1)
    run_dp(sys.argv[2])