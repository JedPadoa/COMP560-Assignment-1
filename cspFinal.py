#Processing input file and representing color constraints
#nodes, and creating the graph
def process_file(f,delim,colors,nodes,graph,arc,ledger):
    with open(f,'r') as file:
        for line in file:
            line = line.strip()
            if(line == '<blank line>'):
                delim+=1
            elif(line != ''):
                if(delim == 0):
                    colors.append(line)
                elif(delim == 1):
                    nodes.append(line)
                else:          
                    graph[line.split()[0]].append(line.split()[1])
                    graph[line.split()[1]].append(line.split()[0])

                    #A -> B and B -> A in arcs
                    #Arcs will get added to agenda
                    arcs.append((line.split()[0],line.split()[1]))
                    arcs.append((line.split()[1],line.split()[0]))

    #Add nodes with no connections
    for i in nodes:
        if i not in graph:
            graph[i] = []
    
    #populate the ledger
    for i in graph.keys():
        ledger[i] = colors.copy()

#CSP Class

class mapcolor:
    def __init__(self,domain,values,graph,arcs,ledger):
        self.domain = domain #colors
        self.values = values #states
        self.graph = graph   #graph as dict
        self.arcs = arcs     #list of arcs A->B and B->A
        self.ledger = ledger


def AC_next(solution,csp):
    #Done with Most Restrained Variable
    remaining_vars = defaultdict(list)
    for value in csp.values:
        if value not in solution.keys():
            remaining_vars[value] = len(csp.ledger[value])
            mrv = min(remaining_vars.keys(), key=(lambda k: remaining_vars[k]))
    return mrv

#Check if labeling was correct
def check(solution,csp):
    for i in solution:
        for j in csp.graph[i]:
            if solution[i] == solution[j]:
                return False
        
    return True

def AC3_ledger(solution,color,xj,csp):
    for xi in csp.graph[xj]:
        if(xi not in solution and color in csp.ledger[xi]):
            if(len(csp.ledger[xi])==1): #the last val is a conflict
                return False
            csp.ledger[xi].remove(color) #remove color from adjacents
    return True

def consistent(color,cur_xi,solution,csp):
    for adj in csp.graph[cur_xi]:
        if adj in solution.keys() and solution[adj]==solution[cur_xi]:
            return False
    return True
	
#execute backtracking algorithm
def backtrack(solution,csp):
    global backtrack_count
    backtrack_count+=1
    if len(solution)==len(csp.graph):
        return solution
    
    cur_xi = AC_next(solution,csp) #cur_xi is A in (A,B) pair or Xi in (Xi,Xj) pair
    
    for color in csp.ledger[cur_xi]: #run backtrack on each possible color for Xi
        if consistent(color,cur_xi,solution,csp):
            solution[cur_xi] = color
        if AC3_ledger(solution,color,cur_xi,csp):
            path = backtrack(solution,csp)
            if path:
                return path
        else:
            del solution[cur_xi]
    return False

import sys
from collections import defaultdict
import random
import time


#Definitions
ledger = defaultdict(list)
delim = 0
colors = []
nodes = []
graph = defaultdict(list)
arcs = []

#variable represents input file:
f1 = input("Enter file path: ")

#processing the input file
process_file(f1,delim,colors,nodes,graph,arcs,ledger)
csp = mapcolor(colors,nodes,graph,arcs,ledger)
 
ledger = defaultdict(list)
delim = 0
colors = []
nodes = []
graph = defaultdict(list)
arcs = []

#Finds number of local conflicts for a given value
def local_conflicts(value,solution,color,csp):
    c=0
    for i in csp.graph[value]:
        if solution[i] == color:
            c+=1
    return c


#Count the number of conflicts that caused by each node
    #dictionary with #of conflicts based on adjacent nodes
    #from graph
#reassign the color for the node with max(conflicts)    
def global_conflicts(solution,csp):
    conflicts = defaultdict(str)
    c=0
    for i in csp.graph.keys():
        c=0
        for j in csp.graph[i]:
            if solution[j] == solution[i]:
                c+=1
        conflicts[i]=c
    return max(conflicts.keys(),key=(lambda k: conflicts[k]))


def reassign(solution,csp):
    conflicts = defaultdict(str)
    
    #get maxconflict from "conflicts"
    max_conflict = global_conflicts(solution,csp)
    updated_domain = csp.domain.copy()
    cur_color = solution[max_conflict]
    updated_domain.remove(cur_color)
    #compare results of each possible color
    for color in updated_domain:  
        conflicts[color] = local_conflicts(max_conflict,solution,color,csp)
    
    #return result that minimizes conflicts
    solution[max_conflict]= min(conflicts.keys(),key=(lambda k:conflicts[k])) #reassign max_conflict to least conflicted color


#Check if labeling was correct
#Functions as the objective function in this case
    #Checks if you're moving towards the goal solution

def goal_state(solution,csp):
    for i in solution:
        for j in csp.graph[i]:
            if solution[i] == solution[j]:
                return False
        
    return True    
    

#Generates initial random solution for hillclimbing algorithm
def generate_random_solution(solution,csp):

    for i in csp.graph.keys():
        solution[i] = csp.domain[random.randint(0,len(csp.domain)-1)]
    return solution

#Executes hillclimbing algorithm
def hillclimbing(solution,csp):
    global hillclimbing_solution
    start = time.time()
    HALT = 60
    #random initialization
    solution = generate_random_solution(solution,csp)
    
    #find greatest global conflict    
    #reassign max global conflict
    #find greatest global conflict
    #reassign max global conflict
    while(not goal_state(solution,csp)):
        hillclimbing_solution+=1
        #Execution time exceeds 1 minute
        if time.time() > start + HALT:
            return('timeout')
        reassign(solution,csp)
    return(solution)


#Run backtracking and hillclimbing on input file

solution1 = defaultdict(list)
backtrack_count=0
backtrack(solution1,csp)

solution2 = defaultdict(list)
hillclimbing_solution=0
hillclimbing(solution2,csp)

#Print assigned colors
print(solution1)
#Check and print if solution was found
backtrack_result=check(solution1,csp)
print("Backtracking consistency check:", backtrack_result)
#Print number of steps to find solution
print("Number of Backtrack steps:",backtrack_count)

#Same for hillclimbing
print(solution2)
print("Hillclimbing consistency check:", check(solution2,csp))
print("Number of Hillclimbing steps:",hillclimbing_solution)




