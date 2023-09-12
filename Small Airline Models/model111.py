import gurobipy as gb
import warnings

import pandas as pd

from Airline import Airline
warnings.filterwarnings('ignore')

small_airlines = ["KAL","AIC","TGZ","CSN","RSY","IRQ","HAY","VIM","LLC"]
results = pd.DataFrame(columns=["airline","model1"])

for small_airline in small_airlines:
    print(small_airline)
    airline = Airline(small_airline)
    # SETS
    # I set of passenger itineraries
    I = airline.itineraries
    # F set of flights
    F = airline.F
    # A set of aircraft
    A = airline.get_a()
    # IC set of one-stop itineraries, IC_it set of indexes of one-stop itineraries
    IC = airline.IC
    IC_it = airline.get_ic_it()
    # FI set of flights within itinerary
    FI = airline.FI
    # R set of aircraft routes
    R = airline.R
    # R3 set of flights within routes
    R3 = airline.R3
    # P set of flights copies
    P = airline.P

    # PARAMETERS
    # D[i]: the demand forecast for passenger itinerary i
    D = airline.get_d()
    # C[r]: the operation and delay penalty cost of executing aircraft route r
    C = airline.get_c()
    # Cap[a]: the number of seats (capacity) in aircraft a
    Cap = airline.get_cap()
    # Fare[i]: the average fare for itinerary i
    Fare = airline.Fare
    # Θ1[f][p][r]: 1 if flight f, copy p ∈ P is served in route r, and 0 otherwise
    Θ1 = airline.get_Θ1()
    # Θ2[i][f]: 1 if itinerary i involves flight f, and 0 otherwise
    Θ2 = airline.get_Θ2()
    # γ[i][f1][p1][f2][p2]: 1 if itinerary i∈IC exists between flight f1, copy p1 and flight f2, copy p2
    γ = airline.get_γ()

    # MODEL 1
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
    obj_value = model1.getObjective().getValue()
    results.loc[len(results)] = [small_airline,obj_value]

    route_solution = list()
    for a in range(len(A)):
        for r in range(len(R[a])):
            if X[a, r].x == 1:
                route_solution.append(R3[R[a][r]])
    print('Route solution:')
    print(route_solution)
    print('_______________________')

print(results)

results.to_csv('small_airlines_results.csv')
