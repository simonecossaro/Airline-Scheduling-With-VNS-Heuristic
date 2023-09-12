from Airline import Airline
from VNS.VNS import VNS
import time
import pandas as pd
import airline_utilities as aut
import warnings
warnings.filterwarnings('ignore')

# setting parameters
thy_flights = pd.read_csv('Big Airline Models/THY_data/THY_flights.csv').iloc[:,1:]
I = aut.dataframe_to_list_without_nan(pd.read_csv('Big Airline Models/THY_data/THY_itineraries.csv').iloc[:,1:])
FI = aut.dataframe_to_list_without_nan(pd.read_csv('Big Airline Models/THY_data/THY_FI.csv').iloc[:,1:])
IR = aut.dataframe_to_list_without_nan(pd.read_csv('Big Airline Models/THY_data/THY_IR.csv').iloc[:,1:])
D = aut.dataframe_to_list(pd.read_csv('Big Airline Models/THY_data/THY_D.csv').iloc[:,1:])
Fare = aut.dataframe_to_list(pd.read_csv('Big Airline Models/THY_data/THY_Fare.csv').iloc[:,1:])
routes = aut.dataframe_to_list_without_nan(pd.read_csv('Big Airline Models/THY_data/THY_routes.csv').iloc[:,1:])
# creation of airline
big_airline = Airline.get_airline(thy_flights,I,FI,routes,IR,D,Fare)
big_airline.name = 'THY'
# vns search
vns = VNS(big_airline)
start = time.perf_counter()
sol, obj_value = vns.search(10)
end = time.perf_counter()

print('Solution aircraft routing problem: ')
print(sol)
print('Revenue(objective function value): ' + str("{:e}".format(obj_value)))
print('Task time: ' + str(end - start) + ' s')
