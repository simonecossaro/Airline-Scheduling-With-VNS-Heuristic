from VNS.Evaluator import Evaluator
from VNS.FeasibleSolutionSearcher import FeasibleSolutionSearcher
from VNS.Neighborhood import Neighborhood
import random

class VNS:
    def __init__(self, airline):
        self.airline = airline
        self.feasibleSolutionSearcher = FeasibleSolutionSearcher(airline)
        self.evaluator = Evaluator(airline)
        self.neighborhood = Neighborhood(airline.flights)
        self.current_solution = self.feasibleSolutionSearcher.search()
        self.neighborhood_func = self.neighborhood.neighborhood
        self.objective_value = self.evaluator.evaluate(self.current_solution)
        
    def search(self,N):
        k = 1
        while k <= N:
            neighbors = self.neighborhood_func(self.current_solution,10)
            neighbor = random.choice(neighbors)
            if neighbor is not None:
                obj = self.evaluator.evaluate(neighbor)
            else:
                obj = 0
            if self.objective_value >= obj:
                k += 1
            else:
                self.objective_value,self.current_solution = obj,neighbor
        return self.current_solution,self.objective_value
