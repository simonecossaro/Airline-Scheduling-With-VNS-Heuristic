from Airline import Airline
from VNS.VNS import VNS
import time
import warnings

warnings.filterwarnings('ignore')

airline = Airline('NVR')
vns = VNS(airline)
start = time.perf_counter()
sol, obj_value = vns.search(10)
end = time.perf_counter()
print('Solution aircraft routing problem: ')
print(sol)
print('Revenue(objective function value): ' + str("{:e}".format(obj_value)))
print('Task time: ' + str(end - start) + ' s')
