from Airline import Airline
import gurobipy as gb
import warnings
warnings.filterwarnings('ignore')

def dateCoding(date):
    d = 0
    day = str(date)[8:10]
    if (day == '12'):
        d = 1
    h = str(date)[11:13]
    m = str(date)[14:16]
    return d*1440+int(h)*60 + int(m)

airlineA = Airline('ISS')

# SETS
I = airlineA.itineraries
F = airlineA.F
A = airlineA.getA()
IC = airlineA.IC
IC_it = airlineA.getICit()
FM = airlineA.getFM()
FO = airlineA.getFO()
IR = airlineA.IR
FI = airlineA.FI
FIO = airlineA.getFIO()
R = airlineA.R
P = airlineA.P

#PARAMETERS
D = airlineA.getD()
DI = airlineA.DI
C = airlineA.getC()
Cap = airlineA.getCap()
Fare = airlineA.Fare
STD = airlineA.flights['sobt']
MPT = 30
MTT = 30
FT = airlineA.getFT()
EPD = airlineA.getEPD()
M = 30
B = airlineA.B
dev = airlineA.dev
Θ1 = airlineA.getΘ1()
Θ2 = airlineA.getΘ2()
Θ3 = airlineA.getΘ3()
γ = airlineA.getγ()

#MODEL 2
model22 = gb.Model()
model22.modelSense = gb.GRB.MAXIMIZE

# DECISION VARIABLES
# x_a,r : 1 if aircraft a flies route r, and 0 otherwise
X = model22.addVars( [(a,r) for a in range(len(A)) for r in range(len(R[a]))], vtype=gb.GRB.BINARY)
# y_f,p : 1 if flight copy p of flight f is selected, and 0 otherwise
Y = model22.addVars( [(f,p) for f in range(len(F)) for p in range(len(P[f]))], vtype=gb.GRB.BINARY)
# z_i : 1 if itinerary i is selected for inclusion, and 0 otherwise
Z = model22.addVars([i for i in range(len(I))], vtype=gb.GRB.BINARY)
# h_i : the number of passengers travelling in itinerary i
H = model22.addVars([i for i in range(len(I))], vtype=gb.GRB.INTEGER, lb = 0)
# t_i,j : the number of passengers requesting itinerary i that the airline attempts to redirect to itinerary j
T = model22.addVars( [(i,j) for i in range(len(I)) for j in range(len(I))], vtype=gb.GRB.INTEGER, lb = 0)
# edt_f : the expected departure time of flight f under expected propagated delays
EDT = model22.addVars([f for f in range(len(F))], vtype=gb.GRB.INTEGER, lb = 0)
# tf_i : 1 if the two connecting flights of itinerary i are operated by the same aircraft (i.e. through flight), and 0 otherwise
TF = model22.addVars([i for i in range(len(IC))], vtype=gb.GRB.BINARY)


# (1) OBJECTIVE FUNCTION
model22.setObjective( 
     ((gb.quicksum( (Fare[i]*H[i]) for i in range(len(I)) )) - (gb.quicksum((gb.quicksum((C[r]*X[a,r])for r in range(len(R[a])))for a in range(len(A)) ) )  )))

# CONSTRAINTS
# (2) ensure that every flight is assigned to an aircraft
for f in range(len(F)):
    for p in range(len(P[f])):
        model22.addConstr(gb.quicksum((gb.quicksum(Θ1[f][p][R[a][r]]*X[a,r] for r in range(len(R[a])))) for a in range(len(A)) ) == Y[f,p] )
# (4) ensure that every aircraft takes at most one route
for a in range(len(A)):
    model22.addConstr( gb.quicksum(X[a,r] for r in range(len(R[a]))) <= 1 )
# (17)
for f in FM:
    model22.addConstr(gb.quicksum(Y[airlineA.nid_index_dict[f],p] for p in range(len(P[airlineA.nid_index_dict[f]]))) == 1)
# (18)
for f in FO:
    model22.addConstr(gb.quicksum(Y[airlineA.nid_index_dict[f],p] for p in range(len(P[airlineA.nid_index_dict[f]]))) <= 1)
# (19)
for f in range(len(F)):
    model22.addConstr(EDT[f] == dateCoding(STD[f]) + 
                         gb.quicksum((gb.quicksum((dev[r][f]*X[a,r])for r in range(len(R[a]))))for a in range(len(A)))
                        )               
# (20)
for i in range(len(I)):
    model22.addConstr( H[i] <= D[i] - gb.quicksum(((T[i,j]-B[i][j]*T[j,i]))for j in IR[i]) )              
# (21)
for i in range(len(I)):
    for f in FIO[i]:
        model22.addConstr( Z[i] <= gb.quicksum((Y[airlineA.nid_index_dict[f],p])for p in range(len(P[airlineA.nid_index_dict[f]]))))
# (22)
for i in range(len(IC)):
    model22.addConstr(TF[i] == gb.quicksum((gb.quicksum((Θ3[i][R[a][r]]*X[a,r])for r in range(len(R[a]))))for a in range(len(A))))
# (23)
for i in range(len(IC)):
    f1 = airlineA.nid_index_dict[IC[i][0]]
    f2 = airlineA.nid_index_dict[IC[i][1]]
    model22.addConstr( EDT[f2] - EDT[f1] - FT[f1] >= 
                                 (-MPT + MTT)* TF[i] + MPT*Z[IC_it[i]] - M*(1-Z[IC_it[i]]) )
# (24)
for f in range(len(F)):
    model22.addConstr( gb.quicksum((Θ2[i][f]*H[i]) for i in range(len(I))) <= 
                           gb.quicksum((Cap[a] * gb.quicksum((gb.quicksum((Θ1[f][p][R[a][r]]*X[a,r])for p in range(len(P[f]))))for r in range(len(R[a]))))for a in range(len(A)) ))                        
# (25)
for i in range(len(I)):
    model22.addConstr( H[i] <= DI[i]*Z[i] )
# (30)
for i in range(len(I)):
    for j in range(len(IR[i])):
        model22.addConstr( T[i,j] <= D[i] )
        
model22.optimize()
