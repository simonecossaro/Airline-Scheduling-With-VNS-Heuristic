import gurobipy as gb
import warnings
warnings.filterwarnings('ignore')
from Airline import Airline

airlineA = Airline('ISS')

# SETS
I = airlineA.itineraries
F = airlineA.F
A = airlineA.getA()
IC = airlineA.IC
IC_it = airlineA.getICit()
FI = airlineA.FI
R = airlineA.R
P = airlineA.P

#PARAMETERS
D = airlineA.getD()
C = airlineA.getC()
Cap = airlineA.getCap()
Fare = airlineA.Fare
B = airlineA.B
Θ1 = airlineA.getΘ1()
Θ2 = airlineA.getΘ2()
γ = airlineA.getγ()

#MODEL 1
model1 = gb.Model()
model1.modelSense = gb.GRB.MAXIMIZE

# DECISION VARIABLES
# x_a,r : 1 if aircraft a flies route r, and 0 otherwise
X = model1.addVars( [(a,r) for a in range(len(A)) for r in range(len(R[a]))], vtype=gb.GRB.BINARY)
# y_f,p : 1 if flight copy p of flight f is selected, and 0 otherwise
Y = model1.addVars( [(f,p) for f in range(len(F)) for p in range(len(P[f]))], vtype=gb.GRB.BINARY)
# w_f1p1,f2p2 : 1 if flight copy pair (f1p1,f2,p2)is selected, 0 otherwise
W = model1.addVars( [(f1,p1,f2,p2) for f1 in range(len(F)) for p1 in range(len(P[f1])) 
                         for f2 in range(len(F)) for p2 in range(len(P[f2]))], vtype=gb.GRB.BINARY)
# h_i : the number of passengers travelling in itinerary i
H = model1.addVars([i for i in range(len(I))], vtype=gb.GRB.INTEGER, lb = 0)


# (1) OBJECTIVE FUNCTION
model1.setObjective( 
     ((gb.quicksum( (Fare[i]*H[i]) for i in range(len(I)) )) - (gb.quicksum((gb.quicksum((C[r]*X[a,r])for r in range(len(R[a])))for a in range(len(A)) ) )  )))


# CONSTRAINTS
# (2) ensure that every flight is assigned to an aircraft
for f in range(len(F)):
    for p in range(len(P[f])):
        model1.addConstr(gb.quicksum((gb.quicksum(Θ1[f][p][R[a][r]]*X[a,r] for r in range(len(R[a])))) for a in range(len(A)) ) == Y[f,p] )
# (3) ensure that exactly one flight copy will be selected for each flight
for f in range(len(F)):
    model1.addConstr( gb.quicksum(Y[f,p] for p in range(len(P[f]))) == 1 )
# (4) ensure that every aircraft takes at most one route
for a in range(len(A)):
    model1.addConstr( gb.quicksum(X[a,r] for r in range(len(R[a]))) <= 1 )
# (5) limit the number of passengers taken on itineraries to the forecast demand 
for i in range(len(I)):
    model1.addConstr( H[i] <= D[i] )
# (6) limit the number of passengers taken on itineraries to the number of available aircraft seats
for f in range(len(F)):
    model1.addConstr( gb.quicksum((Θ2[i][f]*H[i]) for i in range(len(I))) <= 
                         gb.quicksum((Cap[a] * gb.quicksum((gb.quicksum((Θ1[f][p][R[a][r]]*X[a,r])for p in range(len(P[f]))))for r in range(len(R[a]))))for a in range(len(A)) ))  
#(11)
for i in range(len(FI)):
    for fm in FI[i]:
        for fn in FI[i]:
            if(Θ2[i][airlineA.nid_index_dict[fm]] == 1 and Θ2[i][airlineA.nid_index_dict[fn]] == 1):
                model1.addConstr( H[i] <= D[i]*gb.quicksum((gb.quicksum(γ[i][FI[i].index(fm)][pm][FI[i].index(fn)][pn]*W[airlineA.nid_index_dict[fm],pm,airlineA.nid_index_dict[fn],pn] for pn in range(len(P[airlineA.nid_index_dict[fn]])))for pm in range(len(P[airlineA.nid_index_dict[fm]]))) ))
#(12)
for i in range(len(I)):
    for fm in range(len(FI[i])):
        for fn in range(len(FI[i])):
            for pm in range(len(P[fm])):
                for pn in range(len(P[fn])):
                    model1.addConstr( W[fm,pm,fn,pn] <= Y[fm,pm] )
#(13)
for i in range(len(I)):
    for fm in range(len(FI[i])):
        for fn in range(len(FI[i])):
            for pm in range(len(P[fm])):
                for pn in range(len(P[fn])):
                    model1.addConstr( W[fm,pm,fn,pn] <= Y[fn,pn] )
#(14)
for i in range(len(I)):
    for fm in range(len(FI[i])):
        for fn in range(len(FI[i])):
            for pm in range(len(P[fm])):
                for pn in range(len(P[fn])):
                    model1.addConstr( W[fm,pm,fn,pn] >= Y[fm,pm]+Y[fn,pn]-1 )


model1.optimize()



