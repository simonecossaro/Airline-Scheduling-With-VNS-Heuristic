from Airline import Airline
from VNS.VNS import VNS
import time
import warnings
warnings.filterwarnings('ignore')


start = time.perf_counter()
small_airline = Airline('WRC')
vns = VNS(small_airline)
sol, obj_value = vns.search(10)
end = time.perf_counter()
print('Solution aircraft routing problem: ')
print(sol)
print('Revenue(objective function value): ' + str(obj_value))
print('Task time: ' + str(end - start) + ' s')
