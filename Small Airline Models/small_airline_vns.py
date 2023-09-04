import time
import Airline
import VNS

start = time.perf_counter()
small_airline = Airline('WRC')
vns = VNS(small_airline)
sol, obj_value = vns.search(10)
end = time.perf_counter()
print('Solution aircraft routing problem: ')
print(sol)
print('Revenue(objective function value): '+ str(sa_obj_value))
print('Task time: '+ str(sa_end-sa_start) + ' s')
