# Airline-Scheduling-With-VNS-Heuristic
The airline integrated robust scheduling problem integrates flight scheduling, fleet assignment and aircraft routing.
The integration of aircraft routing and fleet assignment subproblems enables a match between the itinerary-based passenger demand and the aircraft capacity that maximizes the profit, while taking direct operating costs and delay penalty costs into account. By further integrating schedule design, more opportunities for delay mitigation, and re-optimization flexibility can be explored. Schedule design adopts flight re-timing and optional flight selection decisions where small modifications to the scheduled time of departure (STD), e.g., ±10 min, and flight cancellation can be made with the goal of increasing profits, reducing passenger disruptions and reactionary delays. Therefore, the airline integrated robust scheduling aims at determining the departure times of the selected flight legs, appropriate fleets to perform each flight, and the routes of individual aircraft to maximize the profit based on the demand dynamics, fleet configuration, and delay distributions. 
Due to the high computational complexity induced by the large number of variables and constraints, traditional decomposition methods do not scale up well to instances of large size (over 900 flights). A VNS-based heuristic is capable of deriving fast and efficient solutions to overcome this issue.
To analyze scalability, the models were first implemented for a small airline (<20 flights per day), then for a medium-sized one (around 150 flights) and finally for a large one (>1000 flights).

# Directories
#B Big Airline Model
#B Medium Airline Model
#B Small Airline Model
#B Results
#B VNS


# .py files
#B Airline
#B airline_utilities

# csv
#B flight_schedule
#B aircraft_clusters
#B aircraft_seats

