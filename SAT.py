import sys, time, random, numpy as np
from operator import itemgetter
from collections import Counter

class SolutionFound(Exception):
    pass

class NoSolutionFound(Exception):
    pass

final_assignment_dictionary = {}
amount_of_backtracks = 0
amount_of_splits = 0
n_positive_assign = 0
n_negative_assign = 0
#n_assignments_solution = 0
vsids_counter = Counter()
clauses_learned = 0
#amount_filled_in_neighboorhood = 0
original_info = [] #Number of clauses, number of variables (729, in literal dict is 1458 as with negation for 9x9 sudoku), initial_filled]
info_before_loop = []  #Number of clauses left, number of variables left in literal dict, amount_variables assigned
                    # number of variables left, so is 1458 - literal assigned or (amount_ variables assigned *2)
                    #amount variables assigned, is abs_literal = value, so also its negation is determined, so times 2 if count its negation.
total_runtime = 0

def read_dimacs(dimacs_file):

    clauses = []
    n_clauses = 0
    n_variables = 0

    #Check first two lines for the c and p lines if they are there
    for line in dimacs_file:

        if not (line.strip()[0] == "c" or line.strip()[0] == "%" or line.strip()[0] == "0" or line.strip() == "\n" or line.strip() == "0\n" or line.strip() == ""):
            if line.strip()[0] == "p":
                splitted_line = line.split()
                n_clauses = splitted_line[-1]
                n_variables = splitted_line[-2]
            else:
                clause = line.split()[:-1]
                clauses.append(clause)

    return n_variables,n_clauses,clauses


def try_simplify(clauses_dict,literal_dict,assign_dict):

    easy_case = False
    failure_found = False

    #Check for pure literal
    for literal in list(literal_dict.keys()):

        if literal[0] == "-":
            opposite = literal[1:]
            abs_literal = opposite
            value = 0
            global n_negative_assign
            n_negative_assign += 1
        else:
            opposite = "-" + literal
            abs_literal = literal
            value = 1
            global n_positive_assign
            n_positive_assign += 1

        opposite_value = literal_dict.get(opposite,None)
        if opposite_value is None:
            assign_dict["new_changes"][abs_literal] = value #Since it does not affect others, can directly assign to it
            easy_case = True

    #Check for unit clause, (also check for contradiction, otherwise infinite loop because of putting it into new changes)
    for clause_id, clause in list(clauses_dict.items()):
        if len(clause) == 1:
            #unit_clause = clause[0][1:] if "-" == clause[0][0] else clause [0]
            if "-" == clause[0][0]:
                unit_clause = clause[0][1:]
                new_value = 0  # If negative like -112 then take 112 and say it is false with 0
            else:
                unit_clause = clause[0]
                new_value = 1

            has_value = assign_dict.get(unit_clause, None)
            if has_value is not None and has_value != new_value:
                failure_found = True
                break
            elif not has_value:
                assign_dict["new_changes"][unit_clause] = new_value #If negative like -112 then take 112 and say it is false with 0
                easy_case = True

    return clauses_dict,literal_dict,assign_dict, easy_case,failure_found


def check_status(clause_dict,assign_dict, n_clauses): #Check for set of clauses are satisfied  (or all values are assigned? maybe not)

    if len(clause_dict) == 0: #and amount_satisfied_clauses == n_clauses:
        global final_assignment_dictionary
        final_assignment_dictionary = assign_dict
        raise SolutionFound() #To jump to the exception of what to do when solution is found in run_dp

    return


def check_clauses(literal,literal_value,pos_or_neg_claus_ids,pos_or_neg, clauses_dict,literal_dict,assign_dict,n_clauses,heuristic):

    #Change in clause dict if check value is true, delete the clause id as it is satisfied, and remove any reference to this id
    #Change in clause dict if check value is false, get each clause and remove the literal from it
    #Check if it is last literal in that clause, if so, then failure as it is an empty clause
    #If second last, then last one is forced move, can propagate immediately

    check_value = 1 if pos_or_neg == 1 else 0
    failure_found = False

    for clause_id in pos_or_neg_claus_ids:

        global clauses_learned
        clauses_learned += 1

        # All clauses are immediately satisfied, so can be neglected
        if literal_value == check_value:

            #All these clauses are satisfied, so need to update each literal of satisfied claues to not point to this clause ID and remove clause ID from clauses dict
            clause = clauses_dict.get(clause_id,[])
            for literal_to_update in clause:  #
                if literal_to_update != literal and literal_to_update in literal_dict: # and clause_id in literal_dict[literal_to_update]: TODO can enable this if get error
                    literal_dict[literal_to_update].remove(clause_id)
            if clauses_dict.pop(clause_id,None) is not None:
                assign_dict["satis_counter"] += 1

        else:
            #Cases where the opposite version of literal is false, check for cases when amount_literals is 1, 2 or more
            literals_in_clause = clauses_dict.get(clause_id,[])
            amount_literals = len(literals_in_clause)

            #This is last literal, so would result into a forced move that is a contradiction
            if amount_literals == 1:
                failure_found = True
                break

            if amount_literals == 2: #Forced move as then there will be an unit clause, but also need to check contradicion

                #print("Literal to te removed: ", literal)
                #if literal in literals_in_clause:  TODO can enable this if get error
                literals_in_clause.remove(literal)
                #clauses_dict[clause_id] = literals_in_clause  # Maybe redundant as the other is already a reference TODO can enable this if get error

                #Go in to recursion as it is a forced move
                #copy_assign_dict = assign_dict
                #copy_literal_dict = literal_dict
                #copy_clauses_dict = clauses_dict

                new_literal = literals_in_clause[0]
                if "-" == new_literal[0]:
                    new_literal = new_literal[1:]
                    assign_dict["new_changes"] = {new_literal: 0}
                    global n_negative_assign
                    n_negative_assign += 1
                    #copy_assign_dict["new_changes"] = {new_literal: 0}
                else:
                    assign_dict["new_changes"] = {new_literal: 1}
                    global n_positive_assign
                    n_positive_assign += 1
                    #copy_assign_dict["new_changes"] = {new_literal: 1}

                clauses_dict, literal_dict, assign_dict, failure_found = process_assignments(clauses_dict,literal_dict,assign_dict,n_clauses,heuristic)
                #clauses_dict, literal_dict, assign_dict,failure_found = process_assignments(copy_clauses_dict, copy_literal_dict, copy_assign_dict,n_clauses) TODO can enable this if get error
                if failure_found:
                    break

            elif amount_literals > 2:
                #if literal in literals_in_clause:TODO can enable this if get error
                literals_in_clause.remove(literal)
                #clauses_dict[clause_id] = literals_in_clause  # Maybe redundant as the other is already a reference TODO can enable this if get error

    return clauses_dict, literal_dict, assign_dict, failure_found

def process_assignments(clauses_dict,literal_dict,assign_dict,n_clauses,heuristic):

    failure_found = False

    #Turn to list to make it faster?
    for literal, new_value in list(assign_dict["new_changes"].items()):

        neg_literal = "-" + literal
        pos_clauses_ids = literal_dict.get(literal,[])   #Literal from assignments and changes are literals without "-" sign and then value 0 or 1
        neg_clauses_ids = literal_dict.get(neg_literal,[]) #In case there it is pure literal, one of them lookups dont exist, thus return empty list

        #Check for contradiction in primary assigment dictionary and new assignment dictionairy for that literal.
        has_value = assign_dict.get(literal, None)

        if has_value is not None and has_value is not new_value:
            failure_found = True
            break
        #elif not has_value:
        elif has_value is None:

            #Delete the list of clauses the literal contained and assign the value
            assign_dict["assign_counter"] += 1
            assign_dict[literal] = new_value
            literal_dict.pop(literal, None)
            literal_dict.pop(neg_literal, None)

            #For clauses with positive version of literal
            clauses_dict, literal_dict, assign_dict, failure_found = check_clauses(literal,new_value,pos_clauses_ids,1,clauses_dict, literal_dict, assign_dict,n_clauses,heuristic)

            if failure_found:
                #print("Clause contradiction:", literal,new_value)
                #print("punt 1 in process")
                break

            # For clauses with negative version of literal
            clauses_dict, literal_dict, assign_dict, failure_found = check_clauses(neg_literal,new_value, neg_clauses_ids, 0, clauses_dict, literal_dict, assign_dict,n_clauses,heuristic)

            if failure_found:
                #print("Clause contradiction:", literal,new_value)
                #print("punt 2 in process")
                break

    #Reset
    assign_dict["new_changes"].clear()

    return clauses_dict,literal_dict,assign_dict, failure_found

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
            #if clause_id in literal_dict[literal_to_update]:       TODO can enable this if get error
            literal_dict[literal_to_update].remove(clause_id)
        if clauses_dict.pop(clause_id, None) is not None:
            assign_dict["satis_counter"] += 1

    return clauses_dict, literal_dict, assign_dict

def store_clauses(initial_clauses):
    clauses_dict = {}
    literal_dict = {}
    assignments = {}
    new_changes = {}

    id = 1
    satisfied_counter = 0

    for clause in initial_clauses:

        #Found unit clause
        if len(clause) == 1:
            unit_clause = clause[0]
            if "-" == unit_clause[0]:
                unit_clause = unit_clause[1:]
                new_changes[unit_clause] = 0    #If negative like -112 then take 112 and say it is false with 0
                global n_negative_assign
                n_negative_assign += 1
            else:
                new_changes[unit_clause] = 1    # If positive literal, assign it a 1 for true
                global n_positive_assign
                n_positive_assign += 1
            satisfied_counter += 1
            continue

        clauses_dict[id] = clause #a clause has an ID, except for pure literal clauses that already have a forced move

        # Both -111 and 111 can be in the literal dict. So no uniqueness, compared to assignment and new changes dictionairy, which only has 111 and then value 0 or 1
        for literal in clause:
            if literal in literal_dict:
                id_list = literal_dict[literal]
                id_list.append(id)
            else: id_list = [id]
            literal_dict[literal] = id_list

        id += 1

    assignments["assign_counter"] = 0
    assignments["satis_counter"] = satisfied_counter
    assignments["new_changes"] = new_changes

    return clauses_dict,literal_dict,assignments
"""
def update_literal_count(clauses_ids,clauses_dict):

    global clauses_learned
    decay = False
    n = 50
    k = 0.9

    for clause_id in clauses_ids:
        clause = clauses_dict.get(clause_id,[])
        for literal in clause:
            vsids_counter[literal] += 1
        clauses_learned += 1
        if clauses_learned % n == 0:
            decay = True

    if decay:
        for literal in vsids_counter:
            vsids_counter[literal] *= k
"""

#"""
def update_literal_count_v2(clause_id,clauses_dict,correspond_literal):

    global clauses_learned
    decay = False
    n = 100
    k = 0.9

    clause = clauses_dict.get(clause_id, [])
    for literal in clause:
        if literal != correspond_literal:
            vsids_counter[literal] += 1
            clauses_learned += 1
            if clauses_learned % n == 0:
                decay = True

    if decay:
        for literal in vsids_counter:
            vsids_counter[literal] *= k
#"""

def check_ties(sorted_list):
    max_value = sorted_list[0][1]
    max_list = []
    for literal, value in sorted_list:
        if value == max_value:
            max_list.append(literal)
        else:
            break

    literal = random.choice(max_list)  # Random when there are ties, else 1 option

    return literal

def split_values_heuristic(heuristic,unassigned_literals,clauses_dict,literal_dict,assign_dict):
    failure_found = False

    if heuristic == 2 or heuristic == 3 or (heuristic > 3 and heuristic < 8): #Jeroslow Wang, one sided and two sided respectively on 2 and 3
                                                                               #MCML1 on 4, MCML2 on 5, PMCML1 on 6 and PMCML2 on 7
        if len(unassigned_literals) == 0:
            return None, None, None, None, True

        score_list = {}
        total_score_twos_sided = []
        for unassigned_literal in unassigned_literals:
            if unassigned_literal[0] == "-":
                pos_literal = unassigned_literal[1:]
                opposite = pos_literal
            else:
                pos_literal = unassigned_literal
                opposite = "-" + pos_literal

            if pos_literal in assign_dict:
                unassigned_literals.remove(unassigned_literal)
                continue

            score = 0
            clause_ids = literal_dict[unassigned_literal]
            for clause_id in clause_ids:
                clause = clauses_dict[clause_id]
                if heuristic == 2 or heuristic == 3:
                    score += 2 ** -len(clause)
                else: #Heuristic 4,5,6,8
                    score += len(clause)

            if heuristic == 2 or heuristic == 4 or heuristic == 6: #One sided
                score_list[unassigned_literal] =  score
            else: #Two sided, so combine score and check which score is higher, which are 3,5 and 7

                opposite_score = score_list.get(opposite, None)
                if opposite_score is not None:
                    total = score + opposite_score

                    if heuristic == 3:

                        if score >= opposite_score and unassigned_literal == pos_literal:
                            total_score_twos_sided.append( (pos_literal, total,1,0))
                        elif score >= opposite_score and unassigned_literal[0] == "-":
                            total_score_twos_sided.append((pos_literal, total, 0, 1))
                        elif score < opposite_score and unassigned_literal == pos_literal:
                            total_score_twos_sided.append((pos_literal, total, 0, 1))
                        elif score < opposite_score and unassigned_literal[0] == "-":
                            total_score_twos_sided.append((pos_literal, total, 1, 0))

                    elif heuristic == 5 or 7:

                        if score <= opposite_score and unassigned_literal == pos_literal:
                            total_score_twos_sided.append( (pos_literal, total,1,0))
                        elif score <= opposite_score and unassigned_literal[0] == "-":
                            total_score_twos_sided.append((pos_literal, total, 0, 1))
                        elif score > opposite_score and unassigned_literal == pos_literal:
                            total_score_twos_sided.append((pos_literal, total, 0, 1))
                        elif score > opposite_score and unassigned_literal[0] == "-":
                            total_score_twos_sided.append((pos_literal, total, 1, 0))
                else:
                    score_list[unassigned_literal] = score
        if len(total_score_twos_sided) > 0:
            if heuristic == 3:
                sorted_list_two_sided = sorted(total_score_twos_sided, key=itemgetter(1),reverse=True)
            else:
                sorted_list_two_sided = sorted(total_score_twos_sided, key=itemgetter(1)) #Two sided, 5 and 7. Dont reverse
            #print("0 index", sorted_list_two_sided[0])
            #print("laatste index", sorted_list_two_sided[-1])
            #input()
            if heuristic == 7: #Probabilistic version
                new = []
                sum = 0
                for literal, score,value_picked,other_value in sorted_list_two_sided:
                    new.append((literal, 2 ** -score,value_picked,other_value))
                    sum += 2 ** -score
                prob_list = []
                literal_list = []
                lit_values = {}
                for literal, score,v1,v2 in new:
                    prob_list.append(score / sum)
                    literal_list.append(literal)
                    lit_values[literal] = (v1,v2)
                literal = np.random.choice(literal_list, 1, p=prob_list)[0]
                value_picked,other_value = lit_values[literal]
            else:
                max_value = sorted_list_two_sided[0][1]
                max_list = []
                for literal,score,v1,v2, in sorted_list_two_sided:
                    if score == max_value:
                        max_list.append((literal,score,v1,v2))
                    else:
                        break
                literal, score, value_picked, other_value = random.choice(max_list)

        elif len(score_list) > 0:
            if heuristic == 2:
                score_list = sorted(list(score_list.items()), key=itemgetter(1),reverse=True)
            else:
                score_list = sorted(list(score_list.items()), key=itemgetter(1)) #One sided 4,6 dont reverse

            if heuristic == 6: #Probabilistic version of 4
                new = []
                sum = 0
                for literal, score in score_list:
                    new.append((literal, 2 ** -score))
                    sum += 2 ** -score
                prob_list = []
                literal_list = []

                for literal, score in new:
                    prob_list.append(score / sum)
                    literal_list.append(literal)
                literal = np.random.choice(literal_list, 1, p=prob_list)[0]
            else:           #heuristic 2 and 4
                literal = check_ties(score_list)

            unassigned_literals.remove(literal)

            if literal[0] == "-":
                literal = literal[1:]
                value_picked = 0
                other_value = 1
            else:
                value_picked = 1
                other_value = 0

    else:
        literal = random.choice(unassigned_literals)     #Random, basic DP
        unassigned_literals.remove(literal)

        while literal in assign_dict:
            if len(unassigned_literals) == 0:
                return None,None,None,None, True
            literal = random.choice(unassigned_literals)
            unassigned_literals.remove(literal)
        values = [0, 1]
        assign_value_index = random.choice([0, 1])
        value_picked = values.pop(assign_value_index)
        other_value = values[0]

    return literal,value_picked,other_value,unassigned_literals,failure_found

def dp_loop(clauses_dict,literal_dict,assign_dict,n_clauses,split_level,unassigned_literals,heuristic):
    failure_found = False
    can_simplify = True

    if len(assign_dict["new_changes"]) > 0:
        clauses_dict, literal_dict, assign_dict, failure_found = process_assignments(clauses_dict, literal_dict, assign_dict, n_clauses,heuristic)

    if failure_found:
        can_simplify = False

    while can_simplify and not failure_found:
        clauses_dict, literal_dict, assign_dict, can_simplify,failure_found = try_simplify(clauses_dict,literal_dict,assign_dict)

        if can_simplify:
            clauses_dict, literal_dict, assign_dict, failure_found = process_assignments(clauses_dict, literal_dict, assign_dict, n_clauses,heuristic)

    if not failure_found:  # Check if all clauses have been satisfied
        check_status(clauses_dict, assign_dict, n_clauses)

    if not failure_found and len(unassigned_literals) > 0:
        # Make copy of dictionaries for the split
        copy_assign_dict = {key: value_assign for (key, value_assign) in assign_dict.items() if key != "new_changes"}
        copy_clauses_dict = {clause_id: clause.copy() for (clause_id, clause) in clauses_dict.items()}
        copy_literal_dict = {literal: list_ids.copy() for (literal, list_ids) in literal_dict.items()}

        literal, value_picked,other_value,unassigned_literals,failure_found = split_values_heuristic(heuristic,unassigned_literals,clauses_dict,literal_dict,assign_dict)
        global n_positive_assign
        global n_negative_assign
        if value_picked == 0:
            n_negative_assign += 1
        else:
            n_positive_assign += 1

        if failure_found:
            return clauses_dict,literal_dict,assign_dict,failure_found

        global amount_of_splits
        amount_of_splits += 1
        copy_unassigned_literals = []
        copy_unassigned_literals.extend(unassigned_literals)
        copy_assign_dict["new_changes"] = {literal:value_picked}

        new_clauses_dict, new_literal_dict, new_assign_dict, failure_found = dp_loop(copy_clauses_dict, copy_literal_dict,copy_assign_dict, n_clauses,split_level+1,copy_unassigned_literals,heuristic)
        if failure_found:
            global amount_of_backtracks
            amount_of_backtracks += 1

            if other_value == 0:
                n_negative_assign += 1
            else:
                n_positive_assign += 1

            assign_dict["new_changes"] = {literal: other_value}
            new_clauses_dict, new_literal_dict, new_assign_dict, failure_found = dp_loop(clauses_dict,literal_dict,assign_dict, n_clauses,split_level + 1,unassigned_literals,heuristic)

        clauses_dict, literal_dict, assign_dict = new_clauses_dict, new_literal_dict, new_assign_dict
    else:
        failure_found = True


    return clauses_dict,literal_dict,assign_dict, failure_found

def run_dp(dimacs_file,heuristic=1):
    solution = False
    try:

        n_variables, n_clauses, set_clauses = read_dimacs(dimacs_file) #Extract from dimacs file
        clauses_dict, literal_dict, assign_dict = store_clauses(set_clauses) #Store clauses,literals in dictionaries and also find unit clauses assignments

        global original_info
        original_info = [n_clauses, n_variables, len(assign_dict["new_changes"])]
        #print("Initial info, amount of clauses, variables, amount filled in", original_info)

        #print("-" * 175)
        #print(len(clauses_dict), len(literal_dict), len(assign_dict)-3)
        new_clauses_dict, new_literal_dict, new_assign_dict,failure_found = process_assignments(clauses_dict,literal_dict,assign_dict,n_clauses,heuristic) #Process the assignments that were found

        if failure_found:
            print("-" * 175)
            raise NoSolutionFound()

        #update_print(new_clauses_dict,new_literal_dict,new_assign_dict,n_clauses,n_variables,failure_found)

        #Check for tautology once
        new_clauses_dict, new_literal_dict, new_assign_dict = check_tautology(new_clauses_dict,new_literal_dict,new_assign_dict)

        global info_before_loop
        info_before_loop = [len(clauses_dict), len(literal_dict), len(assign_dict) - 3]
        #print("Info before loop, amount clauses left, amount literals unassigned, amount of variables assigned", info_before_loop)
        #update_print(new_clauses_dict, new_literal_dict, new_assign_dict, n_clauses, n_variables)

        unassigned_literals = []

        for literal in list(literal_dict.keys()):
            if heuristic == 1 and "-" != literal[0] and literal not in assign_dict:
                 unassigned_literals.append(literal)
            elif heuristic == 2 or heuristic == 3 or (heuristic > 3 and heuristic < 8):
                if literal[0] == "-":
                    pos_literal = literal[1:]
                    neg_literal = literal
                else:
                    pos_literal = literal
                    neg_literal = "-" + pos_literal

                if pos_literal not in assign_dict:
                    unassigned_literals.append(pos_literal)
                    unassigned_literals.append(neg_literal)

        random.shuffle(unassigned_literals)

        #Start searching after initialization of storing clauses, propagating unit clauses and check for tautology
        new_clauses_dict, new_literal_dict, new_assign_dict, failure_found = dp_loop(new_clauses_dict,new_literal_dict,new_assign_dict,n_clauses,1,unassigned_literals,heuristic)

    except SolutionFound:
        #print("-" * 175)
        #print("A solution has been found")
        solution = True
    except NoSolutionFound:
        solution = False
        #print("-" * 175)
        #print("Early contradiction found, no solution")

    return solution

def update_print(clauses_dict,literal_dict,assign_dict,n_clauses, n_variables,failure_found=False):
    print("-" * 175)
    print(len(clauses_dict), len(literal_dict), len(assign_dict) - 3, failure_found)
    print("Amount Variables and assigned ", n_variables, assign_dict["assign_counter"])
    print("Amount clauses and Satisfied clauses:", n_clauses, assign_dict["satis_counter"])
    print("Amount positive and negative assignments:", n_positive_assign, n_negative_assign)
    print("Amount of clauses encountered", clauses_learned)

def display_values(assign_dict):
    print("-" * 175)
    print("Amount of assignments :", len(assign_dict)-3)
    l = [int(k) for (k, v) in assign_dict.items() if v == 1]
    print("length of positive ", len(l))
    l.sort()
    #print(l)

    #Display assignments of all literals for a 9x9 sudoku
    sudoku = []
    for r in range(1, 10):
        for c in range(1, 10):
            pos = str(r) + str(c)
            list = []
            for value in range(1, 10):
                check = pos + str(value)
                check_assignment = assign_dict.get(check, -2)
                list.append((check, check_assignment))
                if (check_assignment == 1):
                    sudoku.append(value)
            #print(list)

    #Displaying the solution of the 9x9 sudoku puzzle
    print("\n")
    for value in range(0, len(sudoku), 9):
        print(sudoku[value:value + 9])
    print("\n")

if __name__ == "__main__":

    if len(sys.argv) == 3:
        if not  "-S" in sys.argv[1]:
            print("Please run as: ./SAT -Sn input_file")
            sys.exit(1)
        else: 
            heuristic = int(sys.argv[1][-1])
        
        input_file = sys.argv[2]
        
        t1 = time.time()
        file = open(input_file,"r")
        found_solution = run_dp(file,heuristic)
        t2 = time.time()

        if found_solution:
            display_values(final_assignment_dictionary)
            print("Amount of splits: ", amount_of_splits)
            print("Amount of backtracks: ", amount_of_backtracks)
            print("Amount of clauses encountered", clauses_learned)
            print("Runtime not including display matrix: " + str((t2 - t1)*1000) + " ms")
            
            del final_assignment_dictionary["new_changes"]
            del final_assignment_dictionary["assign_counter"]
            del final_assignment_dictionary["satis_counter"]
            
            output_file = open(input_file + ".out","w")
            output_file.write("p cnf " + str(len(final_assignment_dictionary)) + " " + str(len(final_assignment_dictionary)) + "\n")
            
            final_assignment = [(k,v) for k, v in final_assignment_dictionary.items()]
            final_assignment.sort(key=lambda tup: tup[0]) 
            for tup in final_assignment:
                if tup[1] == 0:
                    output_file.write("-" + str(tup[0])  + " 0\n")
                else:
                    output_file.write(str(tup[0]) + " 0\n")
        else:
            print("There was no solution")
    else:
        print("Error: Not enough arguments were given. Run as ./SAT -Sn input_file")
        sys.exit(1)