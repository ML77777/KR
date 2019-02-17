#File format version
#For reading Dimacs input from sudoku clauses and sudoku puzzle
import sys

def read_dimacs(dimacs_file):

    clauses = []
    n_clauses = 0
    n_variables = 0

    #Check first two lines for the c and p lines if they are there
    lines = dimacs_file.readlines()
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
    clauses_dict = {} #dictionary with key = id and value = clause
    literal_dict = {} #dictionary with key = literal and value = list of clauses in which literal occurs
    id = 1

    assignments = {} #dictionary with key = literal and value = assigned truth value
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
                id_list.append(id)
            else: id_list = [id]
            literal_dict[literal] = id_list

        id += 1

    assignments["counter"] = counter
    assignments["order"] = order
    print(counter)
    print(order)

    return clauses_dict,literal_dict,assignments

def run_dp(dimacs_file):
    n_variables, n_clauses, set_clauses = read_dimacs(dimacs_file)
    clauses_dict, literal_dict, assignments = store_clauses(set_clauses)

    #Algorithm loop starts here
    clauses_dict, clauses_count, literal_dict, assignments, changed_literals = dp(clauses_dict, n_clauses, literal_dict, assignments)
    
    if clauses_count == 0:
        return True, assignments    
    else:
        return False, assignments
    

### TODO: Simplify and Split steps
def dp(clauses_dict, clauses_count, literal_dict, assignments, changed_literals, contradiction):
    new_changed_literals = []
    
    #Check contradictions and simplify
    for lit in changed_literals:
        relevant_clauses = literal_dict[lit]
        for clause in relevant_clauses:
            clause = clauses_dict[clause]
            
            count_false = 0
            for literal in clause:
                if "-" in literal: 
                    if assignments[literal[1:]] == 0:
                        clauses_count =- 1
                    elif assignments[literal[1:]] == 1:
                        count_false =+ 1
                        
                else:
                    if assignments[literal] == 1:
                        clauses_count =- 1
                    elif assignments[literal] == 0:
                        count_false =+ 1
            
            #check for contradiction
            if count_false == len(clause):
                return clauses_dict, clauses_count, literal_dict, assignments, [], True
        else:
            
    #Check stop condition
    if clauses_count == 0:
        return clauses_dict, clauses_count, literal_dict, assignments, [], False
    else:
    #Split
        #Choose literal from the not yet assigned literals:
            #assign literal true (or false)
            
            #Recursion
            clauses_dict1, clauses_count1, literal_dict1, assignments1, changed_literals1, contradition1 = dp(clauses_dict, clauses_count, literal_dict, assignments, new_changed_literals)
            if contradiction1 == True:
                #give the above literal the other truth value
                
                #Recursion
                clauses_dict1, clauses_count1, literal_dict1, assignments1, changed_literals1, contradition1 = dp(clauses_dict, clauses_count, literal_dict, assignments, new_changed_literals)
            
            if contradiction1 == True:
                return clauses_dict1, clauses_count1, literal_dict1, assignments1, changed_literals1, contradition1
            else:
                return clauses_dict1, clauses_count1, literal_dict1, assignments1, changed_literals1, contradition1
        

if __name__ == "__main__":
    if len(sys.argv) == 1:
        file = open("./input_file.cnf","r") #For testing
        run_dp(file)#For testing

        print("Error: No arguments were given")
        sys.exit(1)
    run_dp(sys.argv[2])
    
    
#######  Temporary testing function  #######
def test_dp():
    assignments = run_dp()
    
test_tp()
    