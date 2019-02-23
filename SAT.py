#File format version
#For reading Dimacs input from sudoku clauses and sudoku puzzle
import sys
import time
import random

class SolutionFound(Exception):
    pass

class NoSolutionFound(Exception):
    pass

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
    new_changes = {}

    id = 1
    #assigned_counter = 0
    #satisfied_counter = 0

    #TODO Check for tautology Once

    for clause in initial_clauses:

        #Found unit clause
        if len(clause) == 1:
            unit_clause = clause[0]
            if "-" == unit_clause[0]:
                unit_clause = unit_clause[1:]
                new_changes[unit_clause] = 0
                #assignments[unit_clause] = 0 #If negative like -112 then take 112 and say it is false with 0
            else:
                new_changes[unit_clause] = 1
                #assignments[unit_clause] = 1 # If positive literal, assign it a 1 for true
            #assigned_counter += 1
            #satisfied_counter += 1
            #order.append(unit_clause) Leave out if recursion
            continue

        clauses_dict[id] = clause #a clause has an ID, except for pure literal clauses that already have a forced move
        for literal in clause:
            #Both -111 and 111 can be in the literal dict. So no uniqueness, compared to assignment and new changes dictionairy, which only has 111 and then value 0 or 1
            if literal in literal_dict:
                id_list = literal_dict[literal]
                id_list.append(id)
            else: id_list = [id]
            literal_dict[literal] = id_list

        id += 1

    assignments["assign_counter"] = 0
    assignments["satis_counter"] = 0
    assignments["new_changes"] = new_changes
    #print(assigned_counter)
    #print(satisfied_counter)
    #print(order)

    return clauses_dict,literal_dict,assignments

def check_tautology(clauses_dict,literal_dict,assign_dict):

    tautology_clauses = []
    for id,clause in list(clauses_dict.items()):
        literals_seen = set()
        for literal in clause:
            if literal[0] == "-":
                opposite = literal[1:]
            else:
                opposite = "-" + literal

            if opposite in literals_seen:
                tautology_clauses.append(id)
                break
            literals_seen.add(literal)

    #Process the tautology
    for clause_id in tautology_clauses:
        clause = clauses_dict.get(clause_id, [])
        for literal_to_update in clause:  #
            if clause_id in literal_dict[literal_to_update]:
                literal_dict[literal_to_update].remove(clause_id)
        clauses_dict.pop(clause_id, None)  # or use function clauses_dict.pop(clause_id) if want to return default value
        assign_dict["satis_counter"] += 1

    return clauses_dict, literal_dict, assign_dict

def try_simplify(clauses_dict,literal_dict,assign_dict):

    easy_case = False
    #Check for pure literal and unit clause
    #Run through dictionaries of literal/variables, to see if there is a pure literal and to check for tautology.

    #Check for pure literal
    for literal in list(literal_dict.keys()):

        if literal[0] == "-":
            opposite = literal[1:]
            abs_literal = opposite
            value = 0
        else:
            opposite = "-" + literal
            abs_literal = literal
            value = 1

        opposite_value = literal_dict.get(opposite,None)
        if opposite_value == None:
            assign_dict["new_changes"][abs_literal] = value
            easy_case = True

    for clause_id, clause in list(clauses_dict.items()):
        if len(clause) == 1:
            easy_case = True

            unit_clause = clause[0]

            if "-" == unit_clause[0]:
                unit_clause = unit_clause[1:]
                assign_dict["new_changes"][unit_clause] = 0
                #assignments[unit_clause] = 0 #If negative like -112 then take 112 and say it is false with 0
            else:
                assign_dict["new_changes"][unit_clause] = 1

    return clauses_dict,literal_dict,assign_dict, easy_case


def check_status(clause_dict,assign_dict, n_clauses): #Check for set of clauses are satisfied  (or all values are assigned? maybe not)
    amount_satisfied_clauses = assign_dict["satis_counter"]

    if len(clause_dict) == 0 and amount_satisfied_clauses == n_clauses:
        raise SolutionFound() #To jump to the exception of what to do when solution is found in run_dp

    return


def check_clauses(literal,literal_value,pos_or_neg_claus_ids,pos_or_neg, clauses_dict,literal_dict,assign_dict,n_clauses):

    #Change in clause dict if value is true, delete the clause id
    #Change in clause dict if value is false, get the clause and remove the literal
    #TODO: Check if it is last literal in clause, if false, then failure
    #TODO: If second last and is false, then last one is forced move.

    print("Check clauses; Literal, value, pos or neg case ",literal,literal_value,pos_or_neg)

    check_value = 1 if pos_or_neg == 1 else 0
    failure_found = False

    #adjusted_clause_ids = list(pos_or_neg_claus_ids) #Or use pos__rneg_claus_ids[:] may be faster, but weird syntax, or [i for i in pos__rneg_claus_ids] list comprehension


    # If all test have passed, can assign the value and
    # Delete the list of clauses the literal contained and
    #assign_dict["assign_counter"] += 1
    #if pos_or_neg == 0:
    #    neg_literal = literal
    #    pos_literal = literal[1:]
    #else:
    #    neg_literal = "-" + literal
    #    pos_literal = literal
    #assign_dict[pos_literal] = literal_value
    #literal_dict.pop(pos_literal, None)
    #literal_dict.pop(neg_literal, None)

    for clause_id in pos_or_neg_claus_ids:
        # All clauses are immediately satisfied, so can be neglected
        if literal_value == check_value:  # pos_literal_value = 1 if value == 1 else 0
            #print("Clause satisfied:",clauses_dict[clause_id])
            #All these clauses are satisfied, so need to update each variable to not point to this clause ID and remove clause ID from
            clause = clauses_dict.get(clause_id,[])
            for literal_to_update in clause:  #
                if literal_to_update != literal and clause_id in literal_dict[literal_to_update]:
                    literal_dict[literal_to_update].remove(clause_id)
            clauses_dict.pop(clause_id,None)  # or use function clauses_dict.pop(clause_id) if want to return default value
            assign_dict["satis_counter"] += 1
        else:
            #Cases where the opposite version of literal is false
            #Check for cases when amount_literals is 1 or 2
            literals_in_clause = clauses_dict.get(clause_id,[])
            print("Literals in clause ",literals_in_clause)
            amount_literals = len(literals_in_clause)

            #This is last literal
            if amount_literals == 1:
                failure_found = True
                break

            if amount_literals == 2: #Forced move as then there will be an unit clause
                print("Literal to te removed: ", literal)
                print("Amount literals is 2")
                if literal in literals_in_clause:
                    literals_in_clause.remove(literal)
                clauses_dict[clause_id] = literals_in_clause  # Maybe redundant as the other is already a reference
                #Go in to recursion as it is a forced move
                #If want to avoid this if statement, dont store new changes inside it
                copy_assign_dict = {key:value_assign for (key, value_assign) in list(assign_dict.items()) if key != "new_changes"}
                new_literal = literals_in_clause[0]
                if "-" == new_literal[0]:
                    new_literal = new_literal[1:]
                    copy_assign_dict["new_changes"] = {new_literal: 0}
                else:
                    copy_assign_dict["new_changes"] = {new_literal: 1}

                clauses_dict, literal_dict, assign_dict,failure_found = process_assignments(clauses_dict, literal_dict, copy_assign_dict,n_clauses)
            elif amount_literals > 2:
                print("Literal to te removed: ", literal)
                print("Amount literals > 2")
                if literal in literals_in_clause:
                    literals_in_clause.remove(literal)
                clauses_dict[clause_id] = literals_in_clause  # Maybe redundant as the other is already a reference

    return clauses_dict, literal_dict, assign_dict, failure_found

def process_assignments(clauses_dict,literal_dict,assign_dict,n_clauses):

    failure_found = False

    #for literal,value in assign_dict.items():
    for literal, new_value in assign_dict["new_changes"].items():                #TODO: Check if list(assign_dict["new_changes"].items())may be faster

        neg_literal = "-" + literal
        pos_clauses_ids = literal_dict.get(literal,[])   #Literal from assignments and changes are literals without "-" sign and then value 0 or 1
        neg_clauses_ids = literal_dict.get(neg_literal,[]) #In case there it is pure literal, one of them lookups dont exist, thus return empty list
        print("Literal",literal)
        print("Value",new_value)

        #Check for contradiction in primary assigment dictioanry and new assignment dictionairy for that lteral.
        has_value = assign_dict.get(literal, None)

        if (has_value == 0 or has_value == 1) and has_value != new_value:
            failure_found = True
            break
        elif not has_value:
            #For clauses with positive version of literal
            clauses_dict, literal_dict, assign_dict, failure_found = check_clauses(literal,new_value,pos_clauses_ids,1,clauses_dict, literal_dict, assign_dict,n_clauses)

            if failure_found:
                print("Clause contradiction:", literal,value)
                break

            # For clauses with negative version of literal
            clauses_dict, literal_dict, assign_dict, failure_found = check_clauses(neg_literal,new_value, neg_clauses_ids, 0, clauses_dict, literal_dict, assign_dict,n_clauses)

            if failure_found:
                print("Clause contradiction:", literal,value)
                break

        #If all test have passed, can assign the value and
        #Delete the list of clauses the literal contained and
        assign_dict["assign_counter"] += 1  #Moved, as does not work for recursion here
        assign_dict[literal] = new_value
        literal_dict.pop(literal,None)
        literal_dict.pop(neg_literal,None)

    if not failure_found: #Check if all clauses have been satisfied, might not be the best spot.
        check_status(clauses_dict,assign_dict,n_clauses)

    return clauses_dict,literal_dict,assign_dict, failure_found

def dp_loop(clauses_dict,literal_dict,assign_dict,n_clauses):
    failure_found = False

    can_simplify = True

    while can_simplify:
        clauses_dict, literal_dict, assign_dict, can_simplify = try_simplify(clauses_dict,literal_dict,assign_dict)
        if can_simplify:
            new_clauses_dict, new_literal_dict, new_assign_dict, failure_found = process_assignments(clauses_dict, literal_dict, assign_dict, n_clauses)

    #Split
    literal = random.choice(list(literal_dict.keys()))
    assign_value = random.choice([0,1])

    #Make copy of dictionaries
    #Call dp_loop again? or use while loop again and then dp_loop



    return clauses_dict,literal_dict,assign_dict, failure_found

def run_dp(dimacs_file):

    solution = False
    try:
        n_variables, n_clauses, set_clauses = read_dimacs(dimacs_file) #Extract from dimalcs file
        clauses_dict, literal_dict, assign_dict = store_clauses(set_clauses)#,n_variables,n_clauses) #Store clauses in dictionaries and also find unit clauses assignments

        print(len(clauses_dict), len(literal_dict), len(assign_dict))
        new_clauses_dict, new_literal_dict, new_assign_dict,failure_found = process_assignments(clauses_dict,literal_dict,assign_dict,n_clauses) #Process the assignments that were found

        if failure_found:
            raise NoSolutionFound()

        print(len(new_clauses_dict), len(new_literal_dict), len(new_assign_dict), failure_found)
        print("Amount Variables and assigned ", n_variables, new_assign_dict["assign_counter"])
        print("Amount clauses and Satisfied clauses:", n_clauses, new_assign_dict["satis_counter"])

        #Check for tautology
        new_clauses_dict, new_literal_dict, new_assign_dict = check_tautology(new_clauses_dict,new_literal_dict,new_assign_dict)

        print(len(new_clauses_dict), len(new_literal_dict), len(new_assign_dict), failure_found)
        print("Amount Variables and assigned ", n_variables, new_assign_dict["assign_counter"])
        print("Amount clauses and Satisfied clauses:", n_clauses, new_assign_dict["satis_counter"])

        #Start searching after initialization of storing clauses, propagating unit clauses and check for tautology
        new_clauses_dict, new_literal_dict, new_assign_dict, failure_found = dp_loop(new_clauses_dict,new_literal_dict,new_assign_dict,n_clauses)


    except SolutionFound:
        print("A solution has been found")
        solution = True
    except NoSolutionFound:
        print("Early contradiction found, no solution")
    finally:
        print(len(new_clauses_dict),len(new_literal_dict),len(new_assign_dict),failure_found)
        print("Amount Variables and assigned ",n_variables,new_assign_dict["assign_counter"])
        print("Amount clauses and Satisfied clauses:", n_clauses, new_assign_dict["satis_counter"])
        l = [int(k) for (k,v) in new_assign_dict.items() if v == 1]
        l.sort()
        print(l)
        #new_assign_dict["new_changes"] = {"112":0}
        #new_clauses_dict, new_literal_dict, new_assign_dict, failure_found = process_assignments( new_clauses_dict, new_literal_dict, new_assign_dict)
        #print(len(new_clauses_dict), len(new_literal_dict), len(new_assign_dict), failure_found)


    return new_assign_dict,solution

if __name__ == "__main__":
    if len(sys.argv) == 1:
        t1 = time.time()

        file = open("./input_file.cnf","r") #For testing
        assignments, solution = run_dp(file)#For testing
        #for i in range(30000000): 30 million actions to take around 1 second?
        #    i = 0
        if solution:
            l = [int(k) for (k, v) in assignments.items() if v == 1]
            l.sort()
            print(l)
            #file = open("./output_file.cnf", "w")
            #for assign in l:
            #    file.write(str(assign) + " " + "\n"
        else:
            print("There was no solution")
            #open("./output_file.cnf", "w")
        t2 = time.time()
        print("Runtime: " + str((t2 - t1)))#* 1000))

        print("Error: No arguments were given")
        sys.exit(1)
    run_dp(sys.argv[2])