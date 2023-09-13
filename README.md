# Airline-Scheduling-With-VNS-Heuristic
The airline integrated robust scheduling problem integrates flight scheduling, fleet assignment and aircraft routing.
The integration of aircraft routing and fleet assignment subproblems enables a match between the itinerary-based passenger demand and the aircraft capacity that maximizes the profit, while taking direct operating costs and delay penalty costs into account. By further integrating schedule design, more opportunities for delay mitigation, and re-optimization flexibility can be explored. Schedule design adopts flight re-timing and optional flight selection decisions where small modifications to the scheduled time of departure (STD), e.g., ±10 min, and flight cancellation can be made with the goal of increasing profits, reducing passenger disruptions and reactionary delays. Therefore, the airline integrated robust scheduling aims at determining the departure times of the selected flight legs, appropriate fleets to perform each flight and the routes of individual aircraft to maximize the profit based on the demand dynamics, fleet configuration and delay distributions. 
Due to the high computational complexity induced by the large number of variables and constraints, traditional decomposition methods do not scale up well to instances of large size (over 900 flights). A VNS-based heuristic is capable of deriving fast and efficient solutions to overcome this issue.

To analyze scalability, the models were first implemented for a small airline (<20 flights per day), then for a medium-sized one (around 150 flights) and finally for a large one (>1000 flights).

This repository aims to implement the models presented in the following paper:

Xu, Y., Wandelt, S., & Sun, X. (2021). [Airline integrated robust scheduling with a variable neighborhood search based heuristic](https://www.sciencedirect.com/user/identity/landing?code=GuXkMOVgQi6PaRovtDYzYvzioxxSFR2ayyUw9c29&state=retryCounter%3D0%26csrfToken%3D654f3f82-73d7-42ff-b68e-ae8babbc031a%26idpPolicy%3Durn%253Acom%253Aelsevier%253Aidp%253Apolicy%253Aproduct%253Ainst_assoc%26returnUrl%3D%252Fscience%252Farticle%252Fpii%252FS0191261521000850%253Fvia%25253Dihub%26prompt%3Dlogin%26cid%3Darp-9294e37e-4dba-4b2e-ab45-8391d6afa5b4). Transportation Research Part B: Methodological, 149, 181-203

The code used is Python and Gurobi is the mathematical optimization software library chosen for the implementation of the models.

# Directories
### VNS

See the internal README.md file of the [VNS](https://github.com/simonecossaro/Airline-Scheduling-With-VNS-Heuristic/tree/main/VNS) directory.

### Big Airline Models

Implementation of model 1, model 2 and VNS-heuristic for an airline of big size.

### Medium Airline Models

Implementation of model 1, model 2 and VNS-heuristic for a medium airline.

### Small Airline Models

Implementation of model 1, model 2 and VNS-heuristic for a small airline.

### Results

The results obtained from model implementations for various airlines.  

# .py files
### Airline.py

This class implements an airline. Its fields and functions concern the sets and parameters useful for model implementations. 

### airline_utilities.py

This file contains numerous useful functions for calculating parameters, not only for the airline class but also for other classes present in the repository.

# csv
### flight_schedule.csv

This dataset contains data on one day's flights. Provides information regarding origin, destination, airline, departure and arrival time, aircraft and even more about each flight.

### aircraftClustering.csv

This dataset provides information regarding the cluster to which each aircraft belongs.

### aircraftSeats.csv

This dataset provides information about the number of seats on each aircraft.

