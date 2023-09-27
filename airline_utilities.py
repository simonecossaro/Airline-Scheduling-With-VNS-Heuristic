import pandas as pd
import numpy as np

aircraft_clusters = pd.read_csv('aircraftClustering.csv')
cluster_seat = pd.read_csv('aircraftSeats.csv')


def get_number_seats(aircraft):
    aircraft_cluster = aircraft_clusters[aircraft_clusters['AircraftType'] == aircraft]['AssignedAircraftType'].iloc[0]
    seats = cluster_seat[cluster_seat['Aircraft'] == str(aircraft_cluster)].iloc[0, 2]
    return seats


def nid_index_dict_func(flights):
    nid_index_dict = dict()
    for f in range(len(flights)):
        nid_index_dict[flights.iloc[f, 0]] = f
    return nid_index_dict


def index_nid_dict_func(flights):
    index_nid_dict = dict()
    for f in range(len(flights)):
        index_nid_dict[f] = flights.iloc[f, 0]
    return index_nid_dict


def find_flights_itinerary(flights, itinerary):
    nid_index_dict = nid_index_dict_func(flights)
    flights1 = flights[flights['origin'] == itinerary[0]]
    flight1 = flights1[flights1['destination'] == itinerary[1]].iloc[0, 0]
    flights2 = flights[flights['origin'] == itinerary[1]]
    flights2 = flights2[flights2['destination'] == itinerary[2]]
    for f in range(len(flights2)):
        if (pd.to_datetime(flights2.iloc[f, 11]) - pd.to_datetime(
                flights.iloc[nid_index_dict[flight1], 12]) > pd.Timedelta(30, "m")):
            return list([flight1, flights2.iloc[f, 0]])


def fare_for_flight(flights, flight_id):
    flight = flights[flights['nid'] == flight_id].iloc[0, :]
    return flight['gcdistance'] / 10


def fare_for_itinerary(flights, itinerary):
    fare = 0
    for f in itinerary:
        fare += fare_for_flight(flights, f)
    return fare


def find_min_cap(flights, itinerary):
    minimum = np.Inf
    for i in itinerary:
        cap = flights[flights['nid'] == i].iloc[0, 17]
        if cap < minimum:
            minimum = cap
    return minimum


def can_be_redirect(itineraries, i, j):
    dest = itineraries[i][-1]
    if (any((itineraries[i][a] in itineraries[j]) and (dest in itineraries[j])
            and (itineraries[j].index(itineraries[i][a]) < itineraries[j].index(dest)) for a in
            range(len(itineraries[i]) - 1))):
        return True
    return False


def find_min_pax(flights, itinerary):
    minimum = np.Inf
    for i in itinerary:
        pax = flights[flights.nid == i].iloc[0, 18]
        if pax < minimum:
            minimum = pax
    return minimum


def calc_route_cost(flights, route):
    nid_index_dict = nid_index_dict_func(flights)
    cost = 0
    for f in route:
        if (f > 33000):
            cost += calc_flight_cost(flights.iloc[nid_index_dict[f], :])
        else:
            cost += calc_flight_cost(flights.iloc[int((f - 10001) / 2), :])
    return cost

def calc_flight_cost(flight):
    dep = flight['sobt']
    arr = flight['sibt']
    dep = pd.to_datetime(str(dep))
    arr = pd.to_datetime(str(arr))
    return calc_minutes(arr - dep) * 2000 / 60


def calc_minutes(date):
    h = str(date)[7:9]
    m = str(date)[10:12]
    return int(m) + int(h) * 60


def exist_ic_between(ic, f1, p1, f2, p2):
    for i in ic:
        if ((i[0] == f1) or (i[0] == p1)) and ((i[1] == f2) or (i[1] == p2)):
            return True
    return False


def substitution_in_list(list, f, p):
    index = len(list) + 1
    for i in range(len(list)):
        if list[i] == f:
            index = i
            break
    list[index] = p
    return list


def flight_to_direct_itinerary(flights, flight, airline_itineraries, itineraries):
    flight_origin = flights[flights.nid == flight].iloc[0, 7]
    flight_dest = flights[flights.nid == flight].iloc[0, 8]
    for i in range(len(airline_itineraries)):
        if (len(airline_itineraries[i]) == 2 and airline_itineraries[i][0] == flight_origin and
                airline_itineraries[i][1] == flight_dest and (i in itineraries)):
            return i

def get_cap_flight(flights, flight_nid):
    return get_number_seats(flights[flights.nid == flight_nid].iloc[0,13])

def calc_max_fare_ij(itinerary, itineraries, fare, b):
    max_fare = 0
    j_max = 0
    for j in range(len(itineraries)):
        obj = fare[j] * b[int(itinerary)][j] - fare[int(itinerary)]
        if obj > max_fare:
            max_fare = obj
            j_max = j
    return max_fare, j_max

def dataframe_to_list_without_nan(dataframe):
    output = list()
    for i in range(len(dataframe)):
        list1 = list()
        for j in range(len(dataframe.iloc[0,:])):
            if(pd.notnull(dataframe.iloc[i,j])):
                list1.append(dataframe.iloc[i,j])
            else:
                break
        output.append(list1)
    return output

def dataframe_to_list(dataframe):
    output = list()
    for i in range(len(dataframe)):
        output.append(dataframe.iloc[i,0])
    return output