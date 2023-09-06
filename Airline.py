import pandas as pd
import random 
import networkx as nx
import numpy as np
import AircraftsUtilities as aut

flights = pd.read_csv('flight_schedules.csv').iloc[:,1:]
aircraft_types = flights['aircraft_type'].unique()
aircraft_clusters = pd.read_csv('aircraftClustering.csv')
cluster_seat = pd.read_csv('aircraftSeats.csv')

class Airline:
    def __init__(self,name):
        self.name = name
        self.flights,self.nf,self.nid_index_dict,self.index_nid_dict = self.getFlights()
        self.flights_copies = self.getFlightsCopies()
        self.P = self.getP()
        self.itineraries,self.FI = self.getItineraries()
        self.IR = self.getIR()
        self.routes = self.getRoutes()
        self.F = self.flights.iloc[:,0]
        self.R, self.R3 = self.getR()
        self.IC = self.getIC()
        
        self.Fare = self.getFare()
        self.B = self.getB()
        self.DI = self.getDI()
        self.dev = self.get_dev()
        
        
    def getFlights(self):
        airline_flights = flights[flights.airline==self.name]
        airline_flights = airline_flights.reset_index().iloc[:,1:]
        nf = len(airline_flights)
        nid_index_dict = dict()
        index_nid_dict = dict()
        for i in range(nf):
            nid_index_dict[airline_flights.iloc[i,0]] = i
            index_nid_dict[i] = airline_flights.iloc[i,0]
        mandatory = list()
        for f in range(len(airline_flights)):
            if (random.random() > 0.90):
                mandatory.append(0)
            else:
                mandatory.append(1)
        airline_flights['mandatory'] = mandatory
        total_flights = pd.DataFrame(columns=airline_flights.columns)
        for i in range(nf):
            total_flights.loc[len(total_flights)] = airline_flights.iloc[i,:]
        counter = 1001
        for i in range(nf):
            x = airline_flights.iloc[i,:]
            x['nid']= counter
            counter += 1
            x['sobt']= pd.to_datetime(x['sobt']) + pd.Timedelta(10,'m')
            x['sibt']= pd.to_datetime(x['sibt']) + pd.Timedelta(10,'m')
            total_flights.loc[len(total_flights)] = x
            y = airline_flights.iloc[i,:]
            y['nid']= counter
            counter += 1
            y['sobt']= pd.to_datetime(y['sobt']) - pd.Timedelta(10,'m')
            y['sibt']= pd.to_datetime(y['sibt']) - pd.Timedelta(10,'m')
            total_flights.loc[len(total_flights)] = y
        total_flights = total_flights.reset_index().iloc[:,1:]
        for i in range(nf,len(total_flights)):
            nid_index_dict[total_flights.iloc[i,0]] = i
            index_nid_dict[i] = total_flights.iloc[i,0]
        return total_flights, nf, nid_index_dict, index_nid_dict
    
    def getFlightsCopies(self):
        flights_copies = list()
        counter = 1001
        for i in range(self.nf):
            list1 = list()
            list1.append(self.flights.iloc[i,0])
            list1.append(counter)
            counter += 1
            list1.append(counter)
            counter += 1
            flights_copies.append(list1)
        return flights_copies

    def getP(self):
        P = list()
        for i in range(3):
            for f in self.flights_copies:
                P.append(f)
        return P
    
    def getItineraries(self):
        G = nx.MultiDiGraph()
        for f in range(self.nf):
            G.add_edge(self.flights.iloc[f,7],self.flights.iloc[f,8],flight=self.flights.iloc[f,0])
        itineraries = list()
        for n1 in G.nodes():
            for n2 in G.neighbors(n1):
                itineraries.append([n1,n2])
        n_dir = len(itineraries)
        for n1 in G.nodes():
            for n2 in G.neighbors(n1):
                for n3 in G.neighbors(n2):
                    for e1 in range(len(G[n1][n2])):
                        for e2 in range(len(G[n2][n3])):
                            if ((n1!=n3) and pd.to_datetime(self.flights.iloc[self.nid_index_dict[G[n2][n3][e2]['flight']],11])-pd.to_datetime(self.flights.iloc[self.nid_index_dict[G[n1][n2][e1]['flight']],12]) > pd.Timedelta(30, "m")
                               and pd.to_datetime(self.flights.iloc[self.nid_index_dict[G[n2][n3][e2]['flight']],11])-pd.to_datetime(self.flights.iloc[self.nid_index_dict[G[n1][n2][e1]['flight']],12]) < pd.Timedelta(3, "h")):
                                if (not([n1,n2,n3] in itineraries)):
                                    itineraries.append([n1,n2,n3])
        n_it = len(itineraries)
        n_os = n_it - n_dir
        direct_itineraries = list()
        one_stop_itineraries = list()
        for i in itineraries:
            if (len(i)==2):
                direct_itineraries.append(i)
            elif(len(i)==3):
                one_stop_itineraries.append(i)
        flights_itineraries = list()
        for i in direct_itineraries:
            flights_direct = self.flights[self.flights['origin']== i[0]]
            flight = flights_direct[flights_direct['destination']== i[1]].iloc[0,0]
            flights_itineraries.append(list([flight]))
        for i in one_stop_itineraries:
            flights_itineraries.append(self.find_flights_itineraries(i))
        I = list()
        for i in itineraries:
            I.append(i)
        FI = list()
        for i in flights_itineraries:
            FI.append(i)
        for i in range(n_dir):
            I.append(itineraries[i])
            FI.append(list([self.flights_copies[self.nid_index_dict[FI[i][0]]][1]]))
        for i in range(n_dir):
            I.append(itineraries[i])
            FI.append(list([self.flights_copies[self.nid_index_dict[FI[i][0]]][2]]))
        for i in range(n_dir,n_it):
            for p1 in self.flights_copies[self.nid_index_dict[FI[i][0]]]:
                for p2 in self.flights_copies[self.nid_index_dict[FI[i][1]]]:
                    if (p1!= FI[i][0] or p2!= FI[i][1]):
                        I.append(itineraries[i])
                        FI.append(list([p1,p2]))
        return I, FI
    
    def getIR(self):
        IR = list()
        for i in range(len(self.itineraries)):
            list1 = list()
            for j in range(len(self.itineraries)):
                if (i!=j and self.canBeRedirect(i,j)):
                    list1.append(j)
            IR.append(list1)
        return IR

    def getIC(self):
        IC = list()
        for i in self.FI:
            if (len(i)==2):
                IC.append(i)
        return IC
    
    def getICit(self):
        IC_it = list()
        for i in range(len(self.itineraries)):
            if (len(self.itineraries[i])==3):
                IC_it.append(i)
        return IC_it

    def getFM(self):
        return self.flights[self.flights.mandatory == 1].iloc[:,0]

    def getFO(self):
        return self.flights[self.flights.mandatory == 0].iloc[:,0]

    def getFIO(self):
        FIO = list()
        for i in range(len(self.FI)):
            list1 = list()
            for f in self.FI[i]:
                if(self.flights.iloc[self.nid_index_dict[f],23] == 0):
                    list1.append(f)
            FIO.append(list1)
        return FIO

    def getA(self):
        A = list()
        for i in range(1,len(self.routes)+1):
            if (i<10):
                s = "00" + str(i)
            if (i>= 10 and i<100):
                s = "0" + str(i)
            if (i>=100):
                s = str(i)
            A.append(self.name + s)
        return A

    def getR(self):
        R2 = list()
        for r in self.routes:
            list1 = list()
            list1.append(list(r))
            for f in r:
                for p in self.flights_copies[self.nid_index_dict[f]]:
                    list2 = list(r)
                    list2 = self.substitution_in_list(list2,f,p)
                    if (list2 != list(r)):
                        list1.append(list2)
            R2.append(list1)          
        R = list()
        counter = 0
        for i in range(len(R2)):
            list1 = list()
            for j in range(len(R2[i])):
                list1.append(counter)
                counter+=1
            R.append(list1)
        R3 = list()
        for i in range(len(R2)):
            for j in range(len(R2[i])):
                R3.append(R2[i][j])
        return R,R3
    
    
    def getFare(self):
        Fare = list()
        for i in self.FI:
            Fare.append(self.fare_for_itinerary(i))
        return Fare


    def getD(self):
        D = list()
        for i in range(len(self.FI)):
            D.append(self.find_min_pax(self.FI[i]))
        return(D)
    
    def getDI(self):
        DI = list()
        for i in range(len(self.FI)):
            DI.append(self.find_min_cap(self.FI[i]))
        return DI

    def getC(self):
        C = list()
        for i in range(len(self.R3)):
            C.append(self.calc_route_cost(self.R3[i]))
        return C

    def getFT(self):
        FT = list()
        for i in range(len(self.F)):
            dep = pd.to_datetime(self.flights['sobt']).iloc[i]
            arr = pd.to_datetime(self.flights['sibt']).iloc[i]
            time = arr - dep
            FT.append(self.calc_minutes(time))
        return FT

    def getΘ1(self):
        Θ1 = list()
        for i in range(len(self.flights)):
            list1 = list()
            for p in self.P[i]:
                list2 = list()
                for j in range(len(self.R3)):
                    if (p in self.R3[j]):
                        list2.append(1)
                    else:
                        list2.append(0)
                list1.append(list2)
            Θ1.append(list1)
        return Θ1

    def getΘ2(self):
        Θ2 = list()
        for i in self.FI:
            list1 = np.zeros(len(self.flights))
            for f in i:
                list1[self.nid_index_dict[f]] = 1
            Θ2.append(list1)
        return Θ2

    def getΘ3(self):
        Θ3 = list()
        for i in self.FI:
            list1 = list()
            for j in range(len(self.R3)):
                if (all(flight in self.R3[j] for flight in i)):
                    list1.append(1)
                else:
                    list1.append(0)
            Θ3.append(list1)
        return Θ3

    def getγ(self):
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
                            if (f1 == f2 or self.existICbetween(f1,p1,f2,p2)):
                                list4.append(1)
                            else:
                                list4.append(0)
                        list3.append(list4)
                    list2.append(list3)
                list1.append(list2)        
            γ.append(list1)
        return γ
    
    def getB(self):
        B = list()
        for i in range(len(self.itineraries)):
            list1 = np.zeros(len(self.itineraries))
            rate_max = 0.4
            for j in self.IR[i]:
                if (rate_max == 0):
                    break
                else:
                    r = random.randint(0,5)/100
                    if (rate_max > r):
                        list1[int(j)] = r
                        rate_max -= r
                    else:
                        list1[int(j)] = rate_max
                        rate_max = 0
            B.append(list1)
        return B

    def get_dev(self):
        dev = list()
        for r in range(len(self.R3)):
            list1 = list()
            for f in range(len(self.F)):
                if (self.P[f][0] in self.R3[r]):
                    list1.append(random.randint(1,10))
                else:
                    list1.append(0)
            dev.append(list1)
        return dev

    def getRoutes(self):
        flights_nid = list(self.flights.iloc[:self.nf,:]['nid'])
        G = nx.Graph()
        G.add_nodes_from(self.flights.iloc[:self.nf,:]['nid'])
        for i in range(self.nf):
            if (pd.notnull(self.flights.iloc[i,21]) and (self.flights.iloc[i,21] in flights_nid)):
                G.add_edge(self.flights.iloc[i,21], self.flights.iloc[i,0])
        aircraft_routes = list()
        for i in nx.connected_components(G):
            aircraft_routes.append(list(i))
        return aircraft_routes

    def getEPD(self):
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
    
    def getCap(self):
        Cap = list()
        for a in aircraft_types:
            Cap.append(aut.get_number_seats(a))
        return Cap
        
    def find_flights_itineraries(self,itinerary):
        flights1 = self.flights[self.flights['origin']== itinerary[0]]
        flight1 = flights1[flights1['destination']== itinerary[1]].iloc[0,0]
        flights2 = self.flights[self.flights['origin']== itinerary[1]]
        flights2 = flights2[flights2['destination']== itinerary[2]]
        for f in range(len(flights2)):
            if (pd.to_datetime(flights2.iloc[f,11])-pd.to_datetime(self.flights.iloc[self.nid_index_dict[flight1],12]) > pd.Timedelta(30, "m")):
                return list([flight1,flights2.iloc[f,0]])
    
    def fare_for_flight(self,flight_id):
        flight = self.flights[self.flights['nid']==flight_id].iloc[0,:]
        return flight['gcdistance'] / 10
    
    def fare_for_itinerary(self,itinerary):
        fare = 0
        for f in itinerary:
            fare += self.fare_for_flight(f)
        return fare
    
    def find_min_cap(self,itinerary):
        minimum = np.Inf
        for i in itinerary:
            cap = self.flights[self.flights['nid']==i].iloc[0,17]
            if (cap < minimum ):
                minimum = cap
        return minimum
    
    def canBeRedirect(self,i, j):
        dest = self.itineraries[i][-1]
        if (any((self.itineraries[i][a] in self.itineraries[j])and(dest in self.itineraries[j])
                and(self.itineraries[j].index(self.itineraries[i][a])<self.itineraries[j].index(dest))for a in range(len(self.itineraries[i])-1))):
            return True
        return False  

    def find_min_pax(self,itinerary):
        minimum = np.Inf
        for i in itinerary:
            pax = self.flights[self.flights.nid==i].iloc[0,18]
            if (pax < minimum ):
                minimum = pax
        return minimum

    def calc_route_cost(self,route):
        cost = 0
        for f in route:
            cost += self.calc_flight_cost(self.flights.iloc[self.nid_index_dict[f],:])
        return cost

    def calc_flight_cost(self,flight):
        dep = flight['sobt']
        arr = flight['sibt']
        dep = pd.to_datetime(str(dep))
        arr = pd.to_datetime(str(arr))
        return self.calc_minutes(arr-dep) * 2000/60
    
    def calc_minutes(self,date):
        h = str(date)[7:9]
        m = str(date)[10:12]
        return int(m)+int(h)*60

    def existICbetween(self,f1,p1,f2,p2):
        for i in self.IC:
            if (((i[0] == f1)or(i[0]==p1)) and ((i[1] == f2)or(i[1] == p2))):
                return True
        return False

    def substitution_in_list(self,r,f,p):
        index = len(r)+1
        for i in range(len(r)):
            if (r[i] == f):
                index = i
                break
        r[index] = p
        return r
