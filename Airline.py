import pandas as pd
import random
import networkx as nx
import numpy as np
import airline_utilities as aut

flights = pd.read_csv('flight_schedules.csv').iloc[:, 1:]


class Airline:
    def __init__(self, name):
        self.name = name
        self.flights = self.get_flights()
        self.nid_index_dict = aut.nid_index_dict_func(self.flights)
        self.index_nid_dict = aut.index_nid_dict_func(self.flights)
        self.P = self.get_flights_copies()
        self.itineraries, self.FI = self.get_itineraries()
        self.IR = self.get_ir()
        self.routes = self.get_routes()
        self.F = self.flights.iloc[:, 0]
        self.R, self.R3 = self.get_r()
        self.IC = self.get_ic()
        self.Fare = self.get_fare()
        self.B = self.get_b()
        self.D = self.get_d()
        self.DI = self.get_di()
        self.dev = self.get_dev()

    def get_flights(self):
        airline_flights = flights[flights.airline == self.name]
        airline_flights = airline_flights.reset_index().iloc[:, 1:]
        mandatory = list()
        for f in range(len(airline_flights)):
            if random.random() > 0.90:
                mandatory.append(0)
            else:
                mandatory.append(1)
        airline_flights['mandatory'] = mandatory
        return airline_flights

    def get_flights_copies(self):
        flights_copies = list()
        counter = 10001
        for i in range(len(self.flights)):
            list1 = list()
            list1.append(self.flights.iloc[i, 0])
            list1.append(counter)
            counter += 1
            list1.append(counter)
            counter += 1
            flights_copies.append(list1)
        return flights_copies

    def get_itineraries(self):
        G = nx.MultiDiGraph()
        for f in range(len(self.flights)):
            G.add_edge(self.flights.iloc[f, 7], self.flights.iloc[f, 8], flight=self.flights.iloc[f, 0])
        itineraries = list()
        for n1 in G.nodes():
            for n2 in G.neighbors(n1):
                itineraries.append([n1, n2])
        for n1 in G.nodes():
            for n2 in G.neighbors(n1):
                for n3 in G.neighbors(n2):
                    for e1 in range(len(G[n1][n2])):
                        for e2 in range(len(G[n2][n3])):
                            if ((n1 != n3) and pd.to_datetime(self.flights.iloc[self.nid_index_dict[
                                G[n2][n3][e2]['flight']], 11]) - pd.to_datetime(
                                self.flights.iloc[self.nid_index_dict[G[n1][n2][e1]['flight']], 12]) > pd.Timedelta(
                                30, "m")
                                    and pd.to_datetime(self.flights.iloc[self.nid_index_dict[
                                        G[n2][n3][e2]['flight']], 11]) - pd.to_datetime(self.flights.iloc[
                                                                                            self.nid_index_dict[
                                                                                                G[n1][n2][e1][
                                                                                                    'flight']], 12]) < pd.Timedelta(
                                        3, "h")):
                                if not ([n1, n2, n3] in itineraries):
                                    itineraries.append([n1, n2, n3])
        flights_itineraries = list()
        for i in itineraries:
            if len(i) == 2:
                flights_direct = self.flights[self.flights['origin'] == i[0]]
                flight = flights_direct[flights_direct['destination'] == i[1]].iloc[0, 0]
                flights_itineraries.append(list([flight]))
            elif len(i) == 3:
                flights_itineraries.append(aut.find_flights_itinerary(self.flights, i))
        return itineraries, flights_itineraries

    # returns IR, the set of itineraries where passenger spilled from one itinerary can be redirected to
    def get_ir(self):
        IR = list()
        for i in range(len(self.itineraries)):
            list1 = list()
            for j in range(len(self.itineraries)):
                if i != j and aut.can_be_redirect(self.itineraries, i, j):
                    list1.append(j)
            IR.append(list1)
        return IR

    # returns IC, the set of one-stop itineraries
    def get_ic(self):
        IC = list()
        for i in self.FI:
            if len(i) == 2:
                IC.append(i)
        return IC

    # returns the set of indexes of one-stop itineraries
    def get_ic_it(self):
        IC_it = list()
        for i in range(len(self.FI)):
            if len(self.FI[i]) == 2:
                IC_it.append(i)
        return IC_it

    # returns FM, the set of mandatory flights
    def get_fm(self):
        return self.flights[self.flights.mandatory == 1].iloc[:, 0]

    # return FO, the set of optional flights
    def get_fo(self):
        return self.flights[self.flights.mandatory == 0].iloc[:, 0]

    # returns FIO, the set of optional flights within itinerary
    def get_fio(self):
        FIO = list()
        for i in range(len(self.FI)):
            list1 = list()
            for f in self.FI[i]:
                if self.flights.iloc[self.nid_index_dict[f], 23] == 0:
                    list1.append(f)
            FIO.append(list1)
        return FIO

    # returns A, the set of aircraft
    def get_a(self):
        A = list()
        s = ""
        for i in range(1, len(self.routes) + 1):
            if i < 10:
                s = "00" + str(i)
            if 10 <= i < 100:
                s = "0" + str(i)
            if i >= 100:
                s = str(i)
            A.append(self.name + s)
        return A

    # returns the set of routes
    def get_r(self):
        R2 = list()
        for r in self.routes:
            list1 = list()
            list1.append(list(r))
            for f in r:
                for p in self.P[self.nid_index_dict[f]]:
                    list2 = list(r)
                    list2 = aut.substitution_in_list(list2, f, p)
                    if list2 != list(r):
                        list1.append(list2)
            R2.append(list1)
        R = list()
        counter = 0
        for i in range(len(R2)):
            list1 = list()
            for j in range(len(R2[i])):
                list1.append(counter)
                counter += 1
            R.append(list1)
        R3 = list()
        for i in range(len(R2)):
            for j in range(len(R2[i])):
                R3.append(R2[i][j])
        return R, R3

    def get_aircrafts_routes(self):
        R2 = list()
        for r in self.routes:
            list1 = list()
            list1.append(list(r))
            for f in r:
                for p in self.P[self.nid_index_dict[f]]:
                    list2 = list(r)
                    list2 = aut.substitution_in_list(list2, f, p)
                    if list2 != list(r):
                        list1.append(list2)
            R2.append(list1)


    # returns Fare, the set of fare for itinerary
    def get_fare(self):
        Fare = list()
        for i in self.FI:
            Fare.append(aut.fare_for_itinerary(self.flights, i))
        return Fare

    # returns D, the set of the demand forecast for passenger itinerary
    def get_d(self):
        D = list()
        for i in range(len(self.FI)):
            D.append(aut.find_min_pax(self.flights, self.FI[i]))
        return D

    # returns DI, the maximum number of passengers carried in itinerary
    def get_di(self):
        DI = list()
        for i in range(len(self.FI)):
            DI.append(aut.find_min_cap(self.flights, self.FI[i]))
        return DI

    # returns C, the set of operation and delay penalty cost of executing aircraft route
    def get_c(self):
        C = list()
        for i in range(len(self.R3)):
            C.append(aut.calc_route_cost(self.flights, self.R3[i]))
        return C

    # return FT, the set of the block time of flights
    def get_ft(self):
        FT = list()
        for i in range(len(self.F)):
            dep = pd.to_datetime(self.flights['sobt']).iloc[i]
            arr = pd.to_datetime(self.flights['sibt']).iloc[i]
            time = arr - dep
            FT.append(aut.calc_minutes(time))
        return FT

    # returns the set Θ1, Θ1[f][p][r]: 1 if flight f, copy p ∈ P is served in route r, and 0 otherwise
    def get_Θ1(self):
        Θ1 = list()
        for i in range(len(self.flights)):
            list1 = list()
            for p in self.P[i]:
                list2 = list()
                for j in range(len(self.R3)):
                    if p in self.R3[j]:
                        list2.append(1)
                    else:
                        list2.append(0)
                list1.append(list2)
            Θ1.append(list1)
        return Θ1

    # returns the set Θ2, Θ2[i][f]: 1 if itinerary i involves flight f, and 0 otherwise
    def get_Θ2(self):
        Θ2 = list()
        for i in self.FI:
            list1 = np.zeros(len(self.flights))
            for f in i:
                list1[self.nid_index_dict[f]] = 1
            Θ2.append(list1)
        return Θ2

    # return the set Θ3, Θ3[r][i]: 1 if the component flights of connecting itinerary i are executed by the same aircraft in route r, and 0 otherwise
    def get_Θ3(self):
        Θ3 = list()
        for i in self.FI:
            list1 = list()
            for j in range(len(self.R3)):
                if all(flight in self.R3[j] for flight in i):
                    list1.append(1)
                else:
                    list1.append(0)
            Θ3.append(list1)
        return Θ3

    # returns the set γ, γ[i][f1][p1][f2][p2]: 1 if itinerary i∈IC exists between flight f1, copy p1 and flight f2, copy p2
    def get_γ(self):
        γ = list()
        for i in self.FI:
            list1 = list()
            for f1 in i:
                list2 = list()
                for p1 in self.P[self.nid_index_dict[f1]]:
                    list3 = list()
                    for f2 in i:
                        list4 = list()
                        for p2 in self.P[self.nid_index_dict[f2]]:
                            if f1 == f2 or p1 == p2 or f1 == p2 or p2 == f2 or aut.exist_ic_between(self.IC, f1, p1, f2,
                                                                                                    p2):
                                list4.append(1)
                            else:
                                list4.append(0)
                        list3.append(list4)
                    list2.append(list3)
                list1.append(list2)
            γ.append(list1)
        return γ

    # returns B, B[i][j] is the recapture rate from itinerary i to itinerary j
    def get_b(self):
        B = list()
        for i in range(len(self.itineraries)):
            list1 = np.zeros(len(self.itineraries))
            rate_max = 0.4
            for j in self.IR[i]:
                if rate_max == 0:
                    break
                else:
                    r = random.randint(0, 5) / 100
                    if rate_max > r:
                        list1[int(j)] = r
                        rate_max -= r
                    else:
                        list1[int(j)] = rate_max
                        rate_max = 0
            list1[int(i)] = 1
            B.append(list1)
        return B

    # returns dev[f][r] deviation from the STD of flight f in aircraft route r
    def get_dev(self):
        dev = list()
        for r in range(len(self.R3)):
            list1 = list()
            for f in range(len(self.F)):
                if self.P[f][0] in self.R3[r]:
                    list1.append(random.randint(1, 10))
                else:
                    list1.append(0)
            dev.append(list1)
        return dev

    # returns routes
    def get_routes(self):
        flights_nid = list(self.flights['nid'])
        G = nx.Graph()
        G.add_nodes_from(flights_nid)
        for i in range(len(self.flights)):
            if pd.notnull(self.flights.iloc[i, 21]) and (self.flights.iloc[i, 21] in flights_nid):
                G.add_edge(self.flights.iloc[i, 21], self.flights.iloc[i, 0])
        aircraft_routes = list()
        for i in nx.connected_components(G):
            aircraft_routes.append(list(i))
        return aircraft_routes

    # returns EPD, EPD[r][f] the expected propagated delays of flight f in route r
    def get_epd(self):
        EPD = list()
        for r in range(len(self.R3)):
            list1 = list()
            for f in range(len(self.R3[r])):
                delay_sum = 0
                for d in range(f):
                    delay_sum += self.dev[r][f]
                list1.append(delay_sum)
            EPD.append(list1)
        return EPD

    # returns Cap, Cap[a]: the number of seats (capacity) in aircraft a
    def get_cap(self):
        Cap = list()
        for a in range(len(self.R)):
            for j in range(len(self.R3[self.R[a][0]])):
                if (self.R3[self.R[a][0]][j] > 2000):
                    Cap.append(
                        aut.get_number_seats(self.flights[self.flights.nid == self.R3[self.R[a][0]][0]].iloc[0, 13]))
                    break
        return Cap

    # method that returns an Airline object with the given parameters as fields
    @staticmethod
    def get_airline(F,I,FI,routes,IR,D,Fare):
        airline = Airline("")
        airline.flights = F
        airline.itineraries = I
        airline.FI = FI
        airline.routes = routes
        airline.IR = IR
        airline.D = D
        airline.Fare = Fare
        return airline