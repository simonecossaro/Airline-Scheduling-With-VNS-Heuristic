import pandas as pd
import AircraftsUtilities as aut

class Evaluator:
    def __init__(self,airline):
        self.airline = airline
        
    def evaluate(self,P):
        flights_selected = list()
        for r in P:
            for f in r:
                if (not(f in flights_selected)):
                    flights_selected.append(f)     
        itineraries_selected = list()
        for i in range(len(self.airline.FI)):
            if (all(f in flights_selected for f in self.airline.FI[i])):
                itineraries_selected.append(i)
        flight_index_ev_dict = dict()
        index_flight_ev_dict = dict()
        c = 0
        for f in flights_selected:
            flight_index_ev_dict[f] = c
            index_flight_ev_dict[c] = f
            c +=1   
        itinerary_index_ev_dict = dict()
        index_itinerary_ev_dict = dict()
        c = 0
        for i in itineraries_selected:
            itinerary_index_ev_dict[i] = c
            index_itinerary_ev_dict[c] = i
            c +=1
        fare = list()
        for i in itineraries_selected:
            fare.append(self.airline.Fare[i]) 
        direct_it = pd.DataFrame(columns=['n_dit','fare_d'])
        onestop_it = pd.DataFrame(columns=['n_osit','fare_os'])
        for i in range(len(fare)):
            if (len(self.airline.FI[itineraries_selected[i]])==1):
                direct_it.loc[len(direct_it)]= [i,fare[i]]
            elif(len(self.airline.FI[itineraries_selected[i]])==2):
                onestop_it.loc[len(onestop_it)]= [i,fare[i]]
        direct_it_ord = direct_it.sort_values('fare_d',ascending=False)
        onestop_it_ord = onestop_it.sort_values('fare_os',ascending=False)
        b = list()
        for i in itineraries_selected:
            list1 = list()
            for j in itineraries_selected:
                list1.append(self.airline.B[i][j])
            b.append(list1)   
        di = list()
        for i in itineraries_selected:
            di.append(self.airline.DI[i])
        H = np.zeros(len(itineraries_selected))
        remain = list()
        for f in flights_selected:
            remain.append(aut.get_number_seats(self.airline.flights[self.airline.flights.nid ==f].iloc[0,13]))
        #step1
        for i in range(len(direct_it_ord)):
            flow = min(di[int(direct_it_ord.iloc[i,0])],remain[flight_index_ev_dict[self.airline.FI[itineraries_selected[int(direct_it_ord.iloc[i,0])]][0]]])
            H[int(direct_it_ord.iloc[i,0])] = flow
            remain[flight_index_ev_dict[self.airline.FI[itineraries_selected[int(direct_it_ord.iloc[i,0])]][0]]] -= flow
        #step2
        for i in range(len(onestop_it_ord)):
            f1 = self.airline.FI[itineraries_selected[int(onestop_it_ord.iloc[i,0])]][0]
            f2 = self.airline.FI[itineraries_selected[int(onestop_it_ord.iloc[i,0])]][1]
            i1 = itinerary_index_ev_dict[flight_to_direct_itinerary(f1,itineraries_selected)]
            i2 = itinerary_index_ev_dict[flight_to_direct_itinerary(f2,itineraries_selected)]
            farei = fare[int(onestop_it_ord.iloc[i,0])]
            if (i1!= None and i2!=None):
                fare1 = fare[i1]
                fare2 = fare[i2]
                if (fare1 >= fare2):
                    fj = f1
                    fk = f2
                    j = i1
                    k = i2
                    farej = fare1
                    farek = fare2
                else:
                    fj = f2
                    fk = f1
                    j = i2
                    k = i1
                    farej = fare2
                    farek = fare1
                if ( farei >= farej + farek):
                    H[int(onestop_it_ord.iloc[i,0])] = min(remain[flight_index_ev_dict[fj]]+H[j], remain[flight_index_ev_dict[fk]]+H[k], di[int(onestop_it_ord.iloc[i,0])])
                elif( farei <= farej):
                    H[int(onestop_it_ord.iloc[i,0])] = min(remain[flight_index_ev_dict[fj]],di[int(onestop_it_ord.iloc[i,0])])
                else:
                    H[int(onestop_it_ord.iloc[i,0])] = min(remain[flight_index_ev_dict[fk]], remain[flight_index_ev_dict[fj]]+H[j], remain[flight_index_ev_dict[fk]]+H[k],di[int(onestop_it_ord.iloc[i,0])])
                if (H[int(onestop_it_ord.iloc[i,0])] > H[j]):
                    remain[flight_index_ev_dict[fj]] -= (H[int(onestop_it_ord.iloc[i,0])] - H[j])
                if (H[int(onestop_it_ord.iloc[i,0])] > H[k]):
                    remain[flight_index_ev_dict[fk]] -= (H[int(onestop_it_ord.iloc[i,0])] - H[k])
        #step3
        onestop_it_maxfareij = pd.DataFrame(columns=['n_osit','max_fare_os','j_max_os'])
        for i in range(len(onestop_it)):
            max_fare, j_max = calc_max_fare_ij(onestop_it.iloc[i,0],itineraries_selected,fare,b)
            onestop_it_maxfareij.loc[i] = [onestop_it.iloc[i,0],max_fare,j_max]
        onestop_it_maxfareij_ord = onestop_it_maxfareij.sort_values('max_fare_os',ascending=False)
        for i in range(len(onestop_it_maxfareij_ord)):
            if (onestop_it_maxfareij_ord.iloc[i,1] > 0):
                fj = self.airline.FI[itineraries_selected[int(onestop_it_ord.iloc[i,0])]][0]
                fk = self.airline.FI[itineraries_selected[int(onestop_it_ord.iloc[i,0])]][1]
                j = flight_to_direct_itinerary(fj,itineraries_selected)
                k = flight_to_direct_itinerary(fk,itineraries_selected)
                flow = min(remain[flight_index_ev_dict[fj]]+H[j], remain[flight_index_ev_dict[fk]]+H[k], di[int(onestop_it_ord.iloc[i,2])])
                H[int(onestop_it_ord.iloc[i,2])] += flow
                H[int(onestop_it_ord.iloc[i,0])] -= flow
            else:
                H[int(onestop_it_ord.iloc[i,0])] = di[int(onestop_it_ord.iloc[i,0])]
        #step4
        direct_it_maxfareij = pd.DataFrame(columns=['n_dit','max_fare_d','j_max_d'])
        for i in range(len(direct_it)):
            max_fare, j_max = calc_max_fare_ij(direct_it.iloc[i,0],itineraries_selected,fare,b)
            direct_it_maxfareij.loc[i] = [direct_it.iloc[i,0],max_fare,j_max]
        direct_it_maxfareij_ord = direct_it_maxfareij.sort_values('max_fare_d',ascending=False)
        for i in range(len(direct_it_maxfareij_ord)):
            if (direct_it_maxfare_ij_ord.iloc[i,1] > 0):
                fj = self.airline.FI[itineraries_selected[int(direct_it_ord.iloc[i,0])]][0]
                fk = self.airline.FI[itineraries_selected[int(direct_it_ord.iloc[i,0])]][1]
                j = flight_to_direct_itinerary(fj,itineraries_selected)
                k = flight_to_direct_itinerary(fk,itineraries_selected)
                flow = min(remain[flight_index_ev_dict[fj]]+H[j], remain[flight_index_ev_dict[fk]]+H[k], di[int(direct_it_ord.iloc[i,2])])
                H[direct_it_ord.iloc[i,2]] += flow
                H[int(direct_it_ord.iloc[i,0])] -= flow
            else:
                H[int(direct_it_ord.iloc[i,0])] = di[int(direct_it_ord.iloc[i,0])]
        #revenue calculation
        return gb.quicksum( fare[i]*H[i] for i in range(len(fare))).getValue()
    
    def flight_to_direct_itinerary(self,flight,itineraries):
        flight_origin = self.airline.flights[self.airline.flights.nid == flight].iloc[0,7]
        flight_dest = self.airline.flights[self.airline.flights.nid == flight].iloc[0,8]
        for i in range(len(self.airline.itineraries)):
            if (len(self.airline.itineraries[i]) == 2 and self.airline.itineraries[i][0] == flight_origin and 
                self.airline.itineraries[i][1] == flight_dest and (i in itineraries)):
                return i
        
    def calc_max_fare_ij(itinerary,itineraries,fare,b):
        max_fare = 0
        j_max = 0
        for j in range(len(itineraries)):
            obj = fare[j]*b[int(itinerary)][j] - fare[int(itinerary)]
            if(obj > max_fare):
                max_fare = obj
                j_max = j
        return max_fare, j_max
