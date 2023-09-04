import time
import Airline
import VNS

start = time.perf_counter()
big_airline = Airline('EZY')
vns = VNS(big_airline)
sol, obj_value = vns.search(10)
end = time.perf_counter()
print('Solution aircraft routing problem: ')
print(sol)
print('Revenue(objective function value): '+ str(obj_value))
print('Task time: '+str(end-start)+ ' s')
