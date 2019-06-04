from operation import Operation
import queue
import time
import json

import sys

print(sys.path)
params={}
params['oper']="UPGRADE"
params['params']="../driver/testFirm_164.bin"

params['target']=["osma-dman.ddns.net",5555]


output_q = queue.Queue()
data_q = queue.Queue()


ope=Operation(params, output_q, data_q)
ope.start()

while data_q.empty():
    
    newmsg=output_q.get()
    print(newmsg)
    

while not output_q.empty():
    newmsg=output_q.get(True)
    print(newmsg)
    
if data_q.get():
    print( "Exito en operacion")
   
else:
    print( "Error en operacion")   
    