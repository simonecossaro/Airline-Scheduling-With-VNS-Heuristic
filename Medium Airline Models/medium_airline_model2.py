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
    return d * 1440 + int(h) * 60 + int(m)


airline = Airline('ISS')

# SETS
I = airline.itineraries
F = airline.F
A = airline.getA()
IC = airline.IC
IC_it = airline.getICit()
FM = airline.getFM()
FO = airline.getFO()
IR = airline.IR
FI = airline.FI
FIO = airline.getFIO()
R = airline.R
P = airline.P

# PARAMETERS
D = airline.getD()
DI = airline.DI
C = airline.getC()
Cap = airline.getCap()
Fare = airline.Fare
STD = airline.flights['sobt']
MPT = 30
MTT = 30
FT = airline.getFT()
EPD = airline.getEPD()
M = 30
B = airline.B
dev = airline.dev
Θ1 = airline.getΘ1()
Θ2 = airline.getΘ2()
Θ3 = airline.getΘ3()
γ = airline.getγ()

# MODEL 2
model2 = gb.Model()
model2.modelSense = gb.GRB.MAXIMIZE

# DECISION VARIABLES
# x_a,r : 1 if aircraft a flies route r, and 0 otherwise
X = model2.addVars([(a, r) for a in range(len(A)) for r in range(len(R[a]))], vtype=gb.GRB.BINARY)
# y_f,p : 1 if flight copy p of flight f is selected, and 0 otherwise
Y = model2.addVars([(f, p) for f in range(len(F)) for p in range(len(P[f]))], vtype=gb.GRB.BINARY)
# z_i : 1 if itinerary i is selected for inclusion, and 0 otherwise
Z = model2.addVars([i for i in range(len(I))], vtype=gb.GRB.BINARY)
# h_i : the number of passengers travelling in itinerary i
H = model2.addVars([i for i in range(len(I))], vtype=gb.GRB.INTEGER, lb=0)
# t_i,j : the number of passengers requesting itinerary i that the airline attempts to redirect to itinerary j
T = model2.addVars([(i, j) for i in range(len(I)) for j in range(len(I))], vtype=gb.GRB.INTEGER, lb=0)
# edt_f : the expected departure time of flight f under expected propagated delays
EDT = model2.addVars([f for f in range(len(F))], vtype=gb.GRB.INTEGER, lb=0)
# tf_i : 1 if the two connecting flights of itinerary i are operated by the same aircraft (i.e. through flight), and 0 otherwise
TF = model2.addVars([i for i in range(len(IC))], vtype=gb.GRB.BINARY)

# (1) OBJECTIVE FUNCTION
model2.setObjective(
    ((gb.quicksum((Fare[i] * H[i]) for i in range(len(I)))) - (
        gb.quicksum((gb.quicksum((C[r] * X[a, r]) for r in range(len(R[a]))) for a in range(len(A)))))))

# CONSTRAINTS
# (2) ensure that every flight is assigned to an aircraft
for f in range(len(F)):
    for p in range(len(P[f])):
        model2.addConstr(
            gb.quicksum((gb.quicksum(Θ1[f][p][R[a][r]] * X[a, r] for r in range(len(R[a])))) for a in range(len(A))) ==
            Y[f, p])
# (4) ensure that every aircraft takes at most one route
for a in range(len(A)):
    model2.addConstr(gb.quicksum(X[a, r] for r in range(len(R[a]))) <= 1)
# (17)
for f in FM:
    model2.addConstr(
        gb.quicksum(Y[airline.nid_index_dict[f], p] for p in range(len(P[airline.nid_index_dict[f]]))) == 1)
# (18)
for f in FO:
    model2.addConstr(
        gb.quicksum(Y[airline.nid_index_dict[f], p] for p in range(len(P[airline.nid_index_dict[f]]))) <= 1)
# (19)
for f in range(len(F)):
    model2.addConstr(EDT[f] == dateCoding(STD[f]) +
                      gb.quicksum((gb.quicksum((dev[r][f] * X[a, r]) for r in range(len(R[a])))) for a in range(len(A)))
                      )
# (20)
for i in range(len(I)):
    model2.addConstr(H[i] <= D[i] - gb.quicksum(((T[i, j] - B[i][j] * T[j, i])) for j in IR[i]))
# (21)
for i in range(len(I)):
    for f in FIO[i]:
        model2.addConstr(
            Z[i] <= gb.quicksum((Y[airline.nid_index_dict[f], p]) for p in range(len(P[airline.nid_index_dict[f]]))))
# (22)
for i in range(len(IC)):
    model2.addConstr(TF[i] == gb.quicksum(
        (gb.quicksum((Θ3[i][R[a][r]] * X[a, r]) for r in range(len(R[a])))) for a in range(len(A))))
# (23)
for i in range(len(IC)):
    f1 = airline.nid_index_dict[IC[i][0]]
    f2 = airline.nid_index_dict[IC[i][1]]
    model2.addConstr(EDT[f2] - EDT[f1] - FT[f1] >=
                      (-MPT + MTT) * TF[i] + MPT * Z[IC_it[i]] - M * (1 - Z[IC_it[i]]))
# (24)
for f in range(len(F)):
    model2.addConstr(gb.quicksum((Θ2[i][f] * H[i]) for i in range(len(I))) <=
                      gb.quicksum((Cap[a] * gb.quicksum(
                          (gb.quicksum((Θ1[f][p][R[a][r]] * X[a, r]) for p in range(len(P[f])))) for r in
                          range(len(R[a])))) for a in range(len(A))))
# (25)
for i in range(len(I)):
    model2.addConstr(H[i] <= DI[i] * Z[i])
# (30)
for i in range(len(I)):
    for j in range(len(IR[i])):
        model2.addConstr(T[i, j] <= D[i])

model2.optimize()

