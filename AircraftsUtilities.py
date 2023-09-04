import pandas as pd

aircraft_clusters = pd.read_csv('aircraftClustering.csv')
cluster_seat = pd.read_csv('aircraftSeats.csv')

def get_number_seats(aircraft):
    aircraft_cluster = aircraft_clusters[aircraft_clusters['AircraftType']==aircraft]['AssignedAircraftType'].iloc[0]
    seats = cluster_seat[cluster_seat['Aircraft']==str(aircraft_cluster)].iloc[0,2]
    return seats
