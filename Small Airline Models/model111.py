import pandas as pd

thy_flights = pd.read_csv('Big Airline Models/THY_data/THY_flights.csv').iloc[:,1:]

for i in range(len(thy_flights)):
    num = thy_flights.iloc[i,24][3:]
    thy_flights.iloc[i,24] = "THY" + str(num)

thy_flights.to_csv("Big Airline Models/THY_data/THY_flights.csv")