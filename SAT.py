#File format version
#For reading Dimacs input from sudoku clauses and sudoku puzzle
import sys
import time

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
    clauses_dict = {}       #Can add extension to track which literals already are assigned or have a False value, or essentially which literal to check first
    literal_dict = {}
    assignments = {}

    id = 1
    #assignments["counter"] =  0
    assigned_counter = 0
    satisfied_counter = 0
    #assignments["order"] = []
    order = []

    #TODO Check for tautology Once

    for clause in initial_clauses:

        #Found unit clause
        if len(clause) == 1:
            unit_clause = clause[0]
            if "-" == unit_clause[0]:
                unit_clause = unit_clause[1:]
                assignments[unit_clause] = 0 #If negative like -112 then take 112 and say it is false with 0
            else:
                assignments[unit_clause] = 1 # If positive literal, assign it a 1 for true
            #assignments["counter"] += 1
            assigned_counter += 1
            satisfied_counter += 1
            #assignments["order"] = assignments["order"].append(clause)
            #order.append(unit_clause) Leave out if recursion
            continue

        clauses_dict[id] = clause #A clause has an ID, except for pure literal clauses that already have a forced move
        for literal in clause:
            #Both -111 and 111 can be in the literal dict. So no uniqueness, like in assignment dictionairy
            if literal in literal_dict:
                id_list = literal_dict[literal]
                id_list.append(id)
            else: id_list = [id]
            literal_dict[literal] = id_list

        id += 1

    assignments["assign_count"] = assigned_counter
    assignments["satis_counter"] = satisfied_counter
    #assignments["order"] = order  Leaveo ut for recursion
    print(assigned_counter)
    print(satisfied_counter)
    #print(order)

    return clauses_dict,literal_dict,assignments

#def try_simplify(clauses_dict,literal_dict,assignments): #Check for tautology, pure literal and unit clause
    #Run through dictionaries of literal/variables, to see if there is a pure literal and to check for tautology.
    #Or to check for all three, just go over all clauses once and check with the dictionaries. Might be more logical

def check_clauses(literal_value,pos_or_neg_claus_ids,pos_or_neg, clauses_dict,literal_dict,assign_dict):

    check_value = 1 if pos_or_neg == 1 else 0
    failure_found = False

    for clause_id in pos_or_neg_claus_ids:

        # All clauses are immediately satisfied, so can be neglected
        if literal_value == check_value:  # pos_literal_value = 1 if value == 1 else 0
            print("Clause satisfied:",clauses_dict[clause_id])
            del clauses_dict[clause_id]  # use function clauses_dict.pop(clause_id)
            assign_dict["satis_counter"] += 1
        else:
            # Check if other literals have assignment, if so, this is the last literal that can make it true, so if it is false, it is a contradiction/failure.
            literals_in_clause = clauses_dict.get(clause_id,[])
            everthing_assigned = True
            for a_literal_in_clause in literals_in_clause:  # Can add extension as said in line 30 avoid looping over everything
                if not assign_dict.get(a_literal_in_clause, False):
                    everthing_assigned = False
                    break

            if everthing_assigned:
                failure_found = True
                print("Clause contradiction:", literals_in_clause)

    return clauses_dict, literal_dict, assign_dict, failure_found

def process_assignments(clauses_dict,literal_dict,assign_dict):

    failure_found = False

    for literal,value in assign_dict.items():
        if literal == "assign_counter" or "satis_counter":
            continue

        neg_literal = "-" + literal
        pos_clauses_ids = literal_dict.get(literal,[])   #Literal from assignments are literals without "-" sign and then value
        neg_clauses_ids = literal_dict.get(neg_literal,[]) #In case there it is pure literal, one of them lookups dont exist, thus return empty list
        print("Literal",literal)
        clauses_dict, literal_dict, assign_dict, failure_found = check_clauses(value,pos_clauses_ids,1,clauses_dict, literal_dict, assign_dict)

        if not failure_found:
            clauses_dict, literal_dict, assign_dict, failure_found = check_clauses(value, neg_clauses_ids, 0, clauses_dict, literal_dict, assign_dict)

        """
        for pos_clause_id in pos_clauses_ids:
            #All clauses are immediately satisfied, so can be neglected
            if value == 1:          #pos_literal_value = 1 if value == 1 else 0
                del clauses_dict[pos_clause_id] #use function clauses_dict.pop(clause_id)
                assign_dict["satis_counter"] += 1
            else:
                #Check if other literals have assignment, if so, this is the last literal that can make it true, so if it is false, it is a contradiction/failure.
                literals_in_clause = clauses_dict.get(pos_clause_id,[]]
                everthing_assigned = True
                for a_literal_in_clause in literals_in_clause:          #Can add extension as said in line 30 avoid looping over everything
                    if not assign_dict.get(a_literal_in_clause,False):
                        everthing_assigned = False
                        break

                if everthing_assigned:
                    return clauses_dict,literal_dict,assign_dict, True


        for neg_clause_id in neg_clauses_ids:
            #All clauses are immediately satisfied
            if value == 0:          #neg_literal_value = 1 if value == 0 else 0
                del clauses_dict[neg_clause_id]
                assign_dict["satis_counter"] += 1
            else:

                literals_in_clause = clauses_dict.get(neg_clause_id,[]]
                everthing_assigned = True
                for a_literal_in_clause in literals_in_clause:
                    if not assign_dict.get(a_literal_in_clause,False):
                        everthing_assigned = False
                        break

                if everthing_assigned:
                    return clauses_dict,literal_dict,assign_dict, True}"""


    return clauses_dict,literal_dict,assign_dict, failure_found

def run_dp(dimacs_file):
    n_variables, n_clauses, set_clauses = read_dimacs(dimacs_file)
    clauses_dict, literal_dict, assign_dict = store_clauses(set_clauses)#,n_variables,n_clauses) #Can check for unit clauses to prevent double checking

    print(len(clauses_dict), len(literal_dict), len(assign_dict))

    new_clauses_dict, new_literal_dict, new_assign_dict,failure_found = process_assignments(clauses_dict,literal_dict,assign_dict)

    print(len(new_clauses_dict),len(new_literal_dict),len(new_assign_dict),failure_found)
    #Algorithm loop starts here
    no_answer = True
    #while no_answer:
        #try_simplify(clauses_dict,literal_dict,assignments)
    return

if __name__ == "__main__":
    if len(sys.argv) == 1:
        t1 = time.time()

        file = open("./input_file.cnf","r") #For testing
        run_dp(file)#For testing
        #for i in range(30000000): 30 million actions to take around 1 second?
        #    i = 0

        t2 = time.time()
        print("Runtime: " + str((t2 - t1)))#* 1000))

        print("Error: No arguments were given")
        sys.exit(1)
    run_dp(sys.argv[2])