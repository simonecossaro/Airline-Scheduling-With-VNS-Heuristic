# VNS (Variable Neighborhood Search)
Variable neighborhood search (VNS) is a metaheuristic method for solving a set of combinatorial optimization and global optimization problems. It explores distant neighborhoods of the current incumbent solution and moves from there to a new one if and only if an improvement was made. The local search method is applied repeatedly to get from solutions in the neighborhood to local optima.

Given the large solution space of the integrated airline robust scheduling problem, VNS algorithm seeks to explore high quality solution through generating and improving the base aircraft paths instead of fully searching decision values on routing, re-timing and passenger flow assignment.

First of all let's define the following term. A flight route solution p = {fi,..., fk} is a combination of flights f where an aircraft is able to successively execute all flights with re-timing possibility (i.e. likely to be connected after re-timing). 

## Neighborhood

Class that implements a neighborhood. There four types of neighborhood structures to generate flight route solution pairs: cross, insert, swap, and delete. These neighborhoods provide effective probing to new solutions with varying search depth. We introduce several notations first:
* dep(f): Departure airport of flight f
* arr(f): Arrival airport of flight f
* con(fi, fj): fi can be connected to fj

## FeasibleSolutionSearcher

This class allows to build quickly a feasible solution as shown in the compact aircraft routing model of [Parmentier and Meunier](https://www.sciencedirect.com/science/article/pii/S0305048317306837) (2020).

## Evaluator_Complete
This class implements the complete evaluator, i.e. the one which, as illustrated in the paper, performs 4 steps. In the cases observed experimentally, steps 3 and 4 offer a negligible improvement in revenue evaluation. Furthermore, for large airlines, these steps in which they try to redirect passengers from one itinerary to another take an excessive amount of time. For these reasons, an evaluator with only two steps was used, but the full version was still implemented. 

## Evaluator

Class the implements an object that receives a flight routes solution and returns the value of the airline's revenue for this solution, trying to assign passengers to itineraries in order to get the best revenue. 
One-stop itineraries are favored as they have a higher fare than not-one-stop itineraries. The evaluator first sorts one-stop itineraries by fare. Then following the ranking order it assigns the maximum number of passengers to each one-stop itinerary. The number is given by the minimum between the residual capacity of the flights present in the itinerary and the demand for the itinerary.
Subsequently it does the same for not-one-stop itineraries.
In the end, it calculates costs as the sum of the cost of each individual aircraft route and return the difference between the sum of revenue and costs.

## VNS

This class allows the implementation of the VNS heuristic, using the other classes defined in this directory.
The algorithm initially receives the feasible solution from the FeasibleSolutionSearcher and evaluates it, this represents the initial solution. 
Then it begins to explore the neighborhood and evaluate the neighbors, updating its solution only if a neighbor provides a better objective value.
The search() function requires a parameter N which indicates how many neighbors the algorithm should visit.
