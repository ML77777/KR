#File format version
#For reading Dimacs input from sudoku clauses and sudoku puzzle
import sys
import random
import time
import pickle
counter = 0

def read_dimacs(dimacs_file):

    clauses = []
    n_clauses = 0
    n_variables = 0

    #Check first two lines for the c and p lines if they are there
    lines = dimacs_file.readlines()
    for line in lines:

        if not (line[0] == "c" or line[0] == "%" or line[0] == "0" or line.strip() == "\n" or line.strip() == "0\n" or line.strip() == ""):
            if line[0] == "p":
                splitted_line = line.split()
                n_clauses = int(splitted_line[-1])
                n_variables = int(splitted_line[-2])
            else:
                clause = line.split()[:-1]
                clauses.append(list(map(int,clause)))   #In case to convert every element to actual integer

    #print(n_variables,n_clauses,clauses)
    return n_variables,n_clauses,clauses

## TODO check tautology (in case there is a tautology, randomly assign value and add to changed_literals)
def store_clauses(initial_clauses, n_clauses):#,n_variables,n_clauses):
    clauses_dict = {} #dictionary with key = id and value = clause (= list of strings)
    literal_dict = {} #dictionary with key = literal and value = list of clauses in which literal occurs
    assignments = {} #dictionary with key = literal and value = assigned truth value
    lit_pos_occ = {} #dictionary with key = literal and value = # of positive occurences in not yet satisfied clauses
    lit_neg_occ = {} #dictionary with key = literal and value = # of negative occurences in not yet satisfied clauses
    unassigned_literals = [] #list of all literals that do not yet have a truth value assigned to them
    changed_literals = []
    ID = 1
    
    for clause in initial_clauses:
        clauses_dict[ID] = clause
        for literal in clause:
                #Add literal to assignments with a 2 for 'unassigned'
                if not abs(literal) in assignments:
                    assignments[abs(literal)] = None
                   
                #Add clause id to the literal dict for this literal
                if abs(literal) in literal_dict:
                    id_list = literal_dict[abs(literal)]
                    id_list.append(ID)
                else: 
                    id_list = [ID]
                literal_dict[abs(literal)] = id_list
                
                if literal < 0:
                #Add 1 to the the count of negative occurences
                    if abs(literal) in lit_neg_occ:
                        lit_neg_occ[abs(literal)] += 1
                    else:
                        lit_neg_occ[abs(literal)] = 1
                else:
                #Add 1 to the the count of positive occurences
                    if literal in lit_pos_occ:
                        lit_pos_occ[literal] += 1
                    else:
                        lit_pos_occ[literal] = 1
            
        if len(clause) == 1: #Found unit clause
            unit_clause = clause[0]
            if unit_clause < 0:
                #if it is a negative literal
                unit_clause = abs(unit_clause)
                
                if assignments[unit_clause] == None:
                    #assignments[unit_clause] = False #assign the literal a 0 for 'false'
                    changed_literals.append(unit_clause)
                elif assignments[unit_clause] == True:
                    return clauses_dict, n_clauses, literal_dict, assignments, changed_literals, unassigned_literals, lit_pos_occ, lit_neg_occ, True
            else:
                if assignments[unit_clause] == None:
                    #assignments[unit_clause] = True #assign the literal a 1 for 'true'
                    changed_literals.append(unit_clause)
                    del clauses_dict[ID]
                elif assignments[unit_clause] == False:
                    return clauses_dict, n_clauses, literal_dict, assignments, changed_literals, unassigned_literals, lit_pos_occ, lit_neg_occ, True
                
            n_clauses -= 1

        ID += 1
    
    #Check if all literals are present in lit_neg_occ and lit_pos_occ, else it is a pure literal
    for lit in [k for k, v in assignments.items()]:
        if not (lit in lit_neg_occ):
            lit_neg_occ[lit] = 0
            assignments[lit] = True
            if not lit in changed_literals:
                changed_literals.append(lit)
            
            
        if not (lit in lit_pos_occ):
            lit_pos_occ[lit] = 0
            assignments[lit] = False
            if not lit in changed_literals:
                changed_literals.append(lit)
            
    unassigned_literals = [k for k, v in assignments.items() if v == None]
    
    return clauses_dict, n_clauses, literal_dict, assignments, changed_literals, unassigned_literals, lit_pos_occ, lit_neg_occ, False

def run_dp(dimacs_file):
    n_variables, n_clauses, set_clauses = read_dimacs(dimacs_file)
    clauses_dict, clauses_count, literal_dict, assignments, changed_literals, unassigned_literals, lit_pos_occ, lit_neg_occ, contradiction = store_clauses(set_clauses, n_clauses)
    
    if contradiction:
        return False, {}
    #Algorithm loop starts here
    assignments, contradiction = dp(clauses_dict, clauses_count, literal_dict, assignments, changed_literals, False, unassigned_literals, lit_pos_occ, lit_neg_occ)
    
    if not contradiction:
        return True, assignments    
    else:
        return False, assignments
    

def dp(clauses_dict, clauses_count, literal_dict, assignments, changed_literals, contradiction, unassigned_literals, lit_pos_occ, lit_neg_occ):
    new_changed_literals = []
    
    #Check contradictions and simplify
    for lit in changed_literals:
        relevant_clauses = literal_dict[lit]
        for clause_id in relevant_clauses:
            
            ##Try option where clauses are removed from literal_dict instead
            
            
            #if the clause is not already satisfied
            if clause_id in clauses_dict:
                clauses_dict1, clauses_count1, assignments1, new_changed_literals1, contradiction1, unassigned_literals1, lit_pos_occ1, lit_neg_occ1 = simplify_clause(clause_id, pickle.loads(pickle.dumps(clauses_dict)), clauses_count, assignments.copy(), new_changed_literals, contradiction, unassigned_literals.copy(), lit_pos_occ.copy(), lit_neg_occ.copy())
                if contradiction1:
                    return assignments, True
                else:
                    clauses_dict, clauses_count, assignments, new_changed_literals, contradiction, unassigned_literals, lit_pos_occ, lit_neg_occ = clauses_dict1, clauses_count1, assignments1, new_changed_literals1, contradiction1, unassigned_literals1, lit_pos_occ1, lit_neg_occ1
    #Check stop condition
    if len(clauses_dict) == 0:
        return assignments, False
    elif len(new_changed_literals) > 0:
        
        ###Check out
        assignments, contradiction = dp(pickle.loads(pickle.dumps(clauses_dict)), clauses_count, literal_dict.copy(), assignments.copy(), new_changed_literals, contradiction, unassigned_literals.copy(), lit_pos_occ.copy(), lit_neg_occ.copy())
        return assignments, contradiction
    else:
    #Split
        #Choose literal from the not yet assigned literals:
        #global counter
        #print(counter)
        #counter += 1
        random_lit = random.choice(unassigned_literals)
        print("Clauses left: "+ str(clauses_count) + " unassigned_literals: " + str(len(unassigned_literals)))
        
        random_truth_value = random.choice([True, False])
        
        #assign literal true or false            
        assignments[random_lit] = random_truth_value
        new_changed_literals.append(random_lit)
        unassigned_literals.remove(random_lit)
        
        #Recursion
        assignments1, contradiction1 = dp(pickle.loads(pickle.dumps(clauses_dict)), clauses_count, literal_dict.copy(), assignments.copy(), new_changed_literals, contradiction, unassigned_literals.copy(), lit_pos_occ.copy(), lit_neg_occ.copy())
        if contradiction1 == True:
            #print(contradiction1)
            #give the above literal the other truth value
            assignments[random_lit] = not random_truth_value
            #Recursion
            
            #CHECK OUT
            assignments1, contradiction1 = dp(pickle.loads(pickle.dumps(clauses_dict)), clauses_count, literal_dict.copy(), assignments.copy(), new_changed_literals, contradiction, unassigned_literals.copy(), lit_pos_occ.copy(), lit_neg_occ.copy())
        
        return assignments1, contradiction1
        
def simplify_clause(clause_id, clauses_dict, clauses_count, assignments, changed_literals, contradiction, unassigned_literals, lit_pos_occ, lit_neg_occ):
    #global counter
    #print(counter)
    #counter += 1
    
    if contradiction:
        return clauses_dict, clauses_count, assignments, changed_literals, True, unassigned_literals, lit_pos_occ, lit_neg_occ
    
    clause = clauses_dict[clause_id]
        
    #if it is a unit clause, check for contradiction
    if len(clause) == 1:
        if clause[0] < 0:
            symbol = abs(clause[0])
            
            if assignments[symbol] == None:
                assignments[symbol] = False
                changed_literals.append(symbol)
                unassigned_literals.remove(symbol)
                del clauses_dict[clause_id]
                clauses_count -= 1
            elif assignments[symbol] == True:
                return clauses_dict, clauses_count, assignments, changed_literals, True, unassigned_literals, lit_pos_occ, lit_neg_occ

        else:
            symbol = clause[0]
            if assignments[symbol] == None:
                assignments[symbol] = True
                changed_literals.append(symbol)
                unassigned_literals.remove(symbol)
                del clauses_dict[clause_id]
                clauses_count -= 1
            elif assignments[symbol] == False:
                return clauses_dict, clauses_count, assignments, changed_literals, True, unassigned_literals, lit_pos_occ, lit_neg_occ
                
    #else it is not a unit clause
    else: 
        clause_changed = False
        clause_true = False
        clause_initial = clause.copy()
        for literal in clause_initial:
            if literal < 0: 
                if assignments[abs(literal)] == False:
                    clauses_count -= 1
                    del clauses_dict[clause_id]
                    clause_true = True
                    break
                
                elif assignments[abs(literal)] == True:
                    clause.remove(literal)
                    clause_changed = True
                    
            else:
                if assignments[literal] == True:
                    clauses_count -= 1
                    del clauses_dict[clause_id]
                    clause_true = True
                    break
                
                elif assignments[literal] == False:
                    clause.remove(literal)
                    clause_changed = True
                    
        #check for contradiction
        if len(clause) == 0:
            return clauses_dict, clauses_count, assignments, changed_literals, True, unassigned_literals, lit_pos_occ, lit_neg_occ
        elif clause_true:
            for literal in clause:
                ## Try without pure literal check
                if literal < 0:
                    symbol = abs(literal)
                    
                    if lit_neg_occ[symbol] > 0:
                        lit_neg_occ[symbol] -= 1
                else:
                    symbol = literal
                    
                    if lit_pos_occ[symbol] > 0:
                        lit_pos_occ[symbol] -= 1
                
                if lit_neg_occ[symbol] == 0 and lit_pos_occ[symbol] > 0:
                    if assignments[symbol] == None:
                        assignments[symbol] = True
                        changed_literals.append(symbol)
                        unassigned_literals.remove(symbol)
                elif lit_pos_occ[symbol] == 0 and lit_neg_occ[symbol] > 0:
                    if assignments[symbol] == None:
                        assignments[symbol] = False
                        changed_literals.append(symbol)
                        unassigned_literals.remove(symbol)
               
        if clause_changed and not clause_true:
            clauses_dict[clause_id] = clause
            clauses_dict, clauses_count, assignments, changed_literals, contradiction, unassigned_literals, lit_pos_occ, lit_neg_occ = simplify_clause(clause_id, clauses_dict, clauses_count, assignments, changed_literals, contradiction, unassigned_literals, lit_pos_occ, lit_neg_occ)
    
    return clauses_dict, clauses_count, assignments, changed_literals, contradiction, unassigned_literals, lit_pos_occ, lit_neg_occ
                
#if __name__ == "__main__":
#    if len(sys.argv) == 1:
#        file = open("./input_file.cnf","r") #For testing
#        run_dp(file)#For testing

#        print("Error: No arguments were given")
#        sys.exit(1)
#    run_dp(sys.argv[2])
    
    
#######  Temporary testing function  #######
def test_dp1(): 
    t1 = time.time()
    file = open("./input_file.cnf", "r")
    random.seed(3)
    success, assignments = run_dp(file)
    t2 = time.time()
    print("Runtime: " + str((t2 - t1) * 1000))
    
    return success

def test_dp2():
    suc = 0
    fail = 0
    
    for i in range(1000):
        file = open("./SAT/uf20-0" + str(i+1) + ".cnf","r")
        success, assignments = run_dp(file)
        if success:
            suc += 1
        else:
            fail += 1
        
        if (i+1) % 10 == 0:
            print(str((i+1)/10) + "%")
            
    print("Success rate: " + str(suc/10) + "%")
    print("Fail rate: " + str(fail/10) + "%")
    
    return

def test_dp3():
    for i in range(1000):
        random.seed(i)
        file = open("./input_file2.cnf", "r")
        success, assignments = run_dp(file)
        #print(assignments)
        if not success:
            print(i)
    return

print(test_dp1())
#test_dp2()
#test_dp3()