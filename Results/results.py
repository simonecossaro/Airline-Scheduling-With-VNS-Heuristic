from Airline import Airline
from VNS.VNS import VNS
import time
import zlib
import pandas as pd
import gurobi as gb


def dateCoding(date):
    d = 0
    day = str(date)[8:10]
    if day == '12':
        d = 1
    h = str(date)[11:13]
    m = str(date)[14:16]
    return d * 1440 + int(h) * 60 + int(m)

airlines_name = ["NVR","RSY","ANA","KAL","ASL","DAL","UAL"]
df_results = pd.DataFrame(columns=["airline", "total_flights", "model1", "model1_linear", "model2", "vns","gap"])
df_time = pd.DataFrame(columns=["airline", "total_flights", "model1", "model1_linear", "model2", "vns"])
results = list()

for airline_name in airlines_name:
    res_list = list()
    time_list = list()
    res_list.append(airline_name)
    time_list.append(airline_name)
    airline = Airline(airline_name)
    # SETS
    # I set of passenger itineraries
    I = airline.itineraries
    # F set of flights
    F = airline.F
    res_list.append(len(F))
    time_list.append(len(F))
    # A set of aircraft
    A = airline.get_a()
    # IC set of one-stop itineraries, IC_it set of indexes of one-stop itineraries
    IC = airline.IC
    IC_it = airline.get_ic_it()
    # FM set of mandatory flights
    FM = airline.get_fm()
    # FO set of optional flights
    FO = airline.get_fo()
    # IR the set of itineraries where passenger spilled from itinerary i can be redirected to
    IR = airline.IR
    # FI set of flights within itinerary i
    FI = airline.FI
    # FIO set of optional flights within itinerary i
    FIO = airline.get_fio()
    # R set of aircraft routes
    R = airline.R
    # R3 set of flights within routes
    R3 = airline.R3
    # P set of flights copies
    P = airline.P

    # PARAMETERS
    # D[i]: the demand forecast for passenger itinerary i
    D = airline.get_d()
    # DI[i]: the maximum number of passengers carried in itinerary i
    DI = airline.DI
    # C[r]: the operation and delay penalty cost of executing aircraft route r
    C = airline.get_c()
    # Cap[a]: the number of seats (capacity) in aircraft a
    Cap = airline.get_cap()
    # Fare[i]: the average fare for itinerary i
    Fare = airline.Fare
    # STD[f] the schedule time of departure of flight f
    STD = airline.flights['sobt']
    # MPT the minimum passenger connection time
    MPT = 30
    # MTT the minimum turnaround time
    MTT = 30
    # FT[f] the block time of flight f
    FT = airline.get_ft()
    # EPD[r][f] the expected propagated delays of flight f in route r
    EPD = airline.get_epd()
    # M the minimum possible connection time between flight f1, f2
    M = 30
    # B[i][j] Recapture rate from itinerary i to itinerary j
    B = airline.B
    # de[f][r]v deviation from the STD of flight f in aircraft route r
    dev = airline.dev
    # Θ1[f][p][r]: 1 if flight f, copy p ∈ P is served in route r, and 0 otherwise
    Θ1 = airline.get_Θ1()
    # Θ2[i][f]: 1 if itinerary i involves flight f, and 0 otherwise
    Θ2 = airline.get_Θ2()
    # Θ3[r][i] 1 if the component flights of connecting itinerary i are executed by the same aircraft in route r, and 0 otherwise
    Θ3 = airline.get_Θ3()
    # γ[i][f1][p1][f2][p2]: 1 if itinerary i∈IC exists between flight f1, copy p1 and flight f2, copy p2
    γ = airline.get_γ()

    # MODEL 1
    start = time.perf_counter()
    model1 = gb.Model()
    model1.modelSense = gb.GRB.MAXIMIZE

    # DECISION VARIABLES
    # X[a,r] : 1 if aircraft a flies route r, and 0 otherwise
    X = model1.addVars([(a, r) for a in range(len(A)) for r in range(len(R[a]))], vtype=gb.GRB.BINARY)
    # Y[f,p] : 1 if flight copy p of flight f is selected, and 0 otherwise
    Y = model1.addVars([(f, p) for f in range(len(F)) for p in range(len(P[f]))], vtype=gb.GRB.BINARY)
    # H[i] : the number of passengers travelling in itinerary i
    H = model1.addVars([i for i in range(len(I))], vtype=gb.GRB.INTEGER, lb=0)

    # (1) OBJECTIVE FUNCTION
    model1.setObjective(
        ((gb.quicksum((Fare[i] * H[i]) for i in range(len(I)))) - (
            gb.quicksum((gb.quicksum((C[r] * X[a, r]) for r in range(len(R[a]))) for a in range(len(A)))))))

    # CONSTRAINTS
    # (2) ensure that every flight is assigned to an aircraft
    for f in range(len(F)):
        for p in range(len(P[f])):
            model1.addConstr(
                gb.quicksum(
                    (gb.quicksum(Θ1[f][p][R[a][r]] * X[a, r] for r in range(len(R[a])))) for a in range(len(A))) ==
                Y[f, p])
    # (3) ensure that exactly one flight copy will be selected for each flight
    for f in range(len(F)):
        model1.addConstr(gb.quicksum(Y[f, p] for p in range(len(P[f]))) == 1)
    # (4) ensure that every aircraft takes at most one route
    for a in range(len(A)):
        model1.addConstr(gb.quicksum(X[a, r] for r in range(len(R[a]))) <= 1)
    # (5) limit the number of passengers taken on itineraries to the forecast demand
    for i in range(len(I)):
        model1.addConstr(H[i] <= D[i])
    # (6) limit the number of passengers taken on itineraries to the number of available aircraft seats
    for f in range(len(F)):
        model1.addConstr(gb.quicksum((Θ2[i][f] * H[i]) for i in range(len(I))) <=
                         gb.quicksum((Cap[a] * gb.quicksum(
                             (gb.quicksum((Θ1[f][p][R[a][r]] * X[a, r]) for p in range(len(P[f])))) for r in
                             range(len(R[a])))) for a in range(len(A))))
    # (7) impose nonlinear restrictions on one-stop itineraries in terms of feasible connection
    # after re-timing (i.e. enough connection time is left for passenger connection)
    for i in IC_it:
        for fm in range(len(F)):
            for fn in range(len(F)):
                if fm != fn and Θ2[i][fm] == 1 and Θ2[i][fn] == 1:
                    model1.addConstr(H[i] <= D[i] * gb.quicksum(
                        (gb.quicksum(Y[fm, pm] * Y[fn, pn] for pn in range(len(P[fn])))) for pm in range(len(P[fm]))))

    model1.optimize()
    end = time.perf_counter()
    obj_value1 = model1.getObjective().getValue()
    res_list.append(str("{:e}".format(obj_value1)))
    time_list.append(end-start)

    routes_solution1 = list()
    for a in range(len(A)):
        for r in range(len(R[a])):
            if X[a, r].x == 1:
                routes_solution1.append(R3[R[a][r]])

    # MODEL 1
    start = time.perf_counter()
    model1 = gb.Model()
    model1.modelSense = gb.GRB.MAXIMIZE

    # DECISION VARIABLES
    # X[a,r] : 1 if aircraft a flies route r, and 0 otherwise
    X = model1.addVars([(a, r) for a in range(len(A)) for r in range(len(R[a]))], vtype=gb.GRB.BINARY)
    # Y[f,p] : 1 if flight copy p of flight f is selected, and 0 otherwise
    Y = model1.addVars([(f, p) for f in range(len(F)) for p in range(len(P[f]))], vtype=gb.GRB.BINARY)
    # W[f1,p1,f2,p2] : 1 if flight copy pair (f1p1,f2,p2)is selected, 0 otherwise
    W = model1.addVars([(f1, p1, f2, p2) for f1 in range(len(F)) for p1 in range(len(P[f1]))
                        for f2 in range(len(F)) for p2 in range(len(P[f2]))], vtype=gb.GRB.BINARY)
    # H[i] : the number of passengers travelling in itinerary i
    H = model1.addVars([i for i in range(len(I))], vtype=gb.GRB.INTEGER, lb=0)

    # (1) OBJECTIVE FUNCTION
    model1.setObjective(
        ((gb.quicksum((Fare[i] * H[i]) for i in range(len(I)))) - (
            gb.quicksum((gb.quicksum((C[r] * X[a, r]) for r in range(len(R[a]))) for a in range(len(A)))))))

    # CONSTRAINTS
    # (2) ensure that every flight is assigned to an aircraft
    for f in range(len(F)):
        for p in range(len(P[f])):
            model1.addConstr(gb.quicksum(
                (gb.quicksum(Θ1[f][p][R[a][r]] * X[a, r] for r in range(len(R[a])))) for a in range(len(A))) == Y[f, p])
    # (3) ensure that exactly one flight copy will be selected for each flight
    for f in range(len(F)):
        model1.addConstr(gb.quicksum(Y[f, p] for p in range(len(P[f]))) == 1)
    # (4) ensure that every aircraft takes at most one route
    for a in range(len(A)):
        model1.addConstr(gb.quicksum(X[a, r] for r in range(len(R[a]))) <= 1)
    # (5) limit the number of passengers taken on itineraries to the forecast demand
    for i in range(len(I)):
        model1.addConstr(H[i] <= D[i])
    # (6) limit the number of passengers taken on itineraries to the number of available aircraft seats
    for f in range(len(F)):
        model1.addConstr(gb.quicksum((Θ2[i][f] * H[i]) for i in range(len(I))) <=
                         gb.quicksum((Cap[a] * gb.quicksum(
                             (gb.quicksum((Θ1[f][p][R[a][r]] * X[a, r]) for p in range(len(P[f])))) for r in
                             range(len(R[a])))) for a in range(len(A))))
    # (11)-(14) linearize the constraint 7
    # (11)
    for i in range(len(FI)):
        for fm in FI[i]:
            for fn in FI[i]:
                if Θ2[i][airline.nid_index_dict[fm]] == 1 and Θ2[i][airline.nid_index_dict[fn]] == 1:
                    model1.addConstr(H[i] <= D[i] * gb.quicksum((gb.quicksum(
                        γ[i][FI[i].index(fm)][pm][FI[i].index(fn)][pn] * W[
                            airline.nid_index_dict[fm], pm, airline.nid_index_dict[fn], pn] for pn in
                        range(len(P[airline.nid_index_dict[fn]]))) for pm in
                        range(len(P[airline.nid_index_dict[fm]])))))
    # (12)
    for i in range(len(I)):
        for fm in range(len(FI[i])):
            for fn in range(len(FI[i])):
                for pm in range(len(P[fm])):
                    for pn in range(len(P[fn])):
                        model1.addConstr(W[fm, pm, fn, pn] <= Y[fm, pm])
    # (13)
    for i in range(len(I)):
        for fm in range(len(FI[i])):
            for fn in range(len(FI[i])):
                for pm in range(len(P[fm])):
                    for pn in range(len(P[fn])):
                        model1.addConstr(W[fm, pm, fn, pn] <= Y[fn, pn])
    # (14)
    for i in range(len(I)):
        for fm in range(len(FI[i])):
            for fn in range(len(FI[i])):
                for pm in range(len(P[fm])):
                    for pn in range(len(P[fn])):
                        model1.addConstr(W[fm, pm, fn, pn] >= Y[fm, pm] + Y[fn, pn] - 1)

    model1.optimize()
    end = time.perf_counter()
    obj_value2 = model1.getObjective().getValue()
    res_list.append(str("{:e}".format(obj_value2)))
    time_list.append(end-start)

    # MODEL 2
    start = time.perf_counter()
    model2 = gb.Model()
    model2.modelSense = gb.GRB.MAXIMIZE

    # DECISION VARIABLES
    # X[a,r] : 1 if aircraft a flies route r, and 0 otherwise
    X = model2.addVars([(a, r) for a in range(len(A)) for r in range(len(R[a]))], vtype=gb.GRB.BINARY)
    # Y[f,p] : 1 if flight copy p of flight f is selected, and 0 otherwise
    Y = model2.addVars([(f, p) for f in range(len(F)) for p in range(len(P[f]))], vtype=gb.GRB.BINARY)
    # Z[i] : 1 if itinerary i is selected for inclusion, and 0 otherwise
    Z = model2.addVars([i for i in range(len(I))], vtype=gb.GRB.BINARY)
    # H[i] : the number of passengers travelling in itinerary i
    H = model2.addVars([i for i in range(len(I))], vtype=gb.GRB.INTEGER, lb=0)
    # T[i,j] : the number of passengers requesting itinerary i that the airline attempts to redirect to itinerary j
    T = model2.addVars([(i, j) for i in range(len(I)) for j in range(len(I))], vtype=gb.GRB.INTEGER, lb=0)
    # EDT[f] : the expected departure time of flight f under expected propagated delays
    EDT = model2.addVars([f for f in range(len(F))], vtype=gb.GRB.INTEGER, lb=0)
    # TF[i] : 1 if the two connecting flights of itinerary i are operated by the same aircraft (i.e. through flight), and 0 otherwise
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
                gb.quicksum(
                    (gb.quicksum(Θ1[f][p][R[a][r]] * X[a, r] for r in range(len(R[a])))) for a in range(len(A))) ==
                Y[f, p])
    # (4) ensure that every aircraft takes at most one route
    for a in range(len(A)):
        model2.addConstr(gb.quicksum(X[a, r] for r in range(len(R[a]))) <= 1)
    # (17) flight cover constraint for mandatory flights
    for f in FM:
        model2.addConstr(
            gb.quicksum(Y[airline.nid_index_dict[f], p] for p in range(len(P[airline.nid_index_dict[f]]))) == 1)
    # (18) flight cover constraint for optional flights
    for f in FO:
        model2.addConstr(
            gb.quicksum(Y[airline.nid_index_dict[f], p] for p in range(len(P[airline.nid_index_dict[f]]))) <= 1)
    # (19) computation of expected flight departure time under propagated delays and re-timing decisions
    for f in range(len(F)):
        model2.addConstr(EDT[f] == dateCoding(STD[f]) +
                         gb.quicksum(
                             (gb.quicksum((dev[r][f] * X[a, r]) for r in range(len(R[a])))) for a in range(len(A)))
                         )
    # (20) restrict the number of passengers spilled from an itinerary to be no more than the demand of that itinerary
    for i in range(len(I)):
        model2.addConstr(H[i] <= D[i] - gb.quicksum(((T[i, j] - B[i][j] * T[j, i])) for j in IR[i]))
    # (21) ensure that if an optional flight is not executed, all itineraries containing this flight will not be served as well
    for i in range(len(I)):
        for f in FIO[i]:
            model2.addConstr(
                Z[i] <= gb.quicksum(
                    (Y[airline.nid_index_dict[f], p]) for p in range(len(P[airline.nid_index_dict[f]]))))
    # (22)
    for i in range(len(IC)):
        model2.addConstr(TF[i] == gb.quicksum(
            (gb.quicksum((Θ3[i][R[a][r]] * X[a, r]) for r in range(len(R[a])))) for a in range(len(A))))
    # (23) require that the connection time of every one-stop itinerary must be no less than the minimum passenger connection time
    for i in range(len(IC)):
        f1 = airline.nid_index_dict[IC[i][0]]
        f2 = airline.nid_index_dict[IC[i][1]]
        model2.addConstr(EDT[f2] - EDT[f1] - FT[f1] >=
                         (-MPT + MTT) * TF[i] + MPT * Z[IC_it[i]] - M * (1 - Z[IC_it[i]]))
    # (24) ensure that the number of passengers flown does not exceed the aircraft capacity
    for f in range(len(F)):
        model2.addConstr(gb.quicksum((Θ2[i][f] * H[i]) for i in range(len(I))) <=
                         gb.quicksum((Cap[a] * gb.quicksum(
                             (gb.quicksum((Θ1[f][p][R[a][r]] * X[a, r]) for p in range(len(P[f])))) for r in
                             range(len(R[a])))) for a in range(len(A))))
    # (25) assert that no passenger is served on an inactivated itinerary
    for i in range(len(I)):
        model2.addConstr(H[i] <= DI[i] * Z[i])
    # (30) number of passengers redirect from itinerary i to j must be less or equal than the demand forecast for passenger itinerary i
    for i in range(len(I)):
        for j in range(len(IR[i])):
            model2.addConstr(T[i, j] <= D[i])

    model2.optimize()
    end = time.perf_counter()
    obj_value3 = model2.getObjective().getValue()
    res_list.append(str("{:e}".format(obj_value3)))
    time_list.append(end-start)

    vns = VNS(airline)
    start = time.perf_counter()
    sol, obj_value4 = vns.search(10)
    end = time.perf_counter()
    res_list.append(str("{:e}".format(obj_value4)))
    time_list.append(end-start)

    gap = 1 - obj_value4/obj_value3
    res_list.append(gap)

    df_results.loc[len(df_results)] = res_list
    df_time.loc[len(df_time)] = time_list

df_results.to_csv('Results/results.csv')
df_time.to_csv('Results/times.csv')

