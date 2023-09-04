class Airline:
    def __init__(self,name):
        self.name = name
        self.flights,self.nf,self.nid_index_dict,self.index_nid_dict = self.getFlights()
        self.flights_copies = self.getFlightsCopies()
        self.itineraries,self.FI = self.getItineraries()
        self.IR = self.getIR()
        self.Fare = self.getFare()
        self.B = self.getB()
        self.DI = self.getDI()
        
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
    
    def getFare(self):
        Fare = list()
        for i in self.FI:
            Fare.append(self.fare_for_itinerary(i))
        return Fare
    
    def getDI(self):
        DI = list()
        for i in range(len(self.FI)):
            DI.append(self.find_min_cap(self.FI[i]))
        return DI
    
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
        return flight['gcdistance'] / 5
    
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
