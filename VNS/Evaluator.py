import pandas as pd
import airline_utilities as aut
import gurobipy as gb
import numpy as np


class Evaluator:
    def __init__(self, airline):
        self.airline = airline

    def evaluate(self, P):
        flights_selected = list()
        for r in P:
            for f in r:
                if not (f in flights_selected):
                    flights_selected.append(f)
        itineraries_selected = list()
        for i in range(len(self.airline.FI)):
            if all(f in flights_selected for f in self.airline.FI[i]):
                itineraries_selected.append(i)
        flight_index_ev_dict = dict()
        index_flight_ev_dict = dict()
        counter = 0
        for f in flights_selected:
            flight_index_ev_dict[f] = counter
            index_flight_ev_dict[counter] = f
            counter += 1
        itinerary_index_ev_dict = dict()
        index_itinerary_ev_dict = dict()
        counter = 0
        for i in itineraries_selected:
            itinerary_index_ev_dict[i] = counter
            index_itinerary_ev_dict[counter] = i
            counter += 1
        fare = list()
        for i in itineraries_selected:
            fare.append(self.airline.Fare[i])
        direct_it = pd.DataFrame(columns=['n_dit', 'fare_d'])
        onestop_it = pd.DataFrame(columns=['n_osit', 'fare_os'])
        for i in range(len(fare)):
            if len(self.airline.FI[itineraries_selected[i]]) == 1:
                direct_it.loc[len(direct_it)] = [i, fare[i]]
            elif len(self.airline.FI[itineraries_selected[i]]) == 2:
                onestop_it.loc[len(onestop_it)] = [i, fare[i]]
        direct_it_ord = direct_it.sort_values('fare_d', ascending=False)
        onestop_it_ord = onestop_it.sort_values('fare_os', ascending=False)
        d = list()
        airline_D = self.airline.get_d()
        for i in itineraries_selected:
            d.append(airline_D[i])
        H = np.zeros(len(itineraries_selected))
        cap = list()
        for f in flights_selected:
            cap.append(aut.get_cap_flight(self.airline.flights,f))
        remain = cap
        # step1
        for i in range(len(onestop_it_ord)):
            f1 = self.airline.FI[itineraries_selected[int(onestop_it_ord.iloc[i, 0])]][0]
            f2 = self.airline.FI[itineraries_selected[int(onestop_it_ord.iloc[i, 0])]][1]
            flow = min(remain[flight_index_ev_dict[f1]], remain[flight_index_ev_dict[f2]],
                       d[int(onestop_it_ord.iloc[i, 0])])
            H[int(onestop_it_ord.iloc[i, 0])] = flow
            remain[flight_index_ev_dict[f1]] -= flow
            remain[flight_index_ev_dict[f2]] -= flow
        # step2
        for i in range(len(direct_it_ord)):
            f = self.airline.FI[itineraries_selected[int(direct_it_ord.iloc[i, 0])]][0]
            flow = min(d[int(direct_it_ord.iloc[i, 0])], remain[flight_index_ev_dict[f]])
            H[int(direct_it_ord.iloc[i, 0])] = flow
            remain[flight_index_ev_dict[f]] -= flow
        costs = list()
        for r in P:
            costs.append(aut.calc_route_cost(self.airline.flights, r))
        cost = gb.quicksum(costs[r] for r in range(len(costs))).getValue()
        revenue = gb.quicksum(fare[i] * H[i] for i in range(len(fare))).getValue()
        return revenue - cost
