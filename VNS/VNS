#import evaluator

class VNS:
    def __init__(self, initial_solution, neighborhood_func):
        self.current_solution = initial_solution
        self.neighborhood_func = neighborhood_func
        self.objective_value = evaluator(self.current_solution)
        
    def search(self,N):
        k = 1
        while (k <= N):
            neighbors = self.neighborhood_func(self.current_solution,10)
            neighbor = random.choice(neighbors)
            if (neighbor != None):
                obj = evaluator(neighbor)
            else:
                obj = 0
            if (self.objective_value >= obj):
                k += 1
            else:
                self.objective_value,self.current_solution = obj,neighbor
        return self.current_solution,self.objective_value
